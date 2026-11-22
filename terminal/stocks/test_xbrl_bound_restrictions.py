"""Authoritative XSD numeric bound restriction fixtures and real product admission."""
import copy,hashlib,json,tempfile,unittest
from decimal import localcontext
from pathlib import Path
from unittest.mock import patch
from .test_xbrl_types import sample,restriction,result,proof
from .test_xbrl_restriction_constraints import nil_sample
from .xbrl_types import BOUNDS_PROFILE,RESTRICTION_PROFILE,PROFILES,corroborate,validate_bound_numeric_result
from .xbrl_collection import FilingCollection
from .xbrl_instance import digest,selected_financials,XBRLError
from .test_xbrl_cross_role import inputs


def types(parent,child,base='s:decimal'):
 return restriction('Base',base,parent)+restriction('Amount','t:Base',child)
def evaluate(parent,child,value='5',base='s:decimal'):
 return result(sample(value,types=types(parent,child,base)),profile=BOUNDS_PROFILE)
def numeric(v):return proof(v)['numeric_value_validation']
def parsed(e=None):
 c=FilingCollection('0000320193');c.ingest_dts_batch([e or sample('5',types=types('<s:minInclusive value="0"/><s:maxExclusive value="10"/>','<s:minInclusive value="2"/><s:maxInclusive value="8"/>'))],numeric_profile=BOUNDS_PROFILE);return next(iter(c._filings.values()))
def rehash(p):p.pop('canonical_sha256',None);p['canonical_sha256']=digest(p)


class BoundRestrictions(unittest.TestCase):
 def test_valid_narrowing_and_exact_effective_bounds(self):
  e=sample('5',types=types('<s:minInclusive value="0"/><s:maxExclusive value="10"/>','<s:minExclusive value="2"/><s:maxInclusive value="8"/>'));before=copy.deepcopy(e);p=parsed(e);r=p['dts_corroboration']['numeric_value_validation']['facts'][0]
  self.assertEqual(r['effective_bounds'],{'lower':{'value':'2','inclusive':False},'upper':{'value':'8','inclusive':True},'integer_value_space':False});self.assertEqual(p['numeric_interpretation_profile'],BOUNDS_PROFILE);self.assertEqual(e,before);self.assertTrue(selected_financials(p)['history']['assets']);self.assertFalse(p['dts_corroboration']['schema_type_validation'])
 def test_same_inclusive_and_exclusive_bounds_can_repeat(self):
  for kind,value in(('minInclusive','0'),('minExclusive','0'),('maxInclusive','10'),('maxExclusive','10')):
   f=f'<s:{kind} value="{value}"/>'
   with self.subTest(kind=kind):self.assertTrue(evaluate(f,f)['history']['assets'])
 def test_exclusive_to_inclusive_equal_boundary_is_widening(self):
  for parent,child in(('<s:minExclusive value="0"/>','<s:minInclusive value="0"/>'),('<s:maxExclusive value="10"/>','<s:maxInclusive value="10"/>')):
   with self.subTest(parent=parent),self.assertRaisesRegex(XBRLError,'outside_base_value_space'):evaluate(parent,child)
 def test_inclusive_to_exclusive_equal_boundary_narrows(self):
  self.assertTrue(evaluate('<s:minInclusive value="0"/><s:maxInclusive value="10"/>','<s:minExclusive value="0"/><s:maxExclusive value="10"/>')['history']['assets'])
 def test_widening_bounds_reject_even_when_reported_value_satisfies_all(self):
  for child in('<s:minInclusive value="-1"/>','<s:minExclusive value="-1"/>','<s:maxInclusive value="11"/>','<s:maxExclusive value="11"/>'):
   with self.subTest(child=child),self.assertRaisesRegex(XBRLError,'outside_base_value_space'):evaluate('<s:minInclusive value="0"/><s:maxInclusive value="10"/>',child)
 def test_inherited_cross_side_constraints_apply_without_local_opposite(self):
  for parent,child in(('<s:maxInclusive value="10"/>','<s:minInclusive value="11"/>'),('<s:minInclusive value="0"/>','<s:maxInclusive value="-1"/>'),('<s:maxExclusive value="10"/>','<s:minExclusive value="10"/>'),('<s:minExclusive value="0"/>','<s:maxExclusive value="0"/>')):
   with self.subTest(parent=parent),self.assertRaisesRegex(XBRLError,'outside_base_value_space'):evaluate(parent,child)
 def test_range_definitions_are_checked_for_nil_facts(self):
  e=nil_sample(types('<s:minInclusive value="0"/>','<s:minInclusive value="-1"/>'))
  with self.assertRaisesRegex(XBRLError,'outside_base_value_space'):result(e,profile=BOUNDS_PROFILE)
 def test_nil_unavailable_is_retained_with_valid_bound_proof(self):
  v=result(nil_sample(types('<s:minInclusive value="0"/>','<s:minInclusive value="1"/>')),profile=BOUNDS_PROFILE);self.assertEqual(numeric(v)['facts'][0]['value_validation'],'NIL_UNAVAILABLE');self.assertEqual(v['history']['assets'],[])
 def test_bound_values_must_satisfy_inherited_digit_facets(self):
  for parent,child in(('<s:totalDigits value="1"/>','<s:maxInclusive value="12"/>'),('<s:fractionDigits value="0"/>','<s:minInclusive value="1.5"/>')):
   with self.subTest(parent=parent),self.assertRaisesRegex(XBRLError,'outside_base_value_space'):evaluate(parent,child)
 def test_bound_values_must_belong_to_inherited_enumeration(self):
  with self.assertRaisesRegex(XBRLError,'outside_base_value_space'):evaluate('<s:enumeration value="1"/><s:enumeration value="5"/><s:enumeration value="9"/>','<s:minInclusive value="2"/>')
  self.assertTrue(evaluate('<s:enumeration value="1"/><s:enumeration value="5"/><s:enumeration value="9"/>','<s:minInclusive value="5"/>')['history']['assets'])
 def test_deep_inherited_bound_cannot_be_widened_after_unbounded_step(self):
  t=restriction('Root','s:decimal','<s:minExclusive value="0"/>')+restriction('Base','t:Root','')+restriction('Amount','t:Base','<s:minInclusive value="0"/>')
  with self.assertRaisesRegex(XBRLError,'outside_base_value_space'):result(sample('5',types=t),profile=BOUNDS_PROFILE)
 def test_builtin_integer_bounds_are_exact(self):
  v=result(sample('255',kind='s:unsignedByte',types=''),profile=BOUNDS_PROFILE);r=numeric(v)['facts'][0]['effective_bounds'];self.assertEqual(r,{'lower':{'value':'0','inclusive':True},'upper':{'value':'255','inclusive':True},'integer_value_space':True})
  v=result(sample('18446744073709551615',kind='s:unsignedLong',types=''),profile=BOUNDS_PROFILE);self.assertEqual(numeric(v)['facts'][0]['effective_bounds']['upper']['value'],'18446744073709551615')
 def test_empty_discrete_integer_domain_is_explicitly_unsupported(self):
  e=nil_sample(types('<s:minExclusive value="1"/>','<s:maxExclusive value="2"/>',base='s:integer'))
  with self.assertRaisesRegex(XBRLError,'empty_integer_domain_unsupported'):result(e,profile=BOUNDS_PROFILE)
 def test_empty_inherited_decimal_domain_is_explicitly_unsupported(self):
  e=nil_sample(types('<s:maxInclusive value="1"/>','<s:minExclusive value="1"/>'))
  with self.assertRaisesRegex(XBRLError,'empty_domain_unsupported'):result(e,profile=BOUNDS_PROFILE)
 def test_closed_singleton_domain_is_valid(self):
  v=evaluate('<s:minInclusive value="5"/>','<s:maxInclusive value="5"/>');self.assertEqual(v['history']['assets'][0]['value'],'5')
 def test_decimal_context_cannot_round_restriction_comparisons(self):
  with localcontext()as context:
   context.prec=2
   with self.assertRaisesRegex(XBRLError,'outside_base_value_space'):evaluate('<s:minInclusive value="123456789.123456790"/>','<s:minInclusive value="123456789.123456789"/>',value='123456790')
 def test_source_hash_metadata_and_declaration_sources_remain_bound(self):
  p=parsed();before=copy.deepcopy(p);validate_bound_numeric_result(p);self.assertEqual(p,before)
  for change in('hash','kind','missing','duplicate','unresolved'):
   x=copy.deepcopy(p);v=x['dts_corroboration']
   if change=='hash':v['documents'][0]['sha256']='invalid'
   elif change=='kind':v['documents'][0]['kind']='linkbase'
   elif change=='missing':next(iter(v['type_declarations'].values()))['source_documents']=[]
   elif change=='duplicate':v['documents']*=2
   else:v['unresolved']=[{'uri':'https://authored.invalid/missing.xsd'}]
   rehash(x)
   with self.subTest(change=change),self.assertRaisesRegex(XBRLError,'bound_result_contract'):selected_financials(x)
 def test_resigned_effective_bounds_and_validation_claims_reject(self):
  for change in('bounds','scope','record','profile','marker','missing_marker','selected'):
   p=parsed();v=p['dts_corroboration']['numeric_value_validation']
   if change=='bounds':v['facts'][0]['effective_bounds']['lower']['value']='-999'
   elif change=='scope':v['scope']='Full schema conformance'
   elif change=='record':v['facts'][0]['value_validation']='NIL_UNAVAILABLE'
   elif change=='profile':v['profile']=RESTRICTION_PROFILE
   elif change=='marker':p['numeric_interpretation_profile']='invented'
   elif change=='missing_marker':del p['numeric_interpretation_profile']
   else:p['dts_corroboration']['selected_facts']=[]
   rehash(p)
   with self.subTest(change=change),self.assertRaisesRegex(XBRLError,'bound_result_contract'):selected_financials(p)
 def test_retained_facet_unknown_kind_duplicates_and_types_reject(self):
  for change in('kind','duplicate','value','fixed','extension'):
   p=parsed();d=next(iter(p['dts_corroboration']['type_declarations'].values()))['declaration']
   if change=='kind':d['facets'][0]['kind']='invented'
   elif change=='duplicate':d['facets']*=2
   elif change=='value':d['facets'][0]['value']=True
   elif change=='fixed':d['facets'][0]['fixed']='yes'
   else:d['derivation']='SIMPLE_CONTENT_EXTENSION'
   rehash(p)
   with self.subTest(change=change),self.assertRaisesRegex(XBRLError,'bound_result_contract'):selected_financials(p)
 def test_legacy_profiles_do_not_acquire_new_semantics_or_fields(self):
  e=sample('5',types=types('<s:minInclusive value="0"/>','<s:minInclusive value="-1"/>'));v=result(e,profile=RESTRICTION_PROFILE);self.assertTrue(v['history']['assets']);self.assertNotIn('effective_bounds',numeric(v)['facts'][0]);self.assertEqual(PROFILES[-2],RESTRICTION_PROFILE);self.assertEqual(PROFILES[-1],BOUNDS_PROFILE)
 def test_atomic_collection_admission_preserves_previous_accepted_source(self):
  c=FilingCollection('0000320193');c.ingest_dts_batch([sample('5')],numeric_profile=BOUNDS_PROFILE);before=c.page();bad=sample('5',types=types('<s:minInclusive value="0"/>','<s:minInclusive value="-1"/>'),accession='0000000123-24-000002')
  with self.assertRaises(XBRLError):c.ingest_dts_batch([bad],numeric_profile=BOUNDS_PROFILE)
  self.assertEqual(c.page(),before)
 def test_actual_company_v2_statement_consumer_uses_bound_admission(self):
  from .test_xbrl_statements import entry,ROLE,LATE
  from .service import StockWorkspace
  from .xbrl_product import company_contract
  e=entry();d=e['documents'][0];raw=d['raw'].replace(b'<s:schema ',b'<s:schema xmlns:t="http://fasb.org/us-gaap/2024" ',1).replace(b'type="x:monetaryItemType"',b'type="t:Amount"');raw=raw.replace(b'</s:schema>',types('<s:minInclusive value="0"/>','<s:maxInclusive value="1000"/>').encode()+b'</s:schema>');d['raw']=raw;d['sha256']=hashlib.sha256(raw).hexdigest();c=FilingCollection('0000320193');c.ingest_dts_batch([e],numeric_profile=BOUNDS_PROFILE);w=StockWorkspace(environment={});w.admit_xbrl_collection('AAPL',c);out=company_contract(w,'AAPL',LATE,role=ROLE,profile='accuracy-extension-v2');self.assertEqual(out['schema'],'gig.backend.company_xbrl.v2');self.assertEqual(out['statement_view']['status'],'AVAILABLE');self.assertEqual(out['statement_view']['periods'][0]['rows'][0]['value'],'1000')
 def test_original_inline_set_batch_reaches_actual_selected_consumer(self):
  from .test_inline_set import html,doc
  from .test_xbrl_types import sample
  e=sample('5');raw=e['raw'].decode();resources=raw[raw.index('<x:context'):raw.index('<g:Assets')];page=html('',resources=True).decode();start=page.index('<x:context');end=page.index('</ix:resources>');page=page[:start]+resources+page[end:];originals=[doc('resources.xhtml',page.encode()),doc('facts.xhtml',html('<ix:nonFraction name="g:Assets" contextRef="I" unitRef="USD">5</ix:nonFraction>'))];c=FilingCollection('0000320193');c.ingest_inline_set_batch([{'documents':originals,'concepts':e['concepts'],'taxonomy_documents':e['documents']}],numeric_profile=BOUNDS_PROFILE);out=next(iter(c._filings.values()));self.assertEqual(out['schema'],'gig.sec.xbrl.inline_set.v1');self.assertEqual(out['numeric_interpretation_profile'],BOUNDS_PROFILE);self.assertEqual(selected_financials(out)['history']['assets'][0]['value'],'5')
 def test_selected_numeric_scope_does_not_claim_all_schema_or_gaap_equivalence(self):
  p=parsed();v=p['dts_corroboration']['numeric_value_validation'];self.assertIn('not complete XML Schema/OIM/accounting',v['scope']);self.assertFalse(p['dts_corroboration']['complete_statements']);self.assertEqual(p['facts'][0]['value'],'5')
 def test_fixed_bound_facets_remain_explicitly_unsupported(self):
  with self.assertRaisesRegex(XBRLError,'selected_type_unsupported'):result(sample('5',types=restriction(facets='<s:minInclusive value="0" fixed="true"/>')),profile=BOUNDS_PROFILE)
 def test_cycle_and_depth_limits_remain_enforced(self):
  for t in(restriction('Amount','t:Amount',''),''.join(restriction('Amount'if i==0 else'T'+str(i),'t:T'+str(i+1)if i<8 else's:decimal','')for i in range(9))):
   with self.subTest(types=t),self.assertRaisesRegex(XBRLError,'type_cycle|type_depth'):result(sample('5',types=t),profile=BOUNDS_PROFILE)
 def test_output_budget_and_missing_closure_fail_before_proof_publication(self):
  with patch('terminal.stocks.xbrl_types.MAX_OUTPUT_BYTES',1),self.assertRaisesRegex(XBRLError,'bound_source_contract|output_budget'):parsed()
 def test_input_objects_remain_detached_from_admitted_proof(self):
  e=sample('5');c=FilingCollection('0000320193');c.ingest_dts_batch([e],numeric_profile=BOUNDS_PROFILE);first=c.at_acceptance_time('2024-02-02T00:00:00Z');first['selected_input_coverage'][0]['xbrl_coverage']['dts_corroboration']['numeric_value_validation']['facts'][0]['effective_bounds']['integer_value_space']=True;self.assertFalse(numeric(c.at_acceptance_time('2024-02-02T00:00:00Z'))['facts'][0]['effective_bounds']['integer_value_space'])
 def test_valid_lexical_source_hash_change_requires_matching_declaration_receipt(self):
  p=parsed();p['dts_corroboration']['documents'][0]['sha256']='1'*64;rehash(p)
  with self.assertRaisesRegex(XBRLError,'bound_result_contract'):selected_financials(p)
 def test_source_declaration_fingerprint_cannot_be_resigned_away(self):
  p=parsed();p['dts_corroboration']['numeric_value_validation']['source_declarations_sha256']='0'*64;rehash(p)
  with self.assertRaisesRegex(XBRLError,'bound_result_contract'):selected_financials(p)
 def test_reported_nil_flag_is_boolean_not_truthy_metadata(self):
  p=parsed();p['facts'][0]['nil']='false';rehash(p)
  with self.assertRaisesRegex(XBRLError,'bound_result_contract'):selected_financials(p)
 def test_normative_builtin_numeric_type_replacement_is_unsupported(self):
  from .test_xbrl_dts import document
  e=sample('5',kind='s:decimal',types='');replacement=b'<s:schema xmlns:s="http://www.w3.org/2001/XMLSchema" targetNamespace="http://www.w3.org/2001/XMLSchema"><s:simpleType name="decimal"><s:restriction base="s:string"/></s:simpleType></s:schema>';e['documents'].append(document('counterfeit-standard.xsd',replacement));d=e['documents'][0];raw=d['raw'].replace(b'</s:schema>',b'<s:import namespace="http://www.w3.org/2001/XMLSchema" schemaLocation="counterfeit-standard.xsd"/></s:schema>');d['raw']=raw;d['sha256']=hashlib.sha256(raw).hexdigest()
  with self.assertRaisesRegex(XBRLError,'bound_type_contract'):result(e,profile=BOUNDS_PROFILE)
 def test_legacy_returned_proof_cannot_corrupt_private_collection(self):
  c=FilingCollection('0000320193');c.ingest_dts_batch([sample('5')],numeric_profile=RESTRICTION_PROFILE);before=c.page();v=c.at_acceptance_time('2024-02-02T00:00:00Z');v['selected_input_coverage'][0]['xbrl_coverage']['dts_corroboration']['documents'][0]['sha256']='1'*64;self.assertEqual(c.page(),before);self.assertEqual(c.at_acceptance_time('2024-02-02T00:00:00Z')['history']['assets'][0]['value'],'5')
 def test_real_offline_cli_exports_bound_profile_into_company_consumer(self):
  from scripts.inspect_xbrl_instances import inspect
  e=sample('5')
  with tempfile.TemporaryDirectory()as directory:
   root=Path(directory);(root/'instance.xml').write_bytes(e['raw']);docs=[]
   for i,d in enumerate(e['documents']):
    name='taxonomy'+str(i)+'.xml';(root/name).write_bytes(d['raw']);docs.append({'path':name,'uri':d['uri'],'sha256':d['sha256']})
   batch={'schema':'gig.sec.xbrl.input_dts_batch.v1','issuer_cik':'0000320193','origin':'HISTORICAL_SYNTHETIC','numeric_profile':BOUNDS_PROFILE,'entries':[{'path':'instance.xml','manifest':e['manifest'],'gaap_namespace':'http://fasb.org/us-gaap/2024','instance_uri':e['instance_uri'],'documents':docs}]};(root/'batch.json').write_text(json.dumps(batch));summary,out=inspect(root/'batch.json','2024-02-02T00:00:00Z');self.assertEqual(summary['status'],'OFFLINE_PROFILE_VALIDATED');self.assertEqual(out['history']['assets'][0]['value'],'5');self.assertEqual(numeric(out)['profile'],BOUNDS_PROFILE)

 def test_repeated_exclusive_bound_exception_bypasses_base_enumeration_membership(self):
  for kind,bound in(('minExclusive','0'),('maxExclusive','10')):
   parent=f'<s:{kind} value="{bound}"/><s:enumeration value="1"/><s:enumeration value="5"/>'
   with self.subTest(kind=kind):self.assertEqual(evaluate(parent,f'<s:{kind} value="{bound}"/>')['history']['assets'][0]['value'],'5')
 def test_repeated_exclusive_bound_exception_bypasses_base_digit_membership(self):
  for kind,bound in(('minExclusive','-100'),('maxExclusive','100')):
   parent=f'<s:{kind} value="{bound}"/><s:totalDigits value="1"/>'
   with self.subTest(kind=kind):self.assertEqual(evaluate(parent,f'<s:{kind} value="{bound}"/>')['history']['assets'][0]['value'],'5')
 def test_old_exclusive_bound_cannot_bypass_newer_narrowed_parent(self):
  for kind,old,new in(('minExclusive','0','2'),('maxExclusive','10','8')):
   t=restriction('Root','s:decimal',f'<s:{kind} value="{old}"/>')+restriction('Base','t:Root',f'<s:{kind} value="{new}"/>')+restriction('Amount','t:Base',f'<s:{kind} value="{old}"/>')
   with self.subTest(kind=kind),self.assertRaisesRegex(XBRLError,'outside_base_value_space'):result(sample('5',types=t),profile=BOUNDS_PROFILE)
 def test_exclusive_repetition_cannot_bypass_opposite_inclusive_parent_narrowing(self):
  for oldkind,old,newkind,new in(('minExclusive','0','minInclusive','2'),('maxExclusive','10','maxInclusive','8')):
   t=restriction('Root','s:decimal',f'<s:{oldkind} value="{old}"/>')+restriction('Base','t:Root',f'<s:{newkind} value="{new}"/>')+restriction('Amount','t:Base',f'<s:{oldkind} value="{old}"/>')
   with self.subTest(kind=oldkind),self.assertRaisesRegex(XBRLError,'outside_base_value_space'):result(sample('5',types=t),profile=BOUNDS_PROFILE)
 @staticmethod
 def _resign_fact_identity(p,index=0):
  fact=p['facts'][index];old=fact['source_fact_id'];core={k:v for k,v in fact.items()if k!='source_fact_id'}
  if 'document_set'in p:identity={'document_set_sha256':p['document_set']['sha256'],'fact':core}
  else:
   if core.get('admission')=='CONFLICTED_EXACT_VALUES':core['admission']='ADMITTED_PROFILE'
   identity={'source_sha256':p['source']['source_sha256'],'fact':core}
  fact['source_fact_id']=digest(identity)
  for field in('selected_facts',):
   for record in p['dts_corroboration'][field]:
    if record['source_fact_id']==old:record['source_fact_id']=fact['source_fact_id']
  for record in p['dts_corroboration']['numeric_value_validation']['facts']:
   if record['source_fact_id']==old:record['source_fact_id']=fact['source_fact_id']
  rehash(p)
 def test_reported_value_and_lexical_must_agree_even_after_all_fact_ids_are_resigned(self):
  for field,new in(('value','999'),('value',None),('value',5),('lexical_value','6')):
   for resign in(False,True):
    p=parsed();p['facts'][0][field]=new
    if resign:self._resign_fact_identity(p)
    else:rehash(p)
    with self.subTest(field=field,new=new,resign=resign),self.assertRaisesRegex(XBRLError,'bound_result_contract'):selected_financials(p)
 def test_original_source_fact_id_cannot_be_replaced_with_derived_row_id(self):
  p=parsed();old=p['facts'][0]['source_fact_id'];p['facts'][0]['source_fact_id']='1'*64
  for record in p['dts_corroboration']['selected_facts']+p['dts_corroboration']['numeric_value_validation']['facts']:
   if record['source_fact_id']==old:record['source_fact_id']='1'*64
  rehash(p)
  with self.assertRaisesRegex(XBRLError,'bound_result_contract'):selected_financials(p)
 def test_nil_value_lexical_status_and_boolean_must_remain_consistent(self):
  for change in('value','lexical','nil','status'):
   p=parsed(nil_sample(types('<s:minInclusive value="0"/>','<s:minInclusive value="1"/>')));fact=p['facts'][0]
   if change=='value':fact['value']='5'
   elif change=='lexical':fact['lexical_value']='5'
   elif change=='nil':fact['nil']=False
   else:fact['nil_status']=None
   self._resign_fact_identity(p)
   with self.subTest(change=change),self.assertRaisesRegex(XBRLError,'bound_result_contract'):selected_financials(p)
 def test_context_period_mutation_requires_its_own_hash_and_fact_join(self):
  for rehash_context in(False,True):
   p=parsed();context=p['contexts']['I'];context['period']['end']='2020-01-01'
   if rehash_context:context['semantic_sha256']=digest({k:context[k]for k in('issuer_cik','period','dimensions','opaque_segment')})
   self._resign_fact_identity(p)
   with self.subTest(rehash_context=rehash_context),self.assertRaisesRegex(XBRLError,'bound_result_contract'):selected_financials(p)
 def test_unit_mutation_requires_its_own_hash_and_fact_join(self):
  for rehash_unit in(False,True):
   p=parsed();unit=p['units']['USD'];unit['numerator']=['{http://www.xbrl.org/2003/iso4217}EUR']
   if rehash_unit:unit['semantic_sha256']=digest({k:unit[k]for k in('numerator','denominator')})
   self._resign_fact_identity(p)
   with self.subTest(rehash_unit=rehash_unit),self.assertRaisesRegex(XBRLError,'bound_result_contract'):selected_financials(p)
 def test_context_reference_swap_cannot_reuse_original_fact_aspect_hash(self):
  p=parsed();other=copy.deepcopy(p['contexts']['I']);other['period']['end']='2020-01-01';other['semantic_sha256']=digest({k:other[k]for k in('issuer_cik','period','dimensions','opaque_segment')});p['contexts']['Other']=other;p['facts'][0]['context_ref']='Other';p['facts'][0]['attributes']['contextRef']='Other';self._resign_fact_identity(p)
  with self.assertRaisesRegex(XBRLError,'bound_result_contract'):selected_financials(p)
 def test_unit_reference_swap_cannot_reuse_original_fact_aspect_hash(self):
  p=parsed();other={'numerator':['{http://www.xbrl.org/2003/iso4217}EUR'],'denominator':[]};other['semantic_sha256']=digest(other);p['units']['EUR']=other;p['facts'][0]['unit_ref']='EUR';p['facts'][0]['attributes']['unitRef']='EUR';self._resign_fact_identity(p)
  with self.assertRaisesRegex(XBRLError,'bound_result_contract'):selected_financials(p)
 def test_declared_boolean_and_type_metadata_are_strict_after_fingerprint_resigning(self):
  for field,value in(('abstract',0),('abstract','false'),('nillable',0),('nillable','false'),('type','decimal'),('period_type',True)):
   p=parsed();proof=p['dts_corroboration'];concept=p['facts'][0]['concept'];proof['concept_declarations'][concept]['declaration'][field]=value;proof['numeric_value_validation']['source_declarations_sha256']=digest({k:proof.get(k,{})for k in('documents','concept_declarations','type_declarations')});rehash(p)
   with self.subTest(field=field,value=value),self.assertRaisesRegex(XBRLError,'bound_result_contract'):selected_financials(p)
 def test_unit_lists_and_semantic_shape_are_bounded_exact_and_sorted(self):
  for field,value in(('numerator',[]),('numerator',['bad']),('numerator',[1]),('numerator',['{urn:z}B','{urn:a}A']),('denominator',['{urn:a}A']*9),('semantic_sha256',True)):
   p=parsed();p['units']['USD'][field]=value;rehash(p)
   with self.subTest(field=field,value=value),self.assertRaisesRegex(XBRLError,'bound_result_contract'):selected_financials(p)
 def test_context_entity_identifier_and_semantic_shape_are_strict(self):
  for field,value in(('identifier_lexical','0000000001'),('issuer_cik','0000000001'),('period',[]),('dimensions',{}),('opaque_segment',True)):
   p=parsed();p['contexts']['I'][field]=value;rehash(p)
   with self.subTest(field=field,value=value),self.assertRaisesRegex(XBRLError,'bound_result_contract'):selected_financials(p)
 def test_malformed_proof_report_fact_and_reference_shapes_raise_xbrl_error(self):
  for change in('proof_list','proof_string','report_list','fact_list','context_map','unit_map','unit_record','attributes','reference'):
   p=parsed()
   if change=='proof_list':p['dts_corroboration']=[]
   elif change=='proof_string':p['dts_corroboration']='malformed'
   elif change=='report_list':p['dts_corroboration']['numeric_value_validation']=[]
   elif change=='fact_list':p['facts'][0]=[]
   elif change=='context_map':p['contexts']={'I':[]}
   elif change=='unit_map':p['units']=[]
   elif change=='unit_record':p['units']['USD']=[]
   elif change=='attributes':p['facts'][0]['attributes']=[]
   else:p['facts'][0]['context_ref']=[]
   rehash(p)
   with self.subTest(change=change),self.assertRaises(XBRLError):validate_bound_numeric_result(p)
   with self.subTest(selected_change=change),self.assertRaises(XBRLError):selected_financials(p)
 def test_legitimate_conflicting_source_ids_and_lexical_padding_still_validate(self):
  for lexical in('0005.00','-0.00','+005'):
   p=parsed(sample(lexical));validate_bound_numeric_result(p);self.assertEqual(p['facts'][0]['lexical_value'],lexical);self.assertEqual(selected_financials(p)['history']['assets'][0]['value'],p['facts'][0]['value'])
  e=sample('5');e['raw']=e['raw'].replace(b'<g:Assets contextRef="I" unitRef="USD">5</g:Assets>',b'<g:Assets contextRef="I" unitRef="USD">5</g:Assets><g:Assets contextRef="I" unitRef="USD">6</g:Assets>');e['manifest']['source_sha256']=hashlib.sha256(e['raw']).hexdigest();p=parsed(e);self.assertTrue(all(f['admission']=='CONFLICTED_EXACT_VALUES'for f in p['facts']));validate_bound_numeric_result(p);self.assertFalse(selected_financials(p)['history']['assets'])
 def test_declared_dts_identity_is_well_formed_and_fingerprint_bound(self):
  for value in('malformed','1'*64,True):
   p=parsed();p['dts_corroboration']['dts_sha256']=value;rehash(p)
   with self.subTest(value=value),self.assertRaisesRegex(XBRLError,'bound_result_contract'):selected_financials(p)
 def test_retained_source_uri_must_remain_absolute_canonical_and_bounded(self):
  for value in('', '../schema.xsd','file:///tmp/schema.xsd'):
   p=parsed();v=p['dts_corroboration'];old=v['documents'][0]['uri'];v['documents'][0]['uri']=value
   for entry in list(v['type_declarations'].values())+list(v['concept_declarations'].values()):entry['source_documents']=[value if u==old else u for u in entry['source_documents']]
   v['numeric_value_validation']['source_declarations_sha256']=digest({k:v.get(k,{})for k in('dts_sha256','documents','concept_declarations','type_declarations')});rehash(p)
   with self.subTest(value=value),self.assertRaisesRegex(XBRLError,'bound_result_contract'):selected_financials(p)
 def test_inline_returned_document_receipts_are_detached_too(self):
  from .test_inline_set import parse as inline_parse
  p=inline_parse();before=copy.deepcopy(p);out=selected_financials(p);out['xbrl_coverage']['document_set']['documents'][0]['source']['source_sha256']='0'*64;self.assertEqual(p,before)
