"""Exact aligned-input constant-weight portfolio research;no inferred holdings."""
import hashlib,json,math,re
from fractions import Fraction
from statistics import NormalDist


def number(v):
    if type(v) is not str or not re.fullmatch(r'-?\d{1,3}(?:\.\d{1,12})?',v):raise ValueError('portfolio_decimal')
    return Fraction(v)


def analyze(data,*,_rational=False):
    def parse(v):
        if not _rational:return number(v)
        if type(v) is not str or not re.fullmatch(r'-?\d{1,80}/[1-9]\d{0,79}',v):raise ValueError('portfolio_exact_rational')
        return Fraction(v)

    if type(data) is not dict or set(data)-{'assets','weights','horizon','shocks'} or not {'assets','weights'}<=set(data):raise ValueError('portfolio_fields')
    assets=data['assets'];weights=data['weights']
    if type(assets) is not dict or not 1<=len(assets)<=4 or type(weights) is not dict or set(weights)!=set(assets) or any(not re.fullmatch('[A-Z][A-Z0-9_]{0,7}',k) for k in assets):raise ValueError('portfolio_identity')
    names=sorted(assets);n=None;series=[]
    for name in names:
        values=assets[name]
        if type(values) is not list or not 20<=len(values)<=64 or (n is not None and n!=len(values)):raise ValueError('portfolio_alignment')
        n=len(values);row=[parse(v) for v in values]
        if any(abs(v)>1 for v in row):raise ValueError('portfolio_return_range')
        series.append(row)
    w=[number(weights[k]) for k in names];gross=sum(map(abs,w))
    if sum(w)!=1 or gross>3:raise ValueError('portfolio_weights_net1_gross3_required')
    horizon=data.get('horizon','one user-supplied aligned interval')
    if type(horizon) is not str or not 1<=len(horizon)<=80 or any(ord(c)<32 for c in horizon):raise ValueError('portfolio_horizon')
    mean=[sum(row)/n for row in series]
    cov=[[sum((a-mean[i])*(b-mean[j]) for a,b in zip(series[i],series[j]))/(n-1) for j in range(len(names))] for i in range(len(names))]
    portfolio=[sum(w[j]*series[j][i] for j in range(len(names))) for i in range(n)];mu=sum(portfolio)/n
    variance=sum((r-mu)**2 for r in portfolio)/(n-1)
    if variance!=sum(w[i]*w[j]*cov[i][j] for i in range(len(names)) for j in range(len(names))):raise ValueError('portfolio_covariance_invariant')
    sd=math.sqrt(float(variance));z=NormalDist().inv_cdf(.95);losses=sorted([-v for v in portfolio],reverse=True);tail=(n+19)//20
    def wire(v):return {'numerator':str(v.numerator),'denominator':str(v.denominator)} if max(v.numerator.bit_length(),v.denominator.bit_length())<=4096 else None
    corr=[[max(-1.,min(1.,float(cov[i][j])/math.sqrt(float(cov[i][i]*cov[j][j])))) if cov[i][i] and cov[j][j] else None for j in range(len(names))] for i in range(len(names))]
    wealth=Fraction(1);peak=wealth;drawdown=Fraction();dd_reason=None
    for r in portfolio:
        wealth*=1+r
        if wealth<=0:dd_reason='non_positive_rebalanced_wealth_under_leverage';break
        peak=max(peak,wealth);drawdown=max(drawdown,1-wealth/peak)
    dd=None if dd_reason else wire(drawdown)
    if dd is None and dd_reason is None:dd_reason='exact_rational_capacity'
    shocks=data.get('shocks',[])
    if type(shocks) is not list or len(shocks)>8:raise ValueError('portfolio_shock_budget')
    scenarios=[]
    for shock in shocks:
        if type(shock) is not dict or set(shock)!=set(names):raise ValueError('portfolio_shock_alignment')
        v=[number(shock[k]) for k in names]
        if any(r < -1 or r > 10 for r in v):raise ValueError('portfolio_shock_range')
        scenarios.append({'weighted_return':wire(sum(a*b for a,b in zip(w,v))),'supplied_asset_shocks':shock})
    canonical=lambda x:hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    dataset=canonical({'assets':assets,'horizon':horizon})
    rolling=[]
    for i in range(19,n):
        row=portfolio[i-19:i+1];m=sum(row)/20;rolling.append({'end_index':i,'sample_standard_deviation':math.sqrt(float(sum((v-m)**2 for v in row)/19))})
    return {'schema':'gig.portfolio.v1','classification':'USER_SUPPLIED_RESEARCH_INPUT_NOT_VERIFIED_OBSERVATIONS','dataset_sha256':dataset,'analysis_sha256':canonical(data),'assets':names,'weights':[wire(v) for v in w],'observations':n,'confidence':'0.95','horizon':horizon,'units':'fraction of portfolio equity per supplied interval;not currency P&L','net_exposure':wire(sum(w)),'gross_exposure':wire(gross),'portfolio_returns':[wire(v) for v in portfolio],'sample_covariance':[[wire(v) for v in row] for row in cov],'correlation_approximate':corr,'historical_var':wire(losses[tail-1]),'historical_es':wire(sum(losses[:tail])/tail),'gaussian_var':-float(mu)+z*sd,'gaussian_es':-float(mu)+math.exp(-z*z/2)/math.sqrt(2*math.pi)/.05*sd,'maximum_drawdown':dd,'drawdown_reason':dd_reason,'rolling20':rolling,'scenarios':scenarios,'method':'Constant weights rebalanced each aligned interval;sample n-1 covariance;historical worst ceil(5%N) losses/ES;Gaussian sample-mean/covariance tail;confidence.95','limitations':['Caller declares aligned observations;no timestamps/point-in-time authority inferred','No missing-value imputation;unmatched lengths rejected;zero variance correlation undefined','No actual holdings inferred from stock selection;borrowing,transaction costs and liquidity omitted','Small in-sample empirical tails and Gaussian assumptions are not calibrated forecasts','Long compounded paths may exceed4096-bit display capacity;not silently rounded']}
