"""Exact descriptive returned-bar analytics,not fitted forecasts or strategy alpha."""
from fractions import Fraction

def describe(bars):
    if not bars:return {'status':'UNAVAILABLE','reason':'accepted_closing_prices_required'}
    closes=[Fraction(r['close']) for r in bars]
    if len(closes)>256 or any(p<=0 for p in closes):raise ValueError('price_research_input')
    returns=[b/a-1 for a,b in zip(closes,closes[1:])]
    def wire(x):
        if x is None:return {'value':None,'reason':'insufficient_return_observations'}
        if max(x.numerator.bit_length(),x.denominator.bit_length())>4096:return {'value':None,'reason':'exact_rational_capacity'}
        return {'value':{'numerator':str(x.numerator),'denominator':str(x.denominator)},'reason':None}
    peak=closes[0];dd=Fraction()
    for close in closes:peak=max(peak,close);dd=max(dd,1-close/peak)
    tail=(len(returns)+19)//20;losses=sorted((-r for r in returns),reverse=True)
    return {'status':'DESCRIPTIVE_ACCEPTED_SOURCE_BARS','return_count':len(returns),'first_timestamp':bars[0]['timestamp'],'last_timestamp':bars[-1]['timestamp'],'total_return':wire(closes[-1]/closes[0]-1),'maximum_close_drawdown':wire(dd),'mean_simple_return':wire(sum(returns)/len(returns) if returns else None),'sum_squared_simple_returns':wire(sum((r*r for r in returns),Fraction()) if returns else None),'historical_var_95':wire(losses[tail-1] if len(returns)>=20 else None),'historical_es_95':wire(sum(losses[:tail])/tail if len(returns)>=20 else None),'methodology':'raw unadjusted returned close-to-close simple returns;95% tail uses worst ceil(5%N);at least20 returns;not annualized,complete history,causal alpha,forecast or portfolio risk'}
