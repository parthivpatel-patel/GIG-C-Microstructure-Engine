#!/usr/bin/env python3
"""Bounded offline qualification or separately gated owner-run public SEC reads.

No app/server,broker,stream or permission mutation. --fixture never reads owner
configuration. --fetch requires existing SEC identification plus explicit source
processing gates;failure never falls back to synthetic observations.
"""
import argparse,asyncio,json,os,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from terminal.stocks.sec_filing_ingest import IngestError

async def qualify(args,environment=None):
 from terminal.stocks.service import StockWorkspace
 from terminal.stocks.xbrl_product import company_contract
 from terminal.verification.artifacts import write_private
 from terminal.stocks import sec
 from terminal.stocks.identity import symbol
 symbol(args.symbol)
 if args.as_of is not None:sec.acceptance_ns(args.as_of)
 store=None
 if args.fixture:
  from terminal.stocks.test_sec_filing_ingest import client,ACC,CIK
  from terminal.stocks.test_xbrl_statements import LATE,ROLE
  if args.symbol!='AAPL'or args.accession is not None:raise IngestError('fixture_identity_is_authored_AAPL_only')
  coordinator,_,_=client();workspace=StockWorkspace(environment={});accession=ACC;at=args.as_of or LATE;role=args.role or ROLE
 else:
  from terminal.stocks.sec_config import resolve,enabled
  e,_=resolve(os.environ)if environment is None else(environment,{})
  if not enabled(e.get('GIG_SEC_XBRL_INGEST_ENABLED')):raise IngestError('sec_xbrl_ingestion_gate_required')
  reference=e.get('GIG_SEC_XBRL_PERMISSION_REFERENCE')
  if type(reference)is not str or not 1<=len(reference)<=256:raise IngestError('sec_xbrl_processing_reference_required')
  if args.accession is None or args.as_of is None:raise IngestError('sec_xbrl_exact_accession_and_cutoff_required')
  workspace=StockWorkspace(environment=e);workspace.permission('sec')
  from terminal.stocks.sec_read_wire import SECReadWire
  coordinator=workspace.create_sec_filing_ingestor(args.symbol,transport=SECReadWire(),enabled=True,allow_observed=True,permission_reference=reference,taxonomy_urls=args.taxonomy_url)
  accession=args.accession;at=args.as_of;role=args.role
 if args.checkpoint_root:
  from terminal.stocks.sec_ingest_store import FilingCheckpointStore
  if not args.fixture:
   from terminal.stocks.sec_config import enabled
   if not enabled(e.get('GIG_SEC_XBRL_RETENTION_APPROVED')):raise IngestError('sec_xbrl_retention_gate_required')
  store=FilingCheckpointStore(args.checkpoint_root,enabled=True,retention_approved=True)
 result=await coordinator.ingest(accession,document=args.document,store=store)
 if args.fixture:workspace.admit_xbrl_collection(args.symbol,coordinator.collection)
 else:workspace.install_sec_filing_result(args.symbol)
 view=company_contract(workspace,args.symbol,at,role=role,profile='accuracy-extension-v2')
 if args.output:write_private(args.output,view)
 return {'schema':'gig.sec.filing_ingestion.qualification.v1','status':'OFFLINE_FIXTURE_PASS'if args.fixture else'READ_ONLY_SOURCE_ACCEPTED','origin':coordinator.origin,'symbol':args.symbol,'issuer_cik':coordinator.cik,'filings':result['filings'],'requests':result['requests'],'response_bytes':result['response_bytes'],'collection_sha256':result['collection_sha256'],'statement_status':view['statement_view']['status'],'checkpoint_sha256':__import__('hashlib').sha256(coordinator.checkpoint()).hexdigest()if store else None,'provider_requested':not args.fixture,'trading_enabled':False,'contact_disclosed':False,'qualification_scope':'Bounded source admission;not full financial statements,independent source authentication or current listing/identity reconciliation'}

def main(argv=None,*,environment=None):
 parser=argparse.ArgumentParser(description=__doc__);mode=parser.add_mutually_exclusive_group(required=True);mode.add_argument('--fixture',action='store_true');mode.add_argument('--fetch',action='store_true');parser.add_argument('--symbol',default='AAPL');parser.add_argument('--accession');parser.add_argument('--document');parser.add_argument('--as-of');parser.add_argument('--role');parser.add_argument('--taxonomy-url',action='append',default=[]);parser.add_argument('--checkpoint-root');parser.add_argument('--output');args=parser.parse_args(argv)
 try:result=asyncio.run(qualify(args,environment))
 except (ValueError,TypeError,KeyError,OSError,TimeoutError,MemoryError):
  # No exception text,headers,contact,document contents or untrusted URLs printed.
  print(json.dumps({'schema':'gig.sec.filing_ingestion.qualification.v1','status':'BLOCKED_OR_INVALID','reason':'source_permission_scope_format_or_resource_failure','provider_requested':not args.fixture,'contact_disclosed':False,'trading_enabled':False}));return 2
 print(json.dumps(result,sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
