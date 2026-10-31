"""Authored metadata fixtures,not owner reports ornew SEC reconciliation."""
import copy,datetime,hashlib,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
from terminal.verification.artifacts import EvidenceError,decode,read_bytes,write_private
from terminal.verification.sec_binding import SCOPE,bind

NOW=datetime.datetime(2026,10,31,12,tzinfo=datetime.timezone.utc)
SHA='1'*40


def report():
    return {'schema':'gig.sec.reconciliation.v1','status':'AGREEMENT_WITHIN_SELECTED_RECORD_SCOPE',
            'matched_records':1772,'mismatch_count':0,'mismatches':[],'scope':SCOPE,
            'raw_source_sha256':'a'*64,'as_of_filing_date':'2026-10-28',
            'raw_retained':False,'contact_disclosed':False,
            'source_authority':'fixed_official_TLS_fetch',
            'source_url':'https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json',
            'diagnostics':{'companyfacts_receipt':{'bytes':1000,'sha256':'a'*64}},
            'identity_reference':{'symbol':'AAPL','cik':'0000320193','source':{
                'sha256':'b'*64,'received_at':'2026-10-30T10:00:00Z',
                'classification':'HISTORICAL_SYNTHETIC',
                'integrity':{'input_rows':10430,'accepted_rows':10429,'excluded_rows':1}}}}


def declaration(digest):
    return {'schema':'gig.sec.binding.declaration.v1','report_sha256':digest,'tested_source_sha':SHA,
            'qualified_at':'2026-10-30T11:00:00Z','as_of_filing_date':'2026-10-28',
            'matched_records':1772,'mismatch_count':0,'scope':SCOPE,'accepted_identities':10429,
            'attestation':'OWNER_DECLARED_NOT_INDEPENDENTLY_VERIFIED'}


class Binding(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.path=self.root/'report.json';self.decl=self.root/'declaration.json'

    def write(self,r=None,d=None):
        raw=json.dumps(report()if r is None else r).encode();self.path.write_bytes(raw)
        digest=hashlib.sha256(raw).hexdigest();self.decl.write_text(json.dumps(declaration(digest)if d is None else d));return digest

    def run_binding(self,digest):return bind(self.path,digest,declaration_path=self.decl,expected_source_sha=SHA,now=NOW)

    def test_complete_binding_is_owner_declaration_only(self):
        digest=self.write();out=self.run_binding(digest)
        self.assertEqual(out['status'],'BOUND_OWNER_DECLARATION')
        self.assertEqual(out['accepted_identities'],10429);self.assertEqual(out['matched_records'],1772)
        self.assertFalse(out['independent_provider_verification']);self.assertEqual(out['provider_requests'],0)
        self.assertEqual(out['directory_classification'],'HISTORICAL_SYNTHETIC')
        self.assertEqual(out['identity_symbol'],'AAPL') # One report cannot certifyAPLD/CRWV too.

    def test_missing_declaration_preserves_missing_provenance(self):
        digest=self.write();out=bind(self.path,digest)
        self.assertEqual(out['status'],'INCOMPLETE_METADATA');self.assertIsNone(out['tested_source_sha'])
        self.assertIsNone(out['qualified_at']);self.assertIn('owner_declaration',out['missing_metadata'])

    def test_expected_bytes_and_report_tampering_reject(self):
        digest=self.write();self.path.write_bytes(self.path.read_bytes()+b' ')
        with self.assertRaisesRegex(EvidenceError,'report_hash_mismatch'):self.run_binding(digest)

    def test_different_source_and_declaration_digests_reject(self):
        for field,value,code in [('raw_source_sha256','c'*64,'contradictory_source_digest'),
                                 ('tested_source_sha','2'*40,'contradictory_source_sha')]:
            r=report();r[field]=value;digest=self.write(r)
            with self.assertRaisesRegex(EvidenceError,code):self.run_binding(digest)
        digest=self.write()
        with self.assertRaisesRegex(EvidenceError,'expected_source_sha_mismatch'):bind(self.path,digest,declaration_path=self.decl,expected_source_sha='3'*40,now=NOW)

    def test_invalid_schema_scope_and_privacy_claims(self):
        for field,value in [('schema','other'),('scope','complete historical statements'),('raw_retained',True),('contact_disclosed',True),('source_url','https://attacker.invalid/data')]:
            r=report();r[field]=value;digest=self.write(r)
            with self.assertRaises(EvidenceError):self.run_binding(digest)

    def test_bool_negative_and_contradictory_counts(self):
        for field,value in [('matched_records',True),('matched_records',-1),('mismatch_count',1),('mismatches',[{}])]:
            r=report();r[field]=value;digest=self.write(r)
            with self.assertRaises(EvidenceError):self.run_binding(digest)

    def test_declaration_counts_dates_and_scope_must_match(self):
        digest=self.write()
        for field,value in [('matched_records',1773),('mismatch_count',True),('accepted_identities',10430),
                            ('scope','full market'),('as_of_filing_date','2026-10-27'),
                            ('tested_source_sha','bad'),('report_sha256','c'*64),('attestation','INDEPENDENT_PROVIDER_PASS')]:
            d=declaration(digest);d[field]=value;self.decl.write_text(json.dumps(d))
            with self.assertRaises(EvidenceError):self.run_binding(digest)

    def test_date_cutoffs_offset_and_precision_are_not_invented(self):
        digest=self.write()
        for t in ('2026-10-30','2026-10-30T11:00:00','2026-10-30T11:00:00.123456789Z',
                  '2026-10-28T00:00:00Z','2027-01-01T00:00:00Z','2026-10-30T10:00:00+15:00'):
            d=declaration(digest);d['qualified_at']=t;self.decl.write_text(json.dumps(d))
            with self.assertRaises(EvidenceError):self.run_binding(digest)
        d=declaration(digest);d['qualified_at']='2026-10-30T12:00:00+01:00';self.decl.write_text(json.dumps(d))
        self.assertEqual(self.run_binding(digest)['qualified_at'],'2026-10-30T11:00:00+00:00')

    def test_unknown_sensitive_fields_are_never_serialized(self):
        r=report();r['arbitrary_contact']='PRIVATE_CONTACT_SENTINEL';r['diagnostics']['secret']='DO_NOT_ECHO'
        out=json.dumps(self.run_binding(self.write(r)))
        self.assertNotIn('PRIVATE_CONTACT_SENTINEL',out);self.assertNotIn('DO_NOT_ECHO',out)

    def test_directory_count_unavailable_is_not_owner_count_confirmation(self):
        r=report();r['identity_reference'].pop('source');out=self.run_binding(self.write(r))
        self.assertEqual(out['status'],'INCOMPLETE_METADATA');self.assertIsNone(out['accepted_identities'])
        self.assertIn('source_directory_count_receipt',out['missing_metadata'])

    def test_directory_accounting_and_source_receipt_bounds(self):
        for change in ('count','bytes','digest'):
            r=report()
            if change=='count':r['identity_reference']['source']['integrity']['excluded_rows']=2
            elif change=='bytes':r['diagnostics']['companyfacts_receipt']['bytes']=8388609
            else:r['identity_reference']['source']['sha256']='bad'
            with self.assertRaises(EvidenceError):self.run_binding(self.write(r))

    def test_mismatch_and_empty_results_never_become_agreement(self):
        r=report();r.update(matched_records=0,status='INCONCLUSIVE_NO_SUPPORTED_RECORDS')
        digest=self.write(r);d=declaration(digest);d['matched_records']=0;self.decl.write_text(json.dumps(d))
        self.assertEqual(self.run_binding(digest)['reported_result'],'INCONCLUSIVE_NO_SUPPORTED_RECORDS')
        r.update(mismatch_count=1,status='MISMATCH',mismatches=[{'reason':'AUTHORED'}]);digest=self.write(r)
        d=declaration(digest);d.update(matched_records=0,mismatch_count=1);self.decl.write_text(json.dumps(d))
        self.assertEqual(self.run_binding(digest)['reported_result'],'MISMATCH')

    def test_cli_exclusive_private_output_and_no_secret_echo(self):
        digest=self.write();out=self.root/'binding.json'
        cmd=[sys.executable,'scripts/bind_sec_evidence.py','--report',str(self.path),'--expected-report-sha256',digest,
             '--declaration',str(self.decl),'--expected-source-sha',SHA,'--output',str(out)]
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=10)
        self.assertEqual(r.returncode,0,r.stdout);self.assertEqual(out.stat().st_mode&0o777,0o600)
        before=out.read_bytes();r=subprocess.run(cmd,capture_output=True,text=True,timeout=10)
        self.assertEqual(r.returncode,1);self.assertIn('output_exists',r.stdout);self.assertEqual(out.read_bytes(),before)


class ArtifactBoundaries(unittest.TestCase):
    def test_duplicate_nonfinite_nesting_and_encoding_reject(self):
        for raw in (b'{"x":1,"x":2}',b'{"x":NaN}',b'{"x":1e999}',b'\xff',b'[]',b'{"x":'+b'['*25+b'0'+b']'*25+b'}'):
            with self.assertRaises(EvidenceError):decode(raw)

    def test_symlink_fifo_and_oversize_reads_refuse(self):
        with tempfile.TemporaryDirectory()as d:
            p=Path(d)/'data';p.write_bytes(b'x'*20);link=Path(d)/'link';link.symlink_to(p)
            for file,limit in ((link,100),(p,10)):
                with self.assertRaises(EvidenceError):read_bytes(file,limit)
            fifo=Path(d)/'fifo';os.mkfifo(fifo)
            with self.assertRaisesRegex(EvidenceError,'artifact_not_regular'):read_bytes(fifo)

    def test_private_write_never_overwrites_or_follows_links(self):
        with tempfile.TemporaryDirectory()as d:
            p=Path(d)/'result';write_private(p,{'safe':True});before=p.read_bytes()
            with self.assertRaisesRegex(EvidenceError,'output_exists'):write_private(p,{})
            self.assertEqual(p.read_bytes(),before)
            link=Path(d)/'link';link.symlink_to(p)
            with self.assertRaisesRegex(EvidenceError,'output_symlink'):write_private(link,{})
