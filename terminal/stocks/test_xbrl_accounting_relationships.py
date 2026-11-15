"""Source-bound standard definition arcs; no aliases inferred from labels or values."""
import copy,hashlib,unittest
from unittest.mock import patch
from .test_xbrl_instance import xml,manifest,NS
from .inline_xbrl import parse_filing
from .xbrl_dts import discover,EMBEDDED_PROFILE
from .xbrl_instance import selected_concepts,digest,canonical,XBRLError
from .xbrl_accounting_relationships import extract_accounting_relationships,ESSENCE,REQUIRES
BASE='https://authored.invalid/';ROLE=BASE+'role/source-equivalence'

def arc(before='a',after='b',*,kind=ESSENCE,attrs=''):
 return f'<l:definitionArc xl:type="arc" xl:arcrole="{kind}" xl:from="{before}" xl:to="{after}" {attrs}/>'
def fixture(arcs=None,*,left='1000',right='1000',facts=None,type_b='x:monetaryItemType',period_b='instant',balance_a='debit',balance_b='debit',embedded=False,extra=''):
 if facts is None:facts=('<g:Assets contextRef="I" unitRef="USD" decimals="INF">'+left+'</g:Assets>'if left is not None else'')+('<g:AliasAssets contextRef="I" unitRef="USD" decimals="INF">'+right+'</g:AliasAssets>'if right is not None else'')
 raw=xml(facts);m=manifest(raw)
 concepts=''.join(f'<s:element id="{id_}" name="{name}" type="{typ}" substitutionGroup="x:item" x:periodType="{period}"'+(f' x:balance="{balance}"'if balance else'')+'/>'for id_,name,typ,period,balance in [('assets','Assets','x:monetaryItemType','instant',balance_a),('alias','AliasAssets',type_b,period_b,balance_b)])
 link=('<l:definitionLink xl:type="extended" xl:role="'+ROLE+'"><l:loc xl:type="locator" xl:label="a" xl:href="authored.xsd#assets"/><l:loc xl:type="locator" xl:label="b" xl:href="authored.xsd#alias"/>'+(arc()if arcs is None else arcs)+extra+'</l:definitionLink>')
 base='<l:linkbase xmlns:l="http://www.xbrl.org/2003/linkbase" xmlns:xl="http://www.w3.org/1999/xlink">'+link+'</l:linkbase>'
 schema=('<s:schema xmlns:s="http://www.w3.org/2001/XMLSchema" xmlns:x="http://www.xbrl.org/2003/instance" xmlns:l="http://www.xbrl.org/2003/linkbase" xmlns:xl="http://www.w3.org/1999/xlink" targetNamespace="'+NS+'">'+concepts+'<s:annotation><s:appinfo>'+(base if embedded else'<l:linkbaseRef xl:type="simple" xl:href="definition.xml"/>')+'</s:appinfo></s:annotation></s:schema>').encode()
 docs=[{'uri':BASE+'authored.xsd','raw':schema,'sha256':hashlib.sha256(schema).hexdigest()}]
 if not embedded:docs.append({'uri':BASE+'definition.xml','raw':base.encode(),'sha256':hashlib.sha256(base.encode()).hexdigest()})
 profile=EMBEDDED_PROFILE if embedded else None;p=parse_filing(raw,m,selected_concepts(NS));g=discover(raw,BASE+'instance.xml',m['source_sha256'],docs,embedded_profile=profile)
 return p,g,raw,docs,{'manifest':m,'concepts':selected_concepts(NS),'instance_uri':BASE+'instance.xml','embedded_profile':profile}
def report(*args,**kwargs):
 p,g,raw,docs,options=fixture(*args,**kwargs);return extract_accounting_relationships(p,g,raw,docs,**options)
def check(r):return r['networks'][0]['arcs'][0]['checks'][0]

class AccountingRelationships(unittest.TestCase):
 def test_invalid_declared_period_cannot_claim_equal_source_values(self):
  p,g,raw,docs,options=fixture();raw=raw.replace(b'contextRef="I"',b'contextRef="D"');options['manifest']['source_sha256']=hashlib.sha256(raw).hexdigest();p=parse_filing(raw,options['manifest'],options['concepts']);g=discover(raw,options['instance_uri'],hashlib.sha256(raw).hexdigest(),docs)
  with self.assertRaisesRegex(XBRLError,'declared_period_conflict'):extract_accounting_relationships(p,g,raw,docs,**options)
 def test_abstract_source_facts_and_undeclared_period_are_not_equivalent(self):
  for mode,code in [('abstract','abstract_fact'),('period','alias_period_required')]:
   p,g,raw,docs,options=fixture();docs[0]['raw']=docs[0]['raw'].replace(b'substitutionGroup="x:item"',b'abstract="true" substitutionGroup="x:item"')if mode=='abstract'else docs[0]['raw'].replace(b'x:periodType="instant"',b'');docs[0]['sha256']=hashlib.sha256(docs[0]['raw']).hexdigest();g=discover(raw,options['instance_uri'],hashlib.sha256(raw).hexdigest(),docs)
   with self.subTest(mode=mode),self.assertRaisesRegex(XBRLError,code):extract_accounting_relationships(p,g,raw,docs,**options)
 def test_exact_sources_constraints_fact_ids_and_no_input_mutation(self):
  p,g,raw,docs,options=fixture();before=copy.deepcopy((p,g,docs,options));r=extract_accounting_relationships(p,g,raw,docs,**options);a=r['networks'][0]['arcs'][0]
  self.assertEqual(r['status'],'AVAILABLE');self.assertTrue(r['complete_definition_scope']);self.assertEqual(a['from'],'{'+NS+'}Assets');self.assertEqual(a['to'],'{'+NS+'}AliasAssets');self.assertEqual(check(r)['status'],'SUPPORTED_EQUAL');self.assertTrue(check(r)['standards_value_equality_established']);self.assertEqual(check(r)['source_fact_ids'],[f['source_fact_id']for f in p['facts']]);self.assertEqual(a['provenance'][0]['source_sha256'],docs[-1]['sha256']);self.assertEqual(r['source_audit']['status'],'VERIFIED_ORIGINAL_SOURCE_RECONSTRUCTION');self.assertFalse(r['gaap_aliases_inferred']);self.assertFalse(r['facts_inferred']);self.assertIsNone(r['selected_reported_value']);self.assertEqual(r['sha256'],digest({k:v for k,v in r.items()if k!='sha256'}));self.assertEqual((p,g,docs,options),before)
 def test_declared_type_period_and_present_balance_must_match(self):
  for kwargs,code in[({'type_b':'x:sharesItemType'},'type_conflict'),({'period_b':'duration'},'period_conflict'),({'balance_b':'credit'},'balance_conflict')]:
   with self.subTest(kwargs=kwargs),self.assertRaisesRegex(XBRLError,code):report(**kwargs)
  self.assertEqual(check(report(balance_b=None))['status'],'SUPPORTED_EQUAL')
 def test_prohibition_max_priority_reinstatement_and_equivalent_order(self):
  for arcs,count in[(arc()+arc(attrs='priority="2" use="prohibited"'),0),(arc()+arc(attrs='priority="2" use="prohibited"')+arc(attrs='priority="3"'),1)]:
   r=report(arcs);self.assertEqual(len(r['networks'][0]['arcs']),count);self.assertEqual(len(r['networks'][0]['suppressed']),1-count)
  a=report(arc(attrs='order="1.0"')+arc(attrs='order="+1" priority="2"'))['networks'][0]['arcs'][0];self.assertEqual(a['priority'],2);self.assertEqual(len(a['provenance']),2)
 def test_distinct_order_is_non_exempt_and_cannot_prohibit_other_order(self):
  r=report(arc(attrs='order="1"')+arc(attrs='order="2" priority="9" use="prohibited"'));n=r['networks'][0]
  self.assertEqual(len(n['arcs']),1);self.assertEqual(n['arcs'][0]['order'],{'numerator':'1','denominator':'1'});self.assertEqual(n['arcs'][0]['priority'],0);self.assertEqual(len(n['arcs'][0]['provenance']),1);self.assertEqual(len(n['suppressed']),1)
 def test_effective_essence_cycles_reject_but_requires_cycles_are_permitted(self):
  with self.assertRaisesRegex(XBRLError,'directed_cycle'):report(arc()+arc('b','a'))
  r=report(arc(kind=REQUIRES)+arc('b','a',kind=REQUIRES));self.assertEqual(len(r['networks'][0]['arcs']),2);self.assertTrue(all(a['checks'][0]['status']=='SATISFIED'for a in r['networks'][0]['arcs']))
 def test_missing_counterpart_keeps_original_fact_and_does_not_fill(self):
  r=report(right=None);c=check(r);self.assertEqual(c['status'],'MISSING_COUNTERPART');self.assertEqual(c['reason'],'ALIAS_NOT_REPORTED');self.assertEqual(len(c['essence_facts']),1);self.assertEqual(c['alias_facts'],[]);self.assertIsNone(c['selected_reported_value'])
 def test_differing_reported_values_retain_both_without_rounding_inference(self):
  c=check(report(right='1001'));self.assertEqual(c['status'],'CONFLICTING_REPORTED_VALUES');self.assertEqual(c['essence_facts'][0]['reported_value'],'1000');self.assertEqual(c['alias_facts'][0]['reported_value'],'1001');self.assertFalse(c['standards_value_equality_established'])
 def test_unit_and_context_mismatches_do_not_cross_join(self):
  facts='<x:context id="OLD"><x:entity><x:identifier scheme="http://www.sec.gov/CIK">0000320193</x:identifier></x:entity><x:period><x:instant>2022-12-31</x:instant></x:period></x:context><g:Assets contextRef="I" unitRef="USD">1000</g:Assets><g:AliasAssets contextRef="OLD" unitRef="USD">1000</g:AliasAssets>'
  r=report(facts=facts);self.assertEqual([c['status']for c in r['networks'][0]['arcs'][0]['checks']],['MISSING_COUNTERPART','MISSING_COUNTERPART'])
  p,g,raw,docs,options=fixture();raw=raw.replace(b'</x:xbrl>',b'<x:unit id="EUR"><x:measure>iso:EUR</x:measure></x:unit></x:xbrl>').replace(b'<g:AliasAssets contextRef="I" unitRef="USD"',b'<g:AliasAssets contextRef="I" unitRef="EUR"');options['manifest']=manifest(raw);p=parse_filing(raw,options['manifest'],options['concepts']);g=discover(raw,options['instance_uri'],hashlib.sha256(raw).hexdigest(),docs)
  c=check(extract_accounting_relationships(p,g,raw,docs,**options));self.assertEqual(c['status'],'UNSUPPORTED_ASPECTS');self.assertIn('UNIT_SEMANTIC_CONFLICT',c['reason'])
 def test_requires_element_uses_global_occurrence_not_matching_period_or_unit(self):
  facts='<g:Assets contextRef="I" unitRef="USD">1000</g:Assets><g:AliasAssets contextRef="D" unitRef="USD">300</g:AliasAssets>'
  self.assertEqual(check(report(arc(kind=REQUIRES),facts=facts,period_b='duration'))['status'],'SATISFIED');self.assertEqual(check(report(arc(kind=REQUIRES),right=None))['status'],'REQUIRED_ELEMENT_MISSING');self.assertEqual(check(report(arc(kind=REQUIRES),left=None))['status'],'NOT_TRIGGERED')
 def test_unknown_or_dimensional_definition_scope_cannot_be_ignored(self):
  for bad in(arc(kind='http://xbrl.org/int/dim/arcrole/dimension-domain'),arc(kind='https://authored.invalid/custom'),arc(attrs='custom="value"')):
   with self.assertRaisesRegex(XBRLError,'unsupported'):report(arc()+bad)
 def test_original_embedded_source_ordinals_are_real_and_profile_gated(self):
  r=report(embedded=True);a=r['networks'][0]['arcs'][0];self.assertEqual(a['provenance'][0]['source_uri'],BASE+'authored.xsd');self.assertGreater(a['provenance'][0]['arc_node_ordinal'],a['provenance'][0]['link_node_ordinal'])
  p,g,raw,docs,options=fixture(embedded=True);options['embedded_profile']=None
  with self.assertRaises(XBRLError):extract_accounting_relationships(p,g,raw,docs,**options)
 def test_rehashed_parsed_or_graph_mutation_is_rejected_by_original_source_audit(self):
  for which in('parsed','graph'):
   p,g,raw,docs,options=fixture()
   if which=='parsed':p['facts'][0]['value']='1001';p['canonical_sha256']=digest({k:v for k,v in p.items()if k!='canonical_sha256'})
   else:g['concepts']['{'+NS+'}AliasAssets']['declaration']['balance']='credit';g['canonical_sha256']=digest({k:v for k,v in g.items()if k!='canonical_sha256'})
   with self.assertRaisesRegex(XBRLError,'mismatch'):extract_accounting_relationships(p,g,raw,docs,**options)
 def test_resource_limits_and_profile_are_fail_closed(self):
  args=fixture();p,g,raw,docs,options=args
  with patch('terminal.stocks.xbrl_accounting_relationships.MAX_ARCS',0),self.assertRaisesRegex(XBRLError,'budget'):extract_accounting_relationships(p,g,raw,docs,**options)
  with patch('terminal.stocks.xbrl_accounting_relationships.MAX_OUTPUT',1),self.assertRaisesRegex(XBRLError,'output_budget'):extract_accounting_relationships(p,g,raw,docs,**options)
  with self.assertRaisesRegex(XBRLError,'profile_unsupported'):extract_accounting_relationships(p,g,raw,docs,profile='invented',**options)
 def test_finite_accuracy_and_conflicting_duplicates_never_assert_full_v_equality(self):
  p,g,raw,docs,options=fixture();raw=raw.replace(b'decimals="INF"',b'decimals="0"');options['manifest']=manifest(raw);p=parse_filing(raw,options['manifest'],options['concepts']);g=discover(raw,options['instance_uri'],hashlib.sha256(raw).hexdigest(),docs)
  c=check(extract_accounting_relationships(p,g,raw,docs,**options));self.assertEqual(c['status'],'SUPPORTED_EQUAL');self.assertFalse(c['standards_value_equality_established'])
  facts='<g:Assets contextRef="I" unitRef="USD" decimals="INF">1000</g:Assets><g:AliasAssets contextRef="I" unitRef="USD" decimals="INF">1000</g:AliasAssets><g:AliasAssets contextRef="I" unitRef="USD" decimals="INF">1001</g:AliasAssets>'
  c=check(report(facts=facts));self.assertEqual(c['status'],'CONFLICTING_REPORTED_VALUES');self.assertEqual(len(c['source_fact_ids']),3);self.assertEqual([f['reported_value']for f in c['alias_facts']],['1000','1001']);self.assertIsNone(c['selected_reported_value'])
 def test_nil_members_remain_unavailable_and_global_requires_presence_counts_nil(self):
  for kind in(ESSENCE,REQUIRES):
   p,g,raw,docs,options=fixture(arc(kind=kind));raw=raw.replace(b'>1000</g:AliasAssets>',b' xsi:nil="true"/>');options['manifest']=manifest(raw);docs[0]['raw']=docs[0]['raw'].replace(b'name="AliasAssets"',b'name="AliasAssets" nillable="true"');docs[0]['sha256']=hashlib.sha256(docs[0]['raw']).hexdigest();p=parse_filing(raw,options['manifest'],options['concepts']);g=discover(raw,options['instance_uri'],hashlib.sha256(raw).hexdigest(),docs);c=check(extract_accounting_relationships(p,g,raw,docs,**options))
   if kind==ESSENCE:self.assertEqual(c['status'],'UNSUPPORTED_ASPECTS');self.assertIn('NIL_PARTICIPANT',c['reason']);self.assertIsNone(c['alias_facts'][0]['reported_value'])
   else:self.assertEqual(c['status'],'SATISFIED');self.assertEqual(len(c['to_fact_ids']),1)
 def test_identifier_lexical_context_differences_do_not_merge_by_normalized_cik(self):
  p,g,raw,docs,options=fixture();start=raw.index(b'<x:context id="I">');end=raw.index(b'</x:context>',start)+len(b'</x:context>');other=raw[start:end].replace(b'id="I"',b'id="OTHER"').replace(b'>0000320193<',b'>320193<');raw=raw.replace(b'</x:xbrl>',other+b'</x:xbrl>').replace(b'<g:AliasAssets contextRef="I"',b'<g:AliasAssets contextRef="OTHER"');options['manifest']=manifest(raw);p=parse_filing(raw,options['manifest'],options['concepts']);g=discover(raw,options['instance_uri'],hashlib.sha256(raw).hexdigest(),docs)
  self.assertEqual(p['contexts']['I']['semantic_sha256'],p['contexts']['OTHER']['semantic_sha256']);r=extract_accounting_relationships(p,g,raw,docs,**options);checks=r['networks'][0]['arcs'][0]['checks'];self.assertEqual(len(checks),2);self.assertTrue(all(c['status']=='MISSING_COUNTERPART'for c in checks))
 def test_no_definition_arcs_are_available_without_fabricated_mapping(self):
  r=report('');self.assertEqual(r['networks'],[]);self.assertTrue(r['complete_definition_scope']);self.assertFalse(r['gaap_aliases_inferred'])

if __name__=='__main__':unittest.main(verbosity=2)
