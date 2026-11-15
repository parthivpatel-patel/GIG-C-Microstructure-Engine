"""Negative-only explicit cube conjunction with global context/default admission."""
import copy,hashlib,unittest
from .test_xbrl_negative_dimensions import negative
from .test_xbrl_dimensions import arc,NS
from .test_xbrl_open_dimensions import edited
from .xbrl_dimensions import PROFILE,OPEN_PROFILE,INHERITED_PROFILE,NEGATIVE_PROFILE,NEGATIVE_ONLY_PROFILE,corroborate
from .xbrl_instance import parse_instance,selected_financials,digest,XBRLError
from .xbrl_dts import discover
from .xbrl_binding import bind_declarations
from .xbrl_collection import FilingCollection

def only(**kwargs):
 e=negative(**kwargs);old=arc('all','parent0','cube','xd:closed="true" xd:contextElement="segment"');edited(e,1,e['documents'][1]['raw'].replace(old.encode(),b''));return e

def derive(e=None,profile=NEGATIVE_ONLY_PROFILE):
 e=only()if e is None else e;p=parse_instance(e['raw'],e['manifest'],e['concepts']);d=discover(e['raw'],e['instance_uri'],e['manifest']['source_sha256'],e['documents']);return corroborate(bind_declarations(p,d),d,profile=profile)
def proof(p):return p['dts_corroboration']['dimensional_validation']

class NegativeOnlyDimensions(unittest.TestCase):
 def test_inherited_negative_only_cube_retains_source_operation_and_false_outcome(self):
  e=only();before=copy.deepcopy(e);p=derive(e);r=proof(p)['facts'][0];self.assertEqual(p['schema'],'gig.sec.xbrl.dimensional_instance.v5');self.assertEqual(proof(p)['profile'],NEGATIVE_ONLY_PROFILE);self.assertFalse(proof(p)['complete_drs_validation']);self.assertEqual(e,before)
  self.assertEqual(r['used_defaults'],{});self.assertEqual(r['global_defaults'],{});self.assertEqual(len(r['assignments']),1);a=r['assignments'][0];self.assertEqual(a['kind'],'notAll');self.assertFalse(a['hypercube_valid']);self.assertTrue(a['inherited']);self.assertEqual(a['failure_reason'],'drs_required_dimension_missing')
 def test_default_free_empty_context_can_retain_its_original_reported_number(self):
  p=derive(only(member=None));self.assertEqual(p['contexts']['I']['dimensions'],[]);self.assertEqual(proof(p)['facts'][0]['used_defaults'],{});self.assertEqual(selected_financials(p)['history']['assets'][0]['value'],'1000')
 def test_global_unused_default_prevents_false_consolidation_of_empty_context(self):
  p=derive(only(member=None,positive_default=True));r=proof(p)['facts'][0];expected={'{'+NS+'}RegionAxis':'{'+NS+'}South'};self.assertEqual(r['global_defaults'],expected);self.assertEqual(r['used_defaults'],expected);self.assertEqual(r['assignments'][0]['used_defaults'],{});self.assertEqual(p['contexts']['I']['dimensions'],[]);self.assertFalse(selected_financials(p)['history']['assets'])
 def test_reported_nondefault_value_overrides_implicit_default_without_rewriting_context(self):
  p=derive(only(positive_default=True));r=proof(p)['facts'][0];self.assertEqual(r['global_defaults'],{'{'+NS+'}RegionAxis':'{'+NS+'}South'});self.assertEqual(r['used_defaults'],{});self.assertEqual(p['contexts']['I']['dimensions'][0]['member'],'{'+NS+'}North')
 def test_negative_closed_extras_do_not_remove_unreported_global_defaults(self):
  p=derive(only(closed=True,default=True));r=proof(p)['facts'][0];self.assertEqual(r['global_defaults'],{'{'+NS+'}ExcludedAxis':'{'+NS+'}South'});self.assertEqual(r['used_defaults'],r['global_defaults']);self.assertEqual(r['assignments'][0]['failure_reason'],'drs_closed_extra_dimension');self.assertEqual(r['assignments'][0]['used_defaults'],{})
 def test_valid_negative_cube_still_rejects_even_without_positive_assignments(self):
  with self.assertRaisesRegex(XBRLError,'negative_hypercube_satisfied'):derive(only(default=True))
 def test_explicit_global_default_cannot_be_treated_as_satisfied_negative(self):
  with self.assertRaisesRegex(XBRLError,'explicit_default_member'):derive(only(member='South',positive_default=True,closed=True))
 def test_unknown_or_outside_reported_dimension_is_rejected_before_negative_evaluation(self):
  e=only(closed=True);e['raw']=e['raw'].replace(b'dimension="g:RegionAxis"',b'dimension="g:UnknownAxis"');e['manifest']['source_sha256']=hashlib.sha256(e['raw']).hexdigest()
  with self.assertRaisesRegex(XBRLError,'declaration_unsupported'):derive(e)
  with self.assertRaisesRegex(XBRLError,'member_outside_domain'):derive(only(member='Leaf',closed=True))
 def test_typed_opaque_or_wrong_container_context_is_never_a_negative_witness(self):
  e=only();e['raw']=e['raw'].replace(b'<d:explicitMember dimension="g:RegionAxis">g:North</d:explicitMember>',b'<d:typedMember dimension="g:RegionAxis"><g:Code>A</g:Code></d:typedMember>');e['manifest']['source_sha256']=hashlib.sha256(e['raw']).hexdigest()
  with self.assertRaisesRegex(XBRLError,'context_profile_unsupported'):derive(e)
  e=only();e['raw']=e['raw'].replace(b'</x:segment>',b'<g:Opaque>unmodeled</g:Opaque></x:segment>');e['manifest']['source_sha256']=hashlib.sha256(e['raw']).hexdigest()
  with self.assertRaisesRegex(XBRLError,'context_profile_unsupported'):derive(e)
  e=only();edited(e,1,e['documents'][1]['raw'].replace(b'contextElement="segment"',b'contextElement="scenario"'))
  with self.assertRaisesRegex(XBRLError,'context_profile_unsupported'):derive(e)
 def test_legacy_profiles_continue_refusing_negative_only_scope(self):
  for profile in(PROFILE,OPEN_PROFILE,INHERITED_PROFILE):
   with self.assertRaisesRegex(XBRLError,'not_all_unsupported'):derive(only(),profile)
  with self.assertRaisesRegex(XBRLError,'positive_assignment_required'):derive(only(),NEGATIVE_PROFILE)
 def test_mixed_applicable_assignments_remain_a_separate_explicit_profile(self):
  with self.assertRaisesRegex(XBRLError,'negative_only_assignments_required'):derive(negative())
  self.assertEqual(derive(negative(),NEGATIVE_PROFILE)['schema'],'gig.sec.xbrl.dimensional_instance.v4')
 def test_every_applicable_negative_cube_must_be_false(self):
  e=only(negative_count=2);old=arc('hypercube-dimension','excludedcube1','excludedaxis');edited(e,1,e['documents'][1]['raw'].replace(old.encode(),arc('hypercube-dimension','excludedcube1','axis').encode()))
  with self.assertRaisesRegex(XBRLError,'negative_hypercube_satisfied'):derive(e)
 def test_global_default_conflicts_and_repeated_arcs_reject_even_when_unused(self):
  for member in('north','south'):
   e=only(positive_default=True);edited(e,1,e['documents'][1]['raw'].replace(b'</l:definitionLink>',arc('dimension-default','axis',member).encode()+b'</l:definitionLink>'))
   with self.assertRaisesRegex(XBRLError,'ambiguous_global_default'):derive(e)
 def test_global_default_requires_supported_explicit_declaration_and_valid_domain(self):
  e=only(positive_default=True);edited(e,0,e['documents'][0]['raw'].replace(b'name="RegionAxis"',b'xd:typedDomainRef="#domain" name="RegionAxis"'))
  with self.assertRaisesRegex(XBRLError,'declaration_unsupported'):derive(e)
  e=only(positive_default=True);edited(e,1,e['documents'][1]['raw'].replace(arc('dimension-domain','axis','domain').encode(),b''))
  with self.assertRaisesRegex(XBRLError,'single_domain_required'):derive(e)
 def test_global_default_budget_is_bounded_independently_of_applicable_cubes(self):
  e=only();declarations='';extra=''
  for i in range(33):
   id_='global'+str(i);declarations+='<s:element id="'+id_+'" name="GlobalAxis'+str(i)+'" substitutionGroup="xd:dimensionItem" abstract="true" x:periodType="duration"/>';extra+='<l:loc xl:type="locator" xl:label="'+id_+'" xl:href="authored.xsd#'+id_+'"/>'+arc('dimension-domain',id_,'domain')+arc('dimension-default',id_,'south')
  edited(e,0,e['documents'][0]['raw'].replace(b'</s:schema>',declarations.encode()+b'</s:schema>'));edited(e,1,e['documents'][1]['raw'].replace(b'</l:definitionLink>',extra.encode()+b'</l:definitionLink>'))
  with self.assertRaisesRegex(XBRLError,'global_default_budget'):derive(e)
 def test_applicable_and_network_assignment_limits_remain_sixteen_and_sixtyfour(self):
  self.assertEqual(len(proof(derive(only(negative_count=16)))['facts'][0]['assignments']),16)
  with self.assertRaisesRegex(XBRLError,'fact_assignment_budget'):derive(only(negative_count=17))
  with self.assertRaisesRegex(XBRLError,'positive_assignment_budget'):derive(only(negative_count=65))
 def test_negative_only_inheritance_keeps_cycle_and_depth_bounds(self):
  e=only();edited(e,1,e['documents'][1]['raw'].replace(b'</l:definitionLink>',arc('domain-member','assets','parent0').encode()+b'</l:definitionLink>'))
  with self.assertRaisesRegex(XBRLError,'primary_item_cycle'):derive(e)
 def test_collection_rejects_later_invalid_negative_atomically(self):
  c=FilingCollection('0000320193');c.ingest_dts_batch([only(member=None,positive_default=True)],dimensional_profile=NEGATIVE_ONLY_PROFILE);before=c.page();self.assertFalse(c.at_acceptance_time('2024-02-02T00:00:00Z')['history']['assets'])
  bad=only(default=True);bad['manifest']['accession']='0000000123-24-000002'
  with self.assertRaisesRegex(XBRLError,'negative_hypercube_satisfied'):c.ingest_dts_batch([bad],dimensional_profile=NEGATIVE_ONLY_PROFILE)
  self.assertEqual(c.page(),before)
 def test_inline_original_identity_and_global_defaults_survive_negative_only_derivation(self):
  from .test_inline_set import html,doc
  e=only(member=None,positive_default=True);raw=e['raw'].decode();resources=raw[raw.index('<x:context'):raw.index('<g:Assets')]
  page=html('<ix:nonFraction name="g:Assets" contextRef="I" unitRef="USD">1000</ix:nonFraction>',resources=True).decode();start=page.index('<x:context');end=page.index('</ix:resources>');page=(page[:start]+resources+page[end:]).replace('<html ','<html xmlns:d="http://xbrl.org/2006/xbrldi" ',1)
  original=doc('negative-only.xhtml',page.encode());c=FilingCollection('0000320193');c.ingest_inline_set_batch([{'documents':[original],'concepts':e['concepts'],'taxonomy_documents':e['documents']}],dimensional_profile=NEGATIVE_ONLY_PROFILE)
  p=next(iter(c._filings.values()));self.assertEqual(p['schema'],'gig.sec.xbrl.dimensional_inline_set.v5');self.assertEqual(p['document_set']['documents'][0]['source']['source_sha256'],original['manifest']['source_sha256']);self.assertEqual(proof(p)['facts'][0]['global_defaults'],{'{'+NS+'}RegionAxis':'{'+NS+'}South'});self.assertFalse(c.at_acceptance_time('2024-02-02T00:00:00Z')['history']['assets'])
 def test_v5_proof_default_structure_outcomes_and_identity_reject_corruption(self):
  p=derive(only(member=None,positive_default=True))
  for kind in('schema','profile','drop','global','used','qname','budget','kind','outcome','reason','inherited','reporteddefault','complete'):
   bad=copy.deepcopy(p);bad.pop('canonical_sha256');v=proof(bad);r=v['facts'][0];a=r['assignments'][0]
   if kind=='schema':bad['schema']='gig.sec.xbrl.dimensional_instance.v4'
   elif kind=='profile':v['profile']=NEGATIVE_PROFILE
   elif kind=='drop':r.pop('global_defaults')
   elif kind=='global':r['global_defaults']={}
   elif kind=='used':r['used_defaults']={}
   elif kind=='qname':r['global_defaults']={'not-an-expanded-name':'{'+NS+'}South'}
   elif kind=='budget':r['global_defaults']={'{urn:extra}Axis'+str(i):'{urn:extra}Member'for i in range(33)}
   elif kind=='kind':a['kind']='all';a['hypercube_valid']=True;a['failure_reason']=None
   elif kind=='outcome':a['hypercube_valid']=True
   elif kind=='reason':a['failure_reason']='drs_declaration_unsupported'
   elif kind=='inherited':a['inherited']=not a['inherited']
   elif kind=='reporteddefault':
    # Preserve a valid original context artifact;only claim its actual member is
    # also the globaldefault,which the selected proof must reject independently.
    bad=derive(only(positive_default=True));bad.pop('canonical_sha256');r=proof(bad)['facts'][0];r['global_defaults']={'{'+NS+'}RegionAxis':'{'+NS+'}North'};r['used_defaults']={}
   else:v['complete_drs_validation']=True
   bad['canonical_sha256']=digest(bad)
   with self.subTest(kind=kind),self.assertRaisesRegex(XBRLError,'dimensional_result'):selected_financials(bad)
 def test_unrelated_default_outside_domain_and_cycles_are_source_errors(self):
  e=only(positive_default=True);edited(e,1,e['documents'][1]['raw'].replace(arc('dimension-default','axis','south').encode(),arc('dimension-default','axis','leaf').encode()))
  with self.assertRaisesRegex(XBRLError,'default_conflict_or_domain'):derive(e)
  e=only(positive_default=True);edited(e,1,e['documents'][1]['raw'].replace(b'</l:definitionLink>',arc('domain-member','north','domain').encode()+b'</l:definitionLink>'))
  with self.assertRaisesRegex(XBRLError,'domain_cycle'):derive(e)
 def test_combined_global_defaults_and_reported_axes_remain_bounded(self):
  e=only();declarations='';extra=''
  for i in range(32):
   id_='global'+str(i);declarations+='<s:element id="'+id_+'" name="GlobalAxis'+str(i)+'" substitutionGroup="xd:dimensionItem" abstract="true" x:periodType="duration"/>';extra+='<l:loc xl:type="locator" xl:label="'+id_+'" xl:href="authored.xsd#'+id_+'"/>'+arc('dimension-domain',id_,'domain')+arc('dimension-default',id_,'south')
  edited(e,0,e['documents'][0]['raw'].replace(b'</s:schema>',declarations.encode()+b'</s:schema>'));edited(e,1,e['documents'][1]['raw'].replace(b'</l:definitionLink>',extra.encode()+b'</l:definitionLink>'))
  with self.assertRaisesRegex(XBRLError,'dimension_budget_or_missing'):derive(e)
