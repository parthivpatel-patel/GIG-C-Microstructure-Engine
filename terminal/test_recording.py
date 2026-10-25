import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from terminal.recording import save_authored, load_authored, delete_authored
from terminal.server.fixtures import EVENTS

class Recording(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)/'records'
    def save(self):return save_authored(self.root,'authored-v1',EVENTS,origin='HISTORICAL_SYNTHETIC',enabled=True)
    def test_roundtrip_and_deletion(self):
        manifest=self.save();actual,events=load_authored(self.root,'authored-v1');self.assertEqual(actual,manifest);self.assertEqual(events,list(EVENTS));self.assertEqual(delete_authored(self.root,'authored-v1'),'authored-v1');self.assertFalse((self.root/'authored-v1').exists())
    def test_disabled_no_files(self):
        with self.assertRaises(ValueError):save_authored(self.root,'x',EVENTS,origin='HISTORICAL_SYNTHETIC')
        self.assertFalse(self.root.exists())
    def test_observed_refused_before_encode(self):
        with patch('terminal.recording.canonical',side_effect=AssertionError('must not encode')):
            with self.assertRaises(ValueError):save_authored(self.root,'x',EVENTS,origin='LIVE_OBSERVED',enabled=True)
        self.assertFalse(self.root.exists())
    def test_arbitrary_fixture_refused(self):
        with self.assertRaises(ValueError):save_authored(self.root,'x',[],origin='HISTORICAL_SYNTHETIC',enabled=True)
    def test_tamper_and_no_overwrite(self):
        self.save()
        with self.assertRaises(ValueError):self.save()
        path=self.root/'authored-v1'/'events.jsonl';path.write_bytes(path.read_bytes()+b'{}\n')
        with self.assertRaises(ValueError):load_authored(self.root,'authored-v1')
    def test_path_and_symlink(self):
        with self.assertRaises(ValueError):load_authored(self.root,'../no')
        self.save();(self.root/'linked').symlink_to(self.root/'authored-v1',target_is_directory=True)
        with self.assertRaises(ValueError):load_authored(self.root,'linked')
    def test_retention(self):
        self.save()
        with patch('terminal.recording.time.time',return_value=0):
            with self.assertRaises(ValueError):load_authored(self.root,'authored-v1')
            self.assertEqual(delete_authored(self.root,'authored-v1'),'authored-v1')
    def test_write_failure_rolls_back(self):
        with patch('terminal.recording.os.fsync',side_effect=OSError('injected')):
            with self.assertRaises(OSError):self.save()
        self.assertEqual(list(self.root.iterdir()),[])

if __name__=='__main__':unittest.main()
