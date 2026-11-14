"""Bounded direct open/closed cube expectations from authored XDT source graphs."""
import copy,hashlib,unittest
from .test_xbrl_dimensions import entry,arc,BASE,NS
from .xbrl_dimensions import PROFILE,OPEN_PROFILE,corroborate
from .xbrl_instance import parse_instance,selected_financials,digest,XBRLError
from .xbrl_dts import discover
from .xbrl_binding import bind_declarations
from .xbrl_collection import FilingCollection

def edited(e,doc,raw):
 e['documents'][doc]['raw']=raw;e['documents'][doc]['sha256']=hashlib.sha256(raw).hexdigest();return e

def opened(*,closed=False,member='North',extra_member='North',default=False,extra_default=False,extras=1):
 e=entry(member,default=default,all_attrs='xd:closed="'+str(closed).lower()+'" xd:contextElement="segment"')
 if extras:
  segment=''.join('<d:explicitMember dimension="g:OtherAxis'+str(i)+'">g:'+extra_member+'</d:explicitMember>'for i in range(extras))
  raw=e['raw']
  if b'<x:segment>'in raw:raw=raw.replace(b'</x:segment>',segment.encode()+b'</x:segment>')
  else:raw=raw.replace(b'</x:identifier>',b'</x:identifier><x:segment>'+segment.encode()+b'</x:segment>')
  e['raw']=raw;e['manifest']['source_sha256']=hashlib.sha256(raw).hexdigest()
  schema=e['documents'][0]['raw'];link=e['documents'][1]['raw']
  for i in range(extras):
   id_='other'+str(i);name='OtherAxis'+str(i)
   schema=schema.replace(b'</s:schema>',('<s:element id="'+id_+'" name="'+name+'" substitutionGroup="xd:dimensionItem" abstract="true" x:periodType="duration"/></s:schema>').encode())
   link=link.replace(b'</l:definitionLink>',('<l:loc xl:type="locator" xl:label="'+id_+'" xl:href="authored.xsd#'+id_+'"/>'+arc('dimension-domain',id_,'domain')+(arc('dimension-default',id_,'south')if extra_default else'')+'</l:definitionLink>').encode())
  edited(e,0,schema);edited(e,1,link)
 return e

def derived(e=None,profile=OPEN_PROFILE):
 e=opened()if e is None else e
 parsed=parse_instance(e['raw'],e['manifest'],e['concepts']);graph=discover(e['raw'],e['instance_uri'],e['manifest']['source_sha256'],e['documents'])
 return corroborate(bind_declarations(parsed,graph),graph,profile=profile)

def proof(value):return value['dts_corroboration']['dimensional_validation']

class OpenDimensions(unittest.TestCase):
 def test_direct_open_cube_validates_supplied_additional_dimensions(self):
  e=opened();before=copy.deepcopy(e);p=derived(e);record=proof(p)['facts'][0]
  self.assertEqual(p['schema'],'gig.sec.xbrl.dimensional_instance.v2');self.assertEqual(proof(p)['profile'],OPEN_PROFILE);self.assertFalse(proof(p)['complete_drs_validation'])
  self.assertEqual(record['extra_dimensions'],['{'+NS+'}OtherAxis0']);self.assertFalse(record['closed']);self.assertEqual(record['used_defaults'],{});self.assertEqual(e,before)
 def test_legacy_profile_still_refuses_open_even_without_additional_dimension(self):
  with self.assertRaisesRegex(XBRLError,'direct_closed_assignment_required'):derived(opened(extras=0),PROFILE)
 def test_new_profile_closed_cube_rejects_extras_and_validates_no_extras(self):
  with self.assertRaisesRegex(XBRLError,'closed_extra_dimension'):derived(opened(closed=True))
  p=derived(opened(closed=True,extras=0));self.assertTrue(proof(p)['facts'][0]['closed']);self.assertEqual(proof(p)['facts'][0]['extra_dimensions'],[])
 def test_missing_required_cube_dimension_still_rejects(self):
  with self.assertRaisesRegex(XBRLError,'required_dimension_missing'):derived(opened(member=None))
 def test_defaulted_required_axis_does_not_synthesize_a_context(self):
  p=derived(opened(member=None,default=True));self.assertEqual(proof(p)['facts'][0]['used_defaults'],{'{'+NS+'}RegionAxis':'{'+NS+'}South'});self.assertEqual(len(p['contexts']['I']['dimensions']),1)
 def test_additional_member_must_belong_to_its_supplied_domain(self):
  with self.assertRaisesRegex(XBRLError,'member_outside_domain'):derived(opened(extra_member='Leaf'))
 def test_explicit_default_on_additional_axis_rejects(self):
  with self.assertRaisesRegex(XBRLError,'explicit_default_member'):derived(opened(extra_member='South',extra_default=True))
 def test_additional_typed_or_unknown_dimension_declaration_rejects(self):
  e=opened();schema=e['documents'][0]['raw'].replace(b'name="OtherAxis0"',b'xd:typedDomainRef="#domain" name="OtherAxis0"');edited(e,0,schema)
  with self.assertRaisesRegex(XBRLError,'declaration_unsupported'):derived(e)
  e=opened();schema=e['documents'][0]['raw'].replace(b'id="other0"',b'id="different"');edited(e,0,schema)
  with self.assertRaisesRegex(XBRLError,'profile_unsupported'):derived(e)
 def test_extra_axis_without_supplied_domain_cannot_claim_validation(self):
  e=opened();raw=e['documents'][1]['raw'].replace(arc('dimension-domain','other0','domain').encode(),b'');edited(e,1,raw)
  with self.assertRaisesRegex(XBRLError,'single_domain_required'):derived(e)
 def test_unsupported_negative_roles_cycles_and_inheritance_still_reject(self):
  changes=[arc('notAll','assets','cube','xd:contextElement="segment"'),arc('domain-member','north','domain'),arc('domain-member','north','leaf','xd:targetRole="urn:other"')]
  for change in changes:
   e=opened();edited(e,1,e['documents'][1]['raw'].replace(b'</l:definitionLink>',change.encode()+b'</l:definitionLink>'))
   with self.assertRaises(XBRLError):derived(e)
  e=opened();edited(e,1,e['documents'][1]['raw'].replace(b'xl:from="assets"',b'xl:from="domain"'))
  with self.assertRaisesRegex(XBRLError,'direct_closed_assignment_required'):derived(e)
 def test_wrong_context_placement_still_rejects(self):
  e=opened();edited(e,1,e['documents'][1]['raw'].replace(b'contextElement="segment"',b'contextElement="scenario"'))
  with self.assertRaisesRegex(XBRLError,'context_profile_unsupported'):derived(e)
 def test_combined_cube_and_reported_axis_budget_remains_bounded(self):
  with self.assertRaisesRegex(XBRLError,'dimension_budget'):derived(opened(extras=32))
 def test_collection_integration_and_atomic_later_refusal(self):
  c=FilingCollection('0000320193');c.ingest_dts_batch([opened()],dimensional_profile=OPEN_PROFILE);before=c.page();value=c.at_acceptance_time('2024-02-02T00:00:00Z')
  self.assertFalse(value['history']['assets'])
  bad=opened(extra_member='Leaf');bad['manifest']['accession']='0000000123-24-000002'
  with self.assertRaisesRegex(XBRLError,'member_outside_domain'):c.ingest_dts_batch([bad],dimensional_profile=OPEN_PROFILE)
  self.assertEqual(c.page(),before)
 def test_v2_dimensional_proof_cannot_be_silently_relabeled_or_stripped(self):
  p=derived()
  for kind in('profile','schema','drop'):
   bad=copy.deepcopy(p);bad.pop('canonical_sha256')
   if kind=='profile':bad['dts_corroboration']['dimensional_validation']['profile']=PROFILE
   elif kind=='schema':bad['schema']='gig.sec.xbrl.dimensional_instance.v1'
   else:bad['dts_corroboration'].pop('dimensional_validation')
   bad['canonical_sha256']=digest(bad)
   with self.assertRaisesRegex(XBRLError,'dimensional_result'):selected_financials(bad)

 def test_inline_set_keeps_original_lineage_with_open_dimensional_proof(self):
  from .test_inline_set import html,doc
  e=opened();raw=e['raw'].decode();resources=raw[raw.index('<x:context'):raw.index('<g:Assets')]
  page=html('<ix:nonFraction name="g:Assets" contextRef="I" unitRef="USD">1000</ix:nonFraction>',resources=True).decode();start=page.index('<x:context');end=page.index('</ix:resources>');page=page[:start]+resources+page[end:];page=page.replace('<html ','<html xmlns:d="http://xbrl.org/2006/xbrldi" ',1)
  original=doc('open.xhtml',page.encode());c=FilingCollection('0000320193');c.ingest_inline_set_batch([{'documents':[original],'concepts':e['concepts'],'taxonomy_documents':e['documents']}],dimensional_profile=OPEN_PROFILE)
  parsed=next(iter(c._filings.values()));self.assertEqual(parsed['schema'],'gig.sec.xbrl.dimensional_inline_set.v2');self.assertEqual(parsed['document_set']['documents'][0]['source']['source_sha256'],original['manifest']['source_sha256']);self.assertFalse(c.at_acceptance_time('2024-02-02T00:00:00Z')['history']['assets'])
 def test_v2_proof_record_fields_reject_corruption_after_rehash(self):
  p=derived()
  for change in('bool','duplicate','unsorted','qname','closed','budget','source','complete','status'):
   bad=copy.deepcopy(p);bad.pop('canonical_sha256');record=bad['dts_corroboration']['dimensional_validation']['facts'][0]
   if change=='bool':record['closed']=0
   elif change=='duplicate':record['extra_dimensions']*=2
   elif change=='unsorted':record['extra_dimensions']=['{urn:extra}Z','{urn:extra}A']
   elif change=='qname':record['extra_dimensions']=['missing-expanded-qname']
   elif change=='closed':record['closed']=True
   elif change=='budget':record['extra_dimensions']=['{urn:extra}Axis'+str(i)for i in range(33)]
   elif change=='source':record['source_fact_id']='unknown-fact'
   elif change=='complete':bad['dts_corroboration']['dimensional_validation']['complete_drs_validation']=True
   else:record['status']='COMPLETE_DRS_VALIDATED'
   bad['canonical_sha256']=digest(bad)
   with self.subTest(change=change),self.assertRaisesRegex(XBRLError,'dimensional_result'):selected_financials(bad)
