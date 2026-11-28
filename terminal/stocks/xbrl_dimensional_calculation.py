"""Opt-in positive explicit-dimensional calculation binding over original sources.

Derived aspects are calculation keys only;original facts/contexts remain immutable.
This profile is not complete OIM,XDT,typed,negative or cross-role conformance.
"""
import copy,re
from collections import deque
from decimal import Decimal,InvalidOperation
from . import sec
from .xbrl_instance import X,L,tag,digest,canonical,XBRLError
from .xbrl_binding import bind_declarations
from .xbrl_dimensions import D,INHERITED_PROFILE,corroborate
from .xbrl_accuracy import ROUNDING_MODES,calculation_duplicates,calculation_consistency
from .xbrl_relationships import PROFILE as REL_PROFILE,SUM
from .xbrl_types import BOUNDS_PROFILE,COMPLEX_PROFILE,_bound_sources,_resolve,_value_check
from .xbrl_calculation_report import _identity,_source_fact,_context,HEX

PROFILE='POSITIVE_EXPLICIT_DIMENSIONAL_CALCULATIONS_V1'
SCHEMA='gig.sec.xbrl.dimensional_calculation_report.v1'
BOUND_NUMERIC_PROFILE='POSITIVE_EXPLICIT_DIMENSIONAL_BOUND_NUMERIC_CALCULATIONS_V2'
BOUND_NUMERIC_SCHEMA='gig.sec.xbrl.dimensional_calculation_report.v2'
MAX_OUTPUT=4*1024*1024;MAX_BINDINGS=128
QNAME=re.compile(r'\{[^{}]{1,512}\}[A-Za-z_][A-Za-z0-9_.-]{0,127}\Z')

def _declaration(dts,name,group):
 entry=dts['concepts'].get(name);decl=entry.get('declaration')if type(entry)is dict else None
 if type(decl)is not dict or decl.get('substitution_group')!=group or decl.get('typed_domain_ref')is not None:raise XBRLError('dimcalc_declaration_scope')
 if group==tag(D,'dimensionItem')and decl.get('abstract')is not True:raise XBRLError('dimcalc_declaration_scope')
 return decl

def _global_defaults(dts,docmap):
 """Check every default globally,not only dimensions in an applicable cube."""
 nets=dts.get('definition')
 if type(nets)is not list or len(nets)!=1:raise XBRLError('dimcalc_single_definition_role_required')
 net=nets[0]
 if net.get('usable_for_restricted_profile')is not True or net.get('issues')or type(net.get('arcs'))is not list or not 1<=len(net['arcs'])<=4096:raise XBRLError('dimcalc_definition_scope')
 arcs=net['arcs'];adj={};defaults={};sources={}
 for i,a in enumerate(arcs):
  if a.get('kind')not in('all','hypercube-dimension','dimension-domain','domain-member','dimension-default')or a.get('source_uri')not in docmap:raise XBRLError('dimcalc_definition_scope')
  adj.setdefault((a['kind'],a['from']),set()).add(a['to'])
  if a['kind']=='dimension-default':
   axis=a['from'];member=a['to']
   if axis in defaults:raise XBRLError('dimcalc_ambiguous_global_default')
   defaults[axis]=member;sources[axis]={'member':member,'role':net['role'],'arc_index':i,'source_uri':a['source_uri'],'source_sha256':docmap[a['source_uri']]}
 if len(defaults)>32:raise XBRLError('dimcalc_global_default_budget')
 for axis,default in defaults.items():
  _declaration(dts,axis,tag(D,'dimensionItem'));roots=adj.get(('dimension-domain',axis),set())
  if len(roots)!=1:raise XBRLError('dimcalc_default_domain_scope')
  members=set();pending=deque(roots)
  while pending:
   member=pending.popleft()
   if member in members:continue
   _declaration(dts,member,tag(X,'item'));members.add(member)
   if len(members)>2048:raise XBRLError('dimcalc_default_domain_budget')
   pending.extend(adj.get(('domain-member',member),()))
  children={n:adj.get(('domain-member',n),set())for n in members};degree={n:0 for n in members};depth={n:0 for n in members}
  for nodes in children.values():
   for n in nodes:degree[n]+=1
  pending=deque(n for n in members if not degree[n]);seen=0
  while pending:
   node=pending.popleft();seen+=1
   if depth[node]>=32:raise XBRLError('dimcalc_default_domain_depth')
   for child in children[node]:
    depth[child]=max(depth[child],depth[node]+1);degree[child]-=1
    if not degree[child]:pending.append(child)
  if seen!=len(members):raise XBRLError('dimcalc_default_domain_cycle')
  if default not in members:raise XBRLError('dimcalc_default_outside_domain')
 return defaults,sources

def bind_dimensional_calculation_report(parsed,dts,*,role=None,rounding_mode='round-to-nearest',dimensional_profile=INHERITED_PROFILE,numeric_profile=None):
 if numeric_profile not in (None,BOUNDS_PROFILE):raise XBRLError('dimcalc_numeric_profile_unsupported')
 if dimensional_profile!=INHERITED_PROFILE:raise XBRLError('dimcalc_profile_unsupported')
 if type(rounding_mode)is not str or rounding_mode not in ROUNDING_MODES:raise XBRLError('dimcalc_rounding_mode')
 if role is not None and(type(role)is not str or not 1<=len(role)<=512):raise XBRLError('dimcalc_role')
 _identity(parsed,'canonical_sha256','dimcalc_parsed_identity');_identity(dts,'canonical_sha256','dimcalc_dts_identity')
 if parsed.get('schema')not in('gig.sec.xbrl.instance.v1','gig.sec.xbrl.inline_set.v1'):raise XBRLError('dimcalc_original_artifact_required')
 retained=parsed.get('dts_corroboration')
 if retained is not None and(type(retained)is not dict or retained.get('dts_sha256')!=dts['canonical_sha256']):raise XBRLError('dimcalc_original_binding')
 bound=bind_declarations(parsed,dts)
 if numeric_profile==BOUNDS_PROFILE:
  _bound_sources(bound)
  if retained is not None:
   expected=bound['dts_corroboration']
   for key in ('documents','concept_declarations','type_declarations'):
    if canonical(retained.get(key,{}))!=canonical(expected.get(key,{})):raise XBRLError('dimcalc_numeric_retained_graph_mismatch')
 if dts.get('structural_closure')is not True or dts.get('unresolved'):raise XBRLError('dimcalc_dependency_closure')
 allowed_metadata={'NON_PRESENTATION_LINK_NOT_INTERPRETED'}
 if numeric_profile==BOUNDS_PROFILE:
  # Each participating declared type is resolved and checked below. The
  # discovery-only marker is still reported by the original graph.
  allowed_metadata.add('CUSTOM_TYPE_SCHEMA_VALIDATION_NOT_PERFORMED')
 if type(dts.get('unsupported_semantics'))is not list or any(type(u)is not dict or u.get('feature')not in allowed_metadata for u in dts['unsupported_semantics']):raise XBRLError('dimcalc_unknown_source_semantics')
 documents=dts.get('documents')
 if type(documents)is not list or not 1<=len(documents)<=16:raise XBRLError('dimcalc_document_budget')
 docmap={}
 for doc in documents:
  if type(doc)is not dict or type(doc.get('uri'))is not str or not HEX.fullmatch(doc.get('sha256',''))or doc['uri']in docmap:raise XBRLError('dimcalc_document_identity')
  docmap[doc['uri']]=doc['sha256']
 source=parsed['source'];issuer=source.get('issuer_cik')
 if type(issuer)is not str or not re.fullmatch('[0-9]{10}',issuer)or int(issuer)==0:raise XBRLError('dimcalc_issuer')
 if parsed['schema']=='gig.sec.xbrl.inline_set.v1':
  ds=parsed['document_set'];originals=ds.get('documents')
  if type(originals)is not list or not 1<=len(originals)<=8 or ds.get('sha256')!=digest(originals)or ds['sha256']!=source['source_sha256']:raise XBRLError('dimcalc_inline_identity')
  uris=set();expected=[]
  for original in originals:
   uri=original['uri'];s=original['source']
   if uri in uris or any(s[k]!=source[k]for k in('issuer_cik','accession','form','filed','amends_accession','origin')):raise XBRLError('dimcalc_inline_identity')
   if (None if s['accepted_at']is None else sec.acceptance_ns(s['accepted_at']))!=(None if source['accepted_at']is None else sec.acceptance_ns(source['accepted_at'])):raise XBRLError('dimcalc_inline_identity')
   uris.add(uri);expected.append({'uri':uri,'source_sha256':s['source_sha256']})
  if expected!=dts.get('original_inline_documents'):raise XBRLError('dimcalc_inline_identity')
 defaults,default_sources=_global_defaults(dts,docmap)
 # Recompute complete positive assignment proof from original source identities.
 derived=corroborate(bound,dts,profile=INHERITED_PROFILE);drs=derived['dts_corroboration']['dimensional_validation'];records={r['source_fact_id']:r for r in drs['facts']}
 if len(records)!=len(drs['facts']):raise XBRLError('dimcalc_drs_duplicate_fact')
 rels=dts.get('effective_relationships');_identity(rels,'sha256','dimcalc_relationship_identity')
 if rels.get('profile')!=REL_PROFILE or type(rels.get('networks'))is not list or len(rels['networks'])>64:raise XBRLError('dimcalc_relationship_profile')
 nets=[n for n in rels['networks']if n.get('kind')=='calculation'and(role is None or n.get('role')==role)]
 if len(nets)!=1:raise XBRLError('dimcalc_calculation_role_ambiguous')
 net=nets[0]
 if net.get('usable')is not True or net.get('issues')or net.get('arcrole')!=SUM or net.get('link_qname')!=tag(L,'calculationLink')or net.get('arc_qname')!=tag(L,'calculationArc')or type(net.get('arcs'))is not list or not 1<=len(net['arcs'])<=4096:raise XBRLError('dimcalc_calculation_network_scope')
 parents={};participants=set();pairs=set()
 for a in net['arcs']:
  if (a['from'],a['to'])in pairs or a.get('weight')not in({'numerator':'1','denominator':'1'},{'numerator':'-1','denominator':'1'}):raise XBRLError('dimcalc_calculation_arc_scope')
  if type(a.get('provenance'))is not list or not a['provenance']or any(type(p)is not dict or p.get('source_uri')not in docmap or docmap[p['source_uri']]!=p.get('source_sha256')for p in a['provenance']):raise XBRLError('dimcalc_calculation_arc_lineage')
  _declaration(dts,a['from'],tag(X,'item'));_declaration(dts,a['to'],tag(X,'item'));pairs.add((a['from'],a['to']));parents.setdefault(a['from'],[]).append(a);participants.update((a['from'],a['to']))
 if any(len(a)>128 for a in parents.values()):raise XBRLError('dimcalc_term_budget')
 contexts=parsed.get('contexts');units=parsed.get('units');facts=parsed.get('facts')
 if type(contexts)is not dict or len(contexts)>512 or type(units)is not dict or len(units)>128 or type(facts)is not list or len(facts)>4096 or parsed.get('unsupported_nodes'):raise XBRLError('dimcalc_original_scope')
 source_placements=set()
 for context in contexts.values():
  _context(context,issuer)
  seen_axes=set()
  for dim in context['dimensions']:
   if type(dim)is not dict or set(dim)!={'dimension','member','kind','context_element'}or dim['kind']!='explicit'or dim['context_element']not in('segment','scenario')or type(dim['dimension'])is not str or not QNAME.fullmatch(dim['dimension'])or type(dim['member'])is not str or not QNAME.fullmatch(dim['member'])or dim['dimension']in seen_axes:raise XBRLError('dimcalc_explicit_context_scope')
   seen_axes.add(dim['dimension']);source_placements.add(dim['context_element'])
  if len(source_placements)>1:raise XBRLError('dimcalc_mixed_context_placement')
  if context['opaque_segment']or context['period']['kind']=='forever':raise XBRLError('dimcalc_opaque_or_forever_context')
 for unit in units.values():
  if type(unit)is not dict or set(unit)!={'numerator','denominator','semantic_sha256'}or type(unit['numerator'])is not list or not 1<=len(unit['numerator'])<=8 or type(unit['denominator'])is not list or len(unit['denominator'])>8 or any(type(q)is not str or not QNAME.fullmatch(q)for q in unit['numerator']+unit['denominator'])or digest({k:unit[k]for k in('numerator','denominator')})!=unit['semantic_sha256']:raise XBRLError('dimcalc_unit_identity')
 groups={};aspects={};lineage={};ids=set();placements=set();footprint=0
 for fact in facts:
  if type(fact.get('source_fact_id'))is not str or not HEX.fullmatch(fact['source_fact_id'])or fact['source_fact_id']in ids:raise XBRLError('dimcalc_fact_identity')
  _source_fact(parsed,fact);ids.add(fact['source_fact_id']);context=contexts.get(fact['context_ref']);unit=units.get(fact['unit_ref'])
  if context is None or context['semantic_sha256']!=fact['context_sha256']or(fact['unit_ref']is not None and(unit is None or unit['semantic_sha256']!=fact['unit_sha256'])):raise XBRLError('dimcalc_fact_aspect_identity')
  if fact['concept']not in participants:continue
  r=records.get(fact['source_fact_id'])
  if r is None or r['status']!='VALIDATED_RESTRICTED_EXPLICIT_CONTEXT':raise XBRLError('dimcalc_participant_drs_proof_required')
  if unit is None:raise XBRLError('dimcalc_participant_unit_required')
  placements.add(r['context_element'])
  if len(placements)>1:raise XBRLError('dimcalc_mixed_context_placement')
  reported={}
  for dimension in context['dimensions']:
   if type(dimension)is not dict or set(dimension)!={'dimension','member','kind','context_element'}or dimension['kind']!='explicit'or dimension['context_element']!=r['context_element']or not QNAME.fullmatch(dimension['dimension'])or not QNAME.fullmatch(dimension['member'])or dimension['dimension']in reported:raise XBRLError('dimcalc_explicit_context_scope')
   axis,member=dimension['dimension'],dimension['member']
   if defaults.get(axis)==member:raise XBRLError('dimcalc_explicit_default_member')
   reported[axis]=member
  normalized={**defaults,**reported}
  if len(normalized)>32 or any(defaults.get(k)!=v for k,v in r['used_defaults'].items()):raise XBRLError('dimcalc_default_proof_scope')
  decl=_declaration(dts,fact['concept'],tag(X,'item'))
  if decl['abstract']or decl['period_type']!=context['period']['kind']or(fact['nil']and not decl['nillable']):raise XBRLError('dimcalc_numeric_declaration_scope')
  try:
   base,path=_resolve(decl['type'],dts.get('type_declarations',{}),numeric_profile or COMPLEX_PROFILE)
   _value_check(fact,base,path,units)
   value=None if fact['nil']else sec.exact(Decimal(fact['lexical_value'].strip(' \t\r\n')))
  except (XBRLError,ValueError,InvalidOperation):raise XBRLError('dimcalc_numeric_type_or_value_unsupported')from None
  aspect={'issuer_cik':issuer,'period':copy.deepcopy(context['period']),'dimensions':[{'dimension':k,'member':v}for k,v in sorted(reported.items())],'effective_dimension_values':[{'dimension':k,'member':v}for k,v in sorted(normalized.items())],'unit_sha256':unit['semantic_sha256'],'unit':copy.deepcopy(unit)};key=digest(aspect);aspects[key]=aspect;rows=groups.setdefault((fact['concept'],key),[]);rows.append({**fact,'value':value})
  if len(rows)>8:raise XBRLError('dimcalc_duplicate_budget')
  declsources=dts['concepts'][fact['concept']]['source_documents']
  if not declsources or any(u not in docmap for u in declsources):raise XBRLError('dimcalc_declaration_lineage')
  implicit={k:v for k,v in defaults.items()if k not in reported}
  record={'concept':fact['concept'],'context_ref':fact['context_ref'],'source_context_sha256':context['semantic_sha256'],'unit_ref':fact['unit_ref'],'source_unit_sha256':unit['semantic_sha256'],'reported_dimensions':copy.deepcopy(context['dimensions']),'implicit_default_dimensions':implicit,'aspect_sha256':key,'reported_lexical_value':fact['lexical_value'],'reported_numeric_value':value,'raw_fact_value':fact['value'],'drs_validation':copy.deepcopy(r),'declaration_documents':[{'uri':u,'sha256':docmap[u]}for u in declsources],'inline_source_segments':copy.deepcopy(fact.get('inline_source_segments'))};
  if numeric_profile==BOUNDS_PROFILE:
   dependencies=sorted({uri for step in path for uri in step['source_documents']})
   if any(uri not in docmap for uri in dependencies):raise XBRLError('dimcalc_numeric_type_lineage')
   record['numeric_type_provenance']={'base_type':base,'derivation_path':[step['type']for step in path],
    'documents':[{'uri':uri,'sha256':docmap[uri]}for uri in dependencies]}
  lineage[fact['source_fact_id']]=record;footprint+=len(canonical(record))
  if footprint>MAX_OUTPUT:raise XBRLError('dimcalc_output_budget')
 result={'schema':SCHEMA,'profile':PROFILE,'status':'UNAVAILABLE','reason':'NO_SUPPORTED_PARENT_DATA_POINTS','rounding_mode':rounding_mode,'dimensional_profile':INHERITED_PROFILE,'role':net['role'],'definition_role':dts['definition'][0]['role'],'parsed_sha256':parsed['canonical_sha256'],'dts_sha256':dts['canonical_sha256'],'relationships_sha256':rels['sha256'],'drs_proof_sha256':digest(drs),'definition_sha256':digest(dts['definition']),'source_filing':copy.deepcopy(source),'global_default_dimensions':defaults,'default_provenance':default_sources,'definition_documents':[{'uri':u,'sha256':docmap[u]}for u in sorted({a['source_uri']for a in dts['definition'][0]['arcs']})],'fact_provenance':lineage,'bindings':[],'selected_reported_value':None,'limitations':['Positive inherited/conjunctive explicit DRS V3 only;no typed,negative,opaque,forever,cross-role or mixed context placement','Global defaults are derived calculation aspects only;original source contexts and facts are unchanged','Not complete OIM/XDT/Calc1.1 conformance,independent source authentication or accounting equivalence']}
 if numeric_profile==BOUNDS_PROFILE:
  result.update(schema=BOUND_NUMERIC_SCHEMA,profile=BOUND_NUMERIC_PROFILE,numeric_profile=numeric_profile)
 for parent,arcs in sorted(parents.items()):
  for (concept,key),rows in sorted(groups.items()):
   if concept!=parent:continue
   points={parent:calculation_duplicates(rows,rounding_mode=rounding_mode)};terms=[];missing=[]
   for arc in arcs:
    child=groups.get((arc['to'],key));accuracy=calculation_duplicates(child,rounding_mode=rounding_mode)if child else None
    if accuracy is None:missing.append(arc['to'])
    else:points[arc['to']]=accuracy
    terms.append({'concept':arc['to'],'weight':int(arc['weight']['numerator']),'accuracy':accuracy})
   allids=[i for p in points.values()for i in p['source_fact_ids']]
   result['bindings'].append({'parent':parent,'aspect_sha256':key,'aspects':aspects[key],'source_context_sha256s':sorted({lineage[i]['source_context_sha256']for i in allids}),'data_points':points,'missing_concepts':missing,'calculation':calculation_consistency(points[parent],terms,rounding_mode=rounding_mode),'relationship_provenance':[copy.deepcopy(a['provenance'])for a in arcs]})
   if len(result['bindings'])>MAX_BINDINGS or len(canonical(result))>MAX_OUTPUT:raise XBRLError('dimcalc_output_budget')
 if result['bindings']:result.update(status='AVAILABLE',reason=None)
 result['sha256']=digest(result)
 if len(canonical(result))>MAX_OUTPUT:raise XBRLError('dimcalc_output_budget')
 return result
