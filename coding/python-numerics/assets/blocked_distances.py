"""CPU NumPy teaching asset: bounded explicit work arrays, not an RSS limiter.

Computes each query's minimum squared Euclidean distance. Inputs are unchanged;
matching float32/float64 ndarrays only, finite values, positive feature count,
at least one target. Arithmetic overflow raises rather than returning a false
minimum. Budget covers output + reusable difference buffer + reduction buffer.
Python/NumPy runtime, allocator overhead, inputs and iterator buffers are excluded.
"""
import math
import numpy as np


def nearest_squared(x, y, *, budget_bytes=1048576):
    if isinstance(budget_bytes, bool) or not isinstance(budget_bytes, int):
        raise TypeError('budget_bytes must be an integer')
    if budget_bytes <= 0:
        raise ValueError('budget_bytes must be positive')
    if not isinstance(x, np.ndarray) or not isinstance(y, np.ndarray):
        raise TypeError('pass ndarrays explicitly; no hidden input conversion')
    if x.dtype not in (np.dtype('float32'), np.dtype('float64')) or y.dtype != x.dtype:
        raise TypeError('matching native float32 or float64 required')
    if x.ndim != 2 or y.ndim != 2 or x.shape[1] != y.shape[1]:
        raise ValueError('expected (queries, features), (targets, features)')
    n, d = x.shape
    m = y.shape[0]
    if d == 0 or m == 0:
        raise ValueError('positive feature and target counts required')
    # Scalar iteration is deliberately conservative: validation does not create
    # an input-sized boolean array. It is counted in end-to-end timing.
    if any(not math.isfinite(float(v)) for a in (x, y) for v in a.flat):
        raise ValueError('inputs must be finite')
    if n == 0:
        return np.empty(0, dtype=x.dtype), {'block_targets': 0, 'explicit_peak_bytes': 0}
    size = x.dtype.itemsize
    output_bytes = n * size
    per_target = (d + 1) * size
    block = min(m, (budget_bytes - output_bytes) // per_target)
    if block < 1:
        raise ValueError('budget cannot hold output and one target work row')
    out = np.empty(n, dtype=x.dtype)
    diff = np.empty((block, d), dtype=x.dtype)
    squared = np.empty(block, dtype=x.dtype)
    with np.errstate(over='raise', invalid='raise'):
        for i in range(n):
            best = math.inf
            for start in range(0, m, block):
                count = min(block, m - start)
                work = diff[:count]
                np.subtract(x[i], y[start:start + count], out=work)
                np.square(work, out=work)
                np.sum(work, axis=1, out=squared[:count])
                best = min(best, float(squared[:count].min()))
            out[i] = best
    return out, {'block_targets': block,
                 'explicit_peak_bytes': output_bytes + block * per_target}


if __name__ == '__main__':
    queries = np.array([[0., 0.], [3., 4.]])
    targets = np.array([[1., 0.], [3., 5.], [8., 8.]])
    distances, plan = nearest_squared(queries, targets, budget_bytes=64)
    print({'minimum_squared_distances': distances.tolist(), 'allocation_plan': plan,
           'numpy_version': np.__version__, 'device': 'CPU'})
