"""Explicit server-owned supplied-XBRL product adapter. No provider or file reads.

Admission is an internal operation for an already authorized source collection;
there is deliberately no HTTP mutation/upload route or automatic cache substitute.
"""
import copy
from .xbrl_collection import FilingCollection
from .xbrl_instance import selected_financials,XBRLError,canonical,digest
from .xbrl_statements import select,MAX_OUTPUT
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

def company_contract(workspace,symbol,as_of,*,role=None,form='10-K',profile='legacy-v1'):
 if profile not in('legacy-v1','accuracy-extension-v2'):raise XBRLError('statement_profile_unsupported')
 identity=workspace.resolve(symbol);collection=workspace.xbrl_collections.get(symbol)
 if collection is None:
  from .xbrl_statement_v2 import statement as v2_statement
  statement=(select if profile=='legacy-v1'else v2_statement)({},identity.get('cik'),'UNAVAILABLE',digest({}),as_of,role=role,form=form)
  statement.pop('sha256');statement['reason']='NO_EXPLICITLY_ADMITTED_XBRL_COLLECTION';statement['sha256']=digest(statement)
 else:
  if identity.get('cik')!=collection.cik:raise XBRLError('xbrl_product_identity_changed')
  statement=collection.statement_at(as_of,role=role,form=form,profile=profile)
 result={'schema':'gig.backend.company_xbrl.v1','instrument':identity,'data_origin':statement['origin'],'statement_view':statement,'read_only':True,'provider_requested':False,'limitations':['Supplied XBRL profile,not complete financial statements or history','No companyfacts replacement or source authentication inferred','Missing source receipt stays unknown;exact values are not browser recalculations']}
 coordinator=workspace.filing_ingestors.get(symbol)
 if coordinator is not None:result['source_ingestion']=coordinator.status()
 if profile=='accuracy-extension-v2':result['schema']='gig.backend.company_xbrl.v2';result['profile']=profile
 result['sha256']=digest(result)
 if len(canonical(result))>MAX_OUTPUT:raise XBRLError('xbrl_product_output_budget')
 return result
