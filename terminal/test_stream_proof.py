"""Exact reported localhost rewrite; forwarded-header forgery never authorizes it."""
import json,os,unittest
from unittest.mock import patch
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect
from terminal.server.app import create_app
from terminal.server.stream_tickets import StreamTickets,authorize_socket,PROTOCOL,PREFIX

ORIGIN='https://authored-rewrite-check-8787.app.github.dev'
URL='wss://authored-rewrite-check-8787.app.github.dev/api/v1/stream'
ATTEMPT='01234567-89ab-cdef-0123-456789abcdef'
REWRITE={'Origin':'http://localhost:8787','Host':'localhost:8787','X-Forwarded-Host':'authored-rewrite-check-8787.app.github.dev','X-Forwarded-Proto':'https'}

class ProofContracts(unittest.TestCase):
    def setUp(self):
        self.env=patch.dict(os.environ,{'CODESPACES':'true','CODESPACE_NAME':'authored-rewrite-check','GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN':'app.github.dev','GIG_TERMINAL_ALLOWED_ORIGINS':ORIGIN})
        self.env.start();self.addCleanup(self.env.stop)
        self.client=TestClient(create_app(),base_url=ORIGIN);self.client.__enter__();self.addCleanup(self.client.__exit__,None,None,None)
    def mint(self,origin=ORIGIN,**changes):
        return self.client.post('/api/v1/stream-ticket',headers={'Origin':origin},json={'browser_origin':origin,'websocket_url':URL,'attempt_id':ATTEMPT,**changes})
    def refuse(self,headers,protocols=None):
        with self.assertRaises(WebSocketDisconnect):
            with self.client.websocket_connect('ws://localhost:8787/api/v1/stream',headers=dict(headers),subprotocols=protocols or []):pass
    def test_exact_reported_handshake_still_denied_without_proof(self):
        self.refuse(REWRITE)
        self.assertEqual(self.client.get('/api/v1/connection').json()['last_websocket']['decision'],'rejected_origin')
    def test_valid_http_origin_proves_rewritten_socket_and_native_control(self):
        response=self.mint();self.assertEqual(response.status_code,200);token=response.json()['ticket']
        with self.client.websocket_connect('ws://localhost:8787/api/v1/stream',headers=dict(REWRITE),subprotocols=[PROTOCOL,PREFIX+token]) as ws:
            self.assertEqual(ws.accepted_subprotocol,PROTOCOL)
            self.assertEqual(ws.receive_json()['position'],20)
            self.assertEqual(self.client.post('/api/v1/control',headers={'Origin':ORIGIN},json={'action':'step'}).status_code,200)
            for _ in range(5):
                if ws.receive_json()['position']==21:break
            else:self.fail('native prefix did not advance')
        diag=self.client.get('/api/v1/connection').json()
        self.assertEqual(diag['last_browser_bootstrap']['origin'],ORIGIN)
        self.assertEqual(diag['last_websocket']['authorization'],'accepted_codespaces_rewrite_ticket')
        self.assertEqual(diag['last_websocket']['attempt_id'],ATTEMPT)
        self.assertNotIn(token,json.dumps(diag))
        self.refuse(REWRITE,[PROTOCOL,PREFIX+token])  # One use.
    def test_foreign_origin_cannot_mint_even_with_forwarded_forgery(self):
        response=self.client.post('/api/v1/stream-ticket',headers={**REWRITE,'Origin':'https://attacker.invalid'},json={'browser_origin':ORIGIN,'websocket_url':URL,'attempt_id':ATTEMPT})
        self.assertEqual(response.status_code,403)
    def test_local_origin_cannot_mint(self):self.assertEqual(self.mint('http://localhost:8787').status_code,403)
    def test_valid_ticket_cannot_authorize_foreign_origin(self):
        token=self.mint().json()['ticket'];self.refuse({**REWRITE,'Origin':'https://attacker.invalid'},[PROTOCOL,PREFIX+token])
    def test_valid_ticket_cannot_authorize_other_local_port(self):
        token=self.mint().json()['ticket'];self.refuse({**REWRITE,'Origin':'http://localhost:9999'},[PROTOCOL,PREFIX+token])
    def test_forwarded_headers_do_not_substitute_wrong_host(self):
        token=self.mint().json()['ticket'];self.refuse({**REWRITE,'Host':'127.0.0.1:8787'},[PROTOCOL,PREFIX+token])
    def test_wrong_context_cannot_mint(self):
        for changes in ({'browser_origin':'https://attacker.invalid'},{'websocket_url':'wss://attacker.invalid/api/v1/stream'},{'websocket_url':URL+'?token=x'},{'attempt_id':'invalid'}):
            self.assertEqual(self.mint(**changes).status_code,400)
    def test_malformed_protocol_or_guessed_ticket_denied(self):
        self.refuse(REWRITE,[PROTOCOL,PREFIX+'x'*43])
        token=self.mint().json()['ticket'];self.refuse(REWRITE,[PREFIX+token])
    def test_existing_client_capacity_is_preserved(self):
        from contextlib import ExitStack
        with ExitStack() as stack:
            for _ in range(8):
                ws=stack.enter_context(self.client.websocket_connect(ORIGIN.replace('https','wss')+'/api/v1/stream',headers={'Origin':ORIGIN}))
                self.assertTrue(ws.receive_json()['engine']['native'])
            self.refuse({'Origin':ORIGIN,'Host':'localhost:8787'})
            self.assertEqual(self.client.get('/api/v1/connection').json()['last_websocket']['authorization'],'rejected_capacity')

    def test_normal_origin_uses_and_consumes_proof(self):
        token=self.mint().json()['ticket']
        with self.client.websocket_connect(ORIGIN.replace('https','wss')+'/api/v1/stream',headers={'Origin':ORIGIN},subprotocols=[PROTOCOL,PREFIX+token]) as ws:self.assertTrue(ws.receive_json()['engine']['native'])
        self.refuse(REWRITE,[PROTOCOL,PREFIX+token])

class Bounds(unittest.TestCase):
    def test_expiry_capacity_and_one_use(self):
        now=[0];tickets=StreamTickets(clock=lambda:now[0],capacity=1,ttl=30)
        token=tickets.issue(ORIGIN,ATTEMPT)
        with self.assertRaises(ValueError):tickets.issue(ORIGIN,ATTEMPT)
        self.assertNotIn(token,repr(tickets.pending))
        now[0]=30;self.assertIsNone(tickets.consume(token))
        fresh=tickets.issue(ORIGIN,ATTEMPT);self.assertEqual(tickets.consume(fresh)['origin'],ORIGIN);self.assertIsNone(tickets.consume(fresh))
    def test_forwarded_headers_cannot_enable_compatibility_outside_codespaces(self):
        tickets=StreamTickets();token=tickets.issue(ORIGIN,ATTEMPT)
        accepted,_,_,_=authorize_socket({k.lower():v for k,v in REWRITE.items()},[PROTOCOL,PREFIX+token],[ORIGIN],None,tickets)
        self.assertFalse(accepted)

if __name__=='__main__':unittest.main()
