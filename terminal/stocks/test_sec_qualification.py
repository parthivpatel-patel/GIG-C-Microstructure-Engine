"""Offline SEC qualification diagnostics;all responses and contacts are authored."""
import asyncio
import contextlib
import io
import json
import os
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import AsyncMock,MagicMock,patch

from scripts import qualify_sec_sources as q
from .service import StockWorkspace
from .test_workspace import CIK,SEC_ENV,facts
from .sec_config import save,resolve

SCRIPT=Path(q.__file__)
ARGS=['--fetch','--resolve-identity','--symbol','AAPL','--as-of','2026-10-28']


def entrypoint(args,environment=None):
    out=io.StringIO()
    with patch.dict(os.environ,SEC_ENV if environment is None else environment,clear=True),patch('sys.argv',[str(SCRIPT),*args]),contextlib.redirect_stdout(out):
        try:runpy.run_path(str(SCRIPT),run_name='__main__')
        except SystemExit as error:code=error.code
        else:raise AssertionError('CLI must exit explicitly')
    return code,json.loads(out.getvalue()),out.getvalue()


class CLIReproductions(unittest.TestCase):
    def test_directory_validation_is_not_hidden_by_generic_error(self):
        # The exact owner command,with an authored invalid directory over the real parser.
        payload={'0':{'cik_str':320193,'ticker':'../invalid','title':'Authored issuer'}}
        with patch.object(StockWorkspace,'fetch',AsyncMock(return_value=(payload,'a'*64))):
            code,result,_=entrypoint(ARGS)
        self.assertEqual(code,2)
        self.assertEqual(result['reason'],'sec_directory_symbol')
        self.assertEqual(result['diagnostic']['stage'],'identity_resolution')
        self.assertEqual(result['diagnostic']['category'],'SOURCE_SCHEMA')
        self.assertFalse(result['raw_retained'])

    def test_facts_validation_reports_actual_stage_and_code(self):
        payload=facts();payload['facts']['us-gaap']['Revenues']['units']['USD'][0]['end']='2025-01-01'
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'authored.json';path.write_text(json.dumps(payload))
            code,result,_=entrypoint(['--company-facts',str(path),'--symbol','AAPL','--as-of','2026-10-28'])
        self.assertEqual(code,2);self.assertEqual(result['reason'],'sec_fact_period')
        self.assertEqual(result['diagnostic']['stage'],'companyfacts_validation')
        self.assertEqual(result['diagnostic']['category'],'SOURCE_SEMANTICS')

    def test_prefix_lookalike_exception_does_not_disclose_contact(self):
        secret='SEC_AUTHORED_CONTACT_do_not_echo@example.invalid'
        with patch.object(StockWorkspace,'fetch',AsyncMock(side_effect=ValueError(secret))):
            code,result,output=entrypoint(ARGS)
        self.assertEqual(code,2);self.assertNotIn(secret,output)
        self.assertEqual(result['reason'],'sanitized_source_or_configuration_failure')


class DiagnosticCategories(unittest.TestCase):
    def test_every_known_code_has_a_fixed_category(self):
        for category,codes in q.ERROR_GROUPS.items():
            for code in codes:
                with self.subTest(code=code):
                    result=q.failure_result(ValueError(code),'identity_resolution')
                    self.assertEqual(result['reason'],code);self.assertEqual(result['diagnostic']['category'],category)

    def test_unknown_prefixes_types_and_sensitive_text_are_redacted(self):
        class SensitiveException(Exception):pass
        for error in [ValueError('SEC_HTTP_403 contact@example.invalid'),ValueError('backend_contact@example.invalid'),ValueError('sec_directory_symbol\ncontact@example.invalid'),SensitiveException('contact@example.invalid'),KeyError('contact@example.invalid'),OSError('/private/contact@example.invalid')]:
            with self.subTest(kind=type(error).__name__):
                encoded=json.dumps(q.failure_result(error))
                self.assertNotIn('contact@example.invalid',encoded)
                self.assertLess(len(encoded),700)

    def test_HTTP_status_is_structured_not_arbitrary_exception_text(self):
        for token,status in [('SEC_HTTP_403',403),('upstream_http_429',429),('SEC_HTTP_503',503)]:
            result=q.failure_result(ValueError(token),'identity_resolution')
            self.assertEqual(result['diagnostic']['http_status'],status)
            self.assertEqual(result['diagnostic']['category'],'HTTP_STATUS')
        for token in ('SEC_HTTP_4030','SEC_HTTP_099','SEC_HTTP_403?secret=authored'):
            self.assertNotIn('http_status',q.failure_result(ValueError(token))['diagnostic'])

    def test_transport_errors_are_categorized_without_URLs_or_headers(self):
        import httpx
        errors=[(httpx.ProxyError,'PROXY'),(httpx.ReadTimeout,'TIMEOUT'),(httpx.ConnectError,'CONNECT_OR_TLS'),(httpx.RemoteProtocolError,'TRANSPORT')]
        for kind,category in errors:
            result=q.failure_result(kind('https://secret@example.invalid/private'),'companyfacts_fetch')
            self.assertEqual(result['diagnostic']['category'],category)
            self.assertNotIn('example.invalid',json.dumps(result))

    def test_JSON_and_unicode_errors_never_echo_source_documents(self):
        errors=[(json.JSONDecodeError('authored private','authored private',0),'SOURCE_JSON'),
                (UnicodeDecodeError('utf8',b'\xff',0,1,'authored private'),'SOURCE_ENCODING'),
                (RecursionError('authored private'),'RESOURCE_LIMIT')]
        for error,category in errors:
            r=q.failure_result(error,'companyfacts_decode');self.assertEqual(r['diagnostic']['category'],category)
            self.assertNotIn('authored private',json.dumps(r))


class PipelineBoundaries(unittest.TestCase):
    def offline(self,raw,args=()):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'authored.json';path.write_bytes(raw)
            return entrypoint(['--company-facts',str(path),'--as-of','2026-10-28',*args])

    def test_offline_success_keeps_independent_reconciliation_and_unverified_file_origin(self):
        code,result,output=self.offline(json.dumps(facts()).encode())
        self.assertEqual(code,0);self.assertEqual(result['mismatch_count'],0)
        self.assertGreater(result['matched_records'],0)
        self.assertEqual(result['source_authority'],'owner_supplied_file_origin_not_independently_authenticated')
        self.assertIn('independent_reconciliation',result['diagnostics']['completed_stages'])
        self.assertNotIn(SEC_ENV['GIG_SEC_USER_AGENT'],output)

    def test_JSON_duplicates_constants_and_body_budget_remain_rejected(self):
        for raw,reason in [(b'{"cik":1,"cik":2}','source_duplicate_field'),(b'{"val":NaN}','source_constant'),(b'x'*8388609,'source_body_budget'),(b'{private_html_not_JSON','source_invalid_json')]:
            code,result,_=self.offline(raw)
            self.assertEqual(code,2);self.assertEqual(result['reason'],reason)
            self.assertEqual(result['diagnostic']['stage'],'companyfacts_decode')

    def test_missing_required_fact_key_is_not_disclosed_or_accepted(self):
        payload=facts();del payload['facts']['us-gaap']['Revenues']['units']['USD'][0]['val']
        code,result,_=self.offline(json.dumps(payload).encode())
        self.assertEqual(code,2);self.assertEqual(result['reason'],'source_required_field_missing')
        self.assertEqual(result['diagnostic']['stage'],'companyfacts_validation')

    def test_invalid_calendar_dates_keep_fixed_sec_date_diagnostic(self):
        for field in ('start','end','filed'):
            payload=facts();payload['facts']['us-gaap']['Revenues']['units']['USD'][0][field]='2024-02-30'
            code,result,_=self.offline(json.dumps(payload).encode())
            self.assertEqual(code,2);self.assertEqual(result['reason'],'sec_date')
            self.assertEqual(result['diagnostic']['stage'],'companyfacts_validation')

    def test_contradictory_facts_remain_rejected(self):
        payload=facts();rows=payload['facts']['us-gaap']['Revenues']['units']['USD'];rows.append({**rows[0],'val':999})
        code,result,_=self.offline(json.dumps(payload).encode())
        self.assertEqual(code,2);self.assertEqual(result['reason'],'sec_contradictory_fact')

    def test_invalid_input_has_no_source_requests(self):
        with patch.object(StockWorkspace,'fetch',AsyncMock())as fetch,patch('httpx.Client')as client:
            for extra,reason in [(['--as-of','2026-02-30'],'sec_date'),(['--symbol','../invalid'],'invalid_symbol')]:
                code,result,_=entrypoint([*ARGS,*extra])
                self.assertEqual(code,2);self.assertEqual(result['reason'],reason)
                self.assertEqual(result['diagnostic']['stage'],'input_validation')
            fetch.assert_not_awaited();client.assert_not_called()

    def test_missing_SEC_configuration_stops_before_identity_or_provider_access(self):
        with patch('terminal.stocks.sec_config.resolve',return_value=({}, {'source':'environment','error':None})),patch.object(StockWorkspace,'fetch',AsyncMock())as fetch,patch('httpx.Client')as client:
            code,result,_=entrypoint(ARGS,environment={})
        self.assertEqual(code,2);self.assertEqual(result['diagnostic']['category'],'CONFIGURATION')
        self.assertEqual(result['diagnostic']['stage'],'sec_configuration')
        fetch.assert_not_awaited();client.assert_not_called()

    def test_private_file_permission_fault_is_reported_without_contact_or_path(self):
        with tempfile.TemporaryDirectory() as root:
            save('authored-owner@example.invalid',policy_reviewed=True,root=root)
            (Path(root)/'.gig-sec/config.json').chmod(0o644)
            with patch('terminal.stocks.sec_config.resolve',side_effect=lambda e:resolve(e,root=root)),patch.object(StockWorkspace,'fetch',AsyncMock())as fetch:
                code,result,output=entrypoint(ARGS,environment={})
        self.assertEqual(code,2);self.assertEqual(result['reason'],'sec_private_configuration_invalid')
        self.assertNotIn('authored-owner@example.invalid',output);self.assertNotIn(root,output);fetch.assert_not_awaited()

    def test_private_ready_configuration_and_disabled_Alpaca_run_exact_SEC_pipeline(self):
        directory={'0':{'cik_str':320193,'ticker':'AAPL','title':'Authored issuer'}}
        raw=json.dumps(facts()).encode();response=MagicMock(status_code=200,headers={'content-length':str(len(raw))})
        response.iter_raw.return_value=iter([raw[:10],raw[10:]])
        client=MagicMock();client.__enter__.return_value=client;client.stream.return_value.__enter__.return_value=response
        with tempfile.TemporaryDirectory() as root:
            save('authored-owner@example.invalid',policy_reviewed=True,root=root)
            with patch('terminal.stocks.sec_config.resolve',side_effect=lambda e:resolve(e,root=root)),patch.object(StockWorkspace,'fetch',AsyncMock(return_value=(directory,'a'*64)))as fetch,patch('httpx.Client',return_value=client)as factory,patch('time.sleep')as sleep:
                code,result,output=entrypoint(ARGS,environment={'GIG_ALPACA_ENABLED':'0'})
        self.assertEqual(code,0);self.assertEqual(result['mismatch_count'],0)
        self.assertEqual(result['identity_reference']['cik'],CIK)
        self.assertEqual(result['diagnostics']['configuration']['configuration_source'],'private_file_with_environment_precedence')
        self.assertTrue(result['diagnostics']['configuration']['ready'])
        self.assertNotIn('authored-owner@example.invalid',output)
        self.assertEqual(fetch.await_count,1);sleep.assert_called_once_with(1.01)
        self.assertEqual(client.stream.call_count,1)
        self.assertEqual(client.stream.call_args.args,('GET','https://data.sec.gov/api/xbrl/companyfacts/CIK'+CIK+'.json'))
        self.assertFalse(factory.call_args.kwargs['follow_redirects']);self.assertEqual(factory.call_args.kwargs['timeout'],8)

    def test_unknown_authoritative_symbol_does_not_fall_back_to_seed(self):
        directory={'0':{'cik_str':42,'ticker':'AUTHORED','title':'Fictional issuer42'}}
        with patch.object(StockWorkspace,'fetch',AsyncMock(return_value=(directory,'a'*64))),patch('httpx.Client')as client:
            code,result,_=entrypoint(ARGS)
        self.assertEqual(code,2);self.assertEqual(result['reason'],'SEC_authoritative_symbol_unavailable');client.assert_not_called()

    def test_HTTP_error_reports_identity_stage_and_stops_without_retry(self):
        from .service import AccessError
        with patch.object(StockWorkspace,'fetch',AsyncMock(side_effect=AccessError('upstream_http_403')))as fetch,patch('httpx.Client')as client:
            code,result,_=entrypoint(ARGS)
        self.assertEqual(code,2);self.assertEqual(result['diagnostic']['http_status'],403)
        self.assertEqual(result['diagnostic']['stage'],'identity_resolution');self.assertEqual(fetch.await_count,1);client.assert_not_called()

    def test_decode_success_but_issuer_mismatch_reports_companyfacts_validation(self):
        payload=facts();payload['cik']=42
        code,result,_=self.offline(json.dumps(payload).encode())
        self.assertEqual(code,2);self.assertEqual(result['reason'],'sec_identity')
        self.assertIn('companyfacts_decode',result['diagnostics']['completed_stages'])

    def test_companyfacts_HTTP_failure_keeps_completed_identity_stage(self):
        directory={'0':{'cik_str':320193,'ticker':'AAPL','title':'Authored issuer'}}
        client,response=SourceBoundary().mock_client(status=403)
        with patch.object(StockWorkspace,'fetch',AsyncMock(return_value=(directory,'a'*64))),patch('httpx.Client',return_value=client),patch('time.sleep'):
            code,result,_=entrypoint(ARGS)
        self.assertEqual(code,2);self.assertEqual(result['diagnostic']['stage'],'companyfacts_fetch')
        self.assertEqual(result['diagnostic']['http_status'],403)
        self.assertIn('identity_resolution',result['diagnostics']['completed_stages'])
        self.assertNotIn('companyfacts_receipt',result['diagnostics']);response.iter_raw.assert_not_called()

    def test_pipeline_closes_identity_workspace_on_rejection(self):
        with patch.object(StockWorkspace,'fetch',AsyncMock(side_effect=ValueError('sec_directory_schema'))),patch.object(StockWorkspace,'close',AsyncMock())as close:
            code,result,_=entrypoint(ARGS)
        self.assertEqual(code,2);self.assertEqual(result['reason'],'sec_directory_schema');close.assert_awaited_once()


class SourceBoundary(unittest.TestCase):
    def mock_client(self,status=200,headers=None,chunks=(b'{}',)):
        response=MagicMock(status_code=status,headers=headers or {})
        response.iter_raw.return_value=iter(chunks)
        client=MagicMock();client.__enter__.return_value=client;client.stream.return_value.__enter__.return_value=response
        return client,response

    def test_invalid_CIK_cannot_construct_a_network_request(self):
        for cik in ['../private','320193','0000000000',True,None]:
            with patch('httpx.Client')as client:
                with self.assertRaisesRegex(ValueError,'SEC_invalid_cik'):q.official_fetch(cik,SEC_ENV)
                client.assert_not_called()

    def test_bad_status_compression_and_declared_length_stop_before_body_iteration(self):
        cases=[(403,{},'SEC_HTTP_403'),(302,{},'SEC_HTTP_302'),(429,{},'SEC_HTTP_429'),(200,{'content-encoding':'gzip'},'SEC_encoding'),(200,{'content-length':'8388609'},'SEC_body_budget'),(200,{'content-length':'invalid'},'SEC_length')]
        for status,headers,reason in cases:
            client,response=self.mock_client(status,headers)
            with patch('httpx.Client',return_value=client):
                with self.assertRaisesRegex(ValueError,reason):q.official_fetch(CIK,SEC_ENV)
            response.iter_raw.assert_not_called();self.assertEqual(client.stream.call_count,1)

    def test_stream_body_and_total_deadline_limits_unchanged(self):
        for chunks,clock,reason in [((b'x'*8388609,),[0,0],'SEC_body_budget'),((b'{}',),[0,30],'SEC_total_deadline')]:
            client,_=self.mock_client(chunks=chunks)
            with patch('httpx.Client',return_value=client),patch.object(q.time,'monotonic',side_effect=clock):
                with self.assertRaisesRegex(ValueError,reason):q.official_fetch(CIK,SEC_ENV)

    def test_rejected_directory_does_not_publish_accepted_identity_state(self):
        directory={'0':{'cik_str':320193,'ticker':'AAPL','title':'Authored'},'1':{'cik_str':42,'ticker':'AAPL','title':'Conflicting'}}
        async def fetch(*_):return json.dumps(directory).encode()
        workspace=StockWorkspace(environment=SEC_ENV,fetcher=fetch)
        with self.assertRaisesRegex(ValueError,'sec_directory_duplicate_symbol'):asyncio.run(q.resolve_reference('AAPL',workspace))
        self.assertEqual(workspace.issuers,{});self.assertIsNone(workspace.issuer_source)


if __name__=='__main__':unittest.main()
