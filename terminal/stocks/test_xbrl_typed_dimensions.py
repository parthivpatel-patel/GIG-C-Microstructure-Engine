"""Authored original schema/typed scalar fixtures; no context equivalence inferred."""
import copy,hashlib,unittest
from unittest.mock import patch
from .test_xbrl_binding import declaration,BASE
from .test_xbrl_instance import xml,manifest,NS
from .xbrl_instance import parse_instance,selected_concepts,selected_financials,digest,canonical,tag,XBRLError
from .xbrl_dts import discover
from .xbrl_binding import bind_declarations
from .xbrl_typed_dimensions import check_typed_contexts,PROFILE

D='http://xbrl.org/2005/xbrldt'
def fixture(text='7',kind='s:integer',*,member_attrs='',domain_attrs='',domain_body='',extras='',axis_ref='#typed',axis_group='xd:dimensionItem',member_name='Code'):
 member='<x:segment><d:typedMember dimension="g:DeskAxis"><g:'+member_name+' '+member_attrs+'>'+text+'</g:'+member_name+'></d:typedMember></x:segment>'
 raw=xml('<g:Assets contextRef="I" unitRef="USD">1000</g:Assets>',context_extra=member)
 schema=declaration().replace(b'<s:schema',('<s:schema xmlns:xd="'+D+'" xmlns:t="'+NS+'"').encode(),1)
 parts='<s:element id="axis" name="DeskAxis" substitutionGroup="'+axis_group+'" type="x:stringItemType" abstract="true" x:periodType="duration" xd:typedDomainRef="'+axis_ref+'"/><s:element id="typed" name="Code" '+('type="'+kind+'" 'if kind else'')+domain_attrs+'>'+domain_body+'</s:element>'+extras
 schema=schema.replace(b'</s:schema>',parts.encode()+b'</s:schema>');docs=[{'uri':BASE+'authored.xsd','raw':schema,'sha256':hashlib.sha256(schema).hexdigest()}]
 p=parse_instance(raw,manifest(raw),selected_concepts(NS));g=discover(raw,BASE+'instance.xml',hashlib.sha256(raw).hexdigest(),docs);p=bind_declarations(p,g)
 return p,g,docs

def rebind(p,g):
 g.pop('canonical_sha256',None);g['canonical_sha256']=digest(g);p['dts_corroboration']['dts_sha256']=g['canonical_sha256'];p.pop('canonical_sha256',None);p['canonical_sha256']=digest(p)

class TypedDomains(unittest.TestCase):
 def test_numeric_original_schema_context_fact_ids_and_nonpromotion_are_preserved(self):
  p,g,docs=fixture();before=copy.deepcopy((p,g,docs));report=check_typed_contexts(p,g,docs)
  self.assertEqual(report['status'],'VALIDATED_SUPPORTED_TYPED_SCALARS');self.assertFalse(report['complete_drs_validation']);self.assertFalse(report['financial_admission_changed']);self.assertEqual(report['parsed_sha256'],p['canonical_sha256']);self.assertEqual(report['dts_sha256'],g['canonical_sha256']);context=report['contexts'][0]
  self.assertEqual(context['context_id'],'I');self.assertEqual(context['source_fact_ids'],[p['facts'][0]['source_fact_id']]);self.assertEqual(context['typed_members'][0]['domain']['typed_domain_ref'],BASE+'authored.xsd#typed');self.assertEqual(report['source_schemas'][0]['sha256'],docs[0]['sha256']);self.assertEqual((p,g,docs),before);self.assertEqual(selected_financials(p)['history']['assets'],[])
  self.assertEqual(report['sha256'],digest({k:v for k,v in report.items()if k!='sha256'}))
 def test_string_lexical_is_not_replaced_or_compared_by_normalized_value(self):
  a=fixture(' A  B ','s:string');b=fixture('A B','s:string');ra=check_typed_contexts(*a);rb=check_typed_contexts(*b)
  self.assertEqual(a[0]['contexts']['I']['dimensions'][0]['member']['text'],' A  B ');self.assertNotEqual(ra['contexts'][0]['typed_members'][0]['member_tree_sha256'],rb['contexts'][0]['typed_members'][0]['member_tree_sha256']);self.assertNotEqual(ra['contexts'][0]['context_semantic_sha256'],rb['contexts'][0]['context_semantic_sha256'])
 def test_boolean_and_integer_lexical_rules_are_explicit(self):
  for value in('true','false','1','0',' \ttrue\n'):self.assertEqual(check_typed_contexts(*fixture(value,'s:boolean'))['unsupported_member_count'],0)
  for value,kind in(('TRUE','s:boolean'),('2','s:boolean'),('1.0','s:integer'),('256','s:unsignedByte')):
   with self.subTest(value=value,kind=kind),self.assertRaises(XBRLError):check_typed_contexts(*fixture(value,kind))
 def test_numeric_restrictions_are_bound_to_original_named_simple_types(self):
  types='<s:simpleType name="Amount"><s:restriction base="s:decimal"><s:minInclusive value="0"/><s:maxExclusive value="10"/></s:restriction></s:simpleType>'
  report=check_typed_contexts(*fixture('9.5','t:Amount',extras=types));self.assertEqual(report['contexts'][0]['typed_members'][0]['scalar_validation']['restriction_types'],['{'+NS+'}Amount'])
  for value in('-1','10'):
   with self.assertRaisesRegex(XBRLError,'facet_violation'):check_typed_contexts(*fixture(value,'t:Amount',extras=types))
 def test_complex_attributes_nil_and_anonymous_types_stay_explicitly_unsupported(self):
  cases=[fixture('<g:Code>7</g:Code>'),fixture('',member_attrs='xsi:nil="true"',domain_attrs='nillable="true"'),fixture('7',member_attrs='code="authored"'),fixture('7',kind='',domain_body='<s:simpleType><s:restriction base="s:integer"/></s:simpleType>'),fixture('A','s:QName'),fixture(axis_group='t:UnreviewedAxisGroup')]
  for args in cases:
   with self.subTest(args=args[0]['canonical_sha256']):
    report=check_typed_contexts(*args);self.assertEqual(report['status'],'UNSUPPORTED_TYPED_DOMAIN_SEMANTICS');self.assertEqual(report['unsupported_member_count'],1);self.assertEqual(report['contexts'][0]['typed_members'][0]['status'],'UNSUPPORTED')
 def test_domain_target_axis_kind_and_member_qname_are_not_guessed(self):
  cases=[fixture(member_name='Other'),fixture(axis_ref='#missing'),fixture(axis_ref='absent.xsd#typed'),fixture(domain_attrs='abstract="true"'),fixture(axis_group='x:item')]
  for args in cases:
   with self.assertRaises(XBRLError):check_typed_contexts(*args)
 def test_original_source_hashes_coverage_and_metadata_cannot_be_substituted(self):
  p,g,docs=fixture()
  with self.assertRaisesRegex(XBRLError,'original_schema_required'):check_typed_contexts(p,g,[])
  changed=copy.deepcopy(docs);changed[0]['raw']=changed[0]['raw'].replace(b'Code',b'Other');changed[0]['sha256']=hashlib.sha256(changed[0]['raw']).hexdigest()
  with self.assertRaisesRegex(XBRLError,'source_not_bound'):check_typed_contexts(p,g,changed)
  q,h=copy.deepcopy((p,g));h['concepts']['{'+NS+'}DeskAxis']['declaration']['typed_domain_ref']=BASE+'authored.xsd#assets';rebind(q,h)
  with self.assertRaisesRegex(XBRLError,'element_source_binding'):check_typed_contexts(q,h,docs)
  q,h=copy.deepcopy((p,g));h['concepts']['{'+NS+'}FabricatedAxis']=copy.deepcopy(h['concepts']['{'+NS+'}DeskAxis']);rebind(q,h)
  with self.assertRaisesRegex(XBRLError,'declaration_coverage'):check_typed_contexts(q,h,docs)
 def test_parsed_and_context_hash_binding_cannot_be_rewritten_silently(self):
  p,g,docs=fixture();q=copy.deepcopy(p);q['contexts']['I']['dimensions'][0]['member']['text']='8'
  with self.assertRaisesRegex(XBRLError,'input_identity'):check_typed_contexts(q,g,docs)
  q.pop('canonical_sha256');q['canonical_sha256']=digest(q)
  with self.assertRaisesRegex(XBRLError,'context_identity'):check_typed_contexts(q,g,docs)
  q=copy.deepcopy(p);q['dts_corroboration']['dts_sha256']='0'*64;q.pop('canonical_sha256');q['canonical_sha256']=digest(q)
  with self.assertRaisesRegex(XBRLError,'dts_binding_required'):check_typed_contexts(q,g,docs)
 def test_budget_profile_and_unclosed_dts_fail_before_any_promotion(self):
  p,g,docs=fixture()
  with self.assertRaisesRegex(XBRLError,'profile_unsupported'):check_typed_contexts(p,g,docs,profile='invented')
  with patch('terminal.stocks.xbrl_typed_dimensions.MAX_OUTPUT',100),self.assertRaisesRegex(XBRLError,'input_budget'):check_typed_contexts(p,g,docs)
  with patch('terminal.stocks.xbrl_typed_dimensions.MAX_RECORDS',0),self.assertRaisesRegex(XBRLError,'record_budget'):check_typed_contexts(p,g,docs)
  q,h=copy.deepcopy((p,g));h['structural_closure']=False;rebind(q,h)
  with self.assertRaisesRegex(XBRLError,'closure_required'):check_typed_contexts(q,h,docs)
 def test_observed_gate_precedes_original_xml_and_requires_permission_binding(self):
  p,g,docs=fixture();p['origin']=g['origin']='OBSERVED_OFFICIAL_RESPONSE';p['source']['origin']='OBSERVED_OFFICIAL_RESPONSE';rebind(p,g)
  with patch('terminal.stocks.xbrl_typed_dimensions.parse_xml',side_effect=AssertionError('NO_UNAPPROVED_XML')):
   with self.assertRaisesRegex(XBRLError,'not_approved'):check_typed_contexts(p,g,docs)
  with self.assertRaisesRegex(XBRLError,'permission_binding'):check_typed_contexts(p,g,docs,allow_observed=True)
  permission=hashlib.sha256(b'authored processing reference').hexdigest();p['source']['permission_reference_sha256']=g['permission_reference_sha256']=permission;rebind(p,g)
  self.assertEqual(check_typed_contexts(p,g,docs,allow_observed=True)['typed_member_count'],1)
 def test_no_typed_member_is_not_reported_as_complete_drs_acceptance(self):
  p,g,docs=fixture();p['contexts']['I']['dimensions']=[];context=p['contexts']['I'];context['semantic_sha256']=digest({k:context[k]for k in('issuer_cik','period','dimensions','opaque_segment')});p.pop('canonical_sha256');p['canonical_sha256']=digest(p)
  report=check_typed_contexts(p,g,docs);self.assertEqual(report['status'],'NO_TYPED_MEMBERS');self.assertEqual(report['contexts'],[]);self.assertFalse(report['complete_drs_validation'])

if __name__=='__main__':unittest.main(verbosity=2)
