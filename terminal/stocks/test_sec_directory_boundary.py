"""Authored SEC-shaped registry boundaries;not captured official source data."""
import copy,hashlib,json,unittest
from .service import StockWorkspace
from .test_workspace import SEC_ENV,CIK
from . import sec_identity


def fixture():
    return {'0':{'ticker':'AAPL','cik_str':320193,'title':'Authored Apple'},
            '1':{'ticker':'APLD','cik_str':42,'title':'Fictional CIK42'},
            '2':{'ticker':'CRWV','cik_str':43,'title':'Fictional CIK43'}}


class RegistryScope(unittest.IsolatedAsyncioTestCase):
    def workspace(self,payload):
        async def fetch(*_):return json.dumps(payload).encode()
        return StockWorkspace(environment=SEC_ENV,fetcher=fetch)

    async def test_non_routable_reference_entry_cannot_poison_AAPL_identity(self):
        data=fixture();data['3']={'ticker':'AUTH-WARRANT-A','cik_str':44,'title':'Authored non-routable reference'}
        w=self.workspace(data);r=await w.refresh_identities()
        self.assertEqual(list(w.issuers),['AAPL','APLD','CRWV']);self.assertEqual(w.resolve('AAPL')['cik'],CIK)
        integrity=r['source']['integrity'];self.assertEqual((integrity['input_rows'],integrity['accepted_rows'],integrity['excluded_rows']),(4,3,1))
        self.assertEqual(integrity['excluded_examples'][0]['ticker_sha256'],hashlib.sha256(b'AUTH-WARRANT-A').hexdigest())
        self.assertNotIn('AUTH-WARRANT-A',json.dumps(r));self.assertEqual(r['source']['classification'],'HISTORICAL_SYNTHETIC')

    async def test_malformed_reference_still_rejects_atomically(self):
        for ticker in ('../evil','A B','A\nB','https://evil.invalid','<script>','A..B','',42):
            data=fixture();data['3']={'ticker':ticker,'cik_str':44,'title':'Authored invalid'}
            w=self.workspace(data)
            with self.assertRaisesRegex(ValueError,'sec_directory_symbol'):await w.refresh_identities()
            self.assertFalse(w.issuers);self.assertIsNone(w.issuer_source)

    async def test_cached_mapping_cannot_disappear_into_exclusion(self):
        data=fixture();w=self.workspace(data);await w.refresh_identities();w.cache['APLD']={'sec':{'authored':True}}
        previous=copy.deepcopy(w.issuers);source=copy.deepcopy(w.issuer_source);w.clock=lambda:100000000.
        data['1']['ticker']='APLD/CLASS'
        with self.assertRaisesRegex(ValueError,'sec_directory_cached_issuer_change'):await w.refresh_identities()
        self.assertEqual(w.issuers,previous);self.assertEqual(w.issuer_source,source)

    async def test_refresh_cache_preserves_original_integrity_without_refetch(self):
        data=fixture();w=self.workspace(data)
        first=await w.refresh_identities();second=await w.refresh_identities()
        self.assertEqual(first['source'],second['source']);self.assertEqual(second['refresh'],'CACHED_ACCEPTED_REFERENCE')
        self.assertEqual(second['source']['integrity']['accepted_rows'],3)

    async def test_reference_diagnostics_do_not_exhaust_browser_stream_budget(self):
        from .test_final import client,quote,packet
        from terminal.server.market_events import MarketEvents
        data={str(i):{'ticker':f'NEW{i}','cik_str':42+i,'title':'Authored registry issuer'}for i in range(4)}
        for i in range(40):data[str(i+4)]={'ticker':f'AUTH/{i}','cik_str':100+i,'title':'Authored unsupported'}
        w=self.workspace(data);await w.refresh_identities();c=client();c.workspace.issuers=w.issuers;c.workspace.issuer_source=w.issuer_source;c.symbols=tuple(w.issuers);c.phase='SUBSCRIBED'
        for i in range(256):
            row=quote();row['S']=f'NEW{i%4}';row['bs']=i;c.process(packet(row))
        self.assertEqual(len(c.history),256)
        generator=MarketEvents(c).frames()
        try:frame=await anext(generator)
        finally:await generator.aclose()
        self.assertTrue(frame.startswith('event: state\n'),frame[:100]);self.assertLess(len(frame.encode()),1024*1024)
        event_source=c.history[0]['instrument_metadata']['identity_source']
        self.assertEqual(event_source['sha256'],w.issuer_source['sha256'])
        self.assertEqual(event_source['integrity']['excluded_rows'],40)
        self.assertNotIn('excluded_examples',event_source['integrity'])
        self.assertEqual(len(w.issuer_source['integrity']['excluded_examples']),16)


class ReferenceParser(unittest.TestCase):
    def test_legacy_strict_parser_does_not_silently_drop_reference_entries(self):
        data=fixture();data['3']={'ticker':'AUTH/CLASS','cik_str':44,'title':'Authored reference'}
        with self.assertRaisesRegex(ValueError,'sec_directory_symbol'):sec_identity.parse(data)

    def test_exact_punctuation_is_preserved_without_cross_provider_aliases(self):
        data=fixture()
        for i,ticker in enumerate(('BRK-B','BRK.B','AUTH-A','AUTH/B','AUTH^A','AUTH$A','123AUTH','auth'),3):
            data[str(i)]={'ticker':ticker,'cik_str':44+i,'title':'Authored reference shape'}
        rows,integrity=sec_identity.parse_reference(data)
        self.assertEqual(set(rows),{'AAPL','APLD','CRWV','BRK-B','BRK.B','AUTH-A'})
        self.assertEqual(integrity['excluded_rows'],5);self.assertEqual(integrity['normalization'],'NONE_EXACT_SOURCE_SYMBOLS')
        self.assertEqual(integrity['coverage'],'ACCEPTED_ROUTABLE_SUBSET')

    def test_duplicate_reference_including_excluded_symbol_is_never_silently_merged(self):
        for duplicate in ('AAPL','AUTH/CLASS'):
            data=fixture();data['3']={'ticker':duplicate,'cik_str':44,'title':'Authored first'};data['4']={'ticker':duplicate,'cik_str':45,'title':'Authored second'}
            with self.assertRaisesRegex(ValueError,'sec_directory_duplicate_symbol'):sec_identity.parse_reference(data)

    def test_exclusion_does_not_bypass_CIK_title_or_row_validation(self):
        for change in ({'cik_str':True},{'cik_str':0},{'title':'unsafe\ntext'},{'extra':'field'}):
            data=fixture();data['3']={'ticker':'AUTH/CLASS','cik_str':44,'title':'Authored reference',**change}
            with self.assertRaises(ValueError):sec_identity.parse_reference(data)

    def test_exclusion_examples_are_bounded_and_accounted(self):
        data=fixture()
        for i in range(40):data[str(i+3)]={'ticker':f'AUTH/{i}','cik_str':100+i,'title':'Authored unsupported reference'}
        rows,integrity=sec_identity.parse_reference(data)
        self.assertEqual(len(rows),3);self.assertEqual(integrity['excluded_rows'],40)
        self.assertEqual(len(integrity['excluded_examples']),16);self.assertTrue(integrity['examples_truncated'])
        self.assertEqual(integrity['input_rows'],integrity['accepted_rows']+integrity['excluded_rows'])

    def test_no_routable_reference_cannot_claim_successful_discovery(self):
        with self.assertRaisesRegex(ValueError,'sec_directory_no_supported_symbols'):
            sec_identity.parse_reference({'0':{'ticker':'AUTH/CLASS','cik_str':44,'title':'Authored only'}})

    def test_reference_and_symbol_lengths_remain_bounded(self):
        for symbol in ('A'*65,'A\x7fB','A\x00B'):
            data=fixture();data['3']={'ticker':symbol,'cik_str':44,'title':'Authored reference'}
            with self.assertRaisesRegex(ValueError,'sec_directory_symbol'):sec_identity.parse_reference(data)


class QualificationDiagnostics(unittest.TestCase):
    def test_consolidated_qualification_preserves_safe_SEC_code_and_stage(self):
        from .qualification import stage_error
        result=stage_error(ValueError('sec_directory_symbol'),stage='sec_identity')
        self.assertEqual(result['reason'],'sec_directory_symbol')
        self.assertEqual(result['diagnostic']['stage'],'sec_identity')
        self.assertNotIn('authored_secret',json.dumps(stage_error(ValueError('SEC_authored_secret'),stage='sec_identity')))


class MessagePackResources(unittest.TestCase):
    def test_rejected_integer_keys_do_not_retain_decoded_values(self):
        import gc,tracemalloc
        from .live import unpack
        # Independently authored bytes:array1,map1,integer key42,bin16 value16000.
        raw=b'\x91\x81\x2a\xc5\x3e\x80'+b'x'*16000
        for _ in range(20):
            with self.assertRaisesRegex(ValueError,'invalid_messagepack'):unpack(raw)
        started=not tracemalloc.is_tracing()
        if started:tracemalloc.start()
        try:
            gc.collect();baseline=tracemalloc.get_traced_memory()[0]
            control=[bytearray(16000)for _ in range(8)]
            self.assertGreater(tracemalloc.get_traced_memory()[0]-baseline,128000)
            del control;gc.collect();baseline=tracemalloc.get_traced_memory()[0]
            for _ in range(256):
                with self.assertRaisesRegex(ValueError,'invalid_messagepack'):unpack(raw)
            gc.collect();retained=tracemalloc.get_traced_memory()[0]-baseline
            self.assertLess(retained,4*len(raw),'malformed frames must not cause linear retained memory growth')
        finally:
            if started:tracemalloc.stop()

    def test_unsafe_parser_version_is_rejected_before_decoding(self):
        from unittest.mock import patch
        from .live import unpack
        from .test_final import client
        with patch('msgpack.version',(1,1,2)),patch('msgpack.unpackb')as decoder:
            with self.assertRaisesRegex(ValueError,'msgpack_security_patch_required'):unpack(b'\x91\x80')
            decoder.assert_not_called()
            stream=client()
            with patch.object(stream.workspace,'permission')as permission:
                with self.assertRaisesRegex(ValueError,'msgpack_security_patch_required'):stream.require()
                permission.assert_not_called()


if __name__=='__main__':unittest.main()
