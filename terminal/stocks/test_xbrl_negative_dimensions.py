"""Authored mixed all/notAll cube conjunction and conservative invalidity checks."""
import copy,hashlib,unittest
from .test_xbrl_inherited_dimensions import inherited
from .test_xbrl_dimensions import arc,NS
from .test_xbrl_open_dimensions import edited
from .xbrl_dimensions import PROFILE,OPEN_PROFILE,INHERITED_PROFILE,NEGATIVE_PROFILE,corroborate
from .xbrl_instance import parse_instance,selected_financials,digest,XBRLError
from .xbrl_dts import discover
from .xbrl_binding import bind_declarations
from .xbrl_collection import FilingCollection

def negative(*,closed=False,default=False,positive_default=False,member='North',negative_count=1,inherited_negative=True):
 e=inherited(cubes=1,member=member,default=positive_default);schema=e['documents'][0]['raw'];link=e['documents'][1]['raw']
 declaration='<s:element id="excludedaxis" name="ExcludedAxis" substitutionGroup="xd:dimensionItem" abstract="true" x:periodType="duration"/>'
 loc='<l:loc xl:type="locator" xl:label="excludedaxis" xl:href="authored.xsd#excludedaxis"/>'
 extra=arc('dimension-domain','excludedaxis','domain')+(arc('dimension-default','excludedaxis','south')if default else'')
 for i in range(negative_count):
  id_='excludedcube'+str(i);declaration+='<s:element id="'+id_+'" name="ExcludedCube'+str(i)+'" substitutionGroup="xd:hypercubeItem" abstract="true" x:periodType="duration"/>'
  loc+='<l:loc xl:type="locator" xl:label="'+id_+'" xl:href="authored.xsd#'+id_+'"/>'
  extra+=arc('notAll','parent1'if inherited_negative else'assets',id_,'xd:closed="'+str(closed).lower()+'" xd:contextElement="segment"')+arc('hypercube-dimension',id_,'excludedaxis')
 edited(e,0,schema.replace(b'</s:schema>',declaration.encode()+b'</s:schema>'));edited(e,1,link.replace(b'</l:definitionLink>',(loc+extra).encode()+b'</l:definitionLink>'))
 return e

def derive(e=None,profile=NEGATIVE_PROFILE):
 e=negative()if e is None else e;p=parse_instance(e['raw'],e['manifest'],e['concepts']);d=discover(e['raw'],e['instance_uri'],e['manifest']['source_sha256'],e['documents']);return corroborate(bind_declarations(p,d),d,profile=profile)
def proof(p):return p['dts_corroboration']['dimensional_validation']

class NegativeDimensions(unittest.TestCase):
 def test_inherited_positive_and_missing_axis_negative_have_explicit_outcomes(self):
  e=negative();before=copy.deepcopy(e);p=derive(e);r=proof(p)['facts'][0];self.assertEqual(p['schema'],'gig.sec.xbrl.dimensional_instance.v4');self.assertEqual(proof(p)['profile'],NEGATIVE_PROFILE);self.assertFalse(proof(p)['complete_drs_validation']);self.assertEqual(e,before)
  a,n=r['assignments'];self.assertEqual(a['kind'],'all');self.assertTrue(a['hypercube_valid']);self.assertIsNone(a['failure_reason']);self.assertEqual(n['kind'],'notAll');self.assertFalse(n['hypercube_valid']);self.assertEqual(n['failure_reason'],'drs_required_dimension_missing');self.assertTrue(n['inherited']);self.assertEqual(n['used_defaults'],{})
 def test_direct_negative_is_preserved_as_direct_without_changing_positive_lineage(self):
  p=derive(negative(inherited_negative=False));a,n=proof(p)['facts'][0]['assignments'];self.assertTrue(a['inherited']);self.assertFalse(n['inherited']);self.assertEqual(n['primary_item'],'{'+NS+'}Assets')
 def test_well_formed_closed_negative_fails_on_unexpected_axis(self):
  p=derive(negative(closed=True));n=proof(p)['facts'][0]['assignments'][1];self.assertTrue(n['closed']);self.assertEqual(n['extra_dimensions'],['{'+NS+'}RegionAxis']);self.assertEqual(n['failure_reason'],'drs_closed_extra_dimension')
 def test_valid_negative_cube_rejects_primary_instead_of_ignoring_notall(self):
  with self.assertRaisesRegex(XBRLError,'negative_hypercube_satisfied'):derive(negative(default=True))
 def test_positive_defaults_only_aggregate_without_negative_fact_synthesis(self):
  p=derive(negative(member=None,positive_default=True));r=proof(p)['facts'][0];expected={'{'+NS+'}RegionAxis':'{'+NS+'}South'};self.assertEqual(r['used_defaults'],expected);self.assertEqual(r['assignments'][1]['used_defaults'],{});self.assertEqual(p['contexts']['I']['dimensions'],[])
 def test_all_legacy_profiles_keep_rejecting_negative_scope(self):
  for profile in(PROFILE,OPEN_PROFILE,INHERITED_PROFILE):
   with self.assertRaisesRegex(XBRLError,'not_all_unsupported'):derive(negative(),profile)
 def test_negative_only_assignment_is_explicitly_unsupported(self):
  e=negative();old=arc('all','parent0','cube','xd:closed="true" xd:contextElement="segment"');edited(e,1,e['documents'][1]['raw'].replace(old.encode(),b''))
  with self.assertRaisesRegex(XBRLError,'positive_assignment_required'):derive(e)
 def test_invalid_negative_declaration_is_not_a_satisfied_exclusion(self):
  for old,new in[(b'name="ExcludedAxis"',b'xd:typedDomainRef="#domain" name="ExcludedAxis"'),(b'id="excludedaxis"',b'id="notreferenced"'),(b'name="ExcludedCube0" substitutionGroup="xd:hypercubeItem"',b'name="ExcludedCube0" substitutionGroup="x:item"')]:
   e=negative(closed=True);edited(e,0,e['documents'][0]['raw'].replace(old,new))
   with self.assertRaises(XBRLError):derive(e)
 def test_missing_domain_and_domain_cycle_reject_before_closed_negative_evaluation(self):
  e=negative(closed=True);edited(e,1,e['documents'][1]['raw'].replace(arc('dimension-domain','excludedaxis','domain').encode(),b''))
  with self.assertRaisesRegex(XBRLError,'single_domain_required'):derive(e)
  # The positive axis keeps its original valid domain; only the negative domain cycles.
  e=negative(closed=True);schema=e['documents'][0]['raw'].replace(b'</s:schema>',b'<s:element id="negdomain" name="NegDomain" substitutionGroup="x:item" abstract="true" x:periodType="instant"/></s:schema>');edited(e,0,schema)
  link=e['documents'][1]['raw'].replace(arc('dimension-domain','excludedaxis','domain').encode(),arc('dimension-domain','excludedaxis','negdomain').encode());extra='<l:loc xl:type="locator" xl:label="negdomain" xl:href="authored.xsd#negdomain"/>'+arc('domain-member','negdomain','negdomain');edited(e,1,link.replace(b'</l:definitionLink>',extra.encode()+b'</l:definitionLink>'))
  with self.assertRaisesRegex(XBRLError,'domain_cycle'):derive(e)
 def test_negative_default_conflict_is_not_masked_by_contextual_invalidity(self):
  e=negative(closed=True,default=True);edited(e,1,e['documents'][1]['raw'].replace(b'</l:definitionLink>',arc('dimension-default','excludedaxis','north').encode()+b'</l:definitionLink>'))
  with self.assertRaisesRegex(XBRLError,'default_conflict_or_domain'):derive(e)
 def test_negative_unknown_priority_or_crossrole_never_counts_as_invalid_cube(self):
  for attr in('priority="1"','xd:targetRole="urn:other"','use="prohibited"'):
   e=negative();old=arc('notAll','parent1','excludedcube0','xd:closed="false" xd:contextElement="segment"');edited(e,1,e['documents'][1]['raw'].replace(old.encode(),arc('notAll','parent1','excludedcube0','xd:closed="false" xd:contextElement="segment" '+attr).encode()))
   with self.assertRaisesRegex(XBRLError,'profile_unsupported'):derive(e)
 def test_positive_failure_cannot_be_rescued_by_satisfied_negative(self):
  with self.assertRaisesRegex(XBRLError,'required_dimension_missing'):derive(negative(member=None))
 def test_sixteen_total_assignments_accepted_seventeen_rejected(self):
  self.assertEqual(len(proof(derive(negative(negative_count=15)))['facts'][0]['assignments']),16)
  with self.assertRaisesRegex(XBRLError,'fact_assignment_budget'):derive(negative(negative_count=16))
 def test_negative_axes_and_source_members_cannot_exceed_resource_bounds(self):
  e=negative();edited(e,1,e['documents'][1]['raw'].replace(arc('hypercube-dimension','excludedcube0','excludedaxis').encode(),b''))
  with self.assertRaisesRegex(XBRLError,'dimension_budget_or_missing'):derive(e)
 def test_same_cube_all_and_notall_is_contradiction_not_silent_selection(self):
  e=negative();edited(e,1,e['documents'][1]['raw'].replace(arc('hypercube-dimension','excludedcube0','excludedaxis').encode(),arc('hypercube-dimension','excludedcube0','axis').encode()))
  with self.assertRaisesRegex(XBRLError,'negative_hypercube_satisfied'):derive(e)
 def test_collection_failure_is_atomic_and_defaulted_values_stay_unavailable(self):
  c=FilingCollection('0000320193');c.ingest_dts_batch([negative(member=None,positive_default=True)],dimensional_profile=NEGATIVE_PROFILE);before=c.page();self.assertFalse(c.at_acceptance_time('2024-02-02T00:00:00Z')['history']['assets'])
  bad=negative(default=True);bad['manifest']['accession']='0000000123-24-000002'
  with self.assertRaisesRegex(XBRLError,'negative_hypercube_satisfied'):c.ingest_dts_batch([bad],dimensional_profile=NEGATIVE_PROFILE)
  self.assertEqual(c.page(),before)
 def test_identical_primary_cube_pair_with_opposite_kind_is_a_contradiction(self):
  e=negative();old=arc('notAll','parent1','excludedcube0','xd:closed="false" xd:contextElement="segment"');new=arc('notAll','parent0','cube','xd:closed="true" xd:contextElement="segment"');edited(e,1,e['documents'][1]['raw'].replace(old.encode(),new.encode()))
  with self.assertRaisesRegex(XBRLError,'negative_hypercube_satisfied'):derive(e)
 def test_global_assignment_limit_counts_both_positive_and_negative(self):
  with self.assertRaisesRegex(XBRLError,'positive_assignment_budget'):derive(negative(negative_count=64))
 def test_negative_cube_resource_error_is_not_a_context_exclusion(self):
  e=negative(closed=True);schema=e['documents'][0]['raw'];link=e['documents'][1]['raw'].replace(arc('hypercube-dimension','excludedcube0','excludedaxis').encode(),b'');decl='';extra=''
  for i in range(33):
   id_='many'+str(i);decl+='<s:element id="'+id_+'" name="ManyAxis'+str(i)+'" substitutionGroup="xd:dimensionItem" abstract="true" x:periodType="duration"/>';extra+='<l:loc xl:type="locator" xl:label="'+id_+'" xl:href="authored.xsd#'+id_+'"/>'+arc('hypercube-dimension','excludedcube0',id_)+arc('dimension-domain',id_,'domain')
  edited(e,0,schema.replace(b'</s:schema>',decl.encode()+b'</s:schema>'));edited(e,1,link.replace(b'</l:definitionLink>',extra.encode()+b'</l:definitionLink>'))
  with self.assertRaisesRegex(XBRLError,'dimension_budget_or_missing'):derive(e)
 def test_inline_original_lineage_and_negative_outcomes_are_preserved(self):
  from .test_inline_set import html,doc
  e=negative();raw=e['raw'].decode();resources=raw[raw.index('<x:context'):raw.index('<g:Assets')]
  page=html('<ix:nonFraction name="g:Assets" contextRef="I" unitRef="USD">1000</ix:nonFraction>',resources=True).decode();start=page.index('<x:context');end=page.index('</ix:resources>');page=(page[:start]+resources+page[end:]).replace('<html ','<html xmlns:d="http://xbrl.org/2006/xbrldi" ',1)
  original=doc('negative.xhtml',page.encode());c=FilingCollection('0000320193');c.ingest_inline_set_batch([{'documents':[original],'concepts':e['concepts'],'taxonomy_documents':e['documents']}],dimensional_profile=NEGATIVE_PROFILE)
  p=next(iter(c._filings.values()));self.assertEqual(p['schema'],'gig.sec.xbrl.dimensional_inline_set.v4');self.assertEqual(p['document_set']['documents'][0]['source']['source_sha256'],original['manifest']['source_sha256']);self.assertEqual(proof(p)['facts'][0]['assignments'][1]['kind'],'notAll');self.assertFalse(c.at_acceptance_time('2024-02-02T00:00:00Z')['history']['assets'])
 def test_v4_proof_relabeling_and_boolean_outcomes_are_not_trusted_after_rehash(self):
  p=derive()
  for kind in('schema','profile','drop','outcome','reason','defaults','kind','positive','closed','duplicate','complete','inherited'):
   bad=copy.deepcopy(p);bad.pop('canonical_sha256');v=proof(bad);r=v['facts'][0];n=r['assignments'][1]
   if kind=='schema':bad['schema']='gig.sec.xbrl.dimensional_instance.v3'
   elif kind=='profile':v['profile']=INHERITED_PROFILE
   elif kind=='drop':bad['dts_corroboration'].pop('dimensional_validation')
   elif kind=='outcome':n['hypercube_valid']=True
   elif kind=='reason':n['failure_reason']='drs_declaration_unsupported'
   elif kind=='defaults':n['used_defaults']={'{'+NS+'}ExcludedAxis':'{'+NS+'}South'}
   elif kind=='kind':n['kind']='unknown'
   elif kind=='positive':r['assignments'].pop(0)
   elif kind=='closed':n['failure_reason']='drs_closed_extra_dimension'
   elif kind=='duplicate':r['assignments'].append(copy.deepcopy(n))
   elif kind=='complete':v['complete_drs_validation']=True
   else:n['inherited']=not n['inherited']
   bad['canonical_sha256']=digest(bad)
   with self.subTest(kind=kind),self.assertRaisesRegex(XBRLError,'dimensional_result'):selected_financials(bad)
 def test_explicit_default_is_global_context_error_not_negative_satisfaction(self):
  e=negative(default=True,closed=True);link=e['documents'][1]['raw'].replace(arc('all','parent0','cube','xd:closed="true" xd:contextElement="segment"').encode(),arc('all','parent0','cube','xd:closed="false" xd:contextElement="segment"').encode());edited(e,1,link)
  extra=b'<d:explicitMember dimension="g:ExcludedAxis">g:South</d:explicitMember>';e['raw']=e['raw'].replace(b'</x:segment>',extra+b'</x:segment>');e['manifest']['source_sha256']=hashlib.sha256(e['raw']).hexdigest()
  with self.assertRaisesRegex(XBRLError,'explicit_default_member'):derive(e)
