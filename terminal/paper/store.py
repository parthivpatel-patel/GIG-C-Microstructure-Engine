"""Bounded private SQLite intent state,commit-before-send and hash-chained receipts.

Owner-controlled filesystem;hashes detect corruption,not a malicious rewrite of
the entire database. This journal is separate from the native research journal.
"""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import stat

from .contracts import PaperError, MAX_ORDERS, MAX_AUDIT, STATES, canonical, client_id, intent, integer

MAX_DB = 16 * 1024 * 1024
MAX_STATE = 256 * 1024
APP_ID = 1195984720


class IntentStore:
    def __init__(self, directory, *, before_commit=None):
        self.root = Path(directory).absolute()
        if any(p.is_symlink() for p in (self.root, *self.root.parents)):
            raise PaperError('paper_store_symlink')
        self.root.mkdir(mode=0o700, parents=False, exist_ok=True)
        meta = self.root.stat()
        if meta.st_uid != os.getuid() or meta.st_mode & 0o077:
            raise PaperError('paper_store_private_directory_required')
        self.path = self.root / 'paper-demo.sqlite3'
        self.before_commit = before_commit
        fd = os.open(self.path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        try:
            s = os.fstat(fd)
            if not stat.S_ISREG(s.st_mode) or s.st_uid != os.getuid() or s.st_nlink != 1 or s.st_mode & 0o077 or s.st_size > MAX_DB:
                raise PaperError('paper_store_private_file_required')
            new = s.st_size == 0
        finally:
            os.close(fd)
        with self.connection() as db:
            if new:
                db.executescript('PRAGMA application_id=1195984720; PRAGMA user_version=1;'
                                 'CREATE TABLE state(id INTEGER PRIMARY KEY CHECK(id=1),payload BLOB NOT NULL,digest TEXT NOT NULL);'
                                 'CREATE TABLE audit(seq INTEGER PRIMARY KEY,payload BLOB NOT NULL,previous TEXT NOT NULL,digest TEXT NOT NULL);'
                                 'CREATE TABLE fake(id INTEGER PRIMARY KEY CHECK(id=1),payload BLOB NOT NULL,digest TEXT NOT NULL);')
                value = {'schema': 'gig.paper.state.v1', 'profile': 'fake-paper-v1', 'kill': True,
                         'clock_ms': 0, 'snapshot_revision': 0, 'orders': {}}
                self._save(db, value, 'INITIALIZED')
            self._load(db)

    @contextmanager
    def connection(self):
        db = None
        try:
            if self.path.is_symlink() or self.path.stat().st_size > MAX_DB:
                raise PaperError('paper_store_file_boundary')
            db = sqlite3.connect(self.path, timeout=2)
            db.execute('PRAGMA synchronous=FULL')
            db.execute('PRAGMA max_page_count=4096')
            with db:
                yield db
        except (sqlite3.Error, OSError):
            raise PaperError('paper_storage_unavailable') from None
        finally:
            if db is not None:
                db.close()

    def _load(self, db):
        if db.execute('PRAGMA application_id').fetchone() != (APP_ID,) or db.execute('PRAGMA user_version').fetchone() != (1,) or db.execute('PRAGMA quick_check').fetchone() != ('ok',):
            raise PaperError('paper_store_integrity')
        row = db.execute('SELECT payload,digest FROM state WHERE id=1').fetchone()
        if row is None:
            raise PaperError('paper_store_integrity')
        raw, digest = row
        if type(raw) is not bytes or len(raw) > MAX_STATE or hashlib.sha256(raw).hexdigest() != digest:
            raise PaperError('paper_store_digest')
        try:
            value = json.loads(raw)
        except (ValueError, TypeError, UnicodeError):
            raise PaperError('paper_store_contract') from None
        self._validate(value)
        previous = '0' * 64
        audit = db.execute('SELECT seq,payload,previous,digest FROM audit ORDER BY seq LIMIT ?', (MAX_AUDIT + 1,)).fetchall()
        if not 1 <= len(audit) <= MAX_AUDIT:
            raise PaperError('paper_audit_capacity_or_integrity')
        for i, (seq, payload, parent, receipt) in enumerate(audit, 1):
            if type(seq) is not int or type(payload) is not bytes or len(payload) > 512 or type(parent) is not str or type(receipt) is not str or seq != i or parent != previous or hashlib.sha256(parent.encode() + payload).hexdigest() != receipt:
                raise PaperError('paper_audit_chain')
            previous = receipt
        try:
            if json.loads(audit[-1][1])['state_sha256'] != digest:
                raise PaperError('paper_audit_state_mismatch')
        except (ValueError, TypeError, KeyError, UnicodeError):
            raise PaperError('paper_audit_state_mismatch') from None
        return value

    @staticmethod
    def _validate(value):
        try:
            if type(value) is not dict or set(value) != {'schema', 'profile', 'kill', 'clock_ms', 'snapshot_revision', 'orders'} or value['schema'] != 'gig.paper.state.v1' or value['profile'] != 'fake-paper-v1' or type(value['kill']) is not bool or type(value['orders']) is not dict or len(value['orders']) > MAX_ORDERS:
                raise PaperError('paper_store_contract')
            integer(value['clock_ms'], 0, 2**63 - 1); integer(value['snapshot_revision'])
            for request, record in value['orders'].items():
                if type(record) is not dict or set(record) != {'client_id', 'intent', 'state', 'filled_qty', 'filled_notional_cents', 'broker_id', 'uncertain'} or record['intent'] != intent(record['intent']) or record['client_id'] != client_id(value['profile'], request, record['intent']) or record['state'] not in STATES or type(record['uncertain']) is not bool:
                    raise PaperError('paper_store_order_contract')
                integer(record['filled_qty'], 0, int(record['intent']['quantity']))
                integer(record['filled_notional_cents'])
                if record['uncertain'] != (record['state'] in ('SUBMITTED', 'CANCEL_REQUESTED', 'UNKNOWN')):
                    raise PaperError('paper_store_uncertain_contract')
                broker = record['broker_id']
                if broker is not None and (type(broker) is not str or not 1 <= len(broker) <= 100 or any(ord(c) < 33 or ord(c) > 126 for c in broker)):
                    raise PaperError('paper_store_broker_contract')
        except (ValueError, TypeError, KeyError):
            raise PaperError('paper_store_contract') from None

    def _save(self, db, value, event):
        self._validate(value)
        count = db.execute('SELECT count(*) FROM audit').fetchone()[0]
        if count >= MAX_AUDIT:
            raise PaperError('paper_audit_capacity')
        raw = canonical(value)
        if len(raw) > MAX_STATE:
            raise PaperError('paper_state_capacity')
        digest = hashlib.sha256(raw).hexdigest()
        previous = db.execute('SELECT digest FROM audit ORDER BY seq DESC LIMIT 1').fetchone()
        parent = previous[0] if previous else '0' * 64
        payload = canonical({'event': event, 'state_sha256': digest, 'clock_ms': value['clock_ms']})
        db.execute('INSERT OR REPLACE INTO state VALUES(1,?,?)', (raw, digest))
        db.execute('INSERT INTO audit VALUES(?,?,?,?)', (count + 1, payload, parent, hashlib.sha256(parent.encode() + payload).hexdigest()))

    def mutate(self, event, operation):
        with self.connection() as db:
            db.execute('BEGIN IMMEDIATE')
            value = self._load(db)
            result = operation(value)
            self._save(db, value, event)
            if self.before_commit:
                self.before_commit()
            return result

    def read(self):
        with self.connection() as db:
            db.execute('BEGIN')
            return self._load(db)

    def audit_receipt(self):
        with self.connection() as db:
            db.execute('BEGIN')
            self._load(db)
            count = db.execute('SELECT count(*) FROM audit').fetchone()[0]
            tail = db.execute('SELECT digest FROM audit ORDER BY seq DESC LIMIT 1').fetchone()[0]
        return {'entries': count, 'maximum_entries': MAX_AUDIT, 'chain_sha256': tail,
                'file_bytes': self.path.stat().st_size, 'maximum_file_bytes': MAX_DB}
