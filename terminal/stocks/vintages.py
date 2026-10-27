"""Retained filing-date views,not complete XBRL statements or intraday PIT data."""
import copy
from .sec import date
from .financials import calculate

def at_filing_date(financials,as_of):
    date(as_of)
    if not financials or as_of>financials['as_of_filing_date']:raise ValueError('vintage_cache_boundary')
    out=copy.deepcopy(financials);selected={};truncated=False;ambiguous=0
    for metric,current in financials['history'].items():
        retained=financials.get('revision_history',{}).get(metric,[])
        rows={r['source_fact_id']:r for r in current+retained if r['filed']<=as_of}
        groups={}
        for r in rows.values():groups.setdefault((r['concept'],r['start'],r['end'],r['unit']),[]).append(r)
        newest=[]
        for group in groups.values():
            latest=max(r['filed'] for r in group);winners=[r for r in group if r['filed']==latest]
            if len(winners)!=1:ambiguous+=len(winners);continue
            newest.append(winners[0])
        selected[metric]=sorted(newest,key=lambda r:(r['end'],r['start'] or '',r['filed'],r['concept']),reverse=True)
        truncated|=financials.get('coverage',{}).get(metric,{}).get('revision_history_truncated',False)
    out['history']=selected;out['as_of_filing_date']=as_of
    return {'schema':'gig.financial.vintage.v1','exclusions':{'ambiguous_same_filing_date':ambiguous},'as_of_filing_date':as_of,'history':selected,'descriptors':calculate(out),'retained_history_truncated':truncated,'completeness':'PARTIAL_RETAINED_CACHE_NOT_COMPLETE_FILING_HISTORY','availability':'filing-date granularity only;not acceptance timestamp or tradable point-in-time authority','dimensions':'SEC companyfacts selected consolidated tags;XBRL context/dimension/presentation ingestion not implemented','limitations':['Omitted older revisions cannot be recovered from a latest-only current fact','No quarterly subtraction or missing-value imputation','No official source reconciliation implied']}


def at_acceptance_time(financials,filings,as_of):
    """Conservative retained-cache filter,not an authenticated historical XBRL vintage."""
    import datetime
    from .sec import acceptance_ns as instant
    cutoff=instant(as_of)
    cutoff_day=datetime.datetime.fromtimestamp(cutoff//10**9,datetime.timezone.utc).date().isoformat()
    if not financials or type(filings) is not list or len(filings)>1024:raise ValueError('acceptance_cache_boundary')
    if cutoff_day>financials['as_of_filing_date']:raise ValueError('acceptance_cache_boundary')
    available={};ambiguous=set()
    for filing in filings:
        accession=filing['accession'];value=filing.get('accepted_at')
        if value is None:continue
        ns=instant(value)
        if accession in available and available[accession][0]!=ns:ambiguous.add(accession)
        available[accession]=(ns,value)
    selected={};excluded={'unknown_or_ambiguous_acceptance':0,'after_cutoff':0,'ambiguous_same_time_facts':0};truncated=False
    for metric,current in financials['history'].items():
        rows={r['source_fact_id']:r for r in current+financials.get('revision_history',{}).get(metric,[])};groups={}
        for r in rows.values():
            accession=r['accession']
            if accession not in available or accession in ambiguous:excluded['unknown_or_ambiguous_acceptance']+=1;continue
            ns,value=available[accession]
            if ns>cutoff or r['filed']>cutoff_day:excluded['after_cutoff']+=1;continue
            key=(r['concept'],r['start'],r['end'],r['unit']);groups.setdefault(key,[]).append((ns,r,value))
        accepted=[]
        for group in groups.values():
            latest=max(r[0] for r in group);winners=[r for r in group if r[0]==latest]
            if len(winners)!=1:excluded['ambiguous_same_time_facts']+=len(winners);continue
            _,r,value=winners[0];accepted.append({**r,'accepted_at':value,'availability_source':'cached_submissions_accession_match'})
        selected[metric]=sorted(accepted,key=lambda r:(r['end'],r['start'] or '',r['filed'],r['concept']),reverse=True)
        truncated|=financials.get('coverage',{}).get(metric,{}).get('revision_history_truncated',False)
    out=copy.deepcopy(financials);out['history']=selected;out['as_of_filing_date']=cutoff_day
    return {'schema':'gig.financial.acceptance.v1','as_of':as_of,'cutoff_ns':str(cutoff),'history':selected,'descriptors':calculate(out),'exclusions':excluded,'retained_history_truncated':truncated,'completeness':'PARTIAL_RETAINED_CACHE_NOT_AUTHENTICATED_SOURCE_VINTAGE','limitations':['Unknown acceptance times are excluded,never replaced by midnight or current filings','Bounded1024 submissions/retained revisions may omit older eligible facts','Current companyfacts retrieval cannot prove what an older response contained','No complete XBRL dimensions,presentation or tradable PIT authority']}
