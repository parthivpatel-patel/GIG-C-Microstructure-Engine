"""Authored offline XBRL 2.1 priority/prohibition and original-byte DRS fixtures."""
import copy,hashlib,re,unittest
from unittest.mock import patch
from .test_xbrl_inherited_cross_role import fixture,proof,rehash,derive as v8
from .test_xbrl_cross_role import edited,inputs,ROLES,BASE,NS
from .test_xbrl_dimensions import arc,D
from .xbrl_dimensions import corroborate,EFFECTIVE_CROSS_ROLE_PROFILE
from .xbrl_instance import selected_financials,canonical,XBRLError
from .xbrl_collection import FilingCollection


def derive(e=None,**kw):
 e=fixture()if e is None else e;p,g=inputs(e,observed=e['manifest']['origin']=='OBSERVED_OFFICIAL_RESPONSE')
 return corroborate(p,g,profile=EFFECTIVE_CROSS_ROLE_PROFILE,documents=e['documents'],instance_uri=e['instance_uri'],**kw)


def edge(kind='domain-member',source='domain',target='north',attrs='xd:targetRole="'+ROLES[4]+'"'):
 return arc(kind,source,target,attrs).encode()


def add_link(e,body,role=ROLES[3],separate=False):
 raw=e['documents'][1]['raw'];first=re.search(b'<l:definitionLink\\b[^>]*>(.*?)</l:definitionLink>',raw).group(1)
 locators=b''.join(re.findall(b'<l:loc\\b[^>]*/>',first))
 link=('<l:definitionLink xl:type="extended" xl:role="'+role+'">').encode()+locators+body+b'</l:definitionLink>'
 if separate:
  header=raw[:raw.index(b'<l:definitionLink')];other=header+link+b'</l:linkbase>';e['documents'].append({'uri':BASE+'override.xml','raw':other,'sha256':hashlib.sha256(other).hexdigest()})
  ref=b'<s:annotation><s:appinfo><l:linkbaseRef xl:type="simple" xl:href="override.xml"/></s:appinfo></s:annotation>';edited(e,0,e['documents'][0]['raw'].replace(b'</s:schema>',ref+b'</s:schema>'))
 else:edited(e,1,raw.replace(b'</l:linkbase>',link+b'</l:linkbase>'))
 return e


class EffectiveCrossRole(unittest.TestCase):
 def test_positive_inherited_multiple_cubes_preserve_original_facts(self):
  e=fixture();before=copy.deepcopy(e);p,g=inputs(e);out=derive(e);v=proof(out)
  self.assertEqual(out['schema'],'gig.sec.xbrl.dimensional_instance.v9');self.assertEqual(v['profile'],EFFECTIVE_CROSS_ROLE_PROFILE);self.assertFalse(v['complete_drs_validation']);self.assertEqual(len(v['facts'][0]['assignments']),2)
  for k in('facts','contexts','units','source'):self.assertEqual(out[k],p[k])
  self.assertEqual(e,before);self.assertFalse(selected_financials(out)['history']['assets'])
 def test_equal_priority_optional_arcs_choose_one_source_receipt(self):
  out=derive(add_link(fixture(),edge()));v=proof(out);self.assertEqual(len(v['relationships']),len(v['effective_relationships'])+1);g=next(g for g in v['resolution']if len(g['arc_indexes'])==2);self.assertEqual(g['effective_arc_index'],g['arc_indexes'][0]);selected_financials(out)
 def test_higher_priority_optional_overrides(self):
  out=derive(add_link(fixture(),edge(attrs='xd:targetRole="'+ROLES[4]+'" priority="+000002"')));v=proof(out);g=next(g for g in v['resolution']if len(g['arc_indexes'])==2);self.assertEqual(g['max_priority'],2);self.assertEqual(v['relationships'][g['effective_arc_index']]['priority'],2);selected_financials(out)
 def test_negative_integer_priority_is_defined_not_unsigned(self):
  out=derive(add_link(fixture(),edge(attrs='xd:targetRole="'+ROLES[4]+'" priority="-1" use="prohibited"')));g=next(g for g in proof(out)['resolution']if len(g['arc_indexes'])==2);self.assertEqual(g['max_priority'],0);self.assertEqual(g['status'],'EFFECTIVE')
 def test_prohibition_at_max_removes_member(self):
  with self.assertRaisesRegex(XBRLError,'member_outside_domain'):derive(add_link(fixture(),edge(attrs='xd:targetRole="'+ROLES[4]+'" priority="2" use="prohibited"')))
 def test_equal_priority_prohibition_wins_regardless_of_optional_order(self):
  with self.assertRaisesRegex(XBRLError,'member_outside_domain'):derive(add_link(fixture(),edge(attrs='xd:targetRole="'+ROLES[4]+'" use="prohibited"')))
 def test_higher_optional_can_override_lower_prohibition(self):
  e=add_link(fixture(),edge(attrs='xd:targetRole="'+ROLES[4]+'" priority="1" use="prohibited"'));add_link(e,edge(attrs='xd:targetRole="'+ROLES[4]+'" priority="2"'));out=derive(e);g=next(g for g in proof(out)['resolution']if len(g['arc_indexes'])==3);self.assertEqual(g['max_priority'],2);selected_financials(out)
 def test_unused_prohibition_is_retained_without_promoting_it(self):
  e=add_link(fixture(),edge(source='domain',target='south',attrs='priority="4" use="prohibited"'));out=derive(e);v=proof(out);g=next(g for g in v['resolution']if g['status']=='PROHIBITED_AT_MAX_PRIORITY');self.assertIsNone(g['effective_arc_index']);self.assertTrue(all(a['to']!='{'+NS+'}South'for a in v['effective_relationships']));selected_financials(out)
 def test_different_order_does_not_prohibit_other_order(self):
  out=derive(add_link(fixture(),edge(attrs='xd:targetRole="'+ROLES[4]+'" order="2" priority="9" use="prohibited"')));self.assertTrue(any(g['status']=='PROHIBITED_AT_MAX_PRIORITY'for g in proof(out)['resolution']));selected_financials(out)
 def test_decimal_value_space_and_default_order_are_equivalent(self):
  out=derive(add_link(fixture(),edge(attrs='xd:targetRole="'+ROLES[4]+'" order="+01.000" priority="3"')));self.assertTrue(any(len(g['arc_indexes'])==2 for g in proof(out)['resolution']));selected_financials(out)
 def test_different_target_role_does_not_suppress_existing_relationship(self):
  out=derive(add_link(fixture(),edge(attrs='xd:targetRole="'+ROLES[5]+'" priority="8" use="prohibited"')));selected_financials(out)
 def test_target_role_absent_is_not_replaced_with_source_role_for_equivalence(self):
  out=derive(add_link(fixture(),edge(attrs='priority="8" use="prohibited"')));selected_financials(out)
 def test_other_base_role_cannot_prohibit_selected_base(self):
  out=derive(add_link(fixture(),edge(attrs='xd:targetRole="'+ROLES[4]+'" priority="8" use="prohibited"'),role=ROLES[5]));selected_financials(out)
 def test_other_arcrole_cannot_prohibit_member(self):
  out=derive(add_link(fixture(),edge(kind='dimension-default',source='axis',target='north',attrs='priority="8" use="prohibited"')));selected_financials(out)
 def test_closed_boolean_value_space_equivalence(self):
  original=edge('all','parent1','cube','xd:closed="1" xd:contextElement="segment" xd:targetRole="'+ROLES[1]+'" priority="3"');out=derive(add_link(fixture(),original,role=ROLES[0]));self.assertTrue(any(len(g['arc_indexes'])==2 for g in proof(out)['resolution']));selected_financials(out)
 def test_authored_usable_attribute_presence_is_not_invented_in_psvi(self):
  out=derive(add_link(fixture(),edge(attrs='xd:targetRole="'+ROLES[4]+'" xd:usable="true" priority="8" use="prohibited"')));selected_financials(out)
 def test_effective_selection_spans_independent_original_linkbases(self):
  out=derive(add_link(fixture(),edge(attrs='xd:targetRole="'+ROLES[4]+'" priority="2"'),separate=True));self.assertTrue(any(a['source_uri']==BASE+'override.xml'for a in proof(out)['effective_relationships']));selected_financials(out)
 def test_duplicate_xlink_pair_in_one_link_rejects_before_collapsing(self):
  e=fixture();a=edge();edited(e,1,e['documents'][1]['raw'].replace(a,a+a))
  with self.assertRaisesRegex(XBRLError,'duplicate_xlink_arc'):derive(e)
 def test_non_equivalent_surviving_parallel_edges_remain_unsupported(self):
  with self.assertRaisesRegex(XBRLError,'duplicate_relationship'):derive(add_link(fixture(),edge(attrs='xd:targetRole="'+ROLES[4]+'" order="2" priority="8"')))
 def test_colliding_xpath_orders_do_not_guess_effectiveness(self):
  e=fixture();a=edge();edited(e,1,e['documents'][1]['raw'].replace(a,edge(attrs='xd:targetRole="'+ROLES[4]+'" order="9007199254740992"')));add_link(e,edge(attrs='xd:targetRole="'+ROLES[4]+'" order="9007199254740993" use="prohibited"'))
  with self.assertRaisesRegex(XBRLError,'order_xpath_ambiguity'):derive(e)
 def test_malformed_priority_and_use_reject(self):
  for attrs in('priority="1.1"','priority="1000000"','priority="1e2"','priority=""','use="required"'):
   with self.subTest(attrs=attrs),self.assertRaises(XBRLError):derive(add_link(fixture(),edge(attrs=attrs)))
 def test_unsupported_arc_attributes_and_unusable_stay_explicit(self):
  for attrs in('invented="true"','xd:usable="false"'):
   with self.subTest(attrs=attrs),self.assertRaisesRegex(XBRLError,'unsupported'):derive(add_link(fixture(),edge(attrs=attrs+' use="prohibited"')))
 def test_missing_changed_and_duplicate_originals_reject(self):
  for change in('missing','changed','duplicate'):
   e=fixture()
   if change=='missing':e['documents'].pop()
   elif change=='changed':e['documents'][1]['raw']+=b' '
   else:e['documents'].append(copy.deepcopy(e['documents'][1]))
   with self.subTest(change=change),self.assertRaises(XBRLError):derive(e)
 def test_resigned_effective_resolution_and_context_forgeries_reject(self):
  for change in('effective','resolution','priority','attributes','role','fact','labels'):
   out=derive(add_link(fixture(),edge()));v=proof(out)
   if change=='effective':v['effective_relationships'].pop()
   elif change=='resolution':v['resolution'][0]['max_priority']=999
   elif change=='priority':v['relationships'][0]['priority']=True
   elif change=='attributes':v['relationships'][0]['dimensional_attributes']={}
   elif change=='role':v['role_references']=[]
   elif change=='fact':v['facts'][0]['assignments'].pop()
   else:v['relationships'][0]['from_label']='bad label'
   rehash(out)
   with self.subTest(change=change),self.assertRaisesRegex(XBRLError,'dimensional_result_contract'):selected_financials(out)
 def test_effective_artifact_requires_new_versioned_schema(self):
  out=derive();out['schema']='gig.sec.xbrl.dimensional_instance.v8';rehash(out)
  with self.assertRaisesRegex(XBRLError,'dimensional_result_contract'):selected_financials(out)
 def test_v8_unchanged_rejects_precedence_profile(self):
  with self.assertRaisesRegex(XBRLError,'precedence_or_unusable_unsupported'):v8(add_link(fixture(),edge(attrs='priority="2"')))
 def test_collection_original_dts_path_applies_v9_and_stays_immutable(self):
  e=add_link(fixture(),edge(attrs='xd:targetRole="'+ROLES[4]+'" priority="2"'));before=copy.deepcopy(e);c=FilingCollection('0000320193');c.ingest_dts_batch([e],dimensional_profile=EFFECTIVE_CROSS_ROLE_PROFILE);out=next(iter(c._filings.values()));self.assertEqual(out['schema'],'gig.sec.xbrl.dimensional_instance.v9');self.assertEqual(e,before);self.assertFalse(selected_financials(out)['history']['assets']);self.assertEqual(c.at_acceptance_time('2024-02-02T00:00:00Z')['schema'],'gig.sec.xbrl.acceptance.v1')
 def test_collection_batch_rejects_atomically_on_missing_effective_member(self):
  c=FilingCollection('0000320193');bad=add_link(fixture(accession='0000320193-24-000002'),edge(attrs='xd:targetRole="'+ROLES[4]+'" priority="9" use="prohibited"'))
  with self.assertRaises(XBRLError):c.ingest_dts_batch([fixture(),bad],dimensional_profile=EFFECTIVE_CROSS_ROLE_PROFILE)
  self.assertEqual(c._filings,{})
 def test_resource_limits_are_not_bypassed_by_suppression(self):
  with patch('terminal.stocks.xbrl_effective_cross_role.MAX_OUTPUT',1),self.assertRaisesRegex(XBRLError,'output_budget'):derive()
 def test_observed_input_requires_approval_and_retained_permission(self):
  e=fixture(origin='OBSERVED_OFFICIAL_RESPONSE',permission_reference='owner-permitted-authored-fixture');base='https://www.sec.gov/Archives/edgar/data/320193/000000012324000001/';e['instance_uri']=e['manifest']['source_url']=base+'instance.xml'
  for d in e['documents']:d['uri']=d['uri'].replace(BASE,base)
  with self.assertRaisesRegex(XBRLError,'not_approved'):derive(e)
  selected_financials(derive(e,allow_observed=True))
 def test_removed_effective_cube_assignment_is_not_defaulted_back(self):
  e=fixture(cubes=1,inherited=False);add_link(e,edge('all','assets','cube','xd:closed="true" xd:contextElement="segment" xd:targetRole="'+ROLES[1]+'" priority="2" use="prohibited"'),role=ROLES[0])
  with self.assertRaisesRegex(XBRLError,'assignment_budget'):derive(e)
 def test_same_link_duplicate_pair_is_invalid_even_with_different_arcrole(self):
  e=fixture();a=edge();edited(e,1,e['documents'][1]['raw'].replace(a,a+edge(kind='dimension-domain')))
  with self.assertRaisesRegex(XBRLError,'duplicate_xlink_arc'):derive(e)
 def test_retained_duplicate_node_and_role_type_conflicts_are_rejected(self):
  for change in('node','link','role_type'):
   out=derive();v=proof(out)
   if change=='node':v['relationships'][1]['arc_node_ordinal']=v['relationships'][0]['arc_node_ordinal']
   elif change=='link':v['relationships'][-1]['link_node_ordinal']=v['relationships'][0]['link_node_ordinal']
   else:v['role_references'][1]['role_type_node_ordinal']=v['role_references'][0]['role_type_node_ordinal']
   rehash(out)
   with self.subTest(change=change),self.assertRaisesRegex(XBRLError,'dimensional_result_contract'):selected_financials(out)
 def test_suppressed_source_hash_and_label_identity_must_still_bind(self):
  for change in('hash','locator'):
   out=derive(add_link(fixture(),edge(attrs='xd:targetRole="'+ROLES[4]+'" priority="-1" use="prohibited"')));v=proof(out);a=next(a for a in v['relationships']if a['use']=='prohibited')
   if change=='hash':a['source_sha256']='0'*64
   else:a['from_label']=a['to_label']
   rehash(out)
   with self.subTest(change=change),self.assertRaisesRegex(XBRLError,'dimensional_result_contract'):selected_financials(out)
 def test_new_profile_cannot_reinterpret_already_derived_inputs(self):
  e=fixture();p,g=inputs(e);out=derive(e)
  with self.assertRaisesRegex(XBRLError,'already_applied'):corroborate(out,g,profile=EFFECTIVE_CROSS_ROLE_PROFILE,documents=e['documents'],instance_uri=e['instance_uri'])
 def test_typed_negative_open_and_alternative_bases_remain_unsupported(self):
  for change in('typed','negative','open','alternate'):
   e=fixture()
   if change=='typed':edited(e,0,e['documents'][0]['raw'].replace(b'name="RegionAxis"',b'name="RegionAxis" xd:typedDomainRef="#domain"'))
   elif change=='negative':edited(e,1,e['documents'][1]['raw'].replace(b'/all"',b'/notAll"'))
   elif change=='open':edited(e,1,e['documents'][1]['raw'].replace(b'xd:closed="true"',b'xd:closed="false"'))
   else:add_link(e,edge('all','assets','cube','xd:closed="true" xd:contextElement="segment" xd:targetRole="'+ROLES[1]+'"'),role=ROLES[5])
   with self.subTest(change=change),self.assertRaises(XBRLError):derive(e)
 def test_inline_set_collection_passes_original_sources_to_v9(self):
  from .test_inline_set import html,doc
  e=fixture(member=None,default=True);raw=e['raw'].decode();resources=raw[raw.index('<x:context'):raw.index('<g:Assets')];page=html('',resources=True).decode();start=page.index('<x:context');end=page.index('</ix:resources>');page=(page[:start]+resources+page[end:]).replace('<html ','<html xmlns:d="http://xbrl.org/2006/xbrldi" ',1)
  originals=[doc('resources.xhtml',page.encode()),doc('facts.xhtml',html('<ix:nonFraction name="g:Assets" contextRef="I" unitRef="USD">1000</ix:nonFraction>'))];before=copy.deepcopy(originals);c=FilingCollection('0000320193');c.ingest_inline_set_batch([{'documents':originals,'concepts':e['concepts'],'taxonomy_documents':e['documents']}],dimensional_profile=EFFECTIVE_CROSS_ROLE_PROFILE);out=next(iter(c._filings.values()));self.assertEqual(out['schema'],'gig.sec.xbrl.dimensional_inline_set.v9');self.assertEqual(originals,before);self.assertTrue(proof(out)['facts'][0]['used_defaults']);self.assertFalse(selected_financials(out)['history']['assets'])
 def test_effectiveness_never_changes_conflicting_reported_facts(self):
  e=fixture();e['raw']=e['raw'].replace(b'<g:Assets contextRef="I" unitRef="USD">1000</g:Assets>',b'<g:Assets contextRef="I" unitRef="USD">1000</g:Assets><g:Assets contextRef="I" unitRef="USD">2000</g:Assets>');e['manifest']['source_sha256']=hashlib.sha256(e['raw']).hexdigest();p,g=inputs(e);out=derive(e);self.assertEqual(out['facts'],p['facts']);self.assertTrue(all(f['admission']=='CONFLICTED_EXACT_VALUES'for f in out['facts']));self.assertEqual(len(proof(out)['facts']),2);self.assertFalse(selected_financials(out)['history']['assets'])
 def test_distinct_original_declaration_nodes_cannot_be_merged_by_qname(self):
  e=add_link(fixture(member='South'),edge(attrs='xd:targetRole="'+ROLES[4]+'" use="prohibited" priority="9"'));schema=e['documents'][0]['raw'];north=re.search(b'<s:element[^>]*id="north"[^>]*/>',schema).group(0);second=schema[:schema.index(b'>')+1]+north+b'</s:schema>'
  e['documents'].append({'uri':BASE+'duplicate.xsd','raw':second,'sha256':hashlib.sha256(second).hexdigest()});edited(e,0,schema.replace(b'</s:schema>',b'<s:include schemaLocation="duplicate.xsd"/></s:schema>'));raw=e['documents'][1]['raw'];last=raw.rfind(b'<l:definitionLink');edited(e,1,raw[:last]+raw[last:].replace(b'authored.xsd#north',b'duplicate.xsd#north'))
  with self.assertRaisesRegex(XBRLError,'endpoint_source_ambiguous'):derive(e)
 def test_retained_ambiguous_missing_or_wrong_kind_endpoint_sources_reject(self):
  for sources in([], [BASE+'authored.xsd',BASE+'authored.xsd'], [BASE+'dimensions.xml'], [BASE+'not-supplied.xsd']):
   out=derive();out['dts_corroboration']['concept_declarations']['{'+NS+'}North']['source_documents']=sources;rehash(out)
   with self.subTest(sources=sources),self.assertRaisesRegex(XBRLError,'dimensional_result_contract'):selected_financials(out)
 def test_original_schema_cannot_replace_normative_arc_datatypes_or_defaults(self):
  namespaces=['http://www.xbrl.org/2003/linkbase',D,'http://www.w3.org/2001/XMLSchema','http://www.xbrl.org/2003/instance','http://www.w3.org/1999/xlink','http://www.w3.org/2001/XMLSchema-instance','http://www.w3.org/XML/1998/namespace','http://www.w3.org/2000/xmlns/','http://xbrl.org/2006/xbrldi']
  for namespace in namespaces:
   e=fixture();raw=('<s:schema xmlns:s="http://www.w3.org/2001/XMLSchema" targetNamespace="'+namespace+'"><s:element name="definitionArc" type="s:string"/></s:schema>').encode();e['documents'].append({'uri':BASE+'normative-replacement.xsd','raw':raw,'sha256':hashlib.sha256(raw).hexdigest()});imp=('<s:import namespace="'+namespace+'" schemaLocation="normative-replacement.xsd"/>').encode();edited(e,0,e['documents'][0]['raw'].replace(b'</s:schema>',imp+b'</s:schema>'))
   with self.subTest(namespace=namespace),self.assertRaisesRegex(XBRLError,'reserved_or_invalid_schema_namespace'):derive(e)
 def test_retained_schema_namespace_receipts_require_exact_source_coverage(self):
  for change in('missing','duplicate','reserved','hash','uri','extra'):
   out=derive();v=proof(out)
   if change=='missing':v['schema_sources']=[]
   elif change=='duplicate':v['schema_sources']*=2
   elif change=='reserved':v['schema_sources'][0]['target_namespace']=D
   elif change=='hash':v['schema_sources'][0]['source_sha256']='0'*64
   elif change=='uri':v['schema_sources'][0]['source_uri']=BASE+'dimensions.xml'
   else:v['schema_sources'][0]['unrecognized']='bad'
   rehash(out)
   with self.subTest(change=change),self.assertRaisesRegex(XBRLError,'dimensional_result_contract'):selected_financials(out)
 def test_schema_namespace_cannot_rebind_endpoint_to_other_namespace(self):
  out=derive();proof(out)['schema_sources'][0]['target_namespace']='urn:another-namespace';rehash(out)
  with self.assertRaisesRegex(XBRLError,'dimensional_result_contract'):selected_financials(out)
 def test_namespace_receipts_include_all_original_schemas_in_canonical_order(self):
  e=fixture();raw=b'<s:schema xmlns:s="http://www.w3.org/2001/XMLSchema" targetNamespace="urn:authored:auxiliary"/>';e['documents'].append({'uri':BASE+'auxiliary.xsd','raw':raw,'sha256':hashlib.sha256(raw).hexdigest()});edited(e,0,e['documents'][0]['raw'].replace(b'</s:schema>',b'<s:import namespace="urn:authored:auxiliary" schemaLocation="auxiliary.xsd"/></s:schema>'));out=derive(e);receipts=proof(out)['schema_sources'];self.assertEqual(len(receipts),2);self.assertEqual([r['source_uri']for r in receipts],sorted(r['source_uri']for r in receipts));self.assertEqual({r['source_uri']:r['source_sha256']for r in receipts},{d['uri']:d['sha256']for d in out['dts_corroboration']['documents']if d['kind']=='schema'});selected_financials(out)
  receipts.reverse();rehash(out)
  with self.assertRaisesRegex(XBRLError,'dimensional_result_contract'):selected_financials(out)

 def test_two_original_nodes_in_same_schema_cannot_share_endpoint_qname(self):
  e=fixture();schema=e['documents'][0]['raw'];north=re.search(b'<s:element[^>]*id="north"[^>]*/>',schema).group(0);edited(e,0,schema.replace(b'</s:schema>',north.replace(b'id="north"',b'id="north2"')+b'</s:schema>'))
  with self.assertRaisesRegex(XBRLError,'duplicate_concept_declaration'):derive(e)
