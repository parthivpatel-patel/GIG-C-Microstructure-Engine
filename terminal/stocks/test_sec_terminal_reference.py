"""Authored terminal-marker fixtures matching owner-reported shape,not SEC source rows."""
import copy,hashlib,json,unittest
from unittest.mock import AsyncMock,patch
from . import sec_identity
from .identity import symbol
from .service import StockWorkspace
from .test_workspace import CIK,SEC_ENV,facts
from .test_sec_qualification import ARGS,entrypoint
from . import test_sec_qualification as qualification_fixture


def row(ticker,cik=42):
    return {'ticker':ticker,'cik_str':cik,'title':'Authored reference'}


def directory():
    # The exact live ticker/CIK was not disclosed. All filler/marker rows are authored.
    data={str(i):row(f'S{i:05}',1000000+i)for i in range(10430)}
    data['0']=row('AAPL',320193)
    data['7324']=row('AUTH-')
    return data


class TerminalReference(unittest.TestCase):
    def test_reported_10430_record_shape_resolves_exact_AAPL(self):
        data=directory()
        self.assertEqual(list(data).index('7324')+1,7325)
        self.assertEqual(len(data['7324']['ticker']),5)
        rows,integrity=sec_identity.parse_reference(data,requested_symbol='AAPL')
        self.assertEqual(rows['AAPL']['cik'],CIK)
        self.assertEqual((len(data),len(rows),integrity['excluded_rows']),(10430,10429,1))
        self.assertEqual(integrity['excluded_examples'],[{'record_key':'7324',
            'ticker_sha256':hashlib.sha256(b'AUTH-').hexdigest(),'reason':'unsupported_routing_symbol'}])
        self.assertNotIn('AUTH-',json.dumps(integrity))

    def test_each_existing_separator_can_be_one_terminal_reference_marker(self):
        for ending in '.-/$^':
            with self.subTest(ending=ending):
                ticker='AUTH'+ending
                self.assertIsNone(sec_identity.symbol_condition(ticker))
                data={'0':row('AAPL',320193),'1':row(ticker)}
                rows,integrity=sec_identity.parse_reference(data)
                self.assertEqual(set(rows),{'AAPL'});self.assertEqual(integrity['excluded_rows'],1)
                with self.assertRaisesRegex(ValueError,'invalid_symbol'):symbol(ticker)
                with self.assertRaisesRegex(ValueError,'sec_directory_symbol'):sec_identity.parse(data)

    def test_mixed_exact_formats_preserve_identity_and_full_accounting(self):
        accepted={'AAPL':320193,'BRK-B':42,'BRK.B':43,'AUTH-A':44}
        excluded=['AUTH-', 'AUTH.', 'AUTH/', 'AUTH$', 'AUTH^', 'AUTH/CLASS', 'AUTH^A', 'AUTH$A', '123AUTH', 'auth']
        data={str(i):row(ticker,cik)for i,(ticker,cik)in enumerate(accepted.items())}
        for ticker in excluded:data[str(len(data))]=row(ticker)
        rows,integrity=sec_identity.parse_reference(data)
        self.assertEqual({k:int(v['cik'])for k,v in rows.items()},accepted)
        self.assertEqual(integrity['input_rows'],integrity['accepted_rows']+integrity['excluded_rows'])
        self.assertEqual(integrity['excluded_rows'],len(excluded))
        self.assertEqual(integrity['normalization'],'NONE_EXACT_SOURCE_SYMBOLS')
        self.assertEqual(integrity['coverage'],'ACCEPTED_ROUTABLE_SUBSET')

    def test_terminal_marker_is_never_stripped_or_aliased_to_AAPL(self):
        for ending in '.-/$^':
            data={'0':row('AAPL',320193),'1':row('AAPL'+ending,42)}
            rows,integrity=sec_identity.parse_reference(data)
            self.assertEqual(rows,{'AAPL':{'symbol':'AAPL','company_name':'Authored reference','cik':CIK}})
            self.assertEqual(integrity['excluded_rows'],1)

    def test_only_terminal_references_cannot_claim_supported_identity(self):
        with self.assertRaisesRegex(ValueError,'sec_directory_no_supported_symbols'):
            sec_identity.parse_reference({'0':row('AAPL-')},requested_symbol='AAPL')

    def test_duplicate_terminal_references_remain_fatal_for_same_or_conflicting_CIK(self):
        for ticker in ('AUTH-','AUTH.','AUTH/','AUTH$','AUTH^'):
            for cik in (42,43):
                data={'0':row('AAPL',320193),'1':row(ticker),'2':row(ticker,cik)}
                with self.subTest(ticker=ticker,cik=cik),self.assertRaisesRegex(ValueError,'sec_directory_duplicate_symbol'):
                    sec_identity.parse_reference(data)

    def test_excluded_reference_does_not_hide_later_duplicate_AAPL(self):
        data={'0':row('AAPL',320193),'1':row('AUTH-'),'2':row('AAPL',42)}
        with self.assertRaisesRegex(ValueError,'sec_directory_duplicate_symbol'):sec_identity.parse_reference(data)

    def test_terminal_marker_never_bypasses_row_CIK_title_validation(self):
        for change,reason in [({'cik_str':True},'sec_directory_cik'),({'cik_str':0},'sec_directory_cik'),
                              ({'title':'bad\nname'},'sec_directory_title'),({'extra':1},'sec_directory_schema')]:
            data={'0':row('AAPL',320193),'1':{**row('AUTH-'),**change}}
            with self.assertRaisesRegex(ValueError,reason):sec_identity.parse_reference(data)

    def test_leading_repeated_unsafe_empty_nonstring_values_still_reject(self):
        values=['-AUTH','.AUTH','/AUTH','$AUTH','^AUTH','AUTH--','AUTH..','AUTH/^','AUTH//',
                'AUTH_','AUTH ','AUTH- ',' AAPL','../A','https://x','A?B','A\\B','A\x00B','Aé','',None,True,42]
        for ticker in values:
            with self.subTest(ticker=ticker),self.assertRaisesRegex(ValueError,'sec_directory_symbol'):
                sec_identity.parse_reference({'0':row('AAPL',320193),'1':row(ticker)})

    def test_original_64_character_reference_budget_includes_terminal_marker(self):
        rows,integrity=sec_identity.parse_reference({'0':row('AAPL',320193),'1':row('A'*63+'-')})
        self.assertEqual(set(rows),{'AAPL'});self.assertEqual(integrity['excluded_rows'],1)
        with self.assertRaisesRegex(ValueError,'sec_directory_symbol'):
            sec_identity.parse_reference({'0':row('AAPL',320193),'1':row('A'*64+'-')})

    def test_exclusion_examples_stay_bounded_and_account_for_all_markers(self):
        data={'0':row('AAPL',320193)}
        data.update({str(i+1):row(f'AUTH{i}-')for i in range(40)})
        _,integrity=sec_identity.parse_reference(data)
        self.assertEqual((integrity['accepted_rows'],integrity['excluded_rows']),(1,40))
        self.assertEqual(len(integrity['excluded_examples']),16);self.assertTrue(integrity['examples_truncated'])

    def test_full_CLI_reaches_independent_fact_reconciliation_without_contact_disclosure(self):
        data=directory();digest=hashlib.sha256(json.dumps(data).encode()).hexdigest()
        raw=json.dumps(facts()).encode();client,_=qualification_fixture.SourceBoundary().mock_client(chunks=(raw,))
        with patch.object(StockWorkspace,'fetch',AsyncMock(return_value=(data,digest)))as fetch,patch('httpx.Client',return_value=client),patch('time.sleep')as sleep:
            code,result,output=entrypoint(ARGS)
        self.assertEqual(code,0);self.assertEqual(result['mismatch_count'],0)
        self.assertGreater(result['matched_records'],0);self.assertEqual(result['identity_reference']['cik'],CIK)
        source=result['identity_reference']['source'];self.assertEqual(source['sha256'],digest)
        self.assertEqual(source['integrity']['excluded_rows'],1)
        self.assertIn('independent_reconciliation',result['diagnostics']['completed_stages'])
        self.assertNotIn(SEC_ENV['GIG_SEC_USER_AGENT'],output);self.assertNotIn('AUTH-',output)
        fetch.assert_awaited_once();sleep.assert_called_once_with(1.01)
        self.assertEqual(client.stream.call_args.args,('GET','https://data.sec.gov/api/xbrl/companyfacts/CIK'+CIK+'.json'))

    def test_missing_AAPL_is_not_invented_from_unrelated_terminal_reference(self):
        data={'0':row('AAPL-',42),'1':row('AUTH',43)}
        with patch.object(StockWorkspace,'fetch',AsyncMock(return_value=(data,'a'*64))),patch('httpx.Client')as client:
            code,result,_=entrypoint(ARGS)
        self.assertEqual(code,2);self.assertEqual(result['reason'],'SEC_authoritative_symbol_unavailable')
        client.assert_not_called()


class AtomicPublication(unittest.IsolatedAsyncioTestCase):
    async def test_success_cache_preserves_exact_source_and_never_publishes_marker(self):
        data={'0':row('AAPL',320193),'1':row('AUTH-')};calls=[]
        async def fetch(*args):calls.append(args);return json.dumps(data).encode()
        w=StockWorkspace(environment=SEC_ENV,fetcher=fetch)
        first=await w.refresh_identities(requested_symbol='AAPL');second=await w.refresh_identities(requested_symbol='AAPL')
        self.assertEqual(w.resolve('AAPL')['cik'],CIK);self.assertEqual(len(calls),1)
        self.assertEqual(first['source'],second['source']);self.assertEqual(second['refresh'],'CACHED_ACCEPTED_REFERENCE')
        self.assertEqual(first['source']['sha256'],hashlib.sha256(json.dumps(data).encode()).hexdigest())
        self.assertEqual(first['source']['classification'],'HISTORICAL_SYNTHETIC')
        with self.assertRaises(ValueError):w.resolve('AUTH-')

    async def test_later_failure_preserves_all_accepted_state_after_marker(self):
        data={'0':row('AAPL',320193)};clock=[100.]
        async def fetch(*_):return json.dumps(data).encode()
        w=StockWorkspace(environment=SEC_ENV,fetcher=fetch,clock=lambda:clock[0]);await w.refresh_identities()
        before=(copy.deepcopy(w.issuers),copy.deepcopy(w.issuer_source),w.sec_identity_accepted,w.directory.sec_status)
        data['1']=row('AUTH-');data['2']=row('AAPL',42);clock[0]=161.
        with self.assertRaisesRegex(ValueError,'sec_directory_duplicate_symbol'):await w.refresh_identities()
        self.assertEqual((w.issuers,w.issuer_source,w.sec_identity_accepted,w.directory.sec_status),before)
        self.assertFalse(w.lock.locked())

    async def test_valid_terminal_reference_cannot_hide_curated_CIK_conflict(self):
        async def fetch(*_):return json.dumps({'0':row('AAPL',42),'1':row('AUTH-')}).encode()
        w=StockWorkspace(environment=SEC_ENV,fetcher=fetch)
        with self.assertRaisesRegex(ValueError,'sec_directory_curated_identity_conflict'):await w.refresh_identities()
        self.assertFalse(w.issuers);self.assertIsNone(w.issuer_source);self.assertFalse(w.lock.locked())

    async def test_cached_mapping_cannot_disappear_into_terminal_exclusion(self):
        data={'0':row('AAPL',320193),'1':row('AUTH',42)};clock=[100.]
        async def fetch(*_):return json.dumps(data).encode()
        w=StockWorkspace(environment=SEC_ENV,fetcher=fetch,clock=lambda:clock[0]);await w.refresh_identities()
        w.cache['AUTH']={'sec':{'authored':True}}
        before=(copy.deepcopy(w.issuers),copy.deepcopy(w.issuer_source),w.sec_identity_accepted)
        data['1']['ticker']='AUTH-';clock[0]=161.
        with self.assertRaisesRegex(ValueError,'sec_directory_cached_issuer_change'):await w.refresh_identities()
        self.assertEqual((w.issuers,w.issuer_source,w.sec_identity_accepted),before);self.assertFalse(w.lock.locked())


if __name__=='__main__':unittest.main()
