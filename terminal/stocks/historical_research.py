"""Bounded trailing descriptive research on an accepted historical revision.

No future prices,imputation,annualization or inferred trade direction. Exact
simple-return/SMA/drawdown/volume values;binary64 logs/square roots disclosed.
"""
import hashlib,json,math
from fractions import Fraction
from .historical_v2 import canonical,ns
from terminal.alpaca_wire import WireError


def fraction(value):
    if value is None:return None
    if max(value.numerator.bit_length(),value.denominator.bit_length())>4096:raise WireError('historical_research_exact_capacity')
    return {'numerator':str(value.numerator),'denominator':str(value.denominator)}


def analyze(core,*,window=5,gap_policy='disclose',max_gap_seconds=None):
    if type(core)is not dict or core.get('schema')!='gig.alpaca.history.v2' or core.get('kind')!='bars' or type(core.get('records'))is not list or len(core['records'])>256:raise WireError('historical_research_bars_required')
    if type(window)is not int or not 2<=window<=64 or gap_policy not in ('disclose','break') or max_gap_seconds is not None and (type(max_gap_seconds)is not int or not 1<=max_gap_seconds<=604800):raise WireError('historical_research_parameters')
    if gap_policy=='break' and max_gap_seconds is None:raise WireError('historical_research_declared_gap_required')
    rows=core['records'];series=[];closes=[];logs=[];peak=None;gaps=[];notional=Fraction();volume=Fraction();notional_available=True;prior=None
    for i,r in enumerate(rows):
        try:
            p=Fraction(r['close']);v=Fraction(r['volume']);t=ns(r['timestamp'])
            if p<=0 or v<0 or str(t)!=r['source_timestamp_ns'] or prior is not None and t<=prior:raise ValueError()
        except (ValueError,TypeError,KeyError,ZeroDivisionError):raise WireError('historical_research_input') from None
        elapsed=None if prior is None else t-prior;has_gap=max_gap_seconds is not None and elapsed is not None and elapsed>max_gap_seconds*10**9
        if has_gap:gaps.append({'before_index':i,'elapsed_ns':str(elapsed),'authority':'CALLER_DECLARED_THRESHOLD_NOT_EXCHANGE_CALENDAR'})
        simple=p/closes[-1]-1 if closes and not(has_gap and gap_policy=='break') else None
        log=None
        if simple is not None:
            log=math.log(float(p/closes[-1]))
            if not math.isfinite(log):raise WireError('historical_research_log_capacity')
        closes.append(p);logs.append(log);peak=p if peak is None else max(peak,p)
        sma=sum(closes[-window:],Fraction())/window if i+1>=window else None
        last=logs[max(0,len(logs)-window):]
        rolling=math.sqrt(sum(x*x for x in last)) if len(last)==window and all(x is not None for x in last) else None
        volume+=v
        if v and r.get('vwap') is None:notional_available=False
        elif v:
            vw=Fraction(r['vwap'])
            if vw<=0:raise WireError('historical_research_vwap')
            notional+=vw*v
        series.append({'timestamp':r['timestamp'],'source_timestamp_ns':str(t),'close':r['close'],'simple_return':fraction(simple),'log_return':log,'trailing_sma':fraction(sma),'rolling_log_variation':rolling,'close_drawdown':fraction(1-p/peak),'source_volume':r['volume']})
        prior=t
    valid=[v for v in logs if v is not None]
    result={'schema':'gig.historical.research.v1','source_revision':core['canonical_sha256'],'symbol':core['symbol'],'origin':core['origin'],'feed':core['feed'],'query':core['query'],'adjustment':core['adjustment'],'parameters':{'window':window,'gap_policy':gap_policy,'max_gap_seconds':max_gap_seconds},'state':'AVAILABLE' if len(series)>=2 else 'INSUFFICIENT_OBSERVATIONS','record_count':len(series),'eligible_return_count':len(valid),'series':series,'summary':{'interval_close_return':fraction(closes[-1]/closes[0]-1)if len(closes)>=2 else None,'realized_log_variation':math.sqrt(sum(x*x for x in valid))if valid else None,'maximum_close_drawdown':max((r['close_drawdown'] for r in series),key=lambda x:Fraction(int(x['numerator']),int(x['denominator'])))if series else None,'volume':fraction(volume)if series else None,'notional_turnover':fraction(notional)if notional_available and series else None,'supplied_bar_vwap':fraction(notional/volume)if notional_available and volume else None},'gap_candidates':gaps,'session':core['session'],'source_records':core['source_records'],'received_at':core['received_at'],'units':{'simple_return':'fractional close-to-close return','log_return':'natural log close ratio','trailing_sma':'source price units','rolling_log_variation':'sqrt(sum of last window log-return squares);not annualized','volume':'source reported volume;no lot conversion','notional_turnover':'sum of supplied barVWAP × source volume;unavailable if positive-volumeVWAP missing'},'limitations':['Descriptive trailing outputs,not calibrated forecasts or profitable signals.','Raw/split/dividend adjustment is inherited;corporate actions are not independently reconciled.','Session/holiday/halts completeness is not established;elapsed gaps are explicit.','No interpolation,missing-price fill,depth,queue or trade-sign inference.']}
    result['canonical_sha256']=hashlib.sha256(canonical(result)).hexdigest()
    return result


def compare(analyses):
    if type(analyses)is not list or not 2<=len(analyses)<=4 or len({a['symbol']for a in analyses})!=len(analyses):raise WireError('historical_comparison_scope')
    first=analyses[0]
    for a in analyses:
        if any(a[k]!=first[k] for k in ('feed','origin','adjustment','parameters')) or any(a['query'][k]!=first['query'][k]for k in ('start','end','timeframe')):raise WireError('historical_comparison_scope')
    maps=[{r['source_timestamp_ns']:r for r in a['series']}for a in analyses]
    times=sorted(set.intersection(*(set(m)for m in maps)),key=int)
    result={'schema':'gig.historical.comparison.v1','state':'AVAILABLE' if len(times)>=2 else 'INSUFFICIENT_SHARED_ENDPOINTS','timestamps_ns':times,'symbols':[a['symbol']for a in analyses],'source_revisions':[a['source_revision']for a in analyses],'series':[],'policy':'Exact shared source endpoints;no interpolation or nearest-neighbor fill. Returns span identical selected endpoints;not a synchronized-clock/market-wide claim.'}
    for a,m in zip(analyses,maps):
        base=Fraction(m[times[0]]['close']) if times else None
        result['series'].append({'symbol':a['symbol'],'percentage_change':[fraction((Fraction(m[t]['close'])/base-1)*100)for t in times]})
    return result


def export(client,revision,**parameters):
    core=client.accepted(revision)
    if core['origin']!='HISTORICAL_SYNTHETIC' and not getattr(client.permission,'export_approved',False):raise WireError('historical_export_retention_permission_required')
    payload={'schema':'gig.historical.research.export.v1','source':core,'analysis':analyze(core,**parameters),'privacy':'Owner-only authorized use;no redistribution rights inferred.'}
    return {'payload_json':canonical(payload).decode('utf8'),'payload_sha256':hashlib.sha256(canonical(payload)).hexdigest(),'encoding':'Exact UTF8 payload_json bytes;sorted compact finite JSON;not a signature or provider authenticity proof'}
