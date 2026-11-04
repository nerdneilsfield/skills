#!/usr/bin/env python3
"""Compare two explicit bounded JSON sample records; never run a benchmark/profiler.
Python 3.9+ stdlib. Exit 0 comparable, 1 incomparable, 2 malformed input.
Medians/MAD describe observed samples; no significance or universal speed claim.
"""
import argparse
import json
import math
import os
from pathlib import Path
import stat
import sys

MAX_BYTES = 1024 * 1024
MAX_SAMPLES = 100000


def open_regular(path):
    if not stat.S_ISREG(path.stat().st_mode): raise ValueError('not a regular file')
    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NONBLOCK', 0))
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode): raise ValueError('not a regular file')
        return os.fdopen(fd, 'rb')
    except BaseException:
        os.close(fd)
        raise


def reject_constant(value):
    raise ValueError('JSON contains nonfinite constant')


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result: raise ValueError('duplicate JSON object key')
        result[key] = value
    return result


def read_json(path):
    with open_regular(path) as stream: raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES: raise ValueError('JSON exceeds 1 MiB')
    return json.loads(raw.decode('utf-8'), parse_constant=reject_constant, object_pairs_hook=unique_keys)


def finite_number(value):
    if type(value) not in (int, float): raise ValueError('samples require numbers, not booleans')
    try: number = float(value)
    except (OverflowError, ValueError): raise ValueError('numeric value is outside finite float range') from None
    if not math.isfinite(number): raise ValueError('numeric value must be finite')
    return number


def validate_metadata(value, depth=0):
    if depth > 8: raise ValueError('metadata nesting exceeds eight levels')
    if value is None or type(value) is bool: return
    if type(value) in (int, float): finite_number(value); return
    if type(value) is str:
        if len(value) > 256: raise ValueError('metadata strings exceed 256 characters')
        return
    if type(value) is list:
        if len(value) > 64: raise ValueError('metadata list exceeds 64 items')
        for item in value: validate_metadata(item, depth + 1)
        return
    if type(value) is dict:
        if len(value) > 64: raise ValueError('metadata object exceeds 64 keys')
        for key, item in value.items():
            if not isinstance(key, str) or not key or len(key) > 128: raise ValueError('invalid metadata key')
            validate_metadata(item, depth + 1)
        return
    raise ValueError('unsupported metadata value')


def typed_equal(a, b):
    if type(a) is not type(b): return False
    if isinstance(a, dict): return a.keys() == b.keys() and all(typed_equal(a[k], b[k]) for k in a)
    if isinstance(a, list): return len(a) == len(b) and all(typed_equal(x, y) for x, y in zip(a, b))
    return a == b


def validate(record):
    keys = {'schema_version', 'workload', 'metric', 'unit', 'direction', 'scope', 'samples', 'correctness', 'metadata'}
    if not isinstance(record, dict) or set(record) != keys: raise ValueError('record requires exact documented schema keys')
    if type(record['schema_version']) is not int or record['schema_version'] != 1: raise ValueError('schema_version must be integer 1')
    for key in ('workload', 'metric', 'unit', 'scope'):
        if not isinstance(record[key], str) or not record[key] or len(record[key]) > 256: raise ValueError('labels require 1..256 characters')
    if record['direction'] not in ('lower', 'higher'): raise ValueError('direction must be lower or higher')
    if type(record['correctness']) is not bool: raise ValueError('correctness must be a boolean')
    if not isinstance(record['metadata'], dict): raise ValueError('metadata must be an object')
    validate_metadata(record['metadata'])
    samples = record['samples']
    if not isinstance(samples, list) or not 3 <= len(samples) <= MAX_SAMPLES: raise ValueError('require 3..100000 samples')
    values = [finite_number(x) for x in samples]
    if any(x < 0 for x in values): raise ValueError('samples must be nonnegative')
    return values


def median(values):
    ordered = sorted(values)
    n = len(ordered); m = n // 2
    return ordered[m] if n % 2 else ordered[m-1] + (ordered[m] - ordered[m-1]) / 2


def summary(values):
    center = median(values)
    return {'n': len(values), 'min': min(values), 'median': center,
            'max': max(values), 'mad': median([abs(x - center) for x in values])}


def compare(baseline, candidate, allowed):
    left, right = validate(baseline), validate(candidate)
    if len(allowed) > 64 or len(set(allowed)) != len(allowed): raise ValueError('invalid metadata override list')
    for key in allowed:
        if key not in baseline['metadata'] or key not in candidate['metadata']: raise ValueError('allowed metadata key must exist in both records')
    reasons = [key + '_mismatch' for key in ('workload','metric','unit','scope','direction') if baseline[key] != candidate[key]]
    if not baseline['correctness'] or not candidate['correctness']: reasons.append('correctness_not_passed')
    if baseline['metadata'].keys() != candidate['metadata'].keys(): reasons.append('metadata_keys_mismatch')
    for key in sorted(baseline['metadata'].keys() & candidate['metadata'].keys()):
        if key not in allowed and not typed_equal(baseline['metadata'][key], candidate['metadata'][key]): reasons.append('metadata_mismatch:' + key)
    result = {'schema_version':1, 'status':'incomparable' if reasons else 'comparable',
              'reasons':reasons, 'baseline':summary(left), 'candidate':summary(right),
              'allowed_metadata_differences':list(allowed), 'improvement_percent':None,
              'limitations':['not_statistical_significance','correctness_is_supplied_not_executed','metadata_completeness_is_callers_responsibility']}
    if reasons: return result
    b, c = result['baseline']['median'], result['candidate']['median']
    result.update(metric=baseline['metric'], unit=baseline['unit'], direction=baseline['direction'], scope=baseline['scope'])
    result['median_difference_within_max_mad'] = abs(b-c) <= max(result['baseline']['mad'], result['candidate']['mad'])
    if b == 0:
        result['percent_unavailable_reason'] = 'zero_baseline'
    else:
        change = ((b-c) if baseline['direction']=='lower' else (c-b)) / b * 100
        if math.isfinite(change): result['improvement_percent'] = change
        else: result['percent_unavailable_reason'] = 'finite_inputs_percentage_overflow'
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('baseline', type=Path)
    parser.add_argument('candidate', type=Path)
    parser.add_argument('--allow-metadata-difference', action='append', default=[], metavar='KEY',
                        help='Explicit intended top-level experimental variable (not permission to change workload or correctness)')
    args = parser.parse_args()
    try:
        result = compare(read_json(args.baseline), read_json(args.candidate), args.allow_metadata_difference)
        output = json.dumps(result, allow_nan=False)
    except (OSError, UnicodeError, ValueError, RecursionError, OverflowError) as error:
        print(json.dumps({'schema_version':1, 'error':str(error)[:256]}))
        return 2
    print(output)
    return 0 if result['status']=='comparable' else 1

if __name__=='__main__': sys.exit(main())
