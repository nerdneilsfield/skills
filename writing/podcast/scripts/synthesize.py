#!/usr/bin/env python3
"""Turn a podcast script (see references/script-format.md) into one audio file.

Python 3 standard library only. ffmpeg is optional: needed for mp3 output,
loudness normalisation and non-wav clips. Without it, wav clips are joined
with the wave module and written as .wav.

Endpoints and keys come from environment variables or a config file, never
from code. Nothing is called with --dry-run.
"""
import argparse
import base64
import hashlib
import io
import json
import os
import random
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import wave
from pathlib import Path

DEFAULTS = {
    'backend': 'openai',        # openai | mimo
    'base_url': '',
    'api_key': '',
    'api_key_env': 'PODCAST_TTS_API_KEY',
    'model': '',
    'voices': {},               # speaker id -> "voice" or {"voice","style","speed"}
    'style_mode': 'auto',       # auto | tag | instruction | none
    'format': 'wav',            # clip format requested from the backend
    'sample_rate': 24000,       # used when decoding or joining clips
    'max_chars': 150,           # max characters per request
    'default_pause': 0.35,      # seconds after a line
    'split_pause': 0.12,        # seconds between pieces of one split line
    'retries': 4,
    'backoff': 1.0,             # seconds, doubled each attempt
    'timeout': 120,
    'price_per_1k_chars': 0.0,  # only used to print an estimate
}
ENV_MAP = {
    'PODCAST_TTS_BACKEND': 'backend',
    'PODCAST_TTS_BASE_URL': 'base_url',
    'PODCAST_TTS_API_KEY': 'api_key',
    'PODCAST_TTS_MODEL': 'model',
}
LINE = re.compile(r'^([A-Za-z_][\w-]*)\s*(?:\[([^\]]*)\])?\s*(?:\{\s*([\d.]+)\s*s?\s*\})?\s*[:：]\s*(.+)$')
SENT_END = re.compile(r'(?<=[。！？!?；;…\n])')
CLAUSE_END = re.compile(r'(?<=[，,、：:])')
DISCLOSE = re.compile(r'虚构|fictional|imaginary|假想|杜撰', re.I)


class ScriptError(Exception):
    pass


class BackendError(Exception):
    def __init__(self, msg, retryable=False):
        super().__init__(msg)
        self.retryable = retryable


# ---------- script parsing ----------

def parse_script(text):
    """Return (meta, items). items: dicts of kind 'chapter' or 'line'."""
    meta, items = {}, []
    lines = text.splitlines()
    i = 0
    if lines and lines[0].strip() == '---':
        i = 1
        while i < len(lines) and lines[i].strip() != '---':
            if ':' in lines[i] and not lines[i].lstrip().startswith('#'):
                k, v = lines[i].split(':', 1)
                meta[k.strip()] = v.strip()
            i += 1
        i += 1
    for no in range(i, len(lines)):
        raw = lines[no].strip()
        if not raw or raw.startswith('//'):
            continue
        if raw.startswith('#'):
            items.append({'kind': 'chapter', 'title': raw.lstrip('#').strip(), 'no': no + 1})
            continue
        m = LINE.match(raw)
        if not m:
            raise ScriptError(f'line {no + 1}: not a "speaker [style] {{pause}}: text" line: {raw[:40]}')
        spk, style, pause, body = m.groups()
        items.append({'kind': 'line', 'no': no + 1, 'speaker': spk, 'style': (style or '').strip(),
                      'pause': float(pause) if pause else None, 'text': body.strip()})
    return meta, items


def lint(meta, items):
    warnings = []
    declared = {k.split('.', 1)[1]: v for k, v in meta.items() if k.startswith('speaker.')}
    spoken = [it for it in items if it['kind'] == 'line']
    for it in spoken:
        if declared and it['speaker'] not in declared:
            warnings.append(f"line {it['no']}: speaker {it['speaker']} is not declared in the header")
    fictional = [s for s, v in declared.items() if 'fictional' in v.lower() or '虚构' in v]
    if fictional and not any(DISCLOSE.search(it['text']) for it in spoken[:8]):
        warnings.append('fictional speaker declared but no spoken disclosure in the first 8 lines')
    return warnings


def split_text(text, max_chars):
    """Split on sentence ends, then clause ends, then hard cuts; pack up to max_chars."""
    pieces = []
    for sent in filter(None, SENT_END.split(text)):
        if len(sent) <= max_chars:
            pieces.append(sent)
            continue
        for clause in filter(None, CLAUSE_END.split(sent)):
            while len(clause) > max_chars:
                pieces.append(clause[:max_chars])
                clause = clause[max_chars:]
            if clause:
                pieces.append(clause)
    packed = []
    for p in pieces:
        if packed and len(packed[-1]) + len(p) <= max_chars:
            packed[-1] += p
        else:
            packed.append(p)
    return [p.strip() for p in packed if p.strip()]


# ---------- config ----------

def load_config(path):
    cfg = dict(DEFAULTS)
    path = path or os.environ.get('PODCAST_TTS_CONFIG')
    if path:
        cfg.update(json.loads(Path(path).read_text(encoding='utf-8')))
    for env, key in ENV_MAP.items():
        if os.environ.get(env):
            cfg[key] = os.environ[env]
    if not cfg['api_key']:
        cfg['api_key'] = os.environ.get(cfg['api_key_env'], '')
    return cfg


def voice_for(cfg, speaker):
    v = cfg['voices'].get(speaker)
    if v is None:
        raise ScriptError(f'no voice configured for speaker "{speaker}"')
    return {'voice': v} if isinstance(v, str) else dict(v)


def style_mode(cfg):
    if cfg['style_mode'] != 'auto':
        return cfg['style_mode']
    return 'tag' if cfg['backend'] == 'mimo' else 'instruction'


def plan(items, cfg):
    """Expand lines into requests: one per split piece."""
    reqs = []
    for it in items:
        if it['kind'] != 'line':
            continue
        v = voice_for(cfg, it['speaker'])
        pieces = split_text(it['text'], cfg['max_chars'])
        for n, piece in enumerate(pieces):
            last = n == len(pieces) - 1
            pause = (it['pause'] if it['pause'] is not None else cfg['default_pause']) if last else cfg['split_pause']
            reqs.append({'no': it['no'], 'speaker': it['speaker'], 'text': piece, 'voice': v['voice'],
                         'style': it['style'] or v.get('style', ''), 'speed': v.get('speed'),
                         'pause': pause, 'chapter_before': None})
    return reqs


def cache_key(cfg, req):
    blob = json.dumps({'b': cfg['backend'], 'm': cfg['model'], 'v': req['voice'], 's': req['style'],
                       'sp': req['speed'], 'sm': style_mode(cfg), 'f': cfg['format'], 't': req['text']},
                      ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(blob.encode('utf-8')).hexdigest()[:32]


# ---------- backends ----------

def _opener(url):
    host = urllib.parse.urlparse(url).hostname or ''
    if host in ('localhost', '127.0.0.1', '::1'):
        return urllib.request.build_opener(urllib.request.ProxyHandler({}))
    return urllib.request.build_opener()


def _post(cfg, url, payload, headers):
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json', **headers})
    try:
        with _opener(url).open(req, timeout=cfg['timeout']) as r:
            return r.read(), r.headers.get('Content-Type', '')
    except urllib.error.HTTPError as e:
        body = e.read()[:200].decode('utf-8', 'replace')
        e.close()
        raise BackendError(f'HTTP {e.code}: {body}', retryable=e.code in (408, 429) or e.code >= 500)
    except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
        raise BackendError(f'network: {e}', retryable=True)


def call_openai(cfg, req):
    payload = {'model': cfg['model'], 'input': req['text'], 'voice': req['voice'],
               'response_format': cfg['format']}
    if req['speed']:
        payload['speed'] = req['speed']
    if req['style'] and style_mode(cfg) == 'instruction':
        payload['instructions'] = req['style']
    headers = {'Authorization': f"Bearer {cfg['api_key']}"} if cfg['api_key'] else {}
    body, _ = _post(cfg, cfg['base_url'].rstrip('/') + '/audio/speech', payload, headers)
    if not body:
        raise BackendError('empty audio body', retryable=True)
    return body


def call_mimo(cfg, req):
    text, mode = req['text'], style_mode(cfg)
    messages = []
    if req['style'] and mode == 'instruction':
        messages.append({'role': 'user', 'content': req['style']})
    elif req['style'] and mode == 'tag':
        text = f"({req['style']}){text}"
    messages.append({'role': 'assistant', 'content': text})
    payload = {'model': cfg['model'] or 'mimo-v2.5-tts', 'messages': messages,
               'audio': {'format': cfg['format'], 'voice': req['voice']}}
    body, _ = _post(cfg, cfg['base_url'].rstrip('/') + '/chat/completions', payload,
                    {'api-key': cfg['api_key']})
    try:
        b64 = json.loads(body)['choices'][0]['message']['audio']['data']
        return base64.b64decode(b64)
    except (KeyError, IndexError, TypeError, ValueError) as e:
        raise BackendError(f'unexpected response shape: {e}', retryable=False)


BACKENDS = {'openai': call_openai, 'mimo': call_mimo}


def fetch(cfg, req, sleep=time.sleep):
    call = BACKENDS[cfg['backend']]
    last = None
    for attempt in range(cfg['retries'] + 1):
        try:
            return call(cfg, req)
        except BackendError as e:
            last = e
            if not e.retryable or attempt == cfg['retries']:
                break
            sleep(cfg['backoff'] * (2 ** attempt) * (1 + random.random() * 0.1))
    raise last


# ---------- audio ----------

def have_ffmpeg():
    return shutil.which('ffmpeg') is not None


def decode_pcm(path, rate):
    """Return mono s16le bytes at `rate`."""
    if have_ffmpeg():
        p = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-f', 's16le', '-ac', '1',
                            '-ar', str(rate), 'pipe:1'], capture_output=True)
        if p.returncode != 0:
            raise RuntimeError(f'ffmpeg failed on {path.name}: {p.stderr.decode()[:200]}')
        return p.stdout
    try:
        with wave.open(str(path), 'rb') as w:
            if (w.getnchannels(), w.getsampwidth(), w.getframerate()) != (1, 2, rate):
                raise RuntimeError(f'{path.name}: need mono 16-bit {rate} Hz wav, or install ffmpeg')
            return w.readframes(w.getnframes())
    except wave.Error:
        raise RuntimeError(f'{path.name} is not wav; install ffmpeg to decode other formats')


def write_output(pcm, out, rate, normalize):
    out = Path(out)
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm)
    wav = buf.getvalue()
    if out.suffix.lower() == '.wav' and not normalize:
        out.write_bytes(wav)
        return
    if not have_ffmpeg():
        raise RuntimeError('mp3 output and --normalize need ffmpeg; use a .wav output path without it')
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'wav', '-i', 'pipe:0']
    if normalize:
        cmd += ['-af', 'loudnorm=I=-16:TP=-1.5:LRA=11']
    if out.suffix.lower() == '.mp3':
        cmd += ['-codec:a', 'libmp3lame', '-q:a', '4']
    p = subprocess.run(cmd + [str(out)], input=wav, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f'ffmpeg failed: {p.stderr.decode()[:300]}')


def stamp(sec):
    sec = int(sec)
    return f'{sec // 3600:02d}:{sec % 3600 // 60:02d}:{sec % 60:02d}'


# ---------- main flow ----------

def build(items, cfg, cache_dir, out, normalize, log, sleep=time.sleep):
    reqs = plan(items, cfg)
    cache_dir.mkdir(parents=True, exist_ok=True)
    failures, stats = [], {'cached': 0, 'fetched': 0}
    for r in reqs:
        r['path'] = cache_dir / f"{cache_key(cfg, r)}.{cfg['format']}"
        if r['path'].exists() and r['path'].stat().st_size > 0:
            stats['cached'] += 1
            continue
        try:
            audio = fetch(cfg, r, sleep)
            tmp = r['path'].with_suffix('.part')
            tmp.write_bytes(audio)
            tmp.replace(r['path'])
            stats['fetched'] += 1
        except BackendError as e:
            failures.append((r['no'], r['speaker'], str(e)))
            log(f"FAILED line {r['no']} ({r['speaker']}): {e}")
    if failures:
        return {'ok': False, 'failures': failures, **stats}
    rate = cfg['sample_rate']
    pcm, chapters, by_line = bytearray(), [], {}
    for r in reqs:
        by_line.setdefault(r['no'], []).append(r)
    pending_title = None
    for it in items:
        if it['kind'] == 'chapter':
            pending_title = it['title']
            continue
        if pending_title is not None:
            chapters.append((len(pcm) / 2 / rate, pending_title))
            pending_title = None
        for r in by_line[it['no']]:
            pcm += decode_pcm(r['path'], rate)
            pcm += b'\x00\x00' * int(r['pause'] * rate)
    write_output(bytes(pcm), out, rate, normalize)
    ch = Path(out).with_suffix('.chapters.txt')
    ch.write_text(''.join(f'{stamp(t)} {title}\n' for t, title in chapters), encoding='utf-8')
    return {'ok': True, 'seconds': len(pcm) / 2 / rate, 'chapters': str(ch), **stats}


def dry_run(items, cfg, cache_dir, log):
    reqs = plan(items, cfg)
    chars = sum(len(r['text']) for r in reqs)
    cached = sum(1 for r in reqs if (cache_dir / f"{cache_key(cfg, r)}.{cfg['format']}").exists())
    lines = sum(1 for i in items if i['kind'] == 'line')
    log(f'lines: {lines}, requests: {len(reqs)} ({cached} already cached, {len(reqs) - cached} to call)')
    log(f'characters: {chars}, split lines: {len(reqs) - lines}')
    log(f'estimated speech time: about {chars / 4.5 / 60:.1f} min at ~4.5 chars/s (rough, Chinese)')
    todo = sum(len(r['text']) for r in reqs if not (cache_dir / f"{cache_key(cfg, r)}.{cfg['format']}").exists())
    price = cfg['price_per_1k_chars']
    if price:
        log(f'estimated cost for uncached text: {todo / 1000 * price:.4f} (price_per_1k_chars={price})')
    else:
        log('cost: unknown; set price_per_1k_chars in the config to see an estimate')
    return {'lines': lines, 'requests': len(reqs), 'chars': chars, 'cached': cached}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('script')
    ap.add_argument('--config')
    ap.add_argument('--out', help='output file (.mp3 or .wav); default next to the script')
    ap.add_argument('--cache-dir', help='default: <out dir>/.tts-cache')
    ap.add_argument('--dry-run', action='store_true', help='count lines and cost, call nothing')
    ap.add_argument('--normalize', action='store_true', help='loudness-normalise with ffmpeg')
    a = ap.parse_args(argv)
    log = lambda s: print(s, file=sys.stderr)
    try:
        cfg = load_config(a.config)
        meta, items = parse_script(Path(a.script).read_text(encoding='utf-8'))
        for w in lint(meta, items):
            log('warning: ' + w)
        out = Path(a.out) if a.out else Path(a.script).with_suffix('.mp3' if have_ffmpeg() else '.wav')
        cache_dir = Path(a.cache_dir) if a.cache_dir else out.parent / '.tts-cache'
        if a.dry_run:
            dry_run(items, cfg, cache_dir, log)
            return 0
        if cfg['backend'] not in BACKENDS:
            raise ScriptError(f"unknown backend {cfg['backend']}; use one of {sorted(BACKENDS)}")
        if not cfg['base_url']:
            raise ScriptError('set PODCAST_TTS_BASE_URL or base_url in the config')
        res = build(items, cfg, cache_dir, out, a.normalize, log)
    except (ScriptError, RuntimeError, OSError, json.JSONDecodeError) as e:
        log(f'error: {e}')
        return 2
    if not res['ok']:
        log(f"{len(res['failures'])} line(s) failed; {res['fetched']} fetched, {res['cached']} cached. "
            'Rerun to retry only the failed lines.')
        return 1
    log(f"wrote {out} ({res['seconds']:.0f}s), chapters {res['chapters']}; "
        f"{res['fetched']} fetched, {res['cached']} from cache")
    return 0


if __name__ == '__main__':
    sys.exit(main())
