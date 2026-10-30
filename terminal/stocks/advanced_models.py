"""Deterministic constrained conditional GARCH optimization;fixed missing-data HMM inference."""
import hashlib,json,math
from .models import observations,fit_garch,garch_likelihood,fit_hmm,normalized_weights,logsum

def optimize_garch(values):
    x=observations(values);base=fit_garch(x)
    if not base['fitted']:return {'schema':'gig.garch.optimization.v1','status':'UNIDENTIFIABLE_CONSTANT_SAMPLE','fitted':False}
    variance=sum((r-base['mean'])**2 for r in x)/len(x)
    # omega>0,alpha>=0,beta>=0,alpha+beta<.995 by simplex softmax.
    def decode(v):
        probs=normalized_weights([v[1],v[2],0.]);return math.exp(v[0]),.995*probs[0],.995*probs[1]
    def score(v):
        omega,a,b=decode(v);return garch_likelihood(x,base['mean'],omega,a,b,variance)
    slack=.995-base['alpha']-base['beta'];v=[math.log(base['omega']),math.log(max(base['alpha'],1e-9)/slack),math.log(max(base['beta'],1e-9)/slack)]
    current=score(v);evaluations=1;trace=[current[0]];step=1.;converged=False
    for iteration in range(120):
        best=current;chosen=v
        for axis in range(3):
            for sign in (-1,1):
                candidate=v.copy();candidate[axis]=max(-50.,min(40.,v[axis]+sign*step));result=score(candidate);evaluations+=1
                if result[0]>best[0]+1e-10:best=result;chosen=candidate
        if chosen is v:
            step*=.5
            if step<1e-5:converged=True;break
        else:v=chosen;current=best;trace.append(current[0])
    omega,a,b=decode(v)
    # Boundary grid candidate retained if an interior start cannot improve it.
    improved=current[0]>=base['log_likelihood']
    chosen={'omega':omega,'alpha':a,'beta':b,'log_likelihood':current[0],'next_variance':current[2]} if improved else {k:base[k] for k in ('omega','alpha','beta','log_likelihood','next_variance')}
    return {'schema':'gig.garch.optimization.v1','status':'BOUNDED_CONDITIONAL_LIKELIHOOD_SEARCH','fitted':True,**chosen,'mean':base['mean'],'initial_variance':variance,'iterations':iteration+1,'evaluations':evaluations,'likelihood_trace':trace,'converged':converged,'stop_reason':'step_tolerance' if converged else 'iteration_budget','selected_candidate':'interior_search' if improved else 'boundary_grid_baseline','grid_baseline_log_likelihood':base['log_likelihood'],'dataset_sha256':hashlib.sha256(json.dumps(values,separators=(',',':')).encode()).hexdigest(),'method':'Deterministic coordinate pattern search in log-omega/softmax-simplex coefficients;sample mean and initial variance fixed;omega>0,alpha+beta<.995;grid boundary retained','uncertainty':'No Hessian/parameter confidence interval;no global MLE or predictive superiority claim'}

def missing_hmm(values,means,variances,transition,prior):
    if type(values) is not list or not 1<=len(values)<=256:raise ValueError('hmm_missing_budget')
    if any(type(v)not in (list,tuple)or len(v)!=2 for v in (means,variances,prior,transition)) or any(type(row)not in (list,tuple)or len(row)!=2 for row in transition):raise ValueError('hmm_parameters')
    if any(type(v) not in (int,float) or abs(v)>1.7976931348623157e308 or not math.isfinite(v) for v in [*means,*variances,*prior,*(v for row in transition for v in row)]):raise ValueError('hmm_finite_parameters')
    if min(variances)<=0 or min(prior)<=0 or abs(sum(prior)-1)>1e-12 or any(min(row)<=0 or abs(sum(row)-1)>1e-12 for row in transition):raise ValueError('hmm_probability_parameters')
    result=[];p=list(prior);likelihood=0.
    for i,v in enumerate(values):
        if i:p=[sum(p[k]*transition[k][j] for k in range(2)) for j in range(2)]
        if v is not None:
            r=observations([v]*20)[0];terms=[]
            for j in range(2):
                standardized=(r-means[j])/math.sqrt(variances[j])
                # Separate logs avoid overflowing2*pi*variance;scaled products can
                # represent a negligible state as-inf without raising **2 overflow.
                terms.append((math.log(p[j])if p[j]>0 else -math.inf)-.5*(math.log(2*math.pi)+math.log(variances[j])+standardized*standardized))
            if not any(math.isfinite(t)for t in terms):raise ValueError('hmm_likelihood_capacity')
            likelihood+=logsum(terms)
            if not math.isfinite(likelihood):raise ValueError('hmm_likelihood_capacity')
            p=normalized_weights(terms)
        result.append({'probabilities':p.copy(),'observed':v is not None})
    return {'states':result,'observed_log_likelihood':likelihood,'method':'Fixed-parameter filtering;missing emission integrated out with likelihood1;transition still advances;no imputation or missing-data parameter estimation'}
