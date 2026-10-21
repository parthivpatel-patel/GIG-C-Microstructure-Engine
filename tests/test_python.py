"""Independent Python research consumer tests; run against build tree or installed wheel."""
from copy import deepcopy
from fractions import Fraction
import gc
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import subprocess
import sys
import tempfile
import unittest
import gig_microstructure as gig
from python_fixtures import *
ROOT=Path(__file__).resolve().parents[1]

class InterfaceTests(unittest.TestCase):
    def test_every_event_and_provenance_roundtrip(self):
        variants=[event(),event('1',{'order_id':'1','amount':{'tag':'0','value':{}}}),event('1',{'order_id':'1','amount':{'tag':'1','value':'2'}}),
          event('2',{'old_order_id':'1','new_order_id':'2','side':'0','price_ticks':'101','quantity':'20','priority':'0'}),
          event('3',{'details':{'tag':'0','value':{'price_ticks':'100','quantity':'1','aggressor':missing('1')}}}),
          event('3',{'details':{'tag':'1','value':{'resting_order_id':'1','resting_side':'0','price_ticks':'100','quantity':'1'}}}),
          event('4',{'bid':{'price_ticks':'99','quantity':'10'},'ask':None}),event('5',{'reason':'0','next_epoch':'1'}),snapshot_event(),snapshot_event(kind='1'),event('7',{'action':'0','reason':missing('2')})]
        for value in variants:
            value['data']['metadata']['source_record']=known('quoted;:token\\"')
            value['data']['metadata']['provenance']['parents']=[{'identity':'parent:artifact','sha256':known('a'*64)}]
            normalized=gig.event(value,rules())
            self.assertEqual(normalized.to_dict(),value)
            self.assertEqual(gig.loads(gig.dumps(normalized)).to_dict(),value)
            self.assertTrue(gig.event_canonical(value,rules()).startswith('gig.event.v1;'))
        with self.assertRaises(gig.EngineError):gig.event(event('8',{'wire_type':'999'}),rules())
        incomplete=event();incomplete['data']['metadata']['instrument']=missing('1')
        with self.assertRaises(gig.EngineError):gig.event(incomplete,rules())
        self.assertEqual(gig.event(incomplete,rules(),inspect_incomplete=True)['data']['metadata']['instrument'],missing('1'))

    def test_exact_boundaries_and_strict_input(self):
        value=event(value=add(MAX,'0',HI,MAX),seq=MAX,ordinal=MAX)
        value['data']['metadata']['event_time']['value']['nanoseconds']=str(LO)
        self.assertEqual(gig.loads(gig.dumps(gig.event(value,rules()))).to_dict(),value)
        for invalid in [0,1.5,True,'-1','0','18446744073709551616','1.0','01','+1','-0','1\n']:
            bad=event();bad['data']['payload']['value']['order_id']=invalid
            with self.assertRaises(gig.EngineError):gig.event(bad,rules())
        bad=event();bad['data']['payload']['value']['side']='256'
        with self.assertRaises(gig.EngineError):gig.event(bad,rules())
        for invalid in ['0/1','NaN',None,1]:
            with self.assertRaises(gig.EngineError):gig.exact_fraction(invalid,'1')
        self.assertEqual(gig.exact_fraction(str((1<<127)-1),'1'),Fraction((1<<127)-1))
        with self.assertRaises(gig.EngineError):gig.exact_fraction(str(1<<127),'1')
        with self.assertRaises(gig.EngineError):gig.exact_fraction('1','0')
        duplicate='{"schema":"gig.event","schema":"gig.event","version":"1.0","data":{}}'
        with self.assertRaises(gig.SchemaError):gig.loads(duplicate)
        for encoded in ['NaN','{"a":1.5}','{"a":1}']:
            with self.assertRaises(gig.EngineError):gig.loads(encoded)
        bad=event();bad['data']['payload']['value']['quantity']='9'*10000
        with self.assertRaises(gig.EngineError):gig.event(bad,rules())
        bad=event();bad['data']['metadata']['extra']='unexpected'
        with self.assertRaises(gig.EngineError):gig.event(bad,rules())
        bad=event();bad['version']='2.0'
        with self.assertRaises(gig.EngineError):gig.event(bad,rules())

    def test_replay_ownership_atomicity_and_recovery(self):
        config=replay_config();r=gig.Replay(rules(),config);config['streams'][0]['first_sequence']='99'
        r.apply(event(value=add(1,'0',100,30)));r.apply(event(value=add(2,'1',101,10),seq=1))
        metrics=r.metrics();self.assertEqual(gig.as_fraction(metrics['data']['result']['metrics']['midpoint']),Fraction(201,2))
        self.assertEqual(gig.as_fraction(metrics['data']['result']['metrics']['microprice']),Fraction(403,4))
        snapshot=r.snapshot();original=gig.dumps(snapshot)
        copy=snapshot['data'];copy['book']['bids'][0]['quantity']='1'
        self.assertEqual(gig.dumps(snapshot),original)
        with self.assertRaises(AttributeError):snapshot._json='altered'
        before=r.canonical();bad=event(value=add(1,'0',99,1),seq=2)
        with self.assertRaises(gig.EngineError):r.apply(bad)
        self.assertEqual(r.canonical(),before)
        with self.assertRaises(gig.EngineError):r.apply(event(value=add(3),seq=3))
        self.assertTrue(r.status()['needs_recovery'])
        with self.assertRaises(gig.EngineError):r.snapshot()
        r.recover(snapshot_event(seq=3,ordinal=4));self.assertFalse(r.status()['needs_recovery'])
        self.assertEqual(r.snapshot()['data']['book']['bids'][0]['quantity'],'20')
        reset=event('5',{'reason':'0','next_epoch':'1'},seq=4,ordinal=5)
        restart=[{'venue':'1','scope':scope(1,'next-session'),'dataset':'python-synthetic','dataset_version':'1','first_sequence':'0','rank':'0'}]
        r.reset(reset,restart);self.assertFalse(r.snapshot()['data']['book']['bids'])
        r.recover(snapshot_event(0,6,1,'next-session'))
        self.assertEqual(r.snapshot()['data']['book']['session'],{'session':'next-session','epoch':'1'})
        del r;gc.collect();self.assertEqual(gig.dumps(snapshot),original)
        self.assertEqual(gig.as_fraction(gig.book_analytics(snapshot)['data']['result']['metrics']['midpoint']),Fraction(201,2))
        waiting=gig.Replay(rules(),replay_config(initial='0'))
        with self.assertRaises(gig.EngineError):waiting.apply(event())
        with self.assertRaises(gig.EngineError):waiting.recover(snapshot_event(kind='1'))
        waiting.recover(snapshot_event())
        with self.assertRaises(gig.EngineError) as error:waiting.run([event(value=add(1),seq=1,ordinal=1),event(value=add(1),seq=2,ordinal=2)])
        self.assertEqual((error.exception.accepted,error.exception.failed_input_index),(1,1))
        with self.assertRaises(gig.EngineError):gig.Replay(rules(),replay_config(),resource_budget_bytes='1')
        constrained=gig.Replay(rules(),replay_config(),resource_budget_bytes='4096');before=constrained.canonical()
        with self.assertRaises(gig.EngineError):constrained.apply(event())
        self.assertEqual(constrained.canonical(),before)

    def test_simulation_and_execution(self):
        config=simulation_config();config['execution']['base']='5';s=gig.Simulation(config)
        s.submit('0',order(1));s.submit('0',order(2,'1',100,20));s.advance('0')
        self.assertEqual(s.queue_position('2'),{'orders_ahead':'1','quantity_ahead':'10'})
        s.submit('0',order(3,'0',101,15,'1'));s.advance('0');state=s.snapshot();self.assertEqual(len(state['data']['state']['exchange_fills']),2)
        self.assertFalse(any(r['kind']=='5' for r in state['data']['state']['client_reports']))
        s.advance('5');self.assertEqual(sum(int(r['quantity']) for r in s.snapshot()['data']['state']['client_reports'] if r['kind']=='5' and r['order']=='3'),15)
        self.assertEqual(sum(int(r['quantity']) for r in s.snapshot()['data']['state']['client_reports'] if r['kind']=='5' and r['order'] in ['1','2']),15)
        before=s.canonical();bad=order(4);bad['tif']='255'
        with self.assertRaises(gig.EngineError):s.submit('5',bad)
        self.assertEqual(before,s.canonical())
        frozen=s.snapshot();del s;gc.collect();self.assertEqual(gig.loads(gig.dumps(frozen)).to_dict(),frozen.to_dict())
        p=gig.twap(plan_config());self.assertEqual([c['order']['quantity'] for c in p['data']['children']],['4','3','3'])
        v=gig.vwap(plan_config(),['1','2','1'],'forecast-volume','0');self.assertFalse(v['data']['oracle'])
        with self.assertRaises(gig.EngineError):gig.vwap(plan_config(),['1','2','1'],'future','1')
        self.assertTrue(gig.vwap(plan_config(),['1','2','1'],'oracle','1000',oracle=True)['data']['oracle'])
        points=[{'available_at':'1','lots':'100','source_artifact':'volume-input','ordinal':'1'}]
        self.assertEqual(gig.pov(plan_config(),points,'1','10')['data']['children'][0]['order']['quantity'],'10')
        result=gig.simulate_plan(p,simulation_config(),[order(1,'1',103,100)],'1000')
        self.assertEqual(sum(int(f['quantity']) for f in result.simulation['data']['state']['exchange_fills']),10)
        for document in [state,frozen,p,v,result.plan,result.simulation]:self.assertEqual(gig.loads(gig.dumps(document)).to_dict(),document.to_dict())

    def test_flow_and_costs(self):
        r=gig.Replay(rules(),replay_config());r.apply(event(value=add(1,'0',100,30)));r.apply(event(value=add(2,'1',102,10),seq=1));source0=source(r.snapshot())
        r.apply(event('3',{'details':{'tag':'0','value':{'price_ticks':'102','quantity':'1','aggressor':missing()}}},seq=2));trade_source=source(r.snapshot())
        r.apply(event('2',{'old_order_id':'1','new_order_id':'1','side':'0','price_ticks':'101','quantity':'20','priority':'0'},seq=3));r.apply(event('2',{'old_order_id':'2','new_order_id':'2','side':'1','price_ticks':'103','quantity':'20','priority':'0'},seq=4));source1=source(r.snapshot())
        q=[{'source':source0,'timestamp':'0','utc_clock':'py-utc','bid':{'price_ticks':'100','quantity':'30','order_count':'1'},'ask':{'price_ticks':'102','quantity':'10','order_count':'1'}},
          {'source':source1,'timestamp':'10','utc_clock':'py-utc','bid':{'price_ticks':'101','quantity':'20','order_count':'1'},'ask':{'price_ticks':'103','quantity':'20','order_count':'1'}}]
        t=[{'source':trade_source,'timestamp':'5','utc_clock':'py-utc','price':'102','quantity':'1'}]
        c={'utc_clock':'py-utc','window':'10','quote_lag':'0','horizon':'5','max_quote_age':'100','sampling_interval':'10','continuity_complete':True,'complete_top_updates':True}
        flow=gig.flow_analytics(q,t,c,'10');self.assertEqual(gig.as_fraction(flow['data']['result']['summary']['ofi']),30)
        self.assertEqual(gig.loads(gig.dumps(flow)).to_dict(),flow.to_dict())
        plan=gig.twap(plan_config(20,2));result=gig.simulate_plan(plan,simulation_config(),[order(1,'1',103,10)],'1000');fill=result.simulation['data']['state']['exchange_fills'][0]
        cost_config={'run_id':'cost-run','simulation_run_id':'python-simulation-run','rules':rules(),'side':'0','target':'20','arrival':benchmark(100),'terminal':benchmark(104,1000),'as_of':'1000'}
        rows=[{'fill':fill,'child':'1000','decision_time':'0','decision_benchmark':benchmark(102),'fee_ticks_per_lot':ratio(1,10)}]
        cost=gig.transaction_costs(cost_config,rows)
        self.assertEqual(cost['data']['result']['summary']['implementation_shortfall'],ratio(71));self.assertEqual(cost['data']['result']['summary']['currency_shortfall'],ratio(71,100))
        self.assertEqual(gig.loads(gig.dumps(cost)).to_dict(),cost.to_dict())

    def test_random_fraction_numeric_reference(self):
        rng=random.Random(8033)
        for _ in range(300):
            n=rng.randint(-(1<<120),(1<<120));d=rng.randint(1,1<<120)
            self.assertEqual(gig.exact_fraction(str(n),str(d)),Fraction(n,d))

    def test_manifest_export_integrity_and_failure(self):
        r=gig.Replay(rules(),replay_config());r.apply(event());snapshot=r.snapshot();native_archive=r.canonical().encode()
        sha=hashlib.sha256(native_archive).hexdigest();head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        source_paths=subprocess.check_output(['git','ls-files','-c','-o','--exclude-standard','-z'],cwd=ROOT).split(b'\0')
        hashes={n.decode():hashlib.sha256((ROOT/n.decode()).read_bytes()).hexdigest() for n in sorted(set(source_paths)) if n and n.decode().startswith(('src/','include/','python/','cmake/')) and '__pycache__' not in n.decode()}
        tree_hash=hashlib.sha256(json.dumps(hashes,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True))
        data={'run_id':'python-research-run','code':{'commit_sha':head,'dirty':dirty,'source_tree_sha256':tree_hash},
          'build':{'compiler':gig.native_build_info()['compiler'],'flags':gig.native_build_info()['config_flags']+' '+gig.native_build_info()['binding_flags'],'architecture':platform.machine(),'os':platform.platform(),'dependencies':{'pybind11':'2.13.6','jsonschema':'4.23.0'}},
          'inputs':[{'identity':'accepted-replay-journal','sha256':sha,'license_reference':'synthetic-fixture:no-external-data','origin':'synthetic','source':'python-explicit-fixture-v1','transformation':'reconstructed','local_file':None}],
          'parents':[],'schema_versions':{'gig.book_snapshot':'1.0'},'instrument_rules':[rules()],
          'policies':{'ordering':'capture ordinal','sequence':'strict per stream','recovery':'complete order snapshots only','clock':'py-utc declared','precision':'nanoseconds'},
          'parameters':{'initial_book':'declared empty synthetic'},'seeds':['0'],'coverage':{'start_ns':known('0'),'end_ns':known('0'),'records':'1'},'outputs':[],'errors':[],'complete':True}
        manifest=gig.run_manifest(data)
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'run';final=gig.export_run(path,manifest,{'snapshot.json':snapshot},input_artifacts={'accepted-replay-journal':native_archive})
            self.assertTrue((path/'manifest.json').is_file());self.assertFalse((path/'manifest.incomplete.json').exists())
            self.assertEqual(hashlib.sha256((path/'snapshot.json').read_bytes()).hexdigest(),final['data']['outputs'][0]['sha256'])
            self.assertEqual((path/final['data']['inputs'][0]['local_file']).read_bytes(),native_archive)
            self.assertEqual(gig.verify_export(path).to_dict(),final.to_dict())
            original=(path/'snapshot.json').read_bytes();(path/'snapshot.json').write_bytes(b'{}')
            with self.assertRaises(gig.EngineError):gig.verify_export(path)
            (path/'snapshot.json').write_bytes(original)
            with self.assertRaises(FileExistsError):gig.export_run(path,manifest,{'snapshot.json':snapshot},input_artifacts={'accepted-replay-journal':native_archive})
            with self.assertRaises(gig.SchemaError):gig.export_run(Path(temp)/'bad',manifest,{'snapshot.json':snapshot},input_artifacts={'accepted-replay-journal':b'wrong'})
            self.assertFalse((Path(temp)/'bad').exists())
            import unittest.mock
            with unittest.mock.patch('gig_microstructure.os.link',side_effect=OSError('intentional export failure')):
                with self.assertRaises(OSError):gig.export_run(Path(temp)/'incomplete',manifest,{'snapshot.json':snapshot},input_artifacts={'accepted-replay-journal':native_archive})
            self.assertTrue((Path(temp)/'incomplete/manifest.incomplete.json').is_file());self.assertFalse((Path(temp)/'incomplete/manifest.json').exists())
            with self.assertRaises(gig.EngineError):gig.verify_export(Path(temp)/'incomplete')
            self.assertEqual(json.loads((Path(temp)/'incomplete/manifest.incomplete.json').read_text())['data']['errors'][0]['field'],'OSError')
        bad=deepcopy(data);bad['errors']=[{'code':'invalid','field':'test','index':None}]
        with self.assertRaises(gig.SchemaError):gig.run_manifest(bad)
        bad=deepcopy(data);bad['seeds']=[str(1<<64)]
        with self.assertRaises(gig.SchemaError):gig.run_manifest(bad)

if __name__=='__main__':unittest.main(verbosity=2)
