"""Actual product-session class/selector tests;never constructs the ASGI app."""
import base64,copy,dataclasses,errno,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import gig_microstructure as gig
from gig_microstructure.itch_recovery import ItchRecovery,ItchAdmission
from terminal.server.engine import NativeSession,ControlError
from terminal.itch_product import ItchProduct,ItchProductError,build_bundle,encoded,digest,implementation_identity,save_new,load,migrate,select_product_session

def payload(kind='X',reference=103,quantity=1):
    p=bytearray(23);p[0]=ord(kind);p[1:3]=(1).to_bytes(2,'big');p[5:11]=(1).to_bytes(6,'big');p[11:19]=reference.to_bytes(8,'big');p[19:23]=quantity.to_bytes(4,'big');return bytes(p)
def framed(*packets):return b''.join(len(p).to_bytes(2,'big')+p for p in packets)
class ItchProductTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.directory=tempfile.TemporaryDirectory();root=Path(cls.directory.name)
  import gig_microstructure._native as native
  fixture=Path(os.environ.get('GIG_ITCH_FIXTURE',str(Path(native.__file__).parents[2]/'gig_itch_durable_checkpoint_tests')))
  cls.fixture=fixture
  run=subprocess.run([str(fixture),'--fixture',str(root/'image')],capture_output=True,text=True,check=True,timeout=30)
  meta=json.loads(run.stdout);cls.original=(root/'image').read_bytes();cls.source_a=ItchAdmission(**{k:meta[k]for k in('artifact_sha256','contract_sha256','implementation_sha256','capture','generation')})
 @classmethod
 def tearDownClass(cls):cls.directory.cleanup()
 def bundle(self,**kw):
  image,a=ItchRecovery.migrate(self.original,self.source_a,implementation_identity())
  return build_bundle(image,a,framed(payload(),payload(quantity=2)),**kw)
 def session(self,raw=None):
  raw=self.bundle()if raw is None else raw
  with patch.object(gig.Replay,'apply',side_effect=AssertionError('No default startup events')),patch.object(NativeSession,'restart',side_effect=AssertionError('No startup replay')):
   return NativeSession.restore_checkpoint(raw,digest(raw),implementation_identity())
 def test_actual_product_restores_paused_without_startup_replay(self):
  s=self.session();v=s.state();self.assertEqual(s.position,9);self.assertFalse(s.playing);self.assertIsNone(s.live_feed);self.assertEqual(v['instrument'],'TEST');self.assertEqual(v['price_scale'],'10000');self.assertEqual(v['event_count'],11);self.assertEqual(v['replay_min_position'],9);self.assertEqual(v['origin'],'HISTORICAL_SYNTHETIC');self.assertEqual(v['provenance']['generation'],'17');self.assertFalse(v['feed']['capture_complete']);self.assertIsNone(v['replay_time_ns'])
 def test_both_books_selection_isolation_and_native_metrics(self):
  s=self.session();books=s.itch_session.owner.canonical();self.assertEqual(s.state()['book']['bids'][0]['quantity'],'8');s.control('book',1);self.assertEqual(s.state()['instrument'],'TWO');self.assertEqual(s.state()['book']['bids'][0]['quantity'],'9');s.control('step');self.assertEqual(s.itch_session.owner.canonical()[1],books[1]);s.control('book',0);self.assertEqual(s.state()['book']['bids'][0]['quantity'],'7');self.assertEqual(s.state()['metrics']['bid_depth'],{'numerator':'7','denominator':'1'})
 def test_replay_controls_capture_current_cursor_and_restart(self):
  s=self.session();before=s.itch_session.owner.canonical();s.control('play');self.assertTrue(s.playing);self.assertTrue(s.step());self.assertTrue(s.playing);self.assertTrue(s.step());self.assertFalse(s.playing);self.assertEqual(s.position,11);s.control('speed',4);self.assertFalse(s.playing);s.control('seek',10);self.assertEqual(s.position,10);s.control('restart');self.assertEqual(s.itch_session.owner.canonical(),before);s.control('step');s.control('book',1);s.control('speed',4)
  current=s.checkpoint(implementation_identity());r=self.session(current);self.assertEqual(r.position,10);self.assertEqual(r.speed,4);self.assertEqual(r.itch_session.selected_book,1);self.assertEqual(r.itch_session.owner.canonical(),s.itch_session.owner.canonical());self.assertFalse(r.playing);s.step();r.step();self.assertEqual(r.itch_session.owner.canonical(),s.itch_session.owner.canonical())
 def test_failed_candidate_or_exhaustion_never_replaces_accepted_session(self):
  s=self.session();before=s.itch_session.owner.canonical()
  with self.assertRaises(gig.EngineError):s.itch_session.seek(10,resource_budget_bytes=1)
  self.assertEqual(s.itch_session.owner.canonical(),before);self.assertEqual(s.position,9)
  s.control('play');original_step=ItchProduct.step
  with patch.object(ItchProduct,'step',autospec=True,side_effect=lambda owner:original_step(owner,resource_budget_bytes=1)):
   with self.assertRaises(gig.EngineError):s.step()
  self.assertFalse(s.playing);s.control('speed',4);self.assertFalse(s.playing)
  with self.assertRaises(ValueError):s.select_itch_checkpoint(b'corrupt','0'*64)
  self.assertEqual(s.itch_session.owner.canonical(),before)
  with self.assertRaises(ValueError):ItchProduct.restore(self.bundle(),digest(self.bundle()),resource_budget_bytes=1)
 def test_unsupported_controls_and_unknown_frames_fail_closed(self):
  s=self.session();before=s.state()
  for action,value in [('mode','LIVE'),('mode','SIMULATION'),('connect','kraken'),('book',True),('book',2),('seek',8),('seek',True),('speed',3)]:
   with self.subTest(action=action,value=value),self.assertRaises((ControlError,ValueError)):s.control(action,value)
  self.assertEqual(s.state()['book'],before['book'])
  image,a=ItchRecovery.migrate(self.original,self.source_a,implementation_identity())
  for tail in(b'\x00',b'\x00\x00',b'\xff\xffa',framed(payload(reference=999))):
   with self.assertRaises(ValueError):build_bundle(image,a,tail)
 def test_schema_corruption_tail_control_and_generation_rejection(self):
  raw=self.bundle();v=json.loads(raw)
  for change in [{'version':2},{'version':True},{'extra':0},{'tail_sha256':'0'*64},{'selected_book':True},{'speed':3},{'native_binary_sha256':'0'*64}]:
   candidate=encoded({**v,**change})
   with self.subTest(change=change),self.assertRaises(ValueError):ItchProduct.restore(candidate,digest(candidate))
  for key,value in [('generation',18),('capture','other'),('contract_sha256','0'*64)]:
   candidate=copy.deepcopy(v);candidate['admission'][key]=value;candidate=encoded(candidate)
   with self.assertRaises(ValueError):ItchProduct.restore(candidate,digest(candidate))
  with self.assertRaises(ValueError):ItchProduct.restore(raw[:-1],digest(raw))
 def test_default_and_explicit_environment_selection_fail_closed(self):
  with patch.object(NativeSession,'__init__',return_value=None)as default:
   select_product_session({});default.assert_called_once()
  for env in [{'GIG_TERMINAL_SESSION':'unknown'},{'GIG_ITCH_SESSION_PATH':'x'},{'GIG_TERMINAL_SESSION':'itch'}]:
   with self.assertRaises(ValueError):select_product_session(env)
  with tempfile.TemporaryDirectory()as directory:
   path=Path(directory)/'session';raw=self.bundle();save_new(path,raw,digest(raw));env={'GIG_TERMINAL_SESSION':'itch','GIG_ITCH_SESSION_PATH':str(path),'GIG_ITCH_SESSION_SHA256':digest(raw)}
   with patch.object(NativeSession,'__init__',side_effect=AssertionError('No startup')):selected=select_product_session(env)
   self.assertEqual(selected.state()['instrument'],'TEST');self.assertFalse(selected.playing)
 def test_private_immutable_bundle_and_disk_faults(self):
  raw=self.bundle()
  with tempfile.TemporaryDirectory()as directory:
   path=Path(directory)/'session'
   def fail():raise OSError(errno.ENOSPC,'authored disk fault')
   with self.assertRaises(OSError):save_new(path,raw,digest(raw),before_publish=fail)
   self.assertFalse(path.exists())
   with self.assertRaisesRegex(ValueError,'uncertain'):save_new(path,raw,digest(raw),after_publish=fail)
   self.assertEqual(load(path,digest(raw)).capture(),raw)
   with self.assertRaisesRegex(ValueError,'exists'):save_new(path,raw,digest(raw))
   os.chmod(path,0o644)
   with self.assertRaisesRegex(ValueError,'private'):load(path,digest(raw))
 def test_cross_process_publication_exit_and_product_restart(self):
  raw=self.bundle()
  with tempfile.TemporaryDirectory()as directory:
   path=Path(directory)/'session';source=Path(directory)/'input';source.write_bytes(raw)
   command="from terminal.itch_product import save_new;import os;save_new("+repr(str(path))+",open("+repr(str(source))+",'rb').read(),"+repr(digest(raw))+",after_publish=lambda:os._exit(79))"
   run=subprocess.run([sys.executable,'-c',command],cwd=Path(__file__).resolve().parents[1],env=os.environ.copy(),capture_output=True,timeout=30);self.assertEqual(run.returncode,79,run.stderr.decode(errors='replace'));self.assertEqual(load(path,digest(raw)).position,9)
 def test_explicit_migration_preserves_state_config_and_lineage(self):
  raw=self.bundle();v=json.loads(raw);v['native_binary_sha256']='0'*64;old=encoded(v);before=bytes(old)
  with self.assertRaisesRegex(ValueError,'migration'):ItchProduct.restore(old,digest(old))
  new=migrate(old,digest(old));self.assertEqual(old,before);p=ItchProduct.restore(new,digest(new));self.assertEqual(p.owner.canonical(),self.session(raw).itch_session.owner.canonical());self.assertEqual(p.history[0]['from_bundle_sha256'],digest(old));self.assertEqual(p.owner.describe()['source'],'p1g-native-synthetic')
  with self.assertRaisesRegex(ValueError,'no_migration'):migrate(new,digest(new))
  for change in({'version':99},{'image':base64.b64encode(b'broken').decode()}):
   altered=encoded({**json.loads(old),**change})
   with self.assertRaises(ValueError):migrate(altered,digest(altered))
 def test_switching_away_preserves_existing_authored_workflow(self):
  s=self.session();s.control('dataset','terminal-authored-v2');self.assertIsNone(s.itch_session);self.assertEqual(s.position,20);self.assertEqual(s.state()['provider'],'authored');self.assertTrue(s.state()['capabilities']['itch_checkpoint_available']);s.control('dataset','itch-checkpoint-v1');self.assertEqual(s.state()['instrument'],'TEST');s.control('dataset','terminal-authored-v2');s.control('mode','SIMULATION');self.assertEqual(s.state()['origin'],'SIMULATED')

 def test_native_depth_limit_one_is_honored_in_product_projection(self):
  with tempfile.TemporaryDirectory()as directory:
   target=Path(directory)/'image';run=subprocess.run([str(self.fixture),'--fixture-depth1',str(target)],capture_output=True,text=True,check=True,timeout=30);meta=json.loads(run.stdout);a=ItchAdmission(**{k:meta[k]for k in('artifact_sha256','contract_sha256','implementation_sha256','capture','generation')});image,a=ItchRecovery.migrate(target.read_bytes(),a,implementation_identity());raw=build_bundle(image,a);s=self.session(raw);self.assertEqual(s.itch_session.depth,1);self.assertEqual(len(s.state()['book']['bids']),1)

 def test_authoring_preflights_budgets_before_base64_allocation(self):
  with patch('terminal.itch_product.MAX_BYTES',100),patch('terminal.itch_product.base64.b64encode',side_effect=AssertionError('No over-budget encoding'))as encoder:
   with self.assertRaisesRegex(ValueError,'field_budget'):build_bundle(self.original,self.source_a)
   encoder.assert_not_called()

 def test_app_import_is_lazy_and_actual_factory_selects_product_policy(self):
  command="from unittest.mock import patch;from terminal.server.engine import NativeSession;import importlib;guard=patch.object(NativeSession,'__init__',side_effect=AssertionError('No app construction'));guard.start();module=importlib.import_module('terminal.server.app');assert module._application is None"
  run=subprocess.run([sys.executable,'-c',command],cwd=Path(__file__).resolve().parents[1],capture_output=True,timeout=30);self.assertEqual(run.returncode,0,run.stderr.decode(errors='replace'))
  import ast
  tree=ast.parse((Path(__file__).parent/'server/app.py').read_text());factory=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='create_app')
  self.assertTrue(any(isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='native'for t in n.targets)and isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Name)and n.value.func.id=='select_product_session'for n in ast.walk(factory)))

 def test_offline_operator_migration_and_inspection_commands(self):
  root=Path(__file__).resolve().parents[1];raw=self.bundle();v=json.loads(raw);v['native_binary_sha256']='0'*64;old=encoded(v)
  with tempfile.TemporaryDirectory()as directory:
   path=Path(directory)/'old';path.write_bytes(old);os.chmod(path,0o600);target=Path(directory)/'new'
   command=[sys.executable,str(root/'scripts/manage_itch_session.py'),'migrate','--input',str(path),'--expected-sha256',digest(old),'--output',str(target)];run=subprocess.run(command,cwd=root,capture_output=True,text=True,timeout=30);self.assertEqual(run.returncode,0,run.stdout+run.stderr);receipt=json.loads(run.stdout);self.assertEqual(path.read_bytes(),old)
   inspect=[sys.executable,str(root/'scripts/manage_itch_session.py'),'inspect','--input',str(target),'--expected-sha256',receipt['output_sha256']];run=subprocess.run(inspect,cwd=root,capture_output=True,text=True,timeout=30);self.assertEqual(run.returncode,0,run.stdout+run.stderr);self.assertEqual(json.loads(run.stdout)['status'],'VALID')

 def test_sequential_steps_never_reapply_already_committed_suffix(self):
  s=self.session();original=ItchRecovery.process
  with patch.object(ItchRecovery,'process',autospec=True,side_effect=lambda owner,*a,**kw:original(owner,*a,**kw))as process:
   s.step();s.step();self.assertEqual(process.call_count,2)

 def test_exact_source_projection_supports_nonunit_native_tick_and_share_lots(self):
  with tempfile.TemporaryDirectory()as directory:
   target=Path(directory)/'image';run=subprocess.run([str(self.fixture),'--fixture-units',str(target)],capture_output=True,text=True,check=True,timeout=30);meta=json.loads(run.stdout);a=ItchAdmission(**{k:meta[k]for k in('artifact_sha256','contract_sha256','implementation_sha256','capture','generation')});image,a=ItchRecovery.migrate(target.read_bytes(),a,implementation_identity());raw=build_bundle(image,a);s=self.session(raw);native=s.itch_session.owner.book(0)['snapshot']['data']['book'];self.assertEqual(native['bids'][0]['price_ticks'],'33');self.assertEqual(native['bids'][0]['quantity'],'10');v=s.state();self.assertEqual(v['price_scale'],'10000');self.assertEqual(v['book']['bids'][0]['price_ticks'],'99');self.assertEqual(v['book']['bids'][0]['quantity'],'100');self.assertEqual(v['metrics']['bid_depth'],{'numerator':'100','denominator':'1'});self.assertEqual(v['provenance']['native_lot_size'],{'numerator':'10','denominator':'1'});self.assertEqual(v['metrics']['spread'],{'numerator':'3','denominator':'1'});self.assertEqual(v['metrics']['midprice'],{'numerator':'201','denominator':'2'})
