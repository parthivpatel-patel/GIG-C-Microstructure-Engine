/** Admission for retained filing research; no ratio calculation or PIT completeness inference. */
export type AcceptedFact={concept:string;source_fact_id:string;value:string;unit:string;end:string;start:string|null;accession:string;form:string;filed:string;accepted_at:string};
export type AcceptanceResult={schema:string;admission_profile:string;instrument:{symbol:string};data_origin:string;as_of:string;cutoff_ns:string;completeness:string;retained_history_truncated:boolean;selection_sha256:string;exclusions:Record<string,number>;history:Record<string,AcceptedFact[]>;filing_lineage:{admission_profile:string;matched_filings:{accession:string;form:string;filed:string;accepted_at:string;report_date:string|null}[];superseded_source_fact_ids:string[];original_response_received_at:null;authority:string;policy:string}};
const object=(v:unknown):v is Record<string,unknown>=>v!==null&&typeof v==='object'&&!Array.isArray(v);
const hash=(v:unknown)=>typeof v==='string'&&/^[a-f0-9]{64}$/.test(v);
const date=(s:unknown)=>typeof s==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(s)&&Number.isFinite(Date.parse(s))&&new Date(s).toISOString().startsWith(s);
const accession=(s:unknown)=>typeof s==='string'&&/^\d{10}-\d{2}-\d{6}$/.test(s);
export function acceptanceNanoseconds(value:unknown):bigint{
 if(typeof value!=='string'||value.length>40)throw Error('Invalid acceptance clock');
 const m=/^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(\d{1,9}))?(Z|[+-]\d{2}:\d{2})$/.exec(value);
 if(!m||!date(m[1].slice(0,10))||m[1].slice(11,13)>'23'||m[1].slice(14,16)>'59'||m[1].slice(17,19)>'59')throw Error('Invalid acceptance clock');
 const ms=Date.parse(m[1]+m[3]);if(!Number.isSafeInteger(ms))throw Error('Invalid acceptance clock');
 return BigInt(ms)*1000000n+BigInt((m[2]||'').padEnd(9,'0'));
}
export function validateAcceptance(raw:unknown,symbol:string,cutoff:string):AcceptanceResult{
 const r=raw as AcceptanceResult,limit=acceptanceNanoseconds(cutoff);
 if(!object(r)||r.schema!=='gig.financial.acceptance.v1'||r.admission_profile!=='STRICT_FILING_METADATA_V1'||r.instrument?.symbol!==symbol||r.as_of!==cutoff||r.cutoff_ns!==String(limit)||r.completeness!=='PARTIAL_RETAINED_CACHE_NOT_AUTHENTICATED_SOURCE_VINTAGE'||typeof r.retained_history_truncated!=='boolean'||typeof r.data_origin!=='string'||r.data_origin.length>64||!hash(r.selection_sha256)||!object(r.history)||Object.keys(r.history).length>32||!object(r.exclusions)||Object.keys(r.exclusions).length>16||Object.values(r.exclusions).some(n=>!Number.isSafeInteger(n)||n<0||n>100000))throw Error('Invalid retained acceptance contract');
 const lineage=r.filing_lineage;
 if(!object(lineage)||lineage.admission_profile!==r.admission_profile||lineage.original_response_received_at!==null||typeof lineage.authority!=='string'||lineage.authority.length>512||typeof lineage.policy!=='string'||lineage.policy.length>512||!Array.isArray(lineage.matched_filings)||lineage.matched_filings.length>1024||!Array.isArray(lineage.superseded_source_fact_ids)||lineage.superseded_source_fact_ids.length>8192||!lineage.superseded_source_fact_ids.every(hash))throw Error('Invalid retained filing lineage');
 const filings=new Map<string,typeof lineage.matched_filings[number]>();
 for(const f of lineage.matched_filings){if(!object(f)||!accession(f.accession)||filings.has(f.accession)||typeof f.form!=='string'||f.form.length>32||!date(f.filed)||f.report_date!==null&&!date(f.report_date)||acceptanceNanoseconds(f.accepted_at)>limit)throw Error('Invalid retained filing');filings.set(f.accession,f)}
 const used=new Set<string>();
 for(const [metric,rows]of Object.entries(r.history)){
  if(metric.length>64||!Array.isArray(rows)||rows.length>256)throw Error('Retained fact budget');
  for(const f of rows){
   if(!object(f)||typeof f.concept!=='string'||f.concept.length>160||!hash(f.source_fact_id)||typeof f.value!=='string'||f.value.length>64||! /^-?\d+(?:\.\d+)?(?:[eE][+-]?\d{1,3})?$/.test(f.value)||typeof f.unit!=='string'||f.unit.length>32||!date(f.end)||f.start!==null&&!date(f.start)||!date(f.filed))throw Error('Invalid retained fact');
   const match=filings.get(f.accession);if(!match||f.form!==match.form||f.filed!==match.filed||f.accepted_at!==match.accepted_at||acceptanceNanoseconds(f.accepted_at)>limit)throw Error('Retained fact filing mismatch');
   used.add(f.accession);
  }
 }
 if(used.size!==filings.size)throw Error('Unbound retained filing lineage');
 return r;
}
