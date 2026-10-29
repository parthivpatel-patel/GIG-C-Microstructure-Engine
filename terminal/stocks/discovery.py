"""Exact-identifier union,not guessed security equivalence or listing completeness."""
from .directory import SearchIndex

def snapshot(workspace):
 cached=getattr(workspace,'_discovery_cache',None)
 if cached and cached[0] is workspace.catalog and cached[1] is workspace.issuers:return cached[2]
 rows={s:{**r,'cik':None,'identity_kind':'LISTING_OR_FALLBACK_IDENTITY'} for s,r in workspace.catalog.rows.items()}
 for s,r in workspace.issuers.items():
  if s in rows:rows[s]={**rows[s],'cik':r['cik'],'identity_kind':'CATALOG_AND_SEC_TICKER_MAPPING'}
  else:rows[s]={'symbol':s,'name':r['company_name'],'exchange':'UNVERIFIED','asset_id':None,'cik':r['cik'],'security_type':'SEC_REGISTRANT_NOT_LISTING_CLASSIFICATION','listing_status':'NOT_ESTABLISHED_BY_SEC_TICKER_MAPPING','identity_kind':'SEC_TICKER_MAPPING_ONLY'}
 index=SearchIndex(rows);workspace._discovery_cache=(workspace.catalog,workspace.issuers,index);return index

def search(workspace,query,offset=0,limit=20,filters=None):
 c=workspace.catalog
 return {**snapshot(workspace).search(query,offset,limit,filters),'schema':'gig.security.discovery.v2','catalog_count':len(set(c.rows)|set(workspace.issuers)),'source':{**c.source,'authority':c.source['authority'] if not workspace.issuers else 'EXACT_SYMBOL_UNION_OF_CATALOG_AND_SEC_IDENTITIES','source_classifications':sorted({c.source.get('classification',c.source['authority']),*([] if workspace.issuer_source is None else [workspace.issuer_source['classification']])}),'sec_identity_source':workspace.issuer_source,'sec_identity_count':len(workspace.issuers),'coverage':'Identifiers from accepted reference snapshots;not a complete current US listing,tradability or feed-entitlement claim. No alias/name-based CIK inference.'},'reason':c.reason}
