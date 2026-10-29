#!/usr/bin/env python3
"""Check optional vendor JSON records and local paths; not legal or offline-build certification."""
import argparse
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit

MAX_BYTES = 1024 * 1024

def validate(data, root):
    """Return structural/path errors without executing, modifying or hashing vendor code."""
    root = Path(root).resolve()
    errors = []
    if not root.is_dir():
        return ['root must be an existing directory']
    if not isinstance(data, dict) or not isinstance(data.get('dependencies'), list):
        return ['manifest must be an object with a dependencies list']
    names = set()
    def local_path(value, label, directory=False):
        if not isinstance(value, str) or not value.strip():
            errors.append(f'{label}: expected nonempty root-relative path'); return
        path = Path(value)
        if path.is_absolute():
            errors.append(f'{label}: absolute path is not allowed'); return
        try:
            resolved = (root / path).resolve()
            resolved.relative_to(root)
        except (ValueError, OSError, RuntimeError):
            errors.append(f'{label}: path resolves outside root or cannot be resolved'); return
        try:
            if directory:
                if not resolved.is_dir(): errors.append(f'{label}: source directory missing')
            elif not resolved.is_file() or resolved.stat().st_size == 0:
                errors.append(f'{label}: license/notice file missing or empty')
        except OSError as exc:
            errors.append(f'{label}: cannot inspect path ({exc.__class__.__name__})')
    for index, dep in enumerate(data['dependencies']):
        prefix = f'dependencies[{index}]'
        if not isinstance(dep, dict):
            errors.append(f'{prefix}: expected object'); continue
        for field in ('name', 'revision', 'upstream'):
            if not isinstance(dep.get(field), str) or not dep[field].strip():
                errors.append(f'{prefix}.{field}: expected nonempty string')
        name = dep.get('name')
        if isinstance(name, str):
            if name in names: errors.append(f'{prefix}.name: duplicate name {name!r}')
            names.add(name)
        upstream = dep.get('upstream')
        if isinstance(upstream, str):
            try:
                parsed = urlsplit(upstream)
                if parsed.scheme not in ('https', 'http') or not parsed.netloc:
                    errors.append(f'{prefix}.upstream: expected HTTP(S) provenance URL')
            except ValueError:
                errors.append(f'{prefix}.upstream: malformed provenance URL')
        local_path(dep.get('source'), f'{prefix}.source', directory=True)
        licenses = dep.get('licenses')
        if not isinstance(licenses, list) or not licenses:
            errors.append(f'{prefix}.licenses: expected nonempty list of license/notice file paths')
        else:
            for n, path in enumerate(licenses):
                local_path(path, f'{prefix}.licenses[{n}]')
    return errors

def load(path):
    with path.open('rb') as stream:
        raw=stream.read(MAX_BYTES+1)
    if len(raw)>MAX_BYTES: raise ValueError('manifest exceeds 1 MiB')
    return json.loads(raw)

def main():
    parser=argparse.ArgumentParser(description=__doc__, epilog='Optional schema: {"dependencies":[{"name":"lib","revision":"v1.2","upstream":"https://example.org/lib","source":"third_party/lib-1.2","licenses":["third_party/lib-1.2/LICENSE"]}]}. Existing human-readable dependency records need not migrate to this schema. Exit: 0 structurally valid; 1 findings; 2 input error.')
    parser.add_argument('manifest', type=Path, help='local JSON file, at most 1 MiB')
    parser.add_argument('--root', type=Path, required=True, help='repository root used to resolve all dependency/license paths')
    args=parser.parse_args()
    try:
        data=load(args.manifest)
        errors=validate(data,args.root)
    except (OSError,ValueError) as exc:
        print(f'input error: {exc}',file=sys.stderr); return 2
    print(json.dumps({'status':'findings' if errors else 'structurally_valid','errors':errors,'limitations':[
        'Does not verify revision identity, source completeness, patches, or license text accuracy/completeness.',
        'Does not establish license compatibility/compliance or prove an offline configure/build/test.',
        'No repository code was executed, modified or downloaded.'
    ]},indent=2))
    return 1 if errors else 0

if __name__=='__main__':
    raise SystemExit(main())
