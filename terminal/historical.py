"""Whitelisted authored native diagnostics. Never accepts private input paths."""
import asyncio
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_LIMIT = 192 * 1024


def source_identity():
    digest = hashlib.sha256()
    for directory in ('include', 'src'):
        for path in sorted((ROOT / directory).rglob('*')):
            if path.is_file():
                digest.update(str(path.relative_to(ROOT)).encode())
                digest.update(b'\0')
                digest.update(path.read_bytes())
    return digest.hexdigest()


async def bounded_native(command):
    """One trusted child, bounded transport output and wall time, no shell."""
    child = await asyncio.create_subprocess_exec(
        *map(str, command), stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE, limit=OUTPUT_LIMIT + 1)
    async def read(stream):
        value = await stream.read(OUTPUT_LIMIT + 1)
        if len(value) > OUTPUT_LIMIT:
            raise ValueError('native_output_budget')
        # read(n) may be short before EOF; accumulate within the same fixed budget.
        while True:
            block = await stream.read(OUTPUT_LIMIT + 1 - len(value))
            if not block:
                return value
            value += block
            if len(value) > OUTPUT_LIMIT:
                raise ValueError('native_output_budget')
    try:
        async with asyncio.timeout(20):
            stdout, stderr = await asyncio.gather(read(child.stdout), read(child.stderr))
            code = await child.wait()
        if code:
            raise ValueError('native_authored_validation_failed')
        return json.loads(stdout)
    finally:
        if child.returncode is None:
            child.kill()
            await child.wait()


async def run_authored_validation(profile):
    if profile not in ('itch', 'lobster'):
        raise ValueError('unsupported_authored_profile')
    build = Path(os.environ.get('GIG_TERMINAL_NATIVE_BUILD', str(ROOT / 'build/phase9-clean-release')))
    executable = build / ('gig_itch_validation_demo' if profile == 'itch' else 'gig_lobster_validate')
    if not executable.is_file():
        raise ValueError('native_diagnostic_not_built')
    if profile == 'itch':
        report = await bounded_native([executable, 'restart', source_identity()])
    else:
        # This import contains only independently authored toy fixture generation.
        spec = importlib.util.spec_from_file_location('terminal_authored_lobster', ROOT / 'scripts/lobster_synthetic.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory(prefix='gig-authored-lobster-') as temp:
            message_rows, reference_rows = module.rows()
            manifest, messages, reference = module.write(Path(temp) / 'fixture', message_rows, reference_rows)
            dataset = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
            report = await bounded_native([executable, '--authored', messages, reference,
                manifest['message_sha256'], manifest['reference_sha256'], dataset, '32', '65536', '8388608'])
    return {'schema_version': '1', 'profile': profile, 'origin': 'HISTORICAL_SYNTHETIC',
            'observed_data_accessed': False, 'native_report': report,
            'scope': 'Authored native diagnostic; not an imported observed dataset or interactive source replay'}
