"""Explicitly designated source statement roles at independent acceptance vintages.

Role designations are caller metadata, not inferred accounting equivalence. Rows,
ordering, concepts and values come only from the selected original supplied DTS
and filing. No cross-filing filling or additive amendment reconstruction.
"""
import copy,re
from . import sec
from .xbrl_product import company_contract
from .xbrl_lineage import filing_lineage
from .xbrl_binding import bind_declarations
from .xbrl_calculation_report import _identity,_source_fact,_context
from .xbrl_statement_v2 import statement
from .xbrl_instance import XBRLError,digest,canonical
from .xbrl_relationships import PROFILE as REL_PROFILE,PARENT

KINDS=('balance_sheet','income_statement','cash_flow_statement')
SCHEMA='gig.backend.company_statement_set.v1'
MAX_OUTPUT=1024*1024;MAX_VINTAGES=8;MAX_HISTORY=2*1024*1024
ACCESSION=re.compile(r'[0-9]{10}-[0-9]{2}-[0-9]{6}\Z')

def _finish(body,limit=None):
 if limit is None:limit=MAX_OUTPUT
 body['sha256']=digest(body)
 if len(canonical(body))>limit:raise XBRLError('statement_set_output_budget')
 return body

def _inputs(graphs,bindings):
 for mapping in(graphs,bindings):
  if type(mapping)is not dict or len(mapping)>32 or any(type(a)is not str or not ACCESSION.fullmatch(a)for a in mapping):raise XBRLError('statement_set_source_mapping')
 for mapping in bindings.values():
  if type(mapping)is not dict or set(mapping)!=set(KINDS)or any(role is not None and(type(role)is not str or not 1<=len(role)<=512)for role in mapping.values()):raise XBRLError('statement_set_role_bindings')
  roles=[role for role in mapping.values()if role is not None]
  if len(roles)!=len(set(roles)):raise XBRLError('statement_set_ambiguous_role_designation')

def _revalidate(parsed,graph):
 _identity(parsed,'canonical_sha256','statement_set_parsed_identity')
 _identity(graph,'canonical_sha256','statement_set_dts_identity')
 if parsed.get('dts_corroboration',{}).get('dts_sha256')!=graph['canonical_sha256']:raise XBRLError('statement_set_existing_dts_binding')
 if graph.get('structural_closure')is not True or graph.get('unresolved')or graph.get('definition'):raise XBRLError('statement_set_dts_scope')
 if any(type(u)is not dict or u.get('feature')!='NON_PRESENTATION_LINK_NOT_INTERPRETED'for u in graph.get('unsupported_semantics',[])):raise XBRLError('statement_set_unsupported_dts')
 contexts=parsed['contexts'];units=parsed['units'];facts=parsed['facts'];issuer=parsed['source']['issuer_cik']
 if len(contexts)>512 or len(units)>128 or len(facts)>4096 or parsed.get('unsupported_nodes'):raise XBRLError('statement_set_instance_scope')
 for ctx in contexts.values():_context(ctx,issuer)
 for unit in units.values():
  if type(unit)is not dict or set(unit)!={'numerator','denominator','semantic_sha256'}or digest({k:unit[k]for k in('numerator','denominator')})!=unit['semantic_sha256']:raise XBRLError('statement_set_unit_identity')
 seen=set()
 for fact in facts:
  _source_fact(parsed,fact)
  if fact['source_fact_id']in seen:raise XBRLError('statement_set_duplicate_source_identity')
  seen.add(fact['source_fact_id'])
  if fact['context_ref']not in contexts or fact['context_sha256']!=contexts[fact['context_ref']]['semantic_sha256']:raise XBRLError('statement_set_fact_context')
  if fact['unit_ref']is not None and(fact['unit_ref']not in units or fact['unit_sha256']!=units[fact['unit_ref']]['semantic_sha256']):raise XBRLError('statement_set_fact_unit')
 rels=graph.get('effective_relationships');_identity(rels,'sha256','statement_set_relationship_identity')
 if rels.get('profile')!=REL_PROFILE or type(rels.get('networks'))is not list or len(rels['networks'])>64:raise XBRLError('statement_set_relationship_scope')
 documents=graph['documents']
 if not 1<=len(documents)<=16:raise XBRLError('statement_set_document_budget')
 docs={d['uri']:d['sha256']for d in documents}
 if len(docs)!=len(documents):raise XBRLError('statement_set_document_identity')
 for net in rels['networks']:
  if len(net['arcs'])>4096:raise XBRLError('statement_set_arc_budget')
  for arc in net['arcs']:
   if not arc['provenance']or any(docs.get(p['source_uri'])!=p['source_sha256']for p in arc['provenance']):raise XBRLError('statement_set_arc_source')
   for concept in(arc['from'],arc['to']):
    entry=graph['concepts'].get(concept)
    if entry is None or not entry['source_documents']or any(uri not in docs for uri in entry['source_documents']):raise XBRLError('statement_set_concept_source')
 return bind_declarations(parsed,graph)

def company_statement_set(workspace,symbol,as_of,dts_graphs,role_bindings,*,form='10-K',expected_collection_sha256=None):
 """Reconstruct three separately designated source views from one selected filing.

 role_bindings maps accession to exactly KINDS, each an explicit role or None.
 These designations are labels, not automatic proof of a complete GAAP statement.
 """
 _inputs(dts_graphs,role_bindings)
 selected=company_contract(workspace,symbol,as_of,form=form,profile='accuracy-extension-v2')['statement_view']
 collection=workspace.visible_xbrl_collection(symbol);collection_sha=selected['collection_sha256']
 if expected_collection_sha256 is not None and expected_collection_sha256!=collection_sha:raise XBRLError('statement_set_stale_collection')
 result={'schema':SCHEMA,'instrument':copy.deepcopy(workspace.resolve(symbol)),'as_of':as_of,'cutoff_ns':selected['cutoff_ns'],'form_family':form,'collection_sha256':collection_sha,'status':'UNAVAILABLE','reason':selected['reason'],'source_filing':copy.deepcopy(selected['source_filing']),'parsed_sha256':None,'dts_sha256':None,'role_bindings_sha256':None,'lineage':None,'statements':{},'read_only':True,'provider_requested':False,'complete_statements':False,'complete_history':False,'designation_policy':'Explicit caller role designations,not inferred statement classification or accounting equivalence','selection_policy':'One latest acceptance-qualified filing;all supplied amendment ancestors required;no cross-filing filling','limitations':['Presentation and declaration evidence establishes source structure,not complete GAAP statements','No inferred GAAP aliases,accounting equivalence,restatement status or missing financial values','Dimensioned/default-dependent/opaque contexts remain outside consolidated statement rows']}
 if selected['status']=='AMBIGUOUS':result['reason']='AMBIGUOUS_LATEST_FILING';return _finish(result)
 source=selected['source_filing']
 if source is None or collection is None:return _finish(result)
 accession=source['accession'];lineage=filing_lineage(collection,accession,as_of);result['lineage']=lineage
 if lineage['status']!='SUPPLIED_CHAIN_RESOLVED':result['reason']='EXPLICIT_AMENDMENT_CHAIN_UNRESOLVED';return _finish(result)
 if accession not in dts_graphs:result['reason']='ORIGINAL_DTS_NOT_SUPPLIED';return _finish(result)
 if accession not in role_bindings:result['reason']='ROLE_BINDINGS_NOT_SUPPLIED';return _finish(result)
 graph=dts_graphs[accession];parsed=collection._filings[accession];bound=_revalidate(parsed,graph)
 result.update(parsed_sha256=parsed['canonical_sha256'],dts_sha256=graph['canonical_sha256'],role_bindings_sha256=digest({'issuer_cik':collection.cik,'accession':accession,'dts_sha256':graph['canonical_sha256'],'roles':role_bindings[accession]}))
 filings=dict(collection._filings);filings[accession]=bound;available=0
 for kind in KINDS:
  role=role_bindings[accession][kind]
  if role is None:result['statements'][kind]={'role':None,'status':'UNAVAILABLE','reason':'ROLE_NOT_DESIGNATED','view':None};continue
  nets=[n for n in graph['effective_relationships']['networks']if n['kind']=='presentation'and n['role']==role]
  if len(nets)>1:raise XBRLError('statement_set_ambiguous_network')
  if nets and nets[0]['arcrole']!=PARENT:raise XBRLError('statement_set_presentation_arcrole')
  view=statement(filings,collection.cik,collection.origin,collection_sha,as_of,role=role,form=form)
  # Existing per-source period bounds must never masquerade as complete coverage.
  if view.get('truncated_periods'):raise XBRLError('statement_set_period_budget')
  state=view['status'];reason=view['reason']
  if state=='AVAILABLE'and not view['periods']:state='UNAVAILABLE';reason='NO_ELIGIBLE_REPORTED_PERIODS'
  available+=state=='AVAILABLE'
  result['statements'][kind]={'role':role,'status':state,'reason':reason,'view':view}
 if available:result.update(status='AVAILABLE'if available==len(KINDS)else'PARTIAL',reason=None if available==len(KINDS)else'SOME_DESIGNATED_STATEMENTS_UNAVAILABLE')
 else:result['reason']='NO_DESIGNATED_STATEMENT_AVAILABLE'
 return _finish(result)

def company_statement_history(workspace,symbol,cutoffs,dts_graphs,role_bindings,*,form='10-K',expected_collection_sha256=None):
 if type(cutoffs)is not list or not 1<=len(cutoffs)<=MAX_VINTAGES:raise XBRLError('statement_history_cutoff_budget')
 instants=[sec.acceptance_ns(at)for at in cutoffs]
 if any(a>=b for a,b in zip(instants,instants[1:])):raise XBRLError('statement_history_cutoff_order')
 entries=[];previous=None;identity=expected_collection_sha256
 for cutoff in cutoffs:
  packet=company_statement_set(workspace,symbol,cutoff,dts_graphs,role_bindings,form=form,expected_collection_sha256=identity)
  if identity is None:identity=packet['collection_sha256']
  source=packet['source_filing'];accession=None if source is None else source['accession']
  transition='UNAVAILABLE'if packet['status']=='UNAVAILABLE'else'FIRST_AVAILABLE'if previous is None else'UNCHANGED_SOURCE'if previous==accession else'SOURCE_CHANGED'
  entries.append({'transition':transition,'previous_accession':previous,'packet':packet})
  if len(canonical(entries))>MAX_HISTORY:raise XBRLError('statement_history_output_budget')
  if packet['status']!='UNAVAILABLE':previous=accession
 return _finish({'schema':'gig.backend.company_statement_history.v1','symbol':symbol,'collection_sha256':identity,'entries':entries,'complete_history':False,'read_only':True,'provider_requested':False,'policy':'Independent explicit acceptance cutoffs;source changes are not inferred accounting restatements'},MAX_HISTORY)
