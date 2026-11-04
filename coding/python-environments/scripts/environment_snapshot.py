#!/usr/bin/env python3
"""Read-only current-interpreter evidence, not environment repair or import validation.
Python 3.9+ stdlib. Prefer `python -I environment_snapshot.py` using the intended
interpreter. No manager commands, target imports, CUDA queries or environment dump.
"""
import argparse
import json
import os
from pathlib import Path
import platform
import re
import shutil
import stat
import sys
import sysconfig

MAX_BYTES = 1024 * 1024
MAX_FILES = 16
MAX_PATH = 4096
MAX_VALUE = 256


def bounded(value):
    if value is None:
        return None
    text = str(value)
    return text if len(text) <= MAX_VALUE else text[:MAX_VALUE-11] + '[truncated]'


def open_regular(path):
    if not stat.S_ISREG(path.stat().st_mode):
        raise ValueError('not a regular file')
    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NONBLOCK', 0))
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise ValueError('not a regular file')
        return os.fdopen(fd, 'rb')
    except BaseException:
        os.close(fd)
        raise


def read_metadata(path):
    if len(str(path)) > MAX_PATH:
        raise ValueError('metadata path exceeds 4096 characters')
    with open_regular(path) as stream:
        content = stream.read(MAX_BYTES + 1)
    if len(content) > MAX_BYTES:
        raise ValueError('metadata file exceeds 1 MiB')
    text = content.decode('utf-8')
    fields = {}
    for line in text.splitlines():
        if not line.strip():
            break  # Description body is never evidence or output.
        key, sep, value = line.partition(':')
        if sep and key.lower() in ('name', 'version'):
            key = key.lower()
            value = value.strip()
            if key in fields or not value or len(value) > MAX_VALUE:
                raise ValueError('missing, duplicate or oversized Name/Version metadata')
            if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._+!\-]*', value):
                raise ValueError('Name/Version contains unsupported characters')
            fields[key] = value
    if set(fields) != {'name', 'version'}:
        raise ValueError('metadata requires unique Name and Version headers')
    return fields


def snapshot(paths, include_paths=False):
    if len(paths) > MAX_FILES:
        raise ValueError('at most 16 explicit metadata files')
    result = {
        'schema_version': 1,
        'interpreter': {'implementation': bounded(platform.python_implementation()),
                        'version': bounded(platform.python_version()),
                        'cache_tag': bounded(sys.implementation.cache_tag)},
        'platform': {'system': bounded(platform.system()), 'machine': bounded(platform.machine())},
        'abi': {'soabi': bounded(sysconfig.get_config_var('SOABI')),
                'extension_suffix': bounded(sysconfig.get_config_var('EXT_SUFFIX'))},
        'venv': sys.prefix != sys.base_prefix,
        'manager_commands': {name: shutil.which(name) is not None for name in ('uv', 'conda', 'pixi')},
        'metadata_evidence': [], 'errors': [],
        'limitations': ['current_interpreter_only', 'metadata_does_not_prove_import_or_active_installation',
                        'manager_presence_not_version_or_environment_owner',
                        'cuda_driver_runtime_device_unchecked', 'python_startup_site_configuration_not_audited'],
    }
    if include_paths:
        result['interpreter'].update(executable=str(sys.executable)[:MAX_PATH],
                                     prefix=str(sys.prefix)[:MAX_PATH], base_prefix=str(sys.base_prefix)[:MAX_PATH])
    for index, supplied in enumerate(paths):
        path = Path(supplied)
        try:
            evidence = read_metadata(path)
            if include_paths:
                evidence['path'] = str(path)
            result['metadata_evidence'].append(evidence)
        except (OSError, UnicodeError, ValueError) as error:
            # Do not leak arbitrary source text or path through exception messages.
            message = str(error)[:256] if isinstance(error, ValueError) and not isinstance(error, UnicodeError) else type(error).__name__
            result['errors'].append({'input_index': index, 'error': message})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--metadata-file', type=Path, action='append', default=[],
                        help='Explicit plain UTF-8 package METADATA file; max 16 files, 1 MiB each')
    parser.add_argument('--include-paths', action='store_true', help='Opt in to local interpreter/prefix/file paths; review before sharing')
    args = parser.parse_args()
    try:
        result = snapshot(args.metadata_file, args.include_paths)
    except ValueError as error:
        print(json.dumps({'schema_version': 1, 'error': str(error)}))
        return 2
    print(json.dumps(result, allow_nan=False))
    return 2 if result['errors'] else 0

if __name__ == '__main__': sys.exit(main())
