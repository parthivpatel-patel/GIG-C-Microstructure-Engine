"""Bounded deterministic diagnostic fits;no empirical forecasting claim."""
import math,re


def observations(values):
    if type(values) is not list or not 20<=len(values)<=256 or any(type(v) is not str or not re.fullmatch(r'-?(?:0|1)(?:\.\d{1,12})?',v) for v in values):raise ValueError('model_sample')
    x=[float(v) for v in values]
    if any(not math.isfinite(v) or abs(v)>1 for v in x):raise ValueError('model_range')
    return x


def logsum(v):
    m=max(v);return m+math.log(sum(math.exp(a-m) for a in v))


def normalized_weights(values):
    maximum=max(values);weights=[math.exp(v-maximum) for v in values];total=sum(weights)
    return [v/total for v in weights]


def hmm_filter(x,means,variances,transition,prior):
    n=len(x);emission=[[-.5*(math.log(2*math.pi*variances[j])+(r-means[j])**2/variances[j]) for j in range(2)] for r in x]
    forward=[[math.log(prior[j])+emission[0][j] for j in range(2)]]
    for i in range(1,n):forward.append([emission[i][j]+logsum([forward[-1][k]+math.log(transition[k][j]) for k in range(2)]) for j in range(2)])
    ll=logsum(forward[-1]);probabilities=[]
    for row in forward:
        probabilities.append(normalized_weights(row))
    return ll,probabilities,forward,emission


def fit_hmm(x,max_iterations=40):
    mean=sum(x)/len(x);variance=sum((v-mean)**2 for v in x)/len(x)
    if variance<1e-14:return {'status':'UNIDENTIFIABLE_CONSTANT_SAMPLE','fitted':False}
    means=[mean-math.sqrt(variance)*.5,mean+math.sqrt(variance)*.5];variances=[variance,variance];a=[[.9,.1],[.1,.9]];prior=[.5,.5]
    trace=[];converged=False;reason='iteration_budget'
    ll,filtered,forward,emission=hmm_filter(x,means,variances,a,prior);trace.append(ll)
    for _ in range(max_iterations):
        backward=[[0.,0.] for _ in x]
        for i in range(len(x)-2,-1,-1):backward[i]=[logsum([math.log(a[j][k])+emission[i+1][k]+backward[i+1][k] for k in range(2)]) for j in range(2)]
        gamma=[]
        for f,b in zip(forward,backward):
            row=[f[j]+b[j] for j in range(2)];gamma.append(normalized_weights(row))
        counts=[[0.,0.],[0.,0.]]
        for i in range(len(x)-1):
            terms=[[forward[i][j]+math.log(a[j][k])+emission[i+1][k]+backward[i+1][k] for k in range(2)] for j in range(2)]
            weights=normalized_weights([v for row in terms for v in row])
            for j in range(2):
                for k in range(2):counts[j][k]+=weights[j*2+k]
        weights=[sum(g[j] for g in gamma) for j in range(2)]
        if min(weights)<1e-10:reason='collapsed_state';break
        next_means=[sum(g[j]*v for g,v in zip(gamma,x))/weights[j] for j in range(2)]
        next_vars=[max(1e-12,sum(g[j]*(v-next_means[j])**2 for g,v in zip(gamma,x))/weights[j]) for j in range(2)]
        if any(sum(row)<1e-12 for row in counts):reason='collapsed_transition_row';break
        next_a=[]
        for row in counts:
            p=min(1-1e-6,max(1e-6,row[0]/sum(row)));next_a.append([p,1-p])
        p=min(1-1e-6,max(1e-6,gamma[0][0]));next_prior=[p,1-p]
        updated=hmm_filter(x,next_means,next_vars,next_a,next_prior);new_ll=updated[0]
        if new_ll<ll-1e-8:reason='constrained_update_not_improving';break
        improvement=new_ll-ll;means,variances,a,prior=next_means,next_vars,next_a,next_prior
        ll,filtered,forward,emission=updated;trace.append(ll)
        if abs(improvement)<=1e-7*max(1,abs(ll)):converged=True;reason='relative_likelihood_tolerance';break
    return {'status':'DIAGNOSTIC_FIT','fitted':True,'method':'two-state Gaussian Baum-Welch;deterministic initialization;variance/transition floors;local optimum only',
            'means':means,'variances':variances,'transition':a,'initial_probabilities':prior,'filtered_probabilities':filtered,
            'log_likelihood':ll,'likelihood_trace':trace,'iterations':len(trace)-1,'converged':converged,'stop_reason':reason,
            'warning':'Parameters fitted using the entire supplied sample;historical filtered probabilities therefore have parameter-estimation look-ahead. Not an out-of-sample trading signal.'}


def garch_likelihood(x,mean,omega,alpha,beta,initial):
    h=initial;ll=0.;path=[]
    for r in x:
        path.append(h);ll+=-.5*(math.log(2*math.pi*h)+(r-mean)**2/h);h=omega+alpha*(r-mean)**2+beta*h
    return ll,path,h


def fit_garch(x):
    mean=sum(x)/len(x);variance=sum((r-mean)**2 for r in x)/len(x)
    if variance<1e-14:return {'status':'UNIDENTIFIABLE_CONSTANT_SAMPLE','fitted':False}
    baseline=garch_likelihood(x,mean,variance,0,0,variance);best=(baseline[0],variance,0.,0.,baseline)
    candidates=1
    for alpha in (.02,.08,.15):
        for beta in (.7,.85,.93):
            if alpha+beta>=.995:continue
            for scale in (.5,1.,2.):
                omega=max(1e-12,variance*(1-alpha-beta)*scale);result=garch_likelihood(x,mean,omega,alpha,beta,variance);candidates+=1
                if result[0]>best[0]:best=(result[0],omega,alpha,beta,result)
    ll,omega,alpha,beta,result=best
    return {'status':'BOUNDED_GRID_FIT','fitted':True,'method':'finite Gaussian GARCH(1,1) likelihood grid;sample mean/initial variance;constant-variance baseline included',
            'mean':mean,'omega':omega,'alpha':alpha,'beta':beta,'conditional_variance':result[1],'next_variance':result[2],
            'log_likelihood':ll,'constant_variance_log_likelihood':baseline[0],'evaluated_candidates':candidates,
            'convergence':'finite_grid_exhausted_not_continuous_optimizer_convergence','warning':'In-sample discrete fit and conditional next-variance calculation;no predictive accuracy,parameter uncertainty or global MLE claim'}


def kalman(x):
    if type(x) is not list or not 1<=len(x)<=256 or any(v is not None and (type(v) not in (int,float) or not math.isfinite(v) or abs(v)>1) for v in x):raise ValueError('kalman_input')
    mean=0.;p=1.;rows=[]
    for value in x:
        predicted=p+1e-5
        if value is None:mean_next=mean;p=predicted;gain=None
        else:gain=predicted/(predicted+.001);mean_next=mean+gain*(value-mean);p=(1-gain)**2*predicted+gain**2*.001
        mean=mean_next;rows.append({'estimate':mean,'variance':p,'gain':gain,'observed':value is not None})
    return {'method':'scalar local-level filter;Joseph covariance update;fixed Q=1e-5,R=.001;not fitted','states':rows}


def fit(values):
    x=observations(values)
    return {'schema':'gig.models.v1','classification':'USER_AUTHORED_RESEARCH_INPUT','observations':len(x),
            'hmm':fit_hmm(x),'garch':fit_garch(x),'kalman':kalman(x),
            'limitations':['In-sample numerical diagnostics,not statistically or empirically validated forecasts','No out-of-sample comparison,transaction-cost study or model selection adjustment']}
