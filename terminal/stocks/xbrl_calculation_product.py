"""Acceptance-selected source-bound calculation export; no automatic graph/fact inference."""
import copy
from .xbrl_product import company_contract
from .xbrl_lineage import filing_lineage
from .xbrl_calculation_report import bind_calculation_report
from .xbrl_instance import digest,canonical,XBRLError
MAX_OUTPUT=256*1024

def company_calculation_contract(workspace,symbol,as_of,dts_graphs,*,role=None,form='10-K',rounding_mode='round-to-nearest',expected_collection_sha256=None):
 if type(dts_graphs)is not dict or len(dts_graphs)>32:raise XBRLError('calculation_product_graph_budget')
 if rounding_mode not in('round-to-nearest','truncation')or role is not None and(type(role)is not str or not 1<=len(role)<=512):raise XBRLError('calculation_product_query')
 # The existing selector is the authority for nanosecond cutoff/form/issuer and
 # same-time ambiguity. Presentation role is deliberately not calculation scope.
 selected=company_contract(workspace,symbol,as_of,form=form,profile='accuracy-extension-v2');view=selected['statement_view'];collection=workspace.xbrl_collections.get(symbol);identity=view['collection_sha256']
 if expected_collection_sha256 is not None and expected_collection_sha256!=identity:raise XBRLError('calculation_product_stale_collection')
 result={'schema':'gig.backend.company_calculations.v1','instrument':copy.deepcopy(selected['instrument']),'as_of':as_of,'cutoff_ns':view['cutoff_ns'],'form_family':form,'role':role,'rounding_mode':rounding_mode,'collection_sha256':identity,'status':'UNAVAILABLE','reason':view['reason'],'lineage':None,'report':None,'complete_statements':False,'read_only':True,'provider_requested':False,'policy':'Independent latest acceptance-qualified filing and exact supplied DTS;no cross-filing filling,accounting aliases or ambiguous network selection'}
 source=view['source_filing']
 if view['status']=='AMBIGUOUS':result['reason']='AMBIGUOUS_LATEST_FILING'
 elif source is not None and collection is not None:
  lineage=filing_lineage(collection,source['accession'],as_of);result['lineage']=lineage
  if lineage['status']!='SUPPLIED_CHAIN_RESOLVED':result['reason']='EXPLICIT_AMENDMENT_CHAIN_UNRESOLVED'
  elif source['accession']not in dts_graphs:result['reason']='ORIGINAL_DTS_NOT_SUPPLIED'
  else:
   report=bind_calculation_report(collection._filings[source['accession']],dts_graphs[source['accession']],role=role,rounding_mode=rounding_mode)
   result.update(status=report['status'],reason=report['reason'],role=report['role'],report=report)
 result['sha256']=digest(result)
 if len(canonical(result))>MAX_OUTPUT:raise XBRLError('calculation_product_output_budget')
 return result
