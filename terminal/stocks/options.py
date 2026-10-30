"""European Black–Scholes scenario analytics. Never an observed options chain."""
import datetime,math,re

MIN_PRICE=1e-6
MAX_PRICE=1e7

def finite(x,lo,hi):
    if type(x) not in (int,float) or not lo<=x<=hi or not math.isfinite(x):raise ValueError('model_parameter')
    return float(x)

def contract(code):
    if type(code) is not str:raise ValueError('option_identity')
    m=re.fullmatch(r'([A-Z]{1,6}) {0,5}(\d{6})([CP])(\d{8})',code)
    if not m:raise ValueError('option_identity')
    expiry=datetime.date(2000+int(m[2][:2]),int(m[2][2:4]),int(m[2][4:6]))
    strike=int(m[4])
    if not strike:raise ValueError('option_strike')
    return {'underlying':m[1],'expiration':expiry.isoformat(),'right':'call' if m[3]=='C' else 'put','strike_millis':str(strike),'authority':'parsed OCC-shaped identifier;listing and deliverable not verified'}

def price(spot,strike,years,volatility,rate=0.,dividend=0.,right='call'):
    s=finite(spot,MIN_PRICE,MAX_PRICE);k=finite(strike,MIN_PRICE,MAX_PRICE);t=finite(years,1e-6,10);v=finite(volatility,1e-6,5);r=finite(rate,-.5,.5);q=finite(dividend,-.5,.5)
    if right not in ('call','put'):raise ValueError('option_right')
    root=math.sqrt(t);d1=(math.log(s/k)+(r-q+v*v/2)*t)/(v*root);d2=d1-v*root
    cdf=lambda x:.5*math.erfc(-x/math.sqrt(2));pdf=math.exp(-d1*d1/2)/math.sqrt(2*math.pi)
    sd=s*math.exp(-q*t);kd=k*math.exp(-r*t);sign=1 if right=='call' else -1
    p=sign*(sd*cdf(sign*d1)-kd*cdf(sign*d2))
    delta=sign*math.exp(-q*t)*cdf(sign*d1);gamma=math.exp(-q*t)*pdf/(s*v*root)
    theta=-sd*pdf*v/(2*root)+sign*q*sd*cdf(sign*d1)-sign*r*kd*cdf(sign*d2)
    return {'price':max(0.,p),'delta':delta,'gamma':gamma,'vega':sd*pdf*root,'theta_per_year':theta,'rho':sign*k*t*math.exp(-r*t)*cdf(sign*d2)}

def implied(target,spot,strike,years,rate=0.,dividend=0.,right='call'):
    target=finite(target,0,1e9)
    low,high=1e-6,5.
    minimum=price(spot,strike,years,low,rate,dividend,right)['price'];maximum=price(spot,strike,years,high,rate,dividend,right)['price']
    if not minimum+1e-10<target<maximum-1e-10:raise ValueError('iv_unidentifiable_or_outside_bracket')
    for _ in range(100):
        middle=(low+high)/2;p=price(spot,strike,years,middle,rate,dividend,right)['price']
        if p<target:low=middle
        else:high=middle
    return (low+high)/2

def scenario(config):
    allowed={'spot','strike','years','volatility','rate','dividend','right','target_price'}
    if type(config) is not dict or set(config)-allowed:raise ValueError('option_parameters')
    args={k:config[k] for k in ('spot','strike','years','volatility','rate','dividend','right') if k in config}
    for k in ('spot','strike','years','volatility'):
        if k not in args:raise ValueError('option_parameters')
    # The base domain is exactly price()'s domain. An optional display grid must
    # never invalidate a valid base scenario or silently clip a derived strike.
    metrics=price(**args);surface=[];unavailable=0
    for i in range(9):
        maturity=.05+i*.11875;row=[]
        for j in range(17):
            strike=args['spot']*(.6+j*.05)
            point={'strike':strike,'years':maturity,'volatility':args['volatility']}
            if MIN_PRICE<=strike<=MAX_PRICE:
                point['theoretical_price']=price(**{**args,'strike':strike,'years':maturity})['price']
            else:
                point.update(theoretical_price=None,reason='derived_strike_outside_price_domain')
                unavailable+=1
            row.append(point)
        surface.append(row)
    iv=implied(config['target_price'],args['spot'],args['strike'],args['years'],args.get('rate',0),args.get('dividend',0),args.get('right','call')) if 'target_price' in config else None
    return {'classification':'THEORETICAL_SCENARIO','model':'European Black–Scholes,continuous rate/dividend,constant volatility','metrics':metrics,'implied_volatility':iv,'surface':surface,'surface_coverage':{'schema':'gig.options.grid.v2','total':153,'available':153-unavailable,'unavailable':unavailable,'policy':'Out-of-domain derived strikes retain their coordinates and null price;no clipping or base-metric invalidation'},'surface_scope':'flat input volatility grid;not observed smile/chain or calibrated market surface','greek_units':'vega per1.0 volatility,rho per1.0 rate,theta per year;spot/strike same currency','limitations':['American exercise,discrete dividends and market frictions excluded','No observed quote,open interest,listing or tradable contract claim','Floating-point model approximation;not exact engine monetary arithmetic']}
