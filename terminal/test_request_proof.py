"""Actual owner POST failure and endpoint-bound read proof;not forwarded-header trust."""
import json,os,unittest
from unittest.mock import patch
from starlette.testclient import TestClient
from terminal.server.app import create_app
from terminal.server.request_proofs import RequestProofs

ORIGIN='https://authored-http-rewrite-8787.app.github.dev'
ATTEMPT='01234567-89ab-cdef-0123-456789abcdef'
RAW={'Origin':'http://localhost:8787','Host':'localhost:8787','X-Forwarded-Host':'authored-http-rewrite-8787.app.github.dev','X-Forwarded-Proto':'https','X-Forwarded-Port':'443'}
BODY={'browser_origin':ORIGIN,'websocket_url':ORIGIN.replace('https:','wss:')+'/api/v1/stream','attempt_id':ATTEMPT}

class RequestProof(unittest.TestCase):
    def setUp(self):
        env=patch.dict(os.environ,{'CODESPACES':'true','CODESPACE_NAME':'authored-http-rewrite','GIG_TERMINAL_ALLOWED_ORIGINS':ORIGIN})
        env.start();self.addCleanup(env.stop)
        self.client=TestClient(create_app(),base_url='http://localhost:8787');self.client.__enter__();self.addCleanup(self.client.__exit__,None,None,None)
    def read(self,target='/api/v1/stream-ticket',**changes):
        headers={**RAW,'X-GIG-Bootstrap':'same-origin-v1','X-GIG-Browser-Origin':ORIGIN,'X-GIG-Target':target,'Sec-Fetch-Site':'same-origin',**changes}
        return self.client.get('/api/v1/request-proof',headers=headers)
    def test_exact_unproved_failure_is_still_rejected(self):
        r=self.client.post('/api/v1/stream-ticket',headers=RAW,json=BODY);self.assertEqual(r.status_code,403)
        d=self.client.get('/api/v1/connection').json();self.assertEqual(d['last_mutation']['failure_condition'],'origin_mismatch');self.assertIsNone(d['last_browser_bootstrap'])
    def test_exact_rewrite_issues_ws_ticket_only_with_independent_read_proof(self):
        read=self.read();self.assertEqual(read.status_code,200);proof=read.json()['proof']
        self.assertEqual(read.headers['cache-control'],'no-store');self.assertEqual(read.headers['cross-origin-resource-policy'],'same-origin')
        r=self.client.post('/api/v1/stream-ticket',headers={**RAW,'X-GIG-Request-Proof':proof},json=BODY);self.assertEqual(r.status_code,200)
        d=self.client.get('/api/v1/connection').json()
        self.assertEqual(d['last_mutation']['authorization'],'codespaces_rewrite_request_proof')
        self.assertEqual(d['last_browser_bootstrap']['origin'],'http://localhost:8787')
        self.assertEqual(d['last_browser_bootstrap']['browser_origin'],ORIGIN)
        self.assertEqual(d['last_browser_bootstrap']['authorized_browser_origin'],ORIGIN)
        self.assertNotIn(proof,json.dumps(d));self.assertNotIn(r.json()['ticket'],json.dumps(d))
        self.assertEqual(self.client.post('/api/v1/stream-ticket',headers={**RAW,'X-GIG-Request-Proof':proof},json=BODY).status_code,403)
    def test_rewritten_native_control(self):
        proof=self.read('/api/v1/control').json()['proof']
        r=self.client.post('/api/v1/control',headers={**RAW,'X-GIG-Request-Proof':proof},json={'action':'step'})
        self.assertEqual(r.status_code,200);self.assertEqual(r.json()['position'],21)
    def test_wrong_target_burns_proof(self):
        proof=self.read().json()['proof']
        r=self.client.post('/api/v1/control',headers={**RAW,'X-GIG-Request-Proof':proof},json={'action':'step'});self.assertEqual(r.status_code,403)
        self.assertEqual(self.client.get('/api/v1/state').json()['position'],20)
        self.assertEqual(self.client.post('/api/v1/stream-ticket',headers={**RAW,'X-GIG-Request-Proof':proof},json=BODY).status_code,403)
    def test_forwarded_headers_alone_cannot_read_capability(self):
        self.assertEqual(self.client.get('/api/v1/request-proof',headers=RAW).status_code,403)
        self.assertEqual(self.client.get('/api/v1/request-proof').status_code,403)
    def test_cross_origin_metadata_or_foreign_origin_refused(self):
        for change in ({'Sec-Fetch-Site':'cross-site'},{'Sec-Fetch-Site':'same-site'},{'Origin':'https://attacker.invalid'},{'X-GIG-Browser-Origin':'https://attacker.invalid'},{'X-GIG-Target':'/arbitrary'},{'X-GIG-Bootstrap':''}):
            self.assertEqual(self.read(**change).status_code,403,change)
    def test_cross_origin_custom_header_preflight_denied(self):
        for origin in ('https://attacker.invalid','http://localhost:8787',ORIGIN):
            r=self.client.options('/api/v1/request-proof',headers={'Origin':origin,'Access-Control-Request-Method':'GET','Access-Control-Request-Headers':'x-gig-bootstrap,x-gig-browser-origin,x-gig-target'})
            self.assertEqual(r.status_code,400)
    def test_foreign_or_missing_mutation_origin_not_rescued_by_proof(self):
        for origin in ('https://attacker.invalid',None):
            proof=self.read('/api/v1/control').json()['proof'];h={**RAW,'X-GIG-Request-Proof':proof}
            if origin is None:h.pop('Origin')
            else:h['Origin']=origin
            self.assertEqual(self.client.post('/api/v1/control',headers=h,json={'action':'step'}).status_code,403)
    def test_get_without_origin_is_supported_only_with_same_origin_read_context(self):
        r=self.read(Origin='');self.assertEqual(r.status_code,403)
        h={k:v for k,v in RAW.items() if k!='Origin'};h.update({'X-GIG-Bootstrap':'same-origin-v1','X-GIG-Browser-Origin':ORIGIN,'X-GIG-Target':'/api/v1/control'})
        self.assertEqual(self.client.get('/api/v1/request-proof',headers=h).status_code,200)
    def test_wrong_raw_host_not_rescued_by_forwarded_host(self):
        proof=self.read('/api/v1/control').json()['proof']
        self.assertEqual(self.client.post('/api/v1/control',headers={**RAW,'Host':'127.0.0.1:8787','X-GIG-Request-Proof':proof},json={'action':'step'}).status_code,403)
    def test_proof_capacity_expiry_one_use(self):
        now=[0];proofs=RequestProofs(clock=lambda:now[0],capacity=1,ttl=30)
        token=proofs.issue(ORIGIN,'/api/v1/control')
        with self.assertRaises(ValueError):proofs.issue(ORIGIN,'/api/v1/control')
        now[0]=30;self.assertIsNone(proofs.consume(token))
        token=proofs.issue(ORIGIN,'/api/v1/control');self.assertEqual(proofs.consume(token)['target'],'/api/v1/control');self.assertIsNone(proofs.consume(token))

if __name__=='__main__':unittest.main()
