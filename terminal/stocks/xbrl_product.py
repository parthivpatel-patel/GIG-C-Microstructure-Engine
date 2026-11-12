"""Explicit server-owned supplied-XBRL product adapter. No provider or file reads.

Admission is an internal operation for an already authorized source collection;
there is deliberately no HTTP mutation/upload route or automatic cache substitute.
"""
import copy
from .xbrl_collection import FilingCollection
from .xbrl_instance import selected_financials,XBRLError,canonical,digest
from .xbrl_statements import select
MAX_COMPANIES=8;MAX_BYTES=16*1024*1024

def admit(workspace,symbol,collection):
 identity=workspace.resolve(symbol)
 if type(collection)is not FilingCollection or identity.get('cik')!=collection.cik:raise XBRLError('xbrl_product_issuer_scope')
 # Detach caller-owned state. Admission must complete before any existing entry changes.
 if len(collection._filings)>32 or len(canonical(collection._filings))>MAX_BYTES:raise XBRLError('xbrl_product_memory_budget')
 clone=copy.deepcopy(collection)
 for parsed in clone._filings.values():selected_financials(parsed)
 candidate=dict(workspace.xbrl_collections);candidate[symbol]=clone
 if len(candidate)>MAX_COMPANIES or sum(len(canonical(c._filings))for c in candidate.values())>MAX_BYTES:raise XBRLError('xbrl_product_memory_budget')
 workspace.xbrl_collections=candidate
 return {'schema':'gig.company.xbrl.admission.v1','symbol':symbol,'issuer_cik':clone.cik,'collection_sha256':clone._identity(clone._filings),'origin':clone.origin,'provider_requested':False}

def company_contract(workspace,symbol,as_of,*,role=None,form='10-K'):
 identity=workspace.resolve(symbol);collection=workspace.xbrl_collections.get(symbol)
 if collection is None:
  statement=select({},identity.get('cik'),'UNAVAILABLE',digest({}),as_of,role=role,form=form)
  statement.pop('sha256');statement['reason']='NO_EXPLICITLY_ADMITTED_XBRL_COLLECTION';statement['sha256']=digest(statement)
 else:
  if identity.get('cik')!=collection.cik:raise XBRLError('xbrl_product_identity_changed')
  statement=collection.statement_at(as_of,role=role,form=form)
 result={'schema':'gig.backend.company_xbrl.v1','instrument':identity,'data_origin':statement['origin'],'statement_view':statement,'read_only':True,'provider_requested':False,'limitations':['Supplied XBRL profile,not complete financial statements or history','No companyfacts replacement or source authentication inferred','Missing source receipt stays unknown;exact values are not browser recalculations']}
 result['sha256']=digest(result);return result
