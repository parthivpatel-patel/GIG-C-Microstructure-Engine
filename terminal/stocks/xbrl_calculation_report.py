"""Explicit source/DTS-bound calculation reports for a narrow non-dimensional subset.

No report fetch,source authentication,accounting alias or fact selection. Full OIM,
XDT and Calc1.1 conformance are not established by this restricted binding profile.
"""
import copy,re
from decimal import Decimal,InvalidOperation
from fractions import Fraction
from . import sec
from .xbrl_instance import X,L,tag,digest,canonical,XBRLError
from .xbrl_binding import bind_declarations
from .xbrl_types import _resolve,_value_check,COMPLEX_PROFILE
from .xbrl_accuracy import calculation_duplicates,calculation_consistency,ROUNDING_MODES
from .xbrl_relationships import PROFILE as REL_PROFILE,SUM,number,rational

PROFILE='SOURCE_BOUND_CALCULATIONS_V1';SCHEMA='gig.sec.xbrl.calculation_report.v1'
WEIGHTED_PROFILE='SOURCE_BOUND_DECIMAL_WEIGHT_CALCULATIONS_V2'
WEIGHTED_SCHEMA='gig.sec.xbrl.calculation_report.v2'
MAX_INPUT=8*1024*1024;MAX_OUTPUT=4*1024*1024;MAX_BINDINGS=128
HEX=re.compile('[0-9a-f]{64}\\Z')

def _identity(value,key,code):
 if type(value)is not dict or len(canonical(value))>MAX_INPUT or type(value.get(key))is not str or not HEX.fullmatch(value[key])or digest({k:v for k,v in value.items()if k!=key})!=value[key]:raise XBRLError(code)

def _original_decimal_weight(arc, declarations):
 weight=arc.get('weight')
 for origin in arc['provenance']:
  exact=number(origin.get('weight_lexical'),'calculation_source_weight')
  if not exact or rational(exact)!=weight:raise XBRLError('calculation_source_weight')
 parent=declarations[arc['from']]['declaration']['balance']
 child=declarations[arc['to']]['declaration']['balance']
 if parent is not None and child is not None and (exact>0)!=(parent==child):raise XBRLError('calculation_source_weight_balance')

def _source_fact(parsed,fact):
 core={k:v for k,v in fact.items()if k!='source_fact_id'}
 if parsed['schema']=='gig.sec.xbrl.inline_set.v1':
  expected=digest({'document_set_sha256':parsed['document_set']['sha256'],'fact':core})
  originals={d['uri']:d['source']['source_sha256']for d in parsed['document_set']['documents']}
  segments=fact.get('inline_source_segments')
  if type(segments)is not list or not 1<=len(segments)<=33 or any(type(s)is not dict or originals.get(s.get('document_uri'))!=s.get('document_sha256')for s in segments):raise XBRLError('calculation_report_inline_lineage')
 else:
  # The plain parser marks conflicts after assigning their original source IDs.
  if core.get('admission')=='CONFLICTED_EXACT_VALUES':core['admission']='ADMITTED_PROFILE'
  expected=digest({'source_sha256':parsed['source']['source_sha256'],'fact':core})
 if fact.get('source_fact_id')!=expected:raise XBRLError('calculation_report_fact_identity')

def _context(ctx,issuer):
 if type(ctx)is not dict or set(ctx)!={'issuer_cik','period','dimensions','opaque_segment','identifier_lexical','semantic_sha256'}or ctx['issuer_cik']!=issuer:raise XBRLError('calculation_report_context_contract')
 core={k:ctx[k]for k in('issuer_cik','period','dimensions','opaque_segment')}
 if digest(core)!=ctx['semantic_sha256']:raise XBRLError('calculation_report_context_identity')
 if type(ctx['identifier_lexical'])is not str or not re.fullmatch('[0-9]{1,10}',ctx['identifier_lexical'])or ctx['identifier_lexical'].zfill(10)!=issuer:raise XBRLError('calculation_report_entity_identity')
 p=ctx['period']
 if type(p)is not dict or set(p)!={'kind','start','end'}:raise XBRLError('calculation_report_period_contract')
 if p['kind']=='instant':
  if p['start']is not None:raise XBRLError('calculation_report_period_contract')
  sec.date(p['end'])
 elif p['kind']=='duration':
  sec.date(p['start']);sec.date(p['end'])
  if p['start']>p['end']:raise XBRLError('calculation_report_period_contract')
 elif p!={'kind':'forever','start':None,'end':None}:raise XBRLError('calculation_report_period_contract')
 if type(ctx['dimensions'])is not list or len(ctx['dimensions'])>32 or type(ctx['opaque_segment'])is not list or len(ctx['opaque_segment'])>32:raise XBRLError('calculation_report_context_budget')
 return not(ctx['dimensions']or ctx['opaque_segment']or p['kind']=='forever')

def bind_calculation_report(parsed,dts,*,role=None,rounding_mode='round-to-nearest',weight_profile=None):
 """Bind exact calculation math to canonical original facts and one supplied DTS.

 Explicit original DTS is required;an abbreviated retained proof cannot substitute
 for its graph identity. Source hashes demonstrate integrity,not authentication.
 """
 if weight_profile not in(None,WEIGHTED_PROFILE):raise XBRLError('calculation_weight_profile_unsupported')
 weighted=weight_profile==WEIGHTED_PROFILE
 if type(rounding_mode)is not str or rounding_mode not in ROUNDING_MODES:raise XBRLError('calculation_report_rounding_mode')
 if role is not None and(type(role)is not str or not 1<=len(role)<=512):raise XBRLError('calculation_report_role')
 _identity(parsed,'canonical_sha256','calculation_report_parsed_identity');_identity(dts,'canonical_sha256','calculation_report_dts_identity')
 if parsed.get('schema')not in('gig.sec.xbrl.instance.v1','gig.sec.xbrl.inline_set.v1'):raise XBRLError('calculation_report_artifact_profile')
 proof=parsed.get('dts_corroboration')
 if proof is not None and(type(proof)is not dict or proof.get('dts_sha256')!=dts['canonical_sha256']):raise XBRLError('calculation_report_existing_binding')
 bind_declarations(parsed,dts) # Revalidate original instance/set and declaration scope.
 if dts.get('structural_closure')is not True or dts.get('unresolved')or dts.get('definition'):raise XBRLError('calculation_report_dts_or_dimension_scope')
 # This legacy discovery flag refers to calculation content independently handled
 # by the effective graph;other unknown source semantics remain out of scope.
 if type(dts.get('unsupported_semantics'))is not list or len(dts['unsupported_semantics'])>1024 or any(type(u)is not dict or u.get('feature')!='NON_PRESENTATION_LINK_NOT_INTERPRETED'for u in dts['unsupported_semantics']):raise XBRLError('calculation_report_unknown_dts_semantics')
 source=parsed['source'];issuer=source.get('issuer_cik')
 if type(issuer)is not str or not re.fullmatch('[0-9]{10}',issuer)or int(issuer)==0 or not HEX.fullmatch(source.get('source_sha256','')):raise XBRLError('calculation_report_source_identity')
 if parsed['schema']=='gig.sec.xbrl.inline_set.v1':
  ds=parsed['document_set'];documents=ds.get('documents')
  if type(documents)is not list or not 1<=len(documents)<=8 or ds.get('sha256')!=digest(documents)or source['source_sha256']!=ds['sha256']:raise XBRLError('calculation_report_set_identity')
  originals=[];seen_uris=set()
  for original in documents:
   if type(original)is not dict or type(original.get('uri'))is not str or original['uri']in seen_uris or type(original.get('source'))is not dict:raise XBRLError('calculation_report_set_originals')
   seen_uris.add(original['uri']);o=original['source']
   if type(o.get('source_sha256'))is not str or not HEX.fullmatch(o['source_sha256'])or any(o.get(k)!=source.get(k)for k in('issuer_cik','accession','form','filed','amends_accession','origin')):raise XBRLError('calculation_report_set_originals')
   if (None if o.get('accepted_at')is None else sec.acceptance_ns(o['accepted_at']))!=(None if source.get('accepted_at')is None else sec.acceptance_ns(source['accepted_at'])):raise XBRLError('calculation_report_set_originals')
   originals.append({'uri':original['uri'],'source_sha256':o['source_sha256']})
  if originals!=dts.get('original_inline_documents'):raise XBRLError('calculation_report_set_originals')
 docs=dts.get('documents')
 if type(docs)is not list or not 1<=len(docs)<=16:raise XBRLError('calculation_report_document_budget')
 docmap={}
 for doc in docs:
  if type(doc)is not dict or type(doc.get('uri'))is not str or not 1<=len(doc['uri'])<=512 or not HEX.fullmatch(doc.get('sha256',''))or doc['uri']in docmap:raise XBRLError('calculation_report_document_identity')
  docmap[doc['uri']]=doc['sha256']
 rels=dts.get('effective_relationships');_identity(rels,'sha256','calculation_report_relationship_identity')
 if rels.get('profile')!=REL_PROFILE or type(rels.get('networks'))is not list or len(rels['networks'])>64:raise XBRLError('calculation_report_relationship_profile')
 networks=[n for n in rels['networks']if n.get('kind')=='calculation'and(role is None or n.get('role')==role)]
 if len(networks)!=1:raise XBRLError('calculation_report_role_ambiguous_or_missing')
 net=networks[0]
 issues=net.get('issues')
 if type(issues)is not list or net.get('usable')is not (not issues):raise XBRLError('calculation_report_network_unsupported')
 if any(issue!='WEIGHT_OUTSIDE_SIGNED_UNIT_PROFILE' or not weighted for issue in issues)or net.get('arcrole')!=SUM or net.get('link_qname')!=tag(L,'calculationLink')or net.get('arc_qname')!=tag(L,'calculationArc')or type(net.get('arcs'))is not list or not 1<=len(net['arcs'])<=4096:raise XBRLError('calculation_report_network_unsupported')
 parents={};concepts=set();pairs=set();declarations=dts['concepts']
 for arc in net['arcs']:
  parent,child=arc['from'],arc['to'];weight=arc.get('weight')
  if parent not in declarations or child not in declarations or(parent,child)in pairs or type(weight)is not dict or set(weight)!={'numerator','denominator'}or not weighted and weight not in({'numerator':'1','denominator':'1'},{'numerator':'-1','denominator':'1'}):raise XBRLError('calculation_report_arc_contract')
  provenance=arc.get('provenance')
  if type(provenance)is not list or not 1<=len(provenance)<=4096 or any(type(p)is not dict or p.get('source_uri')not in docmap or docmap[p['source_uri']]!=p.get('source_sha256')for p in provenance):raise XBRLError('calculation_report_arc_lineage')
  if weighted:_original_decimal_weight(arc,declarations)
  pairs.add((parent,child));parents.setdefault(parent,[]).append(arc);concepts.update((parent,child))
 if any(len(v)>128 for v in parents.values()):raise XBRLError('calculation_report_term_budget')
 contexts=parsed.get('contexts');units=parsed.get('units');facts=parsed.get('facts')
 if type(contexts)is not dict or len(contexts)>512 or type(units)is not dict or len(units)>128 or type(facts)is not list or len(facts)>4096 or parsed.get('unsupported_nodes'):raise XBRLError('calculation_report_fact_scope_or_budget')
 supported={key:_context(ctx,issuer)for key,ctx in contexts.items()}
 for unit in units.values():
  if type(unit)is not dict or set(unit)!={'numerator','denominator','semantic_sha256'}or type(unit['numerator'])is not list or not 1<=len(unit['numerator'])<=8 or type(unit['denominator'])is not list or len(unit['denominator'])>8 or digest({k:unit[k]for k in('numerator','denominator')})!=unit['semantic_sha256']:raise XBRLError('calculation_report_unit_identity')
 groups={};excluded=[];ids=set();provenance={};footprint=0
 for fact in facts:
  if type(fact)is not dict or type(fact.get('source_fact_id'))is not str or not HEX.fullmatch(fact['source_fact_id'])or fact['source_fact_id']in ids:raise XBRLError('calculation_report_fact_identity')
  _source_fact(parsed,fact);ids.add(fact['source_fact_id'])
  if fact['context_ref']not in contexts or fact['context_sha256']!=contexts[fact['context_ref']]['semantic_sha256']:raise XBRLError('calculation_report_fact_context')
  if fact['unit_ref']is not None and(fact['unit_ref']not in units or fact['unit_sha256']!=units[fact['unit_ref']]['semantic_sha256']):raise XBRLError('calculation_report_fact_unit')
  if fact['concept']not in concepts:continue
  context=contexts[fact['context_ref']];decl=declarations[fact['concept']]['declaration'];reason=None
  if not supported[fact['context_ref']]:reason='DIMENSIONAL_OPAQUE_OR_FOREVER_CONTEXT_OUTSIDE_PROFILE'
  elif decl['abstract']or decl['substitution_group']!=tag(X,'item')or decl['period_type']!=context['period']['kind']:reason='DECLARATION_PERIOD_OR_SUBSTITUTION_UNSUPPORTED'
  elif fact['unit_ref']is None:reason='NUMERIC_UNIT_MISSING'
  if reason is None:
   try:
    base,path=_resolve(decl['type'],dts.get('type_declarations',{}),COMPLEX_PROFILE)
    lexical=fact['lexical_value'].strip(' \t\r\n');value=None if fact['nil']else sec.exact(Decimal(lexical));_value_check({**fact,'value':value},base,path,units)
    if fact['nil']and not decl['nillable']:raise XBRLError('calculation_report_nil_not_declared')
   except (XBRLError,ValueError,InvalidOperation):reason='NUMERIC_DECLARATION_OR_VALUE_UNSUPPORTED'
  if reason is not None:
   record={'source_fact_id':fact['source_fact_id'],'concept':fact['concept'],'reason':reason};excluded.append(record);footprint+=len(canonical(record))
   if footprint>MAX_OUTPUT:raise XBRLError('calculation_report_output_budget')
   continue
  declaration_sources=declarations[fact['concept']]['source_documents']
  if type(declaration_sources)is not list or not 1<=len(declaration_sources)<=16:raise XBRLError('calculation_report_declaration_lineage')
  if any(uri not in docmap for uri in declaration_sources):raise XBRLError('calculation_report_declaration_lineage')
  key=(fact['concept'],fact['context_sha256'],fact['unit_sha256']);groups.setdefault(key,[]).append({**fact,'value':value})
  if len(groups[key])>8:raise XBRLError('calculation_report_duplicate_budget')
  provenance[fact['source_fact_id']]={'concept':fact['concept'],'context_ref':fact['context_ref'],'unit_ref':fact['unit_ref'],'reported_lexical_value':fact['lexical_value'],'reported_numeric_value':value,'raw_fact_value':fact['value'],'declaration_documents':[{'uri':uri,'sha256':docmap[uri]}for uri in declaration_sources],'inline_source_segments':copy.deepcopy(fact.get('inline_source_segments'))}
  footprint+=len(canonical(provenance[fact['source_fact_id']]))+len(fact['source_fact_id'])
  if footprint>MAX_OUTPUT:raise XBRLError('calculation_report_output_budget')
 result={'schema':SCHEMA,'profile':PROFILE,'status':'UNAVAILABLE','reason':None,'rounding_mode':rounding_mode,'role':net['role'],'parsed_sha256':parsed['canonical_sha256'],'dts_sha256':dts['canonical_sha256'],'relationships_sha256':rels['sha256'],'source_filing':copy.deepcopy(source),'bindings':[],'fact_provenance':provenance,'excluded_facts':excluded,'selected_reported_value':None,'limitations':['Only one supported effective signed-unit summation-item network;no definition/default or dimensional/opaque contexts','Canonical artifact integrity is not source authentication or full OIM/Calc1.1 conformance','No reported fact selection,missing-zero synthesis,period/unit aggregation or accounting equivalence']}
 if weighted:
  result.update(schema=WEIGHTED_SCHEMA,profile=WEIGHTED_PROFILE)
  result['limitations'][0]='One supported effective summation-item network with original nonzero decimal weights;no definition/default or dimensional/opaque contexts'
 for parent,arcs in sorted(parents.items()):
  for key,parent_facts in sorted(groups.items()):
   if key[0]!=parent:continue
   aspects={'issuer_cik':issuer,'period':copy.deepcopy(contexts[parent_facts[0]['context_ref']]['period']),'dimensions':[],'context_sha256':key[1],'unit_sha256':key[2],'unit':copy.deepcopy(units[parent_facts[0]['unit_ref']])}
   terms=[];points={parent:calculation_duplicates(parent_facts,rounding_mode=rounding_mode)};missing=[]
   for arc in arcs:
    rows=groups.get((arc['to'],key[1],key[2]));accuracy=calculation_duplicates(rows,rounding_mode=rounding_mode)if rows else None
    if rows:points[arc['to']]=accuracy
    else:missing.append(arc['to'])
    terms.append({'concept':arc['to'],'weight':arc['provenance'][0]['weight_lexical']if weighted else int(arc['weight']['numerator']),'accuracy':accuracy})
   check=calculation_consistency(points[parent],terms,rounding_mode=rounding_mode)
   result['bindings'].append({'parent':parent,'aspects':aspects,'data_points':points,'missing_concepts':missing,'calculation':check,'relationship_provenance':[copy.deepcopy(a['provenance'])for a in arcs]})
   if len(result['bindings'])>MAX_BINDINGS or len(canonical(result))>MAX_OUTPUT:raise XBRLError('calculation_report_output_budget')
 if result['bindings']:result.update(status='AVAILABLE',reason=None)
 else:result['reason']='NO_SUPPORTED_PARENT_DATA_POINTS'
 result['sha256']=digest(result)
 if len(canonical(result))>MAX_OUTPUT:raise XBRLError('calculation_report_output_budget')
 return result
