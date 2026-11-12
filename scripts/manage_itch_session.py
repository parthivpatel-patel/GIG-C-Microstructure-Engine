#!/usr/bin/env python3
"""Explicit private authored ITCH session operations. Never starts an application.

Expected hashes are mandatory independent admission,not hashes learned from the
same untrusted file. Schema/code migration is explicit and creates a new revision.
"""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from terminal.itch_product import load,migrate,save_new,digest,read_private,continue_source
from gig_microstructure.itch_recovery import ItchSourceAdmission,MAX_BYTES
from terminal.verification.artifacts import read_bytes

def main(argv=None):
 p=argparse.ArgumentParser();p.add_argument('action',choices=['inspect','migrate','continue-source']);p.add_argument('--input',required=True);p.add_argument('--expected-sha256',required=True);p.add_argument('--output');p.add_argument('--source');p.add_argument('--source-sha256');p.add_argument('--container',choices=['binary_file','single_gzip']);p.add_argument('--first-frame',type=int);p.add_argument('--first-ordinal',type=int);a=p.parse_args(argv)
 if a.action!='continue-source'and any(v is not None for v in(a.source,a.source_sha256,a.container,a.first_frame,a.first_ordinal)):p.error('source arguments require continue-source')
 try:
  if a.action=='inspect':
   if a.output:p.error('inspect does not write an output')
   product=load(a.input,a.expected_sha256);s=product.owner.status();result={'schema':'gig.itch.product_operation.v1','status':'VALID','source_records':s['source_records'],'capture':s['capture'],'generation':s['generation'],'selected_book':product.selected_book,'playing':False,'provider_connected':False}
  elif a.action=='migrate':
   if not a.output:p.error('migrate requires a new immutable output path')
   raw=read_private(a.input);new=migrate(raw,a.expected_sha256);sha=digest(new);save_new(a.output,new,sha);result={'schema':'gig.itch.product_operation.v1','status':'MIGRATED','output_sha256':sha,'source_sha256':a.expected_sha256,'provider_connected':False}
  else:
   if not a.output or any(v is None for v in(a.source,a.source_sha256,a.container,a.first_frame,a.first_ordinal)):p.error('continue-source requires source/hash/container/boundary and a new output')
   raw=read_private(a.input);product=load(a.input,a.expected_sha256);status=product.owner.status()
   admission=ItchSourceAdmission(a.source_sha256,status['capture'],int(status['generation']),a.container,a.first_frame,a.first_ordinal)
   new=continue_source(raw,a.expected_sha256,read_private(a.source,limit=MAX_BYTES),admission);sha=digest(new);save_new(a.output,new,sha)
   result={'schema':'gig.itch.product_operation.v1','status':'SOURCE_CONTINUED','output_sha256':sha,'from_bundle_sha256':a.expected_sha256,'source_sha256':a.source_sha256,'provider_connected':False}
  print(json.dumps(result,sort_keys=True));return 0
 except (ValueError,OSError,RuntimeError):
  print(json.dumps({'schema':'gig.itch.product_operation.v1','status':'REJECTED','reason':'private_input_integrity_schema_or_migration_admission','raw_retained':False,'provider_connected':False}));return 1
if __name__=='__main__':raise SystemExit(main())
