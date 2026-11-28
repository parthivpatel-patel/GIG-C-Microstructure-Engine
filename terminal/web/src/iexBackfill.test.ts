import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';
import test from 'node:test';
import {backfillCandidates,backfillHistory} from './iexBackfill.ts';

const fixture=JSON.parse(execFileSync(process.env.GIG_TEST_PYTHON||'python3',['-c',`
import asyncio,json,socket
def forbidden(*args,**kwargs):raise AssertionError('NO_NETWORK')
socket.socket.bind=socket.socket.connect=socket.socket.connect_ex=forbidden
from terminal.stocks.test_iex_backfill import observations,historical,FixtureWire,response
from terminal.stocks.iex_backfill import gaps,backfill
live=observations(); gap,=gaps(live)
wire=FixtureWire(lambda *_:response({'quotes':{'AAPL':[{'t':gap['start'],'bp':100,'ap':101,'bs':4,'as':5}]}}))
packet=asyncio.run(backfill(live,historical(wire),gap['gap_id'],1))
print(json.dumps({'candidates':{'schema':'gig.iex.backfill_candidates.v1','gaps':[gap]},'packet':packet}))
`],{cwd:fileURLToPath(new URL('../../../',import.meta.url)),encoding:'utf8',timeout:10000}));
const gap=fixture.packet.gap;

test('admits actual Python gap and historical records for the same retained generation',()=>{
 const [candidate]=backfillCandidates(fixture.candidates,gap.capture,gap.generation);
 const result=backfillHistory(fixture.packet,candidate,1);
 assert.equal(result.records[0].bid,'100');
 assert.equal(result.origin,'HISTORICAL_SYNTHETIC');
});

test('rejects stale capture, changed origin, boundary overlap and live promotion',()=>{
 assert.throws(()=>backfillCandidates(fixture.candidates,gap.capture,gap.generation+1));
 for(const mutate of [
  (p:typeof fixture.packet)=>{p.gap.current_receipt++;},
  (p:typeof fixture.packet)=>{p.history.origin='OBSERVED_OFFICIAL_RESPONSE';},
  (p:typeof fixture.packet)=>{p.history.records[0].timestamp=gap.end;},
  (p:typeof fixture.packet)=>{p.merged_into_live=true;},
 ]){
  const packet=structuredClone(fixture.packet);mutate(packet);
  assert.throws(()=>backfillHistory(packet,gap,1));
 }
});

test('retired capture may have overlapping receipt numbers without relabeling the current capture',()=>{
 const retired={...gap,previous_capture:'a'.repeat(32),previous_receipt:gap.current_receipt};
 const candidates={...fixture.candidates,gaps:[retired]};
 assert.deepEqual(backfillCandidates(candidates,gap.capture,gap.generation),[retired]);
 assert.throws(()=>backfillCandidates({...candidates,gaps:[{...retired,previous_capture:gap.capture}]},gap.capture,gap.generation));
 assert.throws(()=>backfillHistory({...fixture.packet,gap:retired},gap,1));
});
