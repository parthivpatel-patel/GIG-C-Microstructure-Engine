"""Authored embedded roots with independent source-location/precedence checks."""
import copy,unittest
from unittest.mock import patch
from .test_xbrl_statement_v2 import extension
from .test_xbrl_statements import collection,ROLE,LATE
from .test_xbrl_dts import document
from .xbrl_dts import discover,EMBEDDED_PROFILE
from .xbrl_collection import FilingCollection
from .xbrl_instance import XBRLError,digest

def embedded():
 e=extension();schema=e['documents'][0]['raw'];linkbase=e['documents'][1]['raw'];schema=schema.replace(b'<l:linkbaseRef xl:type="simple" xl:href="presentation.xml"/>',linkbase);e['documents']=[document('authored.xsd',schema),e['documents'][2]];return e

def graph(e=None,profile=EMBEDDED_PROFILE):
 e=e or embedded();return discover(e['raw'],e['instance_uri'],e['manifest']['source_sha256'],e['documents'],embedded_profile=profile)
class Embedded(unittest.TestCase):
 def test_opt_in_resolves_original_document_relative_locators_and_hashes(self):
  e=embedded();g=graph(e);self.assertTrue(g['structural_closure']);self.assertEqual(g['embedded_linkbase_profile'],EMBEDDED_PROFILE);self.assertEqual(g['embedded_linkbases'][0]['source_sha256'],e['documents'][0]['sha256']);n=g['effective_relationships']['networks'][0];self.assertTrue(n['usable']);self.assertEqual(n['arcs'][0]['provenance'][0]['source_uri'],e['documents'][0]['uri']);self.assertIsInstance(n['arcs'][0]['provenance'][0]['arc_node_ordinal'],int)
 def test_legacy_default_is_still_explicitly_unsupported(self):
  g=graph(profile=None);self.assertTrue(any(i['feature']=='EMBEDDED_LINKBASE_UNSUPPORTED'for i in g['unsupported_semantics']));self.assertNotIn('embedded_linkbase_profile',g)
 def test_whole_product_profile_can_use_embedded_presentation_and_calculation(self):
  c=FilingCollection('0000320193');c.ingest_dts_batch([embedded()],embedded_profile=EMBEDDED_PROFILE);r=c.statement_at(LATE,role=ROLE,profile='accuracy-extension-v2');self.assertEqual(r['status'],'AVAILABLE');self.assertEqual(r['periods'][0]['rows'][-1]['status'],'REPORTED_EXTENSION');self.assertEqual(r['periods'][0]['calculations'][0]['status'],'ROUNDING_COMPATIBLE')
 def test_source_node_ordinals_disambiguate_multiple_roots_in_one_schema(self):
  e=embedded();s=e['documents'][0]['raw'];start=s.index(b'<l:linkbase');end=s.index(b'</l:linkbase>')+len(b'</l:linkbase>');duplicate=s[start:end];e['documents'][0]=document('authored.xsd',s.replace(b'</s:appinfo>',duplicate+b'</s:appinfo>'));g=graph(e);self.assertEqual(len(g['embedded_linkbases']),2)
  for n in g['effective_relationships']['networks']:
   self.assertTrue(n['usable']);sources=n['arcs'][0]['provenance'];self.assertEqual(len(sources),2);self.assertNotEqual(sources[0]['arc_node_ordinal'],sources[1]['arc_node_ordinal'])
 def test_cross_container_priority_and_prohibition_are_effective(self):
  e=embedded();s=e['documents'][0]['raw'];start=s.index(b'<l:linkbase');end=s.index(b'</l:linkbase>')+len(b'</l:linkbase>');duplicate=s[start:end].replace(b'<l:presentationArc ',b'<l:presentationArc priority="2" use="prohibited" ');e['documents'][0]=document('authored.xsd',s.replace(b'</s:appinfo>',duplicate+b'</s:appinfo>'));g=graph(e);n=next(n for n in g['effective_relationships']['networks']if n['kind']=='presentation');self.assertEqual(n['arcs'],[]);self.assertEqual(len(n['suppressed']),2)
 def test_non_appinfo_placement_remains_unusable(self):
  e=embedded();s=e['documents'][0]['raw'].replace(b'<s:appinfo>',b'<s:documentation>').replace(b'</s:appinfo>',b'</s:documentation>');e['documents'][0]=document('authored.xsd',s);g=graph(e);self.assertTrue(any(i['feature']=='EMBEDDED_LINKBASE_UNSUPPORTED'for i in g['unsupported_semantics']))
 def test_unknown_embedded_children_or_attributes_are_not_silently_skipped(self):
  for before,after in[(b'</l:linkbase>',b'<l:roleRef/></l:linkbase>'),(b'<l:linkbase ',b'<l:linkbase id="unsupported" ')]:
   e=embedded();e['documents'][0]=document('authored.xsd',e['documents'][0]['raw'].replace(before,after))
   with self.assertRaisesRegex(XBRLError,'embedded_content_unsupported'):graph(e)
 def test_incomplete_dependency_and_cycles_are_not_bypassed(self):
  e=embedded();g=graph({**e,'documents':e['documents'][:1]});self.assertFalse(g['structural_closure']);self.assertTrue(any('UNRESOLVED_LOCATOR'in n['issues']for n in g['effective_relationships']['networks']))
 def test_context_hashes_do_not_change_from_ordinal_bookkeeping(self):
  from .test_xbrl_instance import parsed
  p=parsed();self.assertEqual(p['context_semantic_profile'],'DIM_CONTEXT_ELEMENT_V3_ORDERED');self.assertEqual(p,parsed())
 def test_invalid_profile_and_input_order_are_deterministic(self):
  e=embedded();before=copy.deepcopy(e);self.assertEqual(graph(e),graph({**e,'documents':list(reversed(e['documents']))}));self.assertEqual(e,before)
  with self.assertRaisesRegex(XBRLError,'profile_unsupported'):graph(e,profile='future')
 def test_invalid_later_entry_preserves_accepted_collection(self):
  c=FilingCollection('0000320193');c.ingest_dts_batch([embedded()],embedded_profile=EMBEDDED_PROFILE);before=c.page();bad=embedded();bad['manifest']['accession']='0000000123-24-000002';bad['documents'][0]=document('authored.xsd',bad['documents'][0]['raw'].replace(b'</l:linkbase>',b'<l:arcroleRef/></l:linkbase>'))
  with self.assertRaises(XBRLError):c.ingest_dts_batch([bad],embedded_profile=EMBEDDED_PROFILE)
  self.assertEqual(c.page(),before)
 def test_embedded_definition_uses_existing_explicit_closed_cube_validation(self):
  from .test_xbrl_dimensions import entry,PROFILE,proof
  e=entry();s=e['documents'][0]['raw'];d=e['documents'][1];e['documents']=[document('authored.xsd',s.replace(b'<l:linkbaseRef xl:type="simple" xl:href="dimensions.xml"/>',d['raw']))];c=FilingCollection('0000320193');c.ingest_dts_batch([e],dimensional_profile=PROFILE,embedded_profile=EMBEDDED_PROFILE);out=c.at_acceptance_time(LATE);self.assertEqual(proof(out)['facts'][0]['status'],'VALIDATED_RESTRICTED_EXPLICIT_CONTEXT');self.assertEqual(out['history']['assets'],[])
 def test_private_inspect_export_reaches_embedded_profile(self):
  import tempfile,json
  from pathlib import Path
  from scripts.inspect_xbrl_instances import inspect
  e=embedded()
  with tempfile.TemporaryDirectory()as directory:
   root=Path(directory);(root/'instance.xml').write_bytes(e['raw']);docs=[]
   for i,d in enumerate(e['documents']):
    p=f'taxonomy{i}.xml';(root/p).write_bytes(d['raw']);docs.append({'path':p,'uri':d['uri'],'sha256':d['sha256']})
   path=root/'batch.json';path.write_text(json.dumps({'schema':'gig.sec.xbrl.input_dts_batch.v1','issuer_cik':'0000320193','origin':'HISTORICAL_SYNTHETIC','numeric_profile':None,'entries':[{'path':'instance.xml','manifest':e['manifest'],'gaap_namespace':'http://fasb.org/us-gaap/2024','instance_uri':e['instance_uri'],'documents':docs}]}));_,r=inspect(path,LATE,company_symbol='AAPL',statement_role=ROLE,statement_profile='accuracy-extension-v2',embedded_profile=EMBEDDED_PROFILE);self.assertEqual(r['statement_view']['status'],'AVAILABLE')
