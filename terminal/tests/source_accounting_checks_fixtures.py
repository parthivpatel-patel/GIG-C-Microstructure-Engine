"""Offline original-byte accounting-check edge cases for the TypeScript verifier."""
import hashlib,json,socket,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
def forbidden(*args,**kwargs):raise AssertionError('NO_APPLICATION_OR_NETWORK')
socket.socket.bind=forbidden;socket.socket.connect=forbidden;socket.socket.connect_ex=forbidden
from terminal.stocks.test_xbrl_accounting_statements import recipe,prepared,LATE
from terminal.stocks.test_xbrl_dts import document
from terminal.stocks.xbrl_accounting_relationships import REQUIRES
from terminal.stocks.financial_intelligence_product import company_source_accounting

def fixtures():
 entries=[]
 entries.append(('nil',recipe(alias=None,extra='<ext:IssuerProfit contextRef="FD" unitRef="USD" xsi:nil="true"/>')))
 entries.append(('duplicate',recipe(extra='<ext:IssuerProfit contextRef="FD" unitRef="USD" decimals="0">99</ext:IssuerProfit>')))
 entries.append(('decimal_lexical',recipe(alias='+00100.00',income='100.0',exact=True)))
 entries.append(('signed_zero',recipe(alias='-0.00',income='+0',exact=True)))
 e=recipe();e['raw']=e['raw'].replace(b'<x:period><x:startDate>2023-01-01',b'<x:segment><d:explicitMember dimension="ext:Region">ext:North</d:explicitMember></x:segment><x:period><x:startDate>2023-01-01');entries.append(('dimensional',e))
 e=recipe();raw=e['raw'];start=raw.index(b'<x:context id="FD">');end=raw.index(b'</x:context>',start)+len(b'</x:context>');other=raw[start:end].replace(b'id="FD"',b'id="FD2"').replace(b'>0000320193<',b'>320193<');e['raw']=raw.replace(b'</x:xbrl>',other+b'</x:xbrl>').replace(b'<ext:IssuerProfit contextRef="FD"',b'<ext:IssuerProfit contextRef="FD2"');entries.append(('identifier',e))
 e=recipe();e['raw']=e['raw'].replace(b'</x:xbrl>',b'<x:unit id="EUR"><x:measure>iso:EUR</x:measure></x:unit></x:xbrl>').replace(b'<ext:IssuerProfit contextRef="FD" unitRef="USD"',b'<ext:IssuerProfit contextRef="FD" unitRef="EUR"');entries.append(('units',e))
 for name,missing in [('requires_satisfied',False),('requires_missing',True),('requires_cross_context',False),('requires_nil',False)]:
  e=recipe();d=e['documents'][-1];addition=f'<l:loc xl:type="locator" xl:label="c" xl:href="extension.xsd#CashFlowTotal"/><l:definitionArc xl:type="arc" xl:arcrole="{REQUIRES}" xl:from="b" xl:to="c"/></l:definitionLink>';e['documents'][-1]=document('accounting.xml',d['raw'].replace(b'</l:definitionLink>',addition.encode()))
  if missing:e['raw']=e['raw'].replace(b'<ext:CashFlowTotal contextRef="FD" unitRef="USD" decimals="0">30</ext:CashFlowTotal>',b'')
  if name=='requires_cross_context':
   raw=e['raw'];start=raw.index(b'<x:context id="FD">');end=raw.index(b'</x:context>',start)+len(b'</x:context>');other=raw[start:end].replace(b'id="FD"',b'id="FD2"').replace(b'>0000320193<',b'>320193<');e['raw']=raw.replace(b'</x:xbrl>',other+b'</x:xbrl>').replace(b'<ext:CashFlowTotal contextRef="FD"',b'<ext:CashFlowTotal contextRef="FD2"')
  if name=='requires_nil':e['raw']=e['raw'].replace(b'<ext:CashFlowTotal contextRef="FD" unitRef="USD" decimals="0">30</ext:CashFlowTotal>',b'<ext:CashFlowTotal contextRef="FD" unitRef="USD" xsi:nil="true"/>')
  entries.append((name,e))
 e=recipe(alias='same text',income='same text');e['raw']=e['raw'].replace(b'<ext:IssuerProfit contextRef="FD" unitRef="USD" decimals="0">',b'<ext:IssuerProfit contextRef="FD">').replace(b'<ext:IncomeTotal contextRef="FD" unitRef="USD" decimals="0">',b'<ext:IncomeTotal contextRef="FD">');d=e['documents'][2];e['documents'][2]=document('extension.xsd',d['raw'].replace(b'id="IncomeTotal" name="IncomeTotal" type="x:monetaryItemType"',b'id="IncomeTotal" name="IncomeTotal" type="x:stringItemType"').replace(b'id="profit" name="IssuerProfit" type="x:monetaryItemType"',b'id="profit" name="IssuerProfit" type="x:stringItemType"'));entries.append(('strings',e))
 result=[]
 for name,e in entries:
  e['manifest']['source_sha256']=hashlib.sha256(e['raw']).hexdigest();w,i,b=prepared(e);result.append([name,company_source_accounting(w,'AAPL',LATE,i,b)])
 return result
if __name__=='__main__':print(json.dumps(fixtures(),separators=(',',':')))
