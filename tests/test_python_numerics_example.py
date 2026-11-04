import importlib.util
from pathlib import Path
import unittest
if importlib.util.find_spec("numpy") is None:
    np = None
else:
    # An installed but broken package is an import ERROR, not a missing-dependency skip.
    import numpy as np

ASSET = Path(__file__).resolve().parents[1] / 'coding/python-numerics/assets/blocked_distances.py'

class Packaging(unittest.TestCase):
    def test_asset_exists(self):
        self.assertTrue(ASSET.is_file(), 'Missing runnable numerical asset')

@unittest.skipIf(np is None, 'NumPy unavailable; no numerical execution claimed')
class NumericalExample(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not ASSET.exists():
            raise unittest.SkipTest('Asset not implemented; packaging test is RED')
        spec = importlib.util.spec_from_file_location('blocked_distances', ASSET)
        cls.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.mod)

    def test_reference_float_dtypes(self):
        for dtype in (np.float32, np.float64):
            x = np.arange(15, dtype=dtype).reshape(5, 3) / 7
            y = np.arange(21, dtype=dtype).reshape(7, 3) / 9
            expected = ((x[:, None, :] - y[None, :, :]) ** 2).sum(axis=2).min(axis=1)
            result, plan = self.mod.nearest_squared(x, y, budget_bytes=256)
            self.assertEqual(result.shape, expected.shape)
            np.testing.assert_allclose(result, expected, rtol=1e-6, atol=1e-7)
            self.assertEqual(result.dtype, dtype)
            self.assertLessEqual(plan['explicit_peak_bytes'], 256)

    def test_noncontiguous_readonly_and_no_mutation(self):
        base = np.arange(60, dtype=np.float64).reshape(10, 6)
        x, y = base[::-2, ::2], base[1::2, ::2]
        original = base.copy()
        x.flags.writeable = False
        actual, _ = self.mod.nearest_squared(x, y, budget_bytes=192)
        expected = ((x[:, None] - y[None]) ** 2).sum(axis=2).min(axis=1)
        np.testing.assert_allclose(actual, expected)
        np.testing.assert_array_equal(base, original)

    def test_alias_input_is_safe(self):
        x = np.arange(12, dtype=np.float64).reshape(4, 3)
        result, _ = self.mod.nearest_squared(x, x, budget_bytes=192)
        np.testing.assert_array_equal(result, np.zeros(4))

    def test_budget_rejects_before_output_allocation(self):
        with self.assertRaises(ValueError):
            self.mod.nearest_squared(np.zeros((5, 3)), np.zeros((2, 3)), budget_bytes=40)

    def test_invalid_budget(self):
        for b in (True, 0, -1, 1.5):
            with self.assertRaises((ValueError, TypeError)):
                self.mod.nearest_squared(np.zeros((1, 2)), np.zeros((1, 2)), budget_bytes=b)

    def test_dtype_contract(self):
        for x, y in ((np.zeros((1, 2), dtype=int), np.zeros((1, 2), dtype=int)),
                     (np.zeros((1, 2), dtype=np.float32), np.zeros((1, 2)))):
            with self.assertRaises(TypeError):
                self.mod.nearest_squared(x, y)

    def test_shape_contract(self):
        for x, y in ((np.zeros(2), np.zeros((1, 2))),
                     (np.zeros((1, 2)), np.zeros((1, 3))),
                     (np.zeros((1, 0)), np.zeros((1, 0))),
                     (np.zeros((1, 2)), np.zeros((0, 2)))):
            with self.assertRaises(ValueError):
                self.mod.nearest_squared(x, y)

    def test_empty_queries(self):
        out, plan = self.mod.nearest_squared(np.zeros((0, 2)), np.zeros((1, 2)))
        self.assertEqual(out.shape, (0,))
        self.assertEqual(plan['explicit_peak_bytes'], 0)

    def test_nonfinite_rejected(self):
        for value in (np.nan, np.inf, -np.inf):
            with self.assertRaises(ValueError):
                self.mod.nearest_squared(np.array([[value, 0.]]), np.zeros((1, 2)))
            with self.assertRaises(ValueError):
                self.mod.nearest_squared(np.zeros((1, 2)), np.array([[value, 0.]]))

    def test_overflow_not_silently_accepted(self):
        with self.assertRaises(FloatingPointError):
            self.mod.nearest_squared(np.array([[1e200]]), np.zeros((1, 1)))

    def test_close_large_offsets(self):
        x = np.array([[1e8, 1e8]])
        y = np.array([[1e8 + 1, 1e8 + 2]])
        out, _ = self.mod.nearest_squared(x, y)
        self.assertEqual(out[0], 5.)

if __name__ == '__main__':
    unittest.main()
