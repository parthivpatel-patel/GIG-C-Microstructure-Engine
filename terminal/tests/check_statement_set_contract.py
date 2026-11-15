#!/usr/bin/env python3
"""Actual three-role/history Python→TypeScript developer contract;no app/socket."""
import copy,json,socket,subprocess,sys,tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root))
def forbidden(*_a,**_k):raise AssertionError('NO_APPLICATION_OR_NETWORK_ALLOWED')
socket.socket.bind=forbidden;socket.socket.connect=forbidden;socket.socket.connect_ex=forbidden
from terminal.stocks.test_xbrl_statement_set import authored,prepared,ROLES,KINDS,A,B,EARLY,LATE
from terminal.stocks.xbrl_statement_set import company_statement_set,company_statement_history
from terminal.stocks.xbrl_product import company_contract
from terminal.stocks.xbrl_binding import bind_declarations
from terminal.stocks.xbrl_instance import digest
from terminal.stocks.xbrl_collection import FilingCollection
from terminal.stocks.xbrl_types import COMPLEX_PROFILE
from terminal.stocks.service import StockWorkspace

def expectations(w,graphs,roles):
 out={}
 for accession,parsed in w.xbrl_collections['AAPL']._filings.items():
  out[accession]={'original_parsed_sha256':parsed['canonical_sha256'],'revalidated_parsed_sha256':bind_declarations(parsed,graphs[accession])['canonical_sha256'],'dts_sha256':graphs[accession]['canonical_sha256'],'documents':graphs[accession]['documents'],'relationships_sha256':graphs[accession]['effective_relationships']['sha256'],'source':parsed['source'],'roles':roles[accession],'source_fact_ids':[f['source_fact_id']for f in parsed['facts']],'contexts':parsed['contexts'],'units':parsed['units']}
 return out

def children(w,packet):
 out={}
 for kind,descriptor in packet['statements'].items():
  if descriptor['view']is None:out[kind]=None;continue
  # Test-only adaptation of actual bare child views into the existing v2 envelope.
  # It does not add a runtime API or classify the caller's role designations.
  wrapper=company_contract(w,'AAPL',packet['as_of'],role=descriptor['role'],profile='accuracy-extension-v2');wrapper['statement_view']=copy.deepcopy(descriptor['view']);wrapper.pop('sha256');wrapper['sha256']=digest(wrapper);out[kind]=wrapper
 return out

def main():
 cases=[]
 def add(name,entries=None,*,edit_roles=None,numeric=False):
  entries=entries or[authored()];w,g,r=prepared(*entries)
  if numeric:
   c=FilingCollection('0000320193');c.ingest_dts_batch(entries,numeric_profile=COMPLEX_PROFILE);w=StockWorkspace(environment={});w.admit_xbrl_collection('AAPL',c)
  if edit_roles:edit_roles(r)
  packet=company_statement_set(w,'AAPL',LATE,g,r)
  cases.append({'name':name,'packet':packet,'children':children(w,packet),'sources':expectations(w,g,r)})
 add('three_roles');add('numeric_proof_rebound',numeric=True)
 add('conflicting_income',[authored(extra='<ext:IncomeTotal contextRef="FD" unitRef="USD" decimals="0">101</ext:IncomeTotal>')])
 def partial(r):r[A]['income_statement']=ROLES['income_statement']+'/missing';r[A]['cash_flow_statement']=None
 add('explicit_partial',edit_roles=partial)
 ctx='<x:context id="OLD"><x:entity><x:identifier scheme="http://www.sec.gov/CIK">0000320193</x:identifier></x:entity><x:period><x:startDate>2022-01-01</x:startDate><x:endDate>2022-12-31</x:endDate></x:period></x:context>'
 add('comparative_missing',[authored(extra=ctx+'<ext:RevenueReported contextRef="OLD" unitRef="USD" decimals="0">125</ext:RevenueReported>')])
 w,g,r=prepared(authored(),authored(income='99',accession=B,form='10-K/A',filed='2024-02-10',accepted_at=LATE,amends_accession=A))
 history=company_statement_history(w,'AAPL',['2024-01-01T00:00:00Z',EARLY,LATE,'2024-02-11T00:00:00Z'],g,r)
 bundle={'schema':'gig.statement_set.developer_contract_fixture.v1','sets':cases,'history':{'packet':history,'children':[children(w,e['packet'])for e in history['entries']],'sources':expectations(w,g,r)}}
 with tempfile.TemporaryDirectory()as directory:
  path=Path(directory)/'authored-statement-sets.json';path.write_text(json.dumps(bundle,sort_keys=True));assert path.stat().st_size<=2*1024*1024
  result=subprocess.run(['node','--experimental-strip-types',str(root/'terminal/tests/statement-set-contract.mjs'),str(path)],cwd=root,capture_output=True,text=True,timeout=30)
  if result.returncode:raise AssertionError(result.stderr[-5000:])
  report=json.loads(result.stdout);assert report['sets']==5 and report['history_entries']==4 and not report['application_started']and not report['provider_requested'];print(json.dumps(report,sort_keys=True))
 return 0
if __name__=='__main__':raise SystemExit(main())
