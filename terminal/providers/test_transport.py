"""Actual local WSS-shape client lifecycle contract; no external socket."""
import asyncio,json,unittest
from unittest.mock import patch
from .kraken import Permission,ProviderError,live_messages

class Transport(unittest.IsolatedAsyncioTestCase):
    async def test_exact_endpoint_budgets_subscriptions_and_redirect_denial(self):
        calls=[];sent=[];stop=asyncio.Event()
        class AuthoredConnect:
            def __init__(self,*args,**kwargs):calls.append((args,kwargs));calls.append(self)
            async def __aenter__(self):return self
            async def __aexit__(self,*args):calls.append('closed')
            async def send(self,raw):sent.append(json.loads(raw))
            async def recv(self):return '{"channel":"heartbeat"}'
        with patch('websockets.asyncio.client.connect',AuthoredConnect):
            stream=live_messages(Permission(True,True,True,False,'authored-transport-only'),stop=stop,symbol='ETH/USD')
            self.assertEqual(await anext(stream),'{"channel":"heartbeat"}')
            error=ValueError('authored redirect');self.assertIs(calls[1].process_redirect(error),error)
            stop.set();await stream.aclose()
        args,options=calls[0];self.assertEqual(args,('wss://ws.kraken.com/v2',))
        self.assertEqual(options['max_size'],65536);self.assertEqual(options['max_queue'],4)
        self.assertEqual(options['open_timeout'],10)
        self.assertEqual([x['params']['channel'] for x in sent],['book','trade'])
        self.assertTrue(all(x['params']['symbol']==['ETH/USD'] for x in sent))
        self.assertEqual(calls[-1],'closed')
    async def test_permission_failure_before_client_creation(self):
        with patch('websockets.asyncio.client.connect') as connect:
            stream=live_messages(Permission(),stop=asyncio.Event())
            with self.assertRaises(ProviderError):await anext(stream)
            connect.assert_not_called()

if __name__=='__main__':unittest.main()
