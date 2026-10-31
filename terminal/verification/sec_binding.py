"""Bind existing selected-scope SEC report bytes;no fetch orconfiguration access."""
import datetime
import hashlib
import re
from .artifacts import EvidenceError,decode,digest,read_bytes

SCOPE='selected raw SEC records/values/units/periods/context/identities only;not full statements,ratios or intraday PIT validation'
DECLARATION='gig.sec.binding.declaration.v1'


def date(value):
    try:
        result=datetime.date.fromisoformat(value)
        if result.isoformat()!=value:raise ValueError()
        return result
    except (ValueError,TypeError):raise EvidenceError('invalid_date')from None


def instant(value):
    try:
        if type(value)is not str or not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]{1,6})?(?:Z|[+-][0-9]{2}:[0-9]{2})',value):raise ValueError()
        t=datetime.datetime.fromisoformat(value.replace('Z','+00:00'))
        if t.tzinfo is None or 'T'not in value or abs(t.utcoffset().total_seconds())>14*3600:raise ValueError()
        return t.astimezone(datetime.timezone.utc)
    except (ValueError,TypeError,OverflowError):raise EvidenceError('invalid_timestamp')from None


def count(value):
    if type(value)is not int or not 0<=value<=100000000:raise EvidenceError('invalid_count')
    return value


def bind(report_path,expected_report_sha256,*,declaration_path=None,expected_source_sha=None,now=None):
    expected_report_sha256=digest(expected_report_sha256)
    if expected_source_sha is not None:digest(expected_source_sha,40)
    raw=read_bytes(report_path);report_hash=hashlib.sha256(raw).hexdigest()
    if report_hash!=expected_report_sha256:raise EvidenceError('report_hash_mismatch')
    report=decode(raw)
    if report.get('schema')!='gig.sec.reconciliation.v1':raise EvidenceError('unsupported_sec_report_schema')
    matched=count(report.get('matched_records'));mismatches=count(report.get('mismatch_count'))
    status='MISMATCH'if mismatches else 'AGREEMENT_WITHIN_SELECTED_RECORD_SCOPE'if matched else 'INCONCLUSIVE_NO_SUPPORTED_RECORDS'
    if report.get('status')!=status:raise EvidenceError('contradictory_result_counts')
    detail=report.get('mismatches')
    if type(detail)is not list or len(detail)!=min(32,mismatches):raise EvidenceError('contradictory_mismatch_details')
    if report.get('scope')!=SCOPE:raise EvidenceError('unsupported_report_scope')
    as_of=date(report.get('as_of_filing_date'))
    source_hash=digest(report.get('raw_source_sha256'))
    if report.get('raw_retained')is not False or report.get('contact_disclosed')is not False:
        raise EvidenceError('unsafe_report_privacy_state')
    diagnostics=report.get('diagnostics',{})
    if type(diagnostics)is not dict:raise EvidenceError('invalid_report_diagnostics')
    receipt=diagnostics.get('companyfacts_receipt')
    if receipt is not None:
        if type(receipt)is not dict or digest(receipt.get('sha256'))!=source_hash:raise EvidenceError('contradictory_source_digest')
        if not 1<=count(receipt.get('bytes'))<=8388608:raise EvidenceError('invalid_source_byte_count')
    identity=report.get('identity_reference',{})
    if type(identity)is not dict:raise EvidenceError('invalid_identity_reference')
    symbol=identity.get('symbol');cik=identity.get('cik')
    if type(symbol)is not str or not re.fullmatch(r'[A-Z][A-Z0-9.-]{0,15}',symbol):raise EvidenceError('invalid_report_symbol')
    if type(cik)is not str or not re.fullmatch(r'[0-9]{10}',cik)or int(cik)==0:raise EvidenceError('invalid_report_cik')
    authority=report.get('source_authority')
    if authority not in ('fixed_official_TLS_fetch','owner_supplied_file_origin_not_independently_authenticated'):
        raise EvidenceError('unsupported_report_authority')
    expected_url='https://data.sec.gov/api/xbrl/companyfacts/CIK'+cik+'.json'
    if authority=='fixed_official_TLS_fetch'and report.get('source_url')!=expected_url:raise EvidenceError('unexpected_official_source_url')
    directory=identity.get('source');accepted=None;directory_hash=None;received=None;classification=None
    if directory is not None:
        if type(directory)is not dict:raise EvidenceError('invalid_directory_receipt')
        directory_hash=digest(directory.get('sha256'));received=instant(directory.get('received_at'))
        classification=directory.get('classification')
        if classification not in ('HISTORICAL_SYNTHETIC','OBSERVED_OFFICIAL_RESPONSE'):
            raise EvidenceError('unsupported_directory_classification')
        integrity=directory.get('integrity')
        if type(integrity)is not dict:raise EvidenceError('missing_directory_integrity')
        accepted=count(integrity.get('accepted_rows'));inputs=count(integrity.get('input_rows'));excluded=count(integrity.get('excluded_rows'))
        if accepted+excluded!=inputs:raise EvidenceError('contradictory_directory_counts')
    missing=[];decl=None;qualified=None;source_sha=report.get('tested_source_sha')
    if receipt is None:missing.append('source_byte_count_receipt')
    if directory is None:missing.append('source_directory_count_receipt')
    if source_sha is not None:digest(source_sha,40)
    if declaration_path is not None:
        decl=decode(read_bytes(declaration_path,16384))
        required={'schema','report_sha256','tested_source_sha','qualified_at','as_of_filing_date','matched_records','mismatch_count','scope','accepted_identities','attestation'}
        if set(decl)!=required or decl['schema']!=DECLARATION:raise EvidenceError('unsupported_binding_declaration')
        if decl['attestation']!='OWNER_DECLARED_NOT_INDEPENDENTLY_VERIFIED':raise EvidenceError('unsupported_attestation_claim')
        if digest(decl['report_sha256'])!=report_hash:raise EvidenceError('declaration_report_hash_mismatch')
        sha=digest(decl['tested_source_sha'],40)
        if source_sha is not None and source_sha!=sha:raise EvidenceError('contradictory_source_sha')
        source_sha=sha;qualified=instant(decl['qualified_at'])
        now=datetime.datetime.now(datetime.timezone.utc)if now is None else now
        if qualified.date()<as_of or qualified>now+datetime.timedelta(minutes=5):raise EvidenceError('inconsistent_qualification_date')
        if received is not None and received>qualified:raise EvidenceError('source_received_after_qualification')
        if date(decl['as_of_filing_date'])!=as_of or decl['scope']!=SCOPE:raise EvidenceError('declaration_scope_or_date_mismatch')
        if count(decl['matched_records'])!=matched or count(decl['mismatch_count'])!=mismatches:raise EvidenceError('declaration_count_mismatch')
        if decl['accepted_identities']is not None:
            declared=count(decl['accepted_identities'])
            if accepted is None:pass # Missing receipt was recorded above;never infer from declaration.
            elif declared!=accepted:raise EvidenceError('declaration_directory_count_mismatch')
    else:missing+=['owner_declaration','qualified_at']
    if source_sha is None:missing.append('tested_source_sha')
    if expected_source_sha is not None and source_sha is not None and source_sha!=expected_source_sha:raise EvidenceError('expected_source_sha_mismatch')
    return {'schema':'gig.sec.evidence.binding.v1','status':'INCOMPLETE_METADATA'if missing else 'BOUND_OWNER_DECLARATION',
            'report_sha256':report_hash,'report_bytes':len(raw),'raw_source_sha256':source_hash,
            'reported_source_authority':authority,'tested_source_sha':source_sha,
            'source_sha_authority':'EXPLICIT_OWNER_DECLARATION'if decl else 'REPORT_FIELD_UNATTESTED'if source_sha else 'UNAVAILABLE',
            'qualified_at':qualified.isoformat()if qualified else None,'as_of_filing_date':as_of.isoformat(),
            'matched_records':matched,'mismatch_count':mismatches,'reported_result':status,'scope':SCOPE,
            'identity_symbol':symbol,'identity_cik':cik,'accepted_identities':accepted,'directory_sha256':directory_hash,
            'directory_classification':classification,
            'missing_metadata':missing,'provider_requests':0,'independent_provider_verification':False,
            'interpretation':'Byte/hash/count/date binding only;owner declaration is not independently authenticated execution,complete financial coverage ornew SEC reconciliation',
            'private_contact_disclosed':False,'raw_records_included':False}
