"""Metadata diagnostic policy; no external requests."""
import importlib.util,unittest
from pathlib import Path
from unittest.mock import Mock
import httpx
spec=importlib.util.spec_from_file_location('provider_diagnostic',Path(__file__).resolve().parents[1]/'scripts/diagnose_provider_access.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class Diagnostic(unittest.TestCase):
    def test_only_three_allowlisted_head_requests_no_body_or_redirect(self):
        class Response:
            status_code=302
            def __enter__(self):return self
            def __exit__(self,*_):pass
            @property
            def content(self):raise AssertionError('body accessed')
        client=Mock();client.stream.return_value=Response()
        result=module.diagnose('kraken',client)
        self.assertEqual(client.stream.call_count,3)
        self.assertEqual([c.args[0] for c in client.stream.call_args_list],['HEAD']*3)
        self.assertEqual([c.args[1] for c in client.stream.call_args_list],list(module.ENDPOINTS['kraken']))
        self.assertFalse(result['websocket_started']);self.assertFalse(result['permission_verified'])
    def test_proxy_error_does_not_echo_credentials(self):
        client=Mock();client.stream.side_effect=httpx.ProxyError('secret-token@private-proxy')
        report=module.diagnose('coinbase',client)
        self.assertNotIn('secret-token',str(report));self.assertEqual(report['results'][0]['failure'],'proxy_connect_denied')
    def test_unknown_url_not_accepted(self):
        with self.assertRaises(ValueError):module.diagnose('https://attacker.invalid',Mock())

if __name__=='__main__':unittest.main()
