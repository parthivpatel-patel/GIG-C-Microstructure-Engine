"""Handshake-only contract; no public connection or market subscription."""
import asyncio,importlib.util,json,ssl,socket,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('ws_diagnostic',Path(__file__).resolve().parents[1]/'scripts/diagnose_websocket_access.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class Diagnostic(unittest.IsolatedAsyncioTestCase):
    async def execute(self,frames,**options):
        captured={}
        class TLS:
            def getpeercert(self):return {'validated':True}
        class Connection:
            response=SimpleNamespace(status_code=101)
            transport=SimpleNamespace(get_extra_info=lambda _:TLS())
            async def recv(self):
                captured['reads']=captured.get('reads',0)+1
                return frames.pop(0) if frames else '{"channel":"heartbeat"}'
            async def send(self,*_):raise AssertionError('No application send allowed')
        class Connector:
            def __init__(self,url,**kwargs):captured.update(url=url,options=kwargs)
            async def __aenter__(self):return Connection()
            async def __aexit__(self,*_):captured['closed']=True
        async def resolve(*args,**kwargs):captured['dns']=args;return [(None,)*5]
        result=await module.diagnose('kraken',connector=Connector,resolver=resolve,proxy_configured=options.get('proxy',False))
        return result,captured
    async def test_passive_control_only_no_send_strict_tls_and_limits(self):
        r,c=await self.execute(['{"channel":"status","secret":"never-print"}','{"channel":"heartbeat"}'])
        self.assertEqual(r['dns']['status'],'RESOLVED');self.assertEqual(r['tls']['status'],'VERIFIED')
        self.assertEqual(r['websocket']['http_status'],101);self.assertEqual(r['protocol']['control_frames'],2)
        self.assertEqual(r['subscriptions_sent'],0);self.assertTrue(c['closed']);self.assertNotIn('never-print',json.dumps(r))
        self.assertEqual(c['options']['max_size'],4096);self.assertEqual(c['options']['max_queue'],1)
        self.assertEqual(c['options']['ssl'].verify_mode,ssl.CERT_REQUIRED);self.assertTrue(c['options']['ssl'].check_hostname)
    async def test_unexpected_application_frame_stops_without_copying_fields(self):
        r,c=await self.execute(['{"channel":"book","private_price":123456789}','{"channel":"heartbeat"}'])
        self.assertTrue(r['protocol']['unexpected_application_frame']);self.assertEqual(c['reads'],1)
        self.assertNotIn('123456789',json.dumps(r));self.assertNotIn('private_price',json.dumps(r))
    async def test_proxy_does_not_trigger_direct_dns_or_expose_configuration(self):
        r,c=await self.execute([],proxy=True)
        self.assertNotIn('dns',c);self.assertEqual(r['dns']['status'],'NOT_OBSERVED_PROXY_RESOLUTION')
    async def test_failed_dns_prevents_websocket_attempt(self):
        async def resolve(*args,**kwargs):raise socket.gaierror()
        def connect(*args,**kwargs):self.fail('must not connect')
        r=await module.diagnose('kraken',connector=connect,resolver=resolve,proxy_configured=False)
        self.assertEqual(r['dns']['status'],'FAILED');self.assertEqual(r['websocket']['status'],'NOT_ATTEMPTED')
    async def test_tls_failure_is_separate_and_sanitized(self):
        class Connector:
            def __init__(self,*args,**kwargs):pass
            async def __aenter__(self):raise ssl.SSLCertVerificationError('secret-cert')
            async def __aexit__(self,*args):pass
        r=await module.diagnose('kraken',connector=Connector,proxy_configured=True)
        self.assertEqual(r['tls']['status'],'CERTIFICATE_REJECTED');self.assertNotIn('secret-cert',str(r))
    async def test_unknown_endpoint_rejected_and_redirects_never_followed(self):
        with self.assertRaises(ValueError):await module.diagnose('wss://arbitrary.invalid')
        connector=module.FixedEndpoint(module.ENDPOINTS['kraken']);error=ValueError('redirect')
        self.assertIs(connector.process_redirect(error),error)
    async def test_metadata_redirect_only_canonical_same_host_no_credentials(self):
        spec=importlib.util.spec_from_file_location('http_diag',Path(__file__).resolve().parents[1]/'scripts/diagnose_provider_access.py')
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        url='https://docs.kraken.com/api/docs/websocket-v2/book/'
        self.assertEqual(m.safe_redirect(url,'/api/docs/websocket-v2/book'),url[:-1])
        for target in ('https://[invalid','https://attacker.invalid/',url+'?token=secret','http://docs.kraken.com/api/docs/websocket-v2/book','https://user:secret@docs.kraken.com/api/docs/websocket-v2/book'):
            self.assertIsNone(m.safe_redirect(url,target))

if __name__=='__main__':unittest.main()
