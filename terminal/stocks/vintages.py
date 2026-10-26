"""Retained filing-date views,not complete XBRL statements or intraday PIT data."""
import copy
from .sec import date
from .financials import calculate

def at_filing_date(financials,as_of):
    date(as_of)
    if not financials or as_of>financials['as_of_filing_date']:raise ValueError('vintage_cache_boundary')
    out=copy.deepcopy(financials);selected={};truncated=False
    for metric,current in financials['history'].items():
        retained=financials.get('revision_history',{}).get(metric,[])
        rows={r['source_fact_id']:r for r in current+retained if r['filed']<=as_of}
        newest={}
        for r in sorted(rows.values(),key=lambda r:(r['filed'],r['accession'],r['source_fact_id'])):newest[(r['concept'],r['start'],r['end'],r['unit'])]=r
        selected[metric]=sorted(newest.values(),key=lambda r:(r['end'],r['start'] or '',r['filed'],r['concept']),reverse=True)
        truncated|=financials.get('coverage',{}).get(metric,{}).get('revision_history_truncated',False)
    out['history']=selected;out['as_of_filing_date']=as_of
    return {'schema':'gig.financial.vintage.v1','as_of_filing_date':as_of,'history':selected,'descriptors':calculate(out),'retained_history_truncated':truncated,'completeness':'PARTIAL_RETAINED_CACHE_NOT_COMPLETE_FILING_HISTORY','availability':'filing-date granularity only;not acceptance timestamp or tradable point-in-time authority','dimensions':'SEC companyfacts selected consolidated tags;XBRL context/dimension/presentation ingestion not implemented','limitations':['Omitted older revisions cannot be recovered from a latest-only current fact','No quarterly subtraction or missing-value imputation','No official source reconciliation implied']}
