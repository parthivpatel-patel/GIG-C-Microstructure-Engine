"""Period-aware, bounded SEC-shaped disclosure parsing. No invented missing facts."""
import datetime,re
from fractions import Fraction
from decimal import Decimal

TAGS={'revenue':('RevenueFromContractWithCustomerExcludingAssessedTax','Revenues','SalesRevenueNet'),'net_income':('NetIncomeLoss',),'operating_cash_flow':('NetCashProvidedByUsedInOperatingActivities',),'assets':('Assets',),'liabilities':('Liabilities',),'equity':('StockholdersEquity',),'cash':('CashAndCashEquivalentsAtCarryingValue',),'eps':('EarningsPerShareDiluted',)}
FORMS={'10-K','10-K/A','10-Q','10-Q/A','8-K','8-K/A','13F-HR','13F-HR/A'}

def date(value):
    if type(value) is not str or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',value):raise ValueError('sec_date')
    datetime.date.fromisoformat(value)
    return value

def text(value,limit=256):
    if type(value) is not str or len(value)>limit or any(ord(c)<32 for c in value):raise ValueError('sec_text')
    return value

def exact(value):
    # SEC monetary values are JSON numbers; preserve every supplied decimal digit.
    from decimal import Decimal
    if type(value) not in (int,Decimal) or isinstance(value,bool):raise ValueError('sec_numeric')
    if not Decimal(value).is_finite() or len(str(value))>64 or abs(value)>10**30 or not -12<=Decimal(value).as_tuple().exponent<=30:raise ValueError('sec_numeric')
    return str(value)

def filings(payload,cik):
    if str(payload.get('cik','')).lstrip('0')!=cik.lstrip('0'):raise ValueError('sec_identity')
    recent=payload.get('filings',{}).get('recent',{})
    required=('accessionNumber','form','filingDate','primaryDocument')
    if any(type(recent.get(k)) is not list for k in required):raise ValueError('sec_filing_columns')
    count=len(recent['form'])
    if count>10000 or any(len(recent[k])!=count for k in required):raise ValueError('sec_filing_alignment')
    for k in ('acceptanceDateTime','reportDate'):
        if k in recent and (type(recent[k]) is not list or len(recent[k])!=count):raise ValueError('sec_filing_alignment')
    rows=[]
    for i in range(count):
        form=text(recent['form'][i],32)
        if form not in FORMS:continue
        accession=recent['accessionNumber'][i];doc=recent['primaryDocument'][i]
        if type(accession) is not str or not re.fullmatch(r'\d{10}-\d{2}-\d{6}',accession):raise ValueError('sec_accession')
        if type(doc) is not str or not re.fullmatch(r'[A-Za-z0-9_.-]{1,160}',doc) or '..' in doc:raise ValueError('sec_document')
        filed=date(recent['filingDate'][i]);accepted=recent.get('acceptanceDateTime',[None]*count)[i]
        if accepted is not None:
            text(accepted,40)
            try:stamp=datetime.datetime.fromisoformat(accepted.replace('Z','+00:00'))
            except ValueError:raise ValueError('sec_acceptance_timestamp') from None
            if stamp.tzinfo is None:raise ValueError('sec_acceptance_timestamp')
        report=recent.get('reportDate',[None]*count)[i]
        if report:date(report)
        rows.append({'form':form,'amendment':form.endswith('/A'),'accession':accession,'filed':filed,'accepted_at':accepted,'report_date':report or None,'url':f'https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession.replace("-","")}/{doc}'})
    rows.sort(key=lambda r:(r['filed'],r['accession']),reverse=True)
    return {'filings':rows[:128],'coverage':'recent submissions only;older filing shards not fetched','institutional_holdings':{'status':'UNAVAILABLE','reason':'Issuer filings are not a holder registry. 13F manager reports disclose delayed quarter-end positions, not real-time ownership;information-table ingestion not implemented.'},'timeline':[{'event':r['form'],'published_at':r['accepted_at'],'filing_date':r['filed'],'url':r['url'],'source':'SEC EDGAR'} for r in rows[:64]]}

def facts(payload,cik,as_of):
    date(as_of)
    if str(payload.get('cik','')).lstrip('0')!=cik.lstrip('0'):raise ValueError('sec_identity')
    namespace=payload.get('facts',{}).get('us-gaap',{})
    if type(namespace) is not dict:raise ValueError('sec_facts')
    history={};coverage={}
    for metric,tags in TAGS.items():
        records=[]
        for tag in tags:
            data=namespace.get(tag,{})
            unit='USD/shares' if metric=='eps' else 'USD'
            values=data.get('units',{}).get(unit,[])
            if type(values) is not list or len(values)>10000:raise ValueError('sec_fact_budget')
            for r in values:
                if type(r) is not dict:raise ValueError('sec_fact_record')
                if r.get('form') not in ('10-K','10-K/A','10-Q','10-Q/A'):continue
                filed=date(r['filed']);end=date(r['end']);start=date(r['start']) if 'start' in r else None
                if (start and start>end) or end>filed:raise ValueError('sec_fact_period')
                if filed>as_of:continue
                accession=text(r['accn'],24)
                if not re.fullmatch(r'\d{10}-\d{2}-\d{6}',accession):raise ValueError('sec_accession')
                records.append({'concept':tag,'unit':unit,'value':exact(r['val']),'start':start,'end':end,'filed':filed,'accession':accession,'form':r['form'],'frame':text(r['frame'],40) if 'frame' in r else None})
        # Keep competing concepts separate. Latest filing for the same tagged period
        # is a deliberate as-of restatement policy, not original point-in-time history.
        duplicates={}
        for r in records:
            key=(r['concept'],r['start'],r['end'],r['unit'],r['filed'],r['accession'])
            if key in duplicates and Decimal(duplicates[key])!=Decimal(r['value']):raise ValueError('sec_contradictory_fact')
            duplicates[key]=r['value']
        selected={}
        for r in sorted(records,key=lambda r:(r['filed'],r['accession'])):selected[(r['concept'],r['start'],r['end'],r['unit'])]=r
        ordered=sorted(selected.values(),key=lambda r:(r['end'],r['start'] or '',r['filed'],r['concept']),reverse=True)
        history[metric]=ordered[:256];coverage[metric]={'available':bool(ordered),'truncated':len(ordered)>256,'eligible_periods':len(ordered)}
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
    return {'as_of_filing_date':as_of,'history':history,'coverage':coverage,'ratios':ratios,'methodology':'us-gaap selected tags/units only;all alternatives labelled;latest filing per tagged period as-of date;no fiscal-quarter subtraction,imputation or cross-period ratios;not a point-in-time trading dataset'}
