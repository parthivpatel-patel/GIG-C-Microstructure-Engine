"""Original-source typed/explicit closed-cube fixtures with exact local outcomes."""
import copy,hashlib,unittest
from unittest.mock import patch
from .test_xbrl_dimensions import entry,arc,D
from .test_xbrl_open_dimensions import edited
from .test_xbrl_binding import BASE
from .test_xbrl_instance import NS,manifest
from .xbrl_instance import parse_instance,selected_financials,digest,canonical,XBRLError
from .xbrl_dts import discover
from .xbrl_binding import bind_declarations
from .xbrl_dimensions import corroborate,TYPED_PROFILE,PROFILE,OPEN_PROFILE,INHERITED_PROFILE,NEGATIVE_PROFILE,NEGATIVE_ONLY_PROFILE

def fixture(text='7',kind='s:integer',*,explicit=False,default=False,member_attrs='',extra_types='',domain_body='',axis_ref='#typed'):
 e=entry(None if default else'North',default=default)
 member='<d:typedMember dimension="g:DeskAxis"><g:Code '+member_attrs+'>'+text+'</g:Code></d:typedMember>'
 if default:e['raw']=e['raw'].replace(b'</x:entity>',('<x:segment>'+member+'</x:segment></x:entity>').encode())
 else:e['raw']=e['raw'].replace(b'</x:segment>',member.encode()+b'</x:segment>')
 if not explicit:e['raw']=e['raw'].replace(b'<d:explicitMember dimension="g:RegionAxis">g:North</d:explicitMember>',b'')
 e['manifest']['source_sha256']=hashlib.sha256(e['raw']).hexdigest()
 declarations='<s:element id="desk" name="DeskAxis" substitutionGroup="xd:dimensionItem" abstract="true" type="x:stringItemType" x:periodType="duration" xd:typedDomainRef="'+axis_ref+'"/><s:element id="typed" name="Code" '+('type="'+kind+'"'if kind else'')+'>'+domain_body+'</s:element>'+extra_types
 edited(e,0,e['documents'][0]['raw'].replace(b'</s:schema>',declarations.encode()+b'</s:schema>'))
 added='<l:loc xl:type="locator" xl:label="desk" xl:href="authored.xsd#desk"/>'+arc('hypercube-dimension','cube','desk')
 link=e['documents'][1]['raw'].replace(b'</l:definitionLink>',added.encode()+b'</l:definitionLink>')
 if not explicit:link=link.replace(arc('hypercube-dimension','cube','axis').encode(),b'')
 edited(e,1,link);return e

def inputs(e):
 p=parse_instance(e['raw'],e['manifest'],e['concepts'],allow_observed=e['manifest']['origin']=='OBSERVED_OFFICIAL_RESPONSE');g=discover(e['raw'],e['instance_uri'],e['manifest']['source_sha256'],e['documents'],origin=e['manifest']['origin'],allow_observed=e['manifest']['origin']=='OBSERVED_OFFICIAL_RESPONSE',permission_reference=e['manifest']['permission_reference']);return bind_declarations(p,g),g

def derive(e=None,**kwargs):
 e=fixture()if e is None else e;p,g=inputs(e);return corroborate(p,g,profile=TYPED_PROFILE,documents=e['documents'],instance_uri=e['instance_uri'],**kwargs)
def proof(p):return p['dts_corroboration']['dimensional_validation']
def rehash(p):p.pop('canonical_sha256',None);p['canonical_sha256']=digest(p)

class TypedHypercubes(unittest.TestCase):
 def test_valid_typed_cube_retains_source_fact_context_value_receipts_and_inputs(self):
  e=fixture();before=copy.deepcopy(e);p,g=inputs(e);out=derive(e);r=proof(out)['facts'][0];t=r['typed_dimensions'][0]
  self.assertEqual(out['schema'],'gig.sec.xbrl.dimensional_instance.v6');self.assertEqual(proof(out)['profile'],TYPED_PROFILE);self.assertFalse(proof(out)['complete_drs_validation']);self.assertEqual(r['status'],'VALIDATED_RESTRICTED_TYPED_CONTEXT');self.assertEqual(r['used_defaults'],{})
  self.assertEqual(out['facts'],p['facts']);self.assertEqual(out['contexts'],p['contexts']);self.assertEqual(out['source'],p['source']);self.assertEqual(e,before);self.assertEqual(t['dimension'],'{'+NS+'}DeskAxis');self.assertEqual(t['member_tree_sha256'],digest(p['contexts']['I']['dimensions'][0]['member']));self.assertEqual(t['typed_domain_ref'],BASE+'authored.xsd#typed');self.assertEqual(t['domain_source_sha256'],e['documents'][0]['sha256']);self.assertEqual(t['scalar_validation']['resolved_type'],'{http://www.w3.org/2001/XMLSchema}integer');self.assertEqual(out['canonical_sha256'],digest({k:v for k,v in out.items()if k!='canonical_sha256'}))
 def test_typed_values_and_whitespace_remain_original_no_equality_is_inferred(self):
  a=derive(fixture('  A  B  ','s:string'));b=derive(fixture('A B','s:string'));self.assertEqual(a['contexts']['I']['dimensions'][0]['member']['text'],'  A  B  ');self.assertNotEqual(proof(a)['facts'][0]['typed_dimensions'][0]['member_tree_sha256'],proof(b)['facts'][0]['typed_dimensions'][0]['member_tree_sha256'])
 def test_mixed_required_explicit_and_typed_axes_retain_used_default_only(self):
  p=derive(fixture(explicit=True,default=True));self.assertEqual(proof(p)['facts'][0]['used_defaults'],{'{'+NS+'}RegionAxis':'{'+NS+'}South'});self.assertEqual(len(p['contexts']['I']['dimensions']),1);self.assertEqual(len(proof(p)['facts'][0]['typed_dimensions']),1)
  p=derive(fixture(explicit=True));self.assertEqual(proof(p)['facts'][0]['used_defaults'],{});self.assertEqual(len(p['contexts']['I']['dimensions']),2)
 def test_missing_required_typed_axis_does_not_acquire_a_default(self):
  e=fixture();start=e['raw'].index(b'<d:typedMember');end=e['raw'].index(b'</d:typedMember>')+len(b'</d:typedMember>');e['raw']=e['raw'][:start]+e['raw'][end:];e['manifest']['source_sha256']=hashlib.sha256(e['raw']).hexdigest()
  with self.assertRaisesRegex(XBRLError,'required_dimension_missing'):derive(e)
 def test_typed_dimension_cannot_have_explicit_domain_or_default_arcs(self):
  for kind,target in(('dimension-domain','domain'),('dimension-default','south')):
   e=fixture();edited(e,1,e['documents'][1]['raw'].replace(b'</l:definitionLink>',arc(kind,'desk',target).encode()+b'</l:definitionLink>'))
   with self.subTest(kind=kind),self.assertRaisesRegex(XBRLError,'typed_explicit_relationship'):derive(e)
 def test_missing_explicit_axis_and_reported_default_remain_errors(self):
  e=fixture(explicit=True);e['raw']=e['raw'].replace(b'<d:explicitMember dimension="g:RegionAxis">g:North</d:explicitMember>',b'');e['manifest']['source_sha256']=hashlib.sha256(e['raw']).hexdigest()
  with self.assertRaisesRegex(XBRLError,'required_dimension_missing'):derive(e)
  e=fixture(explicit=True,default=True);e['raw']=e['raw'].replace(b'</x:segment>',b'<d:explicitMember dimension="g:RegionAxis">g:South</d:explicitMember></x:segment>');e['manifest']['source_sha256']=hashlib.sha256(e['raw']).hexdigest()
  with self.assertRaisesRegex(XBRLError,'explicit_default_member'):derive(e)
 def test_closed_extra_wrong_placement_and_opaque_context_remain_unsupported(self):
  cases=[(b'</x:segment>',b'<d:explicitMember dimension="g:RegionAxis">g:North</d:explicitMember></x:segment>','closed_extra'),(b'</x:segment>',b'<g:Opaque>unknown</g:Opaque></x:segment>','context_profile')]
  for old,new,error in cases:
   e=fixture();e['raw']=e['raw'].replace(old,new);e['manifest']['source_sha256']=hashlib.sha256(e['raw']).hexdigest()
   with self.assertRaisesRegex(XBRLError,error):derive(e)
  e=fixture();edited(e,1,e['documents'][1]['raw'].replace(b'contextElement="segment"',b'contextElement="scenario"'))
  with self.assertRaisesRegex(XBRLError,'context_profile'):derive(e)
 def test_numeric_lexical_ranges_boolean_and_restrictions_are_exact(self):
  for text,kind in(('true','s:boolean'),('255','s:unsignedByte'),('-1.25','s:decimal')):self.assertEqual(len(proof(derive(fixture(text,kind)))['facts']),1)
  for text,kind in(('TRUE','s:boolean'),('256','s:unsignedByte'),('1.0','s:integer')):
   with self.subTest(text=text),self.assertRaises(XBRLError):derive(fixture(text,kind))
  types='<s:simpleType name="Limited"><s:restriction base="s:integer"><s:minInclusive value="0"/><s:maxExclusive value="10"/></s:restriction></s:simpleType>'
  # Explicit namespace binding in original schema;no guessed type aliases.
  e=fixture('9','g:Limited',extra_types=types);edited(e,0,e['documents'][0]['raw'].replace(b'<s:schema ',('<s:schema xmlns:g="'+NS+'" ').encode(),1));self.assertEqual(proof(derive(e))['facts'][0]['typed_dimensions'][0]['scalar_validation']['restriction_types'],['{'+NS+'}Limited'])
  e['raw']=e['raw'].replace(b'>9</g:Code>',b'>10</g:Code>');e['manifest']['source_sha256']=hashlib.sha256(e['raw']).hexdigest()
  with self.assertRaisesRegex(XBRLError,'facet_violation'):derive(e)
 def test_complex_nil_attributes_anonymous_qname_values_do_not_become_acceptance(self):
  cases=[fixture('<g:Code>7</g:Code>'),fixture('',member_attrs='xsi:nil="true"'),fixture('7',member_attrs='code="A"'),fixture('7',kind='',domain_body='<s:simpleType><s:restriction base="s:integer"/></s:simpleType>'),fixture('A','s:QName')]
  for e in cases:
   with self.assertRaisesRegex(XBRLError,'scalar_semantics_unsupported'):derive(e)
 def test_axis_domain_source_and_global_element_are_never_guessed(self):
  for reference in('#missing','missing.xsd#typed','#xpointer(id(typed))'):
   with self.subTest(reference=reference),self.assertRaises(XBRLError):derive(fixture(axis_ref=reference))
  e=fixture();edited(e,0,e['documents'][0]['raw'].replace(b'id="typed" name="Code"',b'id="typed" name="Code" abstract="true"'))
  with self.assertRaisesRegex(XBRLError,'abstract_target'):derive(e)
 def test_original_schema_linkbase_coverage_hashes_and_duplicates_are_mandatory(self):
  e=fixture();p,g=inputs(e)
  for docs,error in((e['documents'][:1],'reconstructed_graph_mismatch'),(e['documents'][1:],'original_schema_required'),(e['documents']+[e['documents'][0]],'duplicate_source_uri')):
   with self.subTest(error=error),self.assertRaisesRegex(XBRLError,error):corroborate(p,g,profile=TYPED_PROFILE,documents=docs,instance_uri=e['instance_uri'])
  docs=copy.deepcopy(e['documents']);docs[1]['raw']+=b' '
  with self.assertRaisesRegex(XBRLError,'document_digest'):corroborate(p,g,profile=TYPED_PROFILE,documents=docs,instance_uri=e['instance_uri'])
  docs=copy.deepcopy(e['documents']);docs.append({'uri':BASE+'unrelated.xml','raw':b'<root/>','sha256':hashlib.sha256(b'<root/>').hexdigest()})
  with self.assertRaisesRegex(XBRLError,'source_not_bound'):corroborate(p,g,profile=TYPED_PROFILE,documents=docs,instance_uri=e['instance_uri'])
 def test_recomputed_artifact_hash_cannot_authorize_changed_original_relationship(self):
  e=fixture();p,g=inputs(e);g['definition'][0]['arcs'][0]['closed']=False;rehash(g);p['dts_corroboration']['dts_sha256']=g['canonical_sha256'];rehash(p)
  with self.assertRaisesRegex(XBRLError,'reconstructed_graph_mismatch'):corroborate(p,g,profile=TYPED_PROFILE,documents=e['documents'],instance_uri=e['instance_uri'])
 def test_raw_reconstruction_uses_canonical_boolean_types_and_document_order(self):
  e=fixture()
  for change in('usable','closure','document_order'):
   p,g=inputs(e)
   if change=='usable':g['definition'][0]['usable_for_restricted_profile']=1
   elif change=='closure':g['structural_closure']=1
   else:g['documents'].reverse()
   rehash(g);p['dts_corroboration']['dts_sha256']=g['canonical_sha256'];rehash(p)
   error='closure_required'if change=='closure'else'reconstructed_graph_mismatch'
   with self.subTest(change=change),self.assertRaisesRegex(XBRLError,error):corroborate(p,g,profile=TYPED_PROFILE,documents=e['documents'],instance_uri=e['instance_uri'])
 def test_original_instance_uri_and_root_union_are_required(self):
  e=fixture();p,g=inputs(e)
  with self.assertRaisesRegex(XBRLError,'dts_uri'):corroborate(p,g,profile=TYPED_PROFILE,documents=e['documents'])
  with self.assertRaisesRegex(XBRLError,'original_document_coverage'):corroborate(p,g,profile=TYPED_PROFILE,documents=e['documents'],instance_uri=BASE+'other/instance.xml')
  p['schema_references'][0]['href']='absent.xsd';rehash(p)
  with self.assertRaisesRegex(XBRLError,'original_document_coverage'):corroborate(p,g,profile=TYPED_PROFILE,documents=e['documents'],instance_uri=e['instance_uri'])
 def test_source_scope_and_context_hash_tampering_are_rejected(self):
  e=fixture();p,g=inputs(e);p['contexts']['I']['dimensions'][0]['member']['text']='8';rehash(p)
  with self.assertRaisesRegex(XBRLError,'context_identity'):corroborate(p,g,profile=TYPED_PROFILE,documents=e['documents'],instance_uri=e['instance_uri'])
  p,g=inputs(e);g['instance_sha256']='0'*64;rehash(g);p['dts_corroboration']['dts_sha256']=g['canonical_sha256'];rehash(p)
  with self.assertRaisesRegex(XBRLError,'source_scope'):corroborate(p,g,profile=TYPED_PROFILE,documents=e['documents'],instance_uri=e['instance_uri'])
 def test_open_negative_crossrole_prioritized_and_inherited_scope_fail_closed(self):
  for old,new in((b'closed="true"',b'closed="false"'),(b'arcrole="'+b'http://xbrl.org/int/dim/arcrole/all'+b'"',b'arcrole="http://xbrl.org/int/dim/arcrole/notAll"'),(b'xl:to="desk"',b'xl:to="desk" xd:targetRole="urn:other"'),(b'xl:to="desk"',b'xl:to="desk" priority="1"')):
   e=fixture();edited(e,1,e['documents'][1]['raw'].replace(old,new))
   with self.assertRaises(XBRLError):derive(e)
  e=fixture();edited(e,1,e['documents'][1]['raw'].replace(arc('all','assets','cube','xd:closed="true" xd:contextElement="segment"').encode(),arc('all','domain','cube','xd:closed="true" xd:contextElement="segment"').encode()))
  with self.assertRaisesRegex(XBRLError,'direct_closed_assignment'):derive(e)
 def test_profile_requires_at_least_one_typed_axis(self):
  e=entry();p,g=inputs(e)
  with self.assertRaisesRegex(XBRLError,'typed_axis_required'):corroborate(p,g,profile=TYPED_PROFILE,documents=e['documents'],instance_uri=e['instance_uri'])
 def test_observed_grant_and_permission_binding_precede_all_original_xml(self):
  e=fixture();p,g=inputs(e);p['origin']=g['origin']=p['source']['origin']='OBSERVED_OFFICIAL_RESPONSE';rehash(g);p['dts_corroboration']['dts_sha256']=g['canonical_sha256'];rehash(p)
  with patch('terminal.stocks.xbrl_typed_dimensions.parse_xml',side_effect=AssertionError('UNAPPROVED_XML')),patch('terminal.stocks.xbrl_dts.parse_xml',side_effect=AssertionError('UNAPPROVED_XML')):
   with self.assertRaisesRegex(XBRLError,'not_approved'):corroborate(p,g,profile=TYPED_PROFILE,documents=e['documents'],instance_uri=e['instance_uri'])
   with self.assertRaisesRegex(XBRLError,'permission_binding'):corroborate(p,g,profile=TYPED_PROFILE,documents=e['documents'],instance_uri=e['instance_uri'],allow_observed=True)
 def test_original_inline_document_set_uses_actual_reference_union_and_receipts(self):
  from .test_inline_set import html,doc
  from .inline_set import parse_document_set
  from .xbrl_dts import discover_inline_set
  e=fixture(explicit=True,default=True);raw=e['raw'].decode();resources=raw[raw.index('<x:context'):raw.index('<g:Assets')]
  page=html('',resources=True).decode();start=page.index('<x:context');end=page.index('</ix:resources>');page=(page[:start]+resources+page[end:]).replace('<html ','<html xmlns:d="http://xbrl.org/2006/xbrldi" ',1)
  originals=[doc('resources.xhtml',page.encode()),doc('facts.xhtml',html('<ix:nonFraction name="g:Assets" contextRef="I" unitRef="USD">1000</ix:nonFraction>'))]
  parsed=parse_document_set(originals,e['concepts']);g=discover_inline_set(parsed,e['documents']);p=bind_declarations(parsed,g);before=copy.deepcopy((p,g,originals));out=corroborate(p,g,profile=TYPED_PROFILE,documents=e['documents'])
  self.assertEqual(out['schema'],'gig.sec.xbrl.dimensional_inline_set.v6');self.assertEqual(out['document_set'],p['document_set']);self.assertEqual(out['source'],p['source']);self.assertEqual(out['facts'],p['facts']);self.assertEqual((p,g,originals),before);self.assertEqual(proof(out)['facts'][0]['used_defaults'],{'{'+NS+'}RegionAxis':'{'+NS+'}South'});self.assertEqual(out['document_set']['documents'][0]['source']['received_at'],None)
  p['document_set']['schema_references'].append({'uri':BASE+'missing.xsd','fetched':False});rehash(p)
  with self.assertRaisesRegex(XBRLError,'reconstructed_graph_mismatch'):corroborate(p,g,profile=TYPED_PROFILE,documents=e['documents'])
 def test_inline_permission_hashes_gate_every_raw_schema_before_parsing(self):
  from .test_inline_set import html,doc
  from .inline_set import parse_document_set
  from .xbrl_dts import discover_inline_set
  e=fixture();raw=e['raw'].decode();resources=raw[raw.index('<x:context'):raw.index('<g:Assets')];page=html('<ix:nonFraction name="g:Assets" contextRef="I" unitRef="USD">1000</ix:nonFraction>',resources=True).decode();start=page.index('<x:context');end=page.index('</ix:resources>');page=(page[:start]+resources+page[end:]).replace('<html ','<html xmlns:d="http://xbrl.org/2006/xbrldi" ',1)
  parsed=parse_document_set([doc('a.xhtml',page.encode())],e['concepts']);g=discover_inline_set(parsed,e['documents']);p=bind_declarations(parsed,g);p['origin']=g['origin']=p['source']['origin']='OBSERVED_OFFICIAL_RESPONSE';p['document_set']['documents'][0]['source']['origin']='OBSERVED_OFFICIAL_RESPONSE';p['document_set']['sha256']=digest(p['document_set']['documents']);p['source']['source_sha256']=g['document_set_sha256']=p['document_set']['sha256'];rehash(g);p['dts_corroboration']['dts_sha256']=g['canonical_sha256'];rehash(p)
  with patch('terminal.stocks.xbrl_typed_dimensions.parse_xml',side_effect=AssertionError('UNAPPROVED_XML')),patch('terminal.stocks.xbrl_dts.parse_xml',side_effect=AssertionError('UNAPPROVED_XML')):
   with self.assertRaisesRegex(XBRLError,'not_approved'):corroborate(p,g,profile=TYPED_PROFILE,documents=e['documents'])
   with self.assertRaisesRegex(XBRLError,'permission_binding'):corroborate(p,g,profile=TYPED_PROFILE,documents=e['documents'],allow_observed=True)
 def test_thirtytwo_axes_accept_and_thirtythree_cube_axes_reject(self):
  e=fixture();decls='';links='';reported=''
  for i in range(1,33):
   id_='desk'+str(i);name='DeskAxis'+str(i)
   decls+='<s:element id="'+id_+'" name="'+name+'" substitutionGroup="xd:dimensionItem" abstract="true" xd:typedDomainRef="#typed"/>'
   links+='<l:loc xl:type="locator" xl:label="'+id_+'" xl:href="authored.xsd#'+id_+'"/>'+arc('hypercube-dimension','cube',id_)
   if i<32:reported+='<d:typedMember dimension="g:'+name+'"><g:Code>7</g:Code></d:typedMember>'
  edited(e,0,e['documents'][0]['raw'].replace(b'</s:schema>',decls.encode()+b'</s:schema>'));edited(e,1,e['documents'][1]['raw'].replace(b'</l:definitionLink>',links.encode()+b'</l:definitionLink>'))
  e['raw']=e['raw'].replace(b'</x:segment>',reported.encode()+b'</x:segment>');e['manifest']['source_sha256']=hashlib.sha256(e['raw']).hexdigest()
  with self.assertRaisesRegex(XBRLError,'dimension_budget'):derive(e)
  edited(e,1,e['documents'][1]['raw'].replace(arc('hypercube-dimension','cube','desk32').encode(),b''));p=derive(e);self.assertEqual(len(proof(p)['facts'][0]['typed_dimensions']),32)
  self.assertEqual([t['dimension']for t in proof(p)['facts'][0]['typed_dimensions']],sorted(t['dimension']for t in proof(p)['facts'][0]['typed_dimensions']))
 def test_explicit_cycles_defaults_and_primary_polymorphism_remain_errors(self):
  cases=[(arc('domain-member','north','domain'),'domain_cycle'),(arc('dimension-default','axis','north')+arc('dimension-default','axis','south'),'default_conflict'),(arc('domain-member','domain','assets'),'primary_item_polymorphism')]
  for extra,error in cases:
   e=fixture(explicit=True);edited(e,1,e['documents'][1]['raw'].replace(b'</l:definitionLink>',extra.encode()+b'</l:definitionLink>'))
   with self.subTest(error=error),self.assertRaisesRegex(XBRLError,error):derive(e)
 def test_omitted_embedded_semantics_cannot_hide_behind_external_cube(self):
  e=fixture();embedded='<s:annotation><s:appinfo><l:linkbase><l:definitionLink xl:type="extended" xl:role="urn:unreviewed"/></l:linkbase></s:appinfo></s:annotation>'
  edited(e,0,e['documents'][0]['raw'].replace(b'</s:schema>',embedded.encode()+b'</s:schema>'))
  with self.assertRaisesRegex(XBRLError,'profile_unsupported'):derive(e)
 def test_explicit_supported_embedded_profile_reconstructs_same_raw_sources(self):
  from .xbrl_dts import EMBEDDED_PROFILE
  e=fixture();embedded=e['documents'][1]['raw'];schema=e['documents'][0]['raw'].replace(b'<l:linkbaseRef xl:type="simple" xl:href="dimensions.xml"/>',embedded);edited(e,0,schema);e['documents'].pop()
  p=parse_instance(e['raw'],e['manifest'],e['concepts']);g=discover(e['raw'],e['instance_uri'],e['manifest']['source_sha256'],e['documents'],embedded_profile=EMBEDDED_PROFILE);p=bind_declarations(p,g)
  out=corroborate(p,g,profile=TYPED_PROFILE,documents=e['documents'],instance_uri=e['instance_uri']);self.assertEqual(out['schema'],'gig.sec.xbrl.dimensional_instance.v6');self.assertEqual(proof(out)['facts'][0]['typed_dimensions'][0]['domain_source_sha256'],e['documents'][0]['sha256'])
 def test_approved_observed_raw_processing_keeps_receipts_without_provider_contact(self):
  e=fixture();base='https://www.sec.gov/Archives/edgar/data/320193/000000012324000001/';e['instance_uri']=base+'authored.xml'
  for d in e['documents']:d['uri']=base+d['uri'].rsplit('/',1)[-1]
  e['manifest'].update(origin='OBSERVED_OFFICIAL_RESPONSE',source_url=e['instance_uri'],permission_reference='authored offline processing approval')
  out=derive(e,allow_observed=True);self.assertEqual(out['source']['source_url'],e['instance_uri']);self.assertIsNone(out['source']['received_at']);self.assertNotIn('permission_reference',out['source']);self.assertEqual(proof(out)['facts'][0]['typed_dimensions'][0]['typed_domain_ref'],base+'authored.xsd#typed')
 def test_limits_are_enforced_and_legacy_profiles_still_reject_typed_contexts(self):
  e=fixture();p,g=inputs(e)
  with patch('terminal.stocks.xbrl_typed_dimensions.MAX_RECORDS',0),self.assertRaisesRegex(XBRLError,'record_budget'):derive(e)
  for profile in(PROFILE,OPEN_PROFILE,INHERITED_PROFILE,NEGATIVE_PROFILE):
   with self.subTest(profile=profile),self.assertRaises(XBRLError):corroborate(p,g,profile=profile)
  with self.assertRaisesRegex(XBRLError,'document_budget'):corroborate(p,g,profile=TYPED_PROFILE,documents=e['documents']*9,instance_uri=e['instance_uri'])

class TypedHypercubeIntegration(unittest.TestCase):
 def test_selected_financials_accepts_typed_proof_without_promoting_dimensioned_rows(self):
  for e in(fixture(),fixture(' A  B ','s:string'),fixture('false','s:boolean'),fixture(explicit=True,default=True)):
   p=derive(e);result=selected_financials(p)
   self.assertFalse(result['history']['assets']);self.assertEqual(result['xbrl_coverage']['excluded']['dimensioned_or_opaque'],1);self.assertEqual(result['xbrl_coverage']['dts_corroboration']['dimensional_validation'],proof(p))
 def test_rehashed_proof_corruption_is_rejected_by_selected_financials(self):
  for change in('member_hash','domain_hash','domain_uri','missing_typed','duplicate_typed','axis','placement','default_overlap','scalar_status','scalar_type','scalar_profile','scalar_restrictions','extra_field','diagnostics_hash','missing_proof','missing_fact','duplicate_fact','schema'):
   p=derive();v=proof(p);r=v['facts'][0];t=r['typed_dimensions'][0]
   if change=='member_hash':t['member_tree_sha256']='0'*64
   elif change=='domain_hash':t['domain_source_sha256']='0'*64
   elif change=='domain_uri':t['typed_domain_ref']=BASE+'not-bound.xsd#typed'
   elif change=='missing_typed':r['typed_dimensions']=[]
   elif change=='duplicate_typed':r['typed_dimensions']*=2
   elif change=='axis':t['dimension']='{'+NS+'}OtherAxis'
   elif change=='placement':r['context_element']='scenario'
   elif change=='default_overlap':r['used_defaults'][t['dimension']]='{'+NS+'}North'
   elif change=='scalar_status':t['scalar_validation']['validation']='STRING_LEXICAL_RETAINED'
   elif change=='scalar_type':t['scalar_validation']['resolved_type']='{http://www.w3.org/2001/XMLSchema}float'
   elif change=='scalar_profile':t['scalar_validation']['numeric_profile']='unreviewed'
   elif change=='scalar_restrictions':t['scalar_validation']['restriction_types']=['not-expanded']
   elif change=='extra_field':t['invented_equivalence']=True
   elif change=='diagnostics_hash':v['typed_context_diagnostics_sha256']='unknown'
   elif change=='missing_proof':p['dts_corroboration'].pop('dimensional_validation')
   elif change=='missing_fact':v['facts']=[]
   elif change=='duplicate_fact':v['facts']*=2
   else:p['schema']='gig.sec.xbrl.instance.v1'
   rehash(p)
   with self.subTest(change=change),self.assertRaisesRegex(XBRLError,'dimensional_result'):selected_financials(p)
 def test_context_tree_cannot_change_by_rehashing_only_outer_artifact(self):
  p=derive();p['contexts']['I']['dimensions'][0]['member']['text']='another';rehash(p)
  with self.assertRaisesRegex(XBRLError,'dimensional_result'):selected_financials(p)
 def test_numeric_lexical_and_boolean_validation_are_independently_checked(self):
  for text,kind,bad in(('7','s:integer','7.5'),('true','s:boolean','TRUE')):
   p=derive(fixture(text,kind));context=p['contexts']['I'];member=context['dimensions'][0]['member'];member['text']=bad
   proof(p)['facts'][0]['typed_dimensions'][0]['member_tree_sha256']=digest(member);context['semantic_sha256']=digest({k:context[k]for k in('issuer_cik','period','dimensions','opaque_segment')});rehash(p)
   with self.assertRaisesRegex(XBRLError,'dimensional_result'):selected_financials(p)
 def test_plain_collection_forwards_raw_sources_and_atomic_failure_preserves_state(self):
  from .xbrl_collection import FilingCollection
  c=FilingCollection('0000320193');e=fixture();before=copy.deepcopy(e)
  with patch('socket.socket.connect',side_effect=AssertionError('NO_NETWORK')):c.ingest_dts_batch([e],dimensional_profile=TYPED_PROFILE)
  result=c.at_acceptance_time('2024-02-02T00:00:00Z');self.assertFalse(result['history']['assets']);self.assertEqual(result['selected_input_coverage'][0]['xbrl_coverage']['dts_corroboration']['dimensional_validation']['profile'],TYPED_PROFILE);self.assertEqual(e,before)
  state=c.page();valid=fixture('8');valid['manifest']['accession']='0000000123-24-000002';bad=fixture();bad['manifest']['accession']='0000000123-24-000003';bad['documents'][1]['raw']+=b' '
  with self.assertRaisesRegex(XBRLError,'document_digest'):c.ingest_dts_batch([valid,bad],dimensional_profile=TYPED_PROFILE)
  self.assertEqual(c.page(),state)
 def test_inline_collection_preserves_original_document_set_and_atomic_failure(self):
  from .xbrl_collection import FilingCollection
  from .test_inline_set import html,doc
  e=fixture();raw=e['raw'].decode();resources=raw[raw.index('<x:context'):raw.index('<g:Assets')]
  page=html('',resources=True).decode();start=page.index('<x:context');end=page.index('</ix:resources>');page=(page[:start]+resources+page[end:]).replace('<html ','<html xmlns:d="http://xbrl.org/2006/xbrldi" ',1)
  batch={'documents':[doc('resources.xhtml',page.encode()),doc('facts.xhtml',html('<ix:nonFraction name="g:Assets" contextRef="I" unitRef="USD">1000</ix:nonFraction>'))],'concepts':e['concepts'],'taxonomy_documents':e['documents']};before=copy.deepcopy(batch);c=FilingCollection('0000320193')
  with patch('socket.socket.connect',side_effect=AssertionError('NO_NETWORK')):c.ingest_inline_set_batch([batch],dimensional_profile=TYPED_PROFILE)
  result=c.at_acceptance_time('2024-02-02T00:00:00Z');coverage=result['selected_input_coverage'][0]['xbrl_coverage'];self.assertFalse(result['history']['assets']);self.assertEqual(len(coverage['document_set']['documents']),2);self.assertEqual(coverage['dts_corroboration']['dimensional_validation']['profile'],TYPED_PROFILE);self.assertEqual(batch,before)
  state=c.page();bad=copy.deepcopy(batch);bad['taxonomy_documents'][0]['sha256']='0'*64
  with self.assertRaisesRegex(XBRLError,'document_digest'):c.ingest_inline_set_batch([batch,bad],dimensional_profile=TYPED_PROFILE)
  self.assertEqual(c.page(),state)
 def test_legacy_collection_calls_receive_no_new_source_kwargs(self):
  from .xbrl_collection import FilingCollection
  from .xbrl_dimensions import corroborate as original
  seen=[]
  def wrapped(*args,**kwargs):seen.append(kwargs);return original(*args,**kwargs)
  with patch('terminal.stocks.xbrl_dimensions.corroborate',side_effect=wrapped):FilingCollection('0000320193').ingest_dts_batch([entry()],dimensional_profile=PROFILE)
  self.assertEqual(seen,[{'profile':PROFILE}])

if __name__=='__main__':unittest.main(verbosity=2)
