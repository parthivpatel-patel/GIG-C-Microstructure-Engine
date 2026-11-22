"""Original-byte authored V10 mixed all/notAll cross-role/effective DRS fixtures."""
import copy,hashlib,re,unittest
from unittest.mock import patch
from .test_xbrl_inherited_cross_role import fixture as positive,proof,rehash
from .test_xbrl_cross_role import edited,inputs,ROLES,BASE,NS
from .test_xbrl_dimensions import arc,D
from .test_xbrl_effective_cross_role import add_link
from .xbrl_dimensions import corroborate,MIXED_CROSS_ROLE_PROFILE,EFFECTIVE_CROSS_ROLE_PROFILE
from .xbrl_instance import selected_financials,XBRLError,canonical
from .xbrl_collection import FilingCollection


def source_edit(e,raw):e['raw']=raw;e['manifest']['source_sha256']=hashlib.sha256(raw).hexdigest();return e


def fixture(*,negative_root='south',negative_axis=False,negative_count=1,negative_inherited=True,**kwargs):
 e=positive(**kwargs);decls='';locs='';assign='';axes='';domains=''
 for i in range(negative_count):
  cube='excludedcube'+str(i);decls+='<s:element id="'+cube+'" name="ExcludedCube'+str(i)+'" substitutionGroup="xd:hypercubeItem" abstract="true" x:periodType="duration"/>';locs+='<l:loc xl:type="locator" xl:label="'+cube+'" xl:href="authored.xsd#'+cube+'"/>'
  source='parent1'if negative_inherited and kwargs.get('inherited',True)else'assets';assign+=arc('notAll',source,cube,'xd:closed="true" xd:contextElement="segment" xd:targetRole="'+ROLES[1]+'"');axes+=arc('hypercube-dimension',cube,'excludedaxis'if negative_axis else'axis','xd:targetRole="'+ROLES[5]+'"')
 if negative_axis:
  decls+='<s:element id="excludedaxis" name="ExcludedAxis" substitutionGroup="xd:dimensionItem" abstract="true" x:periodType="duration"/>';locs+='<l:loc xl:type="locator" xl:label="excludedaxis" xl:href="authored.xsd#excludedaxis"/>'
 domains=arc('dimension-domain','excludedaxis'if negative_axis else'axis',negative_root)
 edited(e,0,e['documents'][0]['raw'].replace(b'</s:schema>',decls.encode()+b'</s:schema>'))
 raw=e['documents'][1]['raw'];raw=re.sub(b'(<l:definitionLink[^>]*>)',lambda m:m.group(0)+locs.encode(),raw)
 needle=arc('all','parent1'if kwargs.get('inherited',True)else'assets','cube','xd:closed="true" xd:contextElement="segment" xd:targetRole="'+ROLES[1]+'"').encode();assert needle in raw;raw=raw.replace(needle,needle+assign.encode())
 needle=arc('hypercube-dimension','cube','axis','xd:targetRole="'+ROLES[2]+'"').encode();assert needle in raw;raw=raw.replace(needle,needle+axes.encode());edited(e,1,raw)
 # Default-role links already exist only when default=True. Use a separate link
 # so the authored locator pair never duplicates an existing XLink arc.
 add_link(e,domains.encode(),role=ROLES[5])
 return e


def derive(e=None,**kwargs):
 e=fixture()if e is None else e;p,g=inputs(e,observed=e['manifest']['origin']=='OBSERVED_OFFICIAL_RESPONSE')
 return corroborate(p,g,profile=MIXED_CROSS_ROLE_PROFILE,documents=e['documents'],instance_uri=e['instance_uri'],**kwargs)


def replace_negative(e,old,new):
 raw=e['documents'][1]['raw'];assert old in raw;edited(e,1,raw.replace(old,new));return e


class MixedCrossRole(unittest.TestCase):
 def test_mixed_inherited_cube_operations_preserve_actual_sources(self):
  e=fixture();before=copy.deepcopy(e);p,g=inputs(e);out=derive(e);v=proof(out);r=v['facts'][0]
  self.assertEqual(out['schema'],'gig.sec.xbrl.dimensional_instance.v10');self.assertEqual(v['profile'],MIXED_CROSS_ROLE_PROFILE);self.assertFalse(v['complete_drs_validation']);self.assertEqual(r['status'],'VALIDATED_RESTRICTED_MIXED_CROSS_ROLE_CONTEXT');self.assertEqual(len(r['assignments']),3);self.assertEqual(r['role'],ROLES[0]);self.assertEqual(r['global_defaults'],{});self.assertEqual(e,before)
  negative=next(a for a in r['assignments']if a['kind']=='notAll');self.assertFalse(negative['hypercube_valid']);self.assertEqual(negative['failure_reason'],'drs_mixed_cross_member_outside_domain');self.assertTrue(negative['inherited']);self.assertEqual(negative['used_defaults'],{})
  for k in('source','facts','contexts','units'):self.assertEqual(out[k],p[k])
  self.assertFalse(selected_financials(out)['history']['assets'])
 def test_direct_negative_and_inherited_positive_conjoin(self):
  out=derive(fixture(negative_inherited=False));self.assertFalse(next(a for a in proof(out)['facts'][0]['assignments']if a['kind']=='notAll')['inherited']);selected_financials(out)
 def test_valid_negative_cube_rejects_entire_conjunction(self):
  with self.assertRaisesRegex(XBRLError,'negative_hypercube_satisfied'):derive(fixture(negative_root='north'))
 def test_each_negative_must_be_false_not_only_one(self):
  e=fixture(negative_count=2);a=arc('hypercube-dimension','excludedcube1','axis','xd:targetRole="'+ROLES[5]+'"').encode();b=arc('hypercube-dimension','excludedcube1','axis','xd:targetRole="'+ROLES[2]+'"').encode();replace_negative(e,a,b)
  with self.assertRaisesRegex(XBRLError,'negative_hypercube_satisfied'):derive(e)
 def test_negative_closed_extra_dimension_is_exact_false_witness(self):
  out=derive(fixture(negative_axis=True));a=next(a for a in proof(out)['facts'][0]['assignments']if a['kind']=='notAll');self.assertEqual(a['failure_reason'],'drs_mixed_cross_closed_extra_dimension');self.assertEqual(a['extra_dimensions'],['{'+NS+'}RegionAxis']);self.assertEqual(a['used_defaults'],{});selected_financials(out)
 def test_negative_missing_dimension_is_false_after_positive_default_validation(self):
  out=derive(fixture(member=None,default=True,negative_axis=True));r=proof(out)['facts'][0];a=next(a for a in r['assignments']if a['kind']=='notAll');self.assertEqual(a['failure_reason'],'drs_mixed_cross_required_dimension_missing');self.assertEqual(a['used_defaults'],{});self.assertEqual(r['used_defaults'],{'{'+NS+'}RegionAxis':'{'+NS+'}South'});self.assertEqual(out['contexts']['I']['dimensions'],[]);self.assertFalse(selected_financials(out)['history']['assets'])
 def test_positive_failure_is_not_replaced_with_negative_success(self):
  e=fixture(member='Outside');decl=b'<s:element id="outside" name="Outside" substitutionGroup="x:item" type="x:stringItemType" x:periodType="duration"/>';edited(e,0,e['documents'][0]['raw'].replace(b'</s:schema>',decl+b'</s:schema>'))
  with self.assertRaisesRegex(XBRLError,'member_outside_domain'):derive(e)
  with self.assertRaisesRegex(XBRLError,'required_dimension_missing'):derive(fixture(member=None))
 def test_explicit_default_is_global_error_before_negative_witness(self):
  with self.assertRaisesRegex(XBRLError,'explicit_default_member'):derive(fixture(member='South',default=True,negative_axis=True))
 def test_unreported_global_defaults_not_used_by_positive_cube_remain_visible(self):
  e=fixture(negative_axis=True);add_link(e,arc('dimension-default','excludedaxis','south').encode(),role=ROLES[5]);out=derive(e);r=proof(out)['facts'][0];self.assertEqual(r['global_defaults'],{'{'+NS+'}ExcludedAxis':'{'+NS+'}South'});self.assertEqual(r['used_defaults'],r['global_defaults']);self.assertTrue(all(not a['used_defaults']for a in r['assignments']));self.assertFalse(selected_financials(out)['history']['assets'])
 def test_negative_target_role_replaces_instead_of_unions_domain(self):
  e=fixture();a=arc('hypercube-dimension','excludedcube0','axis','xd:targetRole="'+ROLES[5]+'"').encode();replace_negative(e,a,arc('hypercube-dimension','excludedcube0','axis','xd:targetRole="'+ROLES[2]+'"').encode())
  with self.assertRaisesRegex(XBRLError,'negative_hypercube_satisfied'):derive(e)
 def test_same_cube_different_target_role_does_not_reuse_other_shape(self):
  e=fixture();old=arc('notAll','parent1','excludedcube0','xd:closed="true" xd:contextElement="segment" xd:targetRole="'+ROLES[1]+'"').encode();replace_negative(e,old,b'');add_link(e,arc('notAll','parent1','cube','xd:closed="true" xd:contextElement="segment" xd:targetRole="'+ROLES[5]+'"').encode(),role=ROLES[0]);add_link(e,arc('hypercube-dimension','cube','axis','xd:targetRole="'+ROLES[5]+'"').encode(),role=ROLES[5]);out=derive(e);selected_financials(out);self.assertEqual(next(a for a in proof(out)['facts'][0]['assignments']if a['kind']=='notAll')['hypercube'],'{'+NS+'}Cube')
 def test_prohibited_negative_does_not_participate_but_retains_source(self):
  e=fixture(negative_root='north');a=arc('notAll','parent1','excludedcube0','xd:closed="true" xd:contextElement="segment" xd:targetRole="'+ROLES[1]+'" priority="1" use="prohibited"').encode();add_link(e,a,role=ROLES[0]);out=derive(e);v=proof(out);self.assertTrue(any(a['kind']=='notAll'for a in v['relationships']));self.assertFalse(any(a['kind']=='notAll'for a in v['effective_relationships']));self.assertTrue(any(g['status']=='PROHIBITED_AT_MAX_PRIORITY'for g in v['resolution']));selected_financials(out)
 def test_higher_optional_restores_negative_after_prohibition(self):
  e=fixture(negative_root='north');attrs='xd:closed="true" xd:contextElement="segment" xd:targetRole="'+ROLES[1]+'"';add_link(e,arc('notAll','parent1','excludedcube0',attrs+' priority="1" use="prohibited"').encode(),role=ROLES[0]);add_link(e,arc('notAll','parent1','excludedcube0',attrs+' priority="2"').encode(),role=ROLES[0])
  with self.assertRaisesRegex(XBRLError,'negative_hypercube_satisfied'):derive(e)
 def test_notall_cannot_prohibit_all_equivalence_group(self):
  e=positive();add_link(e,arc('notAll','parent1','cube','xd:closed="true" xd:contextElement="segment" xd:targetRole="'+ROLES[1]+'" use="prohibited" priority="9"').encode(),role=ROLES[0]);out=derive(e);self.assertTrue(any(a['kind']=='all'for a in proof(out)['effective_relationships']));selected_financials(out)
 def test_alternative_bases_and_negative_only_are_explicitly_unsupported(self):
  e=fixture();old=arc('notAll','parent1','excludedcube0','xd:closed="true" xd:contextElement="segment" xd:targetRole="'+ROLES[1]+'"').encode();replace_negative(e,old,b'');add_link(e,old,role=ROLES[5])
  with self.assertRaisesRegex(XBRLError,'alternative_base_roles'):derive(e)
  e=fixture();raw=e['documents'][1]['raw'];raw=re.sub(b'<l:definitionArc[^>]*arcrole="[^"]*/all"[^>]*/>',b'',raw);edited(e,1,raw)
  with self.assertRaisesRegex(XBRLError,'positive_assignment_required'):derive(e)
 def test_open_typed_opaque_and_mixed_container_are_not_negative_witnesses(self):
  for change in('open','typed','opaque','container'):
   e=fixture(negative_axis=True)
   if change=='open':edited(e,1,e['documents'][1]['raw'].replace(b'xd:closed="true"',b'xd:closed="false"'))
   elif change=='typed':edited(e,0,e['documents'][0]['raw'].replace(b'name="ExcludedAxis"',b'name="ExcludedAxis" xd:typedDomainRef="#south"'))
   elif change=='opaque':source_edit(e,e['raw'].replace(b'</x:segment>',b'<g:Opaque>A</g:Opaque></x:segment>'))
   else:
    old=arc('notAll','parent1','excludedcube0','xd:closed="true" xd:contextElement="segment" xd:targetRole="'+ROLES[1]+'"').encode();replace_negative(e,old,old.replace(b'contextElement="segment"',b'contextElement="scenario"'))
   with self.subTest(change=change),self.assertRaises(XBRLError):derive(e)
 def test_unsupported_negative_shape_and_cycles_reject_before_context_failure(self):
  for change in('missing','cycle'):
   e=fixture(negative_axis=True);a=arc('dimension-domain','excludedaxis','south').encode()
   if change=='missing':replace_negative(e,a,b'')
   else:replace_negative(e,a,a+arc('domain-member','south','south').encode())
   with self.subTest(change=change),self.assertRaises(XBRLError):derive(e)
 def test_primary_inheritance_cycle_and_cross_base_are_not_negated(self):
  for change in('cycle','role'):
   e=fixture();a=arc('domain-member','parent0','assets').encode();replace_negative(e,a,a+arc('domain-member','assets','parent1').encode()if change=='cycle'else a.replace(b'/>',('xd:targetRole="'+ROLES[1]+'"/>').encode()))
   with self.subTest(change=change),self.assertRaisesRegex(XBRLError,'primary_'):derive(e)
 def test_default_outside_selected_domain_is_explicit_unsupported_shape(self):
  with self.assertRaisesRegex(XBRLError,'default_outside_selected_domain'):derive(fixture(default=True,negative_root='north'))
 def test_resource_budgets_are_never_negated(self):
  e=fixture()
  for limit,reason in(('MAX_DOMAIN_STATES','domain_state_budget'),('MAX_PRIMARY_STATES','primary_state_budget'),('MAX_ASSIGNMENTS','assignment_budget'),('MAX_FACT_ASSIGNMENTS','assignment_budget'),('MAX_OUTPUT','output_budget')):
   with self.subTest(limit=limit),patch('terminal.stocks.xbrl_mixed_cross_role.'+limit,1),self.assertRaisesRegex(XBRLError,reason):derive(e)
 def test_retained_negative_outcomes_and_sources_reject_resigned_forgeries(self):
  for change in('operation','valid','reason','defaults','global','role','effective','resolution','source','namespace','context','label'):
   out=derive();v=proof(out);r=v['facts'][0];a=next(a for a in r['assignments']if a['kind']=='notAll')
   if change=='operation':a['kind']='all'
   elif change=='valid':a['hypercube_valid']=True
   elif change=='reason':a['failure_reason']='guessed'
   elif change=='defaults':a['used_defaults']={'{'+NS+'}RegionAxis':'{'+NS+'}South'}
   elif change=='global':r['global_defaults']={'{'+NS+'}RegionAxis':'{'+NS+'}South'}
   elif change=='role':v['role_references']=[]
   elif change=='effective':v['effective_relationships'].pop()
   elif change=='resolution':v['resolution'][0]['max_priority']=2
   elif change=='source':v['relationships'][0]['source_sha256']='0'*64
   elif change=='namespace':v['schema_sources'][0]['target_namespace']=D
   elif change=='context':out['contexts']['I']['semantic_sha256']='0'*64
   else:v['relationships'][0]['from_label']='not legal'
   rehash(out)
   with self.subTest(change=change),self.assertRaisesRegex(XBRLError,'dimensional_result_contract'):selected_financials(out)
 def test_source_hash_missing_duplicate_and_issuer_boundaries_remain_strict(self):
  for change in('hash','missing','duplicate'):
   e=fixture()
   if change=='hash':e['documents'][1]['raw']+=b' '
   elif change=='missing':e['documents'].pop()
   else:e['documents'].append(copy.deepcopy(e['documents'][0]))
   with self.subTest(change=change),self.assertRaises(XBRLError):derive(e)
 def test_prior_v9_does_not_silently_accept_negative_scope(self):
  e=fixture();p,g=inputs(e)
  with self.assertRaisesRegex(XBRLError,'unsupported'):corroborate(p,g,profile=EFFECTIVE_CROSS_ROLE_PROFILE,documents=e['documents'],instance_uri=e['instance_uri'])
 def test_new_profile_requires_versioned_derived_schema(self):
  out=derive();out['schema']='gig.sec.xbrl.dimensional_instance.v9';rehash(out)
  with self.assertRaisesRegex(XBRLError,'dimensional_result_contract'):selected_financials(out)
 def test_collection_original_path_and_failed_batch_are_atomic(self):
  e=fixture();before=copy.deepcopy(e);c=FilingCollection('0000320193');c.ingest_dts_batch([e],dimensional_profile=MIXED_CROSS_ROLE_PROFILE);out=next(iter(c._filings.values()));self.assertEqual(out['schema'],'gig.sec.xbrl.dimensional_instance.v10');self.assertEqual(e,before);self.assertFalse(c.at_acceptance_time('2024-02-02T00:00:00Z')['history']['assets']);prior=c.page()
  with self.assertRaises(XBRLError):c.ingest_dts_batch([fixture(negative_root='north')],dimensional_profile=MIXED_CROSS_ROLE_PROFILE)
  self.assertEqual(c.page(),prior)
 def test_inline_collection_uses_original_multidocument_sources(self):
  from .test_inline_set import html,doc
  e=fixture();raw=e['raw'].decode();resources=raw[raw.index('<x:context'):raw.index('<g:Assets')];page=html('',resources=True).decode();start=page.index('<x:context');end=page.index('</ix:resources>');page=(page[:start]+resources+page[end:]).replace('<html ','<html xmlns:d="http://xbrl.org/2006/xbrldi" ',1);originals=[doc('resources.xhtml',page.encode()),doc('facts.xhtml',html('<ix:nonFraction name="g:Assets" contextRef="I" unitRef="USD">1000</ix:nonFraction>'))];before=copy.deepcopy(originals);c=FilingCollection('0000320193');c.ingest_inline_set_batch([{'documents':originals,'concepts':e['concepts'],'taxonomy_documents':e['documents']}],dimensional_profile=MIXED_CROSS_ROLE_PROFILE);out=next(iter(c._filings.values()));self.assertEqual(out['schema'],'gig.sec.xbrl.dimensional_inline_set.v10');self.assertEqual(originals,before);self.assertTrue(any(a['kind']=='notAll'for a in proof(out)['facts'][0]['assignments']));self.assertFalse(selected_financials(out)['history']['assets'])
 def test_observed_permission_precedes_original_xml_processing(self):
  e=fixture(origin='OBSERVED_OFFICIAL_RESPONSE',permission_reference='authored-grant');base='https://www.sec.gov/Archives/edgar/data/320193/000000012324000001/';e['instance_uri']=e['manifest']['source_url']=base+'instance.xml'
  for d in e['documents']:d['uri']=d['uri'].replace(BASE,base)
  with patch('terminal.stocks.xbrl_cross_role.parse_xml',side_effect=AssertionError('NO_XML'))as parser:
   with self.assertRaisesRegex(XBRLError,'not_approved'):derive(e)
   parser.assert_not_called()
  selected_financials(derive(e,allow_observed=True))
 def test_sixteen_applicable_assignments_and_sixtyfour_network_assignments_are_bounded(self):
  out=derive(fixture(cubes=1,negative_count=15));self.assertEqual(len(proof(out)['facts'][0]['assignments']),16)
  with self.assertRaisesRegex(XBRLError,'fact_assignment_budget'):derive(fixture(cubes=1,negative_count=16))
  with self.assertRaisesRegex(XBRLError,'closed_assignment_budget'):derive(fixture(negative_count=63))
 def test_undeclared_reported_axis_or_member_cannot_supply_negative_witness(self):
  for before,after in((b'dimension="g:RegionAxis"',b'dimension="g:UnknownAxis"'),(b'>g:North</d:explicitMember>',b'>g:UnknownMember</d:explicitMember>')):
   e=fixture();source_edit(e,e['raw'].replace(before,after))
   with self.subTest(after=after),self.assertRaisesRegex(XBRLError,'declaration_unsupported'):derive(e)
 def test_typed_instance_payload_and_wrong_container_fail_globally(self):
  e=fixture();source_edit(e,e['raw'].replace(b'<d:explicitMember dimension="g:RegionAxis">g:North</d:explicitMember>',b'<d:typedMember dimension="g:RegionAxis"><g:Code>A</g:Code></d:typedMember>'))
  with self.assertRaisesRegex(XBRLError,'context_unsupported'):derive(e)
  e=fixture();source_edit(e,e['raw'].replace(b'<x:segment>',b'<x:scenario>').replace(b'</x:segment>',b'</x:scenario>'))
  with self.assertRaises(XBRLError):derive(e)
 def test_negative_primary_polymorphism_is_not_context_falsehood(self):
  e=fixture();needle=arc('dimension-domain','axis','south').encode();replace_negative(e,needle,needle+arc('domain-member','south','parent1').encode())
  with self.assertRaisesRegex(XBRLError,'primary_item_polymorphism'):derive(e)
 def test_malformed_negative_precedence_attribute_scope_and_target_roles_fail(self):
  old=arc('notAll','parent1','excludedcube0','xd:closed="true" xd:contextElement="segment" xd:targetRole="'+ROLES[1]+'"').encode()
  for extra in(b' priority="1e2"',b' use="required"',b' xd:usable="false"',b' invented="true"'):
   e=fixture();replace_negative(e,old,old.replace(b'/>',extra+b'/>'))
   with self.subTest(extra=extra),self.assertRaises(XBRLError):derive(e)
  e=fixture();replace_negative(e,old,old.replace(ROLES[1].encode(),b'urn:unresolved'))
  with self.assertRaisesRegex(XBRLError,'target_role_not_resolved'):derive(e)
 def test_duplicate_xlink_pair_across_all_notall_in_same_link_is_invalid(self):
  e=positive();a=arc('all','parent1','cube','xd:closed="true" xd:contextElement="segment" xd:targetRole="'+ROLES[1]+'"').encode();replace_negative(e,a,a+a.replace(b'/all"',b'/notAll"'))
  with self.assertRaisesRegex(XBRLError,'duplicate_xlink_arc'):derive(e)
 def test_distinct_declaration_sources_cannot_merge_negative_endpoints(self):
  e=fixture();schema=e['documents'][0]['raw'];south=re.search(b'<s:element[^>]*id="south"[^>]*/>',schema).group(0);other=schema[:schema.index(b'>')+1]+south+b'</s:schema>';e['documents'].append({'uri':BASE+'duplicate.xsd','raw':other,'sha256':hashlib.sha256(other).hexdigest()});edited(e,0,schema.replace(b'</s:schema>',b'<s:include schemaLocation="duplicate.xsd"/></s:schema>'))
  with self.assertRaisesRegex(XBRLError,'endpoint_source_ambiguous'):derive(e)
 def test_reserved_original_schema_namespace_cannot_supply_arc_semantics(self):
  e=fixture();raw=('<s:schema xmlns:s="http://www.w3.org/2001/XMLSchema" targetNamespace="'+D+'"/>').encode();e['documents'].append({'uri':BASE+'replacement.xsd','raw':raw,'sha256':hashlib.sha256(raw).hexdigest()});edited(e,0,e['documents'][0]['raw'].replace(b'</s:schema>',('<s:import namespace="'+D+'" schemaLocation="replacement.xsd"/></s:schema>').encode()))
  with self.assertRaisesRegex(XBRLError,'reserved_or_invalid_schema_namespace'):derive(e)
 def test_schema_source_receipts_must_be_complete_even_for_prohibited_arcs(self):
  out=derive();proof(out)['schema_sources']=[];rehash(out)
  with self.assertRaisesRegex(XBRLError,'dimensional_result_contract'):selected_financials(out)
 def test_rehashed_duplicate_source_nodes_and_role_bindings_fail(self):
  for change in('arc','link','role_type','sources'):
   out=derive();v=proof(out)
   if change=='arc':v['relationships'][1]['arc_node_ordinal']=v['relationships'][0]['arc_node_ordinal']
   elif change=='link':v['relationships'][-1]['link_node_ordinal']=v['relationships'][0]['link_node_ordinal']
   elif change=='role_type':v['role_references'][1]['role_type_node_ordinal']=v['role_references'][0]['role_type_node_ordinal']
   else:out['dts_corroboration']['concept_declarations']['{'+NS+'}South']['source_documents'].append(BASE+'authored.xsd')
   rehash(out)
   with self.subTest(change=change),self.assertRaisesRegex(XBRLError,'dimensional_result_contract'):selected_financials(out)
 def test_conflicting_values_are_preserved_never_selected_by_negative_validation(self):
  e=fixture();source_edit(e,e['raw'].replace(b'<g:Assets contextRef="I" unitRef="USD">1000</g:Assets>',b'<g:Assets contextRef="I" unitRef="USD">1000</g:Assets><g:Assets contextRef="I" unitRef="USD">2000</g:Assets>'));p,g=inputs(e);out=derive(e);self.assertEqual(out['facts'],p['facts']);self.assertTrue(all(f['admission']=='CONFLICTED_EXACT_VALUES'for f in out['facts']));self.assertEqual(len(proof(out)['facts']),2);self.assertFalse(selected_financials(out)['history']['assets'])
 def test_document_input_order_does_not_change_original_ordinal_semantics(self):
  e=fixture();first=derive(e);e['documents'].reverse();second=derive(e);self.assertEqual(first,second)
 def test_default_conflicts_reject_even_when_negative_cube_already_false(self):
  e=fixture(default=True,negative_axis=True);add_link(e,arc('dimension-default','axis','north').encode(),role=ROLES[5])
  with self.assertRaisesRegex(XBRLError,'global_default_conflict'):derive(e)
 def test_derived_input_cannot_be_reinterpreted_or_claim_complete_conformance(self):
  e=fixture();p,g=inputs(e);out=derive(e)
  with self.assertRaisesRegex(XBRLError,'already_applied'):corroborate(out,g,profile=MIXED_CROSS_ROLE_PROFILE,documents=e['documents'],instance_uri=e['instance_uri'])
  proof(out)['complete_drs_validation']=True;rehash(out)
  with self.assertRaisesRegex(XBRLError,'dimensional_result_contract'):selected_financials(out)
 def test_positive_only_v10_remains_a_bounded_explicit_profile(self):
  out=derive(positive());self.assertTrue(all(a['kind']=='all'for a in proof(out)['facts'][0]['assignments']));self.assertFalse(proof(out)['complete_drs_validation']);selected_financials(out)
 def test_numeric_bound_profile_composes_with_mixed_original_source_validation(self):
  from .xbrl_types import BOUNDS_PROFILE
  e=fixture();before=copy.deepcopy(e);c=FilingCollection('0000320193');c.ingest_dts_batch([e],numeric_profile=BOUNDS_PROFILE,dimensional_profile=MIXED_CROSS_ROLE_PROFILE);out=next(iter(c._filings.values()));self.assertEqual(out['numeric_interpretation_profile'],BOUNDS_PROFILE);self.assertEqual(proof(out)['profile'],MIXED_CROSS_ROLE_PROFILE);self.assertEqual(e,before);self.assertFalse(selected_financials(out)['history']['assets'])
 def test_numeric_bound_forgery_cannot_hide_behind_negative_context_success(self):
  from .xbrl_types import BOUNDS_PROFILE
  e=fixture();c=FilingCollection('0000320193');c.ingest_dts_batch([e],numeric_profile=BOUNDS_PROFILE,dimensional_profile=MIXED_CROSS_ROLE_PROFILE);out=next(iter(c._filings.values()));out['dts_corroboration']['numeric_value_validation']['facts'][0]['effective_bounds']['lower']={'value':'-999','inclusive':True};rehash(out)
  with self.assertRaisesRegex(XBRLError,'bound_result_contract'):selected_financials(out)
