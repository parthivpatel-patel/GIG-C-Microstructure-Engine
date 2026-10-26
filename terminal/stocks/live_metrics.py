"""Exact best-quote analytics from bounded accepted observations,not full-depth flow."""
from fractions import Fraction
import math

def metrics(history,symbol,generation):
    rows=[r for r in history if r['symbol']==symbol and r['generation']==generation]
    quotes=[r for r in rows if r['kind']=='quote' and not r['out_of_order'] and Fraction(r['data']['bid'])>0 and Fraction(r['data']['ask'])>=Fraction(r['data']['bid'])]
    trades=[r for r in rows if r['kind']=='trade' and not r['out_of_order']]
    corrected=any(r['kind'] in ('correction','cancel') for r in rows)
    wire=lambda f:{'numerator':str(f.numerator),'denominator':str(f.denominator)}
    def frequency(events):
        span=int(events[-1]['source_timestamp_ns'])-int(events[0]['source_timestamp_ns']) if len(events)>1 else 0
        return wire(Fraction((len(events)-1)*10**9,span)) if span>0 else None
    value={'schema':'gig.iex.l1.metrics.v1','symbol':symbol,'source':'alpaca/iex','generation':generation,'retained_events':len(rows),'valid_ordered_quotes':len(quotes),'ordered_trade_prints':len(trades),'window_first_source_ns':rows[0]['source_timestamp_ns'] if rows else None,'window_last_capture_source_ns':rows[-1]['source_timestamp_ns'] if rows else None,'contains_correction_or_cancel':corrected,'quote_frequency_per_source_second':frequency(quotes),'trade_frequency_per_source_second':frequency(trades),'units':'price in provider-reported units;size unit unverified;returns dimensionless;rates per source second','method':'Best-quote exact spread/mid/size imbalance;ordered valid observations only;frequency(N-1)/elapsed source time;log-mid quadratic variation over retained window,not annualized','limitations':['Single-venue IEX,not SIP/NBBO/L2/L3','Window is a bounded received prefix,not a complete market tape','Crossed/zero-sided and out-of-order quotes excluded from metrics,retained diagnostically','No exchange calendar,halt authority or aggressor/queue inference','Corrections/cancels suppress unreconciled trade-volume/trajectory metrics','No previous-session close supplied;price change is first-to-last retained valid mid only']}
    if quotes:
        q=quotes[-1]['data'];bid,ask,bs,az=map(Fraction,(q['bid'],q['ask'],q['bid_size'],q['ask_size']));mid=(bid+ask)/2
        mids=[(Fraction(r['data']['bid'])+Fraction(r['data']['ask']))/2 for r in quotes]
        value.update(quote_metric_source_ns=quotes[-1]['source_timestamp_ns'],spread=wire(ask-bid),midprice=wire(mid),relative_spread=wire((ask-bid)/mid),best_quote_size_imbalance=wire((bs-az)/(bs+az)) if bs+az else None,retained_mid_change=wire(mid-mids[0]),retained_mid_return=wire(mid/mids[0]-1),realized_log_mid_volatility=math.sqrt(sum((math.log(b.numerator)-math.log(b.denominator)-math.log(a.numerator)+math.log(a.denominator))**2 for a,b in zip(mids,mids[1:]))) if len(mids)>1 else None)
    else:value.update(quote_metric_source_ns=None,spread=None,midprice=None,relative_spread=None,best_quote_size_imbalance=None,retained_mid_change=None,retained_mid_return=None,realized_log_mid_volatility=None)
    value['observed_trade_size_sum']=wire(sum((Fraction(r['data']['size']) for r in trades),Fraction())) if trades and not corrected else None
    value['trade_price_change']=wire(Fraction(trades[-1]['data']['price'])-Fraction(trades[0]['data']['price'])) if trades and not corrected else None
    return value
