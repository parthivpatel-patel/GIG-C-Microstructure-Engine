"""Read-only deployment receipts. No providers, private configuration or remote requests.

A startup receipt binds observed checkout/assets at app construction, not every
loaded Python byte, a security attestation, or GitHub's private-port authentication.
"""
import hashlib
from importlib import metadata
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys

from .artifacts import EvidenceError, decode, digest, read_bytes


def _git(root, *arguments):
    return subprocess.check_output(
        ['git', '-C', str(root), *arguments], stderr=subprocess.DEVNULL,
        timeout=3, text=True, env={**os.environ, 'GIT_OPTIONAL_LOCKS': '0'})


def release_receipt(root):
    """Capture once at application construction; failure stays explicit and bounded."""
    root = Path(root)
    result = {'schema': 'gig.application.release.v1', 'source_sha': None,
              'tracked_clean': None, 'frontend_entry_sha256': None,
              'frontend_index_sha256': None, 'errors': []}
    try:
        result['source_sha'] = digest(_git(root, 'rev-parse', 'HEAD').strip(), 40)
        # Tracked changes anywhere are significant. Untracked runtime files are
        # separately checked by qualify(); do not enumerate private files here.
        result['tracked_clean'] = not bool(_git(root, 'diff', 'HEAD', '--name-only'))
    except (OSError, subprocess.SubprocessError, EvidenceError):
        result['errors'].append('source_identity_unavailable')
    try:
        dist = root / 'terminal/web/dist'
        manifest = decode(read_bytes(dist / '.vite/manifest.json', 256 * 1024))
        entry = manifest['index.html']['file']
        if type(entry) is not str or not re.fullmatch(r'assets/[A-Za-z0-9_-]+\.js', entry):
            raise EvidenceError('invalid_frontend_entry')
        result['frontend_entry_sha256'] = hashlib.sha256(read_bytes(dist / entry, 2 * 1024 * 1024)).hexdigest()
        result['frontend_index_sha256'] = hashlib.sha256(read_bytes(dist / 'index.html', 256 * 1024)).hexdigest()
    except (OSError, KeyError, TypeError, EvidenceError):
        result['errors'].append('frontend_identity_unavailable')
    return result


def runtime_inventory(root):
    """Compare direct runtime pins and inventory Requires-Dist without executing it.

    Conditional/extras metadata is retained as metadata, not asserted resolved by
    this function. `python -m pip check` is the complementary offline resolver.
    No advisory database, system patch status or bundled JS clearance is implied.
    """
    raw = read_bytes(Path(root) / 'terminal/server/requirements.txt', 16 * 1024)
    pins = []
    for line in raw.decode('utf-8').splitlines():
        if not line.strip() or line.startswith('#'):
            continue
        if not re.fullmatch(r'[A-Za-z0-9_-]+==[A-Za-z0-9.+_-]+', line):
            raise EvidenceError('runtime_lock_format')
        name, expected = line.split('==')
        try:
            actual = metadata.version(name)
        except metadata.PackageNotFoundError:
            actual = None
        pins.append({'name': name, 'expected': expected, 'actual': actual, 'matches': actual == expected})
    installed = []
    for package in metadata.distributions():
        # Metadata only; no module import or arbitrary environment dump.
        name = package.metadata['Name']
        if not name or not re.fullmatch(r'[A-Za-z0-9_.-]{1,128}', name):
            raise EvidenceError('runtime_package_name')
        if not re.fullmatch(r'[A-Za-z0-9.+_-]{1,128}', package.version):
            raise EvidenceError('runtime_package_version')
        requirements = package.requires or []
        if len(requirements) > 128:
            raise EvidenceError('runtime_dependency_budget')
        dependencies = []
        for requirement in requirements:
            match = re.match(r'^([A-Za-z0-9_.-]{1,128})(?=[\s\[;<>=!~@]|$)', requirement)
            if not match:
                raise EvidenceError('runtime_dependency_format')
            dependencies.append({'name': match[1], 'conditional': ';' in requirement,
                                 'direct_reference': '@' in requirement})
        installed.append({'name': name, 'version': package.version,
                          'dependencies': dependencies})
    if len(installed) > 512:
        raise EvidenceError('runtime_inventory_budget')
    return {'python': platform.python_version(), 'implementation': platform.python_implementation(),
            'architecture': platform.machine(), 'openssl': __import__('ssl').OPENSSL_VERSION,
            'sqlite': __import__('sqlite3').sqlite_version, 'expat': __import__('pyexpat').EXPAT_VERSION,
            'runtime_lock_sha256': hashlib.sha256(raw).hexdigest(), 'pins': pins,
            'installed': sorted(installed, key=lambda p: p['name'].lower()),
            'all_direct_pins_match': all(p['matches'] for p in pins),
            'security_clearance': 'UNVERIFIED_REQUIRES_TARGET_PATCH_AND_ADVISORY_REVIEW'}


def local_health():
    """Explicitly opted-in fixed-loopback read: no redirects or proxy environment."""
    from urllib.request import ProxyHandler, HTTPRedirectHandler, build_opener
    class NoRedirect(HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):
            return None
    try:
        with build_opener(ProxyHandler({}), NoRedirect()).open(
                'http://127.0.0.1:8787/api/v1/health', timeout=2) as response:
            if response.status != 200:
                raise EvidenceError('local_health_status')
            length = response.headers.get('Content-Length')
            if length is not None and (not length.isdecimal() or int(length) > 65536):
                raise EvidenceError('local_health_budget')
            raw = response.read(65536)
            # An exact-cap response is conservatively rejected, never over-read.
            if len(raw) >= 65536:
                raise EvidenceError('local_health_budget')
            value = decode(raw)
            # Never echo the rest of health/private server state.
            receipt = value.get('application_release')
            if type(receipt) is not dict or receipt.get('schema') != 'gig.application.release.v1':
                raise EvidenceError('local_health_release_missing')
            source = digest(receipt.get('source_sha'), 40)
            return {'source_sha': source, 'tracked_clean': receipt.get('tracked_clean') is True,
                    'frontend_entry_sha256': digest(receipt.get('frontend_entry_sha256')),
                    'frontend_index_sha256': digest(receipt.get('frontend_index_sha256'))}
    except EvidenceError:
        raise
    except Exception:
        raise EvidenceError('local_health_unavailable') from None


def qualify(root, expected_sha, *, check_local_server=False, environment=None):
    expected_sha = digest(expected_sha, 40)
    root = Path(root)
    receipt = release_receipt(root)
    failures = list(receipt['errors'])
    if receipt['source_sha'] != expected_sha:
        failures.append('checkout_sha_mismatch')
    if receipt['tracked_clean'] is not True:
        failures.append('tracked_changes_present')
    # Ignore build/evidence/private directories; flag unexpected runtime source.
    untracked = _git(root, 'ls-files', '--others', '--exclude-standard', '--',
                     'terminal', 'python', 'scripts').splitlines()
    if any(Path(p).suffix in ('.py', '.ts', '.tsx', '.js', '.mjs', '.sh') for p in untracked):
        failures.append('untracked_runtime_source')
    runtime = runtime_inventory(root)
    if not runtime['all_direct_pins_match']:
        failures.append('runtime_pin_mismatch')
    # No private provider settings are read. Only launcher-owned public metadata.
    from terminal.server.config import launch_settings
    public_keys = ('CODESPACES', 'CODESPACE_NAME', 'GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN',
                   'GIG_TERMINAL_ALLOWED_ORIGINS')
    env = os.environ if environment is None else environment
    public_env = {key: env[key] for key in public_keys if key in env}
    try:
        host, origins, expected_origin = launch_settings(public_env)
        codespaces = expected_origin is not None
        exact_only = codespaces and [v.strip() for v in origins.split(',')] == [expected_origin]
        launcher = {'codespaces_metadata_present': codespaces, 'exact_forwarded_origin_only': exact_only,
                    'bind_host': host, 'private_port_authentication': 'UNVERIFIED_EXTERNAL_GATE'}
        if codespaces and not exact_only:
            failures.append('launcher_not_single_exact_origin')
    except ValueError:
        launcher = {'configuration': 'INVALID', 'private_port_authentication': 'UNVERIFIED_EXTERNAL_GATE'}
        failures.append('launcher_metadata_invalid')
    local = {'status': 'NOT_REQUESTED'}
    if check_local_server:
        observed = local_health()
        same = all(observed[key] == receipt[key] for key in observed)
        local = {'status': 'MATCH' if same else 'MISMATCH', 'startup_receipt': observed}
        if not same:
            failures.append('running_server_receipt_mismatch')
    return {'schema': 'gig.private.deployment.qualification.v1',
            'status': 'PASS_OFFLINE_CHECKS_ONLY' if not failures else 'BLOCKED',
            'expected_source_sha': expected_sha, 'checkout_receipt': receipt,
            'runtime': runtime, 'launcher': launcher, 'local_server': local,
            'failures': failures, 'network_requests': int(check_local_server),
            'external_requests': 0, 'private_target_acceptance': 'UNVERIFIED',
            'limitations': ['Startup receipt is not loaded-byte attestation or authentication',
                            'No provider, credentials, port visibility or private configuration inspected',
                            'No vulnerability clearance; run offline pip check and target advisory review',
                            'Offline proxy tests do not prove owner HTTPS/WSS or GitHub access control']}
