import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

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
