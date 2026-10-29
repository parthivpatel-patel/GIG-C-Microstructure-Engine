"""Build once, then qualify browser journeys against an unchanged asset snapshot.

Start the authored fixture servers on 8787/18787/18788/18789 first (see Phase 2
report). Do not rebuild assets while this command runs. No provider requests.
"""
from pathlib import Path
import hashlib
import json
import os
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.environ.get('GIG_ATLAS_BROWSER_EVIDENCE', str(ROOT / 'build/atlas2/resume'))).resolve()
SCRIPTS = ('browser-validation', 'stock-intelligence-validation',
           'stock-loading-validation', 'atlas-validation', 'atlas2-validation',
           'recorded-playback-validation', 'live-controls-validation')


def snapshot():
    dist = ROOT / 'terminal/web/dist'
    return {str(p.relative_to(dist)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(dist.rglob('*')) if p.is_file()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / 'build.log').open('w') as log:
        subprocess.run(['npm', '--prefix', 'terminal/web', 'run', 'build'],
                       cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
    expected = snapshot()
    if 'index.html' not in expected or '.vite/manifest.json' not in expected:
        raise RuntimeError('Incomplete asset build')
    completed = []
    for name in SCRIPTS:
        if snapshot() != expected:
            raise RuntimeError('Assets changed before ' + name)
        with (OUT / (name + '.log')).open('w') as log:
            result = subprocess.run(['node', 'terminal/tests/' + name + '.mjs'],
                                    cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                                    env={**os.environ, 'TERMINAL_URL': 'http://127.0.0.1:8787',
                                         'TERMINAL_EVIDENCE': str(OUT / 'native-browser')})
        if snapshot() != expected:
            raise RuntimeError('Assets changed during ' + name)
        if result.returncode:
            raise RuntimeError(name + ' failed; see its preserved log')
        completed.append(name)
    (OUT / 'stable-assets.json').write_text(json.dumps(
        {'schema': 'gig.atlas.stable-assets.v1', 'completed': completed,
         'asset_sha256': expected, 'asset_mutation_detected': False}, indent=2)+'\n')
    print('PASS: build completed before all seven browser suites; asset hashes unchanged')


if __name__ == '__main__':
    main()
