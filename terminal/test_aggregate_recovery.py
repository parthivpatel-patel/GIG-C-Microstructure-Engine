"""Real native aggregate-state import;no sockets,provider source or order IDs."""
import copy,json,unittest
import gig_microstructure as gig

class AggregateRecovery(unittest.TestCase):
 def book(self):
  b=gig._native.AggregateDepth(8,1048576)
  gig._checked(b.snapshot([{'price_ticks':'100','quantity':'7'},{'price_ticks':'99','quantity':'3'}],[{'price_ticks':'101','quantity':'9'}],'40'))
  gig._checked(b.update([{'price_ticks':'100','quantity':'6'}],[],'41'));return b
 def test_hot_import_retains_full_levels_revision_sequence_and_exact_metrics(self):
  b=self.book();image=json.loads(json.dumps(gig._checked(b.checkpoint())));r=gig._checked(gig._native.restore_aggregate(image,'8','1048576'))
  def state(x):return {k:v for k,v in gig._checked(x.state()).items()if not k.startswith('pmr_')}
  self.assertEqual(state(r),state(b))
  for owner in (b,r):gig._checked(owner.update([],[{'price_ticks':'101','quantity':'2'}],'42'))
  self.assertEqual(state(r),state(b));self.assertEqual(state(r)['revision'],'3')
 def test_malformed_checkpoint_wrong_contract_and_allocation_budget_are_atomic(self):
  b=self.book();clean=gig._checked(b.checkpoint())
  cases=[{**clean,'version':'2'},{**clean,'initialized':False},{**clean,'initialized':'true'},{**clean,'revision':'0'},{**clean,'bids':clean['bids']*2},{**clean,'extra':True}]
  for image in cases:
   with self.subTest(image=list(image)):
    with self.assertRaises(gig.EngineError):gig._checked(gig._native.restore_aggregate(image,'8','1048576'))
  for n,budget in [('7','1048576'),('8','1')]:
   with self.assertRaises(gig.EngineError):gig._checked(gig._native.restore_aggregate(clean,n,budget))
  self.assertEqual(gig._checked(b.checkpoint()),clean)
 def test_empty_uninitialized_import_does_not_invent_an_initial_snapshot(self):
  b=gig._native.AggregateDepth(8,1048576);image=gig._checked(b.checkpoint());r=gig._checked(gig._native.restore_aggregate(image,'8','1048576'))
  self.assertFalse(gig._checked(r.state())['initialized'])
  with self.assertRaises(gig.EngineError):gig._checked(r.update([],[]))
