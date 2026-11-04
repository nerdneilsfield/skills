import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]

def load(skill, filename):
    path = ROOT / 'coding' / skill / 'scripts' / filename
    spec = importlib.util.spec_from_file_location(filename.replace('.', '_'), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def run_record(samples=(10, 11, 12), **changes):
    data = dict(schema_version=1, workload='points-1000-seed7', metric='elapsed_wall', unit='ms',
                direction='lower', scope='end_to_end', samples=list(samples), correctness=True,
                metadata={'python': '3.12', 'dtype': 'float64', 'threads': 1})
    data.update(changes)
    return data

class PythonSkillTools(unittest.TestCase):
    def test_tools_exist_before_loading(self):
        for skill, filename in [('python-environments', 'environment_snapshot.py'), ('python-performance', 'compare_samples.py')]:
            self.assertTrue((ROOT/'coding'/skill/'scripts'/filename).is_file(), filename)

    def test_environment_snapshot_allowlist_no_paths_default(self):
        tool = load('python-environments', 'environment_snapshot.py')
        result = tool.snapshot([], include_paths=False)
        self.assertEqual(set(result), {'schema_version', 'interpreter', 'platform', 'abi', 'venv', 'manager_commands', 'metadata_evidence', 'errors', 'limitations'})
        self.assertNotIn('environment', result)
        self.assertNotIn('executable', result['interpreter'])
        self.assertIn('soabi', result['abi'])
        self.assertTrue(all(isinstance(v, bool) for v in result['manager_commands'].values()))

    def test_environment_abi_output_bound(self):
        tool=load('python-environments','environment_snapshot.py')
        with mock.patch.object(tool.sysconfig,'get_config_var',return_value='x'*10000):
            result=tool.snapshot([],include_paths=False)
        self.assertLessEqual(len(result['abi']['soabi']),256)

    def test_explicit_metadata_only_no_import(self):
        tool = load('python-environments', 'environment_snapshot.py')
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'METADATA'
            p.write_text('Metadata-Version: 2.1\nName: numpy\nVersion: 2.2.0\n\nsecret body not echoed\n')
            r = tool.snapshot([p], include_paths=False)
            self.assertEqual(r['metadata_evidence'][0], {'name': 'numpy', 'version': '2.2.0'})
            self.assertNotIn('secret body', json.dumps(r))
            self.assertFalse(r['errors'])
            p.write_text('Name: first\nName: second\nVersion: 1\n')
            self.assertTrue(tool.snapshot([p], include_paths=False)['errors'])

    def test_metadata_bounds_unicode_and_missing(self):
        tool = load('python-environments', 'environment_snapshot.py')
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'METADATA';p.write_bytes(b'\xff')
            self.assertTrue(tool.snapshot([p], include_paths=False)['errors'])
            self.assertTrue(tool.snapshot([p.parent/'missing'], include_paths=False)['errors'])
            self.assertTrue(tool.snapshot([p.parent], include_paths=False)['errors'])
            with self.assertRaises(ValueError):tool.snapshot([p]*17, include_paths=False)
        stream = mock.MagicMock();stream.__enter__.return_value=stream;stream.read.return_value=b'x'*(tool.MAX_BYTES+1)
        with mock.patch.object(tool, 'open_regular', return_value=stream):
            with self.assertRaises(ValueError): tool.read_metadata(Path('fixture'))
        stream.read.assert_called_once_with(tool.MAX_BYTES+1)

    def test_comparable_summary_and_noise_is_descriptive(self):
        tool = load('python-performance', 'compare_samples.py')
        result = tool.compare(run_record(), run_record((8,9,10)), [])
        self.assertEqual(result['status'], 'comparable')
        self.assertEqual(result['baseline']['median'], 11)
        self.assertAlmostEqual(result['improvement_percent'], 200/11)
        self.assertIn('not_statistical_significance', result['limitations'])

    def test_incompatible_and_explicit_metadata_variable(self):
        tool = load('python-performance', 'compare_samples.py')
        for change in ({'workload':'other'}, {'scope':'kernel_only'}, {'unit':'s'}, {'direction':'higher'}, {'correctness':False}, {'metadata':{'python':'3.13','dtype':'float64','threads':1}}):
            self.assertEqual(tool.compare(run_record(),run_record(**change),[])['status'], 'incomparable')
        changed=run_record(metadata={'python':'3.13','dtype':'float64','threads':1})
        self.assertEqual(tool.compare(run_record(), changed, ['python'])['status'], 'comparable')
        with self.assertRaises(ValueError):tool.compare(run_record(), changed, ['missing'])

    def test_metadata_types_not_equal(self):
        tool=load('python-performance','compare_samples.py')
        self.assertEqual(tool.compare(run_record(),run_record(metadata={'python':'3.12','dtype':'float64','threads':True}),[])['status'],'incomparable')

    def test_higher_direction_nested_metadata_and_duplicate_keys(self):
        tool=load('python-performance','compare_samples.py')
        r=tool.compare(run_record((10,10,10),direction='higher'),run_record((20,20,20),direction='higher'),[])
        self.assertEqual(r['improvement_percent'],100)
        self.assertEqual(tool.compare(run_record(metadata={'x':{'thread':[1]}}),run_record(metadata={'x':{'thread':[True]}}),[])['status'],'incomparable')
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'r.json';p.write_text('{"x":1,"x":2}')
            with self.assertRaises(ValueError):tool.read_json(p)

    def test_bad_samples_zero_extreme_and_tiny(self):
        tool=load('python-performance','compare_samples.py')
        for samples in ([1,2], [1,-1,3], [1,float('nan'),3], [1,True,3], [1,10**400,3]):
            with self.assertRaises(ValueError):tool.compare(run_record(samples),run_record(),[])
        self.assertIsNone(tool.compare(run_record((0,0,0)),run_record(),[])['improvement_percent'])
        r=tool.compare(run_record((1e308,)*4),run_record((1e308,)*4),[])
        self.assertEqual(r['baseline']['median'],1e308)
        r=tool.compare(run_record((5e-324,)*4),run_record((1e308,)*4),[])
        self.assertEqual(r['baseline']['median'],5e-324)
        self.assertIsNone(r['improvement_percent'])

    def test_json_read_bound_and_invalid_constants(self):
        tool=load('python-performance','compare_samples.py')
        stream=mock.MagicMock();stream.__enter__.return_value=stream;stream.read.return_value=b'x'*(tool.MAX_BYTES+1)
        with mock.patch.object(tool,'open_regular',return_value=stream):
            with self.assertRaises(ValueError):tool.read_json(Path('fixture'))
        stream.read.assert_called_once_with(tool.MAX_BYTES+1)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'a.json';p.write_text('{"x":NaN}')
            with self.assertRaises(ValueError):tool.read_json(p)

    def test_cli_help_and_compare_exit_codes(self):
        for skill,name in [('python-environments','environment_snapshot.py'),('python-performance','compare_samples.py')]:
            cmd=[sys.executable,'-I',str(ROOT/'coding'/skill/'scripts'/name),'--help']
            self.assertEqual(subprocess.run(cmd,capture_output=True,timeout=5).returncode,0)
        with tempfile.TemporaryDirectory() as d:
            a=Path(d)/'a.json';b=Path(d)/'b.json';a.write_text(json.dumps(run_record()));b.write_text(json.dumps(run_record(correctness=False)))
            cmd=[sys.executable,'-I',str(ROOT/'coding/python-performance/scripts/compare_samples.py'),str(a),str(b)]
            r=subprocess.run(cmd,capture_output=True,timeout=5)
            self.assertEqual(r.returncode,1);self.assertEqual(json.loads(r.stdout)['status'],'incomparable')
            b.write_text('not json');r=subprocess.run(cmd,capture_output=True,timeout=5)
            self.assertEqual(r.returncode,2);self.assertIn('error',json.loads(r.stdout))

if __name__=='__main__':unittest.main()
