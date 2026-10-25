"""Bounded display-cadence research, exact Fraction arithmetic; never book-transition logic.

All ordering is source capture order on one declared receive-monotonic clock.
This module does not infer exchange-time causality, order identity or cancellations.
"""
from collections import deque
from decimal import Decimal,localcontext
from fractions import Fraction

LIMIT=128
BITS=1024

def unit(text,maximum):
    if type(text) is not str or len(text)>20 or not text.isascii() or not text.isdecimal() or text.startswith('0'):
        raise ValueError('research_exact_unit')
    value=int(text)
    if value>maximum:raise ValueError('research_exact_unit')
    return value

def bounded(value):
    value=Fraction(value)
    if value.numerator.bit_length()>BITS or value.denominator.bit_length()>BITS:raise ArithmeticError('exact_capacity')
    return value

def wire(value):
    value=bounded(value)
    return {'numerator':str(value.numerator),'denominator':str(value.denominator)}

def field(calculation,reason='insufficient_observations'):
    try:
        value=calculation()
        return {'value':None,'reason':reason} if value is None else {'value':wire(value),'reason':None}
    except (ArithmeticError,ValueError):return {'value':None,'reason':'exact_capacity_or_invalid_denominator'}

class ResearchWindow:
    def __init__(self,*,window_ns=10_000_000_000,aggressor_side_confirmed=False):
        if type(window_ns) is not int or not 1<=window_ns<=60_000_000_000:raise ValueError('research_window')
        self.window=window_ns;self.aggressor=aggressor_side_confirmed
        self.quotes=deque(maxlen=LIMIT);self.trades=deque(maxlen=LIMIT)
        self.last_time=None;self.last_ordinal=None;self.started=None
        self.quote_dropped=self.trade_dropped=None
    def observe(self,receipt,native,now,ordinal):
        if type(now) is not int or now<0 or type(ordinal) is not int or ordinal<0:raise ValueError('research_identity')
        if self.last_time is not None and (now<self.last_time or ordinal<=self.last_ordinal):raise ValueError('research_order')
        kind=receipt.get('kind')
        if kind not in ('snapshot','update','trades'):return
        if kind in ('snapshot','update'):
            sides=[]
            for side in ('bids','asks'):
                levels=native[side]
                if len(levels)>32:raise ValueError('research_depth_budget')
                mapping={}
                for x in levels:
                    p,q=unit(x['price_ticks'],2**63-1),unit(x['quantity'],2**64-1)
                    if not 0<p<=2**63-1 or not 0<q<=2**64-1 or p in mapping:raise ValueError('research_level')
                    mapping[p]=q
                sides.append(mapping)
            quote={'time':now,'ordinal':ordinal,'bids':sides[0],'asks':sides[1]}
            if kind=='snapshot':
                self.quotes.clear();self.trades.clear();self.quote_dropped=self.trade_dropped=None;self.started=now
            if len(self.quotes)==LIMIT:self.quote_dropped=self.quotes[0]['time']
            self.quotes.append(quote)
        else:
            batch=receipt.get('trades')
            if type(batch) is not list or len(batch)>100:raise ValueError('research_trade_budget')
            # Initial historical trade snapshots are not received-interval arrivals.
            if receipt.get('historical_snapshot'):return
            prior=self.quotes[-1] if self.quotes else None
            midpoint=self.mid(prior)
            if prior is None or now-prior['time']>10_000_000_000:midpoint=None
            candidates=[]
            for t in batch:
                p,q=unit(t['price_ticks'],2**63-1),unit(t['quantity'],2**64-1)
                if not 0<p<=2**63-1 or not 0<q<=2**64-1 or t['side'] not in ('buy','sell'):raise ValueError('research_trade')
                candidates.append({'time':now,'ordinal':ordinal,'price':p,'quantity':q,'side':t['side'],'prior_midpoint':midpoint})
            for t in candidates:
                if len(self.trades)==LIMIT:self.trade_dropped=self.trades[0]['time']
                self.trades.append(t)
        self.last_time,self.last_ordinal=now,ordinal
    @staticmethod
    def top(q):
        if q and q['bids'] and q['asks']:
            b,a=max(q['bids']),min(q['asks'])
            if b<=a:return b,a,q['bids'][b],q['asks'][a]
        return None
    @classmethod
    def mid(cls,q):
        top=cls.top(q)
        return Fraction(top[0]+top[1],2) if top else None
    def view(self,now):
        if type(now) is not int or now<0 or (self.last_time is not None and now<self.last_time):raise ValueError('research_future_observation')
        start=max(self.started if self.started is not None else now,now-self.window)
        quotes=list(self.quotes);anchor=[q for q in quotes if q['time']<=start]
        selected=([q for q in quotes if q['time']>=start] if start==self.started else ([anchor[-1]] if anchor else [])+[q for q in quotes if q['time']>start])
        trades=[t for t in self.trades if t['time']>=start]
        complete_quotes=self.quote_dropped is None or self.quote_dropped<start
        complete_trades=self.trade_dropped is None or self.trade_dropped<start
        elapsed=now-start;latest=quotes[-1] if quotes else None;top=self.top(latest)
        def ofi():
            if not complete_quotes or len(selected)<2:return None
            total=0
            for previous,current in zip(selected,selected[1:]):
                old,new=self.top(previous),self.top(current)
                if not old or not new:return None
                b0,a0,qb0,qa0=old;b,a,qb,qa=new
                total+=(qb if b>=b0 else 0)-(qb0 if b<=b0 else 0)-(qa if a<=a0 else 0)+(qa0 if a>=a0 else 0)
            return total
        def dynamics(increase):
            if not complete_quotes or len(selected)<2:return None
            total=0
            for old,new in zip(selected,selected[1:]):
                for side in ('bids','asks'):
                    for price in old[side].keys()&new[side].keys():
                        change=new[side][price]-old[side][price]
                        total+=max(0,change if increase else -change)
            return total
        def variance():
            if not complete_quotes or len(selected)<2:return None
            total=Fraction(0)
            for old,new in zip(selected,selected[1:]):
                a,b=self.mid(old),self.mid(new)
                if a is None or b is None:return None
                r=bounded(b/a-1);total=bounded(total+bounded(r*r))
            return total
        def effective():
            if not self.aggressor or not complete_trades or not trades:return None
            total=Fraction(0);qty=0
            for t in trades:
                if t['prior_midpoint'] is None:return None
                sign=1 if t['side']=='buy' else -1
                total=bounded(total+bounded(2*sign*(t['price']-t['prior_midpoint'])*t['quantity']));qty+=t['quantity']
            return bounded(total/qty)
        bd=sum(latest['bids'].values()) if latest else 0;ad=sum(latest['asks'].values()) if latest else 0
        metrics={
          'spread':field(lambda:top[1]-top[0] if top else None),
          'relative_spread':field(lambda:Fraction(2*(top[1]-top[0]),top[0]+top[1]) if top else None),
          'depth_imbalance':field(lambda:Fraction(bd-ad,bd+ad) if bd+ad else None),
          'weighted_midprice':field(lambda:Fraction(top[1]*top[2]+top[0]*top[3],top[2]+top[3]) if top else None),
          'microprice':field(lambda:Fraction(top[1]*top[2]+top[0]*top[3],top[2]+top[3]) if top else None),
          'ofi':field(ofi,'incomplete_top_quote_interval'),
          'matched_level_replenishment':field(lambda:dynamics(True),'incomplete_matched_level_interval'),
          'matched_level_depletion':field(lambda:dynamics(False),'incomplete_matched_level_interval'),
          'trade_intensity_per_second':field(lambda:Fraction(len(trades)*10**9,elapsed) if complete_trades and elapsed>0 and self.started is not None else None,'incomplete_trade_interval'),
          'reported_side_net_quantity':field(lambda:sum(t['quantity']*(1 if t['side']=='buy' else -1) for t in trades) if complete_trades and self.started is not None else None),
          'event_sampled_realized_variance':field(variance,'incomplete_return_interval'),
          'effective_spread':field(effective,'aggressor_semantics_or_prior_quote_unverified'),
          'bid_top_concentration':field(lambda:Fraction(latest['bids'][max(latest['bids'])],bd) if bd else None),
          'ask_top_concentration':field(lambda:Fraction(latest['asks'][min(latest['asks'])],ad) if ad else None),
        }
        volatility=None;rv=metrics['event_sampled_realized_variance']['value']
        if rv:
            with localcontext() as c:
                c.prec=34;volatility=str((Decimal(rv['numerator'])/Decimal(rv['denominator'])).sqrt())
        return {'schema_version':'1','status':('AVAILABLE' if complete_quotes and complete_trades else 'PARTIAL') if latest else 'INSUFFICIENT',
            'as_of_receive_ns':str(now),'effective_start_receive_ns':str(start),'requested_window_ns':str(self.window),
            'quotes':len(selected),'trades':len(trades),'maximum_each':LIMIT,
            'window_warmup_complete':self.started is not None and now-self.started>=self.window,
            'quote_coverage_complete':complete_quotes,'trade_coverage_complete':complete_trades,
            'metrics':metrics,'realized_volatility_approximate':volatility,
            'methodology':{'clock':'receive-monotonic;capture-order ties;not exchange-time causal proof',
                'ofi':'best-price Cont-style displayed-size changes;not identified orders',
                'liquidity_dynamics':'quantity changes only at prices present in consecutive subscribed views;boundary changes excluded',
                'variance':'sum of squared simple midpoint returns at event arrivals;not annualized or regular-sampled',
                'weighted_midprice':'same top-quantity formula as microprice;not an independent signal',
                'trade_sign':'provider-reported side;aggressor semantics confirmed only by explicit configuration',
                'effective_spread':'quantity weighted, strictly prior captured valid quote,max age10s;no future quote',
                'arithmetic':'Python Fraction exact,1024-bit capacity;Decimal34 approximate square root;not native hot path',
                'research_status':'descriptive;not empirically validated alpha'}}
