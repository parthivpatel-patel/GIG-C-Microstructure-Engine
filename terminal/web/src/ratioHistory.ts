import {metricNames,validateDescriptor} from './financial.ts';import type {Descriptor,Period} from './financial';
export type HistoryPoint=Descriptor&{requested_period:{start:string|null;end:string}};
export type RatioPacket={schema:string;data_origin:string;instrument:{symbol:string};period_filter:Period;metrics:Record<string,HistoryPoint[]>;availability:string;limitations:string[];observed_at:string|null;as_of_filing_date:string|null;source_records:{component:string;url:string;sha256:string}[]};
export function validateRatioHistory(raw:unknown,symbol:string,period:Period):RatioPacket{
 const date=(v:unknown):v is string=>typeof v==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(v)&&Number.isFinite(Date.parse(v))&&new Date(v).toISOString().slice(0,10)===v;
 const v=raw as RatioPacket;if(!v||!['UNAVAILABLE','HISTORICAL_SYNTHETIC','OBSERVED_OFFICIAL_RESPONSE'].includes(v.data_origin)||v.schema!=='gig.financial_history.v1'||v.instrument?.symbol!==symbol||v.period_filter!==period||v.availability!=='RETAINED_RESTATED_SNAPSHOT_NOT_POINT_IN_TIME'||!Array.isArray(v.limitations)||!v.metrics||Object.keys(v.metrics).length!==12||!Array.isArray(v.source_records)||v.source_records.length>8)throw Error('Invalid reported ratio history');
 if(v.observed_at!==null&&(typeof v.observed_at!=='string'||!Number.isFinite(Date.parse(v.observed_at))))throw Error('Invalid history receipt');
 if(v.source_records.some(r=>!r||typeof r.component!=='string'||typeof r.url!=='string'||!/^https:\/\/data\.sec\.gov\//.test(r.url)||! /^[a-f0-9]{64}$/.test(r.sha256)))throw Error('Invalid history provenance');
 for(const name of metricNames){const points=v.metrics[name];if(!Array.isArray(points)||points.length>12)throw Error('Unbounded ratio history');const seen=new Set<string>();for(const p of points){validateDescriptor(p);const key=p.requested_period;if(!key||!date(key.end)||(key.start!==null&&(!date(key.start)||key.start>key.end)))throw Error('Invalid history anchor');const id=key.start+'|'+key.end;if(seen.has(id))throw Error('Duplicate history period');seen.add(id);if(p.status==='AVAILABLE'&&!p.period)throw Error('Missing available ratio period');if(p.period&&p.period.duration_days!==(key.start===null?null:(Date.parse(key.end)-Date.parse(key.start))/86400000+1))throw Error('Invalid reported duration');if(p.period&&(p.period.start!==key.start||p.period.end!==key.end))throw Error('Ratio history period mismatch');if(p.unit!==(name==='free_cash_flow'?'USD':'ratio'))throw Error('Ratio history unit mismatch')}}return v;
}
/** Display projection only;never calculate a financial descriptor or connect missing periods. */
export function ratioSeries(points:HistoryPoint[]):{point:HistoryPoint;value:number}[]{
 points=[...points].sort((a,b)=>a.requested_period.end.localeCompare(b.requested_period.end));
 while(points.length&&points[0].status!=='AVAILABLE')points.shift();while(points.length&&points.at(-1)!.status!=='AVAILABLE')points.pop();
 if(points.length<2||points.some(p=>p.status!=='AVAILABLE'||!p.value||!p.period))return [];
 if(new Set(points.map(p=>p.period!.end)).size!==points.length||new Set(points.map(p=>p.unit+'|'+p.formula)).size!==1)return [];
 const days=points.map(p=>p.period!.duration_days);if(days.some(d=>d===null)!==days.every(d=>d===null))return [];
 const durations=days.filter((d):d is number=>d!==null);if(durations.length&&Math.max(...durations)-Math.min(...durations)>35)return [];
 const result=points.map(point=>({point,value:Number(point.value!.numerator)/Number(point.value!.denominator)}));return result.some(r=>!Number.isFinite(r.value))?[]:result.sort((a,b)=>a.point.period!.end.localeCompare(b.point.period!.end));
}
