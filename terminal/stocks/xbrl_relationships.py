"""Bounded standard XBRL 2.1 relationships. No fetch or accounting inference.

Base sets include link/arc QNames,role and arcrole. Equivalence includes supported
non-exempt attributes (order,preferredLabel/weight);use/priority select effective
arcs. Unsupported attributes invalidate the entire affected role/kind.
"""
from collections import deque
from fractions import Fraction
from urllib.parse import urljoin
import re
from .xbrl_instance import L,XL,tag,canonical,digest,XBRLError
PROFILE='STANDARD_EFFECTIVE_ARCS_V1'
PARENT='http://www.xbrl.org/2003/arcrole/parent-child'
SUM='http://www.xbrl.org/2003/arcrole/summation-item'
MAX_ARCS=4096;MAX_NETWORKS=64

def number(value,code):
 if type(value)is not str or not re.fullmatch(r'[+-]?(?:[0-9]{1,24}(?:\.[0-9]{0,12})?|\.[0-9]{1,12})',value):raise XBRLError(code)
 return Fraction(value)

def rational(value):return {'numerator':str(value.numerator),'denominator':str(value.denominator)}

def effective(linkbases,locators,concepts,documents):
 from .xbrl_dts import uri
 groups={};count=0;hashes={d['uri']:d['sha256']for d in documents}
 for source,root in sorted(linkbases,key=lambda v:v[0]):
  for li,link in enumerate(root.children):
   kind='presentation'if link.name==tag(L,'presentationLink')else'calculation'if link.name==tag(L,'calculationLink')else None
   if kind is None:continue
   role=link.attrs.get(tag(XL,'role'))
   if link.attrs.get(tag(XL,'type'))!='extended'or type(role)is not str or not 1<=len(role)<=512:raise XBRLError('effective_link_structure')
   expected=PARENT if kind=='presentation'else SUM
   key=(kind,role);g=groups.setdefault(key,{'kind':kind,'role':role,'link_qname':link.name,'arc_qname':tag(L,kind+'Arc'),'arcrole':expected,'issues':set(),'records':[]})
   if len(groups)>MAX_NETWORKS:raise XBRLError('effective_network_budget')
   if set(link.attrs)-{tag(XL,'type'),tag(XL,'role')}:g['issues'].add('EXTENDED_LINK_ATTRIBUTE_UNSUPPORTED')
   labels={}
   for node in link.children:
    if node.name!=tag(L,'loc'):continue
    a=node.attrs;label=a.get(tag(XL,'label'));href=a.get(tag(XL,'href'))
    if a.get(tag(XL,'type'))!='locator'or type(label)is not str or not 1<=len(label)<=128 or label in labels or type(href)is not str:raise XBRLError('effective_locator')
    labels[label]=locators.get(uri(urljoin(source,href),fragment=True))
    if labels[label]is None:g['issues'].add('UNRESOLVED_LOCATOR')
    if set(a)-{tag(XL,k)for k in('type','label','href')}:g['issues'].add('LOCATOR_ATTRIBUTE_UNSUPPORTED')
   for ni,node in enumerate(link.children):
    if node.name==tag(L,'loc'):continue
    if node.name!=tag(L,kind+'Arc'):g['issues'].add('EXTENDED_LINK_CONTENT_UNSUPPORTED');continue
    count+=1
    if count>MAX_ARCS:raise XBRLError('effective_arc_budget')
    a=node.attrs;before=a.get(tag(XL,'from'));after=a.get(tag(XL,'to'))
    if a.get(tag(XL,'type'))!='arc'or before not in labels or after not in labels:raise XBRLError('effective_arc_structure')
    priority=a.get('priority','0');use=a.get('use','optional')
    if not re.fullmatch(r'\+?[0-9]{1,6}',priority)or use not in('optional','prohibited'):raise XBRLError('effective_priority_or_use')
    order=number(a.get('order','1'),'effective_order');preferred=a.get('preferredLabel');weight=None
    allowed={tag(XL,k)for k in('type','from','to','arcrole')}|{'priority','use','order'}|({'preferredLabel'}if kind=='presentation'else{'weight'})
    if set(a)-allowed or a.get(tag(XL,'arcrole'))!=expected or node.children or node.text().strip():g['issues'].add('ARC_ROLE_OR_ATTRIBUTE_UNSUPPORTED')
    if kind=='presentation':
     if preferred is not None and(type(preferred)is not str or not 1<=len(preferred)<=512 or not re.match(r'https?://[^\s]+$',preferred)):raise XBRLError('effective_preferred_label')
    else:
     weight=number(a.get('weight'),'effective_weight')
     if weight not in(-1,1):g['issues'].add('WEIGHT_OUTSIDE_SIGNED_UNIT_PROFILE')
     p=concepts.get(labels[before],{}).get('declaration',{}).get('balance');c=concepts.get(labels[after],{}).get('declaration',{}).get('balance')
     if p and c and (weight>0)!=(p==c):g['issues'].add('WEIGHT_BALANCE_CONFLICT')
    provenance={'source_uri':source,'source_sha256':hashes[source],'extended_link_index':li,'arc_index':ni,'priority':int(priority),'use':use,'order_lexical':a.get('order','1'),'weight_lexical':a.get('weight')}
    record={'from':labels[before],'to':labels[after],'order':rational(order),'preferred_label':preferred,'weight':rational(weight)if weight is not None else None,'provenance':provenance}
    g['records'].append(record)
 networks=[]
 for _,g in sorted(groups.items()):
  equivalent={}
  for r in g.pop('records'):
   k=canonical({a:r[a]for a in('from','to','order','preferred_label','weight')});equivalent.setdefault(k,[]).append(r)
  arcs=[];suppressed=[]
  for k,records in sorted(equivalent.items()):
   highest=max(r['provenance']['priority']for r in records);winners=[r for r in records if r['provenance']['priority']==highest]
   sources=sorted((r['provenance']for r in records),key=canonical)
   if any(r['provenance']['use']=='prohibited'for r in winners):suppressed.append({'equivalence_sha256':digest(k.decode()),'reason':'PROHIBITED_AT_MAX_PRIORITY','provenance':sources});continue
   arc={a:winners[0][a]for a in('from','to','order','preferred_label','weight')};arc.update(priority=highest,provenance=sources);arcs.append(arc)
  if g['kind']=='calculation':
   pairs=[(r['from'],r['to'])for r in arcs]
   if len(pairs)!=len(set(pairs)):g['issues'].add('MULTIPLE_EFFECTIVE_CALCULATION_RELATIONSHIPS')
  arcs.sort(key=lambda a:(a['from']or'',Fraction(int(a['order']['numerator']),int(a['order']['denominator'])),a['to']or'',a['preferred_label']or'',canonical(a['weight'])))
  vertices={v for a in arcs for v in(a['from'],a['to'])if v is not None};degree={v:0 for v in vertices};children={v:[]for v in vertices};depth={v:0 for v in vertices}
  for a in arcs:
   if a['from']is not None and a['to']is not None:children[a['from']].append(a['to']);degree[a['to']]+=1
  roots=sorted(v for v in vertices if degree[v]==0);pending=deque(roots);seen=0
  while pending:
   parent=pending.popleft();seen+=1
   for child in children[parent]:
    depth[child]=max(depth[child],depth[parent]+1);degree[child]-=1
    if not degree[child]:pending.append(child)
  if seen!=len(vertices):g['issues'].add('DIRECTED_RELATIONSHIP_CYCLE')
  if any(v>32 for v in depth.values()):g['issues'].add('RELATIONSHIP_DEPTH_UNSUPPORTED')
  g.update(arcs=arcs,suppressed=suppressed,roots=roots,issues=sorted(g['issues']));g['usable']=not g['issues'];networks.append(g)
 result={'schema':'gig.sec.xbrl.effective_relationships.v1','profile':PROFILE,'networks':networks,'input_arcs':count,'complete_taxonomy_validation':False,'scope':'Standard locator-to-concept presentation/calculation;unsupported role content invalidates whole role/kind;no label text inference'}
 result['sha256']=digest(result)
 if len(canonical(result))>4*1024*1024:raise XBRLError('effective_output_budget')
 return result
