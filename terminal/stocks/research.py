"""Bounded transparent fixed-parameter models and causal authored backtest references."""
import math,re
from fractions import Fraction

def analyze(values):
    if type(values) is not list or not 20<=len(values)<=256 or any(type(v) is not str or not re.fullmatch(r'-?(?:0|1)(?:\.\d{1,12})?',v) for v in values):raise ValueError('research_sample_budget')
    exact=[Fraction(v) for v in values]
    if any(abs(v)>1 for v in exact):raise ValueError('research_return_range')
    x=list(map(float,exact));losses=sorted([-r for r in exact],reverse=True);tail=(len(x)+19)//20
    var=losses[tail-1];es=sum(losses[:tail])/tail
    # Fixed declared coefficients, no claimed fit or predictive performance.
    variance=.0001;garch=[];mean=0.;covariance=1.;filtered=[];prob=[.5,.5];regimes=[]
    def density(y,mu,sigma):return math.exp(-.5*((y-mu)/sigma)**2)/(sigma*math.sqrt(2*math.pi))
    for r in x:
        garch.append(variance);variance=1e-6+.08*r*r+.90*variance
        covariance+=1e-5;gain=covariance/(covariance+.001);mean+=gain*(r-mean);covariance*=1-gain;filtered.append(mean)
        prior=[.95*prob[0]+.05*prob[1],.05*prob[0]+.95*prob[1]]
        likelihood=[density(r,0,.01),density(r,0,.05)];weight=[prior[i]*likelihood[i] for i in range(2)];total=sum(weight)
        if not total:raise ValueError('hmm_likelihood_underflow')
        prob=[a/total for a in weight];regimes.append(prob[1])
    wealth=Fraction(1);position=0;cost=Fraction(1,10000);trades=0;curve=[];positions=[]
    for i,r in enumerate(exact):
        # Only returns strictly before i determine the next exposed position.
        next_position=int(i>=5 and sum(exact[i-5:i])>0)
        turnover=abs(next_position-position);trades+=turnover
        wealth*=1+next_position*r-turnover*cost
        position=next_position;positions.append(position);curve.append(float(wealth))
    wire=lambda f:{'numerator':str(f.numerator),'denominator':str(f.denominator)}
    return {'classification':'USER_AUTHORED_RESEARCH_INPUT','count':len(x),'historical_risk':{'confidence':'0.95','tail_count':tail,'var':wire(var),'expected_shortfall':wire(es),'method':'worst ceil(5%N) loss order statistics;ES mean of same tail;no distributional guarantee'},'kalman':{'filtered_mean':filtered,'measurement_variance':.001,'process_variance':1e-5,'initial_mean':0,'initial_covariance':1},'garch':{'one_step_variance':garch,'omega':1e-6,'alpha':.08,'beta':.90,'initial_variance':.0001,'fitted':False},'hmm':{'high_volatility_probability':regimes,'transition':[[.95,.05],[.05,.95]],'means':[0,0],'standard_deviations':[.01,.05],'initial_probability':[.5,.5],'fitted':False,'filter_only_no_future_smoothing':True},'strategy':{'equity_curve':curve,'positions':positions,'terminal_wealth':wire(wealth),'turnover_units':trades,'cost_per_turnover':'0.0001','end_liquidation':False,'cost_model':'linear turnover only;no spread,impact or fills','rule':'long if preceding5 returns sum positive,else flat;current return never used in signal','validation':'causal rolling evaluation,fixed rule;not model-selection walk-forward or empirical alpha'},'limitations':['No observed price ingestion implied by this endpoint','Small empirical tails are unstable','No calibrated forecasts,portfolio correlations or execution-fill model','No guarantee of positive wealth for extreme authored returns']}
