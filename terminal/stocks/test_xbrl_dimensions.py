"""Authored closed-cube domains/defaults;independent expected memberships."""
import copy,hashlib,unittest
from .test_xbrl_binding import declaration,BASE
from .test_xbrl_instance import xml,manifest,NS
from .xbrl_instance import selected_concepts,XBRLError
from .xbrl_collection import FilingCollection
from .xbrl_dimensions import PROFILE,ARC,D

def arc(kind,a,b,attrs=''):
 return '<l:definitionArc xl:type="arc" xl:arcrole="'+ARC+kind+'" xl:from="'+a+'" xl:to="'+b+'" '+attrs+'/>'
def entry(member='North',*,default=False,extra='',all_attrs='xd:closed="true" xd:contextElement="segment"',**metadata):
 segment=''if member is None else'<x:segment><d:explicitMember dimension="g:RegionAxis">g:'+member+'</d:explicitMember></x:segment>'
 raw=xml('<g:Assets contextRef="I" unitRef="USD">1000</g:Assets>',context_extra=segment)
 schema=declaration().replace(b'<s:schema',b'<s:schema xmlns:xd="http://xbrl.org/2005/xbrldt" xmlns:l="http://www.xbrl.org/2003/linkbase" xmlns:xl="http://www.w3.org/1999/xlink"',1)
 components=''.join('<s:element id="'+id_+'" name="'+name+'" type="x:stringItemType" substitutionGroup="'+group+'" abstract="'+abstract+'" x:periodType="duration"/>'for id_,name,group,abstract in [('cube','Cube','xd:hypercubeItem','true'),('axis','RegionAxis','xd:dimensionItem','true'),('domain','Domain','x:item','true'),('north','North','x:item','false'),('south','South','x:item','false'),('leaf','Leaf','x:item','false')])
 schema=schema.replace(b'</s:schema>',(components+'<s:annotation><s:appinfo><l:linkbaseRef xl:type="simple" xl:href="dimensions.xml"/></s:appinfo></s:annotation></s:schema>').encode())
 locators=''.join('<l:loc xl:type="locator" xl:label="'+id_+'" xl:href="authored.xsd#'+id_+'"/>'for id_ in('assets','cube','axis','domain','north','south','leaf'))
 links=arc('all','assets','cube',all_attrs)+arc('hypercube-dimension','cube','axis')+arc('dimension-domain','axis','domain')+arc('domain-member','domain','north')+arc('domain-member','domain','south')+(arc('dimension-default','axis','south')if default else'')+extra
 linkbase=('<l:linkbase xmlns:l="http://www.xbrl.org/2003/linkbase" xmlns:xl="http://www.w3.org/1999/xlink" xmlns:xd="'+D+'"><l:definitionLink xl:type="extended" xl:role="urn:authored:closed">'+locators+links+'</l:definitionLink></l:linkbase>').encode()
 return {'raw':raw,'manifest':manifest(raw,**metadata),'concepts':selected_concepts(NS),'instance_uri':BASE+'instance.xml','documents':[{'uri':BASE+'authored.xsd','raw':schema,'sha256':hashlib.sha256(schema).hexdigest()},{'uri':BASE+'dimensions.xml','raw':linkbase,'sha256':hashlib.sha256(linkbase).hexdigest()}]}
def evaluate(e=None):
 c=FilingCollection('0000320193');c.ingest_dts_batch([entry()if e is None else e],dimensional_profile=PROFILE);return c.at_acceptance_time('2024-02-02T00:00:00Z')
def proof(v):return v['selected_input_coverage'][0]['xbrl_coverage']['dts_corroboration']['dimensional_validation']
class Dimensions(unittest.TestCase):
 def test_explicit_domain_context_is_checked_without_becoming_consolidated(self):
  e=entry();before=copy.deepcopy(e);v=evaluate(e);p=proof(v);self.assertEqual(p['profile'],PROFILE);self.assertFalse(p['complete_drs_validation']);self.assertEqual(p['facts'][0]['status'],'VALIDATED_RESTRICTED_EXPLICIT_CONTEXT');self.assertFalse(v['history']['assets']);self.assertEqual(e,before)
 def test_valid_default_is_reported_without_synthesizing_context_or_consolidated_value(self):
  v=evaluate(entry(None,default=True));self.assertEqual(proof(v)['facts'][0]['used_defaults'],{'{'+NS+'}RegionAxis':'{'+NS+'}South'});self.assertFalse(v['history']['assets']);self.assertEqual(v['selected_input_coverage'][0]['xbrl_coverage']['excluded']['dimensioned_or_opaque'],1)
 def test_missing_axis_outside_member_and_explicit_default_fail(self):
  for e in(entry(None),entry('Unknown'),entry('South',default=True)):
   with self.assertRaises(XBRLError):evaluate(e)
 def test_closed_extra_dimension_and_wrong_placement_fail(self):
  e=entry();e['raw']=e['raw'].replace(b'</x:segment>',b'<d:explicitMember dimension="g:ExtraAxis">g:North</d:explicitMember></x:segment>');e['manifest']['source_sha256']=hashlib.sha256(e['raw']).hexdigest()
  with self.assertRaisesRegex(XBRLError,'extra_dimension'):evaluate(e)
  with self.assertRaisesRegex(XBRLError,'context_profile_unsupported'):evaluate(entry(all_attrs='xd:closed="true" xd:contextElement="scenario"'))
 def test_default_conflict_and_domain_cycles_including_diamond_are_rejected(self):
  for e in(entry(default=True,extra=arc('dimension-default','axis','north')),entry(extra=arc('domain-member','north','domain')),entry(extra=arc('domain-member','north','leaf')+arc('domain-member','south','leaf')+arc('domain-member','leaf','south'))):
   with self.assertRaises(XBRLError):evaluate(e)
 def test_unreviewed_relationship_semantics_cannot_be_marked_valid(self):
  for e in(entry(all_attrs='xd:contextElement="segment"'),entry(extra=arc('notAll','assets','cube','xd:contextElement="segment"')),entry(extra=arc('domain-member','north','leaf','xd:targetRole="urn:other"')),entry(extra=arc('domain-member','north','leaf','use="prohibited"')),entry(extra=arc('domain-member','north','leaf','xd:usable="false"'))):
   with self.assertRaises(XBRLError):evaluate(e)
 def test_missing_taxonomy_and_multiple_links_remain_unsupported(self):
  e=entry();e['documents'].pop()
  with self.assertRaisesRegex(XBRLError,'profile_unsupported'):evaluate(e)
  e=entry();doc=e['documents'][1];raw=doc['raw'];link=raw[raw.index(b'<l:definitionLink'):raw.index(b'</l:definitionLink>')+len(b'</l:definitionLink>')];doc['raw']=raw.replace(b'</l:linkbase>',link+b'</l:linkbase>');doc['sha256']=hashlib.sha256(doc['raw']).hexdigest()
  with self.assertRaisesRegex(XBRLError,'profile_unsupported'):evaluate(e)
 def test_invalid_later_context_leaves_accepted_collection_unchanged(self):
  c=FilingCollection('0000320193');c.ingest_dts_batch([entry()],dimensional_profile=PROFILE);before=c.page()
  with self.assertRaises(XBRLError):c.ingest_dts_batch([entry('Unknown',accession='0000000123-24-000002')],dimensional_profile=PROFILE)
  self.assertEqual(c.page(),before)
 def test_typed_axis_and_nonabstract_cube_are_explicitly_unsupported(self):
  for replacement in[(b'name="RegionAxis"',b'xd:typedDomainRef="#domain" name="RegionAxis"'),(b'substitutionGroup="xd:hypercubeItem" abstract="true"',b'substitutionGroup="xd:hypercubeItem" abstract="false"')]:
   e=entry();doc=e['documents'][0];doc['raw']=doc['raw'].replace(*replacement);doc['sha256']=hashlib.sha256(doc['raw']).hexdigest()
   with self.assertRaisesRegex(XBRLError,'declaration_'):evaluate(e)
 def test_inline_document_set_uses_same_source_bound_dimension_contract(self):
  from .test_inline_set import html,doc
  e=entry();raw=e['raw'].decode();resources=raw[raw.index('<x:context'):raw.index('<g:Assets')]
  page=html('<ix:nonFraction name="g:Assets" contextRef="I" unitRef="USD">1000</ix:nonFraction>',resources=True).decode();start=page.index('<x:context');end=page.index('</ix:resources>');page=page[:start]+resources+page[end:];page=page.replace('<html ','<html xmlns:d="http://xbrl.org/2006/xbrldi" ',1)
  c=FilingCollection('0000320193');c.ingest_inline_set_batch([{'documents':[doc('a.xhtml',page.encode())],'concepts':selected_concepts(NS),'taxonomy_documents':e['documents']}],dimensional_profile=PROFILE);v=c.at_acceptance_time('2024-02-02T00:00:00Z');self.assertEqual(len(proof(v)['facts']),1);self.assertFalse(v['history']['assets'])
