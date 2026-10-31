"""Authored subprocess interruption checks, not power-loss or provider recovery."""
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

from terminal.stocks.history import normalize
from terminal.stocks.history_store import HistoryStore
from terminal.stocks.history_backup import backup, restore
from terminal.stocks.test_phase3 import bar, pages, source


class Recovery(unittest.TestCase):
    def test_abrupt_exit_during_restore_preserves_destination_then_restart_restores(self):
        child = '''
import os, sys
from terminal.stocks.history_store import HistoryStore
from terminal.stocks import history_backup as m
original=m._copy
calls=0
def stop(source, target):
    global calls
    calls+=1
    if calls==1:return original(source,target)
    def progress(status,left,total):
        if left:os._exit(73)
    source.backup(target,pages=1,progress=progress)
    raise AssertionError('fixture must contain multiple SQLite pages')
m._copy=stop
m.restore(HistoryStore(sys.argv[1]))
'''
        with tempfile.TemporaryDirectory() as directory:
            store = HistoryStore(Path(directory) / 'private')
            old = normalize('AAPL', '1Min', pages([bar()]), source())
            old_key = store.save(old)['revision']
            backup(store)
            store.delete(old_key)
            new = normalize('AAPL', '1Min', pages([bar(close='102')]), source())
            new_key = store.save(new)['revision']
            result = subprocess.run([sys.executable, '-c', child, str(store.path.parent)],
                                    timeout=10, capture_output=True)
            self.assertEqual(result.returncode, 73, result.stderr)
            restarted = HistoryStore(store.path.parent)
            self.assertEqual(restarted.read(new_key), new)
            with self.assertRaises(ValueError):restarted.read(old_key)
            self.assertEqual(restore(restarted)['restored_revisions'], 1)
            self.assertEqual(HistoryStore(store.path.parent).read(old_key), old)
            with self.assertRaises(ValueError):restarted.read(new_key)

    def test_interrupted_backup_without_manifest_is_not_accepted_or_overwritten(self):
        child = '''
import os,sys
from terminal.stocks.history_store import HistoryStore
from terminal.stocks import history_backup as m
original=m.os.open
def stop(path,*args,**kwargs):
    if str(path).endswith('history.backup.json'):os._exit(74)
    return original(path,*args,**kwargs)
m.os.open=stop
m.backup(HistoryStore(sys.argv[1]))
'''
        with tempfile.TemporaryDirectory() as directory:
            store = HistoryStore(Path(directory) / 'private')
            core = normalize('AAPL', '1Min', pages([bar()]), source())
            key = store.save(core)['revision']
            result = subprocess.run([sys.executable, '-c', child, str(store.path.parent)],
                                    timeout=10, capture_output=True)
            self.assertEqual(result.returncode, 74, result.stderr)
            self.assertTrue((store.path.parent / 'history.backup.sqlite3').exists())
            with self.assertRaises((OSError, ValueError)):restore(store)
            with self.assertRaisesRegex(ValueError, 'exists'):backup(store)
            self.assertEqual(HistoryStore(store.path.parent).read(key), core)

    def test_outer_backup_digest_cannot_hide_corrupt_internal_revision(self):
        with tempfile.TemporaryDirectory() as directory:
            store = HistoryStore(Path(directory) / 'private')
            core = normalize('AAPL', '1Min', pages([bar()]), source())
            key = store.save(core)['revision']
            backup(store)
            database = store.path.parent / 'history.backup.sqlite3'
            with sqlite3.connect(database) as connection:
                connection.execute('UPDATE snapshots SET payload=?', (b'{"authored_corruption":true}',))
            manifest_path = store.path.parent / 'history.backup.json'
            manifest = json.loads(manifest_path.read_bytes())
            raw = database.read_bytes()
            manifest.update(sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
            manifest_path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, 'revision'):restore(store)
            self.assertEqual(HistoryStore(store.path.parent).read(key), core)
