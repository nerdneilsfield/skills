import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / 'writing' / 'academic-writing' / 'scripts' / 'check_paper.py'

MAIN = r"""\documentclass{article}
\begin{document}
\begin{abstract}
We present a design in 28 nm that reaches 3.2 GOPS/W and 41.7 mW at 500 MHz.
\end{abstract}
\section{Intro}\label{sec:intro}
Prior work~\cite{good,missing} exists. See Fig.~\ref{fig:arch} and Table~\ref{tab:none}.
% TODO hidden in a comment is ignored
Our chip runs at 500 MHz in 28 nm and draws 41.7 mW. TODO fill in.
\begin{figure}\caption{Arch}\label{fig:arch}\end{figure}
\label{fig:unused}
\input{part}
\bibliography{refs}
\end{document}
"""
BIB = """@article{good, author={A. B}, title={T}, year={2020}}
@article{extra, author={C. D}, title={U}}
"""


class CheckPaper(unittest.TestCase):
    def run_tool(self, *extra):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / 'main.tex').write_text(MAIN)
            (d / 'part.tex').write_text('Extra text \\label{sec:intro}\n')
            (d / 'refs.bib').write_text(BIB)
            return subprocess.run([sys.executable, '-I', str(TOOL), str(d / 'main.tex'), '--json', *extra],
                                  capture_output=True, text=True)

    def test_reports_expected_findings(self):
        r = self.run_tool()
        self.assertEqual(r.returncode, 1)
        found = {(i['code'], i['message']) for i in json.loads(r.stdout)}
        codes = {c for c, _ in found}
        self.assertTrue({'undefined-citation', 'undefined-reference', 'duplicate-label', 'unused-label',
                         'unused-bib-entry', 'incomplete-bib-entry', 'placeholder',
                         'abstract-number-not-in-body'} <= codes)
        msgs = ' '.join(m for _, m in found)
        self.assertIn("'missing'", msgs)
        self.assertIn('3.2', msgs)
        self.assertNotIn('abstract number 28 ', msgs)
        self.assertNotIn('abstract number 41.7 ', msgs)

    def test_clean_paper_passes(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / 'm.tex').write_text('\\begin{abstract}Gain of 12.5\\% .\\end{abstract}\n'
                                     'Gain of 12.5\\% shown~\\cite{k} in \\ref{a}.\\label{a}\n\\bibliography{r}\n')
            (d / 'r.bib').write_text('@misc{k, title={T}}\n')
            r = subprocess.run([sys.executable, '-I', str(TOOL), str(d / 'm.tex'), '--strict'],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout)


if __name__ == '__main__':
    unittest.main()
