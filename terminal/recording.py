"""Bounded authored event recording; observed recording is deliberately unavailable."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
import time

MAX_BYTES = 2 * 1024 * 1024
MAX_RECORDS = 512
MAX_DATASETS = 8
MAX_AGE_SECONDS = 24 * 60 * 60


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def safe_id(identity):
    if type(identity) is not str or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,47}', identity):
        raise ValueError('recording_identity')
    return identity


def root_path(directory):
    directory = Path(directory)
    if directory.is_symlink():
        raise ValueError('recording_root_symlink')
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    return directory.resolve()


def save_authored(directory, identity, events, *, origin, enabled=False):
    # No observed data enters the encoder, filesystem or retention mechanism.
    if enabled is not True:
        raise ValueError('recording_disabled')
    if origin != 'HISTORICAL_SYNTHETIC':
        raise ValueError('observed_recording_permission_unverified')
    identity = safe_id(identity)
    if type(events) not in (list, tuple) or len(events) > MAX_RECORDS:
        raise ValueError('recording_record_budget')
    from .server.fixtures import EVENTS, FIXTURE_SHA256
    # Current recording scope is the exact independently authored source only.
    # Reject arbitrary caller values/provenance before storing or relabeling them.
    if list(events) != list(EVENTS):
        raise ValueError('recording_not_authored_source')
    payload = b''.join(canonical(event) + b'\n' for event in events)
    if len(payload) > MAX_BYTES:
        raise ValueError('recording_byte_budget')
    root = root_path(directory)
    if len(list(root.iterdir())) >= MAX_DATASETS:
        raise ValueError('recording_dataset_budget')
    target = root / identity
    if target.exists() or target.is_symlink():
        raise ValueError('recording_exists')
    staged = Path(tempfile.mkdtemp(prefix='.pending-', dir=root))
    try:
        digest = hashlib.sha256(payload).hexdigest()
        manifest = {'schema': 'gig.terminal.authored_recording.v1', 'origin': origin,
            'identity': identity, 'records': len(events), 'bytes': len(payload),
            'sha256': digest, 'fixture_sha256': FIXTURE_SHA256,
            'complete': True, 'created_unix_seconds': int(time.time()),
            'retention_seconds': MAX_AGE_SECONDS, 'observed_recording': False}
        for name, data in [('events.jsonl', payload), ('manifest.json', canonical(manifest))]:
            fd = os.open(staged / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, 'wb') as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
        # Single-owner gateway performs this operation; not a hostile shared-FS sandbox.
        if target.exists():
            raise ValueError('recording_exists')
        staged.rename(target)
        return manifest
    except BaseException:
        shutil.rmtree(staged, ignore_errors=True)
        raise


def load_authored(directory, identity, *, enforce_retention=True):
    root = root_path(directory)
    target = root / safe_id(identity)
    if target.is_symlink() or not target.is_dir():
        raise ValueError('recording_path')
    result = []
    for name, limit in [('manifest.json', 8192), ('events.jsonl', MAX_BYTES)]:
        path = target / name
        if path.is_symlink():
            raise ValueError('recording_path')
        with path.open('rb') as stream:
            data = stream.read(limit + 1)
        if len(data) > limit:
            raise ValueError('recording_byte_budget')
        result.append(data)
    manifest = json.loads(result[0])
    if manifest.get('schema') != 'gig.terminal.authored_recording.v1' or manifest.get('origin') != 'HISTORICAL_SYNTHETIC' or manifest.get('complete') is not True or manifest.get('observed_recording') is not False:
        raise ValueError('recording_manifest')
    if manifest.get('identity') != identity or manifest.get('bytes') != len(result[1]) or manifest.get('sha256') != hashlib.sha256(result[1]).hexdigest():
        raise ValueError('recording_integrity')
    if type(manifest.get('created_unix_seconds')) is not int or (enforce_retention and (time.time() - manifest['created_unix_seconds'] > MAX_AGE_SECONDS or manifest['created_unix_seconds'] > time.time()+60)):
        raise ValueError('recording_retention_expired')
    events = [json.loads(line) for line in result[1].splitlines()]
    from .server.fixtures import EVENTS, FIXTURE_SHA256
    if events != list(EVENTS) or manifest.get('fixture_sha256') != FIXTURE_SHA256 or manifest.get('records') != len(events):
        raise ValueError('recording_not_authored_source')
    return manifest, events


def delete_authored(directory, identity):
    # Validate an allowed authored dataset before deleting, no arbitrary paths.
    manifest, _ = load_authored(directory, identity, enforce_retention=False)
    shutil.rmtree(root_path(directory) / safe_id(identity))
    return manifest['identity']
