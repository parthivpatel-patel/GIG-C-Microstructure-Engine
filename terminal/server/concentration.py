"""Proposed v1 research statistic on supplied levels,not exchange-wide liquidity.

The historical requirement names concentration but does not define an estimator.
This explicit research extension does not close that original acceptance decision.
"""
from fractions import Fraction
import re

MAX_LEVELS=20
UINT64_MAX=2**64-1
PRICE_MAX=2**63-1


def calculate(state,side='both',depth=10):
    if side not in ('bid','ask','both') or type(depth) is not int or not 1<=depth<=MAX_LEVELS:
        raise ValueError('concentration_selection')
    source={key:state.get(key) for key in ('origin','provider','instrument','revision','position','source_timestamp_ns','replay_time_ns')}
    parents=state.get('provenance',{})
    source['parents']={k:parents.get(k) for k in ('dataset','fixture_sha256','recording_sha256','clock')}
    result={'schema':'gig.research.supplied_depth_concentration.v1',
            'contract_status':'PROPOSED_RESEARCH_NOT_ORIGINAL_REQUIREMENT_ACCEPTANCE',
            'status':'UNAVAILABLE','reason':None,'side':side,'requested_depth_per_side':depth,
            'hhi':None,'normalized_hhi':None,'selected_levels':0,'source':source,
            'units':'dimensionless quantity shares squared;not price/notional concentration',
            'coverage':'Supplied selected levels only;full-book/full-market completeness not established',
            'normalization':'(n*HHI-1)/(n-1) for n>1;single positive level convention1',
            'historical_requirement':'Estimator definition remains unresolved;this is an explicit research proposal'}
    if state.get('origin') in (None,'UNAVAILABLE'):
        result['reason']='source_unavailable';return result
    selected=('bids','asks') if side=='both' else ('bids',) if side=='bid' else ('asks',)
    quantities=[];available={}
    try:
        for name in selected:
            levels=state['book'][name]
            if type(levels) is not list or len(levels)>MAX_LEVELS:raise ValueError()
            previous=None;available[name]=len(levels)
            for row in levels:
                p,q=row['price_ticks'],row['quantity']
                if any(type(v) is not str or not re.fullmatch(r'0|[1-9][0-9]{0,19}',v) for v in (p,q)):raise ValueError()
                p,q=int(p),int(q)
                if not 1<=p<=PRICE_MAX or not 0<=q<=UINT64_MAX:raise ValueError()
                if previous is not None and (p>=previous if name=='bids' else p<=previous):raise ValueError()
                previous=p
            quantities.extend(int(row['quantity']) for row in levels[:depth])
    except (KeyError,TypeError,ValueError):
        result['reason']='invalid_supplied_levels';return result
    result.update(available_levels=available,selected_levels=len(quantities),
                  requested_depth_populated=all(n>=depth for n in available.values()))
    if not quantities:
        result['reason']='no_supplied_levels';return result
    total=sum(quantities)
    if total==0:
        result['reason']='zero_quantity_denominator';return result
    if any(q==0 for q in quantities):
        result['reason']='zero_quantity_level';return result
    # <=40 uint64 quantities:sum<2**70;sum-of-squares<2**134.
    # Python integers/Fraction preserve exact ratios without monetary clipping.
    hhi=Fraction(sum(q*q for q in quantities),total*total);n=len(quantities)
    normalized=(n*hhi-1)/(n-1) if n>1 else Fraction(1)
    wire=lambda v:{'numerator':str(v.numerator),'denominator':str(v.denominator)}
    result.update(status='AVAILABLE_SUPPLIED_SUBSET',reason=None,hhi=wire(hhi),normalized_hhi=wire(normalized))
    return result
