import base64
import importlib.util
import io
import json
import os
import shutil
import tempfile
import threading
import unittest
import wave
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('synthesize', ROOT / 'writing/podcast/scripts/synthesize.py')
syn = importlib.util.module_from_spec(spec)
spec.loader.exec_module(syn)


def tone(seconds=0.2, rate=24000):
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b'\x10\x00' * int(seconds * rate))
    return buf.getvalue()


class Fake:
    """Local fake speech server. fail_first: statuses returned before success."""

    def __init__(self, fail_first=(), always=None):
        self.requests, self.fail_first, self.always = [], list(fail_first), always
        fake = self

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                fake.requests.append((self.path, dict(self.headers), body))
                status = fake.always or (fake.fail_first.pop(0) if fake.fail_first else 200)
                if status != 200:
                    self.send_response(status)
                    self.end_headers()
                    self.wfile.write(b'{"error":"x"}')
                    return
                audio = tone()
                if self.path.endswith('/chat/completions'):
                    out = json.dumps({'choices': [{'message': {'audio': {'data': base64.b64encode(audio).decode()}}}]}).encode()
                else:
                    out = audio
                self.send_response(200)
                self.end_headers()
                self.wfile.write(out)

        self.server = HTTPServer(('127.0.0.1', 0), H)
        self.url = f'http://127.0.0.1:{self.server.server_port}/v1'
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()


SCRIPT = """---
title: Test
speaker.A: Host A
speaker.B: Host B
---
# Opening
A [curious] {0.5}: 第一句。第二句！
B: 这是回应。
# Second
A: 结束了。
"""


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.fake = None

    def serve(self, **kw):
        self.fake = Fake(**kw)
        self.addCleanup(self.fake.close)
        return self.fake

    def cfg(self, **kw):
        c = dict(syn.DEFAULTS, base_url=self.fake.url if self.fake else '', model='m',
                 voices={'A': 'va', 'B': {'voice': 'vb', 'speed': 1.1}}, backoff=0, retries=2, max_chars=5)
        c.update(kw)
        return c

    def items(self, text=SCRIPT):
        return syn.parse_script(text)


class Parsing(Base):
    def test_parse_and_lint(self):
        meta, items = self.items()
        lines = [i for i in items if i['kind'] == 'line']
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0]['style'], 'curious')
        self.assertEqual(lines[0]['pause'], 0.5)
        self.assertEqual(syn.lint(meta, items), [])

    def test_bad_line_reports_number(self):
        with self.assertRaisesRegex(syn.ScriptError, 'line 2'):
            syn.parse_script('A: ok\nnot a line\n')

    def test_fictional_needs_disclosure(self):
        meta, items = syn.parse_script('---\nspeaker.X: Zed | fictional\n---\nX: 你好\n')
        self.assertTrue(syn.lint(meta, items))

    def test_split_respects_limit_and_keeps_text(self):
        text = '甲' * 30 + '。' + '乙' * 30 + '，' + '丙' * 90 + '！' + '丁' * 25
        parts = syn.split_text(text, 50)
        self.assertTrue(all(len(p) <= 50 for p in parts))
        self.assertEqual(''.join(parts), text)
        self.assertGreater(len(parts), 3)

    def test_short_text_not_split(self):
        self.assertEqual(syn.split_text('一句话。', 50), ['一句话。'])


class Calls(Base):
    def test_cache_makes_rerun_free(self):
        self.serve()
        _, items = self.items()
        out = self.tmp / 'o.wav'
        r1 = syn.build(items, self.cfg(), self.tmp / 'c', out, False, lambda s: None)
        n = len(self.fake.requests)
        self.assertTrue(r1['ok'])
        self.assertEqual(n, 4)
        r2 = syn.build(items, self.cfg(), self.tmp / 'c', out, False, lambda s: None)
        self.assertEqual(len(self.fake.requests), n)
        self.assertEqual(r2['cached'], 4)

    def test_changed_line_refetches_only_that_line(self):
        self.serve()
        out = self.tmp / 'o.wav'
        syn.build(self.items()[1], self.cfg(), self.tmp / 'c', out, False, lambda s: None)
        n = len(self.fake.requests)
        syn.build(self.items(SCRIPT.replace('这是回应', '这是答复'))[1], self.cfg(), self.tmp / 'c', out, False, lambda s: None)
        self.assertEqual(len(self.fake.requests), n + 1)

    def test_request_shape_and_auth(self):
        self.serve()
        syn.build(self.items()[1], self.cfg(api_key='k'), self.tmp / 'c', self.tmp / 'o.wav', False, lambda s: None)
        path, headers, body = self.fake.requests[0]
        self.assertEqual(path, '/v1/audio/speech')
        self.assertEqual(headers['Authorization'], 'Bearer k')
        self.assertEqual((body['voice'], body['instructions']), ('va', 'curious'))
        self.assertEqual(self.fake.requests[2][2]['speed'], 1.1)

    def test_retry_then_success(self):
        self.serve(fail_first=[503, 429])
        slept = []
        r = syn.fetch(self.cfg(), {'text': 't', 'voice': 'v', 'style': '', 'speed': None}, slept.append)
        self.assertTrue(r.startswith(b'RIFF'))
        self.assertEqual(len(slept), 2)

    def test_client_error_not_retried(self):
        self.serve(always=401)
        with self.assertRaises(syn.BackendError):
            syn.fetch(self.cfg(), {'text': 't', 'voice': 'v', 'style': '', 'speed': None}, lambda s: None)
        self.assertEqual(len(self.fake.requests), 1)

    def test_failure_reported_and_nothing_written(self):
        self.serve(always=500)
        logs = []
        out = self.tmp / 'o.wav'
        r = syn.build(self.items()[1], self.cfg(), self.tmp / 'c', out, False, logs.append, sleep=lambda s: None)
        self.assertFalse(r['ok'])
        self.assertEqual(len(r['failures']), 4)
        self.assertEqual(r['failures'][0][0], 7)
        self.assertFalse(out.exists())
        self.assertTrue(any('FAILED line 7' in m for m in logs))
        self.assertEqual(len(self.fake.requests), 4 * 3)

    def test_mimo_adapter(self):
        self.serve()
        cfg = self.cfg(backend='mimo', model='')
        syn.build(self.items()[1], cfg, self.tmp / 'c', self.tmp / 'o.wav', False, lambda s: None)
        path, headers, body = self.fake.requests[0]
        self.assertEqual(path, '/v1/chat/completions')
        self.assertIn('Api-Key', headers)
        self.assertEqual(body['model'], 'mimo-v2.5-tts')
        self.assertEqual(body['messages'][-1], {'role': 'assistant', 'content': '(curious)第一句。'})
        self.assertEqual(body['audio']['voice'], 'va')

    def test_mimo_voicedesign_sends_user_message_and_no_voice(self):
        self.serve()
        cfg = self.cfg(backend='mimo', model='mimo-v2.5-tts-voicedesign',
                       voices={'A': {'instruction': 'young male'}, 'B': {'instruction': 'old female'}})
        syn.build(self.items()[1], cfg, self.tmp / 'c', self.tmp / 'o.wav', False, lambda s: None)
        body = self.fake.requests[0][2]
        self.assertEqual(body['messages'][0], {'role': 'user', 'content': 'young male'})
        self.assertNotIn('voice', body['audio'])
        with self.assertRaises(syn.ScriptError):
            syn.plan(self.items()[1], dict(cfg, voices={'A': 'x', 'B': 'y'}))

    def test_cache_key_has_endpoint_not_key(self):
        _, items = syn.parse_script(SCRIPT)
        a = syn.plan(items, self.cfg(base_url='http://h1/v1/', api_key='SECRET1'))[0]
        k1 = syn.cache_key(self.cfg(base_url='http://h1/v1/', api_key='SECRET1'), a)
        self.assertEqual(k1, syn.cache_key(self.cfg(base_url='http://H1/v1', api_key='OTHER'), a))
        self.assertNotEqual(k1, syn.cache_key(self.cfg(base_url='http://h2/v1'), a))

    def test_max_chars_must_be_positive(self):
        cf = self.tmp / 'c.json'
        for bad in (0, -3, 1.5, 'x'):
            cf.write_text(json.dumps({'max_chars': bad}))
            with self.assertRaises(syn.ScriptError):
                syn.load_config(str(cf))
        script = self.tmp / 's.txt'
        script.write_text(SCRIPT, encoding='utf-8')
        cf.write_text(json.dumps({'max_chars': 0, 'voices': {'A': 'a', 'B': 'b'}}))
        self.assertEqual(syn.main([str(script), '--config', str(cf), '--dry-run']), 2)

    def test_consecutive_and_trailing_chapters_kept(self):
        self.serve()
        _, items = syn.parse_script('# One\n## Two\nA: hi\n# End\n')
        out = self.tmp / 'o.wav'
        syn.build(items, self.cfg(), self.tmp / 'c', out, False, lambda s: None)
        titles = [l.split(' ', 1)[1] for l in out.with_suffix('.chapters.txt').read_text().splitlines()]
        self.assertEqual(titles, ['One', 'Two', 'End'])

    def test_wav_concat_with_pauses_and_chapters(self):
        self.serve()
        out = self.tmp / 'o.wav'
        r = syn.build(self.items()[1], self.cfg(), self.tmp / 'c', out, False, lambda s: None)
        with wave.open(str(out)) as w:
            seconds = w.getnframes() / w.getframerate()
        # 4 clips of 0.2s plus pauses 0.12 + 0.5 + 0.35 + 0.35
        self.assertAlmostEqual(seconds, 0.8 + 1.32, places=2)
        lines = Path(r['chapters']).read_text().splitlines()
        self.assertEqual(lines[0], '00:00:00 Opening')
        self.assertTrue(lines[1].endswith('Second'))

    @unittest.skipUnless(shutil.which('ffmpeg'), 'ffmpeg not installed')
    def test_mp3_and_normalize(self):
        self.serve()
        out = self.tmp / 'o.mp3'
        r = syn.build(self.items()[1], self.cfg(), self.tmp / 'c', out, True, lambda s: None)
        self.assertTrue(r['ok'])
        self.assertGreater(out.stat().st_size, 500)


    @unittest.skipUnless(shutil.which('ffmpeg'), 'needs ffmpeg')
    def test_normalize_keeps_sample_rate(self):
        self.serve()
        out = self.tmp / 'o.wav'
        syn.build(self.items()[1], self.cfg(), self.tmp / 'c', out, True, lambda s: None)
        with wave.open(str(out)) as w:
            self.assertEqual(w.getframerate(), 24000)


class Cli(Base):
    def test_dry_run_calls_nothing_and_needs_no_url(self):
        script = self.tmp / 's.txt'
        script.write_text(SCRIPT, encoding='utf-8')
        cfgf = self.tmp / 'c.json'
        cfgf.write_text(json.dumps({'voices': {'A': 'a', 'B': 'b'}, 'price_per_1k_chars': 0.5}))
        logs = []
        cfg = syn.load_config(str(cfgf)); cfg['max_chars'] = 5
        _, items = syn.parse_script(SCRIPT)
        res = syn.dry_run(items, cfg, self.tmp / 'cache', logs.append)
        self.assertEqual((res['lines'], res['requests']), (3, 4))
        self.assertTrue(any('estimated cost' in m for m in logs))
        self.assertEqual(syn.main([str(script), '--config', str(cfgf), '--dry-run']), 0)

    def test_missing_base_url_is_an_error(self):
        script = self.tmp / 's.txt'
        script.write_text(SCRIPT, encoding='utf-8')
        cfgf = self.tmp / 'c.json'
        cfgf.write_text(json.dumps({'voices': {'A': 'a', 'B': 'b'}}))
        old = os.environ.pop('PODCAST_TTS_BASE_URL', None)
        try:
            self.assertEqual(syn.main([str(script), '--config', str(cfgf)]), 2)
        finally:
            if old:
                os.environ['PODCAST_TTS_BASE_URL'] = old


if __name__ == '__main__':
    unittest.main()
