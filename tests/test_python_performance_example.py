"""Correctness, boundedness and repeatability; no wall-clock speed assertions."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

PATH = Path(__file__).resolve().parents[1] / 'coding/python-performance/assets/batch_pipeline.py'

class BatchPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('batch_pipeline', PATH)
        cls.example = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.example)

    def test_same_work_and_results(self):
        rows = self.example.make_rows(100)
        self.assertEqual(self.example.baseline(rows)['total'], self.example.batched(rows)['total'])

    def test_empty_and_one(self):
        for size in (0, 1):
            rows = self.example.make_rows(size)
            self.assertEqual(self.example.baseline(rows)['total'], self.example.batched(rows)['total'])

    def test_input_validation(self):
        for invalid in (-1, 100001, True, 1.5):
            with self.assertRaises(ValueError):
                self.example.make_rows(invalid)

    def test_parse_once_per_row(self):
        rows = self.example.make_rows(17)
        self.assertEqual(self.example.batched(rows)['parse_calls'], 17)
        self.assertEqual(self.example.baseline(rows)['parse_calls'], 34)

    def test_cli_bounded(self):
        result = subprocess.run([sys.executable, str(PATH), '--rows', '-1'], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)

if __name__ == '__main__':
    unittest.main()
