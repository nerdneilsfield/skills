import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'coding' / 'code-walkthrough'
BUILD = SKILL / 'scripts' / 'build_walkthrough.py'


def build(data, out):
    path = out / 'data.json'
    path.write_text(json.dumps(data), encoding='utf-8')
    return subprocess.run(
        [sys.executable, str(BUILD), str(path), str(out / 'page.html'), '--repo', str(ROOT), '--check'],
        capture_output=True, text=True)


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

    def test_rejects_unknown_graph_node(self):
        self.data['graph']['edges'][0]['to'] = 'missing'
        self.assertIn('unknown node', build(self.data, self.out).stderr)

    def test_rejects_line_out_of_range(self):
        self.data['flows'][0]['steps'][0]['line'] = 10 ** 6
        result = build(self.data, self.out)
        self.assertEqual(result.returncode, 1)
        self.assertIn('outside', result.stderr)

    def test_rejects_step_without_an_edge(self):
        self.data['flows'][0]['steps'][1]['to'] = 'text'
        self.assertIn('no edge', build(self.data, self.out).stderr)

    def test_rejects_verified_step_without_a_file(self):
        del self.data['flows'][0]['steps'][1]['file']
        self.assertIn('without a file', build(self.data, self.out).stderr)


if __name__ == '__main__':
    unittest.main()
