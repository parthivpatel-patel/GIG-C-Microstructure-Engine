#!/usr/bin/env python3
"""Offline supplied-instance research export. Never fetches a URL or reads secrets."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from terminal.verification.artifacts import read_bytes,decode,write_private
from terminal.stocks.xbrl_instance import selected_concepts,XBRLError
from terminal.stocks.xbrl_collection import FilingCollection,MAX_BATCH,MAX_BATCH_BYTES
from terminal.stocks.xbrl_dimensions import INHERITED_PROFILE,PROFILES as DIMENSIONAL_PROFILES
from terminal.stocks.xbrl_dimensional_calculation import PROFILE as DIMENSIONAL_CALCULATIONS,BOUND_NUMERIC_PROFILE,WEIGHTED_DIMENSIONAL_PROFILE
from terminal.stocks.xbrl_types import BOUNDS_PROFILE
from terminal.stocks.xbrl_calculation_report import WEIGHTED_PROFILE
from terminal.stocks.inline_set import TRANSFORMATION_PROFILE

def inspect(batch_path,as_of,*,allow_observed=False,dimensional_profile=None,company_symbol=None,statement_role=None,statement_form='10-K',statement_profile='legacy-v1',embedded_profile=None,inline_transformation_profile=None,calculation_profile=None,calculation_role=None,accounting_roles=None,compare_at=()):
 from terminal.stocks.xbrl_dts import EMBEDDED_PROFILE
 if embedded_profile not in(None,EMBEDDED_PROFILE):raise XBRLError('dts_embedded_profile_unsupported')
 if statement_profile not in('legacy-v1','accuracy-extension-v2'):raise XBRLError('statement_profile_unsupported')
 if statement_profile!='legacy-v1'and company_symbol is None:raise XBRLError('statement_profile_requires_company')
 if dimensional_profile not in(None,*DIMENSIONAL_PROFILES):raise XBRLError('xbrl_dimensional_profile_unsupported')
 if calculation_profile not in(None,DIMENSIONAL_CALCULATIONS,BOUND_NUMERIC_PROFILE,WEIGHTED_PROFILE,WEIGHTED_DIMENSIONAL_PROFILE):
  raise XBRLError('xbrl_calculation_export_profile')
 if calculation_profile is not None and (company_symbol is None or dimensional_profile is not None or statement_role is not None):
  raise XBRLError('xbrl_calculation_export_requires_company_and_original_artifact')
 if calculation_role is not None and calculation_profile is None:
  raise XBRLError('xbrl_calculation_role_requires_profile')
 if accounting_roles is not None and (company_symbol is None or statement_role is not None or calculation_profile is not None):
  raise XBRLError('xbrl_accounting_export_requires_exclusive_company_mode')
 if compare_at and (accounting_roles is None or type(compare_at) not in (list,tuple) or len(compare_at)>7):
  raise XBRLError('xbrl_vintage_comparison_cutoff_contract')
 path=Path(batch_path).absolute();batch=decode(read_bytes(path,128*1024),numeric_policy='exact-integer')
 if batch.get('schema')=='gig.sec.xbrl.input_inline_set_batch.v1':return inspect_inline_sets(path,batch,as_of,allow_observed=allow_observed,dimensional_profile=dimensional_profile,company_symbol=company_symbol,statement_role=statement_role,statement_form=statement_form,statement_profile=statement_profile,embedded_profile=embedded_profile,inline_transformation_profile=inline_transformation_profile,calculation_profile=calculation_profile,calculation_role=calculation_role,accounting_roles=accounting_roles,compare_at=compare_at)
 if inline_transformation_profile is not None:raise XBRLError('xbrl_inline_transformation_requires_document_set')
 dts=batch.get('schema')=='gig.sec.xbrl.input_dts_batch.v1'
 if (dimensional_profile is not None or embedded_profile is not None or calculation_profile is not None or accounting_roles is not None)and not dts:raise XBRLError('xbrl_dimensional_profile_requires_dts')
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
 if dts:collection.ingest_dts_batch(entries,numeric_profile=batch['numeric_profile'],dimensional_profile=dimensional_profile,embedded_profile=embedded_profile)
 else:collection.ingest_batch(entries)
 if calculation_profile is not None:
  return calculation_export(collection,entries,as_of,company_symbol,statement_form,calculation_profile,
                            calculation_role,embedded_profile,inline=False)
 if accounting_roles is not None:
  return accounting_export(collection,entries,as_of,company_symbol,statement_form,accounting_roles,
                           embedded_profile,inline=False,compare_at=compare_at)
 result=collection.at_acceptance_time(as_of)
 summary={'schema':'gig.sec.xbrl.offline_summary.v1','status':'OFFLINE_PROFILE_VALIDATED','origin':collection.origin,'supplied_filings':len(entries),'source_bytes':total,'collection_sha256':result['collection_sha256'],'selection_sha256':result['selection_sha256'],'selected_facts':sum(map(len,result['history'].values())),'exclusions':result['exclusions'],'unresolved_amendment_count':len(result['unresolved_amendment_filings']),'complete_statements_or_history':False,'provider_requested':False,'raw_source_retained':False}
 return company_export(collection,as_of,company_symbol,statement_role,statement_form,statement_profile)if company_symbol is not None else(summary,result)

def inspect_inline_sets(path,batch,as_of,*,allow_observed=False,dimensional_profile=None,company_symbol=None,statement_role=None,statement_form='10-K',statement_profile='legacy-v1',embedded_profile=None,inline_transformation_profile=None,calculation_profile=None,calculation_role=None,accounting_roles=None,compare_at=()):
 from terminal.stocks.xbrl_dts import EMBEDDED_PROFILE
 if embedded_profile not in(None,EMBEDDED_PROFILE):raise XBRLError('dts_embedded_profile_unsupported')
 if statement_profile not in('legacy-v1','accuracy-extension-v2'):raise XBRLError('statement_profile_unsupported')
 if statement_profile!='legacy-v1'and company_symbol is None:raise XBRLError('statement_profile_requires_company')
 if inline_transformation_profile not in(None,TRANSFORMATION_PROFILE):raise XBRLError('inline_set_transformation_profile_unsupported')
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
 collection.ingest_inline_set_batch(entries,numeric_profile=batch['numeric_profile'],dimensional_profile=dimensional_profile,embedded_profile=embedded_profile,transformation_profile=inline_transformation_profile)
 if calculation_profile is not None:
  return calculation_export(collection,entries,as_of,company_symbol,statement_form,calculation_profile,
                            calculation_role,embedded_profile,inline=True)
 if accounting_roles is not None:
  return accounting_export(collection,entries,as_of,company_symbol,statement_form,accounting_roles,
                           embedded_profile,inline=True,transformation_profile=inline_transformation_profile,
                           compare_at=compare_at)
 result=collection.at_acceptance_time(as_of)
 summary={'schema':'gig.sec.xbrl.offline_summary.v1','status':'OFFLINE_PROFILE_VALIDATED','origin':collection.origin,'supplied_filings':len(entries),'supplied_inline_documents':count,'source_bytes':total,'collection_sha256':result['collection_sha256'],'selection_sha256':result['selection_sha256'],'selected_facts':sum(map(len,result['history'].values())),'exclusions':result['exclusions'],'unresolved_amendment_count':len(result['unresolved_amendment_filings']),'complete_statements_or_history':False,'provider_requested':False,'raw_source_retained':False}
 return company_export(collection,as_of,company_symbol,statement_role,statement_form,statement_profile)if company_symbol is not None else(summary,result)

def accounting_export(collection,entries,as_of,symbol,form,role_bindings,embedded_profile,*,inline,transformation_profile=None,compare_at=()):
 from terminal.stocks.service import StockWorkspace
 from terminal.stocks.financial_intelligence_product import company_source_accounting
 workspace=StockWorkspace(environment={})
 workspace.admit_xbrl_collection(symbol,collection)
 originals={}
 for entry in entries:
  if inline:
   if entry['taxonomy_documents'] is None:continue
   accession=entry['documents'][0]['manifest']['accession']
   originals[accession]={**entry,'transformation_profile':transformation_profile,
       'embedded_profile':embedded_profile,'acquisition_manifest':None,'expected_acquisition_manifest_sha256':None}
  else:
   accession=entry['manifest']['accession']
   originals[accession]={**entry,'embedded_profile':embedded_profile}
 if compare_at:
  from terminal.stocks.xbrl_statement_comparison import company_statement_vintage_comparison
  result=company_statement_vintage_comparison(workspace,symbol,[as_of,*compare_at],originals,role_bindings,form=form)
  return {'schema':'gig.sec.xbrl.company_vintage_comparison_summary.v1','status':result['status'],
          'symbol':symbol,'issuer_cik':collection.cik,'sha256':result['sha256'],'cutoffs':len(result['entries']),
          'provider_requested':False,'raw_source_retained':False},result
 result=company_source_accounting(workspace,symbol,as_of,originals,role_bindings,form=form)
 return {'schema':'gig.sec.xbrl.company_source_accounting_summary.v1','status':result['status'],
         'reason':result['reason'],'symbol':symbol,'issuer_cik':collection.cik,'sha256':result['sha256'],
         'provider_requested':False,'raw_source_retained':False},result


def calculation_export(collection,entries,as_of,symbol,form,profile,role,embedded_profile,*,inline):
 from terminal.stocks.service import StockWorkspace
 from terminal.stocks.xbrl_dts import discover,discover_inline_set
 from terminal.stocks.xbrl_product import company_contract
 from terminal.stocks.xbrl_calculation_product import company_calculation_contract
 workspace=StockWorkspace(environment={})
 workspace.admit_xbrl_collection(symbol,collection)
 selected=company_contract(workspace,symbol,as_of,form=form,profile='accuracy-extension-v2')
 source=selected['statement_view']['source_filing']
 graphs={}
 if source is not None and selected['statement_view']['status']!='AMBIGUOUS':
  accession=source['accession']
  for entry in entries:
   manifest=entry['documents'][0]['manifest'] if inline else entry['manifest']
   if manifest['accession']!=accession:continue
   if inline:
    if entry['taxonomy_documents'] is None:break
    references=[doc['manifest']['permission_reference'] for doc in sorted(entry['documents'], key=lambda doc:doc['uri'])]
    graphs[accession]=discover_inline_set(collection._filings[accession],entry['taxonomy_documents'],
        allow_observed=collection.allow_observed,permission_references=references,embedded_profile=embedded_profile)
   else:
    graphs[accession]=discover(entry['raw'],entry['instance_uri'],source['source_sha256'],entry['documents'],
        origin=source['origin'],allow_observed=collection.allow_observed,
        permission_reference=manifest['permission_reference'],embedded_profile=embedded_profile)
   break
 result=company_calculation_contract(workspace,symbol,as_of,graphs,role=role,form=form,
     dimensional_profile=INHERITED_PROFILE if profile!=WEIGHTED_PROFILE else None,
     numeric_profile=BOUNDS_PROFILE if profile==BOUND_NUMERIC_PROFILE else None,
     weight_profile=WEIGHTED_PROFILE if profile in (WEIGHTED_PROFILE,WEIGHTED_DIMENSIONAL_PROFILE) else None)
 summary={'schema':'gig.sec.xbrl.company_calculation_summary.v1','status':result['status'],
          'reason':result['reason'],'symbol':symbol,'issuer_cik':collection.cik,'sha256':result['sha256'],
          'provider_requested':False,'raw_source_retained':False}
 return summary,result


def company_export(collection,as_of,symbol,role,form,profile='legacy-v1'):
 from terminal.stocks.service import StockWorkspace
 from terminal.stocks.xbrl_product import company_contract
 workspace=StockWorkspace(environment={})
 workspace.admit_xbrl_collection(symbol,collection)
 result=company_contract(workspace,symbol,as_of,role=role,form=form,profile=profile)
 return {'schema':'gig.sec.xbrl.company_summary.v1','status':result['statement_view']['status'],'reason':result['statement_view']['reason'],'symbol':symbol,'issuer_cik':collection.cik,'origin':collection.origin,'sha256':result['sha256'],'provider_requested':False,'raw_source_retained':False},result

def main(argv=None):
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--batch',required=True);parser.add_argument('--as-of',required=True);parser.add_argument('--output');parser.add_argument('--allow-observed',action='store_true',help='Only for a separately authorized private supplied copy;does not fetch or grant rights')
 parser.add_argument('--dimensional-profile',choices=DIMENSIONAL_PROFILES)
 parser.add_argument('--inline-transformation-profile',choices=[TRANSFORMATION_PROFILE])
 parser.add_argument('--calculation-profile',choices=[DIMENSIONAL_CALCULATIONS,BOUND_NUMERIC_PROFILE,WEIGHTED_PROFILE,WEIGHTED_DIMENSIONAL_PROFILE])
 parser.add_argument('--calculation-role')
 parser.add_argument('--accounting-roles',help='Local JSON mapping from filing accessions to explicit statement and accounting roles')
 parser.add_argument('--compare-at',action='append',default=[],help='Additional increasing acceptance cutoff for an adjacent statement comparison')
 parser.add_argument('--company-symbol');parser.add_argument('--statement-role');parser.add_argument('--statement-form',choices=['10-K','10-Q'],default='10-K')
 parser.add_argument('--statement-profile',choices=['legacy-v1','accuracy-extension-v2'],default='legacy-v1')
 from terminal.stocks.xbrl_dts import EMBEDDED_PROFILE
 parser.add_argument('--embedded-linkbase-profile',choices=[EMBEDDED_PROFILE])
 args=parser.parse_args(argv)
 if args.statement_role is not None and args.company_symbol is None:parser.error('--statement-role requires --company-symbol')
 try:
  accounting_roles=None
  if args.accounting_roles is not None:
   accounting_roles=decode(read_bytes(args.accounting_roles,128*1024),numeric_policy='exact-integer')
   if type(accounting_roles)is not dict:raise XBRLError('xbrl_accounting_roles_mapping')
  summary,result=inspect(args.batch,args.as_of,allow_observed=args.allow_observed,dimensional_profile=args.dimensional_profile,company_symbol=args.company_symbol,statement_role=args.statement_role,statement_form=args.statement_form,statement_profile=args.statement_profile,embedded_profile=args.embedded_linkbase_profile,inline_transformation_profile=args.inline_transformation_profile,calculation_profile=args.calculation_profile,calculation_role=args.calculation_role,accounting_roles=accounting_roles,compare_at=args.compare_at)
  if args.output:
   if args.compare_at:
    from terminal.stocks.xbrl_statement_comparison import MAX_OUTPUT
    write_private(args.output,result,maximum_bytes=MAX_OUTPUT,compact=True)
   elif args.accounting_roles or args.calculation_profile:
    write_private(args.output,result,compact=True)
   else:
    write_private(args.output,result)
 except (ValueError,TypeError,KeyError,OSError,MemoryError)as exc:
  reason=str(exc)if isinstance(exc,XBRLError)else'resource_exhausted'if isinstance(exc,MemoryError)else'input_contract_or_resource_failure'
  print(json.dumps({'schema':'gig.sec.xbrl.offline_summary.v1','status':'REJECTED','reason':reason,'provider_requested':False,'raw_source_retained':False}));return 2
 print(json.dumps(summary,sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
