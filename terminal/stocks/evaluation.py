"""Chronological authored-input likelihood evaluation with training-only fitting."""
import hashlib,json,math
from .models import observations,fit_hmm,fit_garch,hmm_filter,garch_likelihood


def evaluate(values,train_end,validation_end):
    x=observations(values)
    if type(train_end) is not int or type(validation_end) is not int or not 20<=train_end<validation_end<len(x) or validation_end-train_end<5 or len(x)-validation_end<5:raise ValueError('evaluation_split')
    train=x[:train_end];valid=x[train_end:validation_end];test=x[validation_end:]
    h=fit_hmm(train);g=fit_garch(train)
    if not h['fitted'] or not g['fitted']:return {'schema':'gig.evaluation.v1','status':'UNIDENTIFIABLE_TRAINING_SAMPLE','classification':'USER_SUPPLIED_ORDERED_RETURNS_NOT_POINT_IN_TIME_VERIFIED'}
    ll,posterior,_,_=hmm_filter(train,h['means'],h['variances'],h['transition'],h['initial_probabilities'])
    def advance(prior,rows):
        predicted=[sum(prior[i]*h['transition'][i][j] for i in range(2)) for j in range(2)]
        score,post,_,_=hmm_filter(rows,h['means'],h['variances'],h['transition'],predicted)
        return score,post[-1]
    v_h,post=advance(posterior[-1],valid);t_h,_=advance(post,test)
    v_g,_,nextv=garch_likelihood(valid,g['mean'],g['omega'],g['alpha'],g['beta'],g['next_variance'])
    t_g,_,_=garch_likelihood(test,g['mean'],g['omega'],g['alpha'],g['beta'],nextv)
    variance=sum((r-g['mean'])**2 for r in train)/len(train)
    baseline=lambda rows:sum(-.5*(math.log(2*math.pi*variance)+(r-g['mean'])**2/variance) for r in rows)
    sha=lambda v:hashlib.sha256(json.dumps(v,separators=(',',':')).encode()).hexdigest()
    forecasts=[g['next_variance']]
    for _ in range(4):forecasts.append(g['omega']+(g['alpha']+g['beta'])*forecasts[-1])
    parameters={'hmm':{k:h[k] for k in ('means','variances','transition','initial_probabilities','converged','iterations')},'garch':{k:g[k] for k in ('mean','omega','alpha','beta','convergence')}}
    return {'schema':'gig.evaluation.v1','status':'SCORED_CHRONOLOGICAL_HOLDOUTS','classification':'USER_SUPPLIED_ORDERED_RETURNS_NOT_POINT_IN_TIME_VERIFIED','dataset_sha256':sha(values),'training_sha256':sha(values[:train_end]),'configuration_sha256':sha(parameters),'splits':{'training':[0,train_end],'validation':[train_end,validation_end],'test':[validation_end,len(x)]},'parameters':parameters,'validation_log_likelihood':{'hmm':v_h,'garch':v_g,'constant_gaussian':baseline(valid)},'test_log_likelihood':{'hmm':t_h,'garch':t_g,'constant_gaussian':baseline(test)},'garch_training_conditional_variance_horizons1to5':forecasts,'method':'Fit once on training only;validation observations update filtering/variance state but never fitted parameters;test then conditioned on past observations','uncertainty':'No confidence interval or predictive significance established;not model-selection or observed-market validation','limitations':['Array order is caller-declared;no independently authenticated timestamps or filing vintages','No missing observations dropped/imputed;invalid inputs rejected','No rolling refits or broad hyperparameter search;GARCH remains a finite-grid fit','Deterministic initialization,no random seed used by estimators']}


def walk_forward(values):
    observations(values)
    if len(values)<30:raise ValueError('walk_forward_sample')
    folds=[]
    for cut in range(20,min(len(values)-9,40),5):
        result=evaluate(values[:cut+10],cut,cut+5)
        folds.append({'training_end':cut,'validation_end':cut+5,'test_end':cut+10,'result':result})
    covered=folds[-1]['test_end']
    return {'schema':'gig.evaluation.v1','status':'BOUNDED_EXPANDING_WINDOW_EVALUATION','classification':'USER_SUPPLIED_ORDERED_RETURNS_NOT_POINT_IN_TIME_VERIFIED','folds':folds,'source_observations':len(values),'unused_suffix_observations':len(values)-covered,'method':'Expanding training from20 observations;5 validation then5 nonoverlapping test observations;refit each fold;maximum4 folds','uncertainty':'Fold scores are dependent and no predictive significance/confidence interval is claimed','dataset_sha256':hashlib.sha256(json.dumps(values,separators=(',',':')).encode()).hexdigest()}
