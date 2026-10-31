"""Independently authored exact-SHA/asset/launcher failure controls; no providers."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from terminal.verification.artifacts import EvidenceError
from terminal.verification.deployment import local_health, qualify, release_receipt, runtime_inventory


class Deployment(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.dist = self.root / 'terminal/web/dist'
        (self.dist / '.vite').mkdir(parents=True)
        (self.dist / 'assets').mkdir()
        (self.dist / 'assets/index-test.js').write_bytes(b'authored fixture, not market data')
        (self.dist / 'index.html').write_bytes(b'authored index')
        (self.dist / '.vite/manifest.json').write_text(json.dumps({'index.html': {'file': 'assets/index-test.js'}}))
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        subprocess.run(['git', '-C', str(self.root), 'add', '.'], check=True)
        subprocess.run(['git', '-C', str(self.root), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                        'commit', '-qm', 'authored'], check=True)
        self.sha = subprocess.check_output(['git', '-C', str(self.root), 'rev-parse', 'HEAD'], text=True).strip()
        self.runtime = {'all_direct_pins_match': True}

    def check(self, **kwargs):
        with patch('terminal.verification.deployment.runtime_inventory', return_value=self.runtime):
            return qualify(self.root, kwargs.pop('expected_sha', self.sha), environment=kwargs.pop('environment', {}), **kwargs)

    def test_exact_receipt_no_network_by_default(self):
        with patch('socket.socket.connect', side_effect=AssertionError('unexpected network')):
            value = self.check()
        self.assertEqual(value['status'], 'PASS_OFFLINE_CHECKS_ONLY')
        self.assertEqual(value['external_requests'], 0)
        self.assertEqual(value['private_target_acceptance'], 'UNVERIFIED')
        self.assertEqual(value['checkout_receipt']['frontend_entry_sha256'],
                         hashlib.sha256(b'authored fixture, not market data').hexdigest())

    def test_wrong_sha_dirty_and_untracked_runtime_detected(self):
        self.assertIn('checkout_sha_mismatch', self.check(expected_sha='1' * 40)['failures'])
        (self.dist / 'index.html').write_bytes(b'changed')
        self.assertIn('tracked_changes_present', self.check()['failures'])
        scripts = self.root / 'scripts'; scripts.mkdir()
        (scripts / 'unexpected.py').write_text('pass')
        self.assertIn('untracked_runtime_source', self.check()['failures'])

    def test_missing_and_escaping_assets_fail(self):
        for entry in ('../private.js', '/etc/passwd', 'assets/../../secret.js', None):
            with self.subTest(entry=entry):
                (self.dist / '.vite/manifest.json').write_text(json.dumps({'index.html': {'file': entry}}))
                self.assertIn('frontend_identity_unavailable', release_receipt(self.root)['errors'])
        (self.dist / '.vite/manifest.json').unlink()
        self.assertIn('frontend_identity_unavailable', release_receipt(self.root)['errors'])

    def test_symlink_asset_rejected(self):
        entry = self.dist / 'assets/index-test.js'; entry.unlink(); entry.symlink_to(self.dist / 'index.html')
        self.assertIn('frontend_identity_unavailable', release_receipt(self.root)['errors'])

    def test_codespace_metadata_and_expanded_origins_are_not_authentication(self):
        env = {'CODESPACES': 'true', 'CODESPACE_NAME': 'authored-fixture'}
        value = self.check(environment=env)
        self.assertTrue(value['launcher']['exact_forwarded_origin_only'])
        self.assertEqual(value['launcher']['private_port_authentication'], 'UNVERIFIED_EXTERNAL_GATE')
        env['GIG_TERMINAL_ALLOWED_ORIGINS'] = 'https://authored-fixture-8787.app.github.dev,https://evil.invalid'
        self.assertIn('launcher_not_single_exact_origin', self.check(environment=env)['failures'])
        env['CODESPACE_NAME'] = 'invalid/../name'
        self.assertIn('launcher_metadata_invalid', self.check(environment=env)['failures'])

    def test_runtime_mismatch_and_stale_startup_receipt(self):
        startup = release_receipt(self.root)
        # An app retains its startup receipt across a checkout/asset change.
        (self.dist / 'index.html').write_bytes(b'new frontend')
        self.assertNotEqual(startup['frontend_index_sha256'], release_receipt(self.root)['frontend_index_sha256'])
        observed = {key: startup[key] for key in ('source_sha', 'tracked_clean', 'frontend_entry_sha256', 'frontend_index_sha256')}
        with patch('terminal.verification.deployment.local_health', return_value=observed):
            self.assertIn('running_server_receipt_mismatch', self.check(check_local_server=True)['failures'])
        self.runtime['all_direct_pins_match'] = False
        self.assertIn('runtime_pin_mismatch', self.check()['failures'])

    def test_explicit_loopback_is_fixed_bounded_and_redacted(self):
        class Response:
            status = 200
            headers = {'Content-Length': '10000000'}
            reads = 0
            def __enter__(self):return self
            def __exit__(self, *args):pass
            def read(self, count):self.reads += 1; return b'x' * count
        response = Response()
        with patch('urllib.request.build_opener') as build:
            build.return_value.open.return_value = response
            with self.assertRaisesRegex(EvidenceError, 'local_health_budget'):local_health()
            self.assertEqual(response.reads, 0)
            self.assertEqual(build.return_value.open.call_args.args[0], 'http://127.0.0.1:8787/api/v1/health')
            self.assertEqual(build.return_value.open.call_args.kwargs['timeout'], 2)
            response.headers = {}
            with self.assertRaisesRegex(EvidenceError, 'local_health_budget'):local_health()
            self.assertEqual(response.reads, 1)

    def test_dependency_inventory_is_read_only_and_pin_specific(self):
        source = Path(__file__).resolve().parents[1]
        value = runtime_inventory(source)
        self.assertEqual(len(value['pins']), 17)
        self.assertTrue(value['all_direct_pins_match'])
        self.assertTrue(any(p['dependencies'] for p in value['installed']))
        self.assertTrue(value['security_clearance'].startswith('UNVERIFIED'))


class AppReceipt(unittest.TestCase):
    def test_health_freezes_startup_source_receipt(self):
        from starlette.testclient import TestClient
        from terminal.server.app import create_app
        from terminal.stocks.service import StockWorkspace
        startup = {'schema': 'gig.application.release.v1', 'source_sha': 'a' * 40,
                   'tracked_clean': True, 'frontend_entry_sha256': 'b' * 64,
                   'frontend_index_sha256': 'c' * 64, 'errors': []}
        with patch('terminal.verification.deployment.release_receipt', return_value=copy.deepcopy(startup)) as capture:
            app = create_app(stock_workspace=StockWorkspace(environment={}))
        with TestClient(app, base_url='http://127.0.0.1:8787') as client:
            self.assertEqual(client.get('/api/v1/health').json()['application_release'], startup)
            self.assertEqual(client.get('/api/v1/health').json()['application_release'], startup)
        self.assertEqual(capture.call_count, 1)
