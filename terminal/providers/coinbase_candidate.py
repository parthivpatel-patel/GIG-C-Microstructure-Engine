"""Unverified legacy Exchange-shaped offline candidate. Never opens a socket.

Official current docs/terms are blocked. This is not current protocol or live
qualification. Global source sequence, when supplied, is preserved but is not a
contiguous L2 sequence. Match side is retained as reported maker-side candidate,
not silently reinterpreted as aggressor direction. No FIFO/order identities inferred.
"""
from collections import deque
import re
from .kraken import decode,decimal_wire,timestamp_ns,bounded_integer,ProviderError,PRICE_MAX,UINT64_MAX

class CoinbaseCandidate:
    def __init__(self,apply_native,*,symbol='BTC-USD',max_levels=256,origin='HISTORICAL_SYNTHETIC'):
        if symbol not in ('BTC-USD','ETH-USD') or type(max_levels) is not int or not 1<=max_levels<=256:raise ProviderError('coinbase_configuration')
        if origin not in ('HISTORICAL_SYNTHETIC','LIVE_OBSERVED'):raise ProviderError('coinbase_origin')
        self.origin=origin;self.snapshots=self.updates=0
        self.apply=apply_native;self.symbol=symbol;self.limit=max_levels
        self.bids={};self.asks={};self.state='DISCONNECTED';self.last_book_ns=None;self.last_receive=None
        self.trades=deque(maxlen=128);self.trade_ids=set();self.rejected=0
    def _unit(self,value,price=False):
        result=decimal_wire(value,maximum=PRICE_MAX if price else UINT64_MAX,scale=100000000)[0]
        if price and result=='0':raise ProviderError('coinbase_zero_price')
        return result
    @property
    def last_book_receive_ns(self):return self.last_book_ns
    def connect(self):
        self.disconnected();self.state='SYNCHRONIZING'
    def disconnected(self):
        self.state='DISCONNECTED';self.bids={};self.asks={};self.last_book_ns=self.last_receive=None
        self.trades.clear();self.trade_ids.clear()
    def status(self,now):
        if self.last_book_ns is not None and now-self.last_book_ns>10_000_000_000 and self.state=='CANDIDATE_READY':self.state='STALE'
        return {'state':self.state,'reason':'depth_freshness_deadline' if self.state=='STALE' else 'candidate_profile_no_sequence_or_checksum_proof','provider':'coinbase-exchange-candidate','symbol':self.symbol,
            'profile_verified':False,'live_verified':False,'origin':self.origin,
            'sequence_continuity':'unverified_global_scope_not_a_contiguous_L2_sequence','checksum':'not_defined_in_candidate'}
    def feed(self,raw,now):
        try:
            if type(now) is not int or now<0 or (self.last_receive is not None and now<self.last_receive):raise ProviderError('coinbase_receive_order')
            result=self._feed(decode(raw),now)
            self.last_receive=now
            return result
        except (ProviderError,MemoryError):self.state='RESYNCING';self.rejected+=1;raise
    def _feed(self,p,now):
        kind=p.get('type')
        fields={'snapshot':{'type','product_id','bids','asks','sequence','time'},
            'l2update':{'type','product_id','changes','time','sequence'},
            'match':{'type','product_id','side','trade_id','price','size','time','sequence','maker_order_id','taker_order_id'},
            'last_match':{'type','product_id','side','trade_id','price','size','time','sequence','maker_order_id','taker_order_id'},
            'heartbeat':{'type','product_id','sequence','last_trade_id','time'},'subscriptions':{'type','channels'}}
        if type(kind) is not str or kind not in fields:raise ProviderError('coinbase_unsupported')
        if set(p)-fields[kind]:raise ProviderError('coinbase_unknown_fields')
        if kind=='subscriptions':
            channels=p.get('channels')
            if type(channels) is not list or len(channels)>3:raise ProviderError('coinbase_subscription')
            for c in channels:
                if type(c) is not dict or c.get('name') not in ('level2','matches','heartbeat') or c.get('product_ids')!=[self.symbol]:raise ProviderError('coinbase_subscription')
            return {'kind':'acknowledgment','origin':self.origin}
        if p.get('product_id')!=self.symbol:raise ProviderError('coinbase_product')
        sequence=None if p.get('sequence') is None else str(bounded_integer(p['sequence'],UINT64_MAX,'coinbase_source_sequence'))
        source_ns=None if p.get('time') is None else timestamp_ns(p['time'])
        if kind=='heartbeat':
            last=None if p.get('last_trade_id') is None else str(bounded_integer(p['last_trade_id'],UINT64_MAX,'coinbase_last_trade_id'))
            return {'kind':'heartbeat','source_sequence':sequence,'source_timestamp_ns':source_ns,'last_trade_id':last}
        if kind in ('match','last_match'):
            if p.get('side') not in ('buy','sell') or source_ns is None:raise ProviderError('coinbase_match')
            tid=str(bounded_integer(p.get('trade_id'),UINT64_MAX,'coinbase_trade_id'))
            price,qty=self._unit(p.get('price'),True),self._unit(p.get('size'))
            if qty=='0':raise ProviderError('coinbase_zero_trade')
            trade={'trade_id':tid,'price_ticks':price,'quantity':qty,'reported_side':p['side'],
                'reported_side_role':'maker_candidate_unverified','aggressor_side':None,'source_timestamp_ns':source_ns,
                'source_sequence':sequence,'origin':self.origin}
            next_trades=self.trades.copy();ids=self.trade_ids.copy()
            duplicate=tid in ids
            if not duplicate:
                if len(next_trades)==next_trades.maxlen:ids.remove(next_trades[0]['trade_id'])
                next_trades.append(trade);ids.add(tid)
            references={}
            for name in ('maker_order_id','taker_order_id'):
                if name in p:
                    if type(p[name]) is not str or not re.fullmatch(r'[A-Za-z0-9-]{1,64}',p[name]):raise ProviderError('coinbase_reference')
                    references[name]=p[name]
            trade['source_order_references']=references
            receipt={'kind':'historical_trade' if kind=='last_match' else 'trade','duplicate':duplicate,'trade':trade}
            self.trades,self.trade_ids=next_trades,ids
            return receipt
        if kind not in ('snapshot','l2update'):raise ProviderError('coinbase_unsupported')
        snapshot=kind=='snapshot'
        if not snapshot and self.state!='CANDIDATE_READY':raise ProviderError('coinbase_snapshot_required')
        candidate=[{},{}] if snapshot else [dict(self.bids),dict(self.asks)]
        changes=[[],[]];seen=set()
        if snapshot:
            updates=[]
            for i,name in enumerate(('bids','asks')):
                values=p.get(name)
                if type(values) is not list or len(values)>self.limit:raise ProviderError('coinbase_depth_budget')
                for pair in values:
                    if type(pair) is not list or len(pair)!=2:raise ProviderError('coinbase_level_fields')
                    updates.append((i,*pair))
        else:
            values=p.get('changes')
            if type(values) is not list or len(values)>256 or source_ns is None:raise ProviderError('coinbase_update_fields')
            updates=[]
            for row in values:
                if type(row) is not list or len(row)!=3 or row[0] not in ('buy','sell'):raise ProviderError('coinbase_side')
                updates.append((0 if row[0]=='buy' else 1,row[1],row[2]))
        for side,pv,qv in updates:
            price,qty=self._unit(pv,True),self._unit(qv)
            if (side,price) in seen:raise ProviderError('coinbase_duplicate_level')
            seen.add((side,price))
            if qty=='0':
                if snapshot:raise ProviderError('coinbase_zero_snapshot')
                candidate[side].pop(price,None)
            else:candidate[side][price]=qty
            changes[side].append({'price_ticks':price,'quantity':qty})
        if any(len(s)>self.limit for s in candidate):raise ProviderError('coinbase_depth_budget')
        if candidate[0] and candidate[1] and max(map(int,candidate[0]))>min(map(int,candidate[1])):raise ProviderError('coinbase_crossed')
        receipt={'kind':'snapshot' if snapshot else 'update','source_sequence':sequence,'source_timestamp_ns':source_ns,
            'origin':self.origin,'native_event':{'snapshot':snapshot,'bids':changes[0],'asks':changes[1],'sequence':None}}
        counts=(self.snapshots+int(snapshot),self.updates+int(not snapshot))
        try:self.apply(**receipt['native_event'])
        except Exception as error:raise ProviderError('coinbase_native_rejected') from error
        self.bids,self.asks=candidate;self.last_book_ns=now;self.state='CANDIDATE_READY';self.snapshots,self.updates=counts
        return receipt
