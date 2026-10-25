"""Authored-only recording, interruption, storage failure and native replay oracles."""
import hashlib,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from .l2_recording import L2Writer,load_l2,replay_l2
from .providers.fixtures import EVENTS
from .providers.kraken import Permission,ProviderError
from .recording import canonical

class L2Recording(unittest.TestCase):
    def setUp(self):self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
    def write(self):
        writer=L2Writer(self.root,'authored',enabled=True,clock=lambda:100)
        for i,raw in enumerate(EVENTS):writer.append(raw,i)
        return writer.finish()
    def test_disabled_and_observed_permission_defaults(self):
        with self.assertRaisesRegex(ValueError,'disabled'):L2Writer(self.root,'a')
        with self.assertRaisesRegex(ValueError,'permission'):L2Writer(self.root,'a',enabled=True,origin='LIVE_OBSERVED')
        p=Permission(True,True,True,False,'authored-permission-negative-control')
        with self.assertRaisesRegex(ValueError,'retention'):L2Writer(self.root,'a',enabled=True,origin='LIVE_OBSERVED',permission=p)
        self.assertEqual(list(self.root.iterdir()),[])
    def test_roundtrip_native_exact_seek_and_source_order(self):
        m=self.write();loaded,rows=load_l2(self.root,'authored',clock=lambda:101)
        self.assertEqual(loaded,m);self.assertEqual([r['raw'] for r in rows],list(EVENTS))
        expected=hashlib.sha256(b''.join(canonical({'ordinal':i,'receive_monotonic_ns':str(i),'raw':raw})+b'\n' for i,raw in enumerate(EVENTS))).hexdigest()
        self.assertEqual(m['sha256'],expected)
        first=replay_l2(m,rows,1);self.assertEqual(first['native']['bids'][0]['quantity'],'200000000')
        second=replay_l2(m,rows,2);self.assertEqual(second['native']['bids'][0]['quantity'],'400000000')
        final=replay_l2(m,rows);self.assertEqual(final['native']['bids'][0]['price_ticks'],'9900000000')
        self.assertEqual(final,replay_l2(m,rows));self.assertFalse(final['complete_initialization'])
        self.assertEqual(final['origin'],'HISTORICAL_SYNTHETIC')
    def test_corrupt_recording_digest_detected(self):
        self.write();path=self.root/'authored/events.jsonl';path.write_bytes(path.read_bytes()+b' ')
        with self.assertRaisesRegex(ValueError,'digest'):load_l2(self.root,'authored',clock=lambda:101)
    def test_manifest_count_shift_detected(self):
        self.write();path=self.root/'authored/manifest.json';m=json.loads(path.read_bytes());m['records']+=1;path.write_bytes(canonical(m))
        with self.assertRaisesRegex(ValueError,'count'):load_l2(self.root,'authored',clock=lambda:101)
    def test_interrupted_stage_not_a_complete_log(self):
        writer=L2Writer(self.root,'authored',enabled=True);writer.append(EVENTS[0],1)
        with self.assertRaisesRegex(ValueError,'path'):load_l2(self.root,'authored')
        writer.abort();self.assertEqual(list(self.root.iterdir()),[])
    def test_disk_failure_never_publishes_manifest(self):
        writer=L2Writer(self.root,'authored',enabled=True);writer.append(EVENTS[0],1)
        with patch('terminal.l2_recording.os.fsync',side_effect=OSError('authored ENOSPC')):
            with self.assertRaises(OSError):writer.finish()
        self.assertEqual(list(self.root.iterdir()),[])
    def test_record_limit_abort_is_atomic(self):
        writer=L2Writer(self.root,'authored',enabled=True)
        with patch('terminal.l2_recording.MAX_RECORDS',1):
            writer.append(EVENTS[0],1)
            with self.assertRaisesRegex(ValueError,'budget'):writer.append(EVENTS[1],2)
        self.assertEqual(list(self.root.iterdir()),[])
    def test_byte_limit_abort(self):
        writer=L2Writer(self.root,'authored',enabled=True)
        with patch('terminal.l2_recording.MAX_BYTES',10):
            with self.assertRaisesRegex(ValueError,'budget'):writer.append(EVENTS[0],1)
        self.assertEqual(list(self.root.iterdir()),[])
    def test_receive_clock_regression_abort(self):
        writer=L2Writer(self.root,'authored',enabled=True);writer.append(EVENTS[0],2)
        with self.assertRaisesRegex(ValueError,'clock'):writer.append(EVENTS[1],1)
        self.assertEqual(list(self.root.iterdir()),[])
    def test_expiry_and_future_clock_rejected(self):
        self.write()
        for now in (99,100+86401):
            with self.assertRaisesRegex(ValueError,'expired'):load_l2(self.root,'authored',clock=lambda:now)
    def test_no_overwrite_no_traversal_symlinks(self):
        self.write()
        with self.assertRaisesRegex(ValueError,'exists'):L2Writer(self.root,'authored',enabled=True)
        with self.assertRaises(ValueError):L2Writer(self.root,'../escape',enabled=True)
        (self.root/'alias').symlink_to(self.root/'authored',target_is_directory=True)
        with self.assertRaisesRegex(ValueError,'path'):load_l2(self.root,'alias')
    def test_allocation_failure_aborts_unpublished_log(self):
        writer=L2Writer(self.root,'authored',enabled=True)
        with patch('terminal.l2_recording.canonical',side_effect=MemoryError()):
            with self.assertRaises(MemoryError):writer.append(EVENTS[0],1)
        self.assertEqual(list(self.root.iterdir()),[])
    def test_duplicate_manifest_fields_rejected(self):
        self.write();path=self.root/'authored/manifest.json'
        data=path.read_text();path.write_text(data[:-1]+',"records":5}')
        with self.assertRaisesRegex(ProviderError,'duplicate_json_key'):load_l2(self.root,'authored',clock=lambda:101)
    def test_seek_bounds_and_malformed_source(self):
        m=self.write();_,rows=load_l2(self.root,'authored',clock=lambda:101)
        for pos in (-1,6,True):
            with self.assertRaises(ValueError):replay_l2(m,rows,pos)
        rows[0]['raw']='{}'
        with self.assertRaises(ProviderError):replay_l2(m,rows)

if __name__=='__main__':unittest.main()
