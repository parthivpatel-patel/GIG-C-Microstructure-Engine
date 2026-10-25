"""Native-backed public controls: explicit server gates, same secure POST boundary."""
import os,unittest
from unittest.mock import patch
from starlette.testclient import TestClient
from terminal.server.app import create_app

class LiveAPI(unittest.TestCase):
    def setUp(self):
        self.env=patch.dict(os.environ,{'GIG_LIVE_ENABLED':'0','GIG_TERMINAL_ALLOWED_ORIGINS':'http://localhost:8787'})
        self.env.start();self.addCleanup(self.env.stop)
        self.client=TestClient(create_app(),base_url='http://localhost:8787')
        self.client.__enter__();self.addCleanup(self.client.__exit__,None,None,None)
    def post(self,action,value=None,origin='http://localhost:8787'):
        return self.client.post('/api/v1/control',headers={'Origin':origin},json={'action':action,'value':value})
    def test_disabled_feed_never_falls_back_to_authored_liquidity(self):
        response=self.post('connect',{'provider':'kraken','instrument':'ETH/USD','depth':10})
        self.assertEqual(response.status_code,200)
        state=response.json();self.assertEqual(state['origin'],'UNAVAILABLE');self.assertEqual(state['book'],{'bids':[],'asks':[]})
        self.assertEqual(state['feed']['state'],'ERROR');self.assertFalse(state['feed']['real_time'])
        self.assertFalse(state['provenance']['recording_enabled'])
    def test_invalid_provider_url_depth_instrument_rejected(self):
        for value in ({'provider':'https://attacker.invalid','instrument':'BTC/USD','depth':10},
                      {'provider':'kraken','instrument':'BTC/EUR','depth':10},
                      {'provider':'kraken','instrument':'BTC/USD','depth':1000},
                      {'provider':'kraken','instrument':'BTC/USD','depth':True},
                      {'provider':'kraken','instrument':'BTC/USD','depth':10,'url':'https://attacker.invalid'}):
            self.assertEqual(self.post('connect',value).status_code,400)
    def test_origin_boundary_not_bypassed_by_new_controls(self):
        self.assertEqual(self.post('connect','kraken','https://attacker.invalid').status_code,403)
        self.assertEqual(self.client.get('/api/v1/state').json()['mode'],'HISTORICAL_REPLAY')
    def test_invalid_mode_does_not_change_feed_state(self):
        state=self.post('connect','kraken').json()
        self.assertEqual(self.post('mode','INVALID').status_code,400)
        after=self.client.get('/api/v1/state').json()
        self.assertEqual(after['feed']['state'],state['feed']['state'])
        self.assertEqual(after['mode'],state['mode'])
    def test_switch_back_retains_native_replay(self):
        self.post('connect','kraken');self.post('disconnect')
        state=self.post('mode','HISTORICAL_REPLAY').json()
        self.assertEqual(state['position'],20);self.assertEqual(state['origin'],'HISTORICAL_SYNTHETIC')
        self.assertEqual(self.post('step').json()['position'],21)

if __name__=='__main__':unittest.main()
