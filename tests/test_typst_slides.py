import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.dont_write_bytecode = True  # keep scripts/ free of __pycache__
ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'writing' / 'typst-slides'
ASSETS = SKILL / 'assets'
TEMPLATES = ['research-talk', 'project-review', 'defense', 'client-demo', 'tech-share', 'lecture']


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pptx_spec = load('pptx_spec', SKILL / 'scripts' / 'pptx_spec.py')
check_deck = load('check_deck', SKILL / 'scripts' / 'check_deck.py')

REL = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PKG = 'http://schemas.openxmlformats.org/package/2006/relationships'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
P = 'http://schemas.openxmlformats.org/presentationml/2006/main'


def rels(items):
    body = ''.join(f'<Relationship Id="{i}" Type="{REL}/{t}" Target="{target}"/>' for i, t, target in items)
    return f'<Relationships xmlns="{PKG}">{body}</Relationships>'


def make_pptx(path):
    """A tiny but structurally real deck: one master, one layout, one slide."""
    theme = f'''<a:theme xmlns:a="{A}"><a:themeElements>
      <a:clrScheme name="t"><a:dk1><a:sysClr val="windowText" lastClr="000000"/></a:dk1>
        <a:lt1><a:sysClr val="window" lastClr="FFFFFF"/></a:lt1>
        <a:dk2><a:srgbClr val="1F3A5F"/></a:dk2><a:lt2><a:srgbClr val="F4F1EA"/></a:lt2>
        <a:accent1><a:srgbClr val="C0392B"/></a:accent1><a:accent2><a:srgbClr val="2E86C1"/></a:accent2>
        <a:accent3><a:srgbClr val="28B463"/></a:accent3><a:accent4><a:srgbClr val="F1C40F"/></a:accent4>
        <a:accent5><a:srgbClr val="8E44AD"/></a:accent5><a:accent6><a:srgbClr val="7F8C8D"/></a:accent6>
        <a:hlink><a:srgbClr val="0000FF"/></a:hlink><a:folHlink><a:srgbClr val="800080"/></a:folHlink></a:clrScheme>
      <a:fontScheme name="f"><a:majorFont><a:latin typeface="Georgia"/><a:ea typeface=""/><a:cs typeface=""/>
        <a:font script="Hans" typeface="SimSun"/></a:majorFont>
        <a:minorFont><a:latin typeface="Calibri"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont></a:fontScheme>
    </a:themeElements></a:theme>'''
    pres = f'''<p:presentation xmlns:p="{P}" xmlns:a="{A}"><p:sldSz cx="12192000" cy="6858000"/></p:presentation>'''
    master = f'''<p:sldMaster xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{REL}"><p:cSld>
      <p:bg><p:bgPr><a:solidFill><a:schemeClr val="bg2"/></a:solidFill></p:bgPr></p:bg>
      <p:spTree><p:sp><p:nvSpPr><p:cNvPr id="2" name="Title Placeholder 1"/><p:cNvSpPr/><p:nvPr><p:ph type="title"/></p:nvPr></p:nvSpPr>
        <p:spPr><a:xfrm><a:off x="609600" y="342900"/><a:ext cx="10972800" cy="1028700"/></a:xfrm></p:spPr></p:sp>
      <p:pic><p:nvPicPr><p:cNvPr id="3" name="Logo"/><p:cNvPicPr/><p:nvPr/></p:nvPicPr>
        <p:blipFill><a:blip r:embed="rId9"/></p:blipFill>
        <p:spPr><a:xfrm><a:off x="10800000" y="100000"/><a:ext cx="900000" cy="300000"/></a:xfrm></p:spPr></p:pic>
      <p:sp><p:nvSpPr><p:cNvPr id="4" name="Band"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr><a:xfrm><a:off x="0" y="6500000"/><a:ext cx="12192000" cy="358000"/></a:xfrm>
          <a:prstGeom prst="rect"/><a:solidFill><a:schemeClr val="accent1"/></a:solidFill></p:spPr></p:sp></p:spTree></p:cSld>
      <p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1"/>
      <p:txStyles><p:titleStyle><a:lvl1pPr><a:defRPr sz="3200" b="1"><a:solidFill><a:schemeClr val="tx2"/></a:solidFill>
        <a:latin typeface="+mj-lt"/></a:defRPr></a:lvl1pPr></p:titleStyle>
        <p:bodyStyle><a:lvl1pPr><a:defRPr sz="2000"><a:solidFill><a:schemeClr val="tx1"/></a:solidFill></a:defRPr></a:lvl1pPr></p:bodyStyle>
      </p:txStyles></p:sldMaster>'''
    layout = f'''<p:sldLayout xmlns:p="{P}" xmlns:a="{A}" type="title"><p:cSld name="Cover"><p:spTree>
      <p:sp><p:nvSpPr><p:cNvPr id="2" name="Title"/><p:cNvSpPr/><p:nvPr><p:ph type="ctrTitle"/></p:nvPr></p:nvSpPr>
        <p:spPr><a:xfrm><a:off x="1219200" y="2286000"/><a:ext cx="9753600" cy="1500000"/></a:xfrm></p:spPr>
        <p:txBody><a:bodyPr/><a:lstStyle><a:lvl1pPr algn="ctr"><a:defRPr sz="5400"/></a:lvl1pPr></a:lstStyle></p:txBody></p:sp>
      </p:spTree></p:cSld></p:sldLayout>'''
    slide = f'''<p:sld xmlns:p="{P}" xmlns:a="{A}"><p:cSld><p:spTree>
      <p:sp><p:nvSpPr><p:cNvPr id="2" name="Title"/><p:cNvSpPr/><p:nvPr><p:ph type="ctrTitle"/></p:nvPr></p:nvSpPr>
        <p:spPr/><p:txBody><a:bodyPr/><a:p><a:r><a:rPr sz="6000"><a:solidFill><a:srgbClr val="BCEF59"/></a:solidFill></a:rPr>
        <a:t>Kickoff</a:t></a:r></a:p></p:txBody></p:sp></p:spTree></p:cSld></p:sld>'''
    with zipfile.ZipFile(path, 'w') as z:
        z.writestr('ppt/presentation.xml', pres)
        z.writestr('ppt/theme/theme1.xml', theme)
        z.writestr('ppt/slideMasters/slideMaster1.xml', master)
        z.writestr('ppt/slideMasters/_rels/slideMaster1.xml.rels',
                   rels([('rId1', 'slideLayout', '../slideLayouts/slideLayout1.xml'), ('rId9', 'image', '../media/logo.png')]))
        z.writestr('ppt/slideLayouts/slideLayout1.xml', layout)
        z.writestr('ppt/slides/slide1.xml', slide)
        z.writestr('ppt/slides/_rels/slide1.xml.rels', rels([('rId1', 'slideLayout', '../slideLayouts/slideLayout1.xml')]))
        z.writestr('ppt/media/logo.png', b'\x89PNG fake')


class PptxExtractor(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, 'sample.pptx')
        make_pptx(self.path)
        self.spec = pptx_spec.build(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_slide_size_and_aspect(self):
        self.assertEqual(self.spec['slide_size']['aspect'], '16-9')
        self.assertAlmostEqual(self.spec['slide_size']['cm'][0], 33.87, places=2)

    def test_theme_colors_and_fonts(self):
        colors = self.spec['theme']['colors']
        self.assertEqual(colors['dk2'], '#1F3A5F')
        self.assertEqual(colors['dk1'], '#000000')  # sysClr resolved through lastClr
        fonts = self.spec['theme']['fonts']
        self.assertEqual(fonts['majorFont']['latin'], 'Georgia')
        self.assertEqual(fonts['majorFont']['scripts']['Hans'], 'SimSun')

    def test_master_background_and_title_style(self):
        master = self.spec['masters'][0]
        self.assertEqual(master['background']['hex'], '#F4F1EA')  # bg2 -> lt2
        self.assertEqual(master['text_styles']['titleStyle']['size_pt'], 32.0)
        self.assertEqual(master['text_styles']['titleStyle']['color']['hex'], '#1F3A5F')

    def test_placeholders_logo_and_decor(self):
        shapes = {s['name']: s for s in self.spec['masters'][0]['shapes']}
        title = shapes['Title Placeholder 1']
        self.assertEqual(title['placeholder']['type'], 'title')
        self.assertAlmostEqual(title['position']['x%'], 5.0, places=1)
        self.assertEqual(shapes['Logo']['image'], 'ppt/media/logo.png')
        self.assertIn('licence', shapes['Logo']['note'])
        self.assertEqual(shapes['Band']['fill']['hex'], '#C0392B')

    def test_layout_and_slide(self):
        layout = self.spec['masters'][0]['layouts'][0]
        self.assertEqual(layout['name'], 'Cover')
        self.assertEqual(layout['shapes'][0]['align'], 'center')
        self.assertEqual(layout['shapes'][0]['text_style']['size_pt'], 54.0)
        slide = self.spec['slides'][0]
        self.assertEqual(slide['layout'], 'Cover')
        self.assertEqual(slide['title'], 'Kickoff')
        self.assertEqual(slide['title_run_style']['color']['hex'], '#BCEF59')
        self.assertEqual(self.spec['media'][0]['name'], 'ppt/media/logo.png')

    def test_cli_writes_json_and_rejects_bad_file(self):
        out = os.path.join(self.tmp.name, 'spec.json')
        self.assertEqual(pptx_spec.main([self.path, '-o', out]), 0)
        self.assertEqual(json.loads(Path(out).read_text(encoding='utf-8'))['slides'][0]['title'], 'Kickoff')
        bad = os.path.join(self.tmp.name, 'bad.pptx')
        Path(bad).write_text('not a zip')
        self.assertEqual(pptx_spec.main([bad]), 1)


class Structure(unittest.TestCase):
    def test_files_exist_and_linked(self):
        body = (SKILL / 'SKILL.md').read_text(encoding='utf-8')
        self.assertLessEqual(body.count('\n'), 120)
        self.assertIn('## Gotchas', body)
        self.assertIn('author: DengQi', body)
        for doc in SKILL.glob('references/*.md'):
            self.assertIn(f'references/{doc.name}', body)
        for name in TEMPLATES:
            self.assertTrue((ASSETS / f'{name}.typ').exists(), name)
            self.assertIn(f'{name}.typ', (SKILL / 'references' / 'templates.md').read_text(encoding='utf-8'))

    def test_palette_matches_japanese_theme(self):
        light = json.loads((ROOT / 'research/research-figure/assets/themes/japanese.json').read_text(encoding='utf-8'))['light']
        theme = (ASSETS / 'theme.typ').read_text(encoding='utf-8').lower()
        for key in ('--bg', '--text', '--text-muted', '--color-primary-stroke', '--color-secondary-stroke',
                    '--color-tertiary-stroke', '--color-accent-stroke', '--color-alert-stroke',
                    '--color-neutral-stroke', '--color-primary-fill', '--color-accent-fill'):
            self.assertIn(light[key].lower(), theme, key)

    def test_no_private_paths(self):
        for path in SKILL.rglob('*'):
            if path.is_file() and path.suffix != '.pyc':
                text = path.read_text(encoding='utf-8', errors='ignore')
                self.assertNotRegex(text, r'/(home|opt|Users)/\w+', path)


def find_typst():
    exe = os.environ.get('TYPST') or shutil.which('typst')
    if not exe:
        return None
    out = subprocess.run([exe, '--version'], capture_output=True, text=True).stdout
    m = re.search(r'(\d+)\.(\d+)', out)
    return exe if m and (int(m[1]), int(m[2])) >= (0, 15) else None


TYPST = find_typst()


@unittest.skipUnless(TYPST, 'typst 0.15+ not found (set TYPST or put it on PATH)')
class Compile(unittest.TestCase):
    def compile(self, src, out, root):
        res = subprocess.run([TYPST, 'compile', '--root', str(root), str(src), str(out)],
                             capture_output=True, text=True, timeout=300)
        if res.returncode and re.search(r'download|network|dns|connect', res.stderr, re.I):
            self.skipTest('Typst Universe packages could not be downloaded')
        self.assertEqual(res.returncode, 0, res.stderr)

    def test_every_template_compiles_without_overflow(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in TEMPLATES:
                pdf = Path(tmp) / f'{name}.pdf'
                self.compile(ASSETS / f'{name}.typ', pdf, ASSETS)
                self.assertTrue(pdf.stat().st_size > 5000, name)
                if shutil.which('pdftotext'):
                    self.assertGreaterEqual(len(check_deck.pages(str(pdf))), 6, name)
                    self.assertEqual(self.overflow(str(pdf)), [], f'{name} overflows')

    def overflow(self, pdf):
        seen, prev, bad = [], (None, None), []
        for i, text in enumerate(check_deck.pages(pdf), 1):
            m = re.findall(r'(\d+)\s*/\s*(\d+)\s*$', text.strip(), re.M)
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            n, first = (int(m[-1][0]) if m else None), (lines[0] if lines else '')
            if n is not None and n == prev[0] and first != prev[1]:
                bad.append(i)
            prev = (n, first)
        return bad

    def test_replica_skeleton_compiles(self):
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copy(ASSETS / 'replica-theme.typ', tmp)
            Path(tmp, 'deck.typ').write_text(
                '#import "replica-theme.typ": *\n'
                '#show: replica-theme.with(config-info(title: [Cover], subtitle: [Sub]), footer: [Foot])\n'
                '#title-slide()\n== A claim title\nBody text\n', encoding='utf-8')
            self.compile(Path(tmp) / 'deck.typ', Path(tmp) / 'deck.pdf', tmp)

    def test_syntax_reference_examples_compile(self):
        text = (SKILL / 'references' / 'typst-syntax.md').read_text(encoding='utf-8')
        blocks = [m[2] for m in re.finditer(r'(`{3,})typst\n(.*?)\n\1', text, re.S)]
        self.assertGreaterEqual(len(blocks), 12)
        with tempfile.TemporaryDirectory() as tmp:
            for f in ('theme.typ', 'example-figure.svg'):
                shutil.copy(ASSETS / f, tmp)
            deck = ['#import "theme.typ": *', '#show: jp-theme.with(config-info(title: [T]))']
            for i, b in enumerate(blocks, 1):
                deck.append(f'== Example {i}\n{b}')
            Path(tmp, 'deck.typ').write_text('\n'.join(deck), encoding='utf-8')
            self.compile(Path(tmp) / 'deck.typ', Path(tmp) / 'deck.pdf', tmp)


if __name__ == '__main__':
    unittest.main()
