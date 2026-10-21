"""Self-contained fixed synthetic research example; installed-wheel consumer, no repository imports."""
from fractions import Fraction
import gig_microstructure as gig

def known(value):return {'reason':'0','value':value}
def missing():return {'reason':'3','value':None}

def main():
    rules={'instrument':'1','venue':'1','minimum_price':'1','maximum_price':'9223372036854775807','maximum_quantity':'18446744073709551615','tick_size':{'numerator':'1','denominator':'100'},'lot_size':{'numerator':'1','denominator':'1'}}
    scope={'stream':'1','session':'example-session','epoch':'0','unit':'0'}
    config={'run_id':'python-research-example','session':{'session':'example-session','epoch':'0'},'streams':[{'venue':'1','scope':scope,'dataset':'example-synthetic','dataset_version':'1','first_sequence':'0','rank':'0'}],'ordering':'0','timestamp_clock':missing(),'additional_instruments':[],'max_journal_records':'32','initial_state':'1'}
    replay=gig.Replay(rules,config)
    for sequence,side,price,quantity in [(0,'0','100','30'),(1,'1','101','10')]:
        metadata={'schema_version':'1','instrument':known('1'),'venue':known('1'),'scope':known(scope),'sequence':known(str(sequence)),'subevent_index':'0','subevent_count':'1',
          'event_time':known({'nanoseconds':str(sequence),'clock':known({'domain':'0','identity':'example-logical-utc'}),'precision':known('0')}),'receive_time':missing(),'source_record':known(f'example:{sequence}'),'capture_ordinal':known(str(sequence)),
          'provenance':{'dataset':known({'identity':'example-synthetic','version':known('1'),'license_reference':known('synthetic-fixture:no-external-data'),'sha256':missing()}),'origin':known('0'),'source':known('0'),'generator_seed':known('0'),'lineage':[{'kind':'0','operation':'fixed-example-generator-v1','version':'1'}],'parents':[]}}
        replay.apply({'schema':'gig.event','version':'1.0','data':{'metadata':metadata,'payload':{'tag':'0','value':{'order_id':str(sequence+1),'side':side,'price_ticks':price,'quantity':quantity}}}})
    metrics=replay.metrics()
    assert gig.as_fraction(metrics['data']['result']['metrics']['midpoint'])==Fraction(201,2)
    assert gig.as_fraction(metrics['data']['result']['metrics']['microprice'])==Fraction(403,4)
    print(gig.dumps(metrics))
    zero={'base':'0','jitter':'0'}
    simulation=gig.Simulation({'run_id':'example-offline-simulation','rules':rules,'seed':'1729','arrival':zero,'cancel':zero,'acknowledgment':zero,'execution':{'base':'5','jitter':'0'},'max_orders':'32','max_events':'128','max_fills':'64','max_commands':'64','max_reports':'128'})
    simulation.submit('0',{'id':'1','side':'1','limit':'100','quantity':'10','tif':'0','post_only':False})
    simulation.submit('0',{'id':'2','side':'0','limit':'101','quantity':'5','tif':'1','post_only':False})
    simulation.advance('0')
    assert not any(r['kind']=='5' for r in simulation.snapshot()['data']['state']['client_reports'])
    simulation.advance('5')
    result=simulation.snapshot()
    assert result['data']['origin']=='synthetic' and result['data']['transformation']=='simulated'
    assert sum(int(r['quantity']) for r in result['data']['state']['client_reports'] if r['kind']=='5' and r['order']=='2')==5
    assert sum(int(r['quantity']) for r in result['data']['state']['client_reports'] if r['kind']=='5' and r['order']=='1')==5
    print(gig.dumps(result))

if __name__=='__main__':main()
