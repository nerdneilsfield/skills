import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1] / 'coding/python-ml'
AUDIT = ROOT / 'scripts/split_manifest_audit.py'

class SplitAudit(unittest.TestCase):
    def run_audit(self, rows, *args):
        self.assertTrue(AUDIT.is_file(), 'Missing split audit implementation')
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'split.json'
            p.write_text(json.dumps(rows), encoding='utf-8')
            return subprocess.run([sys.executable, str(AUDIT), str(p), *args], capture_output=True, text=True, timeout=10)

    def test_valid_disjoint_groups(self):
        rows = [{'id':'a','group':'g1','split':'train'}, {'id':'b','group':'g2','split':'test'}]
        result = self.run_audit(rows, '--groups')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['rows'], 2)

    def test_overlap_rejected_without_printing_ids(self):
        result = self.run_audit([{'id':'PRIVATE','split':'train'}, {'id':'PRIVATE','split':'test'}])
        self.assertEqual(result.returncode, 1)
        self.assertNotIn('PRIVATE', result.stdout + result.stderr)

    def test_group_overlap(self):
        result = self.run_audit([{'id':'a','group':'same','split':'train'}, {'id':'b','group':'same','split':'test'}], '--groups')
        self.assertEqual(result.returncode, 1)

    def test_group_repetition_inside_train_allowed(self):
        rows = [{'id':str(i),'group':'g','split':'train'} for i in range(3)] + [{'id':'t','group':'other','split':'test'}]
        self.assertEqual(self.run_audit(rows, '--groups').returncode, 0)

    def test_chronology_and_gap(self):
        rows = [{'id':'a','split':'train','time':10}, {'id':'b','split':'test','time':12}]
        self.assertEqual(self.run_audit(rows, '--time-gap','1').returncode, 0)
        self.assertEqual(self.run_audit(rows, '--time-gap','3').returncode, 1)

    @unittest.skipUnless(hasattr(os, 'mkfifo'), 'FIFO unavailable on this platform')
    def test_fifo_rejected_without_blocking(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'fifo'
            os.mkfifo(path)
            result = subprocess.run([sys.executable, str(AUDIT), str(path)], capture_output=True, timeout=3)
            self.assertEqual(result.returncode, 2)

    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'data.json'
            path.write_text('[{"id":"a","split":"train"},{"id":"b","split":"test"}]')
            link = Path(tmp) / 'link.json'
            try:
                link.symlink_to(path)
            except OSError:
                self.skipTest('symlink creation unavailable')
            result = subprocess.run([sys.executable, str(AUDIT), str(link)], capture_output=True, timeout=3)
            self.assertEqual(result.returncode, 2)

    def test_extreme_finite_chronology(self):
        rows = [{'id':'a','split':'train','time':-1e308}, {'id':'b','split':'test','time':1e308}]
        self.assertEqual(self.run_audit(rows, '--time-gap','1e308').returncode, 0)

    def test_equal_boundary_is_not_future(self):
        rows = [{'id':'a','split':'train','time':10}, {'id':'b','split':'test','time':10}]
        self.assertEqual(self.run_audit(rows, '--time-gap','0').returncode, 1)

    def test_time_and_group_checks_explicitly_unchecked(self):
        result = self.run_audit([{'id':'a','split':'train'}, {'id':'b','split':'test'}])
        report = json.loads(result.stdout)
        self.assertIsNone(report['group_overlap_count'])
        self.assertIsNone(report['chronology_conflicts'])

    def test_read_size_is_bounded_even_if_file_grows(self):
        spec = importlib.util.spec_from_file_location('ml_audit', AUDIT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'metadata.json'
            path.write_text('[]')
            original_fdopen = module.os.fdopen
            sizes = []
            class RecordingStream:
                def __init__(self, stream):
                    self.stream = stream
                def __enter__(self):
                    return self
                def __exit__(self, *args):
                    self.stream.close()
                def read(self, size):
                    sizes.append(size)
                    return self.stream.read(size)
            with mock.patch.object(module.os, 'fdopen', side_effect=lambda fd, mode: RecordingStream(original_fdopen(fd, mode))):
                self.assertEqual(module.read_rows(path), [])
            self.assertEqual(sizes, [module.MAX_BYTES + 1])

    def test_file_bounds_and_duplicate_json_keys(self):
        self.assertTrue(AUDIT.exists())
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'data.json'
            for content in [' ' * 2_000_001, '[{"id":"a","id":"b","split":"train"}]']:
                path.write_text(content)
                result = subprocess.run([sys.executable, str(AUDIT), str(path)], capture_output=True, timeout=10)
                self.assertEqual(result.returncode, 2)

    def test_nonfinite_missing_bool_time(self):
        for value in [float('nan'), True, None]:
            result = self.run_audit([{'id':'a','split':'train','time':value}, {'id':'b','split':'test','time':20}], '--time-gap','0')
            self.assertEqual(result.returncode, 2)

    def test_invalid_or_empty(self):
        for rows in [[], {}, [{'id':'a','split':'train'}], [{'id':'a','split':'test'}, {'id':'b','split':'wrong'}]]:
            self.assertEqual(self.run_audit(rows).returncode, 2)

    def test_duplicate_within_split_rejected(self):
        rows = [{'id':'a','split':'train'}, {'id':'a','split':'train'}, {'id':'t','split':'test'}]
        self.assertEqual(self.run_audit(rows).returncode, 1)

    def test_extra_columns_and_missing_group_rejected(self):
        rows = [{'id':'a','split':'train','payload':'not allowed'}, {'id':'b','split':'test'}]
        self.assertEqual(self.run_audit(rows).returncode, 2)
        self.assertEqual(self.run_audit([{'id':'a','split':'train'}, {'id':'b','split':'test'}], '--groups').returncode, 2)

class OptionalExamples(unittest.TestCase):
    def run_example(self, name, dependency):
        asset = ROOT / 'assets' / name
        self.assertTrue(asset.exists(), 'Missing example ' + name)
        if importlib.util.find_spec(dependency) is None:
            self.skipTest(dependency + ' unavailable; no framework execution claimed')
        result = subprocess.run([sys.executable, str(asset)], capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_sklearn_train_only_scaler(self):
        report = self.run_example('classical_pipeline.py', 'sklearn')
        self.assertTrue(report['train_only_scaler'])
        self.assertEqual(report['test_samples'], 24)
        self.assertGreaterEqual(report['balanced_accuracy'], 0)
        self.assertLessEqual(report['balanced_accuracy'], 1)

    def test_torch_train_eval_invariants(self):
        report = self.run_example('torch_train_eval.py', 'torch')
        self.assertTrue(report['parameters_changed'])
        self.assertFalse(report['evaluation_requires_grad'])
        self.assertTrue(report['evaluation_preserved_parameters'])
        self.assertEqual(report['device'], 'cpu')
        self.assertEqual(report['samples'], 32)

if __name__ == '__main__':
    unittest.main()
