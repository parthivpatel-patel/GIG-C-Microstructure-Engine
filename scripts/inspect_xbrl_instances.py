#!/usr/bin/env python3
"""Offline supplied-instance research export. Never fetches a URL or reads secrets."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from terminal.verification.artifacts import read_bytes,decode,write_private
from terminal.stocks.xbrl_instance import selected_concepts,XBRLError
from terminal.stocks.xbrl_collection import FilingCollection,MAX_BATCH,MAX_BATCH_BYTES

def inspect(batch_path,as_of,*,allow_observed=False,dimensional_profile=None,company_symbol=None,statement_role=None,statement_form='10-K',statement_profile='legacy-v1'):
 if statement_profile not in('legacy-v1','accuracy-extension-v2'):raise XBRLError('statement_profile_unsupported')
 if statement_profile!='legacy-v1'and company_symbol is None:raise XBRLError('statement_profile_requires_company')
 from terminal.stocks.xbrl_dimensions import PROFILE as DIMENSIONS
 if dimensional_profile not in(None,DIMENSIONS):raise XBRLError('xbrl_dimensional_profile_unsupported')
 path=Path(batch_path).absolute();batch=decode(read_bytes(path,128*1024))
 if batch.get('schema')=='gig.sec.xbrl.input_inline_set_batch.v1':return inspect_inline_sets(path,batch,as_of,allow_observed=allow_observed,dimensional_profile=dimensional_profile,company_symbol=company_symbol,statement_role=statement_role,statement_form=statement_form,statement_profile=statement_profile)
 dts=batch.get('schema')=='gig.sec.xbrl.input_dts_batch.v1'
 if dimensional_profile is not None and not dts:raise XBRLError('xbrl_dimensional_profile_requires_dts')
 fields={'schema','issuer_cik','origin','entries'}|({'numeric_profile'}if dts else set())
 if set(batch)!=fields or batch['schema']not in('gig.sec.xbrl.input_batch.v1','gig.sec.xbrl.input_dts_batch.v1')or type(batch['entries'])is not list or not 1<=len(batch['entries'])<=MAX_BATCH:raise XBRLError('xbrl_input_batch_contract')
 if dts:
  from terminal.stocks.xbrl_types import PROFILES
  if batch['numeric_profile']not in(None,*PROFILES):raise XBRLError('xbrl_numeric_profile_unsupported')
 collection=FilingCollection(batch['issuer_cik'],origin=batch['origin'],allow_observed=allow_observed)
 entries=[];total=0
 for record in batch['entries']:
  if type(record)is not dict or set(record)!=({'path','manifest','gaap_namespace'}|({'instance_uri','documents'}if dts else set()))or type(record['path'])is not str or len(record['path'])>512:raise XBRLError('xbrl_input_entry_contract')
  relative=Path(record['path'])
  if relative.is_absolute()or '..'in relative.parts:raise XBRLError('xbrl_input_path_scope')
  raw=read_bytes(path.parent/relative,2*1024*1024);total+=len(raw)
  if total>MAX_BATCH_BYTES:raise XBRLError('xbrl_batch_byte_budget')
  entry={'raw':raw,'manifest':record['manifest'],'concepts':selected_concepts(record['gaap_namespace'])}
  if dts:
   if type(record['documents'])is not list or len(record['documents'])>16:raise XBRLError('xbrl_input_document_budget')
   docs=[]
   for document in record['documents']:
    if type(document)is not dict or set(document)!={'path','uri','sha256'}or type(document['path'])is not str or len(document['path'])>512:raise XBRLError('xbrl_input_document_contract')
    relative=Path(document['path'])
    if relative.is_absolute()or '..'in relative.parts:raise XBRLError('xbrl_input_path_scope')
    data=read_bytes(path.parent/relative,min(2*1024*1024,MAX_BATCH_BYTES-total));total+=len(data)
    if total>MAX_BATCH_BYTES:raise XBRLError('xbrl_batch_byte_budget')
    docs.append({'uri':document['uri'],'sha256':document['sha256'],'raw':data})
   entry.update(instance_uri=record['instance_uri'],documents=docs)
  entries.append(entry)
 if dts:collection.ingest_dts_batch(entries,numeric_profile=batch['numeric_profile'],dimensional_profile=dimensional_profile)
 else:collection.ingest_batch(entries)
 result=collection.at_acceptance_time(as_of)
 summary={'schema':'gig.sec.xbrl.offline_summary.v1','status':'OFFLINE_PROFILE_VALIDATED','origin':collection.origin,'supplied_filings':len(entries),'source_bytes':total,'collection_sha256':result['collection_sha256'],'selection_sha256':result['selection_sha256'],'selected_facts':sum(map(len,result['history'].values())),'exclusions':result['exclusions'],'unresolved_amendment_count':len(result['unresolved_amendment_filings']),'complete_statements_or_history':False,'provider_requested':False,'raw_source_retained':False}
 return company_export(collection,as_of,company_symbol,statement_role,statement_form,statement_profile)if company_symbol is not None else(summary,result)

def inspect_inline_sets(path,batch,as_of,*,allow_observed=False,dimensional_profile=None,company_symbol=None,statement_role=None,statement_form='10-K',statement_profile='legacy-v1'):
 if statement_profile not in('legacy-v1','accuracy-extension-v2'):raise XBRLError('statement_profile_unsupported')
 if statement_profile!='legacy-v1'and company_symbol is None:raise XBRLError('statement_profile_requires_company')
 from terminal.stocks.xbrl_types import PROFILES
 if set(batch)!={'schema','issuer_cik','origin','numeric_profile','entries'}or type(batch['entries'])is not list or not 1<=len(batch['entries'])<=MAX_BATCH or batch['numeric_profile']not in(None,*PROFILES):raise XBRLError('xbrl_input_inline_set_contract')
 collection=FilingCollection(batch['issuer_cik'],origin=batch['origin'],allow_observed=allow_observed);total=0;count=0;entries=[]
 def local(name):
  nonlocal total
  if type(name)is not str or not 1<=len(name)<=512:raise XBRLError('xbrl_input_path_scope')
  relative=Path(name)
  if relative.is_absolute()or '..'in relative.parts:raise XBRLError('xbrl_input_path_scope')
  raw=read_bytes(path.parent/relative,min(2*1024*1024,MAX_BATCH_BYTES-total));total+=len(raw)
  if total>MAX_BATCH_BYTES:raise XBRLError('xbrl_batch_byte_budget')
  return raw
 for entry in batch['entries']:
  if type(entry)is not dict or set(entry)!={'documents','taxonomy_documents','gaap_namespace'}or type(entry['documents'])is not list or not 1<=len(entry['documents'])<=8 or entry['taxonomy_documents']is not None and(type(entry['taxonomy_documents'])is not list or len(entry['taxonomy_documents'])>16):raise XBRLError('xbrl_input_inline_set_entry')
  documents=[];taxonomy=None
  for document in entry['documents']:
   if type(document)is not dict or set(document)!={'path','uri','manifest'}:raise XBRLError('xbrl_input_inline_document')
   documents.append({'uri':document['uri'],'manifest':document['manifest'],'raw':local(document['path'])});count+=1
  if entry['taxonomy_documents']is not None:
   taxonomy=[]
   for document in entry['taxonomy_documents']:
    if type(document)is not dict or set(document)!={'path','uri','sha256'}:raise XBRLError('xbrl_input_document_contract')
    taxonomy.append({'uri':document['uri'],'sha256':document['sha256'],'raw':local(document['path'])})
  entries.append({'documents':documents,'taxonomy_documents':taxonomy,'concepts':selected_concepts(entry['gaap_namespace'])})
 collection.ingest_inline_set_batch(entries,numeric_profile=batch['numeric_profile'],dimensional_profile=dimensional_profile);result=collection.at_acceptance_time(as_of)
 summary={'schema':'gig.sec.xbrl.offline_summary.v1','status':'OFFLINE_PROFILE_VALIDATED','origin':collection.origin,'supplied_filings':len(entries),'supplied_inline_documents':count,'source_bytes':total,'collection_sha256':result['collection_sha256'],'selection_sha256':result['selection_sha256'],'selected_facts':sum(map(len,result['history'].values())),'exclusions':result['exclusions'],'unresolved_amendment_count':len(result['unresolved_amendment_filings']),'complete_statements_or_history':False,'provider_requested':False,'raw_source_retained':False}
 return company_export(collection,as_of,company_symbol,statement_role,statement_form,statement_profile)if company_symbol is not None else(summary,result)

def company_export(collection,as_of,symbol,role,form,profile='legacy-v1'):
 from terminal.stocks.service import StockWorkspace
 from terminal.stocks.xbrl_product import company_contract
 workspace=StockWorkspace(environment={})
 workspace.admit_xbrl_collection(symbol,collection)
 result=company_contract(workspace,symbol,as_of,role=role,form=form,profile=profile)
 return {'schema':'gig.sec.xbrl.company_summary.v1','status':result['statement_view']['status'],'reason':result['statement_view']['reason'],'symbol':symbol,'issuer_cik':collection.cik,'origin':collection.origin,'sha256':result['sha256'],'provider_requested':False,'raw_source_retained':False},result

def main(argv=None):
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--batch',required=True);parser.add_argument('--as-of',required=True);parser.add_argument('--output');parser.add_argument('--allow-observed',action='store_true',help='Only for a separately authorized private supplied copy;does not fetch or grant rights')
 from terminal.stocks.xbrl_dimensions import PROFILE as DIMENSIONS
 parser.add_argument('--dimensional-profile',choices=[DIMENSIONS])
 parser.add_argument('--company-symbol');parser.add_argument('--statement-role');parser.add_argument('--statement-form',choices=['10-K','10-Q'],default='10-K')
 parser.add_argument('--statement-profile',choices=['legacy-v1','accuracy-extension-v2'],default='legacy-v1')
 args=parser.parse_args(argv)
 if args.statement_role is not None and args.company_symbol is None:parser.error('--statement-role requires --company-symbol')
 try:
  summary,result=inspect(args.batch,args.as_of,allow_observed=args.allow_observed,dimensional_profile=args.dimensional_profile,company_symbol=args.company_symbol,statement_role=args.statement_role,statement_form=args.statement_form,statement_profile=args.statement_profile)
  if args.output:write_private(args.output,result)
 except (ValueError,TypeError,KeyError,OSError,MemoryError)as exc:
  reason=str(exc)if isinstance(exc,XBRLError)else'resource_exhausted'if isinstance(exc,MemoryError)else'input_contract_or_resource_failure'
  print(json.dumps({'schema':'gig.sec.xbrl.offline_summary.v1','status':'REJECTED','reason':reason,'provider_requested':False,'raw_source_retained':False}));return 2
 print(json.dumps(summary,sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
