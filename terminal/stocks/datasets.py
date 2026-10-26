"""Exact interval-aligned private revision analysis. No rows exported or currencies inferred."""
from fractions import Fraction
import hashlib,json
from .portfolio import analyze
from .history_store import verify,MAX_PAYLOAD,RETENTION_SECONDS

def analyze_revisions(store,selections,weights):
    if type(selections) is not dict or not 1<=len(selections)<=4 or type(weights) is not dict or set(weights)!=set(selections):raise ValueError('dataset_selection')
    cores={}
    # One serialized SQLite read transaction across every revision prevents mixed restores.
    with store.connect() as db:
        db.execute('BEGIN')
        for alias,revision in selections.items():
            store.key(revision)
            row=db.execute('SELECT created,payload FROM snapshots WHERE revision=?',(revision,)).fetchone()
            if row is None or row[0]<store.clock()-RETENTION_SECONDS:raise ValueError('dataset_revision_missing')
            raw=row[1]
            if type(raw) is not bytes or len(raw)>MAX_PAYLOAD or hashlib.sha256(raw).hexdigest()!=revision:raise ValueError('dataset_revision_integrity')
            core=verify(json.loads(raw))
            if core['source']['origin']!='HISTORICAL_SYNTHETIC' and not store.allow_observed:raise ValueError('dataset_retention_permission')
            cores[alias]=core
    if len({(c['timeframe'],c['source']['adjustment'],c['source']['origin']) for c in cores.values()})!=1:raise ValueError('dataset_incompatible_sources')
    if any(c['source']['adjustment']!='raw' for c in cores.values()):raise ValueError('dataset_adjustments_unverified')
    paths={}
    for alias,core in cores.items():
        rows=core['bars'];paths[alias]={(a['timestamp_ns'],b['timestamp_ns']):Fraction(b['close'])/Fraction(a['close'])-1 for a,b in zip(rows,rows[1:])}
    common=set.intersection(*(set(v) for v in paths.values()));ordered=sorted(common,key=lambda pair:(int(pair[0]),int(pair[1])))
    if not 20<=len(ordered)<=64:raise ValueError('dataset_aligned_interval_budget20_to64')
    def rational(v):return f'{v.numerator}/{v.denominator}'
    inputs={'assets':{alias:[rational(paths[alias][pair]) for pair in ordered] for alias in sorted(cores)},'weights':weights,'horizon':'matched historical timestamp intervals;session calendar unverified'}
    result=analyze(inputs,_rational=True)
    return {'schema':'gig.dataset.analysis.v1','source_revisions':selections,'classification':'SIMULATED' if next(iter(cores.values()))['state']=='SIMULATED' else 'HISTORICAL','aligned_intervals':len(ordered),'excluded_intervals':{a:len(v)-len(ordered) for a,v in paths.items()},'alignment_sha256':hashlib.sha256(json.dumps(ordered,separators=(',',':')).encode()).hexdigest(),'analysis':result,'method':'Exact matching interval start AND end across immutable revisions;explicit weights;no missing fill/no synthetic identities','limitations':['Exact rational returns remain rational;display decimals never used as calculation inputs','No verified exchange calendar,corporate actions,FX or source-price unit compatibility inferred','Inner-intersection exclusions disclosed;selection may bias research','Stored source identity is not independent provider licensing/empirical qualification']}
