#!/usr/bin/env python3
"""Offline supplied-instance research export. Never fetches a URL or reads secrets."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from terminal.verification.artifacts import read_bytes,decode,write_private
from terminal.stocks.xbrl_instance import selected_concepts,XBRLError
from terminal.stocks.xbrl_collection import FilingCollection,MAX_BATCH,MAX_BATCH_BYTES

def inspect(batch_path,as_of,*,allow_observed=False):
 path=Path(batch_path).absolute();batch=decode(read_bytes(path,128*1024))
 if set(batch)!={'schema','issuer_cik','origin','entries'}or batch['schema']!='gig.sec.xbrl.input_batch.v1'or type(batch['entries'])is not list or not 1<=len(batch['entries'])<=MAX_BATCH:raise XBRLError('xbrl_input_batch_contract')
 collection=FilingCollection(batch['issuer_cik'],origin=batch['origin'],allow_observed=allow_observed)
 entries=[];total=0
 for record in batch['entries']:
  if type(record)is not dict or set(record)!={'path','manifest','gaap_namespace'}or type(record['path'])is not str or len(record['path'])>512:raise XBRLError('xbrl_input_entry_contract')
  relative=Path(record['path'])
  if relative.is_absolute()or '..'in relative.parts:raise XBRLError('xbrl_input_path_scope')
  raw=read_bytes(path.parent/relative,2*1024*1024);total+=len(raw)
  if total>MAX_BATCH_BYTES:raise XBRLError('xbrl_batch_byte_budget')
  entries.append({'raw':raw,'manifest':record['manifest'],'concepts':selected_concepts(record['gaap_namespace'])})
 collection.ingest_batch(entries);result=collection.at_acceptance_time(as_of)
 summary={'schema':'gig.sec.xbrl.offline_summary.v1','status':'OFFLINE_PROFILE_VALIDATED','origin':collection.origin,'supplied_filings':len(entries),'source_bytes':total,'collection_sha256':result['collection_sha256'],'selection_sha256':result['selection_sha256'],'selected_facts':sum(map(len,result['history'].values())),'exclusions':result['exclusions'],'unresolved_amendment_count':len(result['unresolved_amendment_filings']),'complete_statements_or_history':False,'provider_requested':False,'raw_source_retained':False}
 return summary,result

def main(argv=None):
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--batch',required=True);parser.add_argument('--as-of',required=True);parser.add_argument('--output');parser.add_argument('--allow-observed',action='store_true',help='Only for a separately authorized private supplied copy;does not fetch or grant rights')
 args=parser.parse_args(argv)
 try:
  summary,result=inspect(args.batch,args.as_of,allow_observed=args.allow_observed)
  if args.output:write_private(args.output,result)
 except (ValueError,TypeError,KeyError,OSError,MemoryError)as exc:
  reason=str(exc)if isinstance(exc,XBRLError)else'resource_exhausted'if isinstance(exc,MemoryError)else'input_contract_or_resource_failure'
  print(json.dumps({'schema':'gig.sec.xbrl.offline_summary.v1','status':'REJECTED','reason':reason,'provider_requested':False,'raw_source_retained':False}));return 2
 print(json.dumps(summary,sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
