"""No-server Python→TypeScript contract check using authored protocol packets only."""
import json,pathlib,socket,subprocess,tempfile,sys
ROOT=pathlib.Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
def forbidden(*_a,**_k):raise AssertionError('application_or_network_forbidden')
socket.socket.bind=forbidden;socket.socket.connect=forbidden;socket.socket.connect_ex=forbidden
from terminal.server import app
app.create_app=forbidden
from terminal.stocks.test_final import client,ready,packet,quote
c=client();ready(c);c.state='SUBSCRIBED';stamp=quote()['t']
c.process(packet({'T':'t','S':'AAPL','t':stamp,'p':100.,'s':2,'i':7,'x':'V','z':'C','c':[]}))
c.process(packet({'T':'c','S':'AAPL','t':stamp,'oi':7,'ci':8,'op':100.,'cp':101.,'os':2,'cs':1,'x':'V','z':'C','oc':[],'cc':[]}))
corrected=c.view();assert corrected['trade_reconciliation']['AAPL']['corrected_size_sum']=={'numerator':'1','denominator':'1'}
c.process(packet({'T':'x','S':'AAPL','t':stamp,'i':8,'p':101.,'s':1,'a':'C','x':'V','z':'C'}))
canceled=c.view();assert canceled['trade_reconciliation']['AAPL']['active_count']==0
module=(ROOT/'terminal/web/src/marketContract.ts').as_uri()
code="""import fs from 'node:fs';import assert from 'node:assert/strict';
const {validateMarketState}=await import(process.argv[2]);
const samples=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));
for(const s of samples)assert.equal(validateMarketState(s),s);
assert.equal(samples[0].trade_reconciliation.AAPL.trades[0].trade_id,'8');
assert.equal(samples[1].trade_reconciliation.AAPL.corrected_size_sum.numerator,'0');
const bad=structuredClone(samples[0]);bad.trade_reconciliation.AAPL.trades[0].lineage_receipts=[1,99];assert.throws(()=>validateMarketState(bad));
bad.trade_reconciliation.AAPL.complete_tape=true;assert.throws(()=>validateMarketState(bad));
console.log(JSON.stringify({schema:'gig.trade.cross_language.v1',passed:6,failed:0,scope:'Authored packets,actual normalized view,TypeScript admission;no application or provider'}));
"""
with tempfile.TemporaryDirectory(prefix='gig-trade-contract-')as directory:
 fixture=pathlib.Path(directory)/'authored.json';fixture.write_text(json.dumps([corrected,canceled]))
 script=pathlib.Path(directory)/'check.mjs';script.write_text(code)
 subprocess.run(['node','--experimental-strip-types',str(script),module,str(fixture)],cwd=ROOT,check=True,timeout=30)
