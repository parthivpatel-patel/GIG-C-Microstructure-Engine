"""Original-source accounting relationships and independently selected statements.

Explicit issuer role labels and essence-alias arcs never create a financial fact,
GAAP metric,missing value or additive amendment. Original bytes are mandatory.
"""
import copy,re
from decimal import Decimal,InvalidOperation
from fractions import Fraction
from . import sec
from .xbrl_instance import X,tag,digest,canonical,parse_instance,validate_manifest,XBRLError
from .xbrl_dts import EMBEDDED_PROFILE,_supplied_documents,discover,uri
from .xbrl_product import company_contract
from .xbrl_lineage import filing_lineage
from .xbrl_statement_set import KINDS,ACCESSION
from .xbrl_types import RESTRICTION_PROFILE,_resolve,_value_check
from .xbrl_accuracy import calculation_duplicates,calculation_consistency
from .xbrl_accounting_relationships import extract_accounting_relationships,_extract
from .xbrl_dts_source_audit import reconstruct_admitted_inline

MAX_OUTPUT=1024*1024;MAX_PERIODS=12;MAX_CONCEPTS=128

def _finish(result):
 result['sha256']=digest(result)
 if len(canonical(result))>MAX_OUTPUT:raise XBRLError('accounting_statement_output_budget')
 return result

def _number(fact,parsed,graph):
 decl=graph['concepts'][fact['concept']]['declaration'];ctx=parsed['contexts'][fact['context_ref']]
 if decl['abstract']or decl['substitution_group']!=tag(X,'item')or decl['period_type']!=ctx['period']['kind']or ctx['dimensions']or ctx['opaque_segment']or ctx['period']['end']is None or fact['unit_ref']is None:raise XBRLError('accounting_statement_numeric_scope')
 if fact['nil']and not decl['nillable']:raise XBRLError('accounting_statement_nil_not_declared')
 if decl['type'] is None:raise XBRLError('accounting_statement_missing_declared_type')
 base,path=_resolve(decl['type'],graph.get('type_declarations',{}),RESTRICTION_PROFILE)
 lexical=fact['lexical_value'].strip(' \t\r\n')
 if not fact['nil']and(len(lexical)>64 or not re.fullmatch(r'[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)',lexical)):raise XBRLError('accounting_statement_numeric_lexical')
 value=None if fact['nil']else sec.exact(Decimal(lexical));_value_check({**fact,'value':value},base,path,parsed['units'])
 return value

def _rows(concepts,period,period_facts,parsed,graph,networks,ctx_by_sha,document_hashes):
 rows=[];points={}
 for concept in concepts:
  entry=graph['concepts'][concept];decl=entry['declaration'];facts=period_facts.get(concept,[])
  row={'concept':concept,'status':'MISSING','reason':'NO_REPORTED_FACT','value':None,'unit':None,'facts':copy.deepcopy(facts),'numeric_facts':[],'classification':{'basis':'ORIGINAL_SOURCE_DECLARATION','concept':concept,'declared_type':decl['type'],'period_type':decl['period_type'],'balance':decl['balance'],'accounting_metric':None,'declaration_documents':[{'uri':u,'sha256':document_hashes[u]}for u in entry['source_documents']]},'essence_concept':None,'equivalence_status':'NO_SOURCE_EQUIVALENCE','accounting_relationships':[]}
  values={};unsupported=False
  for f in facts:
   try:value=_number(f,parsed,graph)
   except (XBRLError,ValueError,InvalidOperation):unsupported=True;continue
   values[f['source_fact_id']]=value;row['numeric_facts'].append({'source_fact_id':f['source_fact_id'],'value':value,'original_lexical_value':f['lexical_value'],'context_sha256':f['context_sha256'],'unit_sha256':f['unit_sha256']})
   points.setdefault((concept,f['context_sha256'],f['unit_sha256'],parsed['contexts'][f['context_ref']]['identifier_lexical']),[]).append({**f,'value':value})
  numbers={Fraction(v)for v in values.values()if v is not None};units={f['unit_sha256']for f in facts};nil=any(v is None for v in values.values())
  if unsupported or decl['abstract']:row.update(status='UNSUPPORTED',reason='DECLARATION_OR_CONTEXT_OUTSIDE_NUMERIC_PROFILE')
  elif len(numbers)>1 or len(units)>1 or numbers and nil:row.update(status='CONFLICTING',reason='CONTRADICTORY_REPORTED_VALUES_OR_UNITS')
  elif numbers:row.update(status='SUPPORTED',reason=None,value=next(v for v in values.values()if v is not None),unit=copy.deepcopy(parsed['units'][facts[0]['unit_ref']]))
  elif facts:row['reason']='NIL_REPORTED'
  essences=set();states=[];equality_checks=[]
  for net in networks:
   for arc in net['arcs']:
    if net['kind']=='essence-alias'and arc['to']!=concept or net['kind']=='requires-element'and arc['from']!=concept:continue
    checks=[]
    for check in arc['checks']:
     context=ctx_by_sha.get(check.get('context_sha256'))
     if context is None or tuple(context['period'][k]for k in('start','end'))==period:checks.append(copy.deepcopy(check))
    row['accounting_relationships'].append({'kind':net['kind'],'role':net['role'],'from':arc['from'],'to':arc['to'],'declaration_constraints':copy.deepcopy(arc['declaration_constraints']),'checks':checks,'provenance':copy.deepcopy(arc['provenance'])})
    if net['kind']=='essence-alias':essences.add(arc['from']);states.extend(c['status']for c in checks);equality_checks.extend(checks)
  if len(essences)>1:row.update(status='UNSUPPORTED',reason='MULTIPLE_SOURCE_ESSENCE_CANDIDATES',value=None,unit=None,equivalence_status='AMBIGUOUS_SOURCE_RELATIONSHIPS')
  elif essences:
   row['essence_concept']=next(iter(essences));row['classification']['basis']='ORIGINAL_ESSENCE_ALIAS_RELATIONSHIP_AND_DECLARATION'
   row['equivalence_status']='CONFLICTING_REPORTED_VALUES'if 'CONFLICTING_REPORTED_VALUES'in states else'UNSUPPORTED_ASPECTS'if 'UNSUPPORTED_ASPECTS'in states else'MISSING_COUNTERPART'if 'MISSING_COUNTERPART'in states or not states else'SOURCE_EQUIVALENCE_VERIFIED'if all(c.get('standards_value_equality_established')is True for c in equality_checks)else'SOURCE_RELATIONSHIP_REPORTED_EQUAL'
   if row['equivalence_status']=='CONFLICTING_REPORTED_VALUES':row.update(status='CONFLICTING',reason='SOURCE_ESSENCE_ALIAS_VALUE_CONFLICT',value=None,unit=None)
  rows.append(row)
 return rows,points

def _section(parsed,graph,relations,binding):
 role=binding['presentation_role'];accounting_role=binding['accounting_role'];result={'presentation_role':role,'accounting_role':accounting_role,'status':'UNAVAILABLE','reason':'PRESENTATION_ROLE_NOT_DESIGNATED','periods':[],'relationships':[]}
 if role is None:return result
 nets=[n for n in graph['effective_relationships']['networks']if n['kind']=='presentation'and n['role']==role]
 if len(nets)!=1:result['reason']='PRESENTATION_ROLE_NOT_IN_SELECTED_FILING';return result
 net=nets[0]
 if not net['usable']:result['reason']='PRESENTATION_NETWORK_UNSUPPORTED';return result
 accounting=[n for n in relations['networks']if n['role']==accounting_role]
 if accounting_role is not None and not accounting:result['reason']='ACCOUNTING_ROLE_NOT_IN_SELECTED_FILING';return result
 children={};concepts=set()
 for arc in net['arcs']:children.setdefault(arc['from'],[]).append(arc['to']);concepts.update((arc['from'],arc['to']))
 if not concepts:result['reason']='EMPTY_PRESENTATION_NETWORK';return result
 if len(concepts)>MAX_CONCEPTS:raise XBRLError('accounting_statement_concept_budget')
 order=[];seen=set();pending=list(reversed(net['roots']))
 while pending:
  concept=pending.pop()
  if concept in seen:continue
  seen.add(concept);order.append(concept);pending.extend(reversed(children.get(concept,[])))
 if seen!=concepts:raise XBRLError('accounting_statement_unreachable_concept')
 facts_by_period={}
 for fact in parsed['facts']:
  if fact['concept'] not in concepts:continue
  aspect=parsed['contexts'][fact['context_ref']]['period']
  if aspect['end'] is None:continue
  key=(aspect['start'],aspect['end'])
  if key not in facts_by_period:
   if len(facts_by_period)>=MAX_PERIODS:raise XBRLError('accounting_statement_period_budget')
   facts_by_period[key]={}
  reported=facts_by_period[key].setdefault(fact['concept'],[])
  if len(reported)>=8:raise XBRLError('accounting_statement_fact_budget')
  reported.append(fact)
 ctx_by_sha={value['semantic_sha256']:value for value in parsed['contexts'].values()}
 document_hashes={source['uri']:source['sha256'] for source in graph['documents']}
 for period in sorted(facts_by_period,key=lambda p:(p[1],p[0]or''),reverse=True):
  rows,points=_rows(order,period,facts_by_period[period],parsed,graph,accounting,ctx_by_sha,document_hashes);checks=[]
  for cn in graph['effective_relationships']['networks']:
   if cn['kind']!='calculation'or cn['role']!=role:continue
   if not cn['usable']:checks.append({'status':'UNSUPPORTED','issues':copy.deepcopy(cn['issues'])});continue
   parents={}
   for arc in cn['arcs']:parents.setdefault(arc['from'],[]).append(arc)
   for parent,arcs in sorted(parents.items()):
    if len(arcs)>128:raise XBRLError('accounting_statement_term_budget')
    aspects=sorted({(c,u,i)for concept,c,u,i in points if concept in{parent,*[a['to']for a in arcs]}})
    for context,unit,identifier in aspects:
     parent_facts=points.get((parent,context,unit,identifier));terms=[]
     for arc in arcs:
      fs=points.get((arc['to'],context,unit,identifier));terms.append({'concept':arc['to'],'weight':int(arc['weight']['numerator']),'accuracy':calculation_duplicates(fs)if fs else None})
     check=calculation_consistency(calculation_duplicates(parent_facts)if parent_facts else None,terms)
     checks.append({'parent':parent,'context_sha256':context,'identifier_lexical':identifier,'unit_sha256':unit,'calculation':check,'relationship_provenance':[copy.deepcopy(a['provenance'])for a in arcs]})
     if len(checks)>128:raise XBRLError('accounting_statement_calculation_budget')
  result['periods'].append({'start':period[0],'end':period[1],'rows':rows,'calculations':checks})
 result.update(status='AVAILABLE'if facts_by_period else'UNAVAILABLE',reason=None if facts_by_period else'NO_SOURCE_PERIODS',relationships=copy.deepcopy(net['arcs']))
 return result

def company_accounting_statements(workspace,symbol,as_of,source_inputs,role_bindings,*,form='10-K',expected_collection_sha256=None):
 packet,_,_=_accounting_sources(workspace,symbol,as_of,source_inputs,role_bindings,form=form,expected_collection_sha256=expected_collection_sha256)
 return packet

def _accounting_sources(workspace,symbol,as_of,source_inputs,role_bindings,*,form,expected_collection_sha256):
 """Return the packet and the very same source artifacts that passed the audit."""
 for mapping in(source_inputs,role_bindings):
  if type(mapping)is not dict or len(mapping)>32 or any(type(k)is not str or not ACCESSION.fullmatch(k)for k in mapping):raise XBRLError('accounting_statement_input_mapping')
 for bindings in role_bindings.values():
  if type(bindings)is not dict or set(bindings)!=set(KINDS):raise XBRLError('accounting_statement_role_binding')
  for binding in bindings.values():
   if type(binding)is not dict or set(binding)!={'presentation_role','accounting_role'}or any(v is not None and(type(v)is not str or not 1<=len(v)<=512)for v in binding.values()):raise XBRLError('accounting_statement_role_binding')
  presentations=[v['presentation_role']for v in bindings.values()if v['presentation_role']is not None]
  if len(presentations)!=len(set(presentations)):raise XBRLError('accounting_statement_ambiguous_presentation_roles')
 view=company_contract(workspace,symbol,as_of,form=form,profile='accuracy-extension-v2')['statement_view'];collection=workspace.xbrl_collections.get(symbol);identity=view['collection_sha256']
 if expected_collection_sha256 is not None and expected_collection_sha256!=identity:raise XBRLError('accounting_statement_stale_collection')
 result={'schema':'gig.backend.company_accounting_statements.v1','instrument':copy.deepcopy(workspace.resolve(symbol)),'as_of':as_of,'cutoff_ns':view['cutoff_ns'],'form_family':form,'collection_sha256':identity,'status':'UNAVAILABLE','reason':view['reason'],'source_filing':copy.deepcopy(view['source_filing']),'admitted_parsed_sha256':None,'original_parsed_sha256':None,'dts_sha256':None,'lineage':None,'accounting_report':None,'statements':{},'read_only':True,'provider_requested':False,'complete_statements':False,'complete_history':False,'policy':'Explicit original-source relationships and role designations;no GAAP aliases,fact filling or additive amendment reconstruction'}
 if view['status']=='AMBIGUOUS':result['reason']='AMBIGUOUS_LATEST_FILING';return _finish(result),None,None
 source=view['source_filing']
 if source is None or collection is None:return _finish(result),None,None
 accession=source['accession'];result['lineage']=filing_lineage(collection,accession,as_of)
 if result['lineage']['status']!='SUPPLIED_CHAIN_RESOLVED':result['reason']='EXPLICIT_AMENDMENT_CHAIN_UNRESOLVED';return _finish(result),None,None
 if accession not in source_inputs or accession not in role_bindings:result['reason']='SELECTED_ORIGINALS_OR_ROLE_BINDINGS_NOT_SUPPLIED';return _finish(result),None,None
 entry=source_inputs[accession];stored=collection._filings[accession]
 if stored.get('schema')=='gig.sec.xbrl.inline_set.v1':
  coordinator=getattr(workspace,'filing_ingestors',{}).get(symbol)
  has_plan=coordinator is not None and accession in coordinator.plans
  planned_identity=coordinator.plans[accession].get('inline_manifest_sha256')if has_plan else None
  parsed,graph,audit=reconstruct_admitted_inline(entry,stored,allow_observed=collection.allow_observed,
      planned_identity=planned_identity,has_plan=has_plan)
  relations=_extract(parsed,graph,entry['taxonomy_documents'],audit,embedded_profile=entry['embedded_profile'])
 else:
  parsed,graph,relations=_plain_sources(entry,stored,source,allow_observed=collection.allow_observed)
 if relations.get('complete_definition_scope')is not True:raise XBRLError('accounting_statement_definition_scope')
 result.update(accounting_report=relations,original_parsed_sha256=parsed['canonical_sha256'],admitted_parsed_sha256=stored['canonical_sha256'],dts_sha256=graph['canonical_sha256'])
 for kind in KINDS:result['statements'][kind]=_section(parsed,graph,relations,role_bindings[accession][kind])
 available=sum(v['status']=='AVAILABLE'for v in result['statements'].values());result.update(status='AVAILABLE'if available==3 else'PARTIAL'if available else'UNAVAILABLE',reason=None if available==3 else'SOME_SOURCE_VIEWS_UNAVAILABLE')
 return _finish(result),parsed,graph

def _plain_sources(entry,stored,source,*,allow_observed):
 required={'raw','manifest','concepts','instance_uri','documents'}
 if type(entry)is not dict or not required<=entry.keys()<=required|{'embedded_profile'}:
  raise XBRLError('accounting_statement_original_recipe')
 embedded=entry.get('embedded_profile')
 if embedded not in (None,EMBEDDED_PROFILE):raise XBRLError('accounting_statement_embedded_profile')
 if type(entry['raw'])is not bytes or len(entry['raw'])>2*1024*1024 or type(entry['documents'])is not list or len(entry['documents'])>16:raise XBRLError('accounting_statement_original_budget')
 if any(type(d)is not dict or type(d.get('raw'))is not bytes for d in entry['documents'])or len(entry['raw'])+sum(len(d['raw'])for d in entry['documents'])>8*1024*1024:raise XBRLError('accounting_statement_original_budget')
 # Compare immutable source and grant receipts before interpreting supplied XML.
 receipt=validate_manifest(entry['raw'],entry['manifest'],allow_observed)
 if canonical(receipt)!=canonical(source):raise XBRLError('accounting_statement_admitted_source_mismatch')
 instance_uri=uri(entry['instance_uri'])
 if source['source_url'] is not None and instance_uri!=source['source_url']:
  raise XBRLError('dts_audit_original_uri_scope')
 supplied=_supplied_documents(entry['documents'])
 if len(supplied)!=len(entry['documents']):raise XBRLError('dts_audit_duplicate_original_uri')
 if 'dts_corroboration' in stored:
  retained=stored['dts_corroboration']['documents']
  if {r['uri']:r['sha256'] for r in retained}!={key:r['sha256'] for key,r in supplied.items()}:
   raise XBRLError('accounting_statement_admitted_dts_mismatch')
 parsed=parse_instance(entry['raw'],entry['manifest'],entry['concepts'],allow_observed=allow_observed)
 if parsed['concept_profile_sha256']!=stored['concept_profile_sha256']:
  raise XBRLError('accounting_statement_admitted_concept_profile_mismatch')
 if canonical(parsed['source'])!=canonical(source)or any(canonical(parsed[k])!=canonical(stored[k])for k in('facts','contexts','units')):raise XBRLError('accounting_statement_admitted_source_mismatch')
 graph=discover(entry['raw'],entry['instance_uri'],source['source_sha256'],entry['documents'],origin=source['origin'],allow_observed=allow_observed,permission_reference=entry['manifest']['permission_reference'],embedded_profile=embedded)
 if 'dts_corroboration'in stored and stored['dts_corroboration']['dts_sha256']!=graph['canonical_sha256']:raise XBRLError('accounting_statement_admitted_dts_mismatch')
 relations=extract_accounting_relationships(parsed,graph,entry['raw'],entry['documents'],manifest=entry['manifest'],concepts=entry['concepts'],instance_uri=instance_uri,allow_observed=allow_observed,embedded_profile=embedded)
 return parsed,graph,relations

def company_accounting_history(workspace,symbol,cutoffs,source_inputs,role_bindings,*,form='10-K',expected_collection_sha256=None):
 if type(cutoffs)is not list or not 1<=len(cutoffs)<=8:raise XBRLError('accounting_history_cutoff_budget')
 instants=[sec.acceptance_ns(at)for at in cutoffs]
 if any(a>=b for a,b in zip(instants,instants[1:])):raise XBRLError('accounting_history_cutoff_order')
 entries=[];previous=None;identity=expected_collection_sha256
 for at in cutoffs:
  packet=company_accounting_statements(workspace,symbol,at,source_inputs,role_bindings,form=form,expected_collection_sha256=identity)
  if identity is None:identity=packet['collection_sha256']
  accession=None if packet['source_filing']is None else packet['source_filing']['accession']
  transition='UNAVAILABLE'if packet['status']=='UNAVAILABLE'else'FIRST_AVAILABLE'if previous is None else'UNCHANGED_SOURCE'if accession==previous else'SOURCE_CHANGED'
  entries.append({'previous_accession':previous,'transition':transition,'packet':packet})
  if len(canonical(entries))>2*1024*1024:raise XBRLError('accounting_history_output_budget')
  if packet['status']!='UNAVAILABLE':previous=accession
 result={'schema':'gig.backend.company_accounting_history.v1','symbol':symbol,'collection_sha256':identity,'entries':entries,'complete_history':False,'read_only':True,'provider_requested':False,'policy':'Independent explicit acceptance vintages;no inferred restatement or cross-filing values'};result['sha256']=digest(result)
 if len(canonical(result))>2*1024*1024:raise XBRLError('accounting_history_output_budget')
 return result
