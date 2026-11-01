"""Local ASGI fixtures only;Origin/proof boundary remains mandatory for fake actions."""
import os
from pathlib import Path
import tempfile
import unittest
from starlette.testclient import TestClient
from terminal.paper.workspace import PaperWorkspace
from terminal.paper.contracts import PaperError
from terminal.server.app import create_app
from terminal.stocks.service import StockWorkspace

ORIGIN='http://127.0.0.1:8787'

class PaperAPI(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.directory=Path(self.temp.name)/'private'
        self.workspace=PaperWorkspace(self.directory)
        self.client=TestClient(create_app(stock_workspace=StockWorkspace(environment={}),paper_workspace=self.workspace),base_url=ORIGIN)
    def tearDown(self): self.client.close();self.temp.cleanup()
    def post(self,v,**kwargs): return self.client.post('/api/v1/paper/control',json=v,headers={'Origin':ORIGIN},**kwargs)
    def test_default_disabled_no_storage(self):
        r=self.client.get('/api/v1/paper/status');self.assertEqual(r.status_code,200)
        self.assertEqual(r.json()['mode'],'DISABLED');self.assertIsNone(r.json()['account']);self.assertFalse(self.directory.exists())
    def test_no_origin_forged_forwarding(self):
        for headers in ({},{'Origin':'https://evil.invalid'},{'Origin':'http://localhost:8787','Host':'evil.invalid','X-Forwarded-Host':'127.0.0.1:8787','X-Forwarded-Proto':'https'}):
            r=self.client.post('/api/v1/paper/control',json={'action':'open_fake'},headers=headers)
            self.assertIn(r.status_code,(400,403));self.assertFalse(self.directory.exists())
    def test_target_bound_proof(self):
        headers={'X-GIG-Bootstrap':'same-origin-v1','X-GIG-Browser-Origin':ORIGIN,'X-GIG-Target':'/api/v1/paper/control'}
        p=self.client.get('/api/v1/request-proof',headers=headers);self.assertEqual(p.status_code,200)
        token=p.json()['proof'];h={'Origin':ORIGIN,'X-GIG-Request-Proof':token}
        self.assertEqual(self.client.post('/api/v1/paper/control',json={'action':'open_fake'},headers=h).status_code,200)
        self.assertEqual(self.client.post('/api/v1/paper/control',json={'action':'open_fake'},headers=h).status_code,403)
    def test_bounded_invalid_json(self):
        for content in ('{"action":"open_fake","action":"kill"}', 'x'*4097):
            r=self.client.post('/api/v1/paper/control',content=content,headers={'Origin':ORIGIN,'Content-Type':'application/json'})
            self.assertIn(r.status_code,(400,413));self.assertFalse(self.directory.exists())
    def test_no_external_action(self):
        for body in ({'action':'open_alpaca'},{'action':'open_fake','host':'https://api.alpaca.markets'},{'action':'submit','intent':{}}):
            self.assertEqual(self.post(body).status_code,422)
        self.assertFalse(self.directory.exists())
    def test_fake_flow_without_native_mutation(self):
        before=self.client.get('/api/v1/state').json()
        for body in ({'action':'open_fake'},{'action':'arm_fake','acknowledge_example_limits':True},
                     {'action':'submit','request_id':'fixture-one','intent':{'symbol':'AAPL','side':'buy','quantity':'1','limit_price':'100','type':'limit','time_in_force':'day'}},
                     {'action':'fill','request_id':'fixture-one','quantity':1,'price':'100'}, {'action':'kill_and_cancel'}):
            r=self.post(body);self.assertEqual(r.status_code,200,r.text)
        s=r.json();self.assertEqual(s['orders'][0]['state'],'FILLED');self.assertTrue(s['kill_switch'])
        self.assertEqual(s['account']['positions'],{'AAPL':1});self.assertFalse(s['external_execution_enabled'])
        after=self.client.get('/api/v1/state').json();self.assertEqual(before['book'],after['book']);self.assertEqual(before['position'],after['position'])
    def test_corruption_safe_response(self):
        self.assertEqual(self.post({'action':'open_fake'}).status_code,200)
        self.workspace.engine.store.path.write_bytes(b'corrupt synthetic sqlite fixture')
        r=self.client.get('/api/v1/paper/status');self.assertEqual(r.status_code,422)
        self.assertNotIn(str(self.directory),r.text)
    def test_restart_rearms_kill(self):
        self.post({'action':'open_fake'});self.post({'action':'arm_fake','acknowledge_example_limits':True})
        self.workspace.engine=None
        r=self.post({'action':'open_fake'});self.assertEqual(r.status_code,200);self.assertTrue(r.json()['kill_switch'])

if __name__=='__main__':unittest.main()
