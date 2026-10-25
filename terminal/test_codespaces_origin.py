"""Reproduce direct-ASGI Codespaces startup and TLS-terminating forwarded requests."""
import os
import unittest
from unittest.mock import patch
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect
from terminal.server.app import create_app

ORIGIN='https://authored-origin-check-8787.app.github.dev'
HEADERS={'Origin':ORIGIN,'X-Forwarded-Proto':'https','X-Forwarded-Host':'authored-origin-check-8787.app.github.dev','X-Forwarded-Port':'443'}

class DirectAsgiCodespaces(unittest.TestCase):
    def setUp(self):
        self.environment=patch.dict(os.environ,{'CODESPACES':'true','CODESPACE_NAME':'authored-origin-check','GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN':'app.github.dev'})
        self.environment.start();self.addCleanup(self.environment.stop)
        explicit=patch.dict(os.environ);explicit.start();self.addCleanup(explicit.stop)
        os.environ.pop('GIG_TERMINAL_ALLOWED_ORIGINS',None)
        # Proxy may rewrite Host to its internal backend while browser Origin stays HTTPS.
        self.client=TestClient(create_app(),base_url='http://127.0.0.1:8787')
        self.client.__enter__();self.addCleanup(self.client.__exit__,None,None,None)
    def test_direct_asgi_forwarded_mutation(self):
        self.assertEqual(self.client.get('/api/v1/state').status_code,200)
        response=self.client.post('/api/v1/control',json={'action':'step'},headers=HEADERS)
        self.assertEqual(response.status_code,200,response.text)
        self.assertEqual(response.json()['position'],21)
    def test_direct_asgi_forwarded_websocket(self):
        with self.client.websocket_connect('ws://127.0.0.1:8787/api/v1/stream',headers=HEADERS) as ws:
            self.assertTrue(ws.receive_json()['engine']['native'])

    def test_diagnostics_capture_actual_safe_proxy_headers(self):
        headers={**HEADERS,'Cookie':'DO_NOT_RETAIN_COOKIE','Authorization':'Bearer DO_NOT_RETAIN_TOKEN','X-Forwarded-For':'DO_NOT_RETAIN_CLIENT_IP'}
        self.client.post('/api/v1/control',json={'action':'pause'},headers=headers)
        response=self.client.get('/api/v1/connection',headers=HEADERS)
        data=response.json();self.assertEqual(data['configured_origins'],[ORIGIN])
        self.assertEqual(data['request']['host'],'127.0.0.1:8787')
        self.assertEqual(data['request']['origin'],ORIGIN)
        self.assertEqual(data['request']['x_forwarded_proto'],'https')
        self.assertEqual(data['request']['x_forwarded_host'],'authored-origin-check-8787.app.github.dev')
        self.assertEqual(data['request']['asgi_scheme'],'http')
        self.assertEqual(data['last_mutation']['decision'],'allowed')
        for secret in ('DO_NOT_RETAIN_COOKIE','DO_NOT_RETAIN_TOKEN','DO_NOT_RETAIN_CLIENT_IP'):self.assertNotIn(secret,response.text)
    def test_forwarded_headers_never_authorize_foreign_origin(self):
        response=self.client.post('/api/v1/control',json={'action':'step'},headers={**HEADERS,'Origin':'https://attacker.invalid'})
        self.assertEqual(response.status_code,403)
        data=self.client.get('/api/v1/connection').json()
        self.assertEqual(data['last_mutation']['decision'],'rejected_origin')
        self.assertEqual(self.client.get('/api/v1/state').json()['position'],20)
    def test_websocket_reconnect_keeps_native_prefix(self):
        for position in (20,21):
            with self.client.websocket_connect('ws://127.0.0.1:8787/api/v1/stream',headers=HEADERS) as ws:
                self.assertEqual(ws.receive_json()['position'],position)
            if position==20:self.client.post('/api/v1/control',json={'action':'step'},headers=HEADERS)
        data=self.client.get('/api/v1/connection').json()
        self.assertEqual(data['last_websocket']['decision'],'accepted')
        self.assertEqual(data['last_websocket']['upgrade_status'],101)
        self.assertEqual(data['last_websocket']['origin'],ORIGIN)
    def test_rejected_websocket_has_classified_diagnostic(self):
        with self.assertRaises(WebSocketDisconnect):
            with self.client.websocket_connect('ws://127.0.0.1:8787/api/v1/stream',headers={**HEADERS,'Origin':'https://attacker.invalid'}):pass
        data=self.client.get('/api/v1/connection').json()
        self.assertEqual(data['last_websocket']['decision'],'rejected_origin')
        self.assertEqual(data['last_websocket']['upgrade_status'],403)
    def test_explicit_wrong_codespace_origin_fails_startup(self):
        with patch.dict(os.environ,{'GIG_TERMINAL_ALLOWED_ORIGINS':'http://127.0.0.1:8787'}):
            with self.assertRaisesRegex(ValueError,'excludes'):create_app()

class SafeDiagnosticsAndStartup(unittest.TestCase):
    def test_codespace_name_without_flag_still_derives_exact_origin(self):
        from terminal.server.config import launch_settings
        host,configured,expected=launch_settings({'CODESPACE_NAME':'authored-origin-check'})
        self.assertEqual(host,'127.0.0.1')
        self.assertEqual(configured,ORIGIN);self.assertEqual(expected,ORIGIN)
    def test_credential_shaped_origin_redacted(self):
        from terminal.server.connection import origin_value
        for value in ('https://user:secret@example.com','https://example.com/?token=secret','x'*1000):
            self.assertEqual(origin_value(value),'<invalid>')
    def test_start_script_refuses_to_replace_listening_process(self):
        import errno,socket,subprocess,sys,tempfile
        from pathlib import Path
        listener=socket.socket()
        try:
            try:listener.bind(('127.0.0.1',8787));listener.listen(1)
            except OSError as e:
                if e.errno!=errno.EADDRINUSE:raise
                listener.close()  # Existing listener must likewise never be killed/replaced.
            with tempfile.TemporaryDirectory(prefix='gig-start-refusal-') as temp:
                root=Path(temp);(root/'scripts').mkdir();(root/'.venv/bin').mkdir(parents=True)
                (root/'terminal/web/dist').mkdir(parents=True);(root/'terminal/web/dist/index.html').touch()
                (root/'.venv/bin/python').symlink_to(sys.executable)
                script=Path(__file__).resolve().parents[1]/'scripts/start_terminal.sh'
                (root/'scripts/start_terminal.sh').write_bytes(script.read_bytes())
                result=subprocess.run(['bash','scripts/start_terminal.sh'],cwd=root,capture_output=True,text=True,timeout=5)
                self.assertNotEqual(result.returncode,0);self.assertIn('already in use',result.stderr)
        finally:listener.close()

if __name__=='__main__':unittest.main()
