"""Authored-only fault tests. No provider, account, order or private dataset access."""
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from terminal.recording import save_authored, load_authored
from terminal.server.fixtures import EVENTS


class RecordingAdmission(unittest.TestCase):
    def save(self, root):
        return save_authored(root, 'sample', EVENTS, origin='HISTORICAL_SYNTHETIC', enabled=True)

    def rejects_fifo_in_child(self, root, module, function, filename):
        target = root / 'sample' / filename
        if target.exists():
            target.unlink()
        os.mkfifo(target, 0o600)
        code = f'''from {module} import {function}
import sys
try:{function}(sys.argv[1], 'sample')
except ValueError:print('REJECTED_NONREGULAR');sys.exit(0)
raise SystemExit('unsafe file was admitted')
'''
        result = subprocess.run([sys.executable, '-c', code, str(root)],
                                capture_output=True, text=True, timeout=2)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('REJECTED_NONREGULAR', result.stdout)

    def test_authored_manifest_fifo_rejected_without_waiting_for_writer(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d);self.save(root)
            self.rejects_fifo_in_child(root, 'terminal.recording', 'load_authored', 'manifest.json')

    def test_authored_events_fifo_rejected_without_waiting_for_writer(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d);self.save(root)
            self.rejects_fifo_in_child(root, 'terminal.recording', 'load_authored', 'events.jsonl')

    def test_l2_manifest_fifo_rejected_without_waiting_for_writer(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d);(root/'sample').mkdir(mode=0o700)
            self.rejects_fifo_in_child(root, 'terminal.l2_recording', 'load_l2', 'manifest.json')

    def test_catalog_manifest_fifo_rejected_without_waiting_for_writer(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d);(root/'sample').mkdir(mode=0o700)
            self.rejects_fifo_in_child(root, 'terminal.l2_playback', 'metadata', 'manifest.json')

    def test_ambiguous_duplicate_manifest_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.save(root);path=root/'sample/manifest.json'
            text=path.read_text();path.write_text(text[:-1]+',"complete":true}')
            with self.assertRaises(ValueError):load_authored(root,'sample')

    def test_nonobject_manifest_is_a_structured_validation_error(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.save(root);(root/'sample/manifest.json').write_text('[]')
            with self.assertRaises(ValueError):load_authored(root,'sample')

    def test_publish_syncs_staging_then_root_directory(self):
        seen=[];original=os.fsync
        def capture(fd):
            if stat.S_ISDIR(os.fstat(fd).st_mode):seen.append(os.readlink(f'/proc/self/fd/{fd}'))
            return original(fd)
        with tempfile.TemporaryDirectory() as d,patch('os.fsync',side_effect=capture):
            root=Path(d);self.save(root)
            self.assertEqual(len(seen),2)
            self.assertIn('.pending-',seen[0])
            self.assertEqual(seen[1],str(root))


class RecoveryBoundaries(unittest.TestCase):
    def save(self, root):
        return save_authored(root, 'sample', EVENTS, origin='HISTORICAL_SYNTHETIC', enabled=True)

    def test_capacity_scan_stops_at_eight_entries(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            for i in range(12):(root/f'x{i}').mkdir()
            original=os.scandir;seen=[]
            class Scan:
                def __enter__(self):self.raw=original(root);return self
                def __exit__(self,*_):self.raw.close()
                def __iter__(self):return self
                def __next__(self):value=next(self.raw);seen.append(value.name);return value
            with patch('terminal.recording.os.scandir',side_effect=lambda _path:Scan()):
                with self.assertRaisesRegex(ValueError,'dataset_budget'):self.save(root)
            self.assertEqual(len(seen),8)

    def test_disk_full_does_not_publish_partial_recording(self):
        import errno
        with tempfile.TemporaryDirectory() as d,patch('terminal.recording.os.fsync',side_effect=OSError(errno.ENOSPC,'authored disk full')):
            root=Path(d)
            with self.assertRaises(OSError):self.save(root)
            self.assertEqual(list(root.iterdir()),[])

    def test_staging_directory_sync_failure_does_not_publish(self):
        with tempfile.TemporaryDirectory() as d,patch('terminal.recording.sync_directory',side_effect=OSError('injected')):
            root=Path(d)
            with self.assertRaises(OSError):self.save(root)
            self.assertEqual(list(root.iterdir()),[])

    def test_postrename_sync_failure_is_explicitly_uncertain_and_never_overwrites(self):
        from terminal.recording import sync_directory
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            def fail_parent(path):
                if path==root:raise OSError('injected parent sync failure')
                sync_directory(path)
            with patch('terminal.recording.sync_directory',side_effect=fail_parent):
                with self.assertRaisesRegex(OSError,'publication_uncertain'):self.save(root)
            self.assertEqual(load_authored(root,'sample')[1],list(EVENTS))
            before=(root/'sample/events.jsonl').read_bytes()
            with self.assertRaisesRegex(ValueError,'recording_exists'):self.save(root)
            self.assertEqual((root/'sample/events.jsonl').read_bytes(),before)

    def interruption(self,after_rename):
        code='''import os,sys
from pathlib import Path
import terminal.recording as recording
from terminal.server.fixtures import EVENTS
original=recording.sync_directory
root=Path(sys.argv[1]);after=sys.argv[2]=='1'
def stop(path):
 if (path==root)==after:os._exit(72 if after else 71)
 original(path)
recording.sync_directory=stop
recording.save_authored(root,'sample',EVENTS,origin='HISTORICAL_SYNTHETIC',enabled=True)
'''
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            r=subprocess.run([sys.executable,'-c',code,str(root),'1' if after_rename else '0'],capture_output=True,timeout=3)
            self.assertEqual(r.returncode,72 if after_rename else 71,r.stderr)
            if after_rename:
                self.assertEqual(load_authored(root,'sample')[1],list(EVENTS))
            else:
                self.assertFalse((root/'sample').exists())
                with self.assertRaises(ValueError):load_authored(root,'sample')
                self.assertTrue(any(p.name.startswith('.pending-')for p in root.iterdir()))

    def test_process_exit_before_rename_leaves_only_unpublished_stage(self):self.interruption(False)
    def test_process_exit_after_rename_recovers_valid_recording(self):self.interruption(True)

    def test_payload_corruption_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.save(root);p=root/'sample/events.jsonl';p.write_bytes(p.read_bytes()+b'\n')
            with self.assertRaises(ValueError):load_authored(root,'sample')

    def test_duplicate_event_keys_rejected_even_with_matching_byte_digest(self):
        import hashlib
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.save(root);p=root/'sample/events.jsonl';lines=p.read_bytes().splitlines()
            value=json.loads(lines[0]);key=next(iter(value));lines[0]=lines[0][:-1]+b','+json.dumps(key).encode()+b':'+json.dumps(value[key]).encode()+b'}'
            raw=b'\n'.join(lines)+b'\n';p.write_bytes(raw);m=root/'sample/manifest.json';manifest=json.loads(m.read_bytes());manifest.update(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest());m.write_text(json.dumps(manifest))
            with self.assertRaises(ValueError):load_authored(root,'sample')

    def test_oversize_manifest_rejected_before_payload_read(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.save(root);(root/'sample/manifest.json').write_bytes(b' '*8193)
            with patch('terminal.verification.artifacts.os.read',side_effect=AssertionError('must not consume')):
                with self.assertRaises(ValueError):load_authored(root,'sample')

    def test_deep_manifest_is_structured_rejection(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.save(root);(root/'sample/manifest.json').write_text('['*2000+']'*2000)
            with self.assertRaises(ValueError):load_authored(root,'sample')

    def test_symlinked_parent_rejected_without_reading_target(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d);root=base/'actual';self.save(root);(base/'link').symlink_to(root,target_is_directory=True)
            with self.assertRaises(ValueError):load_authored(base/'link','sample')

    def test_recording_catalog_stays_responsive_with_fifo_manifest(self):
        code='''from starlette.testclient import TestClient
from terminal.server.app import create_app
from terminal.stocks.service import StockWorkspace
r=TestClient(create_app(stock_workspace=StockWorkspace(environment={})),base_url='http://127.0.0.1:8787').get('/api/v1/recordings')
assert r.status_code==200,r.text
assert len(r.json()['rejected'])==1,r.text
'''
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'sample').mkdir();os.mkfifo(root/'sample/manifest.json',0o600)
            r=subprocess.run([sys.executable,'-c',code],env={**os.environ,'GIG_TERMINAL_L2_RECORDINGS':str(root)},capture_output=True,text=True,timeout=5)
            self.assertEqual(r.returncode,0,r.stderr)


class BenchmarkOracles(unittest.TestCase):
    def test_nearest_rank_against_authored_sorted_reference(self):
        from scripts.qualify_production_performance import distribution
        value=distribution([100,10,70,30,20,40,90,60,80,50])
        self.assertEqual((value['p50_ns'],value['p95_ns'],value['p99_ns']),(50,100,100))
        self.assertEqual(value['samples'],10)

    def test_invalid_or_unresolved_latency_samples_reject(self):
        from scripts.qualify_production_performance import distribution
        for values in ([],[0],[-1],[True],[1.5]):
            with self.assertRaises(ValueError):distribution(values)

    def test_benchmark_resource_limits_admitted_before_io(self):
        from scripts.qualify_production_performance import qualify
        for kwargs in ({'orders':True},{'orders':257},{'observations':4097},{'repetitions':2},{'warmup':0}):
            with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):qualify('unused','unused',**kwargs)

    def test_benchmark_never_overwrites_existing_evidence(self):
        from scripts.qualify_production_performance import qualify
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'sentinel';path.write_text('preserve')
            with self.assertRaisesRegex(ValueError,'evidence_exists'):qualify('unused',d)
            self.assertEqual(path.read_text(),'preserve')

    def test_projection_oracle_detects_deliberately_corrupt_sequence(self):
        from scripts.qualify_production_performance import provider_trial
        from terminal.server.market_delta import MarketProjection
        original=MarketProjection.project
        def corrupt(self,value):
            result=original(self,value);result['browser_delta']['sequence']+=1;return result
        with patch.object(MarketProjection,'project',corrupt):
            with self.assertRaises(AssertionError):provider_trial(2)


class BackupDurability(unittest.TestCase):
    def store(self,root):
        from terminal.stocks.history_store import HistoryStore
        from terminal.stocks.history import normalize
        from terminal.stocks.test_phase3 import bar,pages,source
        store=HistoryStore(root/'private');core=normalize('AAPL','1Min',pages([bar()]),source())
        key=store.save(core)['revision'];return store,key,core

    def test_backup_acknowledgment_includes_parent_directory_sync(self):
        from terminal.stocks.history_backup import backup
        seen=[];original=os.fsync
        def capture(fd):
            if stat.S_ISDIR(os.fstat(fd).st_mode):seen.append(os.readlink(f'/proc/self/fd/{fd}'))
            return original(fd)
        with tempfile.TemporaryDirectory()as d:
            store,_,_=self.store(Path(d))
            with patch('os.fsync',side_effect=capture):backup(store)
            self.assertIn(str(store.path.parent),seen)

    def test_backup_deletion_includes_parent_directory_sync(self):
        from terminal.stocks.history_backup import backup,delete_backup
        seen=[];original=os.fsync
        def capture(fd):
            if stat.S_ISDIR(os.fstat(fd).st_mode):seen.append(os.readlink(f'/proc/self/fd/{fd}'))
            return original(fd)
        with tempfile.TemporaryDirectory()as d:
            store,_,_=self.store(Path(d));backup(store)
            with patch('os.fsync',side_effect=capture):delete_backup(store)
            self.assertIn(str(store.path.parent),seen)

    def test_uncertain_backup_ack_is_recoverable_without_overwriting(self):
        from terminal.stocks.history_backup import backup,restore
        with tempfile.TemporaryDirectory()as d:
            store,key,core=self.store(Path(d))
            with patch('terminal.stocks.history_backup._sync_directory',side_effect=OSError('injected')):
                with self.assertRaisesRegex(OSError,'publication_uncertain'):backup(store)
            with self.assertRaisesRegex(ValueError,'exists'):backup(store)
            store.delete(key);self.assertEqual(restore(store)['restored_revisions'],1)
            self.assertEqual(store.read(key),core)

    def test_stage_fsync_failure_leaves_live_database_unchanged(self):
        from terminal.stocks.history_backup import backup
        with tempfile.TemporaryDirectory()as d:
            store,key,core=self.store(Path(d))
            with patch('terminal.stocks.history_backup.os.fsync',side_effect=OSError('injected ENOSPC')):
                with self.assertRaises(OSError):backup(store)
            self.assertEqual(store.read(key),core)
            self.assertFalse((store.path.parent/'history.backup.sqlite3').exists())
            self.assertFalse(any(p.name.startswith('.history-stage-')for p in store.path.parent.iterdir()))

    def test_backup_delete_and_repeat_are_safe_and_idempotent(self):
        from terminal.stocks.history_backup import backup,delete_backup
        with tempfile.TemporaryDirectory()as d:
            store,key,core=self.store(Path(d));backup(store);delete_backup(store)
            self.assertTrue(delete_backup(store)['deleted'])
            self.assertEqual(store.read(key),core)
