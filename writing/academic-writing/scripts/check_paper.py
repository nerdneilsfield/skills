#!/usr/bin/env python3
"""Static consistency check for a LaTeX paper (standard library only).

Reports undefined citations and references, duplicate labels, unused labels,
unused or incomplete bibliography entries, placeholder text, and numbers that
appear in the abstract but nowhere in the body.

Usage:
    check_paper.py main.tex [--bib refs.bib ...] [--json] [--strict]

Exit status: 1 if any error is found (or any warning with --strict), else 0.
It never edits files and never touches the network. It reads \\input and
\\include files relative to the main file's directory, as LaTeX does, and reports
missing ones. It does not run LaTeX, so macros that
generate labels or citations are invisible to it.
"""
from __future__ import annotations

import argparse
import bisect
import json
import re
import sys
from pathlib import Path

CITE = re.compile(r'\\(?:[a-zA-Z]*cite[a-zA-Z]*|nocite)\*?(?:\[[^\]]*\]){0,2}\{([^}]*)\}')
REF = re.compile(r'\\(?:ref|eqref|autoref|cref|Cref|vref|pageref|nameref)\*?\{([^}]*)\}')
LABEL = re.compile(r'\\label\{([^}]*)\}')
INPUT = re.compile(r'\\(?:input|include)\{([^}]*)\}')
BIBRES = re.compile(r'\\(?:bibliography|addbibresource)(?:\[[^\]]*\])?\{([^}]*)\}')
ABSTRACT = re.compile(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', re.S)
PLACEHOLDER = re.compile(r'\b(TODO|FIXME|XXX|TBD)\b|\[CITATION NEEDED\]|\?\?\?')
NUMBER = re.compile(r'(?<![\w.])\d+(?:[.,]\d+)*(?![\w])|(?<![\w.])\d+(?:\.\d+)?(?=[A-Za-z]{1,4}\b)')
REQUIRED = {'article': ('author', 'title', 'year'), 'inproceedings': ('author', 'title', 'year'),
            'book': ('title', 'year'), 'misc': ('title',)}


def strip_comments(text: str) -> str:
    return re.sub(r'(?<!\\)%.*', '', text)


def load_tex(path: Path, root: Path | None = None, seen: set[Path] | None = None,
             missing: list | None = None) -> list[tuple[Path, int, str]]:
    """Return (file, line number, comment-stripped line) for the file and its inputs.

    Inputs resolve from the main file's directory (`root`), as LaTeX does, not from
    the including file. Inputs that cannot be read are appended to `missing`.
    """
    seen = seen if seen is not None else set()
    path = path.resolve()
    root = root or path.parent
    if path in seen or not path.is_file():
        return []
    seen.add(path)
    lines = []
    for n, raw in enumerate(path.read_text(encoding='utf-8', errors='replace').splitlines(), 1):
        line = strip_comments(raw)
        lines.append((path, n, line))
        for target in INPUT.findall(line):
            sub = root / target.strip()
            if not sub.is_file():
                sub = sub.with_name(sub.name + '.tex')
            if not sub.is_file():
                if missing is not None:
                    missing.append((target.strip(), path, n))
                continue
            lines.extend(load_tex(sub, root, seen, missing))
    return lines


def joined(lines):
    """Join stripped lines into one text and return it with each line's start offset."""
    starts, pos = [], 0
    for _, _, line in lines:
        starts.append(pos)
        pos += len(line) + 1
    return '\n'.join(line for _, _, line in lines), starts


def where_of(lines, starts, offset):
    i = bisect.bisect_right(starts, offset) - 1
    return lines[i][0], lines[i][1]


def parse_bib(path: Path) -> dict[str, tuple[str, set[str]]]:
    """Return {key: (entry type, field names)} using brace-depth scanning."""
    text = path.read_text(encoding='utf-8', errors='replace')
    entries = {}
    for m in re.finditer(r'@(\w+)\s*\{\s*([^,\s]+)\s*,', text):
        kind = m[1].lower()
        if kind in ('comment', 'string', 'preamble'):
            continue
        depth, i, body = 1, m.end(), []
        while i < len(text) and depth:
            depth += {'{': 1, '}': -1}.get(text[i], 0)
            body.append(text[i])
            i += 1
        fields, depth = set(), 0
        flat = []
        for ch in ''.join(body):
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
            flat.append(ch if depth == 0 else ' ')
        fields = {f.lower() for f in re.findall(r'(\w+)\s*=', ''.join(flat))}
        entries[m[2]] = (kind, fields)
    return entries


def keys(pattern: re.Pattern, lines, full=None, starts=None) -> dict[str, tuple[Path, int]]:
    """Map each key to its first location; matches may span several lines."""
    if full is None:
        full, starts = joined(lines)
    found: dict[str, tuple[Path, int]] = {}
    for m in pattern.finditer(full):
        where = where_of(lines, starts, m.start())
        for key in (k.strip() for k in m[1].split(',')):
            if key:
                found.setdefault(key, where)
    return found


def norm_number(token: str) -> str:
    return token.replace(',', '')


def abstract_numbers(text: str) -> list[str]:
    """Numbers worth tracing: decimals, or integers of two or more digits."""
    body = re.sub(r'\\[a-zA-Z]+\*?(\[[^\]]*\])?', ' ', text)
    out = []
    for tok in NUMBER.findall(body):
        t = norm_number(tok)
        if '.' in t or len(t) >= 2:
            out.append(t)
    return list(dict.fromkeys(out))


def check(main: Path, bibs: list[Path]) -> list[dict]:
    issues: list[dict] = []

    def add(level, code, msg, where=None):
        loc = f'{where[0].name}:{where[1]}' if where else None
        issues.append({'level': level, 'code': code, 'message': msg, 'where': loc})

    missing: list = []
    lines = load_tex(main, missing=missing)
    if not lines:
        add('error', 'no-input', f'cannot read {main}')
        return issues
    for target, path, n in missing:
        add('error', 'missing-input', f'\\input/\\include file not found: {target}', (path, n))
    full, starts = joined(lines)

    cites = keys(CITE, lines, full, starts)
    nocite_all = re.search(r'\\nocite\{\*\}', full) is not None
    refs = keys(REF, lines, full, starts)
    labels: dict[str, tuple[Path, int]] = {}
    for m in LABEL.finditer(full):
        lab, where = m[1].strip(), where_of(lines, starts, m.start())
        if lab in labels:
            add('error', 'duplicate-label', f'label {lab!r} defined twice', where)
        labels.setdefault(lab, where)

    if not bibs:
        for group in BIBRES.findall(full):
            for name in group.split(','):
                name = name.strip()
                if name:
                    p = main.parent / name
                    bibs.append(p if p.suffix else p.with_suffix('.bib'))
    bib: dict[str, tuple[str, set[str]]] = {}
    for p in bibs:
        if p.is_file():
            bib.update(parse_bib(p))
        else:
            add('error', 'missing-bib', f'bibliography file not found: {p}')

    if bib or bibs:
        for key, where in cites.items():
            if key != '*' and key not in bib:
                add('error', 'undefined-citation', f'\\cite key {key!r} is not in the bibliography', where)
        if not nocite_all:
            for key in bib:
                if key not in cites:
                    add('warning', 'unused-bib-entry', f'bib entry {key!r} is never cited')
        for key, (kind, fields) in bib.items():
            need = REQUIRED.get(kind, ())
            missing = [f for f in need if f not in fields]
            if kind in ('article', 'inproceedings') and 'author' in missing and 'editor' in fields:
                missing.remove('author')
            if missing:
                add('warning', 'incomplete-bib-entry', f'{key!r} ({kind}) lacks: {", ".join(missing)}')
    elif cites:
        add('warning', 'no-bibliography', 'citations found but no bibliography file was given or declared')

    for key, where in refs.items():
        if key not in labels:
            add('error', 'undefined-reference', f'reference to undefined label {key!r}', where)
    for key, where in labels.items():
        if key not in refs:
            add('warning', 'unused-label', f'label {key!r} is never referenced', where)

    for path, n, line in lines:
        # Placeholders matter; look at the stripped text, so commented notes are ignored.
        if PLACEHOLDER.search(line):
            add('warning', 'placeholder', f'placeholder text: {line.strip()[:60]}', (path, n))

    m = ABSTRACT.search(full)
    if m:
        rest = full.replace(m[0], ' ')
        rest = re.split(r'\\bibliography\{|\\printbibliography|\\begin\{thebibliography\}', rest)[0]
        body_numbers = {norm_number(t) for t in NUMBER.findall(rest)}
        for num in abstract_numbers(m[1]):
            if num not in body_numbers:
                add('warning', 'abstract-number-not-in-body',
                    f'abstract number {num} does not appear in the body; check it against a table or sentence')
    else:
        add('warning', 'no-abstract', 'no abstract environment found; abstract number check skipped')
    return issues


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('tex', type=Path)
    ap.add_argument('--bib', type=Path, action='append', default=[], help='bibliography file (repeatable)')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--strict', action='store_true', help='exit 1 on warnings too')
    args = ap.parse_args(argv)
    issues = check(args.tex, list(args.bib))
    if args.json:
        print(json.dumps(issues, indent=2))
    else:
        for i in issues:
            loc = f" ({i['where']})" if i['where'] else ''
            print(f"{i['level'].upper():7} {i['code']}: {i['message']}{loc}")
        errs = sum(i['level'] == 'error' for i in issues)
        print(f'{errs} error(s), {len(issues) - errs} warning(s)')
    bad = any(i['level'] == 'error' or (args.strict and i['level'] == 'warning') for i in issues)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
