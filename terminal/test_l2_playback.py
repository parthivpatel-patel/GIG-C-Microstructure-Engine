"""Independent native recorded prefixes, guarded API and interruption/durability checks."""
from copy import deepcopy
import hashlib,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from starlette.testclient import TestClient
from .l2_playback import RecordedSession,save_fixture,discover,delete_session
from .l2_recording import load_l2
from .recording import canonical
from .server.app import create_app

class Playback(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
    def test_versioned_native_receipts_timestamps_and_exact_prefixes(self):
        m=save_fixture(self.root);self.assertEqual(m['schema'],'gig.terminal.l2_log.v2')
        self.assertFalse(m['market_session_complete']);self.assertEqual(m['venue'],'Kraken')
        _,rows=load_l2(self.root,'authored-l2-v2');self.assertIsNone(rows[0]['receive_unix_ns'])
        self.assertEqual(rows[0]['normalized']['native_event']['bids'][0]['price_ticks'],'10000000000')
        session=RecordedSession(self.root,'authored-l2-v2')
        for pos,qty in [(1,'200000000'),(2,'400000000')]:
            state=session.view(pos,False,1);self.assertEqual(state['book']['bids'][0]['quantity'],qty)
            self.assertEqual(state['origin'],'HISTORICAL_SYNTHETIC');self.assertFalse(state['feed']['real_time'])
        self.assertEqual(session.view(3,False,1)['last_event']['trades'][0]['source_timestamp_ns'],'1767225600000000001')
        self.assertEqual(session.view(5,False,1)['book']['bids'][0]['price_ticks'],'9900000000')
        self.assertEqual(session.view(2,False,1)['replay_time_ns'],'50000000')
    def test_last_record_stops_playback_without_an_extra_tick(self):
        from .server.engine import NativeSession
        save_fixture(self.root);native=NativeSession();native.recorded_session=RecordedSession(self.root,'authored-l2-v2')
        native.position=4;native.playing=True;native.step()
        self.assertEqual(native.position,5);self.assertFalse(native.playing)
    def test_cache_views_are_owned_and_deterministic(self):
        save_fixture(self.root);a=RecordedSession(self.root,'authored-l2-v2');b=RecordedSession(self.root,'authored-l2-v2')
        self.assertEqual(a.frames,b.frames);view=a.view(1,False,1);view['book']['bids'][0]['quantity']='999'
        self.assertEqual(a.view(1,False,1)['book']['bids'][0]['quantity'],'200000000')
        self.assertLess(a.cache_bytes,8*1024*1024)
    def test_normalized_corruption_rejected_even_if_hash_rewritten(self):
        save_fixture(self.root);events=self.root/'authored-l2-v2/events.jsonl'
        rows=[json.loads(x) for x in events.read_bytes().splitlines()]
        rows[0]['normalized']['native_event']['bids'][0]['quantity']='1'
        payload=b''.join(canonical(x)+b'\n' for x in rows);events.write_bytes(payload)
        path=self.root/'authored-l2-v2/manifest.json';m=json.loads(path.read_bytes())
        m['sha256']=hashlib.sha256(payload).hexdigest();m['bytes']=len(payload);path.write_bytes(canonical(m))
        with self.assertRaisesRegex(ValueError,'normalization_mismatch'):RecordedSession(self.root,'authored-l2-v2')
    def test_catalog_pending_invalid_and_delete(self):
        save_fixture(self.root);(self.root/'.pending-l2-authored').mkdir();(self.root/'invalid').mkdir()
        data=discover(self.root);self.assertEqual(len(data['sessions']),1);self.assertEqual(len(data['rejected']),1)
        self.assertEqual(data['sessions'][0]['status'],'AVAILABLE')
        delete_session(self.root,'authored-l2-v2');self.assertEqual(discover(self.root)['sessions'],[])
    def test_observed_permission_checked_before_payload_read(self):
        save_fixture(self.root);path=self.root/'authored-l2-v2/manifest.json';m=json.loads(path.read_bytes());m['origin']='LIVE_OBSERVED';path.write_bytes(canonical(m))
        (self.root/'authored-l2-v2/events.jsonl').unlink()
        self.assertEqual(discover(self.root)['sessions'][0]['status'],'BLOCKED_PERMISSION')
        with self.assertRaisesRegex(ValueError,'observed_processing_permission'):RecordedSession(self.root,'authored-l2-v2')
    def test_expired_cached_session_is_not_servable_and_storage_prunes(self):
        from .l2_playback import prune_expired
        m=save_fixture(self.root);session=RecordedSession(self.root,'authored-l2-v2')
        future=m['created_unix_seconds']+m['retention_seconds']+1
        with patch('terminal.l2_playback.time.time',return_value=future):
            view=session.view(1,True,1);self.assertEqual(view['origin'],'UNAVAILABLE')
            self.assertEqual(session.frames,[]);self.assertEqual(session.event_count,0)
            self.assertEqual(prune_expired(self.root)['deleted_count'],1)
        self.assertEqual(list(self.root.iterdir()),[])
    def test_pending_deadline_survives_interrupted_short_retention(self):
        from .l2_recording import L2Writer
        from .l2_playback import prune_expired
        from .providers.fixtures import EVENTS
        writer=L2Writer(self.root,'short',enabled=True,clock=lambda:100,retention_seconds=1)
        writer.append(EVENTS[0],0);writer.stream.close()  # Simulate an unfinalized writer.
        self.assertEqual(prune_expired(self.root,now=102)['deleted_count'],1)
        self.assertEqual(list(self.root.iterdir()),[])
    def test_active_pending_capture_excluded_from_expired_cleanup(self):
        from .l2_playback import prune_expired
        stage=self.root/'.pending-l2-authored';stage.mkdir();os.utime(stage,(0,0))
        self.assertEqual(prune_expired(self.root,now=100000,active_stage=stage)['deleted_count'],0)
        self.assertEqual(prune_expired(self.root,now=100000)['deleted_count'],1)
    def test_fsync_stage_and_parent_after_rename(self):
        calls=[]
        with patch('terminal.l2_recording.sync_directory',side_effect=lambda p:calls.append(Path(p).name)):
            save_fixture(self.root)
        self.assertEqual(len(calls),3);self.assertTrue(all(x.startswith('.pending-l2-') for x in calls[:2]));self.assertEqual(calls[-1],self.root.name)
    def test_false_l3_or_session_completeness_rejected(self):
        save_fixture(self.root);path=self.root/'authored-l2-v2/manifest.json';original=json.loads(path.read_bytes())
        for key in ('complete_initialization','market_session_complete'):
            m=dict(original);m[key]=True;path.write_bytes(canonical(m))
            with self.assertRaisesRegex(ValueError,'false_completeness'):RecordedSession(self.root,'authored-l2-v2')
    def test_prefix_cache_budget_refusal(self):
        save_fixture(self.root)
        with patch('terminal.l2_playback.MAX_CACHE_BYTES',1):
            with self.assertRaisesRegex(ValueError,'cache_budget'):RecordedSession(self.root,'authored-l2-v2')
    def test_process_interruption_before_and_after_atomic_rename(self):
        script='''import os,sys
from pathlib import Path
from terminal.l2_playback import save_fixture
if sys.argv[2]=='before':
 import terminal.l2_recording as log
 log.os.fsync=lambda fd:os._exit(77)
else:
 original=Path.rename
 def renamed(self,target):
  original(self,target);os._exit(77)
 Path.rename=renamed
save_fixture(sys.argv[1])
'''
        for phase in ('before','after'):
            target=self.root/phase;target.mkdir()
            result=subprocess.run([sys.executable,'-c',script,str(target),phase],timeout=15,capture_output=True)
            self.assertEqual(result.returncode,77,result.stderr.decode())
            if phase=='before':self.assertEqual(discover(target)['sessions'],[])
            else:self.assertEqual(RecordedSession(target,'authored-l2-v2').event_count,5)

class PlaybackAPI(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        env=patch.dict(os.environ,{'GIG_TERMINAL_L2_RECORDINGS':self.tmp.name,'GIG_TERMINAL_ALLOWED_ORIGINS':'http://127.0.0.1:8787'})
        env.start();self.addCleanup(env.stop);self.c=TestClient(create_app(),base_url='http://127.0.0.1:8787')
        self.c.__enter__();self.addCleanup(self.c.__exit__,None,None,None)
    def post(self,path,data):return self.c.post('/api/v1/'+path,headers={'Origin':'http://127.0.0.1:8787'},json=data)
    def test_session_selection_step_seek_restart_and_source_switch(self):
        self.assertEqual(self.post('recording',{'action':'save_l2_fixture'}).status_code,200)
        self.assertEqual(len(self.c.get('/api/v1/recordings').json()['sessions']),1)
        self.assertEqual(self.post('recording',{'action':'load_l2'}).status_code,200)
        state=self.post('control',{'action':'step'}).json();self.assertEqual(state['position'],1)
        self.assertEqual(state['book']['bids'][0]['quantity'],'200000000');self.assertEqual(state['origin'],'HISTORICAL_SYNTHETIC')
        state=self.post('control',{'action':'seek','value':2}).json();self.assertEqual(state['book']['bids'][0]['quantity'],'400000000')
        self.assertEqual(self.post('control',{'action':'speed','value':4}).json()['speed'],4)
        self.assertTrue(self.post('control',{'action':'play'}).json()['playing'])
        self.assertFalse(self.post('control',{'action':'pause'}).json()['playing'])
        self.assertEqual(self.post('control',{'action':'restart'}).json()['position'],0)
        state=self.post('control',{'action':'dataset','value':'terminal-authored-v2'}).json();self.assertEqual(state['position'],20)
        self.assertEqual(state['provider'],'authored')
    def test_failed_load_origin_and_paths_cannot_change_replay(self):
        self.assertEqual(self.c.post('/api/v1/recording',json={'action':'save_l2_fixture'}).status_code,403)
        for payload in ({'action':'load_l2','identity':'../escape'},{'action':'load_l2','path':'private'}, {'action':'load_l2','identity':'missing'}):
            self.assertIn(self.post('recording',payload).status_code,(400,409))
        self.assertEqual(self.c.get('/api/v1/state').json()['position'],20)
    def test_observed_capture_disabled_before_any_file_or_socket(self):
        response=self.post('recording',{'action':'start_l2'})
        self.assertEqual(response.status_code,409)
        self.assertEqual(list(Path(self.tmp.name).iterdir()),[])
        self.assertEqual(self.c.get('/api/v1/state').json()['mode'],'HISTORICAL_REPLAY')
    def test_delete_session_does_not_mutate_owned_playback(self):
        self.post('recording',{'action':'save_l2_fixture'});self.post('recording',{'action':'load_l2'})
        self.assertEqual(self.post('recording',{'action':'delete_l2'}).status_code,200)
        self.assertEqual(self.post('control',{'action':'seek','value':5}).json()['book']['bids'][0]['price_ticks'],'9900000000')

if __name__=='__main__':unittest.main()
