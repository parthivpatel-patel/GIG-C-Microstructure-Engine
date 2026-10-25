"""Local tests of forwarded-origin policy; no Codespace or external URL is created."""
import os
from unittest.mock import patch
import unittest
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect
from terminal.server.__main__ import launch_settings
from terminal.server.app import create_app, origins_from_environment

ORIGIN='https://authored-access-check-8787.app.github.dev'

class Launcher(unittest.TestCase):
    def test_local_default_stays_loopback(self):
        self.assertEqual(launch_settings({}),('127.0.0.1',None,None))
    def test_codespace_exact_private_origin(self):
        settings=launch_settings({'CODESPACES':'true','CODESPACE_NAME':'authored-access-check'})
        self.assertEqual(settings,('0.0.0.0',ORIGIN,ORIGIN))
    def test_codespace_custom_domain(self):
        value=launch_settings({'CODESPACES':'true','CODESPACE_NAME':'authored','GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN':'app.github.dev'})
        self.assertEqual(value[2],'https://authored-8787.app.github.dev')
    def test_incomplete_codespace_fails_closed(self):
        for extra in ({},{'CODESPACE_NAME':'bad/name'},{'CODESPACE_NAME':'valid','GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN':'bad/name'}):
            with self.assertRaises(ValueError):launch_settings({'CODESPACES':'true',**extra})
    def test_wrong_explicit_origin_fails_closed(self):
        with self.assertRaises(ValueError):launch_settings({'CODESPACES':'true','CODESPACE_NAME':'authored-access-check','GIG_TERMINAL_ALLOWED_ORIGINS':'https://wrong.example'})
    def test_malformed_configuration_is_rejected(self):
        for value in ('https://example.com;bad','https://exam\r\nple.com','https://example.com:0','https://example.com:99999','https://user:pass@example.com','https://*.example.com','https://example.com/path'):
            with patch.dict(os.environ,{'GIG_TERMINAL_ALLOWED_ORIGINS':value}):
                with self.assertRaises(RuntimeError):origins_from_environment()

class ForwardedContracts(unittest.TestCase):
    def setUp(self):
        self.env=patch.dict(os.environ,{'GIG_TERMINAL_ALLOWED_ORIGINS':ORIGIN});self.env.start();self.addCleanup(self.env.stop)
        self.client=TestClient(create_app(),base_url=ORIGIN);self.client.__enter__();self.addCleanup(self.client.__exit__,None,None,None)
    def test_native_http_and_forwarded_csp(self):
        response=self.client.get('/api/v1/state');self.assertEqual(response.status_code,200)
        self.assertTrue(response.json()['engine']['native']);self.assertEqual(response.json()['origin'],'HISTORICAL_SYNTHETIC')
        self.assertIn('wss://authored-access-check-8787.app.github.dev',response.headers['content-security-policy'])
        self.assertNotIn('connect-src *',response.headers['content-security-policy'])
    def test_exact_remote_origin_can_control_real_native(self):
        response=self.client.post('/api/v1/control',json={'action':'step'},headers={'Origin':ORIGIN})
        self.assertEqual(response.status_code,200);self.assertEqual(response.json()['position'],21)
    def test_foreign_origin_cannot_control(self):
        response=self.client.post('/api/v1/control',json={'action':'step'},headers={'Origin':'https://attacker.invalid'})
        self.assertEqual(response.status_code,403)
    def test_wrong_host_is_denied(self):
        self.assertEqual(self.client.get('/api/v1/state',headers={'Host':'attacker.invalid'}).status_code,400)
    def test_remote_websocket_same_native_data(self):
        with self.client.websocket_connect(ORIGIN.replace('https:','wss:')+'/api/v1/stream',headers={'Origin':ORIGIN}) as socket:
            self.assertEqual(socket.receive_json()['position'],20)
    def test_remote_websocket_foreign_origin_denied(self):
        with self.assertRaises(WebSocketDisconnect):
            with self.client.websocket_connect(ORIGIN.replace('https:','wss:')+'/api/v1/stream',headers={'Origin':'https://attacker.invalid'}):pass

if __name__=='__main__':unittest.main()
