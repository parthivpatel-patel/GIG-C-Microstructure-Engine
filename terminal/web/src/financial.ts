/** Display transforms only. Financial ratios are never recomputed here. */
export type Fact={concept:string;value:string;unit:string;start:string|null;end:string;filed:string;accession:string;form?:string;duration_days?:number|null};
export type Period='all'|'annual'|'quarter'|'ytd';
export const metricNames=['gross_margin','operating_margin','net_profit_margin','current_ratio','debt_to_equity','free_cash_flow','cash_conversion','return_on_assets','return_on_equity','annual_revenue_growth','annual_net_income_growth','annual_eps_growth'] as const;
export type Descriptor={value:{numerator:string;denominator:string}|null;status:string;reason:string|null;quality:string;unit:string;formula:string;period:{start:string|null;end:string;duration_days:number|null}|null;as_of_filing_date:string|null;timestamp:null;source:string;input_facts:unknown[];limitations:string[]};
export type CompanyV2={schema:'gig.backend.company.v2';instrument:{symbol:string};data_origin:string;observed_at:string|null;as_of_filing_date:string|null;quality:{sec_response_status:string;source_reconciliation:string};financials:{metrics:Record<string,Descriptor>};provenance:{source_records:{component:string;url:string;sha256:string;received_at?:string}[]};limitations:string[]};
export function validateCompany(x:unknown,symbol:string):CompanyV2{
 const v=x as CompanyV2;
 if(!v||v.schema!=='gig.backend.company.v2'||v.instrument?.symbol!==symbol||typeof v.data_origin!=='string'||!v.quality||typeof v.quality.source_reconciliation!=='string'||!Array.isArray(v.provenance?.source_records)||!Array.isArray(v.limitations))throw Error('Invalid v2 company contract');
 if(v.observed_at!==null&&(typeof v.observed_at!=='string'||!Number.isFinite(Date.parse(v.observed_at))))throw Error('Invalid source receipt timestamp');
 if(v.provenance.source_records.length>8||v.provenance.source_records.some(r=>typeof r.component!=='string'||typeof r.url!=='string'||!/^https:\/\/data\.sec\.gov\//.test(r.url)||! /^[a-f0-9]{64}$/.test(r.sha256)))throw Error('Invalid financial source receipt');
 if(Object.keys(v.financials?.metrics||{}).length!==metricNames.length)throw Error('Invalid financial metric coverage');
 for(const name of metricNames){const m=v.financials?.metrics?.[name];if(!m||!['AVAILABLE','UNAVAILABLE'].includes(m.status)||typeof m.formula!=='string'||typeof m.unit!=='string'||!Array.isArray(m.input_facts)||!Array.isArray(m.limitations)||typeof m.quality!=='string'||typeof m.source!=='string')throw Error('Invalid v2 financial descriptor');
  if(m.period!==null&&(!m.period||typeof m.period.end!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(m.period.end)||(m.period.start!==null&&(typeof m.period.start!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(m.period.start)))))throw Error('Invalid financial period');
  if(m.status==='AVAILABLE'){if(!m.value||typeof m.value.numerator!=='string'||typeof m.value.denominator!=='string'||!/^(-?[1-9]\d*|0)$/.test(m.value.numerator)||! /^[1-9]\d*$/.test(m.value.denominator)||m.value.numerator.length>1300||m.value.denominator.length>1300||m.reason!==null)throw Error('Invalid exact financial value');}
  else if(m.value!==null||typeof m.reason!=='string')throw Error('Missing financial value must remain unavailable');
 }return v;
}
export function inPeriod(row:Fact,period:Period):boolean{
 if(period==='all'||row.start===null)return true;
 const days=row.duration_days??(Date.parse(row.end)-Date.parse(row.start))/86400000+1;
 return period==='annual'?days>=350&&days<=380&&['10-K','10-K/A'].includes(row.form||''):period==='quarter'?days>=75&&days<=105:days>105&&days<350&&['10-Q','10-Q/A'].includes(row.form||'');
}
export function decimalFraction(value:string):[bigint,bigint]{
 if(value.length>64)throw Error('decimal budget');const m=/^(-?)(\d+)(?:\.(\d+))?(?:[eE]([+-]?\d+))?$/.exec(value);if(!m)throw Error('decimal format');const exponent=Number(m[4]||0)-(m[3]?.length||0);if(Math.abs(exponent)>192)throw Error('decimal exponent');let n=BigInt(m[2]+(m[3]||''))*(m[1]?-1n:1n);if(exponent>=0)n*=10n**BigInt(exponent);return [n,exponent<0?10n**BigInt(-exponent):1n];
}
function rounded(n:bigint,d:bigint,places=2){const negative=n<0n;if(negative)n=-n;const scale=10n**BigInt(places),v=(n*scale*2n+d)/(d*2n),whole=v/scale;return `${negative&&v?'-':''}${whole.toLocaleString('en-US')}${places?'.'+(v%scale).toString().padStart(places,'0'):''}`;}
function money(n:bigint,d:bigint){const negative=n<0n;const magnitude=negative?-n:n;for(const [size,label] of [[1000000000000n,'T'],[1000000000n,'B'],[1000000n,'M'],[1000n,'K']] as const)if(magnitude>=d*size)return (negative?'-':'')+'$'+rounded(magnitude,d*size)+label;return (negative?'-':'')+'$'+rounded(magnitude,d);}
export function financialValue(value:string|undefined,unit='USD'):string{
 if(value===undefined)return 'Unavailable';try{const [n,d]=decimalFraction(value),m=n<0n?-n:n;let divisor=1n,suffix='';for(const [size,label] of [[1000000000000n,'T'],[1000000000n,'B'],[1000000n,'M'],[1000n,'K']] as const)if(m>=d*size){divisor=size;suffix=label;break;}return (unit.startsWith('USD')?money(n,d):rounded(n,d*divisor)+suffix)+(unit==='USD/shares'?' / share':'');}catch{return 'Unavailable';}
}
export function descriptorValue(m:Descriptor,name=''):string{if(!m.value)return 'Unavailable';const n=BigInt(m.value.numerator),d=BigInt(m.value.denominator);return m.unit==='USD'?money(n,d):/margin|growth|return_on/.test(name)?rounded(n*100n,d)+'%':rounded(n,d,3)+'×';}
export function comparableHistory(rows:Fact[],period:Period):Fact[]{
 const selected=rows.filter(r=>inPeriod(r,period));const byEnd=new Map<string,Fact[]>();for(const r of selected){const key=r.end;byEnd.set(key,[...(byEnd.get(key)||[]),r]);}
 // Never silently combine annual/YTD/quarter durations or competing concepts.
 if([...byEnd.values()].some(group=>group.length!==1))return [];
 const durations=selected.filter(r=>r.start!==null).map(r=>r.duration_days??(Date.parse(r.end)-Date.parse(r.start!))/86400000+1);
 if(durations.length&&Math.max(...durations)-Math.min(...durations)>35)return [];
 if(new Set(selected.map(r=>r.unit+'|'+r.concept)).size>1)return [];
 return [...selected].sort((a,b)=>a.end.localeCompare(b.end)).slice(-12);
}

export function balancePairs(assets:Fact[],liabilities:Fact[]){
 const a=comparableHistory(assets.filter(r=>r.start===null),'all'),b=comparableHistory(liabilities.filter(r=>r.start===null),'all');
 return a.flatMap(x=>{const y=b.find(r=>r.end===x.end&&r.unit===x.unit);return y?[{assets:x,liabilities:y}]:[];}).slice(-12);
}

export type FilingRecord={form:string;filed:string;accepted_at:string|null;url:string;amendment:boolean;report_date?:string|null;accession?:string};
export type FilingPage={schema:string;instrument:{symbol:string};status:string;records:FilingRecord[];total_cached_matching:number;next_offset:number|null;observed_at:string|null};
export function validateFilings(value:unknown,symbol:string,offset:number):FilingPage{
 const p=value as FilingPage;
 if(!p||p.schema!=='gig.backend.filings.v2'||p.instrument?.symbol!==symbol||typeof p.status!=='string'||!Array.isArray(p.records)||p.records.length>50||!Number.isInteger(p.total_cached_matching)||p.total_cached_matching<0||p.total_cached_matching>1024||p.records.some(r=>!r||typeof r.form!=='string'||typeof r.filed!=='string'||typeof r.amendment!=='boolean'||typeof r.url!=='string'||!/^https:\/\/www\.sec\.gov\/Archives\//.test(r.url)))throw Error('Invalid v2 filing contract');
 if(p.observed_at!==null&&(typeof p.observed_at!=='string'||!Number.isFinite(Date.parse(p.observed_at))))throw Error('Invalid filing receipt timestamp');
 if(p.records.some(r=>(r.accepted_at!==null&&r.accepted_at!==undefined&&typeof r.accepted_at!=='string')||(r.accession!==undefined&&typeof r.accession!=='string')||(r.report_date!==null&&r.report_date!==undefined&&typeof r.report_date!=='string')))throw Error('Invalid filing record metadata');
 if(p.next_offset!==null&&(p.next_offset!==offset+p.records.length||p.records.length!==50||!Number.isInteger(p.next_offset)||p.next_offset<=offset||p.next_offset>1024||p.next_offset>=p.total_cached_matching))throw Error('Invalid filing pagination');
 if(p.records.length>Math.max(0,p.total_cached_matching-offset))throw Error('Contradictory filing count');
 return p;
}
