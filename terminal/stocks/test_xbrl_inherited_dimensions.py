"""Authored positive-cube conjunction and transitive inheritance source graphs."""
import copy,hashlib,unittest
from .test_xbrl_dimensions import entry,arc,NS
from .test_xbrl_open_dimensions import edited
from .xbrl_instance import parse_instance,selected_financials,digest,XBRLError
from .xbrl_dts import discover
from .xbrl_binding import bind_declarations
from .xbrl_dimensions import PROFILE,OPEN_PROFILE,INHERITED_PROFILE,corroborate
from .xbrl_collection import FilingCollection

def inherited(*,depth=2,cubes=2,member='North',default=False,diamond=False,closed=True):
 e=entry(member,default=default,all_attrs='xd:closed="'+str(closed).lower()+'" xd:contextElement="segment"')
 schema=e['documents'][0]['raw'];link=e['documents'][1]['raw'];declarations='';locators='';extra=''
 for i in range(depth):
  name='Parent'+str(i);id_='parent'+str(i)
  declarations+='<s:element id="'+id_+'" name="'+name+'" substitutionGroup="x:item" abstract="true" x:periodType="instant"/>'
  locators+='<l:loc xl:type="locator" xl:label="'+id_+'" xl:href="authored.xsd#'+id_+'"/>'
  extra+=arc('domain-member',id_,'parent'+str(i+1)if i+1<depth else'assets')
 if depth:
  link=link.replace(b'xl:from="assets"',b'xl:from="parent0"')
 if diamond:
  declarations+='<s:element id="branch" name="Branch" substitutionGroup="x:item" abstract="true" x:periodType="instant"/>'
  locators+='<l:loc xl:type="locator" xl:label="branch" xl:href="authored.xsd#branch"/>'
  extra+=arc('domain-member','parent0','branch')+arc('domain-member','branch','assets')
 for i in range(1,cubes):
  id_='cube'+str(i);declarations+='<s:element id="'+id_+'" name="Cube'+str(i)+'" substitutionGroup="xd:hypercubeItem" abstract="true" x:periodType="duration"/>'
  locators+='<l:loc xl:type="locator" xl:label="'+id_+'" xl:href="authored.xsd#'+id_+'"/>'
  extra+=arc('all','assets',id_,'xd:closed="'+str(closed).lower()+'" xd:contextElement="segment"')+arc('hypercube-dimension',id_,'axis')
 edited(e,0,schema.replace(b'</s:schema>',declarations.encode()+b'</s:schema>'))
 edited(e,1,link.replace(b'</l:definitionLink>',(locators+extra).encode()+b'</l:definitionLink>'))
 return e

def derive(e=None,profile=INHERITED_PROFILE):
 e=inherited()if e is None else e;p=parse_instance(e['raw'],e['manifest'],e['concepts']);d=discover(e['raw'],e['instance_uri'],e['manifest']['source_sha256'],e['documents']);return corroborate(bind_declarations(p,d),d,profile=profile)
def proof(p):return p['dts_corroboration']['dimensional_validation']

class InheritedDimensions(unittest.TestCase):
 def test_transitive_and_direct_assignments_are_both_required_with_original_roots(self):
  e=inherited();original=copy.deepcopy(e);p=derive(e);r=proof(p)['facts'][0]
  self.assertEqual(p['schema'],'gig.sec.xbrl.dimensional_instance.v3');self.assertFalse(proof(p)['complete_drs_validation']);self.assertEqual(proof(p)['profile'],INHERITED_PROFILE)
  self.assertEqual(len(r['assignments']),2);self.assertEqual({a['primary_item']for a in r['assignments']},{'{'+NS+'}Parent0','{'+NS+'}Assets'});self.assertEqual({a['inherited']for a in r['assignments']},{True,False});self.assertNotIn('hypercube',r);self.assertEqual(e,original)
 def test_diamond_inheritance_applies_shared_ancestor_assignment_once(self):
  p=derive(inherited(cubes=1,diamond=True));assignments=proof(p)['facts'][0]['assignments'];self.assertEqual(len(assignments),1);self.assertTrue(assignments[0]['inherited'])
 def test_all_positive_cubes_must_validate_instead_of_selecting_a_usable_one(self):
  e=inherited();raw=e['documents'][1]['raw'].replace(arc('hypercube-dimension','cube1','axis').encode(),arc('hypercube-dimension','cube1','leaf').encode());edited(e,1,raw)
  with self.assertRaisesRegex(XBRLError,'closed_extra_dimension'):derive(e)
 def test_defaults_are_aggregated_without_synthesizing_contexts(self):
  p=derive(inherited(member=None,default=True));r=proof(p)['facts'][0];expected={'{'+NS+'}RegionAxis':'{'+NS+'}South'};self.assertEqual(r['used_defaults'],expected);self.assertTrue(all(a['used_defaults']==expected for a in r['assignments']));self.assertEqual(p['contexts']['I']['dimensions'],[])
 def test_legacy_profiles_keep_rejecting_multiple_or_inherited_scope(self):
  for profile in(PROFILE,OPEN_PROFILE):
   with self.assertRaisesRegex(XBRLError,'single_positive_assignment_required'):derive(inherited(),profile)
   with self.assertRaisesRegex(XBRLError,'direct_closed_assignment_required'):derive(inherited(cubes=1),profile)
 def test_primary_inheritance_cycle_is_not_silently_collapsed(self):
  e=inherited(cubes=1);edited(e,1,e['documents'][1]['raw'].replace(b'</l:definitionLink>',arc('domain-member','assets','parent0').encode()+b'</l:definitionLink>'))
  with self.assertRaisesRegex(XBRLError,'primary_item_cycle'):derive(e)
 def test_primary_inheritance_depth_is_bounded(self):
  with self.assertRaisesRegex(XBRLError,'primary_item_depth'):derive(inherited(depth=32,cubes=1))
 def test_sixteen_applicable_assignments_are_accepted_seventeen_reject(self):
  self.assertEqual(len(proof(derive(inherited(cubes=16)))['facts'][0]['assignments']),16)
  with self.assertRaisesRegex(XBRLError,'fact_assignment_budget'):derive(inherited(cubes=17))
 def test_duplicate_positive_relationships_are_explicitly_unsupported(self):
  e=inherited(cubes=1);edited(e,1,e['documents'][1]['raw'].replace(b'</l:definitionLink>',arc('all','parent0','cube','xd:closed="true" xd:contextElement="segment"').encode()+b'</l:definitionLink>'))
  with self.assertRaisesRegex(XBRLError,'duplicate_positive_assignment'):derive(e)
 def test_negative_typed_crossrole_and_priority_semantics_still_reject(self):
  for change in(arc('notAll','assets','cube','xd:contextElement="segment"'),arc('domain-member','parent0','assets','xd:targetRole="urn:other"'),arc('domain-member','parent0','assets','priority="1"')):
   e=inherited(cubes=1);edited(e,1,e['documents'][1]['raw'].replace(b'</l:definitionLink>',change.encode()+b'</l:definitionLink>'))
   with self.assertRaises(XBRLError):derive(e)
  e=inherited();edited(e,0,e['documents'][0]['raw'].replace(b'name="RegionAxis"',b'xd:typedDomainRef="#domain" name="RegionAxis"'))
  with self.assertRaisesRegex(XBRLError,'declaration_unsupported'):derive(e)
 def test_mixed_context_assignments_are_explicitly_outside_profile(self):
  e=inherited();old=arc('all','assets','cube1','xd:closed="true" xd:contextElement="segment"');new=arc('all','assets','cube1','xd:closed="true" xd:contextElement="scenario"');edited(e,1,e['documents'][1]['raw'].replace(old.encode(),new.encode()))
  with self.assertRaisesRegex(XBRLError,'mixed_context_assignments'):derive(e)
 def test_unrelated_positive_assignment_does_not_validate_a_fact(self):
  e=inherited(depth=0,cubes=1);edited(e,1,e['documents'][1]['raw'].replace(b'xl:from="assets"',b'xl:from="leaf"'))
  with self.assertRaisesRegex(XBRLError,'positive_assignment_required'):derive(e)
 def test_primary_item_cannot_also_be_in_its_assigned_dimension_domain(self):
  e=inherited(cubes=1);edited(e,1,e['documents'][1]['raw'].replace(b'</l:definitionLink>',arc('domain-member','domain','parent0').encode()+b'</l:definitionLink>'))
  with self.assertRaisesRegex(XBRLError,'primary_item_polymorphism'):derive(e)
 def test_direct_single_cube_v3_is_distinct_without_changing_v2(self):
  e=inherited(depth=0,cubes=1);p=derive(e);self.assertFalse(proof(p)['facts'][0]['assignments'][0]['inherited']);self.assertEqual(derive(e,OPEN_PROFILE)['schema'],'gig.sec.xbrl.dimensional_instance.v2')
 def test_collection_admission_is_atomic_and_defaults_are_not_consolidated(self):
  c=FilingCollection('0000320193');c.ingest_dts_batch([inherited(member=None,default=True)],dimensional_profile=INHERITED_PROFILE);before=c.page();self.assertFalse(c.at_acceptance_time('2024-02-02T00:00:00Z')['history']['assets'])
  bad=inherited(member='Leaf');bad['manifest']['accession']='0000000123-24-000002'
  with self.assertRaisesRegex(XBRLError,'member_outside_domain'):c.ingest_dts_batch([bad],dimensional_profile=INHERITED_PROFILE)
  self.assertEqual(c.page(),before)
 def test_two_open_cubes_require_both_separately_declared_axes(self):
  e=inherited(closed=False);extra='<s:element id="other" name="OtherAxis" substitutionGroup="xd:dimensionItem" abstract="true" x:periodType="duration"/>'
  edited(e,0,e['documents'][0]['raw'].replace(b'</s:schema>',extra.encode()+b'</s:schema>'))
  link=e['documents'][1]['raw'].replace(arc('hypercube-dimension','cube1','axis').encode(),arc('hypercube-dimension','cube1','other').encode())
  extra='<l:loc xl:type="locator" xl:label="other" xl:href="authored.xsd#other"/>'+arc('dimension-domain','other','domain')
  edited(e,1,link.replace(b'</l:definitionLink>',extra.encode()+b'</l:definitionLink>'))
  member=b'<d:explicitMember dimension="g:OtherAxis">g:North</d:explicitMember>';e['raw']=e['raw'].replace(b'</x:segment>',member+b'</x:segment>');e['manifest']['source_sha256']=hashlib.sha256(e['raw']).hexdigest()
  p=derive(e);assignments=proof(p)['facts'][0]['assignments'];self.assertEqual({tuple(a['extra_dimensions'])for a in assignments},{('{'+NS+'}OtherAxis',),('{'+NS+'}RegionAxis',)})
  for omitted in(member,b'<d:explicitMember dimension="g:RegionAxis">g:North</d:explicitMember>'):
   bad=copy.deepcopy(e);bad['raw']=bad['raw'].replace(omitted,b'');bad['manifest']['source_sha256']=hashlib.sha256(bad['raw']).hexdigest()
   with self.assertRaisesRegex(XBRLError,'required_dimension_missing'):derive(bad)
 def test_inline_original_provenance_survives_inherited_dimensional_derivation(self):
  from .test_inline_set import html,doc
  e=inherited();raw=e['raw'].decode();resources=raw[raw.index('<x:context'):raw.index('<g:Assets')]
  page=html('<ix:nonFraction name="g:Assets" contextRef="I" unitRef="USD">1000</ix:nonFraction>',resources=True).decode();start=page.index('<x:context');end=page.index('</ix:resources>');page=(page[:start]+resources+page[end:]).replace('<html ','<html xmlns:d="http://xbrl.org/2006/xbrldi" ',1)
  original=doc('inherited.xhtml',page.encode());c=FilingCollection('0000320193');c.ingest_inline_set_batch([{'documents':[original],'concepts':e['concepts'],'taxonomy_documents':e['documents']}],dimensional_profile=INHERITED_PROFILE)
  parsed=next(iter(c._filings.values()));self.assertEqual(parsed['schema'],'gig.sec.xbrl.dimensional_inline_set.v3');self.assertEqual(parsed['document_set']['documents'][0]['source']['source_sha256'],original['manifest']['source_sha256']);self.assertEqual(len(proof(parsed)['facts'][0]['assignments']),2)
 def test_v3_proof_identity_and_assignment_structure_rejects_relabeling(self):
  p=derive(inherited(member=None,default=True))
  for kind in('schema','profile','drop','aggregate','count','bool','context','primary','duplicate','claim'):
   bad=copy.deepcopy(p);bad.pop('canonical_sha256');v=proof(bad);r=v['facts'][0]
   if kind=='schema':bad['schema']='gig.sec.xbrl.dimensional_instance.v2'
   elif kind=='profile':v['profile']=OPEN_PROFILE
   elif kind=='drop':bad['dts_corroboration'].pop('dimensional_validation')
   elif kind=='aggregate':r['used_defaults']={}
   elif kind=='count':r['assignments']*=9
   elif kind=='bool':r['assignments'][0]['inherited']=1
   elif kind=='context':r['assignments'][0]['context_element']='scenario'
   elif kind=='primary':r['assignments'][0]['primary_item']='not-an-expanded-name'
   elif kind=='duplicate':r['assignments'].append(copy.deepcopy(r['assignments'][0]))
   else:r['assignments'][0]['inherited']=not r['assignments'][0]['inherited']
   bad['canonical_sha256']=digest(bad)
   with self.subTest(kind=kind),self.assertRaisesRegex(XBRLError,'dimensional_result'):selected_financials(bad)

 def test_repeated_primary_cube_pair_with_distinct_attributes_is_unsupported(self):
  e=inherited(cubes=1);edited(e,1,e['documents'][1]['raw'].replace(b'</l:definitionLink>',arc('all','parent0','cube','xd:closed="false" xd:contextElement="segment"').encode()+b'</l:definitionLink>'))
  with self.assertRaisesRegex(XBRLError,'duplicate_positive_assignment'):derive(e)
 def test_network_positive_assignment_budget_is_bounded_before_fact_evaluation(self):
  with self.assertRaisesRegex(XBRLError,'positive_assignment_budget'):derive(inherited(cubes=65))
 def test_combined_defaulted_axis_union_across_cubes_is_bounded(self):
  e=inherited(member=None,default=True);schema=e['documents'][0]['raw'];link=e['documents'][1]['raw'].replace(arc('hypercube-dimension','cube1','axis').encode(),b'');declarations='';extra=''
  for i in range(32):
   id_='extra'+str(i);declarations+='<s:element id="'+id_+'" name="ExtraAxis'+str(i)+'" substitutionGroup="xd:dimensionItem" abstract="true" x:periodType="duration"/>'
   extra+='<l:loc xl:type="locator" xl:label="'+id_+'" xl:href="authored.xsd#'+id_+'"/>'+arc('hypercube-dimension','cube1',id_)+arc('dimension-domain',id_,'domain')+arc('dimension-default',id_,'south')
  edited(e,0,schema.replace(b'</s:schema>',declarations.encode()+b'</s:schema>'));edited(e,1,link.replace(b'</l:definitionLink>',extra.encode()+b'</l:definitionLink>'))
  with self.assertRaisesRegex(XBRLError,'dimension_budget'):derive(e)
