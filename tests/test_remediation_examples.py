"""Offline original C++ examples: compile/run when an already installed compiler exists."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'coding/cpp-performance/assets/remediation-examples/remediation_examples.cpp'
class RemediationExamples(unittest.TestCase):
    def test_examples_compile_and_preserve_results(self):
        compiler=shutil.which('c++')
        if compiler is None:
            self.skipTest('No installed c++; C++ fixture validation unavailable, no installation attempted')
        if os.name=='nt':
            self.skipTest('This smoke runner uses Unix-style compiler flags; use documented native commands on Windows')
        with tempfile.TemporaryDirectory() as tmp:
            for name,flags in [('debug',['-O0','-g']),('release',['-O2','-DNDEBUG'])]:
                binary=Path(tmp)/name
                build=subprocess.run([compiler,'-std=c++20','-Wall','-Wextra','-Wpedantic','-Werror','-pthread',*flags,str(SOURCE),'-o',str(binary)],capture_output=True,text=True,timeout=90)
                self.assertEqual(build.returncode,0,build.stderr)
                result=subprocess.run([str(binary)],capture_output=True,text=True,timeout=10)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertIn('all correctness checks passed',result.stdout)

if __name__=='__main__':unittest.main()
