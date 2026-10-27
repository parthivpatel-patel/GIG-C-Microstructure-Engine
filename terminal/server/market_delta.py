"""Per-browser bounded projection;receipt numbers are local,not exchange sequences."""
class MarketProjection:
 def __init__(self):self.sequence=0;self.key=None;self.receipt=0
 def project(self,snapshot):
  key=(snapshot['generation'],tuple(snapshot['symbols']),tuple(snapshot['channels']))
  full=self.key!=key;sequence=self.sequence+1
  result=dict(snapshot)
  result['history']=snapshot['history'] if full else [r for r in snapshot['history'] if r['receipt_index']>self.receipt]
  result['browser_delta']={'schema':'gig.market.delta.v1','mode':'full' if full else 'delta','sequence':sequence,'base_sequence':self.sequence,'base_receipt':self.receipt,'history_status':[[r['receipt_index'],r['state'],r['receive_age_seconds']] for r in snapshot['history']]}
  self.key=key;self.receipt=snapshot['accepted_observations'];self.sequence=sequence
  return result
