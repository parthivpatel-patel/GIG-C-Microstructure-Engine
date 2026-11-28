"""V11 direct closed typed cubes with independently rederived numeric V6 receipts.

Original XML is replayed by the producer. Consumers check retained source and
semantic consistency; these receipts do not authenticate source bytes or issuers.
Scalar checks preserve reported trees and never establish typed-value equality.
"""
import copy,re
from .xbrl_instance import X,tag,canonical,digest,parse_xml,XBRLError,MAX_FACTS
from .xbrl_types import XS,QN,_bound_sources
from .xbrl_typed_dimensions import BOUNDS_PROFILE as SCALAR_PROFILE,QNAME_NIL_PROFILE,TEMPORAL_PROFILE,_scalar
from .xbrl_effective_cross_role import _schema_sources,_validate_schema_sources
from .xbrl_dts import walk,uri

PROFILE='DIRECT_CLOSED_TYPED_BOUND_HYPERCUBE_V11'
SCOPE='One original-DTS direct positive closed typed+explicit hypercube;numeric V6 inherited bounds and retained declaration/source/tree consistency;no typed equality,negative,inherited/cross-role cubes,context synthesis,financial promotion or source authentication'
QNAME_NIL_DRS_PROFILE='DIRECT_CLOSED_TYPED_QNAME_NIL_HYPERCUBE_V12'
QNAME_NIL_SCOPE=SCOPE+';direct xs:QName expansion and declared nillable scalar elements'
TEMPORAL_DRS_PROFILE='DIRECT_CLOSED_TYPED_TEMPORAL_HYPERCUBE_V14'
TEMPORAL_SCOPE=QNAME_NIL_SCOPE+';bounded direct XML Schema date,time,dateTime and whitespace-derived string lexicals'
OPEN_DRS_PROFILE='DIRECT_OPEN_TYPED_HYPERCUBE_V15'
OPEN_SCOPE='One original-DTS direct positive open typed+explicit hypercube;required axes and reported extra dimensions revalidated against supplied declarations and domains;no dimension promotion,typed equality,negative,inheritance or source authentication'
SCALAR_BY_DRS_PROFILE={
 PROFILE:(SCALAR_PROFILE,11,SCOPE),
 QNAME_NIL_DRS_PROFILE:(QNAME_NIL_PROFILE,12,QNAME_NIL_SCOPE),
 TEMPORAL_DRS_PROFILE:(TEMPORAL_PROFILE,14,TEMPORAL_SCOPE),
 OPEN_DRS_PROFILE:(TEMPORAL_PROFILE,15,OPEN_SCOPE),
}
MAX_OUTPUT=8*1024*1024
D='http://xbrl.org/2005/xbrldt'
SHA=re.compile('[0-9a-f]{64}')
ID=re.compile('[A-Za-z_][A-Za-z0-9_.-]{0,127}')


def _schema_receipts(supplied,dts,diagnostics):
 schemas=_schema_sources(supplied,dts['documents']);types=[];elements={}
 for schema in schemas:
  key=schema['source_uri'];root=parse_xml(supplied[key]['raw']);namespace=schema['target_namespace'];ids=set()
  for node in walk(root):
   id_=node.attrs.get('id')
   if id_ is not None:
    if not ID.fullmatch(id_)or id_ in ids:raise XBRLError('drs_typed_bound_schema_id')
    ids.add(id_)
  for node in root.children:
   if node.name in(tag(XS,'simpleType'),tag(XS,'complexType')):
    types.append({'type':tag(namespace,node.attrs['name']),'source_uri':key,'source_sha256':schema['source_sha256'],'node_ordinal':node.source_ordinal,'kind':node.name})
   if node.name==tag(XS,'element')and 'id'in node.attrs:elements[key+'#'+node.attrs['id']]=node
 domains={}
 for context in diagnostics['contexts']:
  for member in context['typed_members']:
   if member['status']!='VALIDATED_SUPPORTED_TYPED_SCALAR':raise XBRLError('drs_typed_scalar_semantics_unsupported')
   domain=member['domain'];ref=domain['typed_domain_ref'];node=elements[ref]
   domains[ref]={'domain':copy.deepcopy(domain),'source_sha256':supplied[domain['schema_uri']]['sha256'],'node_ordinal':node.source_ordinal,'declaration':copy.deepcopy(dts['concepts'][domain['concept']]['declaration'])}
 return schemas,sorted(types,key=lambda r:(r['source_uri'],r['node_ordinal'])),[domains[k]for k in sorted(domains)]


def _declarations(concepts,types,schemas):
 # A QName and a digest alone cannot join declarations to their schema namespace.
 fields={'concept','type','substitution_group','period_type','balance','abstract','nillable'}
 for name,entry in concepts.items():
  decl=entry['declaration'];sources=entry['source_documents']
  if set(entry)!={'declaration','source_documents'}or set(decl)-{'typed_domain_ref'}!=fields or decl['concept']!=name or type(decl['abstract'])is not bool or type(decl['nillable'])is not bool:raise XBRLError('drs_typed_bound_concept_contract')
  for field in('type','substitution_group'):
   if decl[field]is not None and(type(decl[field])is not str or not QN.fullmatch(decl[field])):raise XBRLError('drs_typed_bound_concept_contract')
  if decl['period_type']not in(None,'instant','duration')or decl['balance']not in(None,'debit','credit'):raise XBRLError('drs_typed_bound_concept_contract')
  if 'typed_domain_ref'in decl:uri(decl['typed_domain_ref'],fragment=True)
  if len(sources)!=1 or schemas.get(sources[0])!=name.split('}',1)[0][1:]:raise XBRLError('drs_typed_bound_declaration_namespace_or_source')
 for name,entry in types.items():
  if len(entry['source_documents'])!=1 or schemas.get(entry['source_documents'][0])!=name.split('}',1)[0][1:]:raise XBRLError('drs_typed_bound_declaration_namespace_or_source')


def _validate_scalar_receipts(parsed,p):
 proof,concepts,types=_bound_sources(parsed);schemas=_validate_schema_sources(p['schema_sources'],proof['documents']);_declarations(concepts,types,schemas)
 docs={d['uri']:d for d in proof['documents']};type_kinds={};nodes=set()
 receipts=p['type_sources']
 if type(receipts)is not list or len(receipts)>2048:raise XBRLError('drs_typed_bound_type_receipt')
 for r in receipts:
  if type(r)is not dict or set(r)!={'type','source_uri','source_sha256','node_ordinal','kind'}or type(r['type'])is not str or r['type']not in types or r['source_uri']not in schemas or r['kind']not in(tag(XS,'simpleType'),tag(XS,'complexType'))or type(r['node_ordinal'])is not int or not 1<=r['node_ordinal']<=30000:raise XBRLError('drs_typed_bound_type_receipt')
  name=r['type'];key=(r['source_uri'],r['node_ordinal'])
  if r['kind']==tag(XS,'simpleType')and 'derivation'in types[name]['declaration']:raise XBRLError('drs_typed_bound_type_receipt')
  if key in nodes or name in type_kinds or types[name]['source_documents']!=[r['source_uri']]or docs[r['source_uri']]['sha256']!=r['source_sha256']:raise XBRLError('drs_typed_bound_type_receipt')
  nodes.add(key);type_kinds[name]=[r['kind']]
 if set(type_kinds)!=set(types)or receipts!=sorted(receipts,key=lambda r:(r['source_uri'],r['node_ordinal'])):raise XBRLError('drs_typed_bound_type_receipt')
 domains={};ids=set();receipts=p['domain_sources']
 if type(receipts)is not list or len(receipts)>4096:raise XBRLError('drs_typed_bound_domain_receipt')
 for r in receipts:
  if type(r)is not dict or set(r)!={'domain','source_sha256','node_ordinal','declaration'}or type(r['domain'])is not dict:raise XBRLError('drs_typed_bound_domain_receipt')
  domain=r['domain']
  if set(domain)!={'concept','type','schema_uri','schema_id','typed_domain_ref'}or any(type(v)is not str for v in domain.values())or not ID.fullmatch(domain['schema_id'])or type(r['node_ordinal'])is not int or not 1<=r['node_ordinal']<=30000:raise XBRLError('drs_typed_bound_domain_receipt')
  concept=domain['concept'];source=domain['schema_uri'];ref=domain['typed_domain_ref'];key=(source,r['node_ordinal'])
  if source not in schemas or ref!=source+'#'+domain['schema_id']or ref in domains or key in nodes or (source,domain['schema_id'])in ids or concept not in concepts or concepts[concept]['source_documents']!=[source]or docs[source]['sha256']!=r['source_sha256']:raise XBRLError('drs_typed_bound_domain_receipt')
  decl=concepts[concept]['declaration']
  if canonical(decl)!=canonical(r['declaration'])or decl['abstract']or decl['type']!=domain['type']or decl['substitution_group']is not None or decl['period_type']is not None or decl['balance']is not None or 'typed_domain_ref'in decl:raise XBRLError('drs_typed_bound_domain_receipt')
  domains[ref]=domain;nodes.add(key);ids.add((source,domain['schema_id']))
 if receipts!=sorted(receipts,key=lambda r:r['domain']['typed_domain_ref']):raise XBRLError('drs_typed_bound_domain_receipt')
 return proof,concepts,types,type_kinds,domains,docs


def _validate_receipts(parsed,p):
 proof,concepts,types,type_kinds,domains,docs=_validate_scalar_receipts(parsed,p)
 nets=p['definition']
 if type(nets)is not list or len(nets)!=1:raise XBRLError('drs_typed_bound_definition_receipt')
 net=nets[0]
 if type(net)is not dict or set(net)!={'role','source_uri','arcs','issues','usable_for_restricted_profile'}or type(net['role'])is not str or not 1<=len(net['role'])<=512 or net['issues']!=[]or net['usable_for_restricted_profile']is not True or net['source_uri']not in docs or docs[net['source_uri']]['kind']!='linkbase'or type(net['arcs'])is not list or not 1<=len(net['arcs'])<=4096:raise XBRLError('drs_typed_bound_definition_receipt')
 seen=set()
 for a in net['arcs']:
  if type(a)is not dict or set(a)!={'kind','from','to','closed','context_element','source_uri'}or a['kind']not in('all','hypercube-dimension','dimension-domain','domain-member','dimension-default')or a['from']not in concepts or a['to']not in concepts or type(a['closed'])is not bool or a['source_uri']!=net['source_uri']or a['kind']=='all'and a['context_element']not in('segment','scenario')or a['kind']!='all'and(a['closed']or a['context_element']is not None):raise XBRLError('drs_typed_bound_definition_receipt')
  key=(a['kind'],a['from'],a['to'])
  if key in seen:raise XBRLError('drs_typed_bound_definition_receipt')
  seen.add(key)
 if p['source_declarations_sha256']!=_fingerprint(proof,p):raise XBRLError('drs_typed_bound_source_fingerprint')
 return {'concepts':concepts,'type_declarations':types,'definition':nets,'unsupported_semantics':proof['unsupported_semantics']},type_kinds,domains,docs


def _fingerprint(proof,p):
 return digest({'source_graph':{k:proof.get(k,{})for k in('dts_sha256','documents','concept_declarations','type_declarations')},'receipts':{k:p[k]for k in('schema_sources','type_sources','domain_sources','definition')}})


def _validate_inline_traces(parsed):
    """Join retained segment receipts and repeat the selected inline transformation."""
    from .inline_set import MAX_CHAIN, MAX_DOCUMENTS, MAX_NODES, MAX_VALUE, TRANSFORMATION_PROFILE, _numeric
    from .xbrl_instance import identifier

    document_set = parsed['document_set']
    documents = document_set['documents']
    profile = document_set.get('transformation_profile')
    if (type(documents) is not list or not 1 <= len(documents) <= MAX_DOCUMENTS
            or profile not in (None, TRANSFORMATION_PROFILE)):
        raise XBRLError('drs_typed_bound_inline_documents')
    originals = {row['uri']: row['source']['source_sha256'] for row in documents}
    if (len(originals) != len(documents)
            or any(not SHA.fullmatch(value) for value in originals.values())):
        raise XBRLError('drs_typed_bound_inline_documents')
    traces = document_set['facts']
    if type(traces) is not list or len(traces) != len(parsed['facts']):
        raise XBRLError('drs_typed_bound_inline_trace')

    locations = set()
    identifiers = set()
    for fact, trace in zip(parsed['facts'], traces):
        segments = fact['inline_source_segments']
        if (type(trace) is not dict or set(trace) != {'kind', 'expanded_concept', 'segments',
                'extracted_text', 'transformed_lexical', 'format', 'scale', 'sign'}
                or trace['expanded_concept'] != fact['concept']
                or type(segments) is not list or not 1 <= len(segments) <= MAX_CHAIN + 1
                or canonical(trace['segments']) != canonical(segments)):
            raise XBRLError('drs_typed_bound_inline_trace')
        for index, segment in enumerate(segments):
            if type(segment) is not dict or set(segment) != {'document_uri', 'document_sha256', 'node_ordinal', 'id'}:
                raise XBRLError('drs_typed_bound_inline_segment')
            source = segment['document_uri']
            ordinal = segment['node_ordinal']
            if (source not in originals or originals[source] != segment['document_sha256']
                    or type(ordinal) is not int or not 0 < ordinal < MAX_NODES
                    or (source, ordinal) in locations):
                raise XBRLError('drs_typed_bound_inline_segment')
            locations.add((source, ordinal))
            identity = segment['id']
            if identity is not None or index:
                identifier(identity)
                if identity in identifiers:
                    raise XBRLError('drs_typed_bound_inline_segment')
                identifiers.add(identity)
        if segments[0]['id'] != fact['attributes'].get('id'):
            raise XBRLError('drs_typed_bound_inline_segment')

        text = trace['extracted_text']
        if type(text) is not str or len(text) > MAX_VALUE or trace['kind'] not in ('nonFraction', 'nonNumeric'):
            raise XBRLError('drs_typed_bound_inline_trace')
        numeric = trace['kind'] == 'nonFraction'
        if (numeric != (fact['unit_ref'] is not None)
                or (numeric or fact['nil']) and len(segments) != 1):
            raise XBRLError('drs_typed_bound_inline_trace')
        if numeric and not fact['nil']:
            lexical = _numeric(text, trace['format'], trace['scale'], trace['sign'], profile)
        else:
            if trace['format'] is not None or trace['sign'] is not None or trace['scale'] != ('0' if numeric else None):
                raise XBRLError('drs_typed_bound_inline_trace')
            lexical = text
        if trace['transformed_lexical'] != lexical or fact['lexical_value'] != lexical:
            raise XBRLError('drs_typed_bound_inline_trace')


def _diagnostics(parsed,dts,type_kinds,domains,scalar_profile):
 from .xbrl_calculation_report import _context,_source_fact
 from .xbrl_instance import identifier
 issuer=parsed['source']['issuer_cik'];seen=set();selected=[];members={};used_domains=set();count=0
 if type(issuer)is not str or not re.fullmatch('[0-9]{10}',issuer)or int(issuer)==0:raise XBRLError('drs_typed_bound_source')
 if type(parsed['source'].get('source_sha256'))is not str or not SHA.fullmatch(parsed['source']['source_sha256']):raise XBRLError('drs_typed_bound_source')
 is_set=parsed.get('schema')in('gig.sec.xbrl.inline_set.v1','gig.sec.xbrl.dimensional_inline_set.v11','gig.sec.xbrl.dimensional_inline_set.v12','gig.sec.xbrl.dimensional_inline_set.v14','gig.sec.xbrl.dimensional_inline_set.v15','gig.sec.xbrl.dimensional_inline_set.v20','gig.sec.xbrl.dimensional_inline_set.v21')
 original={**parsed,'schema':'gig.sec.xbrl.inline_set.v1'if is_set else'gig.sec.xbrl.instance.v1'}
 from .xbrl_instance import MAX_UNITS, _reported_numeric_value, _validate_fact_accuracy, selected_concepts
 units=parsed['units']
 if type(units)is not dict or len(units)>MAX_UNITS:raise XBRLError('drs_typed_bound_unit')
 for key,unit in units.items():
  identifier(key)
  if type(unit)is not dict or set(unit)!={'numerator','denominator','semantic_sha256'}:raise XBRLError('drs_typed_bound_unit')
  for side in('numerator','denominator'):
   values=unit[side]
   if type(values)is not list or not(1 if side=='numerator'else 0)<=len(values)<=8 or any(type(v)is not str or not QN.fullmatch(v)for v in values)or values!=sorted(values):raise XBRLError('drs_typed_bound_unit')
  if unit['semantic_sha256']!=digest({k:unit[k]for k in('numerator','denominator')}):raise XBRLError('drs_typed_bound_unit')
 for key,context in sorted(parsed['contexts'].items()):
  identifier(key);_context(context,issuer);rows=[];axes=set()
  for dimension in context['dimensions']:
   if type(dimension)is not dict or set(dimension)!={'dimension','context_element','kind','member'}or type(dimension['dimension'])is not str or not QN.fullmatch(dimension['dimension'])or dimension['dimension']in axes or dimension['context_element']not in('segment','scenario')or dimension['kind']not in('typed','explicit'):raise XBRLError('drs_typed_bound_context')
   axes.add(dimension['dimension'])
   if dimension['kind']=='explicit':
    if type(dimension['member'])is not str or not QN.fullmatch(dimension['member']):raise XBRLError('drs_typed_bound_context')
    continue
   count+=1
   if count>4096:raise XBRLError('drs_typed_bound_member_budget')
   axis=dts['concepts'][dimension['dimension']]['declaration'];ref=axis.get('typed_domain_ref');domain=domains.get(ref)
   if axis['abstract']is not True or axis['substitution_group']!=tag(D,'dimensionItem')or domain is None:raise XBRLError('drs_typed_bound_domain_binding')
   reason,scalar=_scalar(dimension['member'],domain,dts,type_kinds,profile=scalar_profile)
   if reason:raise XBRLError('drs_typed_scalar_semantics_unsupported')
   used_domains.add(ref);rows.append({'dimension':dimension['dimension'],'member_tree_sha256':digest(dimension['member']),'domain':domain,'scalar_validation':scalar,'status':'VALIDATED_SUPPORTED_TYPED_SCALAR'})
  if rows:members[key]=rows
 if is_set:
  _validate_inline_traces(parsed)
 for fact in parsed['facts']:
  if type(fact)is not dict or fact.get('admission')not in('ADMITTED_PROFILE','CONFLICTED_EXACT_VALUES','UNVERIFIED_CONCEPT','PERIOD_OR_UNIT_MISMATCH')or type(fact.get('source_fact_id'))is not str or not SHA.fullmatch(fact['source_fact_id']):raise XBRLError('drs_typed_bound_fact_identity')
  if fact['source_fact_id']in seen:raise XBRLError('drs_typed_bound_fact_identity')
  seen.add(fact['source_fact_id'])
  _source_fact(original,fact)
  if fact['admission']not in('ADMITTED_PROFILE','CONFLICTED_EXACT_VALUES'):continue
  identifier(fact['context_ref']);identifier(fact['unit_ref'])
  context=parsed['contexts'][fact['context_ref']];unit=units[fact['unit_ref']]
  if type(fact['nil'])is not bool or type(fact['lexical_value'])is not str or len(fact['lexical_value'])>16384:raise XBRLError('drs_typed_bound_fact_identity')
  attributes=fact['attributes']
  if type(attributes)is not dict or len(attributes)>24 or any(type(k)is not str or len(k)>640 or type(v)is not str or len(v)>1024 for k,v in attributes.items())or any(attributes.get(k)!=fact[field]for k,field in(('contextRef','context_ref'),('unitRef','unit_ref'),('decimals','decimals'),('precision','precision'))):raise XBRLError('drs_typed_bound_fact_identity')
  _validate_fact_accuracy(fact['decimals'],fact['precision'])
  nil_lexical=attributes.get(tag('http://www.w3.org/2001/XMLSchema-instance','nil'),'false')
  if nil_lexical not in('true','false','1','0')or fact['nil']!=(nil_lexical in('true','1')):raise XBRLError('drs_typed_bound_fact_identity')
  lexical=fact['lexical_value'].strip(' \t\r\n')
  if fact['nil']:
   if fact['value']is not None or lexical or fact['nil_status']!='NIL_REPORTED_UNAVAILABLE':raise XBRLError('drs_typed_bound_fact_identity')
  elif type(fact['value'])is not str or fact['nil_status']is not None or fact['value']!=_reported_numeric_value(fact['lexical_value']):raise XBRLError('drs_typed_bound_fact_identity')
  if fact['context_sha256']!=context['semantic_sha256']or fact['unit_sha256']!=unit['semantic_sha256']:raise XBRLError('drs_typed_bound_fact_identity')
  decl=dts['concepts'][fact['concept']]['declaration'];period=context['period']['kind']
  if decl['period_type']!=period or decl['abstract']or decl['substitution_group']!=tag(X,'item')or fact['nil']and not decl['nillable']:raise XBRLError('drs_typed_bound_fact_declaration')
  namespace = fact['concept'][1:].split('}', 1)[0]
  if re.fullmatch(r'https?://fasb\.org/us-gaap/[0-9]{4}', namespace):
   spec = selected_concepts(namespace).get(fact['concept'])
   if spec is None or any(fact[k] != spec[k] for k in ('metric', 'local_name')):
    raise XBRLError('drs_typed_bound_fact_concept')
   if period != spec['period_type'] or any(unit[k] != spec[k] for k in ('numerator', 'denominator')):
    raise XBRLError('drs_typed_bound_fact_concept')
  selected.append({'source_fact_id':fact['source_fact_id'],'concept':fact['concept'],'source_documents':dts['concepts'][fact['concept']]['source_documents'],'period_type':period,'declared_type':decl['type'],'type_validation':'NOT_PERFORMED'})
 if used_domains!=set(domains)or canonical(selected)!=canonical(parsed['dts_corroboration']['selected_facts']):raise XBRLError('drs_typed_bound_selected_binding')
 return {'contexts':[{'context_id':key,'typed_members':value}for key,value in sorted(members.items())]}


def corroborate_typed_bounds(parsed,dts,documents,allow_observed,instance_uri,*,profile=PROFILE):
 from .xbrl_typed_dimensions import check_typed_contexts
 from .xbrl_dimensions import _typed_original_graph,_typed_records
 scalar_profile,version,scope=SCALAR_BY_DRS_PROFILE[profile]
 # Exact observed approval/source receipts are checked before either XML reader.
 diagnostics=check_typed_contexts(parsed,dts,documents,profile=scalar_profile,allow_observed=allow_observed)
 supplied=_typed_original_graph(parsed,dts,documents,instance_uri)
 if diagnostics['unsupported_member_count']:raise XBRLError('drs_typed_scalar_semantics_unsupported')
 schemas,types,domains=_schema_receipts(supplied,dts,diagnostics)
 p={'profile':profile,'facts':[],'schema_sources':schemas,'type_sources':types,'domain_sources':domains,'definition':copy.deepcopy(dts['definition']),'complete_drs_validation':False,'scope':scope}
 p['source_declarations_sha256']=_fingerprint(parsed['dts_corroboration'],p)
 graph,kinds,domain_map,docs=_validate_receipts(parsed,p)
 checked=_diagnostics(parsed,graph,kinds,domain_map,scalar_profile)
 p['facts']=_typed_records(parsed,graph,checked,docs,open_cube=profile==OPEN_DRS_PROFILE)
 result=copy.deepcopy(parsed);result.pop('canonical_sha256');result['schema']=f'gig.sec.xbrl.dimensional_inline_set.v{version}' if parsed['schema']=='gig.sec.xbrl.inline_set.v1' else f'gig.sec.xbrl.dimensional_instance.v{version}';result['dts_corroboration']['dimensional_validation']=p
 result['canonical_sha256']=digest(result)
 if len(canonical(result))>MAX_OUTPUT:raise XBRLError('drs_typed_bound_output_budget')
 return result


def validate_typed_bound_result(parsed):
 """Recompute the versioned typed proof in filing and collection consumers."""
 from .xbrl_dimensions import _typed_records
 try:
  version=parsed['schema'].rsplit('.',1)[1]
  profiles={'v11':PROFILE,'v12':QNAME_NIL_DRS_PROFILE,'v14':TEMPORAL_DRS_PROFILE,'v15':OPEN_DRS_PROFILE}
  profile=profiles[version]
  scalar_profile,_,scope=SCALAR_BY_DRS_PROFILE[profile]
  p=parsed['dts_corroboration']['dimensional_validation']
  if type(p)is not dict or set(p)!={'profile','facts','schema_sources','type_sources','domain_sources','definition','complete_drs_validation','scope','source_declarations_sha256'}or p['profile']!=profile or p['scope']!=scope or p['complete_drs_validation']is not False or type(p['facts'])is not list or len(p['facts'])>MAX_FACTS or len(canonical(parsed))>MAX_OUTPUT:raise XBRLError('drs_typed_bound_result_contract')
  graph,kinds,domains,docs=_validate_receipts(parsed,p);diagnostics=_diagnostics(parsed,graph,kinds,domains,scalar_profile)
  if canonical(_typed_records(parsed,graph,diagnostics,docs,open_cube=profile==OPEN_DRS_PROFILE))!=canonical(p['facts']):raise XBRLError('drs_typed_bound_result_contract')
 except (XBRLError,KeyError,TypeError,ValueError,ArithmeticError,AttributeError):raise XBRLError('xbrl_dimensional_result_contract')from None
