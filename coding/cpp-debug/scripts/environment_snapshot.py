#!/usr/bin/env python3
"""Print a minimal read-only host/tool snapshot, without running tools or reading environment values."""
import argparse
import json
import os
import platform
import shutil

TOOLS = ('cmake', 'ninja', 'make', 'clang', 'clang++', 'gcc', 'g++', 'cl',
         'gdb', 'lldb', 'perf', 'xcrun', 'wpr', 'wpa', 'clang-tidy', 'cppcheck')

def snapshot():
    """Return only an allowlisted set of non-secret machine/tool-discovery fields."""
    return {
        'schema_version': 1,
        'system': platform.system(),
        'release': platform.release(),
        'machine': platform.machine(),
        'python': platform.python_version(),
        'logical_cpu_count': os.cpu_count(),
        'tools': {name: shutil.which(name) for name in TOOLS},
        'limitations': [
            'Tool paths indicate discovery only, not versions, usability or permissions.',
            'No tools were executed; no network access, files or full environment were read.',
            'Tool paths may contain user-directory names; review before sharing.',
            'CPU count is logical host availability, not a measured affinity/cgroup quota.',
        ],
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__, epilog='Example: python environment_snapshot.py > environment.json. Output goes to stdout; this program itself writes no files. Review tool paths before sharing.')
    parser.parse_args()
    print(json.dumps(snapshot(), indent=2, sort_keys=True))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
