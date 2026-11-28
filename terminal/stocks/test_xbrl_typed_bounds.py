"""Original-byte V11 fixtures and independently resigned consumer contradictions."""
import copy,hashlib,unittest
from unittest.mock import patch
from .test_xbrl_typed_hypercubes import fixture,inputs,proof,rehash,derive as legacy
from .test_xbrl_open_dimensions import edited
from .test_xbrl_instance import NS
from .xbrl_instance import digest,selected_financials,XBRLError
from .xbrl_dimensions import corroborate,TYPED_BOUND_PROFILE
from .xbrl_typed_dimensions import check_typed_contexts,BOUNDS_PROFILE as SCALAR_PROFILE
from .xbrl_types import BOUNDS_PROFILE as NUMERIC_PROFILE
from .xbrl_typed_bounds import _fingerprint
from .xbrl_collection import FilingCollection


def restricted(parent='<s:minInclusive value="0"/><s:maxExclusive value="10"/>',child='<s:minInclusive value="1"/><s:maxExclusive value="9"/>',text='7',base='s:decimal',**kwargs):
 types='<s:simpleType name="Parent"><s:restriction base="'+base+'">'+parent+'</s:restriction></s:simpleType><s:simpleType name="Child"><s:restriction base="g:Parent">'+child+'</s:restriction></s:simpleType>'
 e=fixture(text,'g:Child',extra_types=types,**kwargs);edited(e,0,e['documents'][0]['raw'].replace(b'<s:schema ',('<s:schema xmlns:g="'+NS+'" ').encode(),1));return e


def derive(e=None,**kwargs):
 e=restricted()if e is None else e;p,g=inputs(e)
 return corroborate(p,g,profile=TYPED_BOUND_PROFILE,documents=e['documents'],instance_uri=e['instance_uri'],**kwargs)


def scalar(out):return proof(out)['facts'][0]['typed_dimensions'][0]['scalar_validation']
def resign(out):
 p=proof(out);p['source_declarations_sha256']=_fingerprint(out['dts_corroboration'],p);rehash(out)


def relink(out):
 """Resign fact IDs too, so semantic rejections cannot rely on stale digests."""
 context=out['contexts']['I'];context['semantic_sha256']=digest({k:context[k]for k in('issuer_cik','period','dimensions','opaque_segment')})
 for fact in out['facts']:
  old=fact['source_fact_id'];fact['context_sha256']=context['semantic_sha256'];fact['source_fact_id']=digest({'source_sha256':out['source']['source_sha256'],'fact':{k:v for k,v in fact.items()if k!='source_fact_id'}})
  for rows in(out['dts_corroboration']['selected_facts'],proof(out)['facts']):
   for row in rows:
    if row['source_fact_id']==old:row['source_fact_id']=fact['source_fact_id']
 for row in proof(out)['facts']:
  for typed in row['typed_dimensions']:
   member=next(d['member']for d in context['dimensions']if d['dimension']==typed['dimension']);typed['member_tree_sha256']=digest(member)
 resign(out)


class TypedBounds(unittest.TestCase):
 def test_opt_in_receipts_and_preserved_originals(self):
  e=restricted(explicit=True,default=True);before=copy.deepcopy(e);p,g=inputs(e);out=derive(e);v=scalar(out)
  self.assertEqual(out['schema'],'gig.sec.xbrl.dimensional_instance.v11');self.assertEqual(proof(out)['profile'],TYPED_BOUND_PROFILE);self.assertFalse(proof(out)['complete_drs_validation'])
  self.assertEqual(v['numeric_profile'],NUMERIC_PROFILE);self.assertEqual(v['declared_type'],'{'+NS+'}Child');self.assertEqual([r['type']for r in v['restrictions']],['{'+NS+'}Child','{'+NS+'}Parent'])
  self.assertEqual(v['effective_bounds'],{'lower':{'value':'1','inclusive':True},'upper':{'value':'9','inclusive':False},'integer_value_space':False})
  self.assertEqual(proof(out)['facts'][0]['used_defaults'],{'{'+NS+'}RegionAxis':'{'+NS+'}South'})
  for key in('facts','contexts','source'):self.assertEqual(out[key],p[key])
  self.assertEqual(e,before);selected_financials(out)
 def test_legacy_typed_v6_hashes_match_original_baseline(self):
  self.assertEqual(legacy(fixture())['canonical_sha256'],'ae634207db19b78376f900d468cb2f48d3990bda32ba1002677e989e8e6461d8')
  self.assertEqual(legacy(restricted(explicit=True,default=True))['canonical_sha256'],'a4f8a805e6616db3e852a48bb0a70da4b353bc07e65037c5ae3a75ca15fa2fb9')
 def test_scalar_v2_diagnostics_are_separate_and_declared_bound(self):
  e=restricted();p,g=inputs(e);before=copy.deepcopy(p);v=check_typed_contexts(p,g,e['documents'],profile=SCALAR_PROFILE)
  self.assertEqual(v['schema'],'gig.sec.xbrl.typed_context_diagnostics.v2');self.assertEqual(v['profile'],SCALAR_PROFILE);self.assertEqual(v['contexts'][0]['typed_members'][0]['scalar_validation']['numeric_profile'],NUMERIC_PROFILE);self.assertEqual(p,before)
 def test_v6_identity_and_old_inherited_definition_semantics_preserved(self):
  e=restricted(child='<s:maxExclusive value="20"/>');out=legacy(e)
  self.assertEqual(out['schema'],'gig.sec.xbrl.dimensional_instance.v6');self.assertNotIn('restrictions',scalar(out));self.assertEqual(scalar(out)['numeric_profile'],'NUMERIC_RESTRICTION_CONSTRAINTS_V5')
  with self.assertRaisesRegex(XBRLError,'outside_base_value_space'):derive(e)
 def test_all_four_bounds_reject_widened_parent_range(self):
  cases=[('<s:minInclusive value="2"/>','<s:minInclusive value="1"/>'),('<s:minExclusive value="2"/>','<s:minExclusive value="1"/>'),('<s:maxInclusive value="8"/>','<s:maxInclusive value="9"/>'),('<s:maxExclusive value="8"/>','<s:maxExclusive value="9"/>')]
  for parent,child in cases:
   with self.subTest(child=child),self.assertRaisesRegex(XBRLError,'outside_base_value_space'):derive(restricted(parent,child))
 def test_exclusive_repetition_and_inclusive_endpoint_rules(self):
  for kind in('min','max'):
   parent='<s:'+kind+'Exclusive value="7"/>';text='8'if kind=='min'else'6'
   selected_financials(derive(restricted(parent,parent,text)))
   with self.assertRaisesRegex(XBRLError,'outside_base_value_space'):derive(restricted(parent,'<s:'+kind+'Inclusive value="7"/>',text))
 def test_newer_parent_boundary_cannot_be_bypassed(self):
  e=restricted('<s:maxExclusive value="10"/>','<s:maxExclusive value="8"/>')
  third='<s:simpleType name="Third"><s:restriction base="g:Child"><s:maxExclusive value="10"/></s:restriction></s:simpleType>'
  edited(e,0,e['documents'][0]['raw'].replace(b'type="g:Child"',b'type="g:Third"').replace(b'</s:schema>',third.encode()+b'</s:schema>'))
  with self.assertRaisesRegex(XBRLError,'outside_base_value_space'):derive(e)
 def test_numeric_endpoints_obey_parent_enumerations_and_digits(self):
  for parent,child,text in(('<s:enumeration value="2"/><s:enumeration value="4"/><s:enumeration value="8"/>','<s:minInclusive value="3"/>','4'),('<s:totalDigits value="1"/>','<s:maxInclusive value="10"/>','7'),('<s:fractionDigits value="1"/>','<s:minInclusive value="0.12"/>','7')):
   with self.subTest(parent=parent),self.assertRaisesRegex(XBRLError,'outside_base_value_space'):derive(restricted(parent,child,text))
 def test_integer_builtin_ranges_and_empty_supported_domains(self):
  self.assertTrue(scalar(derive(restricted('', '<s:maxInclusive value="10"/>','7',base='s:unsignedByte')))['effective_bounds']['integer_value_space'])
  for parent,child,base in(('', '<s:maxInclusive value="256"/>','s:unsignedByte'),('<s:minExclusive value="0"/>','<s:maxExclusive value="1"/>','s:integer'),('<s:minInclusive value="8"/>','<s:maxExclusive value="8"/>','s:decimal')):
   with self.subTest(child=child),self.assertRaises(XBRLError):derive(restricted(parent,child,base=base))
 def test_string_boolean_and_numeric_text_remain_original_without_equality(self):
  for text,kind in(('  desk  A  ','s:string'),(' true ','s:boolean'),('  +007  ','s:integer')):
   out=derive(fixture(text,kind));self.assertEqual(out['contexts']['I']['dimensions'][0]['member']['text'],text);selected_financials(out)
  a=derive(fixture('+007','s:integer'));b=derive(fixture('7','s:integer'));self.assertNotEqual(proof(a)['facts'][0]['typed_dimensions'][0]['member_tree_sha256'],proof(b)['facts'][0]['typed_dimensions'][0]['member_tree_sha256'])
 def test_original_source_graph_and_metadata_mismatch_fail(self):
  e=restricted();p,g=inputs(e);p['dts_corroboration']['type_declarations']['{'+NS+'}Child']['declaration']['facets'][0]['value']='2';rehash(p)
  with self.assertRaisesRegex(XBRLError,'retained_graph_mismatch'):corroborate(p,g,profile=TYPED_BOUND_PROFILE,documents=e['documents'],instance_uri=e['instance_uri'])
  p,g=inputs(e);g['type_declarations']['{'+NS+'}Child']['declaration']['facets'][0]['value']='2';p['dts_corroboration']['type_declarations']=copy.deepcopy(g['type_declarations']);rehash(g);p['dts_corroboration']['dts_sha256']=g['canonical_sha256'];rehash(p)
  with self.assertRaisesRegex(XBRLError,'source_binding|reconstructed_graph_mismatch'):corroborate(p,g,profile=TYPED_BOUND_PROFILE,documents=e['documents'],instance_uri=e['instance_uri'])
 def test_normalized_source_metadata_rejects_resigned_unsafe_facets(self):
  for kind,value,extra in(('minInclusive','1',{'fixed':False}),('fractionDigits','0',{'fixed':1}),('whiteSpace','preserve',{}),('minInclusive','NaN',{})):
   out=derive();entry=out['dts_corroboration']['type_declarations']['{'+NS+'}Child'];entry['declaration']['facets']=[{'kind':kind,'value':value,**extra}];resign(out)
   with self.subTest(kind=kind,extra=extra),self.assertRaisesRegex(XBRLError,'dimensional_result_contract'):selected_financials(out)
 def test_resigned_scalar_proof_fields_are_rederived(self):
  for field,value in(('declared_type','{'+NS+'}Parent'),('resolved_type','{http://www.w3.org/2001/XMLSchema}integer'),('numeric_profile','NUMERIC_RESTRICTION_CONSTRAINTS_V5'),('restriction_types',[]),('restrictions',[]),('effective_bounds',{'lower':None,'upper':None,'integer_value_space':False}),('validation','STRING_LEXICAL_RETAINED')):
   out=derive();scalar(out)[field]=value;resign(out)
   with self.subTest(field=field),self.assertRaisesRegex(XBRLError,'dimensional_result_contract'):selected_financials(out)
 def test_consumer_rederives_values_after_all_context_fact_and_proof_hashes_change(self):
  for text in('9','0','7.123456789012345678901234567890123456789012345678901234567890123456789'):
   out=derive();out['contexts']['I']['dimensions'][0]['member']['text']=text;relink(out)
   with self.subTest(text=text),self.assertRaisesRegex(XBRLError,'dimensional_result_contract'):selected_financials(out)
 def test_resigned_domain_declaration_source_and_type_receipts_join(self):
  for change in('domain_name','domain_type','domain_id','domain_hash','domain_source','declaration','namespace','type_kind','type_hash','type_node','type_ordinal_budget','domain_ordinal_budget','type_omitted','reserved_namespace'):
   out=derive();v=proof(out);domain=v['domain_sources'][0];r=v['type_sources'][0]
   if change=='domain_name':domain['domain']['concept']='{'+NS+'}North'
   elif change=='domain_type':domain['domain']['type']='{http://www.w3.org/2001/XMLSchema}integer'
   elif change=='domain_id':domain['domain']['schema_id']='another'
   elif change=='domain_hash':domain['source_sha256']='0'*64
   elif change=='domain_source':domain['domain']['schema_uri']=out['dts_corroboration']['documents'][1]['uri']
   elif change=='declaration':domain['declaration']['nillable']=True
   elif change=='namespace':v['schema_sources'][0]['target_namespace']='urn:wrong'
   elif change=='reserved_namespace':v['schema_sources'][0]['target_namespace']='http://www.w3.org/2001/XMLSchema'
   elif change=='type_kind':r['kind']='{http://www.w3.org/2001/XMLSchema}complexType'
   elif change=='type_hash':r['source_sha256']='0'*64
   elif change=='type_node':r['node_ordinal']=domain['node_ordinal']
   elif change=='type_ordinal_budget':r['node_ordinal']=30001
   elif change=='domain_ordinal_budget':domain['node_ordinal']=30001
   elif change=='type_omitted':v['type_sources'].pop()
   resign(out)
   with self.subTest(change=change),self.assertRaisesRegex(XBRLError,'dimensional_result_contract'):selected_financials(out)
 def test_resigned_numeric_widening_definition_and_source_lists_fail(self):
  for change in('widening','source_duplicate','builtin_redefinition','context_order','namespaces','declaration_type'):
   out=derive();types=out['dts_corroboration']['type_declarations'];entry=types['{'+NS+'}Child']
   if change=='widening':entry['declaration']['facets'][1]['value']='20'
   elif change=='source_duplicate':entry['source_documents']*=2
   elif change=='builtin_redefinition':types['{http://www.w3.org/2001/XMLSchema}integer']=copy.deepcopy(entry)
   elif change=='context_order':out['contexts']['I']['dimensions'][0]['member']['content_order']=['invented']
   elif change=='namespaces':out['contexts']['I']['dimensions'][0]['member']['namespaces']['invented']=False
   elif change=='declaration_type':out['dts_corroboration']['concept_declarations']['{'+NS+'}Code']['declaration']['type']='{http://www.w3.org/2001/XMLSchema}integer'
   relink(out)
   with self.subTest(change=change),self.assertRaisesRegex(XBRLError,'dimensional_result_contract'):selected_financials(out)
 def test_resigned_definition_shapes_and_defaults_are_rechecked(self):
  for change in('open','negative','primary','extra_axis','duplicate','source','usable','closure','missing_facts','extra_proof'):
   out=derive(restricted(explicit=True,default=True));v=proof(out);net=v['definition'][0];a=next(a for a in net['arcs']if a['kind']=='all')
   if change=='open':a['closed']=False
   elif change=='negative':a['kind']='notAll'
   elif change=='primary':a['from']='{'+NS+'}Domain'
   elif change=='extra_axis':v['facts'][0]['used_defaults']['{'+NS+'}Other']='{'+NS+'}South'
   elif change=='duplicate':net['arcs'].append(copy.deepcopy(a))
   elif change=='source':a['source_uri']=out['dts_corroboration']['documents'][0]['uri']
   elif change=='usable':net['usable_for_restricted_profile']=1
   elif change=='closure':out['dts_corroboration']['structural_closure']=1
   elif change=='missing_facts':v['facts']=[]
   elif change=='extra_proof':v['typed_equality']=True
   resign(out)
   with self.subTest(change=change),self.assertRaisesRegex(XBRLError,'dimensional_result_contract'):selected_financials(out)
 def test_producer_unsupported_cube_semantics_remain_closed(self):
  for old,new in((b'closed="true"',b'closed="false"'),(b'arcrole="http://xbrl.org/int/dim/arcrole/all"',b'arcrole="http://xbrl.org/int/dim/arcrole/notAll"'),(b'xl:to="desk"',b'xl:to="desk" xd:targetRole="urn:other"'),(b'xl:to="desk"',b'xl:to="desk" priority="1"')):
   e=restricted();edited(e,1,e['documents'][1]['raw'].replace(old,new))
   with self.subTest(new=new),self.assertRaises(XBRLError):derive(e)
  for text,kind,kwargs in(('<g:Code>7</g:Code>','s:integer',{}),('7','s:integer',{'member_attrs':'xsi:nil="true"'}),('A','s:QName',{})):
   with self.subTest(text=text),self.assertRaisesRegex(XBRLError,'scalar_semantics_unsupported'):derive(fixture(text,kind,**kwargs))
 def test_producer_observed_permission_checks_precede_every_xml_read(self):
  e=restricted();p,g=inputs(e);p['origin']=g['origin']=p['source']['origin']='OBSERVED_OFFICIAL_RESPONSE';rehash(g);p['dts_corroboration']['dts_sha256']=g['canonical_sha256'];rehash(p)
  with patch('terminal.stocks.xbrl_typed_dimensions.parse_xml',side_effect=AssertionError('UNAPPROVED_XML')),patch('terminal.stocks.xbrl_dts.parse_xml',side_effect=AssertionError('UNAPPROVED_XML')),patch('terminal.stocks.xbrl_effective_cross_role.parse_xml',side_effect=AssertionError('UNAPPROVED_XML')):
   for kwargs,error in(({},'not_approved'),({'allow_observed':True},'permission_binding')):
    with self.subTest(kwargs=kwargs),self.assertRaisesRegex(XBRLError,error):corroborate(p,g,profile=TYPED_BOUND_PROFILE,documents=e['documents'],instance_uri=e['instance_uri'],**kwargs)
 def test_no_network_collection_consumers_and_atomic_failure(self):
  c=FilingCollection('0000320193');e=restricted();before=copy.deepcopy(e)
  with patch('socket.socket.connect',side_effect=AssertionError('NO_NETWORK')):c.ingest_dts_batch([e],dimensional_profile=TYPED_BOUND_PROFILE)
  result=c.at_acceptance_time('2024-02-02T00:00:00Z');self.assertFalse(result['history']['assets']);self.assertEqual(e,before);self.assertEqual(result['selected_input_coverage'][0]['xbrl_coverage']['dts_corroboration']['dimensional_validation']['profile'],TYPED_BOUND_PROFILE)
  state=c.page();bad=restricted(child='<s:maxExclusive value="20"/>');bad['manifest']['accession']='0000000123-24-000002'
  with self.assertRaisesRegex(XBRLError,'outside_base_value_space'):c.ingest_dts_batch([e,bad],dimensional_profile=TYPED_BOUND_PROFILE)
  self.assertEqual(c.page(),state)
 def test_plain_collection_revalidates_resigned_receipts_on_read(self):
  c=FilingCollection('0000320193');c.ingest_dts_batch([restricted()],dimensional_profile=TYPED_BOUND_PROFILE)
  value=next(iter(c._filings.values()));scalar(value)['restrictions']=[];resign(value)
  with self.assertRaisesRegex(XBRLError,'dimensional_result_contract'):c.at_acceptance_time('2024-02-02T00:00:00Z')
 def test_optional_fact_numeric_v6_profile_composes(self):
  c=FilingCollection('0000320193');c.ingest_dts_batch([restricted()],numeric_profile=NUMERIC_PROFILE,dimensional_profile=TYPED_BOUND_PROFILE);self.assertFalse(c.at_acceptance_time('2024-02-02T00:00:00Z')['history']['assets'])
 def test_inline_document_set_and_collection_keep_actual_originals(self):
  from .test_inline_set import html,doc
  e=restricted(explicit=True,default=True);raw=e['raw'].decode();resources=raw[raw.index('<x:context'):raw.index('<g:Assets')];page=html('',resources=True).decode();start=page.index('<x:context');end=page.index('</ix:resources>');page=(page[:start]+resources+page[end:]).replace('<html ','<html xmlns:d="http://xbrl.org/2006/xbrldi" ',1)
  batch={'documents':[doc('resources.xhtml',page.encode()),doc('facts.xhtml',html('<ix:nonFraction name="g:Assets" contextRef="I" unitRef="USD">1000</ix:nonFraction>'))],'concepts':e['concepts'],'taxonomy_documents':e['documents']};before=copy.deepcopy(batch);c=FilingCollection('0000320193')
  with patch('socket.socket.connect',side_effect=AssertionError('NO_NETWORK')):c.ingest_inline_set_batch([batch],dimensional_profile=TYPED_BOUND_PROFILE)
  out=next(iter(c._filings.values()));self.assertEqual(out['schema'],'gig.sec.xbrl.dimensional_inline_set.v11');self.assertEqual(batch,before);selected_financials(out)
  result=c.at_acceptance_time('2024-02-02T00:00:00Z');self.assertFalse(result['history']['assets']);self.assertEqual(len(result['selected_input_coverage'][0]['xbrl_coverage']['document_set']['documents']),2)
  for field,tampered in (('extracted_text','2000'),('transformed_lexical','2000'),('scale','1'),('segments',[])):
   forgery=copy.deepcopy(out);forgery['document_set']['facts'][0][field]=tampered;rehash(forgery)
   with self.subTest(field=field),self.assertRaisesRegex(XBRLError,'dimensional_result_contract'):selected_financials(forgery)
  from .service import StockWorkspace
  workspace=StockWorkspace(environment={})
  self.assertFalse(workspace.admit_xbrl_collection('AAPL',c)['provider_requested'])
  corrupted=copy.deepcopy(c);changed=next(iter(corrupted._filings.values()))
  changed['document_set']['facts'][0]['scale']='1';rehash(changed)
  with self.assertRaisesRegex(XBRLError,'dimensional_result_contract'):workspace.admit_xbrl_collection('AAPL',corrupted)
  state=c.page();bad=copy.deepcopy(batch);bad['taxonomy_documents'][0]['sha256']='0'*64
  with self.assertRaisesRegex(XBRLError,'document_digest'):c.ingest_inline_set_batch([batch,bad],dimensional_profile=TYPED_BOUND_PROFILE)
  self.assertEqual(c.page(),state)
 def test_resource_bounds_and_original_document_coverage(self):
  e=restricted();p,g=inputs(e)
  for docs,error in((e['documents'][:1],'reconstructed_graph_mismatch'),(e['documents'][1:],'original_schema_required'),(e['documents']*2,'duplicate_source_uri')):
   with self.subTest(error=error),self.assertRaisesRegex(XBRLError,error):corroborate(p,g,profile=TYPED_BOUND_PROFILE,documents=docs,instance_uri=e['instance_uri'])
  for field,value in(('type_sources',[]),('domain_sources',[]),('schema_sources',[])):
   out=derive();proof(out)[field]=value;resign(out)
   with self.subTest(field=field),self.assertRaisesRegex(XBRLError,'dimensional_result_contract'):selected_financials(out)

if __name__=='__main__':unittest.main(verbosity=2)
