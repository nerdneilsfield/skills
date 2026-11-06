import base64
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'coding' / 'interactive-guide'
BUILD = SKILL / 'scripts' / 'build_guide.py'


def build(data, out):
    path = SKILL / 'assets' / '.test-data.json'
    path.write_text(json.dumps(data), encoding='utf-8')
    try:
      return subprocess.run(
        [sys.executable, str(BUILD), str(path), str(out / 'page.html'), '--repo', str(ROOT), '--check'],
        capture_output=True, text=True)
    finally:
        path.unlink()


def run_builder(data_path, *flags, env=None):
    return subprocess.run(
        [sys.executable, str(BUILD), str(data_path), str(data_path) + '.html', '--check', *flags],
        capture_output=True, text=True, env=env)


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')


def builder():
    sys.path.insert(0, str(BUILD.parent))
    import build_guide
    return build_guide


PAGE = {'id': 'a', 'title': 'A', 'blocks': [{'type': 'text', 'md': 'x'}]}


class GuideDirectory(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name) / 'guide'
        write(self.dir / 'pages' / '01-a.json', PAGE)
        write(self.dir / 'guide.json', {'title': 'T', 'summary': 'S', 'pages': ['pages/01-a.json', dict(PAGE, id='b')]})

    def test_merges_listed_pages_in_order(self):
        data, base, notes = builder().load_guide(self.dir)
        self.assertEqual([p['id'] for p in data['pages']], ['a', 'b'])
        self.assertEqual((base, notes), (self.dir.resolve(), []))
        self.assertEqual(run_builder(self.dir).returncode, 0)

    def test_warns_about_a_page_file_not_listed(self):
        write(self.dir / 'pages' / '02-b.json', PAGE)
        self.assertIn('not listed', run_builder(self.dir).stderr)

    def test_missing_page_file_is_a_clear_error(self):
        (self.dir / 'pages' / '01-a.json').unlink()
        result = run_builder(self.dir)
        self.assertEqual(result.returncode, 1)
        self.assertIn('cannot read', result.stderr)
        self.assertNotIn('Traceback', result.stderr)

    def test_images_resolve_from_the_guide_directory_in_page_files(self):
        (self.dir / 'a.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"/>', encoding='utf-8')
        write(self.dir / 'pages' / '01-a.json', dict(PAGE, blocks=[{'type': 'figure', 'src': 'a.svg', 'alt': 'a'}]))
        self.assertEqual(run_builder(self.dir).returncode, 0)


class MissingFacts(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / 'data.json'

    def check(self, data):
        write(self.path, data)
        return run_builder(self.path)

    def test_missing_display_field_warns_and_builds(self):
        result = self.check({'repo': 'x', 'pages': [{'id': 'a', 'blocks': [
            {'type': 'figure', 'src': 'data:image/png;base64,AA'},
            {'type': 'compare', 'headers': ['a', 'b'], 'rows': [['1']]}]}]})
        self.assertEqual(result.returncode, 0, result.stderr)
        for gap in ('guide: title', 'guide: summary', 'guide: commit', 'page a: title', 'figure: alt', 'compare: row 1'):
            self.assertIn(gap, result.stderr)

    def test_missing_structure_still_fails(self):
        result = self.check({'title': 'T', 'summary': 'S', 'pages': [{'id': 'a', 'blocks': [{'type': 'code'}]}]})
        self.assertEqual(result.returncode, 1)
        self.assertIn('code needs code', result.stderr)

    def test_page_without_blocks_fails(self):
        self.assertIn('no blocks', self.check({'title': 'T', 'summary': 'S', 'pages': [{'id': 'a'}]}).stderr)

    def test_assumptions_must_be_strings(self):
        result = self.check({'title': 'T', 'summary': 'S', 'assumptions': 'one', 'pages': [PAGE]})
        self.assertIn('assumptions', result.stderr)


class QuickAnswer(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / 'answer.json'
        self.block = {'type': 'text', 'md': 'x'}

    def answer(self, count):
        write(self.path, {'mode': 'answer', 'title': 'Q', 'summary': 'A', 'blocks': [self.block] * count})
        return run_builder(self.path)

    def test_example_is_valid(self):
        result = run_builder(SKILL / 'assets' / 'example-answer.json')
        self.assertEqual((result.returncode, result.stderr), (0, ''))

    def test_top_level_blocks_become_one_page(self):
        self.answer(2)
        data = builder().load_guide(self.path)[0]
        self.assertEqual(len(data['pages']), 1)
        self.assertNotIn('blocks', data)

    def test_block_count_is_bounded(self):
        self.assertEqual(self.answer(4).returncode, 0)
        for count in (1, 5):
            self.assertIn('2 to 4 blocks', self.answer(count).stderr)

    def test_rejects_unknown_mode(self):
        write(self.path, {'mode': 'nope', 'title': 'T', 'summary': 'S', 'pages': [PAGE]})
        self.assertIn('unknown mode', run_builder(self.path).stderr)


class ImageSize(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)
        self.bin = self.dir / 'bin'
        self.bin.mkdir()
        self.png = self.dir / 'big.png'
        self.png.write_bytes(b'\x89PNG' + b'0' * (builder().IMAGE_WARN_KB * 1024 + 10))
        self.data = {'pages': [{'blocks': [{'type': 'figure', 'src': 'big.png', 'alt': 'a'}]}]}

    def inline(self, compress):
        warnings = []
        with mock.patch.dict(os.environ, {'PATH': str(self.bin)}):
            self.assertEqual(builder().inline_images(self.data, self.dir, warnings, compress=compress), [])
        return warnings

    def fake_tool(self, name, body):
        tool = self.bin / name
        tool.write_text(f'#!/bin/sh\n{body}\n', encoding='utf-8')
        tool.chmod(0o755)

    def test_warns_over_the_threshold(self):
        self.assertIn('large image', self.inline(False)[0])

    def test_small_image_is_quiet(self):
        self.png.write_bytes(b'\x89PNG')
        self.assertEqual(self.inline(True), [])

    def test_no_tool_falls_back_to_the_original(self):
        warnings = self.inline(True)
        self.assertIn('no PNG compressor', warnings[0])
        self.assertIn('large image', warnings[1])

    def test_uses_a_detected_tool_and_keeps_the_source(self):
        size = self.png.stat().st_size
        self.fake_tool('pngquant', 'while [ "$1" != "--output" ]; do shift; done; printf small > "$2"')
        self.assertEqual(self.inline(True), [])
        self.assertEqual(self.png.stat().st_size, size)
        self.assertTrue(self.data['pages'][0]['blocks'][0]['src'].endswith(base64.b64encode(b'small').decode()))

    def test_failing_tool_keeps_the_original(self):
        self.fake_tool('oxipng', 'exit 1')
        self.assertIn('large image', self.inline(True)[0])

    def test_check_does_not_compress(self):
        self.fake_tool('pngquant', 'exit 1')
        write(self.dir / 'g.json', {'title': 'T', 'summary': 'S', 'pages': [{'id': 'a', 'blocks': self.data['pages'][0]['blocks']}]})
        result = run_builder(self.dir / 'g.json')
        self.assertEqual(result.returncode, 0)
        self.assertIn('large image', result.stderr)


class Walkthrough(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((SKILL / 'assets' / 'example.json').read_text(encoding='utf-8'))
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.out = Path(self.tmp.name)

    def test_example_is_valid(self):
        self.assertEqual(build(self.data, self.out).returncode, 0)

    def test_app_pins_cdn_libraries(self):
        pkg = json.loads((SKILL / 'assets' / 'app' / 'package.json').read_text(encoding='utf-8'))
        for version in pkg['dependencies'].values():
            self.assertRegex(version, r'^\d')

    def flow(self):
        return next(b for p in self.data['pages'] for b in p['blocks'] if b['type'] == 'flow')

    def test_rejects_unknown_block(self):
        self.data['pages'][0]['blocks'].append({'type': 'nope'})
        self.assertIn('unknown type', build(self.data, self.out).stderr)

    def test_rejects_line_out_of_range(self):
        self.flow()['flows'][0]['steps'][0]['line'] = 10 ** 6
        self.assertIn('outside', build(self.data, self.out).stderr)

    def test_rejects_step_without_an_edge(self):
        self.flow()['flows'][0]['steps'][1]['to'] = 'text'
        self.assertIn('no edge', build(self.data, self.out).stderr)

    def test_rejects_bad_papercode_status(self):
        self.data['pages'][0]['blocks'].append({'type': 'papercode', 'items': [{'paper': 'p', 'file': 'README.md', 'status': 'maybe'}]})
        self.assertIn('bad status', build(self.data, self.out).stderr)

    def test_rejects_empty_or_malformed_structure(self):
        blocks = self.data['pages'][0]['blocks']
        cases = [({'type': 'figuretour', 'src': 'x.png', 'stops': []}, 'stops'),
                 ({'type': 'figuretour', 'src': 'x.png', 'stops': [{'x': 1, 'y': 1}]}, 'stops'),
                 ({'type': 'flow', 'nodes': [], 'edges': [], 'flows': []}, 'flow needs'),
                 ({'type': 'graph', 'nodes': [], 'edges': []}, 'graph needs')]
        for block, word in cases:
            blocks.append(block)
            err = build(self.data, self.out).stderr
            blocks.pop()
            self.assertIn(word, err)
            self.assertNotIn('Traceback', err)

    def test_papercode_without_file_is_a_marked_gap(self):
        sys.path.insert(0, str(BUILD.parent))
        import build_guide
        data = {'title': 't', 'summary': 's', 'pages': [{'id': 'a', 'title': 'A', 'blocks': [
            {'type': 'papercode', 'items': [{'paper': 'p', 'status': 'match'}, {'paper': 'q', 'status': 'unstated'}]}]}]}
        self.assertEqual(build_guide.validate(data, None), [])
        self.assertEqual([g for g in build_guide.display_gaps(data) if 'file' in g], ['page a block 1 papercode: item 1 file'])

    def test_rejects_remote_image(self):
        figure = self.data['pages'][0]['blocks'][0]
        figure['src'] = 'https://example.com/a.png'
        self.assertIn('remote image', build(self.data, self.out).stderr)

    def test_local_image_is_inlined(self):
        sys.path.insert(0, str(BUILD.parent))
        from build_guide import inline_images
        self.assertEqual(inline_images(self.data, SKILL / 'assets'), [])
        self.assertTrue(self.data['pages'][0]['blocks'][0]['src'].startswith('data:image/svg+xml;base64,'))


if __name__ == '__main__':
    unittest.main()
