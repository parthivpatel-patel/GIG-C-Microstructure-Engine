"""Authored original-byte cross-role fixtures and independent expected memberships."""
import copy,hashlib,unittest
from unittest.mock import patch
from .test_xbrl_dimensions import entry,arc,D
from .test_xbrl_binding import BASE
from .test_xbrl_instance import NS,manifest,selected_concepts
from .xbrl_instance import parse_instance,selected_financials,canonical,digest,XBRLError
from .xbrl_dts import discover
from .xbrl_binding import bind_declarations
from .xbrl_dimensions import corroborate,CROSS_ROLE_PROFILE,PROFILE,TYPED_PROFILE
from .xbrl_collection import FilingCollection
from .xbrl_cross_role import STANDARD
ROLES=['urn:authored:assignment','urn:authored:cube','urn:authored:axis','urn:authored:domain','urn:authored:leaf','urn:authored:defaults']
def edited(e,i,raw):e['documents'][i]={'uri':e['documents'][i]['uri'],'raw':raw,'sha256':hashlib.sha256(raw).hexdigest()}
def fixture(member='North',*,default=False,**metadata):
 e=entry(member,**metadata)
 types=''.join('<l:roleType id="role'+str(i)+'" roleURI="'+r+'"><l:usedOn>l:definitionLink</l:usedOn></l:roleType>'for i,r in enumerate(ROLES))
 edited(e,0,e['documents'][0]['raw'].replace(b'</s:schema>',('<s:annotation><s:appinfo>'+types+'</s:appinfo></s:annotation></s:schema>').encode()))
 locators=''.join('<l:loc xl:type="locator" xl:label="'+n+'" xl:href="authored.xsd#'+n+'"/>'for n in('assets','cube','axis','domain','north','south','leaf'))
 def link(i,body):return '<l:definitionLink xl:type="extended" xl:role="'+ROLES[i]+'">'+locators+body+'</l:definitionLink>'
 target=lambda i:'xd:targetRole="'+ROLES[i]+'"'
 links=link(0,arc('all','assets','cube','xd:closed="true" xd:contextElement="segment" '+target(1)))+link(1,arc('hypercube-dimension','cube','axis',target(2)))+link(2,arc('dimension-domain','axis','domain',target(3)))+link(3,arc('domain-member','domain','north',target(4))+arc('domain-member','domain','south'))+link(4,arc('domain-member','north','leaf'))+(link(5,arc('dimension-default','axis','south'))if default else'')
 refs=''.join('<l:roleRef roleURI="'+r+'" xl:type="simple" xl:href="authored.xsd#role'+str(i)+'"/>'for i,r in enumerate(ROLES))
 raw=('<l:linkbase xmlns:l="http://www.xbrl.org/2003/linkbase" xmlns:xl="http://www.w3.org/1999/xlink" xmlns:xd="'+D+'">'+refs+links+'</l:linkbase>').encode();edited(e,1,raw);return e

def inputs(e,*,observed=False):
 p=parse_instance(e['raw'],e['manifest'],e['concepts'],allow_observed=observed)
 g=discover(e['raw'],e['instance_uri'],e['manifest']['source_sha256'],e['documents'],origin=e['manifest']['origin'],permission_reference=e['manifest']['permission_reference'],allow_observed=observed)
 return bind_declarations(p,g),g

def derive(e=None,**kw):
 e=fixture()if e is None else e;p,g=inputs(e,observed=e['manifest']['origin']=='OBSERVED_OFFICIAL_RESPONSE')
 return corroborate(p,g,profile=CROSS_ROLE_PROFILE,documents=e['documents'],instance_uri=e['instance_uri'],**kw)
def proof(p):return p['dts_corroboration']['dimensional_validation']
def rehash(p):p.pop('canonical_sha256',None);p['canonical_sha256']=digest(p)
class CrossRole(unittest.TestCase):
 def test_valid_chain_preserves_original_inputs_values_contexts_and_source_ids(self):
  e=fixture();before=copy.deepcopy(e);p,g=inputs(e);out=derive(e);r=proof(out)['facts'][0]
  self.assertEqual(out['schema'],'gig.sec.xbrl.dimensional_instance.v7');self.assertEqual(proof(out)['profile'],CROSS_ROLE_PROFILE);self.assertFalse(proof(out)['complete_drs_validation']);self.assertEqual(r['role'],ROLES[0]);self.assertEqual(r['status'],'VALIDATED_RESTRICTED_CROSS_ROLE_CONTEXT');self.assertEqual(r['used_defaults'],{});self.assertEqual(e,before)
  for k in('facts','contexts','units','source'):self.assertEqual(out[k],p[k])
  self.assertEqual(out['canonical_sha256'],digest({k:v for k,v in out.items()if k!='canonical_sha256'}));self.assertEqual(len(proof(out)['role_references']),6);self.assertFalse(selected_financials(out)['history']['assets'])
 def test_cross_role_descendant_is_valid_member(self):self.assertEqual(len(proof(derive(fixture('Leaf')))['facts']),1)
 def test_target_role_replaces_source_role_not_union(self):
  e=fixture('Leaf');edited(e,1,e['documents'][1]['raw'].replace(('xd:targetRole="'+ROLES[4]+'"').encode(),b''))
  with self.assertRaisesRegex(XBRLError,'member_outside_domain'):derive(e)
 def test_missing_target_role_link_cannot_fall_back_to_source_role(self):
  e=fixture();edited(e,1,e['documents'][1]['raw'].replace(('xd:targetRole="'+ROLES[1]+'"').encode(),b''))
  with self.assertRaisesRegex(XBRLError,'dimension_budget_or_missing'):derive(e)
 def test_global_default_from_another_role_is_used_without_synthesis(self):
  e=fixture(None,default=True);p=derive(e);self.assertEqual(proof(p)['facts'][0]['used_defaults'],{'{'+NS+'}RegionAxis':'{'+NS+'}South'});self.assertEqual(p['contexts']['I']['dimensions'],[]);self.assertFalse(selected_financials(p)['history']['assets'])
 def test_default_from_other_role_is_never_allowed_explicitly(self):
  with self.assertRaisesRegex(XBRLError,'explicit_default_member'):derive(fixture('South',default=True))
 def test_conflicting_global_defaults_reject(self):
  e=fixture(default=True);edited(e,1,e['documents'][1]['raw'].replace(b'</l:definitionLink></l:linkbase>',arc('dimension-default','axis','north').encode()+b'</l:definitionLink></l:linkbase>'))
  with self.assertRaisesRegex(XBRLError,'global_default_conflict'):derive(e)
 def test_default_must_belong_to_selected_cross_role_domain(self):
  e=fixture(None,default=True);edited(e,1,e['documents'][1]['raw'].replace(arc('domain-member','domain','south').encode(),b''))
  with self.assertRaisesRegex(XBRLError,'default_outside_selected_domain'):derive(e)
 def test_unknown_and_missing_members_preserve_explicit_failure(self):
  for e,reason in((fixture('Unknown'),'member_outside_domain'),(fixture(None),'required_dimension_missing')):
   with self.subTest(reason=reason),self.assertRaisesRegex(XBRLError,reason):derive(e)
 def test_cross_role_cycle_rejects_even_when_state_roles_differ(self):
  e=fixture('Leaf');edited(e,1,e['documents'][1]['raw'].replace(arc('domain-member','north','leaf').encode(),(arc('domain-member','north','leaf')+arc('domain-member','leaf','domain','xd:targetRole="'+ROLES[5]+'"')).encode()))
  with self.assertRaisesRegex(XBRLError,'domain_cycle'):derive(e)
 def test_converging_domain_paths_are_legal(self):
  e=fixture('Leaf');edited(e,1,e['documents'][1]['raw'].replace(arc('domain-member','domain','south').encode(),(arc('domain-member','domain','south','xd:targetRole="'+ROLES[4]+'"')).encode()).replace(arc('domain-member','north','leaf').encode(),(arc('domain-member','north','leaf')+arc('domain-member','south','leaf')).encode()));self.assertEqual(len(proof(derive(e))['facts']),1)
 def test_duplicate_relationships_do_not_create_precedence_guesses(self):
  e=fixture();a=arc('hypercube-dimension','cube','axis','xd:targetRole="'+ROLES[2]+'"').encode();edited(e,1,e['documents'][1]['raw'].replace(a,a+a))
  with self.assertRaisesRegex(XBRLError,'duplicate_relationship'):derive(e)
 def test_role_ref_must_resolve_exact_original_role_type(self):
  for old,new in((b'authored.xsd#role1',b'authored.xsd#missing'),(b'authored.xsd#role1',b'missing.xsd#role1'),(b'authored.xsd#role1',b'authored.xsd#role2')):
   e=fixture();edited(e,1,e['documents'][1]['raw'].replace(old,new))
   with self.subTest(new=new),self.assertRaisesRegex(XBRLError,'role_not_resolved'):derive(e)
 def test_role_ref_required_in_same_original_linkbase(self):
  e=fixture();needle=('<l:roleRef roleURI="'+ROLES[1]+'" xl:type="simple" xl:href="authored.xsd#role1"/>').encode();edited(e,1,e['documents'][1]['raw'].replace(needle,b''))
  with self.assertRaisesRegex(XBRLError,'target_role_not_resolved'):derive(e)
 def test_role_type_used_on_and_schema_ids_are_bound(self):
  for old,new,reason in((b'<l:usedOn>l:definitionLink</l:usedOn>',b'<l:usedOn>l:presentationLink</l:usedOn>','role_used_on'),(b'id="role1"',b'id="role0"','duplicate_schema_id')):
   e=fixture();edited(e,0,e['documents'][0]['raw'].replace(old,new))
   with self.subTest(reason=reason),self.assertRaisesRegex(XBRLError,reason):derive(e)
 def test_priority_prohibition_and_unusable_stay_explicitly_unsupported(self):
  for attrs in('priority="1"','use="prohibited"','xd:usable="false"'):
   e=fixture();a=arc('domain-member','north','leaf').encode();edited(e,1,e['documents'][1]['raw'].replace(a,arc('domain-member','north','leaf',attrs).encode()))
   with self.subTest(attrs=attrs),self.assertRaisesRegex(XBRLError,'precedence_or_unusable_unsupported'):derive(e)
 def test_negative_open_typed_and_multiple_assignments_remain_unsupported(self):
  for change in('negative','open','typed','multiple'):
   e=fixture()
   if change=='typed':edited(e,0,e['documents'][0]['raw'].replace(b'name="RegionAxis"',b'name="RegionAxis" xd:typedDomainRef="#domain"'))
   else:
    raw=e['documents'][1]['raw']
    if change=='negative':raw=raw.replace(b'/arcrole/all',b'/arcrole/notAll')
    elif change=='open':raw=raw.replace(b'xd:closed="true"',b'xd:closed="false"')
    else:raw=raw.replace(b'</l:definitionLink>',arc('all','assets','cube','xd:closed="true" xd:contextElement="segment"').encode()+b'</l:definitionLink>',1)
    edited(e,1,raw)
   with self.subTest(change=change),self.assertRaises(XBRLError):derive(e)
 def test_original_document_missing_changed_duplicate_or_rehashed_graph_rejects(self):
  e=fixture();p,g=inputs(e)
  for docs in(e['documents'][:1],e['documents']+[e['documents'][0]],copy.deepcopy(e['documents'])):
   if len(docs)==2:docs[1]['raw']+=b' '
   with self.subTest(count=len(docs)),self.assertRaises(XBRLError):corroborate(p,g,profile=CROSS_ROLE_PROFILE,documents=docs,instance_uri=e['instance_uri'])
  g['concepts']['{'+NS+'}North']['declaration']['abstract']=True;g.pop('canonical_sha256');g['canonical_sha256']=digest(g);p['dts_corroboration']['dts_sha256']=g['canonical_sha256'];p['dts_corroboration']['concept_declarations']=copy.deepcopy(g['concepts']);rehash(p)
  with self.assertRaisesRegex(XBRLError,'reconstructed_graph_mismatch'):corroborate(p,g,profile=CROSS_ROLE_PROFILE,documents=e['documents'],instance_uri=e['instance_uri'])
 def test_permission_before_original_xml(self):
  e=fixture(origin='OBSERVED_OFFICIAL_RESPONSE',permission_reference='approved-authored-test');base='https://www.sec.gov/Archives/edgar/data/320193/000000012324000001/';e['instance_uri']=e['manifest']['source_url']=base+'instance.xml'
  for d in e['documents']:d['uri']=d['uri'].replace(BASE,base)
  p,g=inputs(e,observed=True)
  with patch('terminal.stocks.xbrl_dts.parse_xml',side_effect=AssertionError('NO_XML'))as parser:
   with self.assertRaisesRegex(XBRLError,'processing_not_approved'):corroborate(p,g,profile=CROSS_ROLE_PROFILE,documents=e['documents'],instance_uri=e['instance_uri'])
   parser.assert_not_called()
  self.assertEqual(len(proof(derive(e,allow_observed=True))['facts']),1)
 def test_collection_atomicity_and_legacy_default_rejection(self):
  e=fixture();c=FilingCollection('0000320193');c.ingest_dts_batch([e],dimensional_profile=CROSS_ROLE_PROFILE);before=c.page();bad=fixture('Unknown',accession='0000000123-24-000002')
  with self.assertRaises(XBRLError):c.ingest_dts_batch([bad],dimensional_profile=CROSS_ROLE_PROFILE)
  self.assertEqual(c.page(),before)
  with self.assertRaises(XBRLError):FilingCollection('0000320193').ingest_dts_batch([e],dimensional_profile=PROFILE)
 def test_retained_source_and_context_proof_tampering_reject_after_rehash(self):
  original=derive()
  for change in('drop','empty','profile','default','relationship','reference','source','role','placement'):
   p=copy.deepcopy(original);v=proof(p)
   if change=='drop':p['dts_corroboration'].pop('dimensional_validation')
   elif change=='empty':v['facts']=[]
   elif change=='profile':v['profile']='future'
   elif change=='default':v['facts'][0]['used_defaults']={'{'+NS+'}RegionAxis':'{'+NS+'}South'}
   elif change=='relationship':v['relationships'][0]['target_role']=None
   elif change=='reference':v['role_references'][0]['schema_sha256']='0'*64
   elif change=='source':v['relationships'][0]['source_sha256']='0'*64
   elif change=='role':v['facts'][0]['role']='urn:invented'
   else:v['facts'][0]['context_element']='scenario'
   rehash(p)
   with self.subTest(change=change),self.assertRaises(XBRLError):selected_financials(p)
 def test_input_and_output_bounds_are_errors(self):
  e=fixture();p,g=inputs(e)
  with patch('terminal.stocks.xbrl_cross_role.MAX_OUTPUT',1),self.assertRaisesRegex(XBRLError,'input_budget'):corroborate(p,g,profile=CROSS_ROLE_PROFILE,documents=e['documents'],instance_uri=e['instance_uri'])
 def test_same_role_consecutive_arcs_work_without_target_attribute(self):
  e=fixture();raw=e['documents'][1]['raw'];import re
  raw=re.sub(b' xd:targetRole="[^"]+"',b'',raw);raw=re.sub(b'xl:role="[^"]+"',('xl:role="'+ROLES[0]+'"').encode(),raw);edited(e,1,raw)
  self.assertEqual(len(proof(derive(e))['facts']),1)
 def test_standard_link_role_requires_no_role_ref(self):
  e=fixture();raw=e['documents'][1]['raw'];import re
  raw=re.sub(b'<l:roleRef[^>]+/>',b'',raw)
  for role in ROLES:raw=raw.replace(role.encode(),STANDARD.encode())
  edited(e,1,raw);out=derive(e);self.assertEqual(proof(out)['role_references'],[]);self.assertEqual(proof(out)['facts'][0]['role'],STANDARD)
 def test_source_role_reference_not_only_target_reference_is_checked(self):
  e=fixture();ref=('<l:roleRef roleURI="'+ROLES[0]+'" xl:type="simple" xl:href="authored.xsd#role0"/>').encode();edited(e,1,e['documents'][1]['raw'].replace(ref,b''))
  with self.assertRaisesRegex(XBRLError,'source_role_not_resolved'):derive(e)
 def test_inline_two_document_collection_retains_original_source_and_default(self):
  from .test_inline_set import html,doc
  e=fixture(None,default=True);raw=e['raw'].decode();resources=raw[raw.index('<x:context'):raw.index('<g:Assets')]
  page=html('',resources=True).decode();start=page.index('<x:context');end=page.index('</ix:resources>');page=(page[:start]+resources+page[end:]).replace('<html ','<html xmlns:d="http://xbrl.org/2006/xbrldi" ',1)
  originals=[doc('resources.xhtml',page.encode()),doc('facts.xhtml',html('<ix:nonFraction name="g:Assets" contextRef="I" unitRef="USD">1000</ix:nonFraction>'))]
  c=FilingCollection('0000320193');c.ingest_inline_set_batch([{'documents':originals,'concepts':e['concepts'],'taxonomy_documents':e['documents']}],dimensional_profile=CROSS_ROLE_PROFILE)
  out=next(iter(c._filings.values()));self.assertEqual(out['schema'],'gig.sec.xbrl.dimensional_inline_set.v7');self.assertEqual(len(out['document_set']['documents']),2);self.assertTrue(proof(out)['facts'][0]['used_defaults']);self.assertFalse(selected_financials(out)['history']['assets'])
 def test_bound_graph_metadata_cannot_be_replaced_after_rehash(self):
  for field in('documents','concept_declarations','dts_sha256'):
   e=fixture();p,g=inputs(e);p['dts_corroboration'][field]='tampered';rehash(p)
   with self.subTest(field=field),self.assertRaisesRegex(XBRLError,'binding'):corroborate(p,g,profile=CROSS_ROLE_PROFILE,documents=e['documents'],instance_uri=e['instance_uri'])
 def test_malformed_retained_proof_types_reject_explicitly(self):
  for change in('uri','target','reference','ord','closed'):
   p=derive();v=proof(p)
   if change=='uri':v['relationships'][0]['source_uri']=[]
   elif change=='target':v['relationships'][0]['target_role']={}
   elif change=='reference':v['role_references'][0]['role_type_uri']={}
   elif change=='ord':v['relationships'][0]['arc_node_ordinal']=True
   else:v['relationships'][0]['closed']=1
   rehash(p)
   with self.subTest(change=change),self.assertRaises(XBRLError):selected_financials(p)
 def test_whole_batch_stays_atomic_when_later_new_filing_fails(self):
  c=FilingCollection('0000320193');e=fixture();c.ingest_dts_batch([e],dimensional_profile=CROSS_ROLE_PROFILE);before=c.page()
  good=fixture(accession='0000000123-24-000002');bad=fixture('Unknown',accession='0000000123-24-000003')
  with self.assertRaises(XBRLError):c.ingest_dts_batch([good,bad],dimensional_profile=CROSS_ROLE_PROFILE)
  self.assertEqual(c.page(),before)
 def test_domain_depth_thirtyone_edges_accepts_next_level_rejects(self):
  def deep(n):
   e=fixture('Node'+str(n));decls=''.join('<s:element id="n'+str(i)+'" name="Node'+str(i)+'" substitutionGroup="x:item" x:periodType="duration"/>'for i in range(1,n+1));locs=''.join('<l:loc xl:type="locator" xl:label="n'+str(i)+'" xl:href="authored.xsd#n'+str(i)+'"/>'for i in range(1,n+1));links=''.join(arc('domain-member','north'if i==1 else'n'+str(i-1),'n'+str(i))for i in range(1,n+1));edited(e,0,e['documents'][0]['raw'].replace(b'</s:schema>',decls.encode()+b'</s:schema>'));needle=arc('domain-member','north','leaf').encode();edited(e,1,e['documents'][1]['raw'].replace(needle,locs.encode()+needle+links.encode()));return e
  self.assertEqual(len(proof(derive(deep(30)))['facts']),1)
  with self.assertRaisesRegex(XBRLError,'domain_depth'):derive(deep(31))
 def test_thirtytwo_axes_accept_thirtythree_reject(self):
  e=fixture();decls='';locs='';cube='';domains='';reported=''
  for i in range(1,33):
   id_='axis'+str(i);name='Axis'+str(i);decls+='<s:element id="'+id_+'" name="'+name+'" substitutionGroup="xd:dimensionItem" abstract="true" x:periodType="duration"/>';locs+='<l:loc xl:type="locator" xl:label="'+id_+'" xl:href="authored.xsd#'+id_+'"/>';cube+=arc('hypercube-dimension','cube',id_,'xd:targetRole="'+ROLES[2]+'"');domains+=arc('dimension-domain',id_,'domain','xd:targetRole="'+ROLES[3]+'"')
   if i<32:reported+='<d:explicitMember dimension="g:'+name+'">g:North</d:explicitMember>'
  edited(e,0,e['documents'][0]['raw'].replace(b'</s:schema>',decls.encode()+b'</s:schema>'));raw=e['documents'][1]['raw'];a=arc('hypercube-dimension','cube','axis','xd:targetRole="'+ROLES[2]+'"').encode();b=arc('dimension-domain','axis','domain','xd:targetRole="'+ROLES[3]+'"').encode();raw=raw.replace(a,locs.encode()+a+cube.encode()).replace(b,locs.encode()+b+domains.encode());edited(e,1,raw);e['raw']=e['raw'].replace(b'</x:segment>',reported.encode()+b'</x:segment>');e['manifest']['source_sha256']=hashlib.sha256(e['raw']).hexdigest()
  with self.assertRaisesRegex(XBRLError,'dimension_budget'):derive(e)
  edited(e,1,e['documents'][1]['raw'].replace(arc('hypercube-dimension','cube','axis32','xd:targetRole="'+ROLES[2]+'"').encode(),b''));self.assertEqual(len(proof(derive(e))['facts']),1)
 def test_semantic_order_does_not_sort_authored_source_nodes(self):
  e=fixture('South');out=derive(e);members=[a for a in proof(out)['relationships']if a['kind']=='domain-member'and a['from']=='{'+NS+'}Domain'];self.assertEqual([a['to']for a in members],['{'+NS+'}North','{'+NS+'}South']);self.assertLess(members[0]['arc_node_ordinal'],members[1]['arc_node_ordinal'])
 def test_role_type_must_be_direct_schema_annotation_appinfo_child(self):
  for location in('schema','element','nested'):
   e=fixture();raw=e['documents'][0]['raw'];role=('<l:roleType id="role1" roleURI="'+ROLES[1]+'"><l:usedOn>l:definitionLink</l:usedOn></l:roleType>').encode();raw=raw.replace(role,b'')
   if location=='schema':raw=raw.replace(b'</s:schema>',role+b'</s:schema>')
   elif location=='element':raw=raw.replace(b'</s:schema>',b'<s:element name="Carrier"><s:annotation><s:appinfo>'+role+b'</s:appinfo></s:annotation></s:element></s:schema>')
   else:raw=raw.replace(b'</s:schema>',b'<s:annotation><s:appinfo><l:Carrier>'+role+b'</l:Carrier></s:appinfo></s:annotation></s:schema>')
   edited(e,0,raw)
   with self.subTest(location=location),self.assertRaisesRegex(XBRLError,'role_type_location'):derive(e)
 def test_malformed_source_context_types_fail_explicitly(self):
  for value in(True,{},[True],[{'kind':'explicit','dimension':[]}],[{'kind':'explicit','dimension':'bad','member':'bad','context_element':'segment'}]):
   e=fixture();p,g=inputs(e);context=p['contexts']['I'];context['dimensions']=value;context['semantic_sha256']=digest({k:context[k]for k in('issuer_cik','period','dimensions','opaque_segment')});rehash(p)
   with self.subTest(value=value),self.assertRaisesRegex(XBRLError,'context_unsupported'):corroborate(p,g,profile=CROSS_ROLE_PROFILE,documents=e['documents'],instance_uri=e['instance_uri'])
 def test_role_type_duplicate_uri_and_invalid_definition_order_reject(self):
  for change in('duplicate','order','standard'):
   e=fixture();raw=e['documents'][0]['raw']
   if change=='duplicate':raw=raw.replace(ROLES[1].encode(),ROLES[0].encode())
   elif change=='standard':raw=raw.replace(ROLES[0].encode(),STANDARD.encode())
   else:raw=raw.replace(b'</l:roleType>',b'<l:definition>late</l:definition></l:roleType>',1)
   edited(e,0,raw)
   with self.subTest(change=change),self.assertRaises(XBRLError):derive(e)
