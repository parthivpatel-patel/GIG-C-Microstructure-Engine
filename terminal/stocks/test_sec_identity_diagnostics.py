"""Authored rejection predicates,not a captured live SEC response or license claim."""
import asyncio,copy,json,unittest
from unittest.mock import AsyncMock,patch
from .service import StockWorkspace
from . import sec_identity
from scripts import qualify_sec_sources as q
from .test_workspace import SEC_ENV
from .test_sec_qualification import entrypoint,ARGS


def payload(value,key='7'):
    # AAPL intentionally follows the failing record to test full-request context.
    return {key:{'ticker':value,'cik_str':42,'title':'Authored unrelated reference'},
            '20':{'ticker':'AAPL','cik_str':320193,'title':'Authored Apple'}}


class RejectionContext(unittest.TestCase):
    def fail_cli(self,value):
        with patch.object(StockWorkspace,'fetch',AsyncMock(return_value=(payload(value),'a'*64)))as fetch:
            code,result,output=entrypoint(ARGS)
        self.assertEqual(code,2);self.assertEqual(result['reason'],'sec_directory_symbol')
        self.assertEqual(result['diagnostic']['stage'],'identity_resolution');self.assertEqual(fetch.await_count,1)
        self.assertIn('directory_rejection',result['diagnostic'])
        return result['diagnostic']['directory_rejection'],output

    def test_actual_error_family_distinguishes_all_four_remaining_conditions(self):
        for value,condition,kind in [(None,'NON_STRING','null'),(True,'NON_STRING','boolean'),(42,'NON_STRING','integer'),([], 'NON_STRING','array'),('', 'EMPTY','string'),('X'*65,'TOO_LONG','string'),('AUTH_', 'REFERENCE_PATTERN','string')]:
            with self.subTest(condition=condition,kind=kind):
                d,_=self.fail_cli(value)
                self.assertEqual(d['condition'],condition);self.assertEqual(d['value_type'],kind)
                self.assertEqual(d['record_key'],'7');self.assertEqual(d['record_ordinal'],1)
                self.assertEqual(d['input_records'],2);self.assertEqual(d['requested_exact_records'],1)
                self.assertEqual(d['requested_symbol'],'AAPL');self.assertEqual(d['source_sha256'],'a'*64)
                self.assertEqual(d['parser_path'],'reference_admission')

    def test_reference_syntax_flags_identify_structure_without_printing_values(self):
        for value,expected in [('AUTH_',['UNDERSCORE','DISALLOWED_ASCII']),('AUTH--',['TRAILING_SEPARATOR','REPEATED_SEPARATOR']),('AUTH..A',['REPEATED_SEPARATOR']),(' AAPL',['WHITESPACE','DISALLOWED_ASCII']),('A\nB',['CONTROL','WHITESPACE','DISALLOWED_ASCII']),('Aé',['NON_ASCII'])]:
            with self.subTest(flags=expected):
                d,output=self.fail_cli(value)
                self.assertTrue(set(expected)<=set(d['shape_flags']))
                self.assertNotIn(value,output)

    def test_requested_relation_is_diagnostic_only_and_never_normalizes_acceptance(self):
        for value,relation in [(' AAPL','ASCII_WHITESPACE_VARIANT'),('aapl ','ASCII_CASE_WHITESPACE_VARIANT'),('OTHER_','OTHER_STRING'),(None,'NON_STRING')]:
            with self.subTest(relation=relation):
                d,_=self.fail_cli(value);self.assertEqual(d['requested_relation'],relation)

    def test_exact_AAPL_itself_cannot_trigger_remaining_guard(self):
        self.assertIsNone(sec_identity.symbol_condition('AAPL'))
        rows,_=sec_identity.parse_reference({'0':{'ticker':'AAPL','cik_str':320193,'title':'Authored Apple'}},requested_symbol='AAPL')
        self.assertEqual(rows['AAPL']['cik'],'0000320193')

    def test_empty_or_missing_exact_requested_reference_is_not_invented(self):
        data=payload(None);del data['20']
        with patch.object(StockWorkspace,'fetch',AsyncMock(return_value=(data,'b'*64))):
            code,result,_=entrypoint(ARGS)
        self.assertEqual(code,2);d=result['diagnostic']['directory_rejection']
        self.assertEqual(d['requested_exact_records'],0);self.assertEqual(d['requested_relation'],'NON_STRING')

    def test_duplicate_requested_records_are_reported_without_choosing_an_identity(self):
        data=payload('BAD_');data['21']={**data['20'],'cik_str':43}
        with patch.object(StockWorkspace,'fetch',AsyncMock(return_value=(data,'b'*64))):
            code,result,_=entrypoint(ARGS)
        self.assertEqual(code,2);self.assertEqual(result['diagnostic']['directory_rejection']['requested_exact_records'],2)

    def test_record_position_counts_capture_order_not_numeric_key_order(self):
        data={'40':{'ticker':'AAPL','cik_str':320193,'title':'Authored Apple'},'3':{'ticker':'','cik_str':42,'title':'Authored invalid'}}
        with patch.object(StockWorkspace,'fetch',AsyncMock(return_value=(data,'c'*64))):
            code,result,_=entrypoint(ARGS)
        d=result['diagnostic']['directory_rejection'];self.assertEqual(code,2)
        self.assertEqual((d['record_key'],d['record_ordinal']),('3',2))

    def test_parser_fingerprint_and_path_are_reproducible_public_source_metadata(self):
        import hashlib
        from pathlib import Path
        d,_=self.fail_cli('BAD_')
        self.assertEqual(d['parser_profile'],sec_identity.PARSER_PROFILE)
        self.assertEqual(d['parser_source_sha256'],hashlib.sha256(Path(sec_identity.__file__).read_bytes()).hexdigest())
        self.assertNotIn('/',d['parser_profile'])

    def test_legacy_all_rows_rejection_is_separate_from_reference_admission(self):
        data=payload('AUTH/CLASS')
        with self.assertRaises(sec_identity.SECReferenceSymbolError)as caught:sec_identity.parse(data)
        d=q.failure_result(caught.exception)['diagnostic']['directory_rejection']
        self.assertEqual(d['condition'],'LEGACY_EXCLUSIONS_NOT_ALLOWED');self.assertEqual(d['parser_path'],'legacy_all_rows')
        self.assertEqual(d['requested_relation'],'NOT_REQUESTED')

    def test_null_types_and_sensitive_fields_are_never_dumped(self):
        marker='AUTHORED_PRIVATE_MARKER@example.invalid'
        for value in [marker,{'secret':marker},[marker],64.5]:
            d,output=self.fail_cli(value);self.assertNotIn(marker,output);self.assertLess(len(output),1900)
            self.assertNotIn('cik',json.dumps(d));self.assertNotIn('title',d)

    def test_unknown_exception_attributes_cannot_inject_diagnostic_values(self):
        marker='AUTHORED_PRIVATE_MARKER@example.invalid';error=ValueError('sec_directory_symbol');error._context={'contact':marker}
        result=q.failure_result(error,'identity_resolution')
        self.assertNotIn('directory_rejection',result['diagnostic']);self.assertNotIn(marker,json.dumps(result))

    def test_source_digest_is_validated_before_inclusion(self):
        with self.assertRaises(sec_identity.SECReferenceSymbolError)as caught:sec_identity.parse_reference(payload('BAD_'))
        error=caught.exception;error.attach_source_digest('private-contact@example.invalid')
        self.assertIsNone(error.diagnostic()['source_sha256'])
        error.attach_source_digest('d'*64);self.assertEqual(error.diagnostic()['source_sha256'],'d'*64)

    def test_schema_identity_and_duplicate_checks_remain_fatal(self):
        cases=[({'0':{'ticker':'AAPL','cik_str':True,'title':'Authored'}},'sec_directory_cik'),
               ({'0':{'ticker':'AAPL','cik_str':320193,'title':'Authored','extra':1}},'sec_directory_schema'),
               ({'0':{'ticker':'AAPL','cik_str':320193,'title':'bad\nname'}},'sec_directory_title'),
               ({'0':{'ticker':'AAPL','cik_str':320193,'title':'Authored'},'1':{'ticker':'AAPL','cik_str':42,'title':'Conflict'}},'sec_directory_duplicate_symbol')]
        for data,reason in cases:
            with self.assertRaisesRegex(ValueError,reason):sec_identity.parse_reference(data)


class Atomicity(unittest.IsolatedAsyncioTestCase):
    async def test_error_context_does_not_publish_parsed_prefix_or_destroy_accepted_snapshot(self):
        data={'0':{'ticker':'AAPL','cik_str':320193,'title':'Authored Apple'}};clock=[100.]
        async def fetch(*_):return json.dumps(data).encode()
        w=StockWorkspace(environment=SEC_ENV,fetcher=fetch,clock=lambda:clock[0]);await w.refresh_identities()
        before=(copy.deepcopy(w.issuers),copy.deepcopy(w.issuer_source),w.sec_identity_accepted)
        data['10']={'ticker':None,'cik_str':42,'title':'Authored invalid'};clock[0]=161.
        with self.assertRaises(sec_identity.SECReferenceSymbolError)as caught:await w.refresh_identities(requested_symbol='AAPL')
        self.assertEqual(caught.exception.diagnostic()['condition'],'NON_STRING')
        self.assertEqual((w.issuers,w.issuer_source,w.sec_identity_accepted),before);self.assertFalse(w.lock.locked())

    async def test_invalid_diagnostic_target_cannot_request_or_disclose_configuration(self):
        fetch=AsyncMock();w=StockWorkspace(environment=SEC_ENV,fetcher=fetch)
        with self.assertRaisesRegex(ValueError,'invalid_symbol'):await w.refresh_identities(requested_symbol='contact@example.invalid')
        fetch.assert_not_awaited()


if __name__=='__main__':unittest.main()
