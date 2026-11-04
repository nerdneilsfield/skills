"""Bounded, read-only CSV structural audit. Never emits cell values."""
import argparse
import csv
import io
import json
import math
import os
from pathlib import Path
import stat


def audit(path, *, key=(), numeric=(), max_bytes=4_000_000, max_rows=100_000,
          max_columns=256):
    if not (1 <= max_bytes <= 32_000_000 and 1 <= max_rows <= 1_000_000
            and 1 <= max_columns <= 1024):
        raise ValueError('limits outside supported bounds')
    if any(len(selectors) > max_columns or len(set(selectors)) != len(selectors)
           or any(not isinstance(x, str) or not 1 <= len(x) <= 256 for x in selectors)
           for selectors in (key, numeric)):
        raise ValueError('invalid or repeated selectors')
    path = Path(path)
    if path.is_symlink():
        raise ValueError('symlink inputs are not supported')
    # Nonblocking open prevents a raced FIFO from hanging before fstat. NOFOLLOW
    # also rejects raced symlinks on platforms that expose this flag.
    flags = os.O_RDONLY | getattr(os, 'O_NONBLOCK', 0) | getattr(os, 'O_NOFOLLOW', 0)
    fd = os.open(path, flags)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise ValueError('input must be a regular file')
        with os.fdopen(fd, 'rb', closefd=False) as f:
            data = f.read(max_bytes + 1)
    finally:
        os.close(fd)
    if len(data) > max_bytes:
        raise ValueError('byte limit exceeded; no partial audit')
    text = data.decode('utf-8-sig')
    reader = csv.reader(io.StringIO(text, newline=''), strict=True)
    header = next(reader, None)
    if not header or any(not x.strip() for x in header) or len(set(header)) != len(header):
        raise ValueError('empty or duplicate CSV headers')
    if len(header) > max_columns or any(len(x) > 256 for x in header):
        raise ValueError('column limit exceeded')
    if any(col not in header for col in (*key, *numeric)):
        raise ValueError('a requested column is absent')
    key_indices = [header.index(x) for x in key]
    number_indices = {x: header.index(x) for x in numeric}
    report = {'rows': 0, 'columns': len(header), 'missing_key_rows': 0,
              'duplicate_key_rows': 0, 'numeric': {
                  x: {'missing': 0, 'invalid': 0, 'nonfinite': 0} for x in numeric}}
    seen = set()
    for row in reader:
        if len(row) != len(header):
            raise ValueError('row width differs from header')
        report['rows'] += 1
        if report['rows'] > max_rows:
            raise ValueError('row limit exceeded; no partial audit')
        if key_indices:
            values = tuple(row[i] for i in key_indices)
            if any(not value.strip() for value in values):
                report['missing_key_rows'] += 1
            elif values in seen:
                report['duplicate_key_rows'] += 1
            else:
                seen.add(values)
        for name, index in number_indices.items():
            value = row[index]
            if not value.strip():
                report['numeric'][name]['missing'] += 1
                continue
            try:
                number = float(value)
            except ValueError:
                report['numeric'][name]['invalid'] += 1
            else:
                if not math.isfinite(number):
                    report['numeric'][name]['nonfinite'] += 1
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv', type=Path)
    parser.add_argument('--key', action='append', default=[])
    parser.add_argument('--numeric', action='append', default=[])
    parser.add_argument('--max-bytes', type=int, default=4_000_000)
    parser.add_argument('--max-rows', type=int, default=100_000)
    args = parser.parse_args()
    try:
        result = audit(args.csv, key=args.key, numeric=args.numeric,
                       max_bytes=args.max_bytes, max_rows=args.max_rows)
    except (ValueError, OSError, csv.Error, UnicodeError):
        # Parser exceptions can quote raw data/paths; do not print them.
        parser.exit(2, 'CSV audit rejected input: check format, schema, encoding and limits locally.\n')
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
