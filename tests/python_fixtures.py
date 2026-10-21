"""Explicit synthetic inputs; no real-market or observed-execution claim."""
from copy import deepcopy
MAX=(1<<64)-1
LO=-(1<<63)
HI=(1<<63)-1

def known(value):return {'reason':'0','value':value}
def missing(reason='3'):return {'reason':reason,'value':None}
def rules():return {'instrument':'1','venue':'1','minimum_price':'1','maximum_price':str(HI),'maximum_quantity':str(MAX),'tick_size':{'numerator':'1','denominator':'100'},'lot_size':{'numerator':'1','denominator':'1'}}
def scope(epoch=0,session='py-session'):return {'stream':'1','session':session,'epoch':str(epoch),'unit':'0'}
def metadata(seq=0,ordinal=None,epoch=0,session='py-session'):
    return {'schema_version':'1','instrument':known('1'),'venue':known('1'),'scope':known(scope(epoch,session)),
      'sequence':known(str(seq)),'subevent_index':'0','subevent_count':'1',
      'event_time':known({'nanoseconds':str(seq if seq<=HI else HI),'clock':known({'domain':'0','identity':'py-utc'}),'precision':known('0')}),
      'receive_time':missing('2'),'source_record':known(f'py-record:{epoch}:{seq}'),'capture_ordinal':known(str(seq if ordinal is None else ordinal)),
      'provenance':{'dataset':known({'identity':'python-synthetic','version':known('1'),'license_reference':known('synthetic-fixture:no-external-data'),'sha256':missing()}),
      'origin':known('0'),'source':known('0'),'generator_seed':known('0'),'lineage':[{'kind':'0','operation':'python-explicit-fixture-v1','version':'1'}],'parents':[]}}
def add(identifier=1,side='0',price=100,quantity=10):return {'order_id':str(identifier),'side':side,'price_ticks':str(price),'quantity':str(quantity)}
def event(tag='0',value=None,seq=0,**kw):return {'schema':'gig.event','version':'1.0','data':{'metadata':metadata(seq,**kw),'payload':{'tag':str(tag),'value':add() if value is None else value}}}
def replay_config(first=0,initial='1'):
    return {'run_id':'python-research-run','session':{'session':'py-session','epoch':'0'},'streams':[{'venue':'1','scope':scope(),'dataset':'python-synthetic','dataset_version':'1','first_sequence':str(first),'rank':'0'}],
     'ordering':'0','timestamp_clock':missing(),'additional_instruments':[],'max_journal_records':'4096','initial_state':initial}
def simulation_config():
    zero={'base':'0','jitter':'0'}
    return {'run_id':'python-simulation-run','rules':rules(),'seed':'1729','arrival':deepcopy(zero),'cancel':deepcopy(zero),'acknowledgment':deepcopy(zero),'execution':deepcopy(zero),'max_orders':'1024','max_events':'4096','max_fills':'4096','max_commands':'4096','max_reports':'4096'}
def order(identifier=1,side='1',price=100,quantity=10,tif='0',post=False):return {'id':str(identifier),'side':side,'limit':str(price),'quantity':str(quantity),'tif':tif,'post_only':post}
def plan_config(target=10,bins=3):return {'run_id':'python-simulation-run','assumptions_id':'synthetic-fixed-limit-v1','rules':rules(),'side':'0','limit':'105','target':str(target),'inventory_limit':str(target),'max_child':str(MAX),'start':'0','end':'1000','bins':str(bins),'first_child_id':'1000','tif':'1','post_only':False}
def ratio(n,d=1):return {'numerator':str(n),'denominator':str(d)}
def benchmark(value,at=0):return {'midpoint':ratio(value),'available_at':str(at),'source_artifact':'synthetic-benchmark-prices'}
def source(snapshot):
    d=snapshot['data'];b=d['book'];return {'run_id':d['run_id'],'journal_prefix':d['journal_prefix'],'revision':b['revision'],'rules':b['rules'],'session':b['session']}
def snapshot_event(seq=0,ordinal=0,epoch=0,session='py-session',kind='0'):
    value={'kind':kind,'coverage':'0','depth':'0','orders':[{'order':add(77,'0',98,20),'priority_index':'7'}] if kind=='0' else [],'levels':[] if kind=='0' else [{'side':'0','price_ticks':'98','quantity':'20'}],
     'boundaries':[{'scope':scope(epoch,session),'sequence':str(seq),'last_subevent':'0','subevent_count':'1'}]}
    return event('6',value,seq=seq,ordinal=ordinal,epoch=epoch,session=session)
