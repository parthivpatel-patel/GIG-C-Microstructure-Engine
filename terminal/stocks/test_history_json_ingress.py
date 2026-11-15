"""Private source-revision JSON must remain unambiguous even with matching byte hashes."""
import hashlib,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from terminal.verification.artifacts import EvidenceError
from .history_store import HistoryStore,canonical
from .history import normalize
from .test_phase3 import bar,pages,source
from .history_backup import backup,restore
from .datasets import analyze_revisions

class HistoryJSONIngress(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)/'private';self.store=HistoryStore(self.root,clock=lambda:1000000.25);self.core=normalize('AAPL','1Min',pages([bar()]),source())
 def ambiguous(self,prefix=b'"symbol":"WRONG",'):
  raw=b'{'+prefix+canonical(self.core)[1:];revision=hashlib.sha256(raw).hexdigest()
  with self.store.connect()as db:db.execute('INSERT INTO snapshots VALUES(?,?,?,?,?)',(revision,'AAPL','1Min',1000000.25,raw))
  return revision
 def test_matching_revision_hash_does_not_authorize_conflicting_duplicate_source_keys(self):
  for prefix in(b'"symbol":"WRONG",',b'"\\u0073ymbol":"WRONG",'):
   revision=self.ambiguous(prefix)
   with self.assertRaisesRegex(EvidenceError,'duplicate_json_field'):self.store.read(revision)
 def test_selected_dataset_revision_uses_the_same_duplicate_aware_ingress(self):
  revision=self.ambiguous()
  with self.assertRaisesRegex(EvidenceError,'duplicate_json_field'):analyze_revisions(self.store,{'authored':revision},{'authored':'1'})
 def test_backup_revalidates_source_json_before_publishing_any_revision(self):
  self.ambiguous()
  with self.assertRaisesRegex(EvidenceError,'duplicate_json_field'):backup(self.store)
  self.assertFalse((self.root/'history.backup.sqlite3').exists());self.assertFalse((self.root/'history.backup.json').exists())
 def test_ambiguous_backup_manifest_rejects_before_copy_and_preserves_accepted_data(self):
  revision=self.store.save(self.core)['revision'];backup(self.store);manifest=self.root/'history.backup.json';manifest.write_bytes(b'{"schema":"WRONG",'+manifest.read_bytes()[1:])
  with patch('terminal.stocks.history_backup._staging',side_effect=AssertionError('NO_UNTRUSTED_COPY')):
   with self.assertRaisesRegex(EvidenceError,'duplicate_json_field'):restore(self.store)
  self.assertEqual(self.store.read(revision),self.core)
 def test_ordinary_revision_and_fractional_retention_clock_remain_compatible(self):
  revision=self.store.save(self.core)['revision'];self.assertEqual(self.store.list()[0]['retained_at_unix'],1000000.25);self.assertEqual(self.store.read(revision),self.core);backup(self.store);self.store.delete(revision);self.assertEqual(restore(self.store)['restored_revisions'],1);self.assertEqual(self.store.read(revision),self.core)

if __name__=='__main__':unittest.main(verbosity=2)
