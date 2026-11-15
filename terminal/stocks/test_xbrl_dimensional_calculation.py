"""Authored explicit-dimension report calculations;no observed source corpus."""
import copy,hashlib,unittest
from unittest.mock import patch
from .test_xbrl_statements import entry as statement_entry,ROLE,NS
from .test_xbrl_dimensions import arc
from .test_xbrl_dts import document
from .xbrl_instance import digest,XBRLError
from .inline_xbrl import parse_filing
from .xbrl_dts import discover,discover_inline_set
from .xbrl_binding import bind_declarations
from .xbrl_dimensional_calculation import bind_dimensional_calculation_report
from .xbrl_calculation_report import bind_calculation_report
from .xbrl_dimensions import INHERITED_PROFILE,corroborate

def fixture(member='North',*,default=False,extra='',schema_extra='',closed=True):
 segment=''if member is None else'<x:segment><d:explicitMember dimension="g:RegionAxis">g:'+member+'</d:explicitMember></x:segment>'
 e=statement_entry(context_extra=segment);raw=e['raw'].replace(b'unitRef="USD">',b'unitRef="USD" decimals="0">');e['raw']=raw;e['manifest']['source_sha256']=hashlib.sha256(raw).hexdigest()
 components=''.join(f'<s:element id="{id_}" name="{name}" type="x:stringItemType" substitutionGroup="{group}" abstract="{abstract}" x:periodType="instant"/>'for id_,name,group,abstract in [('primary','Primary','x:item','true'),('cube','Cube','xd:hypercubeItem','true'),('axis','RegionAxis','xd:dimensionItem','true'),('domain','Domain','x:item','true'),('north','North','x:item','false'),('south','South','x:item','false')])
 schema=e['documents'][0]['raw'].replace(b'<s:schema ',b'<s:schema xmlns:xd="http://xbrl.org/2005/xbrldt" ',1).replace(b'</s:schema>',(components+schema_extra+'<s:annotation><s:appinfo><l:linkbaseRef xl:type="simple" xl:href="dimensions.xml"/></s:appinfo></s:annotation></s:schema>').encode());e['documents'][0]=document('authored.xsd',schema)
 loc=''.join(f'<l:loc xl:type="locator" xl:label="{id_}" xl:href="authored.xsd#{id_}"/>'for id_ in('primary','assets','cash','liabilities','cube','axis','domain','north','south'))
 links=arc('all','primary','cube',f'xd:closed="{str(closed).lower()}" xd:contextElement="segment"')+''.join(arc('domain-member','primary',n)for n in('assets','cash','liabilities'))+arc('hypercube-dimension','cube','axis')+arc('dimension-domain','axis','domain')+arc('domain-member','domain','north')+arc('domain-member','domain','south')+(arc('dimension-default','axis','south')if default else'')+extra
 wire=f'<l:linkbase xmlns:l="http://www.xbrl.org/2003/linkbase" xmlns:xl="http://www.w3.org/1999/xlink" xmlns:xd="http://xbrl.org/2005/xbrldt"><l:definitionLink xl:type="extended" xl:role="{ROLE}">{loc}{links}</l:definitionLink></l:linkbase>'.encode();e['documents'].append(document('dimensions.xml',wire));return e

def inputs(e=None):
 e=e or fixture();p=parse_filing(e['raw'],e['manifest'],e['concepts']);g=discover(e['raw'],e['instance_uri'],e['manifest']['source_sha256'],e['documents']);return p,g

def report(e=None,**kw):return bind_dimensional_calculation_report(*inputs(e),**kw)
def rehash(v):v['canonical_sha256']=digest({k:x for k,x in v.items()if k!='canonical_sha256'});return v
def raw_change(e,a,b):
 e=copy.deepcopy(e);e['raw']=e['raw'].replace(a,b);e['manifest']['source_sha256']=hashlib.sha256(e['raw']).hexdigest();return e

class DimensionalCalculations(unittest.TestCase):
 def test_explicit_inherited_aspects_bind_exact_math_with_original_ids(self):
  p,g=inputs();before=copy.deepcopy((p,g));r=bind_dimensional_calculation_report(p,g);self.assertEqual(r['status'],'AVAILABLE');b=r['bindings'][0];self.assertEqual(b['calculation']['status'],'CALCULATION_COMPATIBLE');self.assertEqual(b['aspects']['dimensions'],[{'dimension':'{'+NS+'}RegionAxis','member':'{'+NS+'}North'}]);self.assertEqual((p,g),before);self.assertEqual(r['sha256'],digest({k:v for k,v in r.items()if k!='sha256'}));self.assertEqual(b['source_context_sha256s'],[p['contexts']['I']['semantic_sha256']]);self.assertIsNone(r['selected_reported_value'])
 def test_valid_defaults_normalize_aspects_without_mutating_source_contexts(self):
  p,g=inputs(fixture(None,default=True));before=copy.deepcopy(p);r=bind_dimensional_calculation_report(p,g);axis='{'+NS+'}RegionAxis';self.assertEqual(r['global_default_dimensions'],{axis:'{'+NS+'}South'});self.assertEqual(p['contexts']['I']['dimensions'],[]);self.assertEqual(p,before);self.assertTrue(all(v['implicit_default_dimensions']==r['global_default_dimensions']for v in r['fact_provenance'].values()));self.assertEqual(r['default_provenance'][axis]['source_sha256'],g['documents'][-1]['sha256']if g['documents'][-1]['uri'].endswith('dimensions.xml')else next(d['sha256']for d in g['documents']if d['uri'].endswith('dimensions.xml')))
 def test_global_defaults_not_just_defaults_of_applicable_cubes_are_normalized(self):
  names=[('other','OtherAxis','xd:dimensionItem','true'),('otherdomain','OtherDomain','x:item','true'),('othermember','OtherDefault','x:item','false')];schema=''.join(f'<s:element id="{i}" name="{n}" substitutionGroup="{g}" abstract="{a}" x:periodType="instant"/>'for i,n,g,a in names);loc=''.join(f'<l:loc xl:type="locator" xl:label="{i}" xl:href="authored.xsd#{i}"/>'for i,*_ in names);e=fixture(schema_extra=schema,extra=loc+arc('dimension-domain','other','otherdomain')+arc('domain-member','otherdomain','othermember')+arc('dimension-default','other','othermember'));p,g=inputs(e);r=bind_dimensional_calculation_report(p,g)
  axis='{'+NS+'}OtherAxis';self.assertEqual(r['global_default_dimensions'][axis],'{'+NS+'}OtherDefault');self.assertTrue(all(axis in v['implicit_default_dimensions']for v in r['fact_provenance'].values()));self.assertTrue(all(axis not in v['drs_validation']['used_defaults']for v in r['fact_provenance'].values()))
 def test_different_explicit_members_do_not_join_into_a_calculation(self):
  e=fixture();raw=e['raw'];start=raw.index(b'<x:context id="I">');end=raw.index(b'</x:context>',start)+len(b'</x:context>');other=raw[start:end].replace(b'id="I"',b'id="SOUTH"').replace(b'g:North',b'g:South');e=raw_change(e,b'</x:xbrl>',other+b'</x:xbrl>');e=raw_change(e,b'<g:Liabilities contextRef="I"',b'<g:Liabilities contextRef="SOUTH"');r=report(e);self.assertEqual(r['bindings'][0]['calculation']['status'],'INCOMPLETE');self.assertEqual(r['bindings'][0]['missing_concepts'],['{'+NS+'}Liabilities'])
 def test_explicit_occurrence_of_default_member_is_invalid(self):
  with self.assertRaisesRegex(XBRLError,'explicit_default_member'):report(fixture('South',default=True))
 def test_unknown_or_conflicting_global_defaults_reject_even_when_unused(self):
  with self.assertRaisesRegex(XBRLError,'ambiguous_global_default'):report(fixture(default=True,extra=arc('dimension-default','axis','north')))
  with self.assertRaises(XBRLError):report(fixture(extra=arc('dimension-default','axis','primary')))
 def test_unsupported_typed_opaque_negative_and_cross_role_are_not_ignored(self):
  e=fixture();e['documents'][0]=document('authored.xsd',e['documents'][0]['raw'].replace(b'name="RegionAxis"',b'xd:typedDomainRef="#domain" name="RegionAxis"'))
  with self.assertRaises(XBRLError):report(e)
  for extra in(arc('notAll','primary','cube','xd:contextElement="segment"'),arc('domain-member','primary','assets','xd:targetRole="urn:elsewhere"')):
   with self.assertRaises(XBRLError):report(fixture(extra=extra))
  e=raw_change(fixture(),b'</x:segment>',b'<g:Opaque>value</g:Opaque></x:segment>')
  with self.assertRaises(XBRLError):report(e)
 def test_untrusted_supplied_dimensional_proof_is_recomputed(self):
  p,g=inputs();bound=bind_declarations(p,g);bound['dts_corroboration']['dimensional_validation']={'profile':'invented','facts':[]};rehash(bound);r=bind_dimensional_calculation_report(bound,g);expected=corroborate(bind_declarations(p,g),g,profile=INHERITED_PROFILE)['dts_corroboration']['dimensional_validation'];self.assertEqual(r['drs_proof_sha256'],digest(expected));self.assertEqual(r['bindings'][0]['calculation']['status'],'CALCULATION_COMPATIBLE')
 def test_derived_artifact_cannot_substitute_for_original(self):
  p,g=inputs();derived=corroborate(bind_declarations(p,g),g,profile=INHERITED_PROFILE)
  with self.assertRaisesRegex(XBRLError,'original_artifact_required'):bind_dimensional_calculation_report(derived,g)
 def test_context_and_unit_semantic_hashes_and_source_ids_are_revalidated(self):
  for kind in('context','unit','fact'):
   p,g=inputs()
   if kind=='context':p['contexts']['I']['semantic_sha256']='0'*64
   elif kind=='unit':p['units']['USD']['semantic_sha256']='0'*64
   else:p['facts'][0]['source_fact_id']='0'*64
   rehash(p)
   with self.assertRaises(XBRLError):bind_dimensional_calculation_report(p,g)
 def test_compatible_and_disjoint_duplicates_keep_every_reported_value(self):
  for value,status in(('401','CALCULATION_COMPATIBLE'),('404','UNSUPPORTED_ACCURACY')):
   e=raw_change(fixture(),b'</x:xbrl>',f'<g:Liabilities contextRef="I" unitRef="USD" decimals="0">{value}</g:Liabilities></x:xbrl>'.encode());r=report(e);point=r['bindings'][0]['data_points']['{'+NS+'}Liabilities'];self.assertEqual(r['bindings'][0]['calculation']['status'],status);self.assertEqual([f['reported_value']for f in point['facts']],['400',value]);self.assertIsNone(point['selected_reported_value'])
 def test_missing_accuracy_and_nil_are_not_zero(self):
  e=raw_change(fixture(),b'unitRef="USD" decimals="0">600',b'unitRef="USD">600');self.assertEqual(report(e)['bindings'][0]['calculation']['status'],'UNSUPPORTED_ACCURACY')
  e=fixture();e['documents'][0]=document('authored.xsd',e['documents'][0]['raw'].replace(b'name="Liabilities"',b'nillable="true" name="Liabilities"'));e=raw_change(e,b'>400</g:Liabilities>',b' xsi:nil="true"/>');r=report(e);self.assertEqual(r['bindings'][0]['data_points']['{'+NS+'}Liabilities']['reason'],'NIL_ONLY')
 def test_modes_are_explicit_legacy_binder_and_default_statement_unchanged(self):
  p,g=inputs();before=copy.deepcopy((p,g));r=bind_dimensional_calculation_report(p,g,rounding_mode='truncation');self.assertEqual(r['rounding_mode'],'truncation');self.assertEqual((p,g),before)
  with self.assertRaisesRegex(XBRLError,'dts_or_dimension_scope'):bind_calculation_report(p,g)
  with self.assertRaisesRegex(XBRLError,'profile_unsupported'):bind_dimensional_calculation_report(p,g,dimensional_profile='future')
 def test_output_and_binding_counts_are_bounded(self):
  p,g=inputs()
  with patch('terminal.stocks.xbrl_dimensional_calculation.MAX_BINDINGS',0),self.assertRaisesRegex(XBRLError,'output_budget'):bind_dimensional_calculation_report(p,g)
  with patch('terminal.stocks.xbrl_dimensional_calculation.MAX_OUTPUT',1),self.assertRaisesRegex(XBRLError,'output_budget'):bind_dimensional_calculation_report(p,g)
 def test_default_members_never_appear_as_reported_oim_dimensions(self):
  p,g=inputs(fixture(None,default=True));r=bind_dimensional_calculation_report(p,g);a=r['bindings'][0]['aspects'];self.assertEqual(a['dimensions'],[]);self.assertEqual(a['effective_dimension_values'],[{'dimension':'{'+NS+'}RegionAxis','member':'{'+NS+'}South'}]);self.assertEqual(p['contexts']['I']['dimensions'],[])
 def test_period_and_entity_semantics_are_not_replaced_by_dimension_alignment(self):
  e=fixture();raw=e['raw'];start=raw.index(b'<x:context id="I">');end=raw.index(b'</x:context>',start)+len(b'</x:context>');other=raw[start:end].replace(b'id="I"',b'id="OLDER"').replace(b'2023-12-31',b'2022-12-31');e=raw_change(e,b'</x:xbrl>',other+b'</x:xbrl>');e=raw_change(e,b'<g:Liabilities contextRef="I"',b'<g:Liabilities contextRef="OLDER"');self.assertEqual(report(e)['bindings'][0]['calculation']['status'],'INCOMPLETE')
  p,g=inputs();p['contexts']['I']['issuer_cik']='0000000001';p['contexts']['I']['semantic_sha256']=digest({k:p['contexts']['I'][k]for k in('issuer_cik','period','dimensions','opaque_segment')});rehash(p)
  with self.assertRaises(XBRLError):bind_dimensional_calculation_report(p,g)
 def test_matching_context_and_unit_aliases_preserve_distinct_source_refs(self):
  e=fixture();raw=e['raw'];start=raw.index(b'<x:context id="I">');end=raw.index(b'</x:context>',start)+len(b'</x:context>');alias=raw[start:end].replace(b'id="I"',b'id="ALIAS"');e=raw_change(e,b'</x:xbrl>',alias+b'<x:unit id="USD_ALIAS"><x:measure>iso:USD</x:measure></x:unit></x:xbrl>');e=raw_change(e,b'<g:Liabilities contextRef="I" unitRef="USD"',b'<g:Liabilities contextRef="ALIAS" unitRef="USD_ALIAS"');r=report(e);self.assertEqual(r['bindings'][0]['calculation']['status'],'CALCULATION_COMPATIBLE');self.assertEqual({v['context_ref']for v in r['fact_provenance'].values()},{'I','ALIAS'});self.assertEqual({v['unit_ref']for v in r['fact_provenance'].values()},{'USD','USD_ALIAS'})
 def test_unused_global_default_domain_cycle_and_typed_axis_are_rejected(self):
  names=[('other','OtherAxis','xd:dimensionItem','true'),('otherdomain','OtherDomain','x:item','true'),('othermember','OtherDefault','x:item','false')];schema=''.join(f'<s:element id="{i}" name="{n}" substitutionGroup="{g}" abstract="{a}" x:periodType="instant"/>'for i,n,g,a in names);loc=''.join(f'<l:loc xl:type="locator" xl:label="{i}" xl:href="authored.xsd#{i}"/>'for i,*_ in names);extra=loc+arc('dimension-domain','other','otherdomain')+arc('domain-member','otherdomain','othermember')+arc('domain-member','othermember','otherdomain')+arc('dimension-default','other','othermember')
  with self.assertRaisesRegex(XBRLError,'default_domain_cycle'):report(fixture(schema_extra=schema,extra=extra))
  schema=schema.replace('name="OtherAxis"','xd:typedDomainRef="#otherdomain" name="OtherAxis"');extra=extra.replace(arc('domain-member','othermember','otherdomain'),'')
  with self.assertRaisesRegex(XBRLError,'declaration_scope'):report(fixture(schema_extra=schema,extra=extra))
 def test_original_inline_document_set_and_fact_segment_lineage_survive(self):
  from .test_inline_set import html,doc
  from .inline_set import parse_document_set
  e=fixture();wire=e['raw'].decode();resources=wire[wire.index('<x:context'):wire.index('<g:Assets')];facts=''.join(f'<ix:nonFraction name="g:{name}" contextRef="I" unitRef="USD" decimals="0">{value}</ix:nonFraction>'for name,value in(('Assets','1000'),('CashAndCashEquivalentsAtCarryingValue','600'),('Liabilities','400')));page=html(facts,resources=True).decode();start=page.index('<x:context');end=page.index('</ix:resources>');page=(page[:start]+resources+page[end:]).replace('<html ','<html xmlns:d="http://xbrl.org/2006/xbrldi" ',1);p=parse_document_set([doc('a.xhtml',page.encode()),doc('b.xhtml',html(''))],e['concepts']);g=discover_inline_set(p,e['documents']);before=copy.deepcopy(p);r=bind_dimensional_calculation_report(p,g);self.assertEqual(r['bindings'][0]['calculation']['status'],'CALCULATION_COMPATIBLE');self.assertTrue(all(v['inline_source_segments']for v in r['fact_provenance'].values()));self.assertEqual(p,before)
 def test_incompatible_units_and_mixed_report_container_scope_reject(self):
  e=raw_change(fixture(),b'</x:xbrl>',b'<x:unit id="EUR"><x:measure>iso:EUR</x:measure></x:unit></x:xbrl>');e=raw_change(e,b'<g:Liabilities contextRef="I" unitRef="USD"',b'<g:Liabilities contextRef="I" unitRef="EUR"')
  with self.assertRaisesRegex(XBRLError,'participant_drs_proof_required'):report(e)
  p,g=inputs();p['contexts']['D']['dimensions']=copy.deepcopy(p['contexts']['I']['dimensions']);p['contexts']['D']['dimensions'][0]['context_element']='scenario';p['contexts']['D']['semantic_sha256']=digest({k:p['contexts']['D'][k]for k in('issuer_cik','period','dimensions','opaque_segment')});rehash(p)
  with self.assertRaisesRegex(XBRLError,'mixed_context_placement'):bind_dimensional_calculation_report(p,g)
 def test_dts_calculation_role_and_provenance_are_not_inferred(self):
  p,g=inputs();rels=g['effective_relationships'];n=copy.deepcopy(next(n for n in rels['networks']if n['kind']=='calculation'));n['role']='urn:second';rels['networks'].append(n);rels['sha256']=digest({k:v for k,v in rels.items()if k!='sha256'});rehash(g)
  with self.assertRaisesRegex(XBRLError,'role_ambiguous'):bind_dimensional_calculation_report(p,g)
  self.assertEqual(bind_dimensional_calculation_report(p,g,role=ROLE)['role'],ROLE)
  p,g=inputs();net=next(n for n in g['effective_relationships']['networks']if n['kind']=='calculation');net['arcs'][0]['provenance'][0]['source_sha256']='0'*64;g['effective_relationships']['sha256']=digest({k:v for k,v in g['effective_relationships'].items()if k!='sha256'});rehash(g)
  with self.assertRaisesRegex(XBRLError,'arc_lineage'):bind_dimensional_calculation_report(p,g)
