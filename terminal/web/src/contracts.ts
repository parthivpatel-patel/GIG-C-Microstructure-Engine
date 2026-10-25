export type Origin='LIVE_OBSERVED'|'LIVE_DELAYED'|'HISTORICAL_OBSERVED'|'HISTORICAL_SYNTHETIC'|'SIMULATED'|'ESTIMATED'|'UNAVAILABLE';
export type Mode='HISTORICAL_REPLAY'|'SIMULATION'|'LIVE';
export interface Fraction {numerator:string;denominator:string}
export interface Level {price_ticks:string;quantity:string}
export interface TerminalState {
 schema_version:'1';mode:Mode;origin:Origin;instrument:string;provider:string;venue?:string;price_scale:string;
 book:{bids:Level[];asks:Level[]};metrics:{spread:Fraction|null;midprice:Fraction|null;microprice:Fraction|null;imbalance:Fraction|null;[key:string]:unknown};
 position:number;event_count:number;playing:boolean;speed:number;feed:{state:string;reason?:string;[key:string]:unknown};
 provenance:Record<string,unknown>;source_timestamp_ns?:string|null;replay_time_ns?:string|null;received_at_ns?:string|null;
 capabilities?:Record<string,unknown>;engine?:Record<string,unknown>;diagnostics?:Record<string,unknown>;[key:string]:unknown;
}
const unsigned=/^(0|[1-9][0-9]{0,38})$(?![\s\S])/;
const signed=/^(0|-?[1-9][0-9]{0,38})$(?![\s\S])/;
function isRecord(x:unknown):x is Record<string,unknown>{return typeof x==='object'&&x!==null&&!Array.isArray(x)}
export function validateState(value:unknown):TerminalState {
 if(!isRecord(value)||value.schema_version!=='1'||!['HISTORICAL_REPLAY','SIMULATION','LIVE'].includes(String(value.mode))||!['LIVE_OBSERVED','LIVE_DELAYED','HISTORICAL_OBSERVED','HISTORICAL_SYNTHETIC','SIMULATED','ESTIMATED','UNAVAILABLE'].includes(String(value.origin)))throw new Error('Unsupported state schema or provenance');
 if((value.mode==='LIVE'&&!['LIVE_OBSERVED','LIVE_DELAYED','UNAVAILABLE'].includes(String(value.origin)))||(value.mode==='SIMULATION'&&!['SIMULATED','UNAVAILABLE'].includes(String(value.origin)))||(value.mode==='HISTORICAL_REPLAY'&&!['HISTORICAL_SYNTHETIC','HISTORICAL_OBSERVED','UNAVAILABLE'].includes(String(value.origin))))throw new Error('Mode and provenance disagree');
 for(const key of ['instrument','provider','price_scale'])if(typeof value[key]!=='string')throw new Error(`Invalid ${key}`);
 if(!unsigned.test(value.price_scale as string)||BigInt(value.price_scale as string)===0n)throw new Error('Invalid price scale');
 if(!isRecord(value.book)||!isRecord(value.metrics)||!isRecord(value.feed)||typeof value.feed.state!=='string'||!isRecord(value.provenance))throw new Error('Incomplete state');
 for(const side of ['bids','asks']){const levels=value.book[side];if(!Array.isArray(levels)||levels.length>256)throw new Error('Unbounded book');for(const l of levels)if(!isRecord(l)||typeof l.price_ticks!=='string'||typeof l.quantity!=='string'||!signed.test(l.price_ticks)||BigInt(l.price_ticks)<=0n||!unsigned.test(l.quantity)||BigInt(l.quantity)===0n)throw new Error('Inexact book value')}
 for(const k of ['spread','midprice','microprice','imbalance']){const f=value.metrics[k];if(f!==null&&(!isRecord(f)||typeof f.numerator!=='string'||typeof f.denominator!=='string'||!signed.test(f.numerator)||!unsigned.test(f.denominator)||BigInt(f.denominator)===0n))throw new Error('Inexact metric')}
 if(!Number.isSafeInteger(value.position)||!Number.isSafeInteger(value.event_count)||Number(value.position)<0||Number(value.event_count)<0||Number(value.position)>Number(value.event_count)||typeof value.playing!=='boolean'||typeof value.speed!=='number'||!Number.isFinite(value.speed))throw new Error('Invalid replay clock');
 return value as unknown as TerminalState;
}

// Observed export needs a separate rights decision; replay mode alone cannot grant it.
export function syntheticExportAllowed(origin:unknown):boolean{return origin==='HISTORICAL_SYNTHETIC'||origin==='SIMULATED'}
