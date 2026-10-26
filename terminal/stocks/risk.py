"""Descriptive risk for validated closing observations,not an investment forecast."""
import math,re
from statistics import NormalDist
from fractions import Fraction


def analyze(bars):
    if not bars:return {'status':'UNAVAILABLE','reason':'validated_bars_required'}
    closes=[Fraction(r['close']) for r in bars]
    if len(closes)>256 or any(v<=0 for v in closes):raise ValueError('risk_input')
    returns=[b/a-1 for a,b in zip(closes,closes[1:])];n=len(returns)
    if n<20:return {'status':'UNAVAILABLE','reason':'at_least20_returns_required','observations':n}
    x=list(map(float,returns));mean=sum(x)/n;variance=sum((v-mean)**2 for v in x)/(n-1);sd=math.sqrt(variance)
    def wire(v):return {'numerator':str(v.numerator),'denominator':str(v.denominator)}
    losses=sorted([-v for v in returns],reverse=True);tail=(n+19)//20
    logs=[math.log1p(float(r)) if float(r)>-1 else math.log(float(b))-math.log(float(a)) for r,a,b in zip(returns,closes,closes[1:])]
    rolling=[]
    for i in range(19,n):
        window=x[i-19:i+1];m=sum(window)/20;rolling.append({'end_timestamp':bars[i+1]['timestamp'],'sample_standard_deviation':math.sqrt(sum((r-m)**2 for r in window)/19)})
    return {'schema':'gig.risk.v1','status':'DESCRIPTIVE_RETURNED_INTERVAL','observations':n,'confidence':'0.95','horizon':'one supplied bar interval;may cross gaps or sessions','units':'fractional return,not currency P&L','historical_var':wire(losses[tail-1]),'historical_expected_shortfall':wire(sum(losses[:tail])/tail),'historical_method':'worst ceil(5%N) simple-return losses;ES same tail;not interpolated population quantile',
            'normal_parametric_var':-mean+NormalDist().inv_cdf(.95)*sd,'normal_method':'Gaussian simple-return loss quantile using sample mean and n-1 variance;negative estimate retained,no tail calibration',
            'sample_return_standard_deviation':sd,'log_returns_approximate':logs,'rolling20':rolling,
            'limitations':['Unadjusted closes;corporate actions/session gaps may dominate','At least20 returns is an engineering gate,not sufficient statistical precision','No portfolio exposure,correlation,position sizing or empirical tail coverage implied']}


def scenarios(quantity,price,shocks):
    if type(quantity) is not str or type(price) is not str or type(shocks) is not list or not 1<=len(shocks)<=16 or any(type(v) is not str for v in shocks):raise ValueError('scenario_input')
    if any(len(v)>32 for v in [quantity,price,*shocks]):raise ValueError('scenario_budget')
    if any(not re.fullmatch(r'-?\d{1,12}(?:\.\d{1,12})?',v) for v in [quantity,price,*shocks]):raise ValueError('scenario_decimal')
    q,p=Fraction(quantity),Fraction(price);s=[Fraction(v) for v in shocks]
    if abs(q)>10**9 or not 0<p<=10**9 or any(v < -1 or v > 10 for v in s):raise ValueError('scenario_range')
    def wire(v):return {'numerator':str(v.numerator),'denominator':str(v.denominator)}
    return {'schema':'gig.scenarios.v1','classification':'USER_ASSUMPTIONS_NOT_OBSERVED_POSITIONS','exposure':wire(q*p),'currency':'user-price currency;not inferred USD','cases':[{'shock':wire(v),'linear_pnl':wire(q*p*v)} for v in s],'limitations':['Linear single-asset exposure only;no options convexity,liquidity,margin or cross-asset correlation']}
