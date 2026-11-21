"""Actual original-byte comparison exports for the read-only frontend consumer."""
import json,socket,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
def forbidden(*args,**kwargs):raise AssertionError('NO_APPLICATION_OR_NETWORK')
socket.socket.bind=forbidden;socket.socket.connect=forbidden;socket.socket.connect_ex=forbidden
from terminal.stocks.test_xbrl_statement_comparison import compare,recipe,amendment,raw_edit,source_doc,requires,EARLY,LATE,BEFORE
from terminal.stocks.test_xbrl_accounting_statements import prepared,A,B
from terminal.stocks.xbrl_statement_comparison import company_statement_vintage_comparison
from terminal.stocks.test_xbrl_statement_set import EXT

def fixtures():
 result=[]
 for name,new in [('changed',amendment(income='101',alias='101')),('unchanged',amendment()),('missing',amendment(alias=None)),('conflict',amendment(alias='101')),('unit',raw_edit(amendment(),b'>iso:USD<',b'>iso:EUR<')),('context',raw_edit(amendment(),b'>0000320193<',b'>320193<')),('calculation',raw_edit(amendment(),b'>30</ext:CashFlowTotal>',b'>80</ext:CashFlowTotal>'))]:result.append([name,compare(recipe(),new)])
 result.append(['unavailable',compare(cutoffs=[BEFORE,EARLY,LATE])]);result.append(['single',compare(cutoffs=[EARLY])]);result.append(['same_filing',compare(cutoffs=[EARLY,'2024-02-05T00:00:00Z'])])
 new=amendment();d=new['documents'][2];source_doc(new,2,d['raw'].replace(b'id="ExpenseReported" name="ExpenseReported"',b'id="ExpenseReported" name="ExpenseReported" x:balance="debit"'));result.append(['declaration',compare(recipe(),new)])
 new=amendment();d=new['documents'][-1];source_doc(new,len(new['documents'])-1,d['raw'].replace(b'xl:from="a" xl:to="b"',b'xl:from="b" xl:to="a"'));result.append(['relationship',compare(recipe(),new)])
 result.append(['requires',compare(requires(recipe()),raw_edit(requires(amendment()),b'<ext:CashFlowTotal contextRef="FD" unitRef="USD" decimals="0">30</ext:CashFlowTotal>',b''))])
 w,i,b=prepared(recipe(),amendment());b[B]['cash_flow_statement']['presentation_role']=None;result.append(['unavailable_role',company_statement_vintage_comparison(w,'AAPL',[EARLY,LATE],i,b)])
 w,i,b=prepared(recipe(),amendment());b[B]['income_statement']['accounting_role']=None;result.append(['changed_role',company_statement_vintage_comparison(w,'AAPL',[EARLY,LATE],i,b)])
 new=amendment();raw=new['raw'];start=raw.index(b'<x:context id="FD">');end=raw.index(b'</x:context>',start)+len(b'</x:context>');other=raw[start:end].replace(b'id="FD"',b'id="FD2"').replace(b'>0000320193<',b'>320193<');raw_edit(new,b'</x:xbrl>',other+b'<ext:ExpenseReported contextRef="FD2" unitRef="USD" decimals="0">50</ext:ExpenseReported></x:xbrl>');result.append(['ambiguous_aspects',compare(recipe(),new)])
 old=recipe();new=amendment()
 for e,maximum in [(old,'100'),(new,'200')]:
  d=e['documents'][2];declaration='<s:complexType name="ExpenseType"><s:simpleContent><s:restriction base="x:monetaryItemType"><s:maxInclusive value="'+maximum+'"/></s:restriction></s:simpleContent></s:complexType>';raw=d['raw'].replace(b'<s:schema ',('<s:schema xmlns:vintage="'+EXT+'" ').encode(),1).replace(b'id="ExpenseReported" name="ExpenseReported" type="x:monetaryItemType"',b'id="ExpenseReported" name="ExpenseReported" type="vintage:ExpenseType"').replace(b'</s:schema>',(declaration+'</s:schema>').encode());source_doc(e,2,raw)
 result.append(['type_path',compare(old,new)])
 result.append(['eight_cutoffs',compare(recipe(),cutoffs=['2024-02-01T12:00:00.00000000'+str(n)+'Z'for n in range(1,9)])])
 w,i,b=prepared(recipe(),amendment());result.append(['missing_latest_originals',company_statement_vintage_comparison(w,'AAPL',[BEFORE,EARLY,LATE],{A:i[A]},b)])
 return result
if __name__=='__main__':print(json.dumps(fixtures(),separators=(',',':')))
