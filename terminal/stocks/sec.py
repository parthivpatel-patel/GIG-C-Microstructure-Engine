"""Period-aware, bounded SEC-shaped disclosure parsing. No invented missing facts."""
import datetime,re,hashlib,json
from fractions import Fraction
from decimal import Decimal

TAGS={'revenue':('RevenueFromContractWithCustomerExcludingAssessedTax','Revenues','SalesRevenueNet'),'net_income':('NetIncomeLoss',),'operating_cash_flow':('NetCashProvidedByUsedInOperatingActivities',),'assets':('Assets',),'liabilities':('Liabilities',),'equity':('StockholdersEquity',),'cash':('CashAndCashEquivalentsAtCarryingValue',),'eps':('EarningsPerShareDiluted',),'gross_profit':('GrossProfit',),'operating_income':('OperatingIncomeLoss',),'assets_current':('AssetsCurrent',),'liabilities_current':('LiabilitiesCurrent',),'short_term_borrowings':('ShortTermBorrowings',),'long_term_debt_current':('LongTermDebtCurrent',),'long_term_debt_noncurrent':('LongTermDebtNoncurrent',),'capex':('PaymentsToAcquirePropertyPlantAndEquipment',)}
TAGS.update({'cost_of_revenue':('CostOfRevenue','CostOfGoodsAndServicesSold'),
 'cash_investing':('NetCashProvidedByUsedInInvestingActivities',),'cash_financing':('NetCashProvidedByUsedInFinancingActivities',),
 'cash_fx':('EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents',),
 'cash_change':('CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect',),
 'eps_basic':('EarningsPerShareBasic',),'diluted_shares':('WeightedAverageNumberOfDilutedSharesOutstanding',)})
UNITS={'eps':'USD/shares','eps_basic':'USD/shares','diluted_shares':'shares'}
FORMS={'10-K','10-K/A','10-Q','10-Q/A','8-K','8-K/A','13F-HR','13F-HR/A'}

def date(value):
    if type(value) is not str or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',value):raise ValueError('sec_date')
    try:datetime.date.fromisoformat(value)
    except ValueError:raise ValueError('sec_date') from None
    return value

def text(value,limit=256):
    if type(value) is not str or len(value)>limit or any(ord(c)<32 for c in value):raise ValueError('sec_text')
    return value

def exact(value):
    # SEC monetary values are JSON numbers; preserve every supplied decimal digit.
    if type(value) not in (int,Decimal) or isinstance(value,bool):raise ValueError('sec_numeric')
    if not Decimal(value).is_finite() or len(str(value))>64 or Decimal(value).copy_abs()>10**30 or not -128<=Decimal(value).as_tuple().exponent<=30:raise ValueError('sec_numeric')
    return str(value)

def object_value(value):
    if type(value) is not dict:raise ValueError('sec_structure')
    return value

def acceptance_ns(value):
    """One exact acceptance grammar for normalization and retained-cache filtering."""
    from terminal.providers.kraken import timestamp_ns
    if type(value) is not str or len(value)>40:raise ValueError('sec_acceptance_timestamp')
    match=re.fullmatch(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(\.\d{1,9})?(Z|[+-]\d{2}:\d{2})',value)
    if not match:raise ValueError('sec_acceptance_timestamp')
    try:
        whole=datetime.datetime.fromisoformat(match[1]+match[3].replace('Z','+00:00')).astimezone(datetime.timezone.utc)
        return int(timestamp_ns(whole.strftime('%Y-%m-%dT%H:%M:%S')+(match[2] or '')+'Z'))
    except (ValueError,OverflowError):raise ValueError('sec_acceptance_timestamp') from None

def filings(payload,cik,*,limit=128):
    if type(limit) is not int or not 1<=limit<=1024:raise ValueError('sec_filing_output_budget')
    object_value(payload)
    if str(payload.get('cik','')).lstrip('0')!=cik.lstrip('0'):raise ValueError('sec_identity')
    recent=object_value(object_value(payload.get('filings',{})).get('recent',{}))
    required=('accessionNumber','form','filingDate','primaryDocument')
    if any(type(recent.get(k)) is not list for k in required):raise ValueError('sec_filing_columns')
    count=len(recent['form'])
    if count>10000 or any(len(recent[k])!=count for k in required):raise ValueError('sec_filing_alignment')
    for k in ('acceptanceDateTime','reportDate'):
        if k in recent and (type(recent[k]) is not list or len(recent[k])!=count):raise ValueError('sec_filing_alignment')
    rows=[];seen={};duplicates=0
    for i in range(count):
        form=text(recent['form'][i],32)
        if form not in FORMS:continue
        accession=recent['accessionNumber'][i];doc=recent['primaryDocument'][i]
        if type(accession) is not str or not re.fullmatch(r'\d{10}-\d{2}-\d{6}',accession):raise ValueError('sec_accession')
        if type(doc) is not str or not re.fullmatch(r'[A-Za-z0-9_.-]{1,160}',doc) or '..' in doc:raise ValueError('sec_document')
        filed=date(recent['filingDate'][i]);accepted=recent.get('acceptanceDateTime',[None]*count)[i]
        if accepted is not None:
            acceptance_ns(accepted)
        report=recent.get('reportDate',[None]*count)[i]
        if report:date(report)
        row={'form':form,'amendment':form.endswith('/A'),'accession':accession,'filed':filed,'accepted_at':accepted,'report_date':report or None,'url':f'https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession.replace("-","")}/{doc}'}
        if accession in seen:
            if seen[accession]!=row:raise ValueError('sec_contradictory_filing')
            duplicates+=1;continue
        seen[accession]=row;rows.append(row)
    rows.sort(key=lambda r:(r['filed'],r['accession']),reverse=True)
    return {'filings':rows[:limit],'coverage':'recent submissions only;older filing shards not fetched','integrity':{'input_rows':count,'eligible_unique_rows':len(rows),'duplicate_rows':duplicates,'selected_rows':min(len(rows),limit),'truncated':len(rows)>limit},'institutional_holdings':{'status':'UNAVAILABLE','reason':'Issuer filings are not a holder registry. 13F manager reports disclose delayed quarter-end positions, not real-time ownership;information-table ingestion not implemented.'},'timeline':[{'event':r['form'],'published_at':r['accepted_at'],'filing_date':r['filed'],'url':r['url'],'source':'SEC EDGAR'} for r in rows[:64]]}

def facts(payload,cik,as_of):
    object_value(payload)
    date(as_of)
    if str(payload.get('cik','')).lstrip('0')!=cik.lstrip('0'):raise ValueError('sec_identity')
    namespace=object_value(payload.get('facts',{})).get('us-gaap',{})
    if type(namespace) is not dict:raise ValueError('sec_facts')
    history={};coverage={};revisions={}
    for metric,tags in TAGS.items():
        records=[]
        for tag in tags:
            data=object_value(namespace.get(tag,{}))
            unit=UNITS.get(metric,'USD')
            values=object_value(data.get('units',{})).get(unit,[])
            if type(values) is not list or len(values)>10000:raise ValueError('sec_fact_budget')
            for r in values:
                if type(r) is not dict:raise ValueError('sec_fact_record')
                if r.get('form') not in ('10-K','10-K/A','10-Q','10-Q/A'):continue
                filed=date(r['filed']);end=date(r['end']);start=date(r['start']) if 'start' in r else None
                if (start and start>end) or end>filed:raise ValueError('sec_fact_period')
                if filed>as_of:continue
                accession=text(r['accn'],24)
                if not re.fullmatch(r'\d{10}-\d{2}-\d{6}',accession):raise ValueError('sec_accession')
                fiscal_year=r.get('fy');fiscal_period=r.get('fp')
                if fiscal_year is not None and (type(fiscal_year) is not int or not 1800<=fiscal_year<=2200):raise ValueError('sec_filing_fiscal_year')
                if fiscal_period is not None:text(fiscal_period,16)
                row={'issuer_cik':cik,'concept':tag,'unit':unit,'value':exact(r['val']),'start':start,'end':end,'filed':filed,'accession':accession,'form':r['form'],'frame':text(r['frame'],40) if 'frame' in r else None,'filing_fiscal_year':fiscal_year,'filing_fiscal_period':fiscal_period,'period_kind':'duration' if start else 'instant','duration_days':(datetime.date.fromisoformat(end)-datetime.date.fromisoformat(start)).days+1 if start else None}
                row['source_fact_id']=hashlib.sha256(json.dumps(row,sort_keys=True,separators=(',',':')).encode()).hexdigest()
                records.append(row)
        # Keep competing concepts separate. Latest filing for the same tagged period
        # is a deliberate as-of restatement policy, not original point-in-time history.
        duplicates={}
        for r in records:
            key=(r['concept'],r['start'],r['end'],r['unit'],r['filed'],r['accession'])
            if key in duplicates and Decimal(duplicates[key])!=Decimal(r['value']):raise ValueError('sec_contradictory_fact')
            duplicates[key]=r['value']
        selected={}
        for r in sorted(records,key=lambda r:(r['filed'],r['accession'],r['source_fact_id'])):selected[(r['concept'],r['start'],r['end'],r['unit'])]=r
        ordered=sorted(selected.values(),key=lambda r:(r['end'],r['start'] or '',r['filed'],r['concept']),reverse=True)
        revisions[metric]=sorted(records,key=lambda r:(r['filed'],r['accession'],r['source_fact_id']),reverse=True)[:16]
        history[metric]=ordered[:256];coverage[metric]={'available':bool(ordered),'truncated':len(ordered)>256,'eligible_periods':len(ordered),'revision_rows':len(records),'revision_rows_retained':min(16,len(records)),'revision_history_truncated':len(records)>16,'expected_unit':unit}
    # No mixing quarterly/annual durations or incompatible end dates.
    ratios={}
    for name,numerator,denominator,duration in [('net_margin','net_income','revenue',True),('liabilities_to_assets','liabilities','assets',False)]:
        matches=[]
        for a in history[numerator]:
            for b in history[denominator]:
                if (a['start'],a['end'])==(b['start'],b['end']) and bool(a['start'])==duration and Fraction(b['value'])!=0:
                    f=Fraction(a['value'])/Fraction(b['value']);matches.append({'numerator':str(f.numerator),'denominator':str(f.denominator),'start':a['start'],'end':a['end'],'source_accessions':[a['accession'],b['accession']],'concepts':[a['concept'],b['concept']]})
        ambiguous=bool(matches and len({(r['numerator'],r['denominator']) for r in matches if (r['start'],r['end'])==(matches[0]['start'],matches[0]['end'])})>1)
        ratios[name]={'value':matches[0] if matches and not ambiguous else None,'reason':'ambiguous_compatible_concepts' if ambiguous else None if matches else 'missing_compatible_periods'}
    return {'financial_schema_version':'2','issuer_cik':cik,'as_of_filing_date':as_of,'revision_history':revisions,'history':history,'coverage':coverage,'ratios':ratios,'methodology':'us-gaap selected tags/units only;all alternatives labelled;latest filing per tagged period as-of date;no fiscal-quarter subtraction,imputation or cross-period ratios;not a point-in-time trading dataset'}
