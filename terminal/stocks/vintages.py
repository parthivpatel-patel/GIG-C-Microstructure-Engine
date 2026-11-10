"""Retained filing-date views,not complete XBRL statements or intraday PIT data."""
import copy,hashlib,json,re
from .sec import date
from .financials import calculate

def retained_rows(current,revisions):
    if type(current)is not list or len(current)>256 or type(revisions)is not list or len(revisions)>16:raise ValueError('acceptance_fact_budget')
    rows={}
    for row in current+revisions:
        if type(row)is not dict or type(row.get('source_fact_id'))is not str or not re.fullmatch('[a-f0-9]{64}',row['source_fact_id']):raise ValueError('acceptance_fact_identity')
        key=row['source_fact_id']
        if key in rows and rows[key]!=row:raise ValueError('acceptance_contradictory_fact')
        rows[key]=row
    return list(rows.values())

def filing_index(filings,strict):
    from .sec import acceptance_ns,FORMS
    if type(filings)is not list or len(filings)>1024:raise ValueError('acceptance_cache_boundary')
    result={};ambiguous=set()
    for row in filings:
        if type(row)is not dict or type(row.get('accession'))is not str or not re.fullmatch(r'\d{10}-\d{2}-\d{6}',row['accession']):raise ValueError('acceptance_filing_identity')
        if strict or 'form'in row or 'filed'in row:
            if type(row.get('form'))is not str or row['form']not in FORMS:raise ValueError('acceptance_filing_form')
            date(row.get('filed'))
        core={k:row.get(k)for k in ('accession','form','filed','report_date','accepted_at')}
        if core['report_date']is not None:date(core['report_date'])
        if core['accepted_at']is not None:acceptance_ns(core['accepted_at'])
        if core['accession']in result and result[core['accession']]!=core:
            if strict:raise ValueError('acceptance_contradictory_filing')
            ambiguous.add(core['accession'])
        result[core['accession']]=core
    return result,ambiguous


def at_filing_date(financials,as_of):
    date(as_of)
    if not financials or as_of>financials['as_of_filing_date']:raise ValueError('vintage_cache_boundary')
    out=copy.deepcopy(financials);selected={};truncated=False;ambiguous=0
    for metric,current in financials['history'].items():
        retained=financials.get('revision_history',{}).get(metric,[])
        rows={r['source_fact_id']:r for r in retained_rows(current,retained)if r['filed']<=as_of}
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


def at_acceptance_time(financials,filings,as_of,*,strict_filing_metadata=False):
    """Conservative retained-cache filter,not an authenticated historical XBRL vintage."""
    import datetime
    from .sec import acceptance_ns as instant
    if type(strict_filing_metadata)is not bool:raise ValueError('acceptance_profile')
    cutoff=instant(as_of)
    cutoff_day=datetime.datetime.fromtimestamp(cutoff//10**9,datetime.timezone.utc).date().isoformat()
    if not financials or type(filings) is not list or len(filings)>1024:raise ValueError('acceptance_cache_boundary')
    if cutoff_day>financials['as_of_filing_date']:raise ValueError('acceptance_cache_boundary')
    index,ambiguous=filing_index(filings,strict_filing_metadata);available={a:(instant(r['accepted_at']),r['accepted_at'])for a,r in index.items()if r['accepted_at']is not None and a not in ambiguous}
    selected={};excluded={'unknown_or_ambiguous_acceptance':0,'after_cutoff':0,'ambiguous_same_time_facts':0,'filing_metadata_mismatch':0};truncated=False;matched=set();superseded=set()
    for metric,current in financials['history'].items():
        rows={r['source_fact_id']:r for r in retained_rows(current,financials.get('revision_history',{}).get(metric,[]))};groups={}
        for r in rows.values():
            accession=r['accession']
            if accession not in available:excluded['unknown_or_ambiguous_acceptance']+=1;continue
            if index[accession]['form']is not None and (r['form'],r['filed'])!=(index[accession]['form'],index[accession]['filed']):excluded['filing_metadata_mismatch']+=1;continue
            ns,value=available[accession]
            if ns>cutoff or r['filed']>cutoff_day:excluded['after_cutoff']+=1;continue
            key=(r['concept'],r['start'],r['end'],r['unit']);groups.setdefault(key,[]).append((ns,r,value))
        accepted=[]
        for group in groups.values():
            latest=max(r[0] for r in group);winners=[r for r in group if r[0]==latest]
            if len(winners)!=1:excluded['ambiguous_same_time_facts']+=len(winners);continue
            _,r,value=winners[0];matched.add(r['accession']);superseded.update(x[1]['source_fact_id']for x in group if x[1]['source_fact_id']!=r['source_fact_id']);accepted.append({**r,'accepted_at':value,'availability_source':'cached_submissions_accession_match'})
        selected[metric]=sorted(accepted,key=lambda r:(r['end'],r['start'] or '',r['filed'],r['concept']),reverse=True)
        truncated|=financials.get('coverage',{}).get(metric,{}).get('revision_history_truncated',False)
    out=copy.deepcopy(financials);out['history']=selected;out['as_of_filing_date']=cutoff_day
    profile='STRICT_FILING_METADATA_V1'if strict_filing_metadata else'LEGACY_ACCESSION_TIME_V1'
    lineage={'admission_profile':profile,'matched_filings':[index[a]for a in sorted(matched)],'superseded_source_fact_ids':sorted(superseded),'original_response_received_at':None,'authority':'Cached submissions accession/form/filing-date join,not original response vintage or complete XBRL presentation'if strict_filing_metadata else'Legacy cached accession/time match;missing filing form/date unverified;not original source vintage','policy':'Latest accepted retained fact per identical concept/start/end/unit;amendments remain distinct accessions,not additive statements'}
    selection_sha256=hashlib.sha256(json.dumps({'cutoff_ns':str(cutoff),'history':selected,'filing_lineage':lineage},sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return {'schema':'gig.financial.acceptance.v1','admission_profile':profile,'filing_lineage':lineage,'selection_sha256':selection_sha256,'as_of':as_of,'cutoff_ns':str(cutoff),'history':selected,'descriptors':calculate(out),'exclusions':excluded,'retained_history_truncated':truncated,'completeness':'PARTIAL_RETAINED_CACHE_NOT_AUTHENTICATED_SOURCE_VINTAGE','limitations':['Unknown acceptance times are excluded,never replaced by midnight or current filings','Bounded1024 submissions/retained revisions may omit older eligible facts','Current companyfacts retrieval cannot prove what an older response contained','No complete XBRL dimensions,presentation or tradable PIT authority']}
