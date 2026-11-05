import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'research' / 'research-figure'
TOOL = SKILL / 'scripts' / 'figure_tool.py'
THEME = SKILL / 'assets' / 'themes' / 'japanese.json'
SVG = SKILL / 'assets' / 'example-figure.svg'
BOXES = SKILL / 'assets' / 'example-boxes.json'
ACADEMIC = ('Method pipeline', 'Mechanism diagram', 'Network architecture', 'Scientific schematic',
            'Graphical abstract', 'Multi-condition comparison', 'Qualitative comparison grid',
            'Overview poster', 'Publication chart')
TECHNICAL = ('System architecture', 'Sequence diagram', 'State machine', 'Flowchart', 'ER diagram',
             'Network topology', 'Mind map')

spec = importlib.util.spec_from_file_location('figure_tool', TOOL)
figure_tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(figure_tool)


def run(*args):
    return subprocess.run([sys.executable, str(TOOL), *map(str, args)], capture_output=True, text=True)


def luminance(colour):
    channels = [int(colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    r, g, b = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    high, low = sorted((luminance(a), luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


class Skill(unittest.TestCase):
    def test_contract(self):
        text = (SKILL / 'SKILL.md').read_text(encoding='utf-8')
        self.assertLess(len(text.splitlines()), 120)
        head = text.split('---\n')[1]
        for field in ('license: MIT', 'author: DengQi', 'compatibility:'):
            self.assertIn(field, head)
        self.assertIn('## Gotchas', text)

    def test_never_tied_to_one_model(self):
        pattern = re.compile(r'gpt-image|dall-?e|nano banana|gemini|midjourney|stable diffusion|imagen\b', re.I)
        for doc in [SKILL / 'SKILL.md', *SKILL.glob('references/*.md')]:
            self.assertIsNone(pattern.search(doc.read_text(encoding='utf-8')), doc)

    def test_backend_order(self):
        text = (SKILL / 'SKILL.md').read_text(encoding='utf-8')
        marks = ['The user names one', 'project preference', "running agent's own image tool",
                 'Another available agent', "user's drawing MCP", 'SVG or Mermaid, written']
        self.assertEqual(sorted(text.index(m) for m in marks), [text.index(m) for m in marks])

    def test_every_type_is_covered(self):
        for name, types in (('academic-figures', ACADEMIC), ('technical-diagrams', TECHNICAL)):
            text = (SKILL / 'references' / f'{name}.md').read_text(encoding='utf-8')
            for kind in types:
                section = re.search(rf'^## {kind}\n(.*?)(?=^## |\Z)', text, re.M | re.S)
                self.assertIsNotNone(section, kind)
                for part in ('Use when', 'Ask', 'Layout', 'Avoid', 'Route:'):
                    self.assertIn(part, section[1], kind)


class Theme(unittest.TestCase):
    def setUp(self):
        self.theme = json.loads(THEME.read_text(encoding='utf-8'))

    def test_text_and_lines_stay_readable(self):
        for mode in ('light', 'dark'):
            colours = self.theme[mode]
            fills = [v for k, v in colours.items() if k.endswith('-fill')]
            for surface in [colours['--bg'], *fills]:
                self.assertGreaterEqual(contrast(colours['--text'], surface), 4.5, (mode, surface))
                self.assertGreaterEqual(contrast(colours['--text-muted'], surface), 4.5, (mode, surface))
            for key, value in colours.items():
                if key.endswith('-stroke') or key == '--arrow':
                    self.assertGreaterEqual(contrast(value, colours['--bg']), 3, (mode, key))


class SvgTheme(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.out = Path(tmp.name)
        self.theme = json.loads(THEME.read_text(encoding='utf-8'))

    def svg(self, text):
        path = self.out / 'in.svg'
        path.write_text(text, encoding='utf-8')
        return path

    def test_writes_both_variants(self):
        result = run('theme', SVG, '--out-dir', self.out)
        self.assertEqual(result.returncode, 0, result.stderr)
        for mode in ('light', 'dark'):
            text = (self.out / f'example-figure.{mode}.svg').read_text(encoding='utf-8')
            ET.fromstring(text)
            self.assertIn(self.theme[mode]['--bg'], text)
            self.assertNotIn('--placeholder', text)
            self.assertIn('var(--color-primary-fill)', text)

    def test_only_the_root_block_changes(self):
        original = SVG.read_text(encoding='utf-8')
        themed = figure_tool.apply_theme(original, self.theme['light'])
        strip = lambda text: figure_tool.ROOT_BLOCK.sub('', text)
        self.assertEqual(strip(original), strip(themed))

    def test_flatten_leaves_no_variables(self):
        run('theme', SVG, '--out-dir', self.out, '--mode', 'dark', '--flatten')
        text = (self.out / 'example-figure.dark.svg').read_text(encoding='utf-8')
        ET.fromstring(text)
        self.assertNotIn('var(', text)
        self.assertNotIn(':root', text)
        self.assertIn(self.theme['dark']['--text'], text)

    def test_svg_without_style_gets_one(self):
        path = self.svg('<svg xmlns="http://www.w3.org/2000/svg"><text fill="var(--text)">标签</text></svg>')
        self.assertEqual(run('theme', path, '--out-dir', self.out).returncode, 0)
        text = (self.out / 'in.light.svg').read_text(encoding='utf-8')
        ET.fromstring(text)
        self.assertIn('标签', text)
        self.assertIn('<style>', text)

    def test_undefined_variable_fails_and_writes_nothing(self):
        path = self.svg('<svg xmlns="http://www.w3.org/2000/svg"><rect fill="var(--nope)"/></svg>')
        result = run('theme', path, '--out-dir', self.out)
        self.assertEqual(result.returncode, 1)
        self.assertIn('--nope', result.stderr)
        self.assertFalse((self.out / 'in.light.svg').exists())

    def test_fallback_is_allowed_and_flattened(self):
        path = self.svg('<svg xmlns="http://www.w3.org/2000/svg"><rect fill="var(--nope, #123456)"/></svg>')
        self.assertEqual(run('theme', path, '--out-dir', self.out, '--flatten').returncode, 0)
        self.assertIn('fill="#123456"', (self.out / 'in.dark.svg').read_text(encoding='utf-8'))

    def test_second_root_block_is_rejected(self):
        path = self.svg('<svg xmlns="http://www.w3.org/2000/svg"><style>:root{--a:1} '
                        '@media (prefers-color-scheme: dark){:root{--a:2}}</style></svg>')
        self.assertIn(':root blocks', run('theme', path, '--out-dir', self.out).stderr)

    def test_rejects_bad_xml_and_entities(self):
        self.assertEqual(run('theme', self.svg('<svg><rect></svg>')).returncode, 1)
        bomb = '<!DOCTYPE svg [<!ENTITY a "b">]><svg xmlns="http://www.w3.org/2000/svg">&a;</svg>'
        self.assertIn('entity', run('theme', self.svg(bomb)).stderr)

    def test_warns_about_hardcoded_colours(self):
        path = self.svg('<svg xmlns="http://www.w3.org/2000/svg"><rect fill="#000000"/></svg>')
        self.assertIn('hardcoded', run('theme', path, '--out-dir', self.out).stderr)

    def test_rejects_unsafe_theme_values(self):
        bad = json.loads(THEME.read_text(encoding='utf-8'))
        bad['dark']['--bg'] = 'red;}</style>'
        path = self.out / 'bad.json'
        path.write_text(json.dumps(bad), encoding='utf-8')
        self.assertIn('unsafe', run('theme', SVG, '--theme', path, '--out-dir', self.out).stderr)

    def test_rejects_mismatched_modes(self):
        bad = json.loads(THEME.read_text(encoding='utf-8'))
        del bad['dark']['--bg']
        path = self.out / 'bad.json'
        path.write_text(json.dumps(bad), encoding='utf-8')
        self.assertIn('differ', run('theme', SVG, '--theme', path, '--out-dir', self.out).stderr)


class Excalidraw(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.out = Path(tmp.name)
        self.colours = json.loads(THEME.read_text(encoding='utf-8'))['light']

    def scene(self, data):
        return figure_tool.to_excalidraw(data, self.colours)

    def test_cli_writes_a_consistent_scene(self):
        target = self.out / 'nested' / 'scene.excalidraw'
        result = run('excalidraw', BOXES, target)
        self.assertEqual(result.returncode, 0, result.stderr)
        scene = json.loads(target.read_text(encoding='utf-8'))
        self.assertEqual((scene['type'], scene['version']), ('excalidraw', 2))
        elements = {e['id']: e for e in scene['elements']}
        self.assertEqual(len(elements), len(scene['elements']))
        for element in scene['elements']:
            for bound in element['boundElements']:
                self.assertIn(bound['id'], elements)
            if element['type'] == 'text':
                self.assertIn(element['id'], [b['id'] for b in elements[element['containerId']]['boundElements']])
            if element['type'] == 'arrow':
                for end in ('startBinding', 'endBinding'):
                    target_shape = elements[element[end]['elementId']]
                    self.assertIn(element['id'], [b['id'] for b in target_shape['boundElements']])
        self.assertIn('特征记忆', [e.get('text') for e in scene['elements']])

    def test_output_is_deterministic(self):
        data = json.loads(BOXES.read_text(encoding='utf-8'))
        self.assertEqual(self.scene(data), self.scene(json.loads(BOXES.read_text(encoding='utf-8'))))

    def test_layers_follow_edges_and_survive_cycles(self):
        nodes = [{'id': n, 'label': n} for n in 'abc']
        edges = [{'from': 'a', 'to': 'b'}, {'from': 'b', 'to': 'c'}, {'from': 'c', 'to': 'a'}]
        self.assertEqual(set(figure_tool.layer_ranks(nodes, edges).values()), {0, 1, 2})

    def test_feedback_edge_goes_around_a_box_in_its_way(self):
        scene = self.scene(json.loads(BOXES.read_text(encoding='utf-8')))
        feedback = next(e for e in scene['elements'] if e['id'] == 'edge-5')
        self.assertEqual(len(feedback['points']), 3)
        self.assertGreater(feedback['height'], 0)

    def test_arrow_size_matches_its_points(self):
        for element in self.scene(json.loads(BOXES.read_text(encoding='utf-8')))['elements']:
            if element['type'] == 'arrow':
                xs = [p[0] for p in element['points']]
                self.assertEqual(element['points'][0], [0, 0])
                self.assertAlmostEqual(element['width'], max(xs) - min(xs))

    def test_top_to_bottom_direction(self):
        data = {'direction': 'TB', 'nodes': [{'id': 'a', 'label': 'A'}, {'id': 'b', 'label': 'B'}],
                'edges': [{'from': 'a', 'to': 'b'}]}
        elements = {e['id']: e for e in self.scene(data)['elements']}
        self.assertGreater(elements['node-b']['y'], elements['node-a']['y'])
        self.assertEqual(elements['node-b']['x'], elements['node-a']['x'])

    def test_explicit_position_is_kept(self):
        data = {'nodes': [{'id': 'a', 'label': 'A', 'x': 7, 'y': 9}]}
        self.assertEqual(self.scene(data)['elements'][0]['x'], 7)

    def test_bad_input_is_named(self):
        node = {'id': 'a', 'label': 'A'}
        for data, message in (
            ({'nodes': []}, 'nodes'),
            ({'nodes': [node, node]}, 'duplicate'),
            ({'nodes': [node], 'edges': [{'from': 'a', 'to': 'z'}]}, 'unknown node'),
            ({'nodes': [node], 'edges': [{'from': 'a', 'to': 'a'}]}, 'self-loops'),
            ({'nodes': [{**node, 'shape': 'star'}]}, 'shape'),
            ({'nodes': [{**node, 'group': 'nope'}]}, 'no group'),
            ({'nodes': [{**node, 'x': 1}]}, 'both x and y'),
            ({'nodes': [node], 'direction': 'UP'}, 'direction'),
        ):
            with self.assertRaisesRegex(figure_tool.FigureError, message):
                self.scene(data)

    def test_cli_reports_bad_json(self):
        path = self.out / 'bad.json'
        path.write_text('{', encoding='utf-8')
        result = run('excalidraw', path, self.out / 'x.excalidraw')
        self.assertEqual(result.returncode, 1)
        self.assertIn('error:', result.stderr)


if __name__ == '__main__':
    unittest.main()
