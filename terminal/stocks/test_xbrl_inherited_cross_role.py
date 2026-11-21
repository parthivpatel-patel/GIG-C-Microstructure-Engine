"""Authored same-base inherited conjunction with exact cross-role cube paths."""
import copy,hashlib,re,unittest
from unittest.mock import patch
from .test_xbrl_cross_role import fixture as original,edited,inputs,ROLES,BASE,NS,derive as v7
from .test_xbrl_dimensions import arc
from .xbrl_dimensions import corroborate,INHERITED_CROSS_ROLE_PROFILE,CROSS_ROLE_PROFILE
from .xbrl_instance import selected_financials,digest,canonical,XBRLError
from .xbrl_collection import FilingCollection

def fixture(*,cubes=2,depth=2,inherited=True,member='North',default=False,diamond=False,**meta):
 e=original(member,default=default,**meta);decls='';locs='';primary='';all_arcs='';cube_arcs=''
 if inherited:
  for i in range(depth):
   id_='parent'+str(i);decls+='<s:element id="'+id_+'" name="Parent'+str(i)+'" substitutionGroup="x:item" abstract="true" type="x:monetaryItemType" x:periodType="instant"/>';locs+='<l:loc xl:type="locator" xl:label="'+id_+'" xl:href="authored.xsd#'+id_+'"/>';primary+=arc('domain-member',id_,'assets'if i==0 else'parent'+str(i-1))
  source='parent'+str(depth-1)
 else:source='assets'
 if diamond:
  decls+='<s:element id="peer" name="Peer" substitutionGroup="x:item" abstract="true" type="x:monetaryItemType" x:periodType="instant"/>';locs+='<l:loc xl:type="locator" xl:label="peer" xl:href="authored.xsd#peer"/>';primary+=arc('domain-member',source,'peer')+arc('domain-member','peer','assets')
 for i in range(1,cubes):
  id_='cube'+str(i);decls+='<s:element id="'+id_+'" name="Cube'+str(i)+'" substitutionGroup="xd:hypercubeItem" abstract="true" x:periodType="duration"/>';locs+='<l:loc xl:type="locator" xl:label="'+id_+'" xl:href="authored.xsd#'+id_+'"/>';all_arcs+=arc('all','assets',id_,'xd:closed="true" xd:contextElement="segment" xd:targetRole="'+ROLES[1]+'"');cube_arcs+=arc('hypercube-dimension',id_,'axis','xd:targetRole="'+ROLES[2]+'"')
 edited(e,0,e['documents'][0]['raw'].replace(b'</s:schema>',decls.encode()+b'</s:schema>'))
 raw=e['documents'][1]['raw'];old=arc('all','assets','cube','xd:closed="true" xd:contextElement="segment" xd:targetRole="'+ROLES[1]+'"').encode();raw=raw.replace(old,(arc('all',source,'cube','xd:closed="true" xd:contextElement="segment" xd:targetRole="'+ROLES[1]+'"')+primary+all_arcs).encode());needle=arc('hypercube-dimension','cube','axis','xd:targetRole="'+ROLES[2]+'"').encode();raw=raw.replace(needle,needle+cube_arcs.encode())
 # Each locator must be a child of its own extended link, never root-level metadata.
 raw=re.sub(b'(<l:definitionLink[^>]*>)',lambda m:m.group(0)+locs.encode(),raw);edited(e,1,raw);return e

def derive(e=None,**kw):
 e=fixture()if e is None else e;p,g=inputs(e,observed=e['manifest']['origin']=='OBSERVED_OFFICIAL_RESPONSE');return corroborate(p,g,profile=INHERITED_CROSS_ROLE_PROFILE,documents=e['documents'],instance_uri=e['instance_uri'],**kw)
def proof(p):return p['dts_corroboration']['dimensional_validation']
def rehash(p):p.pop('canonical_sha256',None);p['canonical_sha256']=digest(p)
def alternate_domain(e,member='south'):
 # The second cube's dimension enters a separate base containing a different root.
 a=arc('hypercube-dimension','cube1','axis','xd:targetRole="'+ROLES[2]+'"').encode();b=arc('hypercube-dimension','cube1','axis','xd:targetRole="'+ROLES[5]+'"').encode();locs=''.join('<l:loc xl:type="locator" xl:label="'+n+'" xl:href="authored.xsd#'+n+'"/>'for n in('axis','domain','north','south'));link='<l:definitionLink xl:type="extended" xl:role="'+ROLES[5]+'">'+locs+arc('dimension-domain','axis',member)+'</l:definitionLink>';edited(e,1,e['documents'][1]['raw'].replace(a,b).replace(b'</l:linkbase>',link.encode()+b'</l:linkbase>'));return e

class InheritedCrossRole(unittest.TestCase):
 def test_inherited_and_direct_cubes_conjoin_with_original_sources_unchanged(self):
  e=fixture();before=copy.deepcopy(e);p,g=inputs(e);out=derive(e);r=proof(out)['facts'][0]
  self.assertEqual(out['schema'],'gig.sec.xbrl.dimensional_instance.v8');self.assertEqual(proof(out)['profile'],INHERITED_CROSS_ROLE_PROFILE);self.assertFalse(proof(out)['complete_drs_validation']);self.assertEqual(r['status'],'VALIDATED_RESTRICTED_INHERITED_CROSS_ROLE_CONTEXT');self.assertEqual(r['role'],ROLES[0]);self.assertEqual(r['context_element'],'segment');self.assertEqual({a['inherited']for a in r['assignments']},{True,False});self.assertEqual(len(r['assignments']),2);self.assertEqual(r['primary_ancestors'],sorted(['{'+NS+'}Assets','{'+NS+'}Parent0','{'+NS+'}Parent1']));self.assertTrue(all(a['closed']for a in r['assignments']))
  for k in('source','facts','contexts','units'):self.assertEqual(out[k],p[k])
  self.assertEqual(e,before);self.assertEqual(out['canonical_sha256'],digest({k:v for k,v in out.items()if k!='canonical_sha256'}));self.assertFalse(selected_financials(out)['history']['assets'])
 def test_multiple_direct_positive_cubes_are_supported(self):
  p=derive(fixture(inherited=False,cubes=3));r=proof(p)['facts'][0];self.assertEqual(len(r['assignments']),3);self.assertTrue(all(not a['inherited']for a in r['assignments']))
 def test_one_inherited_assignment_has_no_fabricated_direct_edge(self):
  p=derive(fixture(cubes=1));r=proof(p)['facts'][0];self.assertEqual(len(r['assignments']),1);self.assertTrue(r['assignments'][0]['inherited']);self.assertNotEqual(r['assignments'][0]['primary_item'],p['facts'][0]['concept'])
 def test_diamond_inheritance_applies_shared_ancestor_once(self):
  r=proof(derive(fixture(cubes=1,diamond=True)))['facts'][0];self.assertEqual(len(r['assignments']),1);self.assertIn('{'+NS+'}Peer',r['primary_ancestors'])
 def test_second_cube_failure_cannot_be_ignored_or_selected_away(self):
  with self.assertRaisesRegex(XBRLError,'member_outside_domain'):derive(alternate_domain(fixture()))
 def test_cross_role_domain_paths_remain_exact_not_unioned(self):
  e=fixture(member='Leaf');self.assertEqual(len(proof(derive(e))['facts']),1);edited(e,1,e['documents'][1]['raw'].replace(('xd:targetRole="'+ROLES[4]+'"').encode(),b''))
  with self.assertRaisesRegex(XBRLError,'member_outside_domain'):derive(e)
 def test_same_global_default_is_merged_without_context_fact_synthesis(self):
  p=derive(fixture(member=None,default=True));r=proof(p)['facts'][0];d={'{'+NS+'}RegionAxis':'{'+NS+'}South'};self.assertEqual(r['used_defaults'],d);self.assertTrue(all(a['used_defaults']==d for a in r['assignments']));self.assertEqual(p['contexts']['I']['dimensions'],[]);self.assertFalse(selected_financials(p)['history']['assets'])
 def test_global_default_does_not_enter_another_domain_automatically(self):
  with self.assertRaisesRegex(XBRLError,'default_outside_selected_domain'):derive(alternate_domain(fixture(member=None,default=True),'north'))
 def test_reported_default_stays_invalid_for_every_conjunct(self):
  with self.assertRaisesRegex(XBRLError,'explicit_default_member'):derive(fixture(member='South',default=True))
 def test_conflicting_global_defaults_fail_before_acceptance(self):
  e=fixture(default=True);edited(e,1,e['documents'][1]['raw'].replace(b'</l:definitionLink></l:linkbase>',arc('dimension-default','axis','north').encode()+b'</l:definitionLink></l:linkbase>'))
  with self.assertRaisesRegex(XBRLError,'global_default_conflict'):derive(e)
 def test_alternative_has_hypercube_base_roles_are_not_implicitly_conjoined(self):
  e=fixture();needle=arc('all','assets','cube1','xd:closed="true" xd:contextElement="segment" xd:targetRole="'+ROLES[1]+'"').encode();raw=e['documents'][1]['raw'].replace(needle,b'');target=arc('hypercube-dimension','cube','axis','xd:targetRole="'+ROLES[2]+'"').encode();edited(e,1,raw.replace(target,target+needle))
  with self.assertRaisesRegex(XBRLError,'alternative_base_roles_unsupported'):derive(e)
 def test_cross_base_primary_inheritance_is_explicitly_unsupported(self):
  for change in('role','target'):
   e=fixture();a=arc('domain-member','parent0','assets').encode()
   if change=='target':raw=e['documents'][1]['raw'].replace(a,arc('domain-member','parent0','assets','xd:targetRole="'+ROLES[1]+'"').encode())
   else:
    raw=e['documents'][1]['raw'].replace(a,b'');needle=arc('domain-member','north','leaf').encode();raw=raw.replace(needle,needle+a)
   edited(e,1,raw)
   with self.subTest(change=change),self.assertRaisesRegex(XBRLError,'primary_inheritance_role_unsupported'):derive(e)
 def test_primary_cycles_are_not_hidden_by_a_valid_direct_assignment(self):
  e=fixture();needle=arc('domain-member','parent0','assets').encode();edited(e,1,e['documents'][1]['raw'].replace(needle,needle+arc('domain-member','assets','parent1').encode()))
  with self.assertRaisesRegex(XBRLError,'primary_cycle'):derive(e)
 def test_inherited_fact_itself_cannot_also_be_a_selected_domain_member(self):
  e=fixture();needle=arc('domain-member','domain','south').encode();edited(e,1,e['documents'][1]['raw'].replace(needle,needle+arc('domain-member','domain','assets').encode()))
  with self.assertRaisesRegex(XBRLError,'primary_item_polymorphism'):derive(e)
 def test_assignment_source_cannot_also_be_its_own_domain_member(self):
  e=fixture();needle=arc('domain-member','domain','south').encode();edited(e,1,e['documents'][1]['raw'].replace(needle,needle+arc('domain-member','domain','parent1').encode()))
  with self.assertRaisesRegex(XBRLError,'primary_item_polymorphism'):derive(e)
 def test_mixed_context_container_assignments_do_not_get_guessed(self):
  e=fixture();needle=arc('all','assets','cube1','xd:closed="true" xd:contextElement="segment" xd:targetRole="'+ROLES[1]+'"').encode();edited(e,1,e['documents'][1]['raw'].replace(needle,needle.replace(b'"segment"',b'"scenario"')))
  with self.assertRaisesRegex(XBRLError,'mixed_context_assignments_unsupported'):derive(e)
 def test_missing_or_invalid_domain_members_remain_unavailable(self):
  for member,reason in((None,'required_dimension_missing'),('Unknown','member_outside_domain')):
   with self.subTest(member=member),self.assertRaisesRegex(XBRLError,reason):derive(fixture(member=member))
 def test_legacy_v7_keeps_rejecting_multiple_and_inherited_scope(self):
  for e in(fixture(),fixture(cubes=1)):
   with self.assertRaises(XBRLError):v7(e)
 def test_prohibition_priority_negative_open_and_typed_remain_rejected(self):
  for old,new in((b'xd:closed="true"',b'xd:closed="false"'),(b'/arcrole/all',b'/arcrole/notAll'),(b'xl:to="cube1"',b'xl:to="cube1" priority="1"'),(b'xl:to="cube1"',b'xl:to="cube1" use="prohibited"'),(b'xd:targetRole="'+ROLES[4].encode()+b'"',b'xd:targetRole="'+ROLES[4].encode()+b'" xd:usable="false"')):
   e=fixture();edited(e,1,e['documents'][1]['raw'].replace(old,new))
   with self.subTest(new=new),self.assertRaises(XBRLError):derive(e)
  e=fixture();edited(e,0,e['documents'][0]['raw'].replace(b'name="RegionAxis"',b'name="RegionAxis" xd:typedDomainRef="#domain"'))
  with self.assertRaises(XBRLError):derive(e)
 def test_per_fact_assignment_limit_sixteen_accepts_seventeen_rejects(self):
  self.assertEqual(len(proof(derive(fixture(cubes=16)))['facts'][0]['assignments']),16)
  with self.assertRaisesRegex(XBRLError,'fact_assignment_budget'):derive(fixture(cubes=17))
 def test_global_assignment_budget_is_independent(self):
  with self.assertRaisesRegex(XBRLError,'assignment_budget'):derive(fixture(cubes=65))
 def test_primary_depth_limit_accepts_thirtyone_edges_and_rejects_next(self):
  self.assertEqual(len(proof(derive(fixture(cubes=1,depth=31)))['facts'][0]['primary_ancestors']),32)
  with self.assertRaisesRegex(XBRLError,'primary_depth'):derive(fixture(cubes=1,depth=32))
 def test_collection_batch_is_atomic_if_later_member_fails(self):
  c=FilingCollection('0000320193');c.ingest_dts_batch([fixture()],dimensional_profile=INHERITED_CROSS_ROLE_PROFILE);before=c.page()
  with self.assertRaises(XBRLError):c.ingest_dts_batch([fixture(accession='0000000123-24-000002'),fixture(member='Unknown',accession='0000000123-24-000003')],dimensional_profile=INHERITED_CROSS_ROLE_PROFILE)
  self.assertEqual(c.page(),before)
 def test_observed_processing_permission_precedes_original_xml(self):
  e=fixture(origin='OBSERVED_OFFICIAL_RESPONSE',permission_reference='authored-grant');base='https://www.sec.gov/Archives/edgar/data/320193/000000012324000001/';e['instance_uri']=e['manifest']['source_url']=base+'instance.xml'
  for d in e['documents']:d['uri']=d['uri'].replace(BASE,base)
  p,g=inputs(e,observed=True)
  with patch('terminal.stocks.xbrl_cross_role.parse_xml',side_effect=AssertionError('NO_XML'))as parser:
   with self.assertRaisesRegex(XBRLError,'not_approved'):corroborate(p,g,profile=INHERITED_CROSS_ROLE_PROFILE,documents=e['documents'],instance_uri=e['instance_uri'])
   parser.assert_not_called()
  self.assertEqual(len(proof(derive(e,allow_observed=True))['facts']),1)
 def test_original_hash_missing_duplicate_and_forged_graph_reject(self):
  e=fixture();p,g=inputs(e)
  for docs in(e['documents'][:1],e['documents']+[e['documents'][0]],copy.deepcopy(e['documents'])):
   if len(docs)==2:docs[1]['raw']+=b' '
   with self.subTest(count=len(docs)),self.assertRaises(XBRLError):corroborate(p,g,profile=INHERITED_CROSS_ROLE_PROFILE,documents=docs,instance_uri=e['instance_uri'])
  p,g=inputs(e);g['concepts']['{'+NS+'}North']['declaration']['abstract']=True;g.pop('canonical_sha256');g['canonical_sha256']=digest(g);p['dts_corroboration']['dts_sha256']=g['canonical_sha256'];p['dts_corroboration']['concept_declarations']=copy.deepcopy(g['concepts']);rehash(p)
  with self.assertRaisesRegex(XBRLError,'reconstructed_graph_mismatch'):corroborate(p,g,profile=INHERITED_CROSS_ROLE_PROFILE,documents=e['documents'],instance_uri=e['instance_uri'])
 def test_retained_inheritance_and_conjunction_claims_rederive_after_rehash(self):
  original=derive()
  for change in('drop','empty','profile','ancestor','missing_cube','duplicate_cube','primary','inherited','default','source','ordinal','role','relationship','reference'):
   p=copy.deepcopy(original);v=proof(p);r=v['facts'][0]
   if change=='drop':p['dts_corroboration'].pop('dimensional_validation')
   elif change=='empty':v['facts']=[]
   elif change=='profile':v['profile']=CROSS_ROLE_PROFILE
   elif change=='ancestor':r['primary_ancestors']=[]
   elif change=='missing_cube':r['assignments'].pop()
   elif change=='duplicate_cube':r['assignments'].append(copy.deepcopy(r['assignments'][0]))
   elif change=='primary':r['assignments'][0]['primary_item']='{'+NS+'}North'
   elif change=='inherited':r['assignments'][0]['inherited']=not r['assignments'][0]['inherited']
   elif change=='default':r['used_defaults']={'{'+NS+'}RegionAxis':'{'+NS+'}South'}
   elif change=='source':r['assignments'][0]['source_uri']='https://invented.invalid/'
   elif change=='ordinal':r['assignments'][0]['source_arc_node_ordinal']=1
   elif change=='role':r['role']=ROLES[1]
   elif change=='relationship':v['relationships'][0]['source_sha256']='0'*64
   else:v['role_references'][0]['schema_sha256']='0'*64
   rehash(p)
   with self.subTest(change=change),self.assertRaises(XBRLError):selected_financials(p)
 def test_malformed_retained_metadata_types_reject_as_xbrl_error(self):
  for change in('arcs','uri','reference','ord','closed','context'):
   p=derive();v=proof(p)
   if change=='arcs':v['relationships']={}
   elif change=='uri':v['relationships'][0]['source_uri']=[]
   elif change=='reference':v['role_references'][0]['role_type_uri']={}
   elif change=='ord':v['relationships'][0]['arc_node_ordinal']=True
   elif change=='closed':v['relationships'][0]['closed']=1
   else:p['contexts']['I']['dimensions']=True
   rehash(p)
   with self.subTest(change=change),self.assertRaises(XBRLError):selected_financials(p)
 def test_input_and_output_resource_failure_does_not_mutate_source(self):
  e=fixture();p,g=inputs(e);before=copy.deepcopy((p,g,e))
  with patch('terminal.stocks.xbrl_inherited_cross_role.MAX_OUTPUT',1),self.assertRaisesRegex(XBRLError,'output_budget'):corroborate(p,g,profile=INHERITED_CROSS_ROLE_PROFILE,documents=e['documents'],instance_uri=e['instance_uri'])
  self.assertEqual((p,g,e),before)
 def test_closed_cubes_validate_separately_not_against_the_union_of_axes(self):
  e=fixture();decl='<s:element id="otheraxis" name="OtherAxis" substitutionGroup="xd:dimensionItem" abstract="true" x:periodType="duration"/>';loc='<l:loc xl:type="locator" xl:label="otheraxis" xl:href="authored.xsd#otheraxis"/>';edited(e,0,e['documents'][0]['raw'].replace(b'</s:schema>',decl.encode()+b'</s:schema>'));raw=e['documents'][1]['raw'];old=arc('hypercube-dimension','cube1','axis','xd:targetRole="'+ROLES[2]+'"').encode();raw=raw.replace(old,arc('hypercube-dimension','cube1','otheraxis','xd:targetRole="'+ROLES[2]+'"').encode());needle=arc('dimension-domain','axis','domain','xd:targetRole="'+ROLES[3]+'"').encode();raw=raw.replace(needle,needle+arc('dimension-domain','otheraxis','domain','xd:targetRole="'+ROLES[3]+'"').encode());raw=re.sub(b'(<l:definitionLink[^>]*>)',lambda m:m.group(0)+loc.encode(),raw);edited(e,1,raw);e['raw']=e['raw'].replace(b'</x:segment>',b'<d:explicitMember dimension="g:OtherAxis">g:North</d:explicitMember></x:segment>');e['manifest']['source_sha256']=hashlib.sha256(e['raw']).hexdigest()
  with self.assertRaisesRegex(XBRLError,'closed_extra_dimension'):derive(e)
 def test_different_implicit_axes_merge_only_after_each_cube_validates(self):
  e=fixture(member=None,default=True);decl='<s:element id="otheraxis" name="OtherAxis" substitutionGroup="xd:dimensionItem" abstract="true" x:periodType="duration"/>';loc='<l:loc xl:type="locator" xl:label="otheraxis" xl:href="authored.xsd#otheraxis"/>';edited(e,0,e['documents'][0]['raw'].replace(b'</s:schema>',decl.encode()+b'</s:schema>'));raw=e['documents'][1]['raw'];old=arc('hypercube-dimension','cube1','axis','xd:targetRole="'+ROLES[2]+'"').encode();raw=raw.replace(old,arc('hypercube-dimension','cube1','otheraxis','xd:targetRole="'+ROLES[2]+'"').encode());needle=arc('dimension-domain','axis','domain','xd:targetRole="'+ROLES[3]+'"').encode();raw=raw.replace(needle,needle+arc('dimension-domain','otheraxis','domain','xd:targetRole="'+ROLES[3]+'"').encode());needle=arc('dimension-default','axis','south').encode();raw=raw.replace(needle,needle+arc('dimension-default','otheraxis','south').encode());raw=re.sub(b'(<l:definitionLink[^>]*>)',lambda m:m.group(0)+loc.encode(),raw);edited(e,1,raw);out=derive(e);r=proof(out)['facts'][0];self.assertEqual(r['used_defaults'],{'{'+NS+'}OtherAxis':'{'+NS+'}South','{'+NS+'}RegionAxis':'{'+NS+'}South'});self.assertTrue(all(len(a['used_defaults'])==1 for a in r['assignments']));self.assertEqual(out['contexts']['I']['dimensions'],[]);self.assertFalse(selected_financials(out)['history']['assets'])
 def test_two_document_inline_collection_uses_original_inherited_provenance(self):
  from .test_inline_set import html,doc
  e=fixture(member=None,default=True);raw=e['raw'].decode();resources=raw[raw.index('<x:context'):raw.index('<g:Assets')];page=html('',resources=True).decode();start=page.index('<x:context');end=page.index('</ix:resources>');page=(page[:start]+resources+page[end:]).replace('<html ','<html xmlns:d="http://xbrl.org/2006/xbrldi" ',1);originals=[doc('resources.xhtml',page.encode()),doc('facts.xhtml',html('<ix:nonFraction name="g:Assets" contextRef="I" unitRef="USD">1000</ix:nonFraction>'))];before=copy.deepcopy(originals);c=FilingCollection('0000320193');c.ingest_inline_set_batch([{'documents':originals,'concepts':e['concepts'],'taxonomy_documents':e['documents']}],dimensional_profile=INHERITED_CROSS_ROLE_PROFILE);out=next(iter(c._filings.values()));r=proof(out)['facts'][0]
  self.assertEqual(out['schema'],'gig.sec.xbrl.dimensional_inline_set.v8');self.assertEqual(len(out['document_set']['documents']),2);self.assertEqual({a['inherited']for a in r['assignments']},{True,False});self.assertTrue(r['used_defaults']);self.assertEqual(originals,before);self.assertFalse(selected_financials(out)['history']['assets'])
 def test_semantic_conjunction_is_independent_of_authored_assignment_order(self):
  e=fixture();a=arc('all','parent1','cube','xd:closed="true" xd:contextElement="segment" xd:targetRole="'+ROLES[1]+'"').encode();b=arc('all','assets','cube1','xd:closed="true" xd:contextElement="segment" xd:targetRole="'+ROLES[1]+'"').encode();first=derive(e);raw=e['documents'][1]['raw'];raw=raw.replace(a,b'').replace(b,b+a);edited(e,1,raw);second=derive(e)
  def claims(p):
   r=copy.deepcopy(proof(p)['facts'][0])
   for v in r['assignments']:v.pop('source_arc_node_ordinal')
   return r
  self.assertEqual(claims(first),claims(second));ordinal=lambda p:next(a['arc_node_ordinal']for a in proof(p)['relationships']if a['kind']=='all'and a['from']=='{'+NS+'}Parent1');self.assertNotEqual(ordinal(first),ordinal(second))
 def test_source_context_and_role_proof_corruptions_remain_fail_closed(self):
  for change in('context','role_ref','declaration','missing_parent'):
   p=derive();v=proof(p)
   if change=='context':p['contexts']['I']['semantic_sha256']='0'*64
   elif change=='role_ref':v['role_references']=[]
   elif change=='declaration':p['dts_corroboration']['concept_declarations']['{'+NS+'}Parent1']['declaration']['substitution_group']='{'+NS+'}invented'
   else:v['relationships']=[a for a in v['relationships']if not(a['kind']=='domain-member'and a['from']=='{'+NS+'}Parent0'and a['to']=='{'+NS+'}Assets')]
   rehash(p)
   with self.subTest(change=change),self.assertRaises(XBRLError):selected_financials(p)

 def test_global_traversal_budgets_fail_separately_and_preserve_originals(self):
  e=fixture();before=copy.deepcopy(e)
  for constant,code in(('MAX_DOMAIN_STATES','total_domain_state_budget'),('MAX_PRIMARY_STATES','total_primary_state_budget')):
   with self.subTest(constant=constant),patch('terminal.stocks.xbrl_inherited_cross_role.'+constant,1),self.assertRaisesRegex(XBRLError,code):derive(e)
  self.assertEqual(e,before)
 def test_multiple_selected_facts_bind_their_own_inherited_assignment_sets(self):
  e=fixture();decl='<s:element id="liabilities" name="Liabilities" substitutionGroup="x:item" type="x:monetaryItemType" x:periodType="instant"/>';loc='<l:loc xl:type="locator" xl:label="liabilities" xl:href="authored.xsd#liabilities"/>';edited(e,0,e['documents'][0]['raw'].replace(b'</s:schema>',decl.encode()+b'</s:schema>'));raw=re.sub(b'(<l:definitionLink[^>]*>)',lambda m:m.group(0)+loc.encode(),e['documents'][1]['raw']);a=arc('domain-member','parent0','assets').encode();raw=raw.replace(a,a+arc('domain-member','parent0','liabilities').encode());edited(e,1,raw);e['raw']=e['raw'].replace(b'</x:xbrl>',b'<g:Liabilities contextRef="I" unitRef="USD">500</g:Liabilities></x:xbrl>');e['manifest']['source_sha256']=hashlib.sha256(e['raw']).hexdigest();p,g=inputs(e);out=derive(e);records=proof(out)['facts'];facts={f['source_fact_id']:f for f in out['facts']}
  self.assertEqual(out['facts'],p['facts']);self.assertEqual(len(records),2);self.assertEqual({facts[r['source_fact_id']]['concept']:len(r['assignments'])for r in records},{'{'+NS+'}Assets':2,'{'+NS+'}Liabilities':1});self.assertFalse(selected_financials(out)['history']['assets']);self.assertFalse(selected_financials(out)['history']['liabilities'])
 def test_distinct_relationships_cannot_claim_one_original_arc_node(self):
  p=derive();v=proof(p);arcs=[a for a in v['relationships']if a['kind']=='domain-member'and a['role']==ROLES[3]];self.assertGreaterEqual(len(arcs),2);self.assertEqual(arcs[0]['link_node_ordinal'],arcs[1]['link_node_ordinal']);arcs[1]['arc_node_ordinal']=arcs[0]['arc_node_ordinal'];rehash(p)
  with self.assertRaisesRegex(XBRLError,'dimensional_result_contract'):selected_financials(p)
 def test_one_original_extended_link_node_cannot_claim_conflicting_roles(self):
  p=derive();v=proof(p);a=next(a for a in v['relationships']if a['role']==ROLES[4]);b=next(a for a in v['relationships']if a['role']==ROLES[3]);self.assertGreater(a['arc_node_ordinal'],b['link_node_ordinal']);a['link_node_ordinal']=b['link_node_ordinal'];rehash(p)
  with self.assertRaisesRegex(XBRLError,'dimensional_result_contract'):selected_financials(p)
 def test_one_original_role_type_node_cannot_have_conflicting_uri_identity(self):
  p=derive();v=proof(p);a,b=v['role_references'][:2];self.assertEqual(a['role_type_uri'].rsplit('#',1)[0],b['role_type_uri'].rsplit('#',1)[0]);self.assertNotEqual(a['role'],b['role']);b['role_type_node_ordinal']=a['role_type_node_ordinal'];rehash(p)
  with self.assertRaisesRegex(XBRLError,'dimensional_result_contract'):selected_financials(p)
 def test_original_role_type_reused_by_two_linkbases_remains_valid(self):
  e=fixture();raw=e['documents'][1]['raw'];links=list(re.finditer(b'<l:definitionLink\\b[^>]*>.*?</l:definitionLink>',raw));leaf=next(m.group(0)for m in links if ('xl:role="'+ROLES[4]+'"').encode()in m.group(0));header=raw[:raw.index(b'<l:definitionLink')];tail=header+leaf+b'</l:linkbase>';edited(e,1,raw.replace(leaf,b''));e['documents'].append({'uri':BASE+'dimensions-tail.xml','raw':tail,'sha256':hashlib.sha256(tail).hexdigest()});reference='<s:annotation><s:appinfo><l:linkbaseRef xl:type="simple" xl:href="dimensions-tail.xml"/></s:appinfo></s:annotation>';edited(e,0,e['documents'][0]['raw'].replace(b'</s:schema>',reference.encode()+b'</s:schema>'));out=derive(e);refs=proof(out)['role_references'];role_refs=[r for r in refs if r['role']==ROLES[0]];self.assertEqual(len(role_refs),2);self.assertNotEqual(role_refs[0]['source_uri'],role_refs[1]['source_uri']);self.assertEqual(role_refs[0]['role_type_node_ordinal'],role_refs[1]['role_type_node_ordinal']);self.assertEqual(role_refs[0]['role_type_uri'],role_refs[1]['role_type_uri']);self.assertFalse(selected_financials(out)['history']['assets'])
 def test_role_type_uri_cannot_resolve_to_two_original_nodes_after_rehash(self):
  out=derive();v=proof(out);a=copy.deepcopy(v['role_references'][0]);a['role_type_node_ordinal']=max(r['role_type_node_ordinal']for r in v['role_references'])+1000;a['source_uri']=BASE+'second-linkbase.xml';a['source_sha256']='1'*64;out['dts_corroboration']['documents'].append({'uri':a['source_uri'],'sha256':a['source_sha256'],'kind':'linkbase'});v['role_references'].append(a);v['role_references'].sort(key=lambda r:(r['source_uri'],r['role']));rehash(out)
  with self.assertRaisesRegex(XBRLError,'dimensional_result_contract'):selected_financials(out)
