#!/usr/bin/env python3
"""Independent raw-record reconciliation. Default offline;explicit gated fetch only."""
import argparse,datetime,hashlib,http.client,json,os,sys,time
from decimal import Decimal
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
REFERENCE_TAGS={'revenue':('RevenueFromContractWithCustomerExcludingAssessedTax','Revenues','SalesRevenueNet'),'net_income':('NetIncomeLoss',),'operating_cash_flow':('NetCashProvidedByUsedInOperatingActivities',),'assets':('Assets',),'liabilities':('Liabilities',),'equity':('StockholdersEquity',),'cash':('CashAndCashEquivalentsAtCarryingValue',),'eps':('EarningsPerShareDiluted',),'gross_profit':('GrossProfit',),'operating_income':('OperatingIncomeLoss',),'assets_current':('AssetsCurrent',),'liabilities_current':('LiabilitiesCurrent',),'short_term_borrowings':('ShortTermBorrowings',),'long_term_debt_current':('LongTermDebtCurrent',),'long_term_debt_noncurrent':('LongTermDebtNoncurrent',),'capex':('PaymentsToAcquirePropertyPlantAndEquipment',)}

REFERENCE_TAGS.update({'cost_of_revenue':('CostOfRevenue','CostOfGoodsAndServicesSold'),
 'cash_investing':('NetCashProvidedByUsedInInvestingActivities',),'cash_financing':('NetCashProvidedByUsedInFinancingActivities',),
 'cash_fx':('EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents',),
 'cash_change':('CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect',),
 'eps_basic':('EarningsPerShareBasic',),'diluted_shares':('WeightedAverageNumberOfDilutedSharesOutstanding',)})

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
    from terminal.stocks.sec_config import resolve
    effective,_=resolve(environment)
    headers=StockWorkspace(environment=effective).permission('sec')
    url='https://data.sec.gov/api/xbrl/companyfacts/CIK'+cik+'.json'
    with httpx.Client(timeout=8,follow_redirects=False,headers={'Accept-Encoding':'identity'}) as client:
        with client.stream('GET',url,headers=headers) as response:
            if response.status_code!=200:raise ValueError('SEC_HTTP_'+str(response.status_code))
            if response.headers.get('content-encoding','identity').lower() not in ('','identity'):raise ValueError('SEC_encoding')
            raw=bytearray()
            for chunk in response.iter_raw():
                if len(raw)+len(chunk)>8388608:raise ValueError('SEC_body_budget')
                raw.extend(chunk)
    return bytes(raw),url

def main():
    p=argparse.ArgumentParser();p.add_argument('--symbol',default='AAPL');p.add_argument('--as-of',required=True);p.add_argument('--company-facts');p.add_argument('--fetch',action='store_true');p.add_argument('--compare-cache',action='store_true');p.add_argument('--output');a=p.parse_args()
    if bool(a.company_facts)==bool(a.fetch):p.error('choose exactly one authorized JSON file or explicit --fetch')
    from terminal.stocks.identity import instrument
    from terminal.stocks.sec import facts,date
    cik=instrument(a.symbol)['cik'];date(a.as_of)
    if a.fetch:raw,url=official_fetch(cik,os.environ)
    else:
        with Path(a.company_facts).open('rb') as f:raw=f.read(8388609)
        url=None
    parsed=decode(raw);normalized=facts(parsed,cik,a.as_of)
    if a.compare_cache:
        # Fixed local owner server,not arbitrary URLs or forwarded authentication.
        connection=http.client.HTTPConnection('127.0.0.1',8787,timeout=5);connection.request('GET','/api/v1/stocks/company?symbol='+a.symbol)
        response=connection.getresponse();data=response.read(2097153);connection.close()
        if response.status!=200 or len(data)>2097152:raise ValueError('backend_cache_response')
        normalized=json.loads(data)['fundamentals'].get('financials')
        if normalized is None:raise ValueError('backend_SEC_cache_not_loaded')
        if normalized.get('issuer_cik')!=cik:raise ValueError('backend_cache_issuer_mismatch')
        if normalized['as_of_filing_date']!=a.as_of:raise ValueError('backend_cache_as_of_mismatch')
    result=reconcile(raw,normalized,a.as_of);result.update(source_url=url,source_authority='fixed_official_TLS_fetch' if a.fetch else 'owner_supplied_file_origin_not_independently_authenticated',backend_cache_compared=a.compare_cache,raw_retained=False)
    encoded=json.dumps(result,indent=2)+'\n'
    if a.output:
        with open(a.output,'x',encoding='utf-8') as f:f.write(encoded)
    print(encoded,end='');return 0 if result['status']=='AGREEMENT_WITHIN_SELECTED_RECORD_SCOPE' else 1

if __name__=='__main__':
    try:raise SystemExit(main())
    except Exception as error:print(json.dumps({'status':'BLOCKED_OR_INVALID','error_type':type(error).__name__,'reason':str(error) if isinstance(error,ValueError) and str(error).startswith(('SEC_','backend_')) else 'sanitized_source_or_configuration_failure','raw_retained':False}));raise SystemExit(2)
