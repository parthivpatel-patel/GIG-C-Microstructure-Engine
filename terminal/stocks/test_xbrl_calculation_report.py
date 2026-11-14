"""Adversarial report binding over authored original XBRL and supplied DTS."""
import copy,hashlib,unittest
from unittest.mock import patch
from .test_xbrl_statement_v2 import extension,EXT
from .test_xbrl_statements import ROLE,collection,LATE
from .test_xbrl_dts import document
from .xbrl_instance import digest,XBRLError
from .inline_xbrl import parse_filing
from .xbrl_dts import discover,discover_inline_set
from .xbrl_binding import bind_declarations
from .xbrl_calculation_report import bind_calculation_report


def inputs(e=None):
 e=e or extension();p=parse_filing(e['raw'],e['manifest'],e['concepts']);g=discover(e['raw'],e['instance_uri'],e['manifest']['source_sha256'],e['documents']);return p,g

def report(e=None,**kwargs):return bind_calculation_report(*inputs(e),**kwargs)
def rehash(v,key='canonical_sha256'):v[key]=digest({k:x for k,x in v.items()if k!=key});return v

def change(e,old,new):
 e=copy.deepcopy(e);e['raw']=e['raw'].replace(old,new);e['manifest']['source_sha256']=hashlib.sha256(e['raw']).hexdigest();return e

class ReportCalculationBinding(unittest.TestCase):
 def test_original_source_dts_arc_and_fact_identities_bind_exact_math(self):
  p,g=inputs();before=copy.deepcopy((p,g));r=bind_calculation_report(p,g,role=ROLE);b=r['bindings'][0]
  self.assertEqual(r['status'],'AVAILABLE');self.assertEqual(b['calculation']['status'],'CALCULATION_COMPATIBLE');self.assertEqual(r['parsed_sha256'],p['canonical_sha256']);self.assertEqual(r['dts_sha256'],g['canonical_sha256']);self.assertEqual(r['sha256'],digest({k:v for k,v in r.items()if k!='sha256'}));self.assertEqual((p,g),before)
  ids=b['calculation']['source_fact_ids'];self.assertEqual(set(ids),set(r['fact_provenance']));self.assertTrue(all(r['fact_provenance'][i]['declaration_documents']for i in ids));self.assertEqual(len(b['relationship_provenance']),2);self.assertIsNone(r['selected_reported_value'])
 def test_bound_artifact_supported_without_overriding_its_dts_identity(self):
  p,g=inputs();bound=bind_declarations(p,g);r=bind_calculation_report(bound,g);self.assertEqual(r['parsed_sha256'],bound['canonical_sha256']);self.assertEqual(r['bindings'][0]['calculation']['status'],'CALCULATION_COMPATIBLE')
  bound['dts_corroboration']['dts_sha256']='0'*64;rehash(bound)
  with self.assertRaisesRegex(XBRLError,'existing_binding'):bind_calculation_report(bound,g)
 def test_original_or_graph_corruption_and_cross_source_dts_reject(self):
  p,g=inputs()
  for which in('parsed','graph'):
   a,b=copy.deepcopy((p,g));(a if which=='parsed'else b)['canonical_sha256']='0'*64
   with self.assertRaisesRegex(XBRLError,'identity'):bind_calculation_report(a,b)
  for malformed in(None,False,12,[]):
   bad=copy.deepcopy(g);bad['canonical_sha256']=malformed
   with self.assertRaisesRegex(XBRLError,'dts_identity'):bind_calculation_report(p,bad)
  _,other=inputs(extension(value='399'))
  with self.assertRaisesRegex(XBRLError,'source_scope'):bind_calculation_report(p,other)
 def test_no_context_or_unit_cross_join_creates_a_sum(self):
  for old,new in((b'contextRef="I" unitRef="USD" decimals="0">400',b'contextRef="D" unitRef="USD" decimals="0">400'),(b'unitRef="USD" decimals="0">400',b'unitRef="EUR" decimals="0">400')):
   e=extension()
   if b'EUR'in new:e=change(e,b'</x:xbrl>',b'<x:unit id="EUR"><x:measure>iso:EUR</x:measure></x:unit></x:xbrl>')
   e=change(e,old,new);r=report(e);self.assertEqual(r['bindings'][0]['calculation']['status'],'INCOMPLETE');self.assertIn('{'+EXT+'}CompanyLiquidity',r['bindings'][0]['missing_concepts'])
 def test_context_aliases_group_without_selecting_differing_source_values(self):
  e=extension(extra='<ext:CompanyLiquidity contextRef="ALIAS" unitRef="USD" decimals="0">401</ext:CompanyLiquidity>');raw=e['raw'];start=raw.index(b'<x:context id="I">');end=raw.index(b'</x:context>',start)+len(b'</x:context>');alias=raw[start:end].replace(b'id="I"',b'id="ALIAS"');e=change(e,b'</x:xbrl>',alias+b'</x:xbrl>');r=report(e);point=r['bindings'][0]['data_points']['{'+EXT+'}CompanyLiquidity']
  self.assertEqual(point['status'],'INTERVAL_COMPATIBLE');self.assertFalse(point['numeric_values_equal']);self.assertEqual([f['reported_value']for f in point['facts']],['400','401']);self.assertIsNone(point['selected_reported_value']);self.assertEqual({r['fact_provenance'][i]['context_ref']for i in point['source_fact_ids']},{'I','ALIAS'})
 def test_disjoint_duplicate_and_excess_digits_never_select_a_fact(self):
  e=extension(extra='<ext:CompanyLiquidity contextRef="I" unitRef="USD" decimals="0">404</ext:CompanyLiquidity>');r=report(e);self.assertEqual(r['bindings'][0]['calculation']['status'],'UNSUPPORTED_ACCURACY');self.assertEqual(r['bindings'][0]['data_points']['{'+EXT+'}CompanyLiquidity']['status'],'INCONSISTENT_DUPLICATES')
  e=extension(value='400.25');r=report(e);check=r['bindings'][0]['calculation'];self.assertEqual(check['status'],'UNSUPPORTED_ACCURACY');self.assertEqual(check['source_error_codes'],['calc11e:excessDigits'])
 def test_rounding_mode_changes_boundary_diagnostic_without_rewriting_sources(self):
  e=extension(value='399');p,g=inputs(e);a=bind_calculation_report(p,g);b=bind_calculation_report(p,g,rounding_mode='truncation');self.assertEqual(a['bindings'][0]['calculation']['status'],'CALCULATION_COMPATIBLE');self.assertEqual(b['rounding_mode'],'truncation');self.assertEqual(p,inputs(e)[0]);self.assertEqual(set(a['fact_provenance']),set(b['fact_provenance']))
 def test_nil_and_missing_accuracy_are_explicit_without_zero_synthesis(self):
  e=change(extension(),b'>400</ext:CompanyLiquidity>',b' xsi:nil="true"/>');r=report(e);self.assertEqual(r['bindings'][0]['calculation']['status'],'UNSUPPORTED_ACCURACY');point=r['bindings'][0]['data_points']['{'+EXT+'}CompanyLiquidity'];self.assertEqual(point['reason'],'NIL_ONLY');self.assertIsNone(point['facts'][0]['reported_value'])
  e=change(extension(),b'unitRef="USD" decimals="0">600',b'unitRef="USD">600');self.assertEqual(report(e)['bindings'][0]['calculation']['status'],'UNSUPPORTED_ACCURACY')
 def test_dimensioned_or_opaque_contexts_are_excluded_explicitly(self):
  for extra in('<x:segment><d:explicitMember dimension="ext:RegionAxis">ext:NorthMember</d:explicitMember></x:segment>','<x:segment><ext:Opaque>value</ext:Opaque></x:segment>'):
   r=report(extension(context_extra=extra));self.assertEqual(r['status'],'UNAVAILABLE');self.assertEqual(r['reason'],'NO_SUPPORTED_PARENT_DATA_POINTS');self.assertEqual(len(r['excluded_facts']),3);self.assertTrue(all(x['reason']=='DIMENSIONAL_OPAQUE_OR_FOREVER_CONTEXT_OUTSIDE_PROFILE'for x in r['excluded_facts']))
 def test_definition_defaults_or_unclosed_dts_cannot_be_silently_ignored(self):
  for kind in('definition','unresolved','closure'):
   p,g=inputs()
   if kind=='definition':g['definition']=[{'source_uri':'https://authored.invalid/x.xml'}]
   elif kind=='unresolved':g['unresolved']=[{'uri':'https://authored.invalid/x.xsd'}]
   else:g['structural_closure']=False
   rehash(g)
   with self.assertRaisesRegex(XBRLError,'dts_or_dimension_scope'):bind_calculation_report(p,g)
 def test_role_ambiguity_missing_role_and_unusable_graph_reject(self):
  p,g=inputs();g2=copy.deepcopy(g);n=next(n for n in g2['effective_relationships']['networks']if n['kind']=='calculation');clone=copy.deepcopy(n);clone['role']='https://authored.invalid/other';g2['effective_relationships']['networks'].append(clone);rehash(g2['effective_relationships'],'sha256');rehash(g2)
  with self.assertRaisesRegex(XBRLError,'role_ambiguous'):bind_calculation_report(p,g2)
  self.assertEqual(bind_calculation_report(p,g2,role=ROLE)['role'],ROLE)
  with self.assertRaisesRegex(XBRLError,'role_ambiguous'):bind_calculation_report(p,g,role='missing')
  n=next(n for n in g['effective_relationships']['networks']if n['kind']=='calculation');n['usable']=False;n['issues']=['DIRECTED_RELATIONSHIP_CYCLE'];rehash(g['effective_relationships'],'sha256');rehash(g)
  with self.assertRaisesRegex(XBRLError,'network_unsupported'):bind_calculation_report(p,g)
 def test_effective_graph_hash_and_arc_source_binding_are_revalidated(self):
  p,g=inputs();g['effective_relationships']['sha256']='0'*64;rehash(g)
  with self.assertRaisesRegex(XBRLError,'relationship_identity'):bind_calculation_report(p,g)
  p,g=inputs();net=next(n for n in g['effective_relationships']['networks']if n['kind']=='calculation');net['arcs'][0]['provenance'][0]['source_sha256']='0'*64;rehash(g['effective_relationships'],'sha256');rehash(g)
  with self.assertRaisesRegex(XBRLError,'arc_lineage'):bind_calculation_report(p,g)
 def test_context_unit_and_source_fact_semantic_identities_are_revalidated(self):
  for kind in('context','unit','fact'):
   p,g=inputs()
   if kind=='context':p['contexts']['I']['semantic_sha256']='0'*64
   elif kind=='unit':p['units']['USD']['semantic_sha256']='0'*64
   else:p['facts'][0]['source_fact_id']='0'*64
   rehash(p)
   with self.assertRaisesRegex(XBRLError,'identity'):bind_calculation_report(p,g)
 def test_unknown_numeric_extension_type_does_not_gain_a_value(self):
  r=report(extension(kind='t:Unknown'));self.assertEqual(r['bindings'][0]['calculation']['status'],'INCOMPLETE');self.assertEqual(r['excluded_facts'][0]['reason'],'NUMERIC_DECLARATION_OR_VALUE_UNSUPPORTED');self.assertNotIn('{'+EXT+'}CompanyLiquidity',r['bindings'][0]['data_points'])
 def test_legacy_displayed_conflict_and_statement_output_remain_unchanged(self):
  e=extension(extra='<ext:CompanyLiquidity contextRef="I" unitRef="USD" decimals="0">401</ext:CompanyLiquidity>');c=collection(e);before=c.statement_at(LATE,role=ROLE,profile='accuracy-extension-v2');p,g=inputs(e);r=bind_calculation_report(p,g);self.assertEqual(c.statement_at(LATE,role=ROLE,profile='accuracy-extension-v2'),before);self.assertEqual(before['periods'][0]['rows'][-1]['status'],'CONFLICT');self.assertIsNone(r['selected_reported_value'])
 def test_mode_and_output_budget_admission(self):
  p,g=inputs()
  with self.assertRaisesRegex(XBRLError,'rounding_mode'):bind_calculation_report(p,g,rounding_mode='unknown')
  with patch('terminal.stocks.xbrl_calculation_report.MAX_BINDINGS',0),self.assertRaisesRegex(XBRLError,'output_budget'):bind_calculation_report(p,g)
  with patch('terminal.stocks.xbrl_calculation_report.MAX_OUTPUT',1),self.assertRaisesRegex(XBRLError,'output_budget'):bind_calculation_report(p,g)
 def test_same_period_kind_with_different_date_never_binds_by_end_proximity(self):
  e=extension();raw=e['raw'];start=raw.index(b'<x:context id="I">');end=raw.index(b'</x:context>',start)+len(b'</x:context>');other=raw[start:end].replace(b'id="I"',b'id="OTHER"').replace(b'2023-12-31',b'2022-12-31');e=change(e,b'</x:xbrl>',other+b'</x:xbrl>');e=change(e,b'contextRef="I" unitRef="USD" decimals="0">400',b'contextRef="OTHER" unitRef="USD" decimals="0">400');r=report(e);self.assertEqual(r['bindings'][0]['calculation']['status'],'INCOMPLETE')
 def test_equivalent_unit_aliases_bind_semantically_without_losing_original_refs(self):
  e=change(extension(),b'</x:xbrl>',b'<x:unit id="USD_ALIAS"><x:measure>iso:USD</x:measure></x:unit></x:xbrl>');e=change(e,b'unitRef="USD" decimals="0">400',b'unitRef="USD_ALIAS" decimals="0">400');r=report(e);self.assertEqual(r['bindings'][0]['calculation']['status'],'CALCULATION_COMPATIBLE');self.assertIn('USD_ALIAS',{f['unit_ref']for f in r['fact_provenance'].values()})
 def test_unknown_source_semantics_and_duplicate_source_facts_reject(self):
  p,g=inputs();g['unsupported_semantics'].append({'uri':'https://authored.invalid/authored.xsd','feature':'EMBEDDED_LINKBASE_UNSUPPORTED'});rehash(g)
  with self.assertRaisesRegex(XBRLError,'unknown_dts_semantics'):bind_calculation_report(p,g)
  p,g=inputs();p['facts'].append(copy.deepcopy(p['facts'][0]));rehash(p)
  with self.assertRaisesRegex(XBRLError,'fact_identity'):bind_calculation_report(p,g)
 def test_inline_original_set_and_segment_lineage_are_verified(self):
  import re
  from .test_inline_set import html,doc
  from .inline_set import parse_document_set
  from .xbrl_instance import selected_concepts
  from .test_xbrl_instance import NS
  e=extension();plain=e['raw'].decode();parts=[]
  for match in re.finditer(r'<(g|ext):([A-Za-z]+)( [^>]*)>(.*?)</\1:\2>',plain):
   prefix,name,attrs,text=match.groups();parts.append(f'<ix:nonFraction name="{prefix}:{name}"{attrs}>{text}</ix:nonFraction>')
  original=html(''.join(parts),resources=True).replace(b'xmlns:g=',f'xmlns:ext="{EXT}" xmlns:g='.encode());first=doc('a.xhtml',original);second=doc('z.xhtml',html(''))
  p=parse_document_set([first,second],selected_concepts(NS));g=discover_inline_set(p,e['documents']);r=bind_calculation_report(p,g);self.assertEqual(r['bindings'][0]['calculation']['status'],'CALCULATION_COMPATIBLE');self.assertTrue(all(v['inline_source_segments']for v in r['fact_provenance'].values()))
  p['facts'][0]['inline_source_segments'][0]['document_sha256']='0'*64;rehash(p)
  with self.assertRaisesRegex(XBRLError,'inline_lineage'):bind_calculation_report(p,g)
