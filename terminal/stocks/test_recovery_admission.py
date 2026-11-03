"""Independent corrupt-ledger admission fixtures. No real market input or provider."""
import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from .observation_store import ObservationStore, MAX_BYTES


def event():return {'origin':'HISTORICAL_SYNTHETIC','receipt_index':1,'symbol':'AAPL','kind':'quote','data':{'bid':'100','ask':'101'}}


class Admission(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.store=ObservationStore(self.temp.name,clock=lambda:100.,retention_seconds=10)
        self.store.append('a'*32,[event()])

    def replace_payload(self,change):
        with sqlite3.connect(self.store.path)as db:
            raw,parent=db.execute('SELECT payload,previous FROM records').fetchone()
            value=json.loads(raw);changed=change(value)
            raw=changed if type(changed)is bytes else json.dumps(value,sort_keys=True,separators=(',',':')).encode()
            digest=hashlib.sha256(bytes.fromhex(parent)+raw).hexdigest()
            db.execute('UPDATE records SET payload=?,digest=?',(raw,digest))
            db.execute("UPDATE meta SET value=? WHERE key='tail'",(digest,))

    def assert_preflight(self):
        original=sqlite3.connect;delivered=[]
        def connect(*a,**kw):
            connection=original(*a,**kw)
            def factory(cursor,row):
                columns=[c[0]for c in cursor.description]
                if columns==['capture','receipt','created','expires','payload','previous','digest']:delivered.append(len(row[4]) if type(row[4])is bytes else -1)
                return row
            connection.row_factory=factory;return connection
        with patch('terminal.stocks.observation_store.sqlite3.connect',side_effect=connect):
            with self.assertRaises(ValueError):self.store.recover()
        self.assertEqual(delivered,[],'Budget must reject before any full payload row enters Python')

    def test_row_cap_is_enforced_before_materialization(self):
        with sqlite3.connect(self.store.path)as db:
            db.execute('DELETE FROM records')
            db.executemany('INSERT INTO records(capture,receipt,created,expires,payload,previous,digest)VALUES(?,?,?,?,?,?,?)',
                [('b'*32,i,100.,110.,b'{}','0'*64,'0'*64)for i in range(1,10002)])
        self.assert_preflight()

    def test_total_payload_cap_is_enforced_before_materialization(self):
        with sqlite3.connect(self.store.path)as db:
            db.execute('DELETE FROM records')
            db.executemany('INSERT INTO records(capture,receipt,created,expires,payload,previous,digest)VALUES(?,?,?,?,?,?,?)',
                [('b'*32,i,100.,110.,b'x'*65536,'0'*64,'0'*64)for i in range(1,258)])
        self.assert_preflight()

    def test_individual_oversize_record_rejects_before_materialization(self):
        self.replace_payload(lambda value:value['event'].update(padding='x'*65536))
        self.assert_preflight()

    def test_nonblob_payload_rejects_before_materialization(self):
        with sqlite3.connect(self.store.path)as db:db.execute('UPDATE records SET payload=?',('not a blob',))
        self.assert_preflight()

    def test_nonobject_payload_is_structured_failure(self):
        self.replace_payload(lambda _:b'[]')
        with self.assertRaises(ValueError):self.store.recover()

    def test_unknown_origin_cannot_be_recovered_as_observed(self):
        self.store.allow_observed=True
        self.replace_payload(lambda value:value['event'].update(origin='UNDECLARED_ORIGIN'))
        with self.assertRaises(ValueError):self.store.recover()

    def test_invalid_retention_policy_is_rejected(self):
        self.replace_payload(lambda value:value['retention_policy'].update(seconds=999999))
        with self.assertRaises(ValueError):self.store.recover()

    def test_missing_anchor_is_structured_failure(self):
        with sqlite3.connect(self.store.path)as db:db.execute("DELETE FROM meta WHERE key='anchor'")
        with self.assertRaises(ValueError):self.store.recover()

    def test_corrupt_receipt_index_metadata_is_rejected(self):
        with sqlite3.connect(self.store.path)as db:db.execute("UPDATE meta SET value='999'WHERE key='receipt'")
        with self.assertRaises(ValueError):self.store.recover()

    def test_duplicate_json_is_rejected_even_with_consistent_chain_hash(self):
        self.replace_payload(lambda v:json.dumps(v).encode()[:-1]+b',"schema":"gig.iex.observation.v1"}')
        with self.assertRaises(ValueError):self.store.recover()

    def test_corrupt_database_bytes_are_structured_failure(self):
        self.store.path.write_bytes(b'NOT_A_SQLITE_DATABASE')
        with self.assertRaises(ValueError):self.store.recover()

    def test_valid_minimal_v1_envelope_remains_compatible(self):
        rows=self.store.recover();self.assertEqual(rows[0]['event'],event())
        self.assertEqual(rows[0]['classification'],'RETAINED_HISTORICAL_NOT_CURRENT')
        restarted=ObservationStore(self.temp.name,clock=lambda:100.)
        self.assertEqual(restarted.recover(),rows)

    def test_pruned_suffix_preserves_receipt_and_anchor(self):
        self.store.clock=lambda:111.;self.store.prune();self.assertEqual(self.store.recover(),[])
        self.store.append('a'*32,[{**event(),'receipt_index':2}])
        self.assertEqual(self.store.recover()[0]['event']['receipt_index'],2)

    def test_payload_validation_precedes_new_append(self):
        before=self.store.recover()
        bad={**event(),'receipt_index':2,'padding':'x'*65536}
        with self.assertRaises(ValueError):self.store.append('a'*32,[bad])
        self.assertEqual(self.store.recover(),before)

    def test_nonfinite_record_clock_is_rejected(self):
        self.replace_payload(lambda value:value.update(created_seconds=float('nan')))
        with self.assertRaises(ValueError):self.store.recover()

    def test_huge_metadata_rejected_before_payload_materialization(self):
        with sqlite3.connect(self.store.path)as db:db.execute("UPDATE meta SET value=? WHERE key='anchor'",('x'*100000,))
        self.assert_preflight()

    def test_receipt_discontinuity_with_consistent_hashes_rejects(self):
        self.store.append('a'*32,[{**event(),'receipt_index':2}])
        with sqlite3.connect(self.store.path)as db:
            raw,parent=db.execute('SELECT payload,previous FROM records WHERE receipt=2').fetchone();v=json.loads(raw);v['event']['receipt_index']=4
            raw=json.dumps(v,sort_keys=True,separators=(',',':')).encode();digest=hashlib.sha256(bytes.fromhex(parent)+raw).hexdigest()
            db.execute('UPDATE records SET receipt=4,payload=?,digest=? WHERE receipt=2',(raw,digest));db.execute("UPDATE meta SET value='4'WHERE key='receipt'");db.execute("UPDATE meta SET value=?WHERE key='tail'",(digest,))
        with self.assertRaises(ValueError):self.store.recover()

    def test_actual_sqlite_full_rolls_back_and_restart_remains_valid(self):
        from contextlib import contextmanager
        original=self.store._connect;before=self.store.recover()
        @contextmanager
        def capped():
            with original()as db:
                count=db.execute('PRAGMA page_count').fetchone()[0];db.execute('PRAGMA max_page_count='+str(count));yield db
        self.store._connect=capped
        with self.assertRaisesRegex(ValueError,'storage_failure'):
            self.store.append('a'*32,[{**event(),'receipt_index':2,'padding':'x'*16000}])
        self.store._connect=original
        self.assertEqual(ObservationStore(self.temp.name,clock=lambda:100.).recover(),before)

    def test_recovery_rejection_does_not_rewrite_evidence(self):
        self.replace_payload(lambda _:b'[]');before=self.store.path.read_bytes()
        with self.assertRaises(ValueError):self.store.recover()
        self.assertEqual(self.store.path.read_bytes(),before)

    def test_read_snapshot_and_concurrent_writer_preserve_old_prefix(self):
        from concurrent.futures import ThreadPoolExecutor
        import threading
        other=ObservationStore(self.temp.name,clock=lambda:100.,retention_seconds=10)
        original=self.store._admit_rows;ready=threading.Event()
        def admission(db,*a,**kw):
            value=original(db,*a,**kw);ready.set();return value
        def write():
            self.assertTrue(ready.wait(2));other.append('a'*32,[{**event(),'receipt_index':2}])
        with patch.object(self.store,'_admit_rows',side_effect=admission),ThreadPoolExecutor(max_workers=1)as pool:
            future=pool.submit(write);rows=self.store.recover();future.result(timeout=5)
        self.assertEqual(len(rows),1);self.assertEqual(len(self.store.recover()),2)

    def test_restart_does_not_silently_recreate_missing_anchor(self):
        with sqlite3.connect(self.store.path)as db:db.execute("DELETE FROM meta WHERE key='anchor'")
        with self.assertRaises(ValueError):ObservationStore(self.temp.name,clock=lambda:100.)

    def test_restart_rejection_preserves_missing_table_evidence(self):
        with sqlite3.connect(self.store.path)as db:db.execute('DROP TABLE records')
        before=self.store.path.read_bytes()
        with self.assertRaises(ValueError):ObservationStore(self.temp.name,clock=lambda:100.)
        self.assertEqual(self.store.path.read_bytes(),before)

    def test_row_metadata_is_bounded_before_materialization(self):
        for column in ('capture','previous','digest'):
            with self.subTest(column=column):
                with sqlite3.connect(self.store.path)as db:
                    original=db.execute('SELECT '+column+' FROM records').fetchone()[0]
                    db.execute('UPDATE records SET '+column+'=?',('x'*100000,))
                self.assert_preflight()
                with sqlite3.connect(self.store.path)as db:db.execute('UPDATE records SET '+column+'=?',(original,))

    def test_row_sql_types_are_checked_before_materialization(self):
        for column,bad in (('capture',b'a'*32),('receipt',None),('created','bad'),('expires','bad'),('previous',b'0'*64),('digest',b'0'*64)):
            with self.subTest(column=column):
                with sqlite3.connect(self.store.path)as db:
                    original=db.execute('SELECT '+column+' FROM records').fetchone()[0]
                    db.execute('UPDATE records SET '+column+'=?',(bad,))
                self.assert_preflight()
                with sqlite3.connect(self.store.path)as db:db.execute('UPDATE records SET '+column+'=?',(original,))

    def test_ambiguous_duplicate_metadata_keys_are_rejected(self):
        with sqlite3.connect(self.store.path)as db:
            db.execute('DELETE FROM records');db.execute('DROP TABLE meta');db.execute('CREATE TABLE meta(key TEXT,value TEXT)')
            db.executemany('INSERT INTO meta VALUES(?,?)',[('anchor','0'*64),('tail','0'*64),('anchor','0'*64)])
        with self.assertRaises(ValueError):self.store.recover()

    def test_extreme_json_integer_clock_is_structured_failure(self):
        self.replace_payload(lambda value:value.update(created_seconds=10**400))
        with self.assertRaises(ValueError):self.store.recover()
