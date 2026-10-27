"""Exact historical reported-period descriptors from a retained,possibly restated snapshot.
Never a claim that these values were available at the historical period end.
"""
import datetime
from .financials import calculate,DEFINITIONS

def reported_history(normalized,period='annual',limit=12):
    if period not in ('annual','quarter','ytd','all') or type(limit) is not int or not 1<=limit<=12:raise ValueError('ratio_history_query')
    history=normalized.get('history',{});cache={};metrics={};truncated={}
    def eligible(row):
        if row['start'] is None:return True
        days=(datetime.date.fromisoformat(row['end'])-datetime.date.fromisoformat(row['start'])).days+1
        if period=='all':return True
        if period=='annual':return 350<=days<=380 and row['form'] in ('10-K','10-K/A')
        if period=='quarter':return 75<=days<=105
        return 106<=days<=349 and row['form'] in ('10-Q','10-Q/A')
    for name,(_,_,inputs) in DEFINITIONS.items():
        anchor=inputs[0];instant=name in ('current_ratio','debt_to_equity')
        keys={(r['start'],r['end']) for r in history.get(anchor,[]) if (r['start'] is None)==instant and eligible(r)}
        keys=sorted(keys,key=lambda k:(k[1],k[0] or ''),reverse=True);truncated[name]=len(keys)>limit;points=[]
        for key in keys[:limit]:
            if key not in cache:cache[key]=calculate(normalized,target_period=key)['metrics']
            descriptor=cache[key][name]
            # Never fall back to a newer/different period when a required input is absent.
            if descriptor['period'] is not None and (descriptor['period']['start'],descriptor['period']['end'])!=key:raise ValueError('ratio_history_period_mismatch')
            points.append({**descriptor,'requested_period':{'start':key[0],'end':key[1]}})
        metrics[name]=points
    return {'schema':'gig.financial_history.v1','period_filter':period,'metrics':metrics,'truncated_periods':truncated,'as_of_filing_date':normalized.get('as_of_filing_date'),'maximum_periods_per_descriptor':limit,'method':'Existing exact descriptor calculator on explicit reported periods;instants independent of duration filter','availability':'RETAINED_RESTATED_SNAPSHOT_NOT_POINT_IN_TIME','limitations':['Later filings may restate earlier periods;not information available at period end','Missing and ambiguous inputs remain unavailable;no carry-forward,interpolation or inferred quarterly values','Beginning balances and adjacent annual periods are required where the existing formula requires them','Selected US-GAAP facts only;not complete financial statements or an authenticated historical response archive']}
