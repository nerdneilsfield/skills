"""Bounded offline fixture: remove redundant parsing without retaining a cache.

This is NOT a general benchmark runner. It executes only these local functions,
reports wall and process CPU separately, and makes no speedup claim.
"""
import argparse
import json
import time


def make_rows(count):
    if type(count) is not int or not 0 <= count <= 100000:
        raise ValueError('rows must be an integer in [0, 100000]')
    return [json.dumps({'value': i % 97, 'enabled': i % 3 != 0}) for i in range(count)]


def baseline(rows):
    total = 0
    calls = 0
    for row in rows:
        enabled = json.loads(row)['enabled']
        value = json.loads(row)['value']
        calls += 2
        if enabled:
            total += value * value
    return {'total': total, 'parse_calls': calls}


def batched(rows):
    # Parse once within the row's lifetime. No unbounded cross-request cache.
    total = 0
    calls = 0
    for row in rows:
        record = json.loads(row)
        calls += 1
        if record['enabled']:
            total += record['value'] * record['value']
    return {'total': total, 'parse_calls': calls}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rows', type=int, default=10000)
    parser.add_argument('--repeat', type=int, default=3)
    args = parser.parse_args()
    if not 0 <= args.rows <= 100000 or not 1 <= args.repeat <= 20:
        parser.error('rows: 0..100000; repeat: 1..20')
    rows = make_rows(args.rows)  # Input creation is outside this measured scope.
    expected = baseline(rows)['total']
    observations = []
    for repeat in range(args.repeat):
        # Alternate order to reduce order bias; this does not eliminate noise.
        variants = (baseline, batched) if repeat % 2 == 0 else (batched, baseline)
        for function in variants:
            cpu = time.process_time()
            wall = time.perf_counter()
            result = function(rows)
            elapsed = time.perf_counter() - wall
            consumed = time.process_time() - cpu
            if result['total'] != expected:
                raise AssertionError('result changed')
            observations.append({'variant': function.__name__, 'wall_seconds': elapsed,
                                 'process_cpu_seconds': consumed, **result})
    print(json.dumps({'scope': 'parse/filter/reduce; excludes input creation',
                      'rows': args.rows, 'correctness': True, 'observations': observations}, indent=2))


if __name__ == '__main__':
    main()
