"""Cross-language projection equivalence on authored production-source fixtures;offline."""
import copy,json,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from terminal.stocks.test_final import client,ready,packet,quote
from terminal.server.market_delta import MarketProjection
root=Path(__file__).resolve().parents[2];out=root/'build/continuation';out.mkdir(parents=True,exist_ok=True)
c=client();ready(c);c.symbols=('AAPL','MSFT','NVDA','TSLA')
for i in range(256):
 q=quote();q['S']=c.symbols[i%4];q['bs']=i+1;c.process(packet(q))
p=MarketProjection();frames=[];full_bytes=wire_bytes=0;started=time.perf_counter()
for i in range(40):
 if i==30:c.clock=lambda:140.
 if i==35:c.generation+=1
 if i<30:
  q=quote();q['S']=c.symbols[i%4];q['bs']=300+i;c.process(packet(q))
 full=copy.deepcopy(c.view());wire=p.project(full);frames.append({'wire':wire,'expected':full})
 if i:full_bytes+=len(json.dumps(full,separators=(',',':')).encode());wire_bytes+=len(json.dumps(wire,separators=(',',':')).encode())
fixture=out/'projection-fixture.json';fixture.write_text(json.dumps(frames))
script="""import fs from 'node:fs';import assert from 'node:assert/strict';import {MarketProjectionReader} from './terminal/web/src/marketDelta.ts';const frames=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));const r=new MarketProjectionReader();for(const f of frames){const restored={...r.accept(f.wire)};delete restored.browser_delta;assert.deepEqual(restored,f.expected)}console.log('40 cross-language full-window comparisons PASS');"""
# Module imports are resolved from repository root;never write source observations.
runner=root/'build/continuation/projection-runner.mjs';runner.write_text(script.replace("'./terminal/","'../../terminal/"))
subprocess.run(['node','--experimental-strip-types',str(runner),str(fixture)],check=True,cwd=root)
result={'classification':'AUTHORED_FOUR_SYMBOL_NOT_PROVIDER_BENCHMARK','cross_language_comparisons':40,'steady_and_resync_full_bytes':full_bytes,'projection_bytes':wire_bytes,'reduction_fraction':1-wire_bytes/full_bytes,'fixture_and_comparison_seconds':time.perf_counter()-started,'retained_rows':256,'source_observed':False}
(out/'projection-measurements.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
