#!/usr/bin/env python3
"""Validate a locally built sdist against its current source checkout (no extraction)."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import tarfile


def check(archive, root):
    allowed = set(subprocess.check_output(
        ['git', '-C', str(root), 'ls-files', '--cached', '--others', '--exclude-standard'],
        text=True).splitlines())
    manifest = []
    seen = set()
    with tarfile.open(archive) as source:
        for member in source:
            parts = PurePosixPath(member.name).parts
            if (not parts or parts[0] != 'gig_microstructure-0.1.1'
                    or '..' in parts or not member.isfile()):
                raise ValueError('Unsafe archive member: ' + member.name)
            name = '/'.join(parts[1:])
            if name in seen:
                raise ValueError('Duplicate archive member: ' + name)
            seen.add(name)
            if name != 'PKG-INFO' and name not in allowed:
                raise ValueError('Unintended archive member: ' + name)
            if any(p in {'build', 'dist', '__pycache__', '.venv', '.git'} for p in parts):
                raise ValueError('Private output in archive: ' + name)
            with source.extractfile(member) as stream:
                data = stream.read()
            if name != 'PKG-INFO' and data != (root / name).read_bytes():
                raise ValueError('Source content mismatch: ' + name)
            manifest.append({'path': name, 'bytes': len(data),
                             'sha256': hashlib.sha256(data).hexdigest()})
    for name in allowed:
        if name.startswith(('src/', 'include/', 'python/', 'cmake/', 'schemas/')):
            if name not in seen:
                raise ValueError('Required source missing: ' + name)
    for name in ['CMakeLists.txt', 'pyproject.toml', 'README.md', 'THIRD_PARTY_NOTICES.md']:
        if name not in seen:
            raise ValueError('Required build/notice file missing: ' + name)
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('--source-root', type=Path, default=Path('.'))
    parser.add_argument('--manifest', type=Path, required=True)
    args = parser.parse_args()
    result = check(args.archive, args.source_root)
    args.manifest.write_text(json.dumps(result, indent=2) + '\n')
    print(f'PASS: {len(result)} safe, intended, byte-identical members; required source trees complete')
