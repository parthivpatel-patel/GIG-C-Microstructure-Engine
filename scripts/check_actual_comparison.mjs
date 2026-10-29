/** Same-host stdin only;no network or files of provider rows. Output counts/hash only. */
import {createHash} from 'node:crypto';import {alignedComparison,validateHistory} from '../terminal/web/src/historicalMarket.ts';
try{
 let input='';for await(const chunk of process.stdin){input+=chunk;if(Buffer.byteLength(input)>524288)throw Error('comparison_input_budget')}
 const {histories,expected}=JSON.parse(input);
 if(!Array.isArray(histories)||histories.length<2||histories.length>4||!expected||!Array.isArray(expected.timestamps)||!Array.isArray(expected.series))throw Error('comparison_profile');
 const checked=histories.map(h=>validateHistory(h,h.symbol,'bars')),actual=alignedComparison(checked);
 if(JSON.stringify(actual.timestamps)!==JSON.stringify(expected.timestamps)||actual.series.length!==expected.series.length)throw Error('comparison_timestamp_or_series_mismatch');
 for(let i=0;i<actual.series.length;i++){const a=actual.series[i],e=expected.series[i];if(a.symbol!==e.symbol||a.values.length!==e.values.length)throw Error('comparison_identity');for(let j=0;j<a.values.length;j++){const reference=Number(e.values[j].numerator)/Number(e.values[j].denominator);if(!Number.isFinite(reference)||!Number.isFinite(a.values[j])||Math.abs(a.values[j]-reference)>Math.max(1,Math.abs(reference))*1e-10)throw Error('comparison_numerical_mismatch')}}
 console.log(JSON.stringify({status:'PASS',series:actual.series.length,shared_timestamps:actual.timestamps.length,reference_sha256:createHash('sha256').update(JSON.stringify(expected)).digest('hex'),scope:'Python Fraction reference vs actual frontend binary64 display calculation;no total-return,session-close or coverage claim',origin:checked.every(h=>h.origin==='OBSERVED_OFFICIAL_RESPONSE')?'OBSERVED_OFFICIAL_RESPONSE':'FIXTURE_NOT_PROVIDER_QUALIFICATION'}));
}catch{console.log(JSON.stringify({status:'REJECTED',reason:'bounded_comparison_contract_or_independent_reference_disagreement'}));process.exitCode=1}
