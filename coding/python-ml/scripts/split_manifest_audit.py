"""Audit declared split metadata, not raw data or feature leakage. Stdlib only."""
import argparse
import json
import math
import os
from pathlib import Path
import stat
import sys

MAX_BYTES = 2_000_000
MAX_ROWS = 20_000
ORDER = ('train', 'validation', 'test')


def reject_constant(_):
    raise ValueError('nonfinite JSON constant')


def object_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key')
        result[key] = value
    return result


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def read_rows(path):
    path = Path(path)
    if path.is_symlink():
        raise ValueError('symlink input not accepted')
    # Nonblocking open prevents a POSIX FIFO path swap from hanging before fstat.
    flags = os.O_RDONLY | getattr(os, 'O_NONBLOCK', 0) | getattr(os, 'O_NOFOLLOW', 0)
    descriptor = os.open(path, flags)
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > MAX_BYTES:
            raise ValueError('input must be a bounded regular file')
        with os.fdopen(descriptor, 'rb') as stream:
            descriptor = None
            raw = stream.read(MAX_BYTES + 1)
    finally:
        if descriptor is not None:
            os.close(descriptor)
    if len(raw) > MAX_BYTES:
        raise ValueError('input too large')
    return json.loads(raw.decode('utf-8'), parse_constant=reject_constant, object_pairs_hook=object_pairs)


def audit(rows, groups=False, time_gap=None):
    if not isinstance(rows, list) or not 2 <= len(rows) <= MAX_ROWS:
        raise ValueError('expected 2..20000 metadata rows')
    if time_gap is not None and (not finite(time_gap) or time_gap < 0):
        raise ValueError('time gap must be finite and nonnegative')
    seen, group_splits = set(), {}
    counts = {name: 0 for name in ORDER}
    times = {name: [] for name in ORDER}
    duplicates = 0
    for row in rows:
        if not isinstance(row, dict) or set(row) - {'id', 'group', 'split', 'time'}:
            raise ValueError('invalid metadata row keys')
        for key in ('id', 'split'):
            if not isinstance(row.get(key), str) or not 1 <= len(row[key]) <= 256:
                raise ValueError('id/split must be bounded nonempty strings')
        split = row['split']
        if split not in ORDER:
            raise ValueError('unknown split')
        counts[split] += 1
        duplicates += row['id'] in seen
        seen.add(row['id'])
        if 'group' in row and (not isinstance(row['group'], str) or not 1 <= len(row['group']) <= 256):
            raise ValueError('group must be a bounded nonempty string')
        if groups:
            if 'group' not in row:
                raise ValueError('group check requires every group')
            group_splits.setdefault(row['group'], set()).add(split)
        if 'time' in row and not finite(row['time']):
            raise ValueError('time must be a finite numeric value in a shared unit')
        if time_gap is not None:
            if 'time' not in row:
                raise ValueError('time check requires every time')
            times[split].append(row['time'])
    if counts['train'] == 0 or counts['test'] == 0:
        raise ValueError('train and test must both be nonempty')
    group_overlap = sum(len(splits) > 1 for splits in group_splits.values())
    time_conflicts = 0
    if time_gap is not None:
        present = [name for name in ORDER if times[name]]
        for left, right in zip(present, present[1:]):
            # Strict chronological boundary even when the requested gap is zero.
            delta = min(times[right]) - max(times[left])
            if delta <= 0 or delta < time_gap:
                time_conflicts += 1
    return {'rows': len(rows), 'split_counts': counts,
            'duplicate_id_rows': duplicates,
            'group_overlap_count': group_overlap if groups else None,
            'chronology_conflicts': time_conflicts if time_gap is not None else None,
            'passed_declared_checks': not (duplicates or group_overlap or time_conflicts),
            'scope': 'metadata only; no content duplicates, feature availability or target leakage inspected'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest')
    parser.add_argument('--groups', action='store_true')
    parser.add_argument('--time-gap', type=float, default=None,
                        help='check train < validation < test; numeric shared time unit, minimum boundary gap')
    args = parser.parse_args()
    try:
        report = audit(read_rows(args.manifest), args.groups, args.time_gap)
    except (ValueError, TypeError, OSError, OverflowError, RecursionError):
        print('Invalid or unreadable split metadata; check schema and bounds.', file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True, allow_nan=False))
    return 0 if report['passed_declared_checks'] else 1


if __name__ == '__main__':
    sys.exit(main())
