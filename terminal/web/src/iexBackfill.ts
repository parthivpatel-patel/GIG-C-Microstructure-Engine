import {historyNanoseconds} from './historicalMarket.ts';
import {historicalCore} from './historicalResearch.ts';

type Gap = {
 gap_id:string; symbol:string; kind:'quotes'|'trades'; start:string; end:string;
 capture:string; generation:number; origin:string; previous_receipt:number; current_receipt:number;
};
const count = (value:unknown):value is number =>
 typeof value==='number' && Number.isSafeInteger(value) && value>0;
const reject = ():never => {throw Error('Invalid IEX backfill response');};

export function backfillCandidates(raw:unknown,capture:string,generation:number):Gap[]{
 const value=raw as {schema:string;gaps:Gap[]};
 if(value?.schema!=='gig.iex.backfill_candidates.v1'||!Array.isArray(value.gaps)||value.gaps.length>8)reject();
 const seen=new Set<string>();
 for(const gap of value.gaps){
  if(!gap||typeof gap.gap_id!=='string'||!/^[a-f0-9]{64}$/.test(gap.gap_id)||seen.has(gap.gap_id)||
     gap.capture!==capture||gap.generation!==generation||!count(gap.generation)||
     typeof gap.symbol!=='string'||!/^[A-Z][A-Z0-9]{0,9}(?:[.-][A-Z0-9]{1,3})?$/.test(gap.symbol)||
     !['quotes','trades'].includes(gap.kind)||!['HISTORICAL_SYNTHETIC','OBSERVED_OFFICIAL_RESPONSE'].includes(gap.origin)||
     !count(gap.previous_receipt)||!count(gap.current_receipt)||gap.previous_receipt>=gap.current_receipt)reject();
  const span=historyNanoseconds(gap.end)-historyNanoseconds(gap.start);
  if(span<=0n||span>172800000000000n)reject();
  seen.add(gap.gap_id);
 }
 return value.gaps;
}

export function backfillHistory(raw:unknown,expected:Gap,maxPages:number){
 const value=raw as {schema:string;gap:Gap;history:unknown;coverage:string;observation_loss:string;merged_into_live:boolean};
 if(value?.schema!=='gig.iex.backfill.v1'||value.merged_into_live!==false||
    value.observation_loss!=='UNKNOWN_NO_EXCHANGE_SEQUENCE'||!value.gap||
    (Object.keys(expected) as (keyof Gap)[]).some(key=>value.gap[key]!==expected[key]))reject();
 const {symbol,kind,start,end}=expected;
 const history=historicalCore(value.history,{symbol,kind,start,end,feed:'iex',adjustment:'raw',timeframe:'1Day',max_pages:maxPages});
 if(history.origin!==expected.origin||history.source_records.length>maxPages||
    value.coverage!==(history.has_more?'BOUNDED_PREFIX':'SOURCE_RESPONSE_EXHAUSTED'))reject();
 return history;
}
