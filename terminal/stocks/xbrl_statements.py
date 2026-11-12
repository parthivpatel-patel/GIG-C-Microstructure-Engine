"""Versioned source-bound presentation view of one acceptance-qualified filing.

Not complete statements. Never combine filings, periods, units or dimensions to
fill missing cells. Exact-value sums are diagnostics,not XBRL rounding intervals.
"""
import copy,datetime,re
from fractions import Fraction
from . import sec
from .xbrl_instance import canonical,digest,selected_financials,XBRLError
from .xbrl_relationships import PROFILE,rational
SCHEMA='gig.sec.xbrl.statement_view.v1';MAX_CONCEPTS=128;MAX_PERIODS=12;MAX_OUTPUT=256*1024

def _identity(value,key):
 if type(value)is not dict or digest({k:v for k,v in value.items()if k!=key})!=value.get(key):raise XBRLError('statement_input_identity')

def _result(result):
 if len(canonical(result))>MAX_OUTPUT:raise XBRLError('statement_output_budget')
 result['sha256']=digest(result);return result

def select(filings,issuer,origin,collection_sha,as_of,*,role=None,form='10-K'):
 if type(role)is not str and role is not None or role is not None and not 1<=len(role)<=512 or form not in('10-K','10-Q'):raise XBRLError('statement_query')
 cutoff=sec.acceptance_ns(as_of);date=(datetime.datetime(1970,1,1,tzinfo=datetime.timezone.utc)+datetime.timedelta(seconds=cutoff//1000000000)).date().isoformat()
 if type(filings)is not dict or len(filings)>32:raise XBRLError('statement_filing_budget')
 candidates=[];excluded={'unknown_acceptance':0,'after_cutoff':0,'other_form':0};available=set()
 for accession,p in sorted(filings.items()):
  _identity(p,'canonical_sha256');source=p['source']
  if source['issuer_cik']!=issuer or source['origin']!=origin or accession!=source['accession']:raise XBRLError('statement_source_scope')
  if source['form'].removesuffix('/A')!=form:excluded['other_form']+=1;continue
  if source['accepted_at']is None:excluded['unknown_acceptance']+=1;continue
  ns=sec.acceptance_ns(source['accepted_at'])
  if ns>cutoff or source['filed']>date:excluded['after_cutoff']+=1;continue
  selected_financials(p) # Validate dimensional policy even when all facts are missing.
  proof=p.get('dts_corroboration',{});rels=proof.get('effective_relationships')
  if rels is not None:
   _identity(rels,'sha256')
   if rels.get('schema')!='gig.sec.xbrl.effective_relationships.v1'or rels.get('profile')!=PROFILE:raise XBRLError('statement_relationship_profile')
   for n in rels['networks']:
    if n['kind']=='presentation':available.add(n['role'])
  candidates.append((ns,p))
 result={'schema':SCHEMA,'issuer_cik':issuer,'origin':origin,'as_of':as_of,'cutoff_ns':str(cutoff),'form_family':form,'role':role,'available_roles':sorted(available),'collection_sha256':collection_sha,'status':'UNAVAILABLE','reason':'NO_ACCEPTANCE_QUALIFIED_FILING','source_filing':None,'source_documents':[],'selected_instance_sha256':None,'original_inline_documents':[],'relationship_sha256':None,'periods':[],'relationships':[],'diagnostics':[],'unsupported_dts_semantics':[],'exclusions':excluded,'selection_policy':'Latest acceptance-qualified filing in explicit form family;no cross-filing or additive amendment filling','complete_statements':False,'calculation_policy':'Exact reported values,without decimals/precision interval inference;difference is not proof of source defect','source_authentication':'Supplied manifests and hashes are lineage,not independent source authentication'}
 if not candidates:return _result(result)
 ns=max(n for n,_ in candidates);winners=[p for n,p in candidates if n==ns]
 if len(winners)!=1:result.update(status='AMBIGUOUS',reason='MULTIPLE_FILINGS_AT_LATEST_ACCEPTANCE');return _result(result)
 p=winners[0];source=p['source'];proof=p.get('dts_corroboration',{});rels=proof.get('effective_relationships');result.update(source_filing=copy.deepcopy(source),selected_instance_sha256=p['canonical_sha256'],original_inline_documents=copy.deepcopy(p.get('document_set',{}).get('documents',[])))
 if source['form'].endswith('/A'):
  parent=source['amends_accession'];result['diagnostics'].append('AMENDMENT_NOT_ADDITIVELY_MERGED')
  if parent is None or parent not in filings or filings[parent]['source']['accepted_at']is None or sec.acceptance_ns(filings[parent]['source']['accepted_at'])>cutoff:
   result.update(reason='AMENDMENT_LINEAGE_UNRESOLVED');return _result(result)
 if rels is None or not proof.get('structural_closure'):result.update(reason='SUPPLIED_CLOSED_DTS_REQUIRED');return _result(result)
 result['relationship_sha256']=rels['sha256'];result['source_documents']=copy.deepcopy(proof['documents']);result['unsupported_dts_semantics']=copy.deepcopy(proof['unsupported_semantics'])
 available_here=sorted(n['role']for n in rels['networks']if n['kind']=='presentation');result['available_roles']=available_here
 if role is None:result.update(reason='EXPLICIT_PRESENTATION_ROLE_REQUIRED',available_roles=available_here);return _result(result)
 networks=[n for n in rels['networks']if n['kind']=='presentation'and n['role']==role]
 if len(networks)!=1:result.update(reason='ROLE_NOT_IN_LATEST_FILING');return _result(result)
 net=networks[0]
 if not net['usable']:result.update(reason='PRESENTATION_UNSUPPORTED',diagnostics=sorted(set(result['diagnostics']+net['issues'])));return _result(result)
 concepts={v for a in net['arcs']for v in(a['from'],a['to'])}
 if not concepts:result.update(reason='EMPTY_EFFECTIVE_PRESENTATION');return _result(result)
 if len(concepts)>MAX_CONCEPTS:raise XBRLError('statement_concept_budget')
 declarations=proof['concept_declarations'];order=[];seen=set();pending=list(reversed(net['roots']));children={}
 for arc in net['arcs']:children.setdefault(arc['from'],[]).append(arc['to'])
 while pending:
  concept=pending.pop()
  if concept in seen:continue
  seen.add(concept);order.append(concept);pending.extend(reversed(children.get(concept,[])))
 if seen!=concepts:raise XBRLError('statement_unreachable_concept')
 # The normalized selector is also the authority for default-dependent exclusions.
 selected=selected_financials(p);allowed={id_ for history in(selected['history'],selected['revision_history'])for rows in history.values()for row in rows for id_ in row['source_xml_fact_ids']}
 groups={};periods=set();unverified_ids=set();excluded_facts={'dimensioned_or_opaque':0,'unverified':0,'unsupported_period':0}
 for f in p['facts']:
  if f['concept']not in concepts:continue
  ctx=p['contexts'][f['context_ref']];per=ctx['period']
  if ctx['dimensions']or ctx['opaque_segment']:excluded_facts['dimensioned_or_opaque']+=1;continue
  if per['end']is None:excluded_facts['unsupported_period']+=1;continue
  if f['admission']not in('ADMITTED_PROFILE','CONFLICTED_EXACT_VALUES'):excluded_facts['unverified']+=1;unverified_ids.add(f['source_fact_id'])
  if f['admission']=='ADMITTED_PROFILE'and not f['nil']and f['source_fact_id']not in allowed:excluded_facts['unverified']+=1;unverified_ids.add(f['source_fact_id'])
  period=(per['start'],per['end']);periods.add(period);groups.setdefault((period,f['concept']),[]).append(f)
 result['fact_exclusions']=excluded_facts;result['truncated_periods']=len(periods)>MAX_PERIODS
 for start,end in sorted(periods,key=lambda k:(k[1],k[0]or''),reverse=True)[:MAX_PERIODS]:
  rows=[]
  for concept in order:
   facts=groups.get(((start,end),concept),[]);declaration=declarations[concept]['declaration'];status='MISSING';value=None;unit=None
   if len(facts)>8:raise XBRLError('statement_fact_lineage_budget')
   try:values={Fraction(f['value'])for f in facts if not f['nil']}
   except (ValueError,TypeError,ZeroDivisionError):values=set();unverified_ids.update(f['source_fact_id']for f in facts)
   units={f['unit_sha256']for f in facts}
   if declaration['abstract']:status='ABSTRACT'
   elif any(f['admission']=='CONFLICTED_EXACT_VALUES'for f in facts)or len(values)>1 or values and any(f['nil']for f in facts):status='CONFLICT'
   elif len(units)>1:status='AMBIGUOUS_UNITS'
   elif any(f['source_fact_id']in unverified_ids for f in facts):status='UNSUPPORTED_INPUT'
   elif values:status='REPORTED';value=facts[0]['value'];unit=copy.deepcopy(p['units'][facts[0]['unit_ref']])
   rows.append({'concept':concept,'period_type':declaration['period_type'],'status':status,'value':value,'unit':unit,'facts':copy.deepcopy(facts)})
  row_map={r['concept']:r for r in rows};calculations=[]
  for cn in rels['networks']:
   if cn['kind']!='calculation'or cn['role']!=role:continue
   if not cn['usable']:calculations.append({'status':'UNSUPPORTED','issues':cn['issues']});continue
   parents={}
   for arc in cn['arcs']:parents.setdefault(arc['from'],[]).append(arc)
   for parent,arcs in sorted(parents.items()):
    terms=[row_map.get(parent)]+[row_map.get(a['to'])for a in arcs];check={'parent':parent,'status':'INCOMPLETE','reported':None,'weighted_sum':None,'residual':None,'relationship_provenance':[a['provenance']for a in arcs]}
    if all(r and r['status']=='REPORTED'for r in terms)and len({r['unit']['semantic_sha256']for r in terms})==1:
     reported=Fraction(terms[0]['value']);total=sum((Fraction(row_map[a['to']]['value'])*Fraction(int(a['weight']['numerator']),int(a['weight']['denominator']))for a in arcs),Fraction(0));check.update(status='EXACT_MATCH'if reported==total else'EXACT_DIFFERENCE',reported=rational(reported),weighted_sum=rational(total),residual=rational(reported-total))
    calculations.append(check)
  result['periods'].append({'start':start,'end':end,'kind':'instant'if start is None else'duration','rows':rows,'calculations':calculations})
 result.update(status='AVAILABLE',reason=None,relationships=copy.deepcopy(net['arcs']))
 if not result['periods']:result['diagnostics'].append('NO_ELIGIBLE_CONSOLIDATED_FACT_PERIODS')
 return _result(result)
