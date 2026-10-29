"""Run with python -m unittest discover -s tests -v; no third-party imports."""
import importlib.util
import json
import errno
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
def load(skill, filename):
    path = ROOT / 'coding' / skill / 'scripts' / filename
    spec = importlib.util.spec_from_file_location(filename[:-3], path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class ToolTests(unittest.TestCase):
    def test_snapshot_contains_only_documented_fields(self):
        tool = load('cpp-debug', 'environment_snapshot.py')
        result = tool.snapshot()
        self.assertEqual(set(result), {'schema_version', 'system', 'release', 'machine', 'python', 'logical_cpu_count', 'tools', 'limitations'})
        self.assertNotIn('environment', result)
        self.assertNotIn('hostname', result)
        self.assertIn('cmake', result['tools'])

    def test_vendor_valid_and_no_mutation(self):
        tool = load('cpp-project-init', 'check_vendor_manifest.py')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root/'third_party/lib').mkdir(parents=True)
            (root/'third_party/lib/LICENSE').write_text('Example license text')
            data = {'dependencies': [{'name':'lib','revision':'v1.2','upstream':'https://example.com/lib','source':'third_party/lib','licenses':['third_party/lib/LICENSE']}]}
            before = sorted(str(p) for p in root.rglob('*'))
            self.assertEqual(tool.validate(data, root), [])
            self.assertEqual(before, sorted(str(p) for p in root.rglob('*')))

    def test_vendor_missing_empty_and_escape(self):
        tool = load('cpp-project-init', 'check_vendor_manifest.py')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = {'dependencies':[{'name':'x','revision':'','upstream':'not-url','source':'../outside','licenses':[]}]}
            self.assertGreaterEqual(len(tool.validate(data, root)), 4)
            self.assertTrue(tool.validate({'dependencies':'bad'}, root))

    def test_vendor_duplicate_and_symlink_escape(self):
        tool = load('cpp-project-init', 'check_vendor_manifest.py')
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside:
            root = Path(tmp)
            try:
                (root/'lib').symlink_to(outside, target_is_directory=True)
            except OSError as exc:
                if exc.errno in (errno.EPERM,errno.EACCES,errno.ENOSYS,errno.EOPNOTSUPP) or getattr(exc,'winerror',None)==1314:
                    self.skipTest('OS does not permit symlink creation')
                raise
            dep={'name':'x','revision':'v1','upstream':'https://example.com','source':'lib','licenses':['missing']}
            errors=tool.validate({'dependencies':[dep,dep]}, root)
            self.assertTrue(any('outside' in e for e in errors))
            self.assertTrue(any('duplicate' in e for e in errors))

    def run_data(self, samples, **kw):
        value={'metric':'latency','unit':'ms','direction':'lower','samples':samples,'correctness_passed':True,'metadata':{'input':'sha256:abc','compiler':'clang18','threads':1}}
        value.update(kw); return value

    def test_comparison_descriptive_and_noisy(self):
        tool=load('cpp-performance','compare_benchmarks.py')
        result=tool.compare(self.run_data([95,100,105]),self.run_data([94,98,102]))
        self.assertEqual(result['status'],'comparable')
        self.assertEqual(result['spread_relation'],'overlapping_ranges')
        self.assertAlmostEqual(result['relative_improvement_percent'],2)
        self.assertFalse(result['statistical_significance_established'])
        self.assertEqual(result['unit'],'ms')
        self.assertEqual(result['metric'],'latency')
        self.assertEqual(result['direction'],'lower')

    def test_metadata_mismatch_and_explicit_allowance(self):
        tool=load('cpp-performance','compare_benchmarks.py')
        before=self.run_data([10,11,12]); after=self.run_data([7,8,9],metadata={'input':'sha256:abc','compiler':'clang19','threads':1})
        self.assertEqual(tool.compare(before,after)['status'],'incomparable')
        result=tool.compare(before,after,allow_metadata_difference=['compiler'])
        self.assertEqual(result['status'],'comparable')
        self.assertEqual(result['allowed_metadata_differences'],['compiler'])

    def test_metadata_type_changes_are_not_equal(self):
        tool=load('cpp-performance','compare_benchmarks.py')
        for before_value,after_value in [(1,True),({'threads':[1]}, {'threads':[True]}),(1,1.0)]:
            a=self.run_data([1,2,3],metadata={'config':before_value})
            b=self.run_data([1,2,3],metadata={'config':after_value})
            self.assertEqual(tool.compare(a,b)['status'],'incomparable')

    def test_zero_failed_correctness_units_and_direction(self):
        tool=load('cpp-performance','compare_benchmarks.py')
        self.assertIsNone(tool.compare(self.run_data([0,0,0]),self.run_data([0,0,0]))['relative_improvement_percent'])
        self.assertEqual(tool.compare(self.run_data([1,2,3]),self.run_data([1,2,3],correctness_passed=False))['status'],'incomparable')
        self.assertEqual(tool.compare(self.run_data([1,2,3]),self.run_data([1,2,3],unit='s'))['status'],'incomparable')
        self.assertEqual(tool.compare(self.run_data([1,2,3]),self.run_data([1,2,3],direction='higher'))['status'],'incomparable')

    def test_invalid_samples_and_schema(self):
        tool=load('cpp-performance','compare_benchmarks.py')
        for samples in [[1], [1,float('nan'),3], [1,True,3], [-1,2,3]]:
            with self.assertRaises(ValueError): tool.compare(self.run_data(samples),self.run_data([1,2,3]))
        with self.assertRaises(ValueError): tool.compare({}, {})
        with self.assertRaises(ValueError): tool.compare(self.run_data([1,2,3],correctness_passed='true'),self.run_data([1,2,3]))

    def test_cli_help_and_invalid_input(self):
        for skill, filename in [('cpp-debug', 'environment_snapshot.py'), ('cpp-project-init', 'check_vendor_manifest.py'), ('cpp-performance', 'compare_benchmarks.py')]:
            script=ROOT/'coding'/skill/'scripts'/filename
            result=subprocess.run([sys.executable,str(script),'--help'],capture_output=True,text=True,timeout=5)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn('usage:',result.stdout)
        script=ROOT/'coding/cpp-performance/scripts/compare_benchmarks.py'
        with tempfile.TemporaryDirectory() as tmp:
            bad=Path(tmp)/'bad.json'; bad.write_text('{invalid')
            result=subprocess.run([sys.executable,str(script),str(bad),str(bad)],capture_output=True,text=True,timeout=5)
            self.assertEqual(result.returncode,2)
            self.assertIn('input error',result.stderr)

    def test_oversized_read_is_bounded(self):
        for skill, file in [('cpp-performance','compare_benchmarks.py'),('cpp-project-init','check_vendor_manifest.py')]:
            tool=load(skill,file)
            stream=mock.MagicMock()
            stream.__enter__.return_value=stream
            stream.read.return_value=b' '*(tool.MAX_BYTES+1)
            path=mock.MagicMock()
            path.open.return_value=stream
            with self.assertRaises(ValueError): tool.load(path)
            stream.read.assert_called_once_with(tool.MAX_BYTES+1)

    def test_large_finite_samples_do_not_overflow_output(self):
        tool=load('cpp-performance','compare_benchmarks.py')
        result=tool.compare(self.run_data([1e308]*4),self.run_data([1e308]*4))
        self.assertEqual(result['before']['median'],1e308)
        json.dumps(result,allow_nan=False)
        result=tool.compare(self.run_data([1e-308]*3),self.run_data([1e308]*3))
        self.assertIsNone(result['relative_improvement_percent'])
        self.assertIn('unavailable',result)
        json.dumps(result,allow_nan=False)
        with self.assertRaises(ValueError): tool.compare(self.run_data([10**500]*3),self.run_data([1,2,3]))

    def test_unknown_metadata_override_rejected(self):
        tool=load('cpp-performance','compare_benchmarks.py')
        with self.assertRaises(ValueError): tool.compare(self.run_data([1,2,3]),self.run_data([1,2,3]),['typo'])

    def test_higher_is_better(self):
        tool=load('cpp-performance','compare_benchmarks.py')
        a=self.run_data([9,10,11],direction='higher'); b=self.run_data([19,20,21],direction='higher')
        self.assertEqual(tool.compare(a,b)['relative_improvement_percent'],100)

if __name__ == '__main__':
    unittest.main()
