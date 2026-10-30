import {test} from 'node:test';import assert from 'node:assert/strict';import {rational,price,chartRatio} from './format.ts';import {validateState,syntheticExportAllowed} from './contracts.ts';
import {researchNumber,researchFraction} from './format.ts';

test('research summaries preserve missingness,zero and negative signs with units',()=>{
 for(const value of [null,undefined,NaN,Infinity,-Infinity,'1',true])assert.equal(researchNumber(value),'Unavailable');
 assert.equal(researchNumber(0,'return'),'0%');assert.equal(researchNumber(-0,'return'),'0%');
 assert.equal(researchNumber(-.006,'return'),'≈ -0.6%');
 assert.equal(researchNumber(2e-8,'variance'),'≈ 2e-8 return²');
 assert.equal(researchNumber(-123.456,'likelihood'),'≈ -123.5 log L');
});
test('tiny and huge research values never silently become zero or overflow',()=>{
 assert.equal(researchNumber(1e-200,'return'),'≈ 1e-198%');
 assert.equal(researchNumber(1e308,'return'),'≈ 1e+310%');
 assert.equal(researchNumber(Number.MIN_VALUE),'≈ 5e-324');
 assert.equal(researchNumber(Number.MAX_VALUE),'≈ 1.798e+308');
});
test('exact ratio summaries are rounded only for display and retain input objects',()=>{
 const f={numerator:'3',denominator:'500'},copy=JSON.stringify(f);
 assert.equal(researchFraction(f,'return'),'≈ 0.6%');assert.equal(JSON.stringify(f),copy);
 assert.equal(researchFraction({numerator:'1',denominator:'3'}),'≈ 0.3333');
 assert.equal(researchFraction({numerator:'1',denominator:'1'+'0'.repeat(1000)}),'≈ 1e-1000');
 assert.equal(researchFraction({numerator:'9'+'0'.repeat(1000),denominator:'1'}),'≈ 9e+1000');
 assert.equal(researchFraction({numerator:'99999',denominator:'10000'}),'≈ 10');
});
test('malformed research ratio wire values remain unavailable',()=>{
 for(const f of [null,undefined,{numerator:'1',denominator:'0'},{numerator:'1',denominator:'-1'},
                 {numerator:'NaN',denominator:'1'},{numerator:'01',denominator:'1'},
                 {numerator:'1'.repeat(1300),denominator:'1'}])assert.equal(researchFraction(f),'Unavailable');
});
test('financial display preserves huge integers and denotes repeating fractions',()=>{assert.equal(price('900719925474099301','100'),'9007199254740993.01');assert.equal(rational({numerator:'-1',denominator:'3'}),'-0.33333333…');assert.equal(rational({numerator:'201',denominator:'2'},'100'),'1.005');assert.equal(rational(null),'—');assert.equal(chartRatio(1n,4n),.25)});
const state={schema_version:'1',mode:'HISTORICAL_REPLAY',origin:'HISTORICAL_SYNTHETIC',instrument:'SYNTH-USD',provider:'authored',price_scale:'100',book:{bids:[{price_ticks:'100',quantity:'5'}],asks:[]},metrics:{spread:null,midprice:null,microprice:null,imbalance:null},position:0,event_count:10,playing:false,speed:1,feed:{state:'DISCONNECTED'},provenance:{}};
test('wire values must remain exact strings, bounded and versioned',()=>{assert.equal(validateState(state).instrument,'SYNTH-USD');for(const override of [{schema_version:'2'},{origin:'LIVE_FAKE'},{price_scale:'0'},{position:-1},{book:{bids:[{price_ticks:1,quantity:'2'}],asks:[]}},{metrics:{...state.metrics,spread:{numerator:'1',denominator:'0'}}}])assert.throws(()=>validateState({...state,...override}));});

test('mode and source provenance cannot conflict or normalize malformed exact values',()=>{for(const override of [{price_scale:'100\n'},{mode:'LIVE'},{position:11},{book:{bids:[{price_ticks:'-0',quantity:'2'}],asks:[]}},{book:{bids:[{price_ticks:'100',quantity:'0'}],asks:[]}},{metrics:{...state.metrics,spread:{numerator:'-0',denominator:'1'}}}])assert.throws(()=>validateState({...state,...override}));});

test('historical observed replay cannot enable synthetic export',()=>{for(const origin of ['LIVE_OBSERVED','HISTORICAL_OBSERVED','LIVE_DELAYED','UNAVAILABLE',null])assert.equal(syntheticExportAllowed(origin),false);assert.equal(syntheticExportAllowed('HISTORICAL_SYNTHETIC'),true);assert.equal(syntheticExportAllowed('SIMULATED'),true)});
