"""Offline provider-neutral subscription/freshness state,not an Alpaca transport.

A connected socket or heartbeat cannot qualify market observations. Protocol,
entitlements and network activation remain separate owner-controlled gates.
"""
from .identity import symbol
from .prices import timestamp


class ObservationMonitor:
    def __init__(self, *, authorized=False, synthetic=False, stale_after_ns=30_000_000_000, delay_ns=0):
        if type(authorized) is not bool or type(synthetic) is not bool or type(stale_after_ns) is not int or not 1 <= stale_after_ns <= 3600*10**9 or type(delay_ns) is not int or not 0 <= delay_ns <= 86400*10**9:
            raise ValueError('feed_configuration')
        self.authorized=authorized;self.synthetic=synthetic;self.stale_after=stale_after_ns;self.delay=delay_ns
        self.generation=0;self.connected=False;self.subscriptions=set();self.receipts={};self.last_clock=0;self.last_heartbeat=None
    def clock(self, now):
        if type(now) is not int or not self.last_clock <= now <= 2**63-1:
            raise ValueError('feed_monotonic_clock')
    def connect(self, now):
        self.clock(now)
        if not self.authorized:raise ValueError('feed_authorization_required')
        self.generation+=1;self.connected=True;self.subscriptions.clear();self.receipts.clear();self.last_heartbeat=None;self.last_clock=now
        return self.generation
    def acknowledge(self, ticker, generation, now):
        self.clock(now);symbol(ticker)
        if type(generation) is not int or generation!=self.generation or not self.connected:raise ValueError('feed_generation')
        if len(self.subscriptions)>=8 and ticker not in self.subscriptions:raise ValueError('feed_subscription_budget')
        self.subscriptions.add(ticker);self.last_clock=now
    def observe(self, ticker, generation, now, event_timestamp):
        self.clock(now);timestamp(event_timestamp)
        if type(generation) is not int or generation!=self.generation or not self.connected or ticker not in self.subscriptions:raise ValueError('feed_unacknowledged_observation')
        self.receipts[ticker]=(now,event_timestamp);self.last_clock=now
    def heartbeat(self, generation, now):
        self.clock(now)
        if type(generation) is not int or generation!=self.generation or not self.connected:raise ValueError('feed_generation')
        self.last_heartbeat=now;self.last_clock=now
    def disconnect(self, now):
        self.clock(now);self.connected=False;self.subscriptions.clear();self.receipts.clear();self.last_heartbeat=None;self.last_clock=now
    def view(self, ticker, now):
        self.clock(now);symbol(ticker);receipt=self.receipts.get(ticker)
        if not self.authorized:state='BLOCKED'
        elif not self.connected or receipt is None:state='UNAVAILABLE'
        elif now-receipt[0]>self.stale_after:state='STALE'
        elif self.synthetic:state='SIMULATED'
        elif self.delay:state='DELAYED'
        else:state='LIVE'
        return {'state':state,'connected':self.connected,'generation':self.generation,
                'subscription_acknowledged':ticker in self.subscriptions,
                'receive_age_ns':str(now-receipt[0]) if receipt else None,
                'source_timestamp':receipt[1] if receipt else None,
                'declared_delay_ns':str(self.delay),'clock_basis':'local monotonic receipt;not exchange latency',
                'qualification':'State assumes a separately authorized validating adapter;not proof of entitlement,protocol or real feed qualification'}
