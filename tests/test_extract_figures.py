import importlib.util
import shutil
import struct
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('extract_figures', ROOT / 'research/qi-read-paper/scripts/extract_figures.py')
ef = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ef)


def tiny_pdf(rotate):
    """One 200x100 pt page with the given /Rotate."""
    content = b'0 0 0 rg 0 0 50 50 re f'
    objs = [b'<</Type/Catalog/Pages 2 0 R>>', b'<</Type/Pages/Kids[3 0 R]/Count 1>>',
            b'<</Type/Page/Parent 2 0 R/MediaBox[0 0 200 100]/Rotate %d/Contents 4 0 R/Resources<<>>>>' % rotate,
            b'<</Length %d>>\nstream\n' % len(content) + content + b'\nendstream']
    out, offs = b'%PDF-1.4\n', []
    for i, o in enumerate(objs, 1):
        offs.append(len(out))
        out += b'%d 0 obj\n' % i + o + b'\nendobj\n'
    x = len(out)
    out += b'xref\n0 5\n0000000000 65535 f \n' + b''.join(b'%010d 00000 n \n' % o for o in offs)
    return out + b'trailer<</Size 5/Root 1 0 R>>\nstartxref\n%d\n%%%%EOF\n' % x


class Pages(unittest.TestCase):
    def test_ranges_and_bounds(self):
        self.assertEqual(ef.parse_pages('1,3-4,3', 5), [1, 3, 4])
        for bad in ('0', '6', '4-2', 'x'):
            with self.assertRaises(ef.FigureError):
                ef.parse_pages(bad, 5)


@unittest.skipUnless(shutil.which('pdfinfo') and shutil.which('pdftoppm'), 'needs poppler')
class Rotation(unittest.TestCase):
    def test_crop_uses_displayed_size(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            for rot, expect in ((0, (611, 306)), (90, (306, 611)), (270, (306, 611))):
                pdf = d / f'r{rot}.pdf'
                pdf.write_bytes(tiny_pdf(rot))
                self.assertEqual(ef.page_size(pdf, 1), (200.0, 100.0) if rot == 0 else (100.0, 200.0))
                out = d / f'o{rot}.png'
                ef.crop(pdf, 1, [0, 0, 100, 100], out)
                self.assertEqual(struct.unpack('>II', out.read_bytes()[16:24]), expect)
            with self.assertRaises(ef.FigureError):
                ef.crop(pdf, 2, [0, 0, 10, 10], d / 'x.png')


if __name__ == '__main__':
    unittest.main()
