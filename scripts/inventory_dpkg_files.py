"""Selected regular-file checks against passive Debian md5sums and status sources."""
import hashlib
import json
import re
from pathlib import Path

MAX_REQUEST = 128 * 1024
MAX_SUMS = 4 * 1024 * 1024
MAX_MEMBERS = 256
MAX_SUM_LINES = 32768
HASH = re.compile(r'[0-9a-f]{64}')


def verify(reader, request_raw, status_path, status, multi_arch):
    # Import from the package or from the directory of the standalone CLI.
    if __package__:
        from .inventory_local_artifacts import InventoryError, inside, relative
    else:
        from inventory_local_artifacts import InventoryError, inside, relative

    def reject_duplicates(pairs):
        obj = dict(pairs)
        if len(pairs) != len(obj):
            raise InventoryError('inventory_dpkg_request_duplicate_key')
        return obj

    try:
        request = json.loads(request_raw.decode('utf-8'), object_pairs_hook=reject_duplicates)
    except (ValueError, UnicodeError, RecursionError) as error:
        if isinstance(error, InventoryError):
            raise
        raise InventoryError('inventory_dpkg_request_json') from None

    if (not isinstance(request, dict) or set(request) != {'schema', 'status_sha256', 'packages'}
            or request['schema'] != 'gig.security.selected_dpkg_files.v1'
            or type(request['packages']) is not list or not 1 <= len(request['packages']) <= 32):
        raise InventoryError('inventory_dpkg_request_contract')
    if status is None or status_path.parts[-4:] != ('var', 'lib', 'dpkg', 'status'):
        raise InventoryError('inventory_dpkg_status_scope')
    if request['status_sha256'] != status['sha256']:
        raise InventoryError('inventory_dpkg_status_digest_mismatch')

    sysroot = status_path.parents[3]
    records = {(p['package'], p['architecture']): p for p in status['packages']}
    verified = []
    requested_packages = set()
    requested_paths = set()
    for selection in request['packages']:
        keys = {'package', 'architecture', 'version', 'md5sums_sha256', 'files'}
        if (type(selection) is not dict or set(selection) != keys
                or any(type(selection[k]) is not str for k in keys - {'files'})
                or not HASH.fullmatch(selection['md5sums_sha256'])):
            raise InventoryError('inventory_dpkg_file_selection')
        identity = (selection['package'], selection['architecture'])
        entry = records.get(identity)
        if (entry is None or entry['installation_state'] != 'installed' or entry['error_flag'] != 'ok'
                or entry['version'] != selection['version'] or identity in requested_packages):
            raise InventoryError('inventory_dpkg_file_package_identity')
        requested_packages.add(identity)
        members = selection['files']
        if type(members) is not list or not members or len(requested_paths) + len(members) > MAX_MEMBERS:
            raise InventoryError('inventory_dpkg_selected_file_budget')

        paths = {}
        for name in members:
            path = relative(name)
            if len(path.parts) < 3 or path.parts[:2] not in (
                    ('usr', 'bin'), ('usr', 'sbin'), ('usr', 'lib'), ('usr', 'libexec')):
                raise InventoryError('inventory_dpkg_selected_file_scope')
            if name in requested_paths:
                raise InventoryError('inventory_dpkg_duplicate_file_claim')
            requested_paths.add(name)
            paths[name] = inside(sysroot / path, sysroot)

        # dpkg qualifies binary package names for Multi-Arch: same. Never guess
        # an alternate filename or search another package's control directory.
        qualifier = multi_arch[identity]
        if qualifier not in ('no', 'same', 'foreign', 'allowed'):
            raise InventoryError('inventory_dpkg_multiarch_unsupported')
        binary = entry['package'] + (':' + entry['architecture'] if qualifier == 'same' else '')
        info = inside(status_path.parent / 'info' / (binary + '.md5sums'), sysroot)
        raw = reader.read(info, MAX_SUMS)
        if hashlib.sha256(raw).hexdigest() != selection['md5sums_sha256']:
            raise InventoryError('inventory_dpkg_md5sums_digest_mismatch')
        if not raw.endswith(b'\n') or raw.count(b'\n') > MAX_SUM_LINES:
            raise InventoryError('inventory_dpkg_md5sums_lines')
        checks = {}
        for ordinal, line in enumerate(raw[:-1].split(b'\n'), 1):
            match = re.fullmatch(rb'([0-9a-f]{32})  ([ -~]{1,1024})', line)
            if match is None:
                raise InventoryError('inventory_dpkg_md5sums_record')
            checksum, name = (value.decode('ascii') for value in match.groups())
            if ('\\' in name or any(part in ('', '.', '..') for part in name.split('/'))
                    or name in checks):
                raise InventoryError('inventory_dpkg_md5sums_path')
            checks[name] = (ordinal, checksum)
        files = []
        for name in sorted(paths):
            if name not in checks:
                raise InventoryError('inventory_dpkg_file_unlisted')
            ordinal, expected = checks[name]
            data = reader.read(paths[name])
            if hashlib.md5(data, usedforsecurity=False).hexdigest() != expected:
                raise InventoryError('inventory_dpkg_file_digest_mismatch')
            files.append({'path': name, 'bytes': len(data), 'md5sums_line': ordinal,
                          'recorded_md5': expected, 'observed_sha256': hashlib.sha256(data).hexdigest()})
        verified.append({'package': entry['package'], 'architecture': entry['architecture'],
                         'version': entry['version'], 'status': entry['status'],
                         'status_stanza': entry['source_stanza'], 'multi_arch': qualifier,
                         'md5sums_path': info.relative_to(sysroot).as_posix(),
                         'md5sums_sha256': selection['md5sums_sha256'], 'listed_files': len(checks),
                         'files': files})
    return {'schema': 'gig.security.dpkg_file_integrity.v1',
            'scope': 'EXPLICIT_SELECTED_LOCAL_DPKG_REGULAR_FILES',
            'status_sha256': status['sha256'], 'request_sha256': hashlib.sha256(request_raw).hexdigest(),
            'system_root': str(sysroot), 'files_checked': len(requested_paths),
            'packages': sorted(verified, key=lambda p: (p['package'], p['architecture'])),
            'publisher_authenticated': False, 'advisory_analysis': 'NOT_RUN'}
