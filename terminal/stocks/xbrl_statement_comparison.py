"""Bounded original-source comparison of independently selected statement vintages.

Exact reported numbers are compared only after source/aspect/relationship checks.
No alias mapping, additive amendment, missing-value filling or restatement inference.
"""
import copy
from fractions import Fraction
from . import sec
from .financial_intelligence_product import company_source_accounting
from .xbrl_instance import canonical,digest,XBRLError
from .xbrl_statement_set import KINDS
from .xbrl_types import COMPLEX_PROFILE,_resolve

PROFILE='ORIGINAL_SOURCE_ADJACENT_VINTAGES_V1'
MAX_CUTOFFS=8
MAX_ROWS=4096
MAX_OUTPUT=4*1024*1024


def _finish(value):
 value['sha256']=digest(value)
 if len(canonical(value))>MAX_OUTPUT:raise XBRLError('statement_comparison_output_budget')
 return value


def _rows(section):
 rows={}
 for period in section['periods']:
  for row in period['rows']:
   key=(period['start'],period['end'],row['concept'])
   if key in rows:raise XBRLError('statement_comparison_duplicate_row')
   rows[key]=row
 return rows


def _side(index,packet,row):
 if row is None:return None
 source=packet['accounting']['source_filing']
 return {'entry_index':index,'source_packet_sha256':packet['sha256'],
         'row_sha256':digest(row),'accession':source['accession'],
         'source_sha256':source['source_sha256'],
         'original_parsed_sha256':packet['accounting']['original_parsed_sha256'],
         'dts_sha256':packet['accounting']['dts_sha256'],
         'status':row['status'],'reason':row['reason'],'reported_value':row['value'],
         'unit':copy.deepcopy(row['unit']),
         'source_facts':copy.deepcopy(row['facts']),
         'numeric_facts':copy.deepcopy(row['numeric_facts']),
         'equivalence_status':row['equivalence_status'],
         'essence_concept':row['essence_concept']}


def _aspects(packet,row):
 source=packet['source']
 # A statement's grouping key deliberately omits lexical entity spelling. Do not
 # normalize multiple entity lexicals into one comparable historical data point.
 aspects={canonical({k:source['contexts'][fact['context_ref']][k]
                     for k in('issuer_cik','identifier_lexical','period','dimensions','opaque_segment')})
          for fact in row['facts']}
 return aspects


def _type_identity(packet,concept):
 graph=packet['dts'];declaration=graph['concepts'][concept]['declaration']
 base,path=_resolve(declaration['type'],graph.get('type_declarations',{}),COMPLEX_PROFILE)
 # Original document hashes remain in each envelope; a source document revision
 # alone does not change a numeric type. Its exact declarations/facets do.
 return {'declaration':declaration,'resolved_base':base,
         'restriction_path':[{'type':entry['type'],'declaration':entry['declaration']}for entry in path]}


def _relationship_identity(row):
 return {'essence_concept':row['essence_concept'],
         'relationships':[{'kind':r['kind'],'role':r['role'],'from':r['from'],'to':r['to'],
                           'declarations':{k:r['declaration_constraints'][k]
                             for k in('status','type','period_type','from_declaration','to_declaration')}}
                          for r in row['accounting_relationships']]}


def _calculation_index(section,packet):
 contexts=packet['source']['contexts'];parents={}
 for net in packet['dts']['effective_relationships']['networks']:
  if net['kind']=='calculation'and net['role']==section['presentation_role']:
   for arc in net['arcs']:parents.setdefault(arc['from'],{arc['from']}).add(arc['to'])
 result={}
 for period in section['periods']:
  points={row['concept']:{(f['context_sha256'],f['unit_sha256'],
          contexts[f['context_ref']]['identifier_lexical'])for f in row['facts']}
          for row in period['rows']}
  for row in period['rows']:result[(period['start'],period['end'],row['concept'])]=[]
  for check in period['calculations']:
   if check.get('status')=='UNSUPPORTED':members=set(points);aspects=None
   else:
    aspects=(check['context_sha256'],check['unit_sha256'],check['identifier_lexical'])
    members=parents.get(check['parent'],{check['parent']})
   for concept in members&points.keys():
    if aspects is None or aspects in points[concept]:
     result[(period['start'],period['end'],concept)].append(check)
 return result


def _classify(old,new,left,right,roles_equal,left_calcs,right_calcs):
 if not roles_equal:return 'ROLE_BINDING_CHANGED',False
 if left is None:return 'ROW_NOT_IN_PREVIOUS_VIEW',False
 if right is None:return 'ROW_NOT_IN_CURRENT_VIEW',False
 states=(left['status'],right['status'])
 if 'CONFLICTING'in states:return 'CONFLICTING_SOURCE_ROW',False
 if 'UNSUPPORTED'in states:return 'UNSUPPORTED_SOURCE_ROW',False
 if states==('MISSING','MISSING'):return 'BOTH_SOURCE_ROWS_MISSING',False
 if left['status']=='MISSING':return 'PREVIOUS_SOURCE_ROW_MISSING',False
 if right['status']=='MISSING':return 'CURRENT_SOURCE_ROW_MISSING',False
 if states!=('SUPPORTED','SUPPORTED'):raise XBRLError('statement_comparison_row_status')
 a=_aspects(old,left);b=_aspects(new,right)
 if len(a)!=1 or len(b)!=1:return 'AMBIGUOUS_SOURCE_ASPECTS',False
 if a!=b:return 'INCOMPATIBLE_SOURCE_CONTEXT',False
 if left['unit']!=right['unit']:return 'INCOMPATIBLE_SOURCE_UNIT',False
 if canonical(_type_identity(old,left['concept']))!=canonical(_type_identity(new,right['concept'])):
  return 'SOURCE_DECLARATION_CHANGED',False
 if canonical(_relationship_identity(left))!=canonical(_relationship_identity(right)):
  return 'ACCOUNTING_RELATIONSHIP_CHANGED',False
 if any(row['equivalence_status']in('CONFLICTING_REPORTED_VALUES','UNSUPPORTED_ASPECTS','AMBIGUOUS_SOURCE_RELATIONSHIPS')for row in(left,right)):
  return 'INCOMPATIBLE_ACCOUNTING_RELATIONSHIP',False
 if any(check['status']=='REQUIRED_ELEMENT_MISSING'for row in(left,right)
        for relation in row['accounting_relationships']for check in relation['checks']):
  return 'ACCOUNTING_REQUIREMENT_UNSATISFIED',False
 if any(check.get('calculation',{}).get('status')=='DEFINITELY_INCONSISTENT'for check in left_calcs+right_calcs):
  return 'CALCULATION_INCONSISTENT',False
 # This compares reported numeric values, not rounding intervals or an unknown
 # underlying exact value. The original lexical/accuracy evidence stays intact.
 return ('REPORTED_NUMERIC_VALUE_UNCHANGED'if Fraction(left['value'])==Fraction(right['value'])
         else'REPORTED_NUMERIC_VALUE_CHANGED'),True


def _source_relation(old,new):
 a=old['accounting'];b=new['accounting']
 if old['source']is None or new['source']is None:return 'SELECTED_ORIGINAL_SOURCE_UNAVAILABLE'
 before=a['source_filing']['accession'];after=b['source_filing']['accession']
 if before==after:return 'SAME_SELECTED_FILING'
 lineage=b['lineage']
 if lineage and lineage['status']=='SUPPLIED_CHAIN_RESOLVED'and any(
    r['source']['accession']==before for r in lineage['sources'][1:]):
  return 'EXPLICIT_SUPPLIED_AMENDMENT_CHAIN'
 return 'INDEPENDENT_SELECTED_FILINGS'


def company_statement_vintage_comparison(workspace,symbol,cutoffs,source_inputs,role_bindings,
                                         *,form='10-K',expected_collection_sha256=None):
 """Reconstruct each supplied cutoff from originals and compare adjacent views.

 A private callable export only; no HTTP route/provider activation. Unavailable
 adjacent views are never replaced with an older available filing.
 """
 if type(cutoffs)is not list or not 1<=len(cutoffs)<=MAX_CUTOFFS:
  raise XBRLError('statement_comparison_cutoff_budget')
 instants=[sec.acceptance_ns(at)for at in cutoffs]
 if any(a>=b for a,b in zip(instants,instants[1:])):
  raise XBRLError('statement_comparison_cutoff_order')
 entries=[];identity=expected_collection_sha256
 for at in cutoffs:
  packet=company_source_accounting(workspace,symbol,at,source_inputs,role_bindings,
                                  form=form,expected_collection_sha256=identity)
  if identity is None:identity=packet['collection_sha256']
  if packet['collection_sha256']!=identity:raise XBRLError('statement_comparison_collection_changed')
  if entries and packet['instrument']!=entries[0]['instrument']:
   raise XBRLError('statement_comparison_instrument_changed')
  entries.append(packet)
  if len(canonical(entries))>MAX_OUTPUT:raise XBRLError('statement_comparison_output_budget')
 comparisons=[];count=0;used_bytes=len(canonical(entries))
 for index,(old,new)in enumerate(zip(entries,entries[1:])):
  sections={}
  for kind in KINDS:
   before=old['accounting']['statements'].get(kind);after=new['accounting']['statements'].get(kind)
   section={'previous_status':None if before is None else before['status'],
            'current_status':None if after is None else after['status'],
            'previous_reason':old['reason']if before is None else before['reason'],
            'current_reason':new['reason']if after is None else after['reason'],
            'previous_role_binding':None if before is None else{k:before[k]for k in('presentation_role','accounting_role')},
            'current_role_binding':None if after is None else{k:after[k]for k in('presentation_role','accounting_role')},
            'status':'UNAVAILABLE_ADJACENT_VIEW','rows':[]}
   if before is not None and after is not None and before['status']==after['status']=='AVAILABLE':
    section['status']='ANALYZED_SOURCE_ROWS';left=_rows(before);right=_rows(after)
    roles_equal=section['previous_role_binding']==section['current_role_binding']
    left_calcs=_calculation_index(before,old);right_calcs=_calculation_index(after,new)
    for key in sorted(left.keys()|right.keys(),key=lambda k:(k[1],k[0]or'',k[2]),reverse=True):
     count+=1
     if count>MAX_ROWS:raise XBRLError('statement_comparison_row_budget')
     a=left.get(key);b=right.get(key)
     ac=left_calcs.get(key,[]);bc=right_calcs.get(key,[])
     status,comparable=_classify(old,new,a,b,roles_equal,ac,bc)
     comparison={'concept':key[2],'period':{'start':key[0],'end':key[1]},
       'status':status,'reported_values_comparable':comparable,
       'underlying_value_equality_established':False,'restatement_established':False,
       'previous':_side(index,old,a),'current':_side(index+1,new,b),
       'previous_calculations':copy.deepcopy(ac),'current_calculations':copy.deepcopy(bc)}
     used_bytes+=len(canonical(comparison))
     if used_bytes>MAX_OUTPUT:raise XBRLError('statement_comparison_output_budget')
     section['rows'].append(comparison)
   sections[kind]=section
  comparisons.append({'previous_entry_index':index,'current_entry_index':index+1,
     'source_relation':_source_relation(old,new),'restatement_established':False,
     'statements':sections})
  if len(canonical({'entries':entries,'comparisons':comparisons}))>MAX_OUTPUT:
   raise XBRLError('statement_comparison_output_budget')
 return _finish({'schema':'gig.backend.statement_vintage_comparison.v1','profile':PROFILE,
      'instrument':copy.deepcopy(entries[0]['instrument']),'form_family':form,
      'collection_sha256':identity,'entries':entries,'comparisons':comparisons,
      'status':'ANALYZED_BOUNDED_SUPPLIED_VINTAGES','complete_history':False,
      'complete_statements':False,'restatements_inferred':False,'values_filled':False,
      'gaap_aliases_inferred':False,'selected_reported_value':None,
      'read_only':True,'provider_requested':False,
      'policy':'Adjacent exact supplied acceptance cutoffs;exact source concepts and compatible original aspects only;reported-number comparison is not restatement or rounding-based equality'})
