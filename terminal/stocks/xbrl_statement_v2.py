"""Opt-in supplied-DTS extension structures and reported-accuracy consistency.

Never infer a GAAP accounting metric from a name,role or presentation adjacency.
Raw fact objects/IDs remain untouched;DTS-validated numeric values are derived
records bound to those original fact IDs,filing and declaration source documents.
"""
import copy,re
from decimal import Decimal
from fractions import Fraction
from . import sec
from .xbrl_instance import X,tag,canonical,digest,XBRLError
from .xbrl_statements import select,_result
from .xbrl_types import _resolve,_value_check,COMPLEX_PROFILE
from .xbrl_relationships import rational
from .xbrl_accuracy import duplicates,consistency
PROFILE='accuracy-extension-v2';SCHEMA='gig.sec.xbrl.statement_view.v2'
REPORTED=('REPORTED','REPORTED_EXTENSION')

def _numeric(row,p,proof):
 declaration=proof['concept_declarations'][row['concept']]['declaration'];kind='SUPPLIED_EXTENSION_DECLARATION'if not re.fullmatch(r'\{https?://fasb\.org/us-gaap/[0-9]{4}\}.+',row['concept'])else'SUPPLIED_STANDARD_DECLARATION'
 row['numeric_facts']=[];row['mapping_diagnostics']=[];row['accuracy']=None
 row['statement_mapping']={'kind':kind,'concept':row['concept'],'accounting_metric':None,'basis':'SUPPLIED_DECLARATION_AND_EFFECTIVE_PRESENTATION_ONLY','declaration_documents':[]}
 doc_map={d['uri']:d['sha256']for d in proof['documents']}
 for uri in proof['concept_declarations'][row['concept']]['source_documents']:
  if uri not in doc_map:raise XBRLError('extension_declaration_source_missing')
  row['statement_mapping']['declaration_documents'].append({'uri':uri,'sha256':doc_map[uri]})
 if not row['facts']or declaration['abstract']:return
 # This profile excludes source dimensions/opaque contexts and unknown DRS defaults.
 if kind=='SUPPLIED_EXTENSION_DECLARATION'and proof.get('definition_relationships_present')is not False:
  row.update(status='UNSUPPORTED_INPUT',value=None,unit=None);row['mapping_diagnostics'].append('EXTENSION_DRS_SCOPE_UNSUPPORTED_OR_UNKNOWN');return
 if declaration['substitution_group']!=tag(X,'item'):
  row.update(status='UNSUPPORTED_INPUT',value=None,unit=None);row['mapping_diagnostics'].append('EXTENSION_SUBSTITUTION_UNSUPPORTED');return
 try:base,path=_resolve(declaration['type'],proof.get('type_declarations',{}),COMPLEX_PROFILE)
 except XBRLError:
  row.update(status='UNSUPPORTED_INPUT',value=None,unit=None);row['mapping_diagnostics'].append('EXTENSION_NUMERIC_TYPE_UNSUPPORTED');return
 values={};units=set();bad_context=False
 for f in row['facts']:
  ctx=p['contexts'][f['context_ref']]
  if ctx['period']['kind']!=declaration['period_type']or ctx['dimensions']or ctx['opaque_segment']:bad_context=True;continue
  if f['nil']and not declaration['nillable']:raise XBRLError('extension_nil_not_declared')
  if f['unit_ref']is None:raise XBRLError('extension_numeric_unit_required')
  lexical=f['lexical_value'].strip(' \t\r\n')
  if not f['nil']and(len(lexical)>64 or not re.fullmatch(r'[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)',lexical)):raise XBRLError('extension_numeric_lexical')
  try:value=None if f['nil']else sec.exact(Decimal(lexical))
  except ValueError:raise XBRLError('extension_numeric_budget')from None
  derived={**f,'value':value};_value_check(derived,base,path,p['units']);values[f['source_fact_id']]=value;units.add(f['unit_sha256'])
  row['numeric_facts'].append({'source_fact_id':f['source_fact_id'],'concept':f['concept'],'value':value,'declared_type':declaration['type'],'resolved_numeric_base':base,'numeric_profile':COMPLEX_PROFILE,'derived_from':'ORIGINAL_LEXICAL_FACT_PLUS_SUPPLIED_DTS','filing_accession':p['source']['accession'],'instance_sha256':p['canonical_sha256']})
 if bad_context:
  row.update(status='UNSUPPORTED_INPUT',value=None,unit=None);row['mapping_diagnostics'].append('DECLARED_PERIOD_OR_CONTEXT_UNSUPPORTED');return
 nums={Fraction(v)for v in values.values()if v is not None};nil=any(v is None for v in values.values())
 if len(nums)>1 or nil and nums:row.update(status='CONFLICT',value=None,unit=None);return
 if len(units)>1:row.update(status='AMBIGUOUS_UNITS',value=None,unit=None);return
 if row['status']=='UNSUPPORTED_INPUT'and kind=='SUPPLIED_STANDARD_DECLARATION':
  # Existing dimensional/defaulted exclusion remains authoritative for standards.
  row['mapping_diagnostics'].append('STANDARD_SELECTED_POLICY_NOT_OVERRIDDEN');return
 if nums:
  row.update(status='REPORTED_EXTENSION'if kind=='SUPPLIED_EXTENSION_DECLARATION'else'REPORTED',value=next(v for v in values.values()if v is not None),unit=copy.deepcopy(p['units'][row['facts'][0]['unit_ref']]))
  row['accuracy']=duplicates(row['facts'],values=values)
 else:row.update(status='MISSING',value=None,unit=None)

def _calculations(rows,networks,role):
 row_map={r['concept']:r for r in rows};checks=[]
 for net in networks:
  if net['kind']!='calculation'or net['role']!=role:continue
  if not net['usable']:checks.append({'status':'UNSUPPORTED','issues':net['issues'],'accuracy_validation':None,'exact_diagnostic':None});continue
  parents={}
  for arc in net['arcs']:parents.setdefault(arc['from'],[]).append(arc)
  for parent,arcs in sorted(parents.items()):
   if len(arcs)>128:raise XBRLError('statement_calculation_term_budget')
   parent_row=row_map.get(parent);terms=[];eligible=parent_row is not None and parent_row['status']in REPORTED
   parent_unit=parent_row['unit']['semantic_sha256']if eligible else None
   for arc in arcs:
    child=row_map.get(arc['to']);w=Fraction(int(arc['weight']['numerator']),int(arc['weight']['denominator']))
    if w not in(-1,1):raise XBRLError('statement_accuracy_weight')
    same=child is not None and child['status']in REPORTED and child['unit']['semantic_sha256']==parent_unit
    eligible&=same;terms.append({'concept':arc['to'],'weight':int(w),'accuracy':child['accuracy']if same else None})
   accuracy=consistency(parent_row['accuracy']if eligible else None,terms);exact=None
   if eligible:
    reported=Fraction(parent_row['value']);total=sum((Fraction(row_map[a['to']]['value'])*Fraction(int(a['weight']['numerator']),int(a['weight']['denominator']))for a in arcs),Fraction(0));exact={'status':'EXACT_MATCH'if reported==total else'EXACT_DIFFERENCE','reported':rational(reported),'weighted_sum':rational(total),'residual':rational(reported-total)}
   checks.append({'parent':parent,'status':accuracy['status'],'accuracy_validation':accuracy,'exact_diagnostic':exact,'relationship_provenance':[a['provenance']for a in arcs]})
 return checks

def statement(filings,issuer,origin,collection_sha,as_of,*,role=None,form='10-K'):
 result=select(filings,issuer,origin,collection_sha,as_of,role=role,form=form);result.pop('sha256');result.update(schema=SCHEMA,profile=PROFILE,source_contexts={},source_units={})
 result['calculation_policy']='Conservative closed reported-accuracy enclosures;exact-value diagnostic is separate;compatibility is not full XBRL conformance or accounting validity'
 if result['status']!='AVAILABLE':return _result(result)
 p=filings[result['source_filing']['accession']];proof=p['dts_corroboration'];rels=proof['effective_relationships'];result['source_contexts']=copy.deepcopy(p['contexts']);result['source_units']=copy.deepcopy(p['units'])
 for period in result['periods']:
  for row in period['rows']:
   _numeric(row,p,proof);row['statement_mapping']['role']=role;row['statement_mapping']['relationship_indices']=[i for i,a in enumerate(result['relationships'])if a['to']==row['concept']];row['statement_mapping']['root']=row['concept']in next(n['roots']for n in rels['networks']if n['kind']=='presentation'and n['role']==role)
  period['calculations']=_calculations(period['rows'],rels['networks'],role)
 result['mapping_policy']='Source-scoped supplied presentation/declarations only;no name similarity or accounting equivalence inference;companyfacts metrics unchanged'
 return _result(result)
