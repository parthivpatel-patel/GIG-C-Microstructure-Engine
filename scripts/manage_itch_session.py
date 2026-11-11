#!/usr/bin/env python3
"""Explicit private authored ITCH session operations. Never starts an application.

Expected hashes are mandatory independent admission,not hashes learned from the
same untrusted file. Schema/code migration is explicit and creates a new revision.
"""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from terminal.itch_product import load,migrate,save_new,digest,read_private
from terminal.verification.artifacts import read_bytes

def main(argv=None):
 p=argparse.ArgumentParser();p.add_argument('action',choices=['inspect','migrate']);p.add_argument('--input',required=True);p.add_argument('--expected-sha256',required=True);p.add_argument('--output');a=p.parse_args(argv)
 try:
  if a.action=='inspect':
   if a.output:p.error('inspect does not write an output')
   product=load(a.input,a.expected_sha256);s=product.owner.status();result={'schema':'gig.itch.product_operation.v1','status':'VALID','source_records':s['source_records'],'capture':s['capture'],'generation':s['generation'],'selected_book':product.selected_book,'playing':False,'provider_connected':False}
  else:
   if not a.output:p.error('migrate requires a new immutable output path')
   raw=read_private(a.input);new=migrate(raw,a.expected_sha256);sha=digest(new);save_new(a.output,new,sha);result={'schema':'gig.itch.product_operation.v1','status':'MIGRATED','output_sha256':sha,'source_sha256':a.expected_sha256,'provider_connected':False}
  print(json.dumps(result,sort_keys=True));return 0
 except (ValueError,OSError,RuntimeError):
  print(json.dumps({'schema':'gig.itch.product_operation.v1','status':'REJECTED','reason':'private_input_integrity_schema_or_migration_admission','raw_retained':False,'provider_connected':False}));return 1
if __name__=='__main__':raise SystemExit(main())
