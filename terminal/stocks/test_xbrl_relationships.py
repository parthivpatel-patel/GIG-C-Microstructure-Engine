"""Independent authored relationships;no network or application construction."""
import copy,unittest
from unittest.mock import patch
from .test_xbrl_dts import schema,presentation,document,evaluate,ROLE,NS
from .xbrl_relationships import PARENT,SUM
from .xbrl_instance import XBRLError,digest

def graph(raw=None):return evaluate([document('authored.xsd',schema()),document('presentation.xml',presentation()if raw is None else raw)])
def net(raw=None):return graph(raw)['effective_relationships']['networks'][0]
def arc(*,kind='presentation',before='a',after='c',attrs='',role=None):
 return f'<l:{kind}Arc xl:type="arc" xl:arcrole="{role or (PARENT if kind=="presentation"else SUM)}" xl:from="{before}" xl:to="{after}" {attrs}/>'
def link(kind,arcs):
 return f'<l:{kind}Link xl:type="extended" xl:role="{ROLE}"><l:loc xl:type="locator" xl:label="a" xl:href="authored.xsd#assets"/><l:loc xl:type="locator" xl:label="c" xl:href="authored.xsd#cash"/>{arcs}</l:{kind}Link>'
def base(links):return ('<l:linkbase xmlns:l="http://www.xbrl.org/2003/linkbase" xmlns:xl="http://www.w3.org/1999/xlink">'+links+'</l:linkbase>').encode()
class EffectiveRelationships(unittest.TestCase):
 def test_legacy_precedence_stays_refused_but_new_profile_resolves_it(self):
  raw=presentation(attrs='priority="2"');g=graph(raw);self.assertFalse(g['presentation'][0]['usable']);n=g['effective_relationships']['networks'][0];self.assertTrue(n['usable']);self.assertEqual(n['arcs'][0]['priority'],2)
 def test_prohibition_maximum_priority_and_higher_optional_reinstatement(self):
  for last,expected in [('',0),(arc(attrs='priority="3"'),1)]:
   n=net(base(link('presentation',arc()+arc(attrs='priority="2" use="prohibited"')+last)));self.assertTrue(n['usable']);self.assertEqual(len(n['arcs']),expected);self.assertEqual(len(n['suppressed']),1-expected)
 def test_equal_priority_prohibition_wins_independent_of_document_order(self):
  a=arc(attrs='priority="2"');b=arc(attrs='priority="2" use="prohibited"')
  for rows in(a+b,b+a):self.assertEqual(net(base(link('presentation',rows)))['arcs'],[])
 def test_equivalence_preserves_order_label_and_exact_numeric_attributes(self):
  rows=arc(attrs='order="1.00"')+arc(attrs='order="+1" priority="1"')+arc(attrs='order="2" use="prohibited"')+arc(attrs='preferredLabel="https://authored.invalid/total"')
  n=net(base(link('presentation',rows)));self.assertEqual(len(n['arcs']),2);self.assertEqual(len(n['suppressed']),1);self.assertEqual(len(n['arcs'][0]['provenance']),2)
 def test_split_extended_links_are_one_effective_role_with_all_sources(self):
  n=net(base(link('presentation',arc())+link('presentation',arc(attrs='priority="1"'))));self.assertTrue(n['usable']);self.assertEqual(len(n['arcs']),1);self.assertEqual(len(n['arcs'][0]['provenance']),2)
 def test_exact_source_hash_and_arc_location_are_preserved(self):
  g=graph();r=g['effective_relationships'];self.assertEqual(r['sha256'],digest({k:v for k,v in r.items()if k!='sha256'}));p=r['networks'][0]['arcs'][0]['provenance'][0];self.assertEqual(p['source_sha256'],document('presentation.xml',presentation())['sha256']);self.assertEqual(p['extended_link_index'],0)
 def test_unknown_attribute_or_role_invalidates_whole_network_not_just_arc(self):
  for bad in(arc(attrs='custom="x"'),arc(role='https://authored.invalid/custom')):
   n=net(base(link('presentation',arc()+bad)));self.assertFalse(n['usable']);self.assertIn('ARC_ROLE_OR_ATTRIBUTE_UNSUPPORTED',n['issues'])
 def test_unresolved_concept_and_cycles_cannot_be_rendered(self):
  self.assertFalse(net(presentation().replace(b'#cash',b'#missing'))['usable']);self.assertIn('DIRECTED_RELATIONSHIP_CYCLE',net(base(link('presentation',arc()+arc(before='c',after='a'))))['issues'])
 def test_calculation_weights_preserve_exact_sign_and_conflicting_pairs_reject(self):
  n=net(base(link('calculation',arc(kind='calculation',attrs='weight="1.0"'))));self.assertTrue(n['usable']);self.assertEqual(n['arcs'][0]['weight'],{'numerator':'1','denominator':'1'})
  n=net(base(link('calculation',arc(kind='calculation',attrs='weight="1"')+arc(kind='calculation',attrs='weight="-1"'))));self.assertFalse(n['usable']);self.assertIn('MULTIPLE_EFFECTIVE_CALCULATION_RELATIONSHIPS',n['issues'])
 def test_missing_zero_or_fractional_weight_is_not_silently_inferred(self):
  with self.assertRaises(XBRLError):net(base(link('calculation',arc(kind='calculation'))))
  for value in('0','0.5'):self.assertFalse(net(base(link('calculation',arc(kind='calculation',attrs=f'weight="{value}"'))))['usable'])
 def test_calculation_balance_sign_is_checked(self):
  raw=base(link('calculation',arc(kind='calculation',attrs='weight="-1"')));doc=schema().replace(b'name="Cash"',b'name="Cash" x:balance="debit"');g=evaluate([document('authored.xsd',doc),document('presentation.xml',raw)]);self.assertIn('WEIGHT_BALANCE_CONFLICT',g['effective_relationships']['networks'][0]['issues'])
 def test_bad_priority_and_use_reject(self):
  for attrs in('priority="-1"','priority="1e2"','use="unknown"'):
   with self.assertRaises(XBRLError):net(presentation(attrs=attrs))
 def test_input_order_and_caller_inputs_are_not_mutated(self):
  docs=[document('authored.xsd',schema()),document('presentation.xml',presentation())];before=copy.deepcopy(docs);self.assertEqual(evaluate(docs),evaluate(list(reversed(docs))));self.assertEqual(docs,before)
 def test_total_arc_budget_is_enforced_across_links(self):
  with patch('terminal.stocks.xbrl_relationships.MAX_ARCS',1),self.assertRaisesRegex(XBRLError,'arc_budget'):net(base(link('presentation',arc())+link('presentation',arc())))
