import {historyNanoseconds} from './historicalMarket.ts';
import {historicalCore} from './historicalResearch.ts';

type Gap = {
 gap_id:string; symbol:string; kind:'quotes'|'trades'; start:string; end:string;
 capture:string; generation:number; origin:string; previous_capture?:string; previous_receipt:number; current_receipt:number;
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
     !count(gap.previous_receipt)||!count(gap.current_receipt)||
     (gap.previous_capture===undefined?gap.previous_receipt>=gap.current_receipt:
      !/^[a-f0-9]{32}$/.test(gap.previous_capture)||gap.previous_capture===capture))reject();
  const span=historyNanoseconds(gap.end)-historyNanoseconds(gap.start);
  if(span<=0n||span>172800000000000n)reject();
  seen.add(gap.gap_id);
 }
 return value.gaps;
}

type Continuation={after_revision:string|null;next_revision:string|null;pages_seen:number;page_limit:number};
const revision=(value:unknown):value is string=>typeof value==='string'&&/^[a-f0-9]{64}$/.test(value);
export function backfillPage(raw:unknown,expected:Gap,maxPages:number,after:string|null=null,seenPages=0){
 const value=raw as {schema:string;gap:Gap;history:unknown;coverage:string;observation_loss:string;merged_into_live:boolean;continuation?:Continuation};
 if(value?.schema!=='gig.iex.backfill.v1'||value.merged_into_live!==false||
    value.observation_loss!=='UNKNOWN_NO_EXCHANGE_SEQUENCE'||!value.gap||value.gap.previous_capture!==expected.previous_capture||
    (Object.keys(expected) as (keyof Gap)[]).some(key=>value.gap[key]!==expected[key]))reject();
 const {symbol,kind,start,end}=expected;
 const history=historicalCore(value.history,{symbol,kind,start,end,feed:'iex',adjustment:'raw',timeframe:'1Day',max_pages:maxPages});
 if(history.origin!==expected.origin||history.source_records.length>maxPages||
    value.coverage!==(history.has_more?'BOUNDED_PREFIX':'SOURCE_RESPONSE_EXHAUSTED'))reject();
 const continuation=value.continuation;
 if(continuation!==undefined){
  if(!continuation||Object.keys(continuation).sort().join(',')!=='after_revision,next_revision,page_limit,pages_seen'||
     continuation.after_revision!==after||continuation.page_limit!==32||
     continuation.pages_seen!==seenPages+history.source_records.length||!count(continuation.pages_seen)||continuation.pages_seen>32||
     (history.has_more&&continuation.pages_seen<32
       ?!revision(continuation.next_revision)||continuation.next_revision!==history.canonical_sha256||continuation.next_revision===after
       :continuation.next_revision!==null))reject();
 }else if(after!==null)reject();
 return {history,continuation};
}
export function backfillHistory(raw:unknown,expected:Gap,maxPages:number){
 return backfillPage(raw,expected,maxPages).history;
}
