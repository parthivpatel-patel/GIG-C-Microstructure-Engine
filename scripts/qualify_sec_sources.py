#!/usr/bin/env python3
"""Independent raw-record reconciliation. Default offline;explicit gated fetch only."""
import argparse,datetime,hashlib,http.client,json,os,re,sys,time
from contextlib import contextmanager
from decimal import Decimal
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
REFERENCE_TAGS={'revenue':('RevenueFromContractWithCustomerExcludingAssessedTax','Revenues','SalesRevenueNet'),'net_income':('NetIncomeLoss',),'operating_cash_flow':('NetCashProvidedByUsedInOperatingActivities',),'assets':('Assets',),'liabilities':('Liabilities',),'equity':('StockholdersEquity',),'cash':('CashAndCashEquivalentsAtCarryingValue',),'eps':('EarningsPerShareDiluted',),'gross_profit':('GrossProfit',),'operating_income':('OperatingIncomeLoss',),'assets_current':('AssetsCurrent',),'liabilities_current':('LiabilitiesCurrent',),'short_term_borrowings':('ShortTermBorrowings',),'long_term_debt_current':('LongTermDebtCurrent',),'long_term_debt_noncurrent':('LongTermDebtNoncurrent',),'capex':('PaymentsToAcquirePropertyPlantAndEquipment',)}

REFERENCE_TAGS.update({'cost_of_revenue':('CostOfRevenue','CostOfGoodsAndServicesSold'),
 'cash_investing':('NetCashProvidedByUsedInInvestingActivities',),'cash_financing':('NetCashProvidedByUsedInFinancingActivities',),
 'cash_fx':('EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents',),
 'cash_change':('CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect',),
 'eps_basic':('EarningsPerShareBasic',),'diluted_shares':('WeightedAverageNumberOfDilutedSharesOutstanding',)})

# Exact tokens only. Prefix matching can both hide lower-case validator codes and
# disclose arbitrary exception text that happens to begin with SEC_ or backend_.
ERROR_GROUPS={
 'CONFIGURATION':('sec_disabled_pending_fair_access_review','sec_identifying_user_agent_required','sec_private_configuration_invalid'),
 'INPUT':('invalid_symbol','unsupported_symbol','SEC_invalid_cik'),
 'SOURCE_SCHEMA':('sec_directory_budget','sec_directory_schema','sec_directory_cik','sec_directory_symbol','sec_directory_title',
   'sec_structure','sec_facts','sec_fact_budget','sec_fact_record','sec_numeric','sec_text','sec_date','sec_accession','sec_filing_fiscal_year'),
 'SOURCE_IDENTITY':('sec_directory_duplicate_symbol','sec_directory_curated_identity_conflict','sec_directory_cached_issuer_change','sec_identity','SEC_authoritative_symbol_unavailable'),
 'SOURCE_SEMANTICS':('sec_fact_period','sec_contradictory_fact'),
 'SOURCE_JSON':('source_duplicate_field','source_constant','duplicate_field','invalid_constant','upstream_json_nesting','upstream_expected_json_shape'),
 'RESOURCE_LIMIT':('source_body_budget','SEC_body_budget','upstream_body_budget'),
 'SOURCE_ENCODING':('SEC_encoding','compressed_response_refused'),
 'SOURCE_HEADERS':('SEC_length','upstream_length'),
 'DEADLINE':('SEC_total_deadline',),
 'RATE_LIMIT':('upstream_rate_limit_one_request_per_second','upstream_failure_cooldown','upstream_refresh_busy'),
 'CACHE_COMPARISON':('backend_cache_response','backend_SEC_cache_not_loaded','backend_cache_issuer_mismatch','backend_cache_as_of_mismatch'),
}
ERROR_CODES={code:category for category,codes in ERROR_GROUPS.items() for code in codes}


def failure_result(error,stage='initialization',diagnostics=None):
    """Finite public codes;never serialize arbitrary exceptions,URLs or config values."""
    import httpx
    code='sanitized_source_or_configuration_failure';category='UNCLASSIFIED'
    status=None
    if isinstance(error,ValueError):
        token=str(error)
        if token in ERROR_CODES:code=token;category=ERROR_CODES[token]
        else:
            match=re.fullmatch(r'(?:SEC_HTTP_|upstream_http_)([1-5][0-9]{2})',token)
            if match:code='sec_http_status';category='HTTP_STATUS';status=int(match[1])
    # Subclasses can carry response bodies or identifying strings in their text.
    if isinstance(error,json.JSONDecodeError):code='source_invalid_json';category='SOURCE_JSON'
    elif isinstance(error,UnicodeError):code='source_invalid_utf8';category='SOURCE_ENCODING'
    elif isinstance(error,RecursionError):code='source_json_nesting';category='RESOURCE_LIMIT'
    elif isinstance(error,httpx.ProxyError):code='source_proxy_failure';category='PROXY'
    elif isinstance(error,(TimeoutError,httpx.TimeoutException)):code='source_timeout';category='TIMEOUT'
    elif isinstance(error,httpx.ConnectError):code='source_connect_or_tls_failure';category='CONNECT_OR_TLS'
    elif isinstance(error,httpx.TransportError):code='source_transport_failure';category='TRANSPORT'
    elif isinstance(error,KeyError):code='source_required_field_missing';category='SOURCE_SCHEMA'
    elif isinstance(error,(TypeError,AttributeError)):code='source_unexpected_structure';category='SOURCE_SCHEMA'
    elif isinstance(error,OSError):code='local_io_failure';category='LOCAL_IO'
    if stage=='input_validation' and code=='sec_date':category='INPUT'
    kind=type(error).__name__
    if kind not in {'ValueError','AccessError','JSONDecodeError','UnicodeDecodeError','RecursionError','TimeoutError','ReadTimeout','ConnectTimeout','PoolTimeout','WriteTimeout','ProxyError','ConnectError','RemoteProtocolError','ReadError','WriteError','KeyError','TypeError','AttributeError','OSError','FileNotFoundError','FileExistsError','PermissionError'}:kind='Exception'
    diagnostic={'stage':stage,'category':category,'code':code}
    if status is not None:diagnostic['http_status']=status
    return {'schema':'gig.sec.qualification.failure.v2','status':'BLOCKED_OR_INVALID','error_type':kind,
            'reason':code,'diagnostic':diagnostic,'diagnostics':diagnostics or {},'raw_retained':False,'contact_disclosed':False}


class QualificationFailure(Exception):
    def __init__(self,result):self.result=result;super().__init__('sanitized_SEC_qualification_failure')


@contextmanager
def qualification_step(stage,diagnostics):
    try:yield
    except Exception as error:raise QualificationFailure(failure_result(error,stage,diagnostics)) from None
    else:diagnostics['completed_stages'].append(stage)

def decode(raw):
    if len(raw)>8388608:raise ValueError('source_body_budget')
    def pairs(items):
        d={}
        for k,v in items:
            if k in d:raise ValueError('source_duplicate_field')
            d[k]=v
        return d
    return json.loads(raw,parse_float=Decimal,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('source_constant')))

def reconcile(raw,normalized,as_of):
    # Deliberately does not call production selection,exact() or source-ID helpers.
    source=decode(raw);matched=0;mismatches=[]
    if str(source.get('cik','')).zfill(10)!=normalized.get('issuer_cik'):mismatches.append({'metric':'issuer','reason':'issuer_identity'})
    gaap=source.get('facts',{}).get('us-gaap',{})
    for name,tags in REFERENCE_TAGS.items():
        unit='USD/shares' if name in ('eps','eps_basic') else 'shares' if name=='diluted_shares' else 'USD';groups={}
        for tag in tags:
            for r in gaap.get(tag,{}).get('units',{}).get(unit,[]):
                if r.get('form') not in ('10-K','10-K/A','10-Q','10-Q/A') or r['filed']>as_of:continue
                key=(tag,r.get('start'),r['end'],unit);rank=(r['filed'],r['accn'])
                existing=groups.get(key)
                if existing is None or rank>existing[0]:groups[key]=(rank,[r])
                elif rank==existing[0]:existing[1].append(r)
        keys=sorted(groups,key=lambda k:(k[2],k[1] or '',groups[k][0][0],k[0]),reverse=True)[:256]
        rows=normalized.get('history',{}).get(name)
        if rows is None or len(rows)!=len(keys):mismatches.append({'metric':name,'reason':'selected_record_count'});continue
        actual={(r['concept'],r['start'],r['end'],r['unit']):r for r in rows}
        if len(actual)!=len(rows) or set(actual)!=set(keys):mismatches.append({'metric':name,'reason':'selected_period_identity'});continue
        for key in keys:
            row=actual[key];found=False
            for candidate in groups[key][1]:
                original={'issuer_cik':str(source['cik']).zfill(10),'concept':key[0],'unit':unit,'value':str(candidate['val']),'start':candidate.get('start'),'end':candidate['end'],'filed':candidate['filed'],'accession':candidate['accn'],'form':candidate['form'],'frame':candidate.get('frame'),'filing_fiscal_year':candidate.get('fy'),'filing_fiscal_period':candidate.get('fp'),'period_kind':'duration' if candidate.get('start') else 'instant','duration_days':(datetime.date.fromisoformat(candidate['end'])-datetime.date.fromisoformat(candidate['start'])).days+1 if 'start' in candidate else None}
                identifier=hashlib.sha256(json.dumps(original,sort_keys=True,separators=(',',':')).encode()).hexdigest()
                if all(row.get(k)==v for k,v in original.items()) and row.get('source_fact_id')==identifier:found=True;break
            if found:matched+=1
            else:mismatches.append({'metric':name,'reason':'raw_value_period_context_or_identity_mismatch','source_fact_id':row.get('source_fact_id')})
    return {'schema':'gig.sec.reconciliation.v1','status':'MISMATCH' if mismatches else 'AGREEMENT_WITHIN_SELECTED_RECORD_SCOPE' if matched else 'INCONCLUSIVE_NO_SUPPORTED_RECORDS','matched_records':matched,'mismatch_count':len(mismatches),'mismatches':mismatches[:32],'raw_source_sha256':hashlib.sha256(raw).hexdigest(),'as_of_filing_date':as_of,'scope':'selected raw SEC records/values/units/periods/context/identities only;not full statements,ratios or intraday PIT validation'}

def official_fetch(cik,environment):
    from terminal.stocks.service import StockWorkspace
    import httpx
    from terminal.stocks.qualification import nonretaining_environment
    if type(cik) is not str or not re.fullmatch(r'[0-9]{10}',cik) or int(cik)==0:raise ValueError('SEC_invalid_cik')
    effective=nonretaining_environment(environment)
    headers=StockWorkspace(environment=effective).permission('sec')
    url='https://data.sec.gov/api/xbrl/companyfacts/CIK'+cik+'.json'
    started=time.monotonic()
    with httpx.Client(timeout=8,follow_redirects=False,headers={'Accept-Encoding':'identity'}) as client:
        with client.stream('GET',url,headers=headers) as response:
            if response.status_code!=200:raise ValueError('SEC_HTTP_'+str(response.status_code))
            if response.headers.get('content-encoding','identity').lower() not in ('','identity'):raise ValueError('SEC_encoding')
            length=response.headers.get('content-length')
            if length is not None:
                if not re.fullmatch(r'[0-9]{1,10}',length):raise ValueError('SEC_length')
                if int(length)>8388608:raise ValueError('SEC_body_budget')
            raw=bytearray()
            for chunk in response.iter_raw():
                if time.monotonic()-started>25:raise ValueError('SEC_total_deadline')
                if len(raw)+len(chunk)>8388608:raise ValueError('SEC_body_budget')
                raw.extend(chunk)
    return bytes(raw),url

async def resolve_reference(symbol,workspace):
    """Resolve exact SEC ticker identity,including non-seed companies;never guess a CIK."""
    from terminal.stocks.identity import symbol as validate_symbol
    validate_symbol(symbol)
    await workspace.refresh_identities()
    row=workspace.issuers.get(symbol)
    if row is None:raise ValueError('SEC_authoritative_symbol_unavailable')
    return {**row,'source':workspace.issuer_source}

def main():
    p=argparse.ArgumentParser();p.add_argument('--symbol',default='AAPL');p.add_argument('--as-of',required=True);p.add_argument('--company-facts');p.add_argument('--fetch',action='store_true');p.add_argument('--resolve-identity',action='store_true');p.add_argument('--compare-cache',action='store_true');p.add_argument('--output');a=p.parse_args()
    if bool(a.company_facts)==bool(a.fetch):p.error('choose exactly one authorized JSON file or explicit --fetch')
    from terminal.stocks.identity import instrument
    from terminal.stocks.sec import facts,date
    diagnostics={'completed_stages':[]}
    with qualification_step('input_validation',diagnostics):
        from terminal.stocks.identity import symbol
        symbol(a.symbol)
        try:date(a.as_of)
        except ValueError:raise ValueError('sec_date') from None
    if a.resolve_identity:
        if not a.fetch:p.error('--resolve-identity requires explicit --fetch and existing SEC authorization')
    if a.fetch:
        from terminal.stocks.sec_config import resolve,readiness
        from terminal.stocks.qualification import nonretaining_environment
        from terminal.stocks.service import StockWorkspace
        with qualification_step('sec_configuration',diagnostics):
            effective,metadata=resolve(os.environ)
            state=readiness(effective)
            diagnostics['configuration']={'ready':state['ready'],'configuration_source':metadata['source'],
                'missing_configuration':state['missing_configuration'],'contact_disclosed':False}
            if metadata['error']:raise ValueError('sec_private_configuration_invalid')
            # Permission remains SEC-specific;Alpaca enablement is never required.
            workspace=StockWorkspace(environment=nonretaining_environment(effective))
            workspace.permission('sec')
    if a.resolve_identity:
        import asyncio
        async def select_identity():
            try:return await resolve_reference(a.symbol,workspace)
            finally:await workspace.close()
        with qualification_step('identity_resolution',diagnostics):
            identity=asyncio.run(select_identity());cik=identity['cik']
        # Registry then companyfacts share a conservative SEC request cadence.
        time.sleep(1.01)
    else:
        with qualification_step('seed_identity',diagnostics):
            identity=instrument(a.symbol);cik=identity['cik']
    if a.fetch:
        with qualification_step('companyfacts_fetch',diagnostics):raw,url=official_fetch(cik,effective)
    else:
        with qualification_step('local_source_read',diagnostics):
            with Path(a.company_facts).open('rb') as f:raw=f.read(8388609)
        url=None
    diagnostics['companyfacts_receipt']={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
    with qualification_step('companyfacts_decode',diagnostics):parsed=decode(raw)
    with qualification_step('companyfacts_validation',diagnostics):normalized=facts(parsed,cik,a.as_of)
    if a.compare_cache:
        # Fixed local owner server,not arbitrary URLs or forwarded authentication.
        with qualification_step('cache_comparison',diagnostics):
            connection=http.client.HTTPConnection('127.0.0.1',8787,timeout=5)
            try:
                connection.request('GET','/api/v1/stocks/company?symbol='+a.symbol)
                response=connection.getresponse();data=response.read(2097153)
            finally:connection.close()
            if response.status!=200 or len(data)>2097152:raise ValueError('backend_cache_response')
            normalized=json.loads(data)['fundamentals'].get('financials')
            if normalized is None:raise ValueError('backend_SEC_cache_not_loaded')
            if normalized.get('issuer_cik')!=cik:raise ValueError('backend_cache_issuer_mismatch')
            if normalized['as_of_filing_date']!=a.as_of:raise ValueError('backend_cache_as_of_mismatch')
    with qualification_step('independent_reconciliation',diagnostics):result=reconcile(raw,normalized,a.as_of)
    result.update(source_url=url,source_authority='fixed_official_TLS_fetch' if a.fetch else 'owner_supplied_file_origin_not_independently_authenticated',identity_reference=identity,backend_cache_compared=a.compare_cache,raw_retained=False,contact_disclosed=False,diagnostics=diagnostics)
    encoded=json.dumps(result,indent=2)+'\n'
    if a.output:
        with qualification_step('report_write',diagnostics):
            with open(a.output,'x',encoding='utf-8') as f:f.write(encoded)
    print(encoded,end='');return 0 if result['status']=='AGREEMENT_WITHIN_SELECTED_RECORD_SCOPE' else 1

if __name__=='__main__':
    try:raise SystemExit(main())
    except QualificationFailure as error:print(json.dumps(error.result));raise SystemExit(2)
    except Exception as error:print(json.dumps(failure_result(error)));raise SystemExit(2)
