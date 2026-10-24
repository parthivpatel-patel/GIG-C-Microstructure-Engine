#!/usr/bin/env python3
"""Verify local authenticated reproduction receipts; not remote attestation."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import xml.etree.ElementTree as ET


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate evidence field')
        result[key] = value
    return result


def verify(manifest, artifacts):
    with Path(manifest).open('rb') as stream:
        raw = stream.read(1024 * 1024 + 1)
    if len(raw) > 1024 * 1024:
        raise ValueError('manifest exceeds 1 MiB')
    document = json.loads(raw, object_pairs_hook=unique)
    if document['schema'] != 'gig.clean_reproduction.v1':
        raise ValueError('unsupported evidence schema')
    root = Path(artifacts).resolve(strict=True)
    seen = set()
    for item in document['artifacts']:
        name = PurePosixPath(item['path'])
        if name.is_absolute() or '..' in name.parts or str(name) in seen:
            raise ValueError('unsafe or duplicate artifact path')
        seen.add(str(name))
        path = root.joinpath(*name.parts)
        if any(root.joinpath(*name.parts[:i]).is_symlink() for i in range(1, len(name.parts) + 1)) or not path.resolve(strict=True).is_relative_to(root):
            raise ValueError('artifact escapes evidence directory')
        if not path.is_file() or path.stat().st_size > 64 * 1024 * 1024:
            raise ValueError('invalid artifact size/type')
        digest = hashlib.sha256()
        with path.open('rb') as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(block)
        if digest.hexdigest() != item['sha256']:
            raise ValueError('artifact digest mismatch: ' + str(name))
    junit = document['reproducible']['junit']
    if junit not in seen:
        raise ValueError('JUnit is not hash-bound')
    with (root / junit).open('rb') as stream:
        data = stream.read(16 * 1024 * 1024 + 1)
    if len(data) > 16 * 1024 * 1024 or b'\0' in data:
        raise ValueError('invalid JUnit size/encoding')
    text = data.decode('utf-8')
    if '<!DOCTYPE' in text.upper() or '<!ENTITY' in text.upper():
        raise ValueError('DTD/entity not permitted')
    suite = ET.fromstring(text)
    counts = {key: int(suite.get(key, '0')) for key in ('tests', 'failures', 'skipped', 'disabled')}
    required = {'native': 154, 'python': 157, 'python_sanitizer': 158}[document['reproducible']['test_profile']]
    if counts['tests'] != required or counts != document['reproducible']['ctest_counts'] or any(counts[k] for k in ('failures', 'skipped', 'disabled')):
        raise ValueError('missing or failed required tests')
    cases = {case.get('name'): case for case in suite.findall('testcase')}
    if len(cases) != counts['tests']:
        raise ValueError('duplicate or missing test cases')
    expected = document['reproducible']['canonical_sha256']
    if hashlib.sha256(json.dumps(expected, sort_keys=True).encode()).hexdigest() != 'baa420649556c94101f3898863546c3238a630910248d2622b0d4a9d37d882a5' or len(expected) != 8:
        raise ValueError('eight canonical identities required')
    for name, digest in expected.items():
        if digest not in ''.join(cases[name].itertext()):
            raise ValueError('canonical identity mismatch: ' + name)
    return counts


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest')
    parser.add_argument('--artifacts', required=True)
    args = parser.parse_args()
    print(json.dumps({'verified': True, 'counts': verify(args.manifest, args.artifacts)}, sort_keys=True))
