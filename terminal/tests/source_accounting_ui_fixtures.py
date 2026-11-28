"""Authored original-byte products for browser-independent React consumer tests.

No app factory or source transport. Financial quantities and document receipts are
created by the actual bounded backend APIs, not handwritten browser packets.
"""
import copy,json,socket,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
def forbidden(*args,**kwargs):raise AssertionError('NO_APPLICATION_OR_NETWORK')
socket.socket.bind=forbidden;socket.socket.connect=forbidden;socket.socket.connect_ex=forbidden
from terminal.stocks.test_xbrl_accounting_statements import recipe,prepared,prepared_embedded,EARLY,LATE,A,B
from terminal.stocks.test_xbrl_dts import document
from terminal.stocks.test_inline_dts_source_audit import inputs
from terminal.stocks.xbrl_collection import FilingCollection
from terminal.stocks.inline_set import TRANSFORMATION_PROFILE
from terminal.stocks.xbrl_instance import digest
from terminal.stocks.financial_intelligence_product import company_source_accounting,company_inline_audit
from terminal.stocks.service import StockWorkspace

def fixtures():
 accounting=[]
 for name,entry in [('reported',recipe()),('exact',recipe(exact=True)),('conflicting',recipe(alias='101')),('missing',recipe(alias=None))]:
  w,i,b=prepared(entry);accounting.append([name,company_source_accounting(w,'AAPL',LATE,i,b)])
 w,i,b=prepared_embedded();accounting.append(['embedded',company_source_accounting(w,'AAPL',LATE,i,b)])
 e=recipe();d=e['documents'][2];e['documents'][2]=document('extension.xsd',d['raw'].replace(b'id="CashFlowTotal" name="CashFlowTotal" type="x:monetaryItemType"',b'id="CashFlowTotal" name="CashFlowTotal" type="x:stringItemType"'))
 w,i,b=prepared(e);accounting.append(['unsupported',company_source_accounting(w,'AAPL',LATE,i,b)])
 w,i,b=prepared(recipe(),recipe(alias=None,accession=B,form='10-K/A',filed='2024-02-10',accepted_at=LATE,amends_accession=A))
 for name,at in [('before_acceptance','2024-01-01T00:00:00Z'),('original_vintage',EARLY),('amended_vintage',LATE)]:accounting.append([name,company_source_accounting(w,'AAPL',at,i,b)])
 partial=copy.deepcopy(b);partial[B]['cash_flow_statement']['presentation_role']=None
 accounting.append(['partial',company_source_accounting(w,'AAPL',LATE,i,partial)])
 accounting.append(['no_collection',company_source_accounting(StockWorkspace(environment={}),'AAPL',LATE,{}, {})])
 inline=[]
 for name,profile,observed,intent in [('legacy',None,False,True),('transformed',TRANSFORMATION_PROFILE,False,True),('without_acquisition',None,False,False),('permission_receipts',None,True,True)]:
  p,g,docs,tax,concepts,manifest=inputs(profile=profile,observed=observed)
  c=FilingCollection('0000320193',origin='OBSERVED_OFFICIAL_RESPONSE'if observed else'HISTORICAL_SYNTHETIC',allow_observed=observed)
  c.ingest_inline_set_batch([{'documents':docs,'concepts':concepts,'taxonomy_documents':tax}],transformation_profile=profile)
  w=StockWorkspace(environment={});w.admit_xbrl_collection('AAPL',c)
  originals={p['source']['accession']:{'documents':docs,'concepts':concepts,'taxonomy_documents':tax,'transformation_profile':profile,'embedded_profile':None,'acquisition_manifest':manifest if intent else None,'expected_acquisition_manifest_sha256':digest(manifest)if intent else None}}
  inline.append([name,company_inline_audit(w,'AAPL',LATE,originals)])
  if name=='legacy':inline.append(['missing_originals',company_inline_audit(w,'AAPL',LATE,{})])
 inline.append(['no_collection',company_inline_audit(StockWorkspace(environment={}),'AAPL',LATE,{})])
 return {'accounting':accounting,'inline':inline}

if __name__=='__main__':print(json.dumps(fixtures(),separators=(',',':')))
