"""Authored company extensions with explicit source structure,not guessed metrics."""
import copy,hashlib,unittest,ast,tempfile,json
from pathlib import Path
from unittest.mock import patch
from .test_xbrl_statements import entry,collection,ROLE,LATE,EARLY
from .test_xbrl_dts import document
from .test_xbrl_instance import manifest
from .xbrl_instance import XBRLError,digest
from .service import StockWorkspace
from .xbrl_product import company_contract
EXT='https://authored.invalid/taxonomy'

def extension(value='400',name='CompanyLiquidity',*,kind='x:monetaryItemType',types='',period='instant',extra='',**metadata):
 e=entry(**metadata);raw=e['raw'].replace(b'unitRef="USD">600',b'unitRef="USD" decimals="0">600');raw=raw.replace(b'</x:xbrl>',(f'<ext:{name} contextRef="I" unitRef="USD" decimals="0">{value}</ext:{name}>'+extra+'</x:xbrl>').encode());e['raw']=raw;e['manifest']['source_sha256']=hashlib.sha256(raw).hexdigest()
 doc=e['documents'][0]['raw'].replace(b'</s:schema>',f'<s:import namespace="{EXT}" schemaLocation="extension.xsd"/></s:schema>'.encode());e['documents'][0]=document('authored.xsd',doc)
 e['documents'][1]=document('presentation.xml',e['documents'][1]['raw'].replace(b'authored.xsd#liabilities',b'extension.xsd#custom'))
 schema=f'<s:schema xmlns:s="http://www.w3.org/2001/XMLSchema" xmlns:x="http://www.xbrl.org/2003/instance" xmlns:t="{EXT}" targetNamespace="{EXT}"><s:element id="custom" name="{name}" type="{kind}" substitutionGroup="x:item" x:periodType="{period}" nillable="true"/>{types}</s:schema>'.encode();e['documents'].append(document('extension.xsd',schema));return e

def view(e=None,at=LATE):return collection(e or extension()).statement_at(at,role=ROLE,profile='accuracy-extension-v2')
def extrow(r):return r['periods'][0]['rows'][-1]
class AccuracyExtension(unittest.TestCase):
 def test_source_extension_is_reported_without_name_or_metric_guess(self):
  r=view();row=extrow(r);self.assertEqual(r['schema'],'gig.sec.xbrl.statement_view.v2');self.assertEqual(row['status'],'REPORTED_EXTENSION');self.assertEqual(row['value'],'400');self.assertIsNone(row['statement_mapping']['accounting_metric']);self.assertEqual(row['statement_mapping']['declaration_documents'][0]['uri'],'https://authored.invalid/extension.xsd');self.assertEqual(row['statement_mapping']['relationship_indices'],[1]);self.assertFalse(row['statement_mapping']['root'])
 def test_same_local_name_as_GAAP_does_not_create_accounting_equivalence(self):
  r=view(extension(name='Assets'));self.assertEqual(extrow(r)['concept'],'{'+EXT+'}Assets');self.assertIsNone(extrow(r)['statement_mapping']['accounting_metric']);self.assertEqual(extrow(r)['status'],'REPORTED_EXTENSION')
 def test_raw_extension_fact_ids_and_values_are_never_rewritten(self):
  c=collection(extension());before=copy.deepcopy(c._filings);r=c.statement_at(LATE,role=ROLE,profile='accuracy-extension-v2');row=extrow(r);self.assertIsNone(row['facts'][0]['value']);self.assertEqual(row['numeric_facts'][0]['source_fact_id'],row['facts'][0]['source_fact_id']);self.assertEqual(row['numeric_facts'][0]['value'],'400');self.assertEqual(c._filings,before)
 def test_accuracy_match_compatible_difference_and_disjoint_outcomes(self):
  for v,status in [('400','ROUNDING_COMPATIBLE'),('399','ROUNDING_COMPATIBLE'),('397','DEFINITELY_INCONSISTENT')]:
   r=view(extension(value=v));check=r['periods'][0]['calculations'][0];self.assertEqual(check['status'],status);self.assertEqual(check['exact_diagnostic']['status'],'EXACT_MATCH'if v=='400'else'EXACT_DIFFERENCE')
 def test_negative_weight_and_negative_extension_have_correct_interval(self):
  e=extension(value='-400');e['documents'][1]=document('presentation.xml',e['documents'][1]['raw'].replace(b'xl:to="b" weight="1"',b'xl:to="b" weight="-1"'));r=view(e);self.assertEqual(r['periods'][0]['calculations'][0]['status'],'ROUNDING_COMPATIBLE')
 def test_consistent_and_conflicting_extension_duplicates_preserve_ids(self):
  for value,status in [('400','REPORTED_EXTENSION'),('401','CONFLICT')]:
   r=view(extension(extra=f'<ext:CompanyLiquidity contextRef="I" unitRef="USD" decimals="0">{value}</ext:CompanyLiquidity>'));self.assertEqual(extrow(r)['status'],status);self.assertEqual(len(extrow(r)['facts']),2)
 def test_nil_extension_is_missing_and_never_zero(self):
  e=extension();raw=e['raw'].replace(b'<ext:CompanyLiquidity contextRef="I" unitRef="USD" decimals="0">400</ext:CompanyLiquidity>',b'<ext:CompanyLiquidity contextRef="I" unitRef="USD" xsi:nil="true"/>');e['raw']=raw;e['manifest']['source_sha256']=hashlib.sha256(raw).hexdigest();r=view(e);self.assertEqual(extrow(r)['status'],'MISSING');self.assertIsNone(extrow(r)['value']);self.assertEqual(r['periods'][0]['calculations'][0]['status'],'INCOMPLETE')
 def test_unsupported_type_is_not_promoted_or_guessed(self):
  r=view(extension(kind='t:Unknown'));self.assertEqual(extrow(r)['status'],'UNSUPPORTED_INPUT');self.assertIn('EXTENSION_NUMERIC_TYPE_UNSUPPORTED',extrow(r)['mapping_diagnostics'])
 def test_custom_numeric_restriction_is_checked_against_actual_lexical_value(self):
  types='<s:simpleType name="Bounded"><s:restriction base="x:monetaryItemType"><s:maxInclusive value="400"/></s:restriction></s:simpleType>'
  self.assertEqual(extrow(view(extension(kind='t:Bounded',types=types)))['value'],'400')
  with self.assertRaisesRegex(XBRLError,'facet_violation'):view(extension(value='401',kind='t:Bounded',types=types))
 def test_invalid_numeric_value_is_rejected_only_in_explicit_new_profile(self):
  e=extension(value='not numeric');c=collection(e);self.assertEqual(c.statement_at(LATE,role=ROLE)['schema'],'gig.sec.xbrl.statement_view.v1')
  with self.assertRaisesRegex(XBRLError,'numeric_lexical'):c.statement_at(LATE,role=ROLE,profile='accuracy-extension-v2')
 def test_period_mismatch_and_units_are_not_silently_accepted(self):
  self.assertIn('DECLARED_PERIOD_OR_CONTEXT_UNSUPPORTED',extrow(view(extension(period='duration')))['mapping_diagnostics'])
  extra='<x:unit id="EUR"><x:measure>iso:EUR</x:measure></x:unit><ext:CompanyLiquidity contextRef="I" unitRef="EUR" decimals="0">400</ext:CompanyLiquidity>';r=view(extension(extra=extra));self.assertEqual(extrow(r)['status'],'AMBIGUOUS_UNITS');self.assertEqual(r['periods'][0]['calculations'][0]['status'],'INCOMPLETE')
 def test_missing_accuracy_preserves_reported_value_but_prevents_consistency_claim(self):
  e=extension();e['raw']=e['raw'].replace(b'unitRef="USD" decimals="0">600',b'unitRef="USD">600');e['manifest']['source_sha256']=hashlib.sha256(e['raw']).hexdigest();r=view(e);self.assertEqual(r['periods'][0]['calculations'][0]['status'],'UNSUPPORTED_ACCURACY')
 def test_dimensions_are_retained_but_not_consolidated(self):
  e=extension(context_extra='<x:segment><d:explicitMember dimension="ext:RegionAxis">ext:NorthMember</d:explicitMember></x:segment>');r=view(e);self.assertEqual(r['periods'],[]);self.assertTrue(r['source_contexts']['I']['dimensions']);self.assertEqual(r['fact_exclusions']['dimensioned_or_opaque'],3)
 def test_unknown_definition_scope_cannot_enable_extension_consolidation(self):
  c=collection(extension());p=next(iter(c._filings.values()));p['dts_corroboration'].pop('definition_relationships_present');p['canonical_sha256']=digest({k:v for k,v in p.items()if k!='canonical_sha256'});r=c.statement_at(LATE,role=ROLE,profile='accuracy-extension-v2');self.assertEqual(extrow(r)['status'],'UNSUPPORTED_INPUT');self.assertIn('EXTENSION_DRS_SCOPE_UNSUPPORTED_OR_UNKNOWN',extrow(r)['mapping_diagnostics'])
 def test_acceptance_amendment_and_source_scope_are_unchanged(self):
  original=extension();amended=extension(value='399',accession='0000000123-24-000002',form='10-K/A',filed='2024-02-10',accepted_at=LATE,amends_accession='0000000123-24-000001');c=collection(original,amended);early=c.statement_at(EARLY,role=ROLE,profile='accuracy-extension-v2');late=c.statement_at(LATE,role=ROLE,profile='accuracy-extension-v2');self.assertEqual(extrow(early)['value'],'400');self.assertEqual(extrow(late)['value'],'399');self.assertEqual(late['source_filing']['amends_accession'],original['manifest']['accession'])
 def test_v1_contract_stays_v1_and_does_not_promote_extensions(self):
  c=collection(extension());v1=c.statement_at(LATE,role=ROLE);v2=c.statement_at(LATE,role=ROLE,profile='accuracy-extension-v2');self.assertEqual(extrow(v1)['status'],'UNSUPPORTED_INPUT');self.assertEqual(extrow(v2)['status'],'REPORTED_EXTENSION');self.assertEqual(c.statement_at(LATE,role=ROLE),v1)
 def test_product_contract_is_versioned_even_when_unavailable(self):
  w=StockWorkspace(environment={});r=company_contract(w,'AAPL',LATE,profile='accuracy-extension-v2');self.assertEqual(r['schema'],'gig.backend.company_xbrl.v2');self.assertEqual(r['statement_view']['schema'],'gig.sec.xbrl.statement_view.v2');self.assertEqual(r['statement_view']['status'],'UNAVAILABLE');w.admit_xbrl_collection('AAPL',collection(extension()));self.assertEqual(extrow(company_contract(w,'AAPL',LATE,role=ROLE,profile='accuracy-extension-v2')['statement_view'])['value'],'400')
 def test_unsupported_profiles_and_output_exhaustion_fail_closed(self):
  with self.assertRaisesRegex(XBRLError,'profile_unsupported'):collection().statement_at(LATE,profile='unknown')
  with patch('terminal.stocks.xbrl_statements.MAX_OUTPUT',1),self.assertRaisesRegex(XBRLError,'output_budget'):view()
 def test_private_cli_uses_explicit_profile_and_preserves_legacy_export(self):
  from scripts.inspect_xbrl_instances import inspect
  e=extension()
  with tempfile.TemporaryDirectory()as directory:
   root=Path(directory);(root/'instance.xml').write_bytes(e['raw']);docs=[]
   for i,d in enumerate(e['documents']):
    path=f'taxonomy-{i}.xml';(root/path).write_bytes(d['raw']);docs.append({'path':path,'uri':d['uri'],'sha256':d['sha256']})
   batch={'schema':'gig.sec.xbrl.input_dts_batch.v1','issuer_cik':'0000320193','origin':'HISTORICAL_SYNTHETIC','numeric_profile':None,'entries':[{'path':'instance.xml','manifest':e['manifest'],'gaap_namespace':'http://fasb.org/us-gaap/2024','instance_uri':e['instance_uri'],'documents':docs}]};(root/'batch.json').write_text(json.dumps(batch))
   _,v=inspect(root/'batch.json',LATE,company_symbol='AAPL',statement_role=ROLE,statement_profile='accuracy-extension-v2');self.assertEqual(v['schema'],'gig.backend.company_xbrl.v2');self.assertEqual(extrow(v['statement_view'])['value'],'400')
   _,old=inspect(root/'batch.json',LATE,company_symbol='AAPL',statement_role=ROLE);self.assertEqual(old['schema'],'gig.backend.company_xbrl.v1')
   with self.assertRaisesRegex(XBRLError,'requires_company'):inspect(root/'batch.json',LATE,statement_profile='accuracy-extension-v2')
   with self.assertRaisesRegex(XBRLError,'profile_unsupported'):inspect(root/'batch.json',LATE,statement_profile='unknown')

class VersionedRoute(unittest.IsolatedAsyncioTestCase):
 async def test_actual_route_opt_in_and_invalid_profile_without_application(self):
  from starlette.datastructures import QueryParams
  from types import SimpleNamespace
  from urllib.parse import urlencode
  from terminal.server.analysis import AnalysisGate
  tree=ast.parse(Path('terminal/server/app.py').read_text());f=next(n for n in ast.walk(tree)if isinstance(n,ast.AsyncFunctionDef)and n.name=='xbrl_statements_v2');f.decorator_list=[];w=StockWorkspace(environment={});w.admit_xbrl_collection('AAPL',collection(extension()));gate=AnalysisGate();scope={'stocks':w,'analysis':gate,'error':lambda code,message,status=400:{'code':code,'status':status}};exec(compile(ast.fix_missing_locations(ast.Module(body=[f],type_ignores=[])),'<actual-xbrl-profile-route>','exec'),scope)
  async def call(profile):return await scope[f.name](SimpleNamespace(query_params=QueryParams(urlencode({'at':LATE,'role':ROLE,'profile':profile})),path_params={'symbol':'AAPL'}))
  try:
   r=await call('accuracy-extension-v2');self.assertEqual(r['schema'],'gig.backend.company_xbrl.v2');self.assertEqual(extrow(r['statement_view'])['value'],'400');self.assertEqual((await call('legacy-v1'))['schema'],'gig.backend.company_xbrl.v1');self.assertEqual((await call('unknown'))['status'],422)
  finally:await gate.close()

class EmbeddedScope(unittest.TestCase):
 def test_embedded_relationship_scope_cannot_be_silently_omitted(self):
  e=extension();d=e['documents'][-1];embedded=b'<s:annotation><s:appinfo><l:linkbase xmlns:l="http://www.xbrl.org/2003/linkbase"><l:definitionLink xmlns:xl="http://www.w3.org/1999/xlink" xl:type="extended" xl:role="https://authored.invalid/hidden-role"/></l:linkbase></s:appinfo></s:annotation>'
  e['documents'][-1]=document('extension.xsd',d['raw'].replace(b'</s:schema>',embedded+b'</s:schema>'));c=collection(e);p=next(iter(c._filings.values()));self.assertIsNone(p['dts_corroboration']['definition_relationships_present'])
  for profile in('legacy-v1','accuracy-extension-v2'):
   r=c.statement_at(LATE,role=ROLE,profile=profile);self.assertEqual(r['status'],'UNAVAILABLE');self.assertEqual(r['reason'],'PRESENTATION_UNSUPPORTED');self.assertIn('EMBEDDED_LINKBASE_UNSUPPORTED',r['diagnostics'])
