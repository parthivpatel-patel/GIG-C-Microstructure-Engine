/** Explicit V2 contract. Structural extension mapping is never GAAP equivalence. */
import {validateXbrl,verifyXbrl,verifyXbrlDigest} from './xbrlStatements.ts';
import type {XbrlCompany,XbrlRow} from './xbrlStatements.ts';
import {decimalFraction} from './financial.ts';
export type Rational={numerator:string;denominator:string};
export type Interval={lower:Rational;upper:Rational;lower_closed:true;upper_closed:true};
export type RowAccuracy={profile:'CLOSED_REPORTED_ACCURACY_V1';status:'SUPPORTED'|'UNAVAILABLE';reason:string|null;source_fact_ids:string[];interval:Interval|null;facts:{source_fact_id:string;profile:string;declared_decimals:string|null;declared_precision:string|null;status:string;reason:string|null;effective_decimals:number|'INF'|null;interval:Interval|null}[]};
export type Mapping={kind:string;concept:string;accounting_metric:null;basis:string;declaration_documents:{uri:string;sha256:string}[];role:string;relationship_indices:number[];root:boolean};
export type DuplicateDiagnostic={profile:'DUPLICATE_ACCURACY_DIAGNOSTICS_V1';status:string;source_fact_ids:string[];numeric_values_equal:boolean|null;intersection_interval:Interval|null;facts:{source_fact_id:string;reported_value:string|null;interval:Interval|null}[];selection_policy:string};
export type AccuracyRow=Omit<XbrlRow,'status'>&{status:XbrlRow['status']|'REPORTED_EXTENSION';statement_mapping:Mapping;duplicate_diagnostic?:DuplicateDiagnostic|null;accuracy:RowAccuracy|null;mapping_diagnostics:string[];numeric_facts:{source_fact_id:string;concept:string;value:string|null;declared_type:string;resolved_numeric_base:string;numeric_profile:string;derived_from:string;filing_accession:string;instance_sha256:string}[]};
export type AccuracyCheck={parent?:string;status:string;issues?:string[];accuracy_validation:null|{profile:string;status:string;reason:string|null;parent_interval:Interval|null;weighted_sum_interval:Interval|null;residual_interval:Interval|null;terms:{concept:string;weight:number;source_fact_ids:string[];weighted_interval:Interval}[]};exact_diagnostic:null|{status:string;reported:Rational;weighted_sum:Rational;residual:Rational}};
export type AccuracyCompany=Omit<XbrlCompany,'schema'|'statement_view'>&{schema:'gig.backend.company_xbrl.v2';profile:'accuracy-extension-v2';statement_view:Omit<XbrlCompany['statement_view'],'schema'|'periods'>&{schema:'gig.sec.xbrl.statement_view.v2';profile:'accuracy-extension-v2';relationships:{from:string;to:string}[];mapping_policy?:string;source_contexts:Record<string,{semantic_sha256:string;period:{kind:string;start:string|null;end:string|null};dimensions:unknown[];opaque_segment:unknown[]}>;source_units:Record<string,{semantic_sha256:string;numerator:string[];denominator:string[]}>;periods:{start:string|null;end:string;kind:string;rows:AccuracyRow[];calculations:AccuracyCheck[]}[]}};
function bad():never{throw Error('Invalid accuracy/extension statement contract')}
const text=(v:unknown,n=640):v is string=>typeof v==='string'&&v.length<=n;
const hash=(v:unknown)=>typeof v==='string'&&/^[0-9a-f]{64}$/.test(v);
function rat(v:Rational){if(!v||!text(v.numerator,256)||! /^-?\d+$/.test(v.numerator)||!text(v.denominator,256)||!/^\d+$/.test(v.denominator)||BigInt(v.denominator)<=0n)bad();return [BigInt(v.numerator),BigInt(v.denominator)] as const;}
function compare(a:Rational,b:Rational){const aa=rat(a),bb=rat(b);const d=aa[0]*bb[1]-bb[0]*aa[1];return d<0n?-1:d>0n?1:0;}
function interval(v:Interval){if(!v||v.lower_closed!==true||v.upper_closed!==true||compare(v.lower,v.upper)>0)bad();}
function accuracy(a:RowAccuracy,row:AccuracyRow){
 if(!a||a.profile!=='CLOSED_REPORTED_ACCURACY_V1'||!['SUPPORTED','UNAVAILABLE'].includes(a.status)||!Array.isArray(a.facts)||a.facts.length!==row.facts.length||!Array.isArray(a.source_fact_ids)||a.source_fact_ids.length!==row.facts.length||new Set(a.source_fact_ids).size!==a.source_fact_ids.length)bad();
 const source=new Map(row.facts.map(f=>[f.source_fact_id,f]));const seen=new Set<string>();
 for(const f of a.facts){const raw=source.get(f.source_fact_id);if(!raw||seen.has(f.source_fact_id)||f.profile!==a.profile||f.declared_decimals!==(raw.decimals??null)||f.declared_precision!==(raw.precision??null)||!['EXACT','BOUNDED','UNAVAILABLE'].includes(f.status)||!a.source_fact_ids.includes(f.source_fact_id))bad();seen.add(f.source_fact_id);if(f.interval)interval(f.interval);else if(f.status!=='UNAVAILABLE')bad();}
 if(a.status==='SUPPORTED'){if(!a.interval||a.reason!==null)bad();interval(a.interval);for(const f of a.facts)if(!f.interval||compare(a.interval.lower,f.interval.lower)<0||compare(a.interval.upper,f.interval.upper)>0)bad();}else if(a.interval!==null||!text(a.reason,256))bad();
}
export function validateAccuracyXbrl(raw:unknown,symbol:string,cik:string|null):AccuracyCompany{
 const p=raw as AccuracyCompany,s=p?.statement_view;
 if(!p||p.schema!=='gig.backend.company_xbrl.v2'||p.profile!=='accuracy-extension-v2'||!s||s.schema!=='gig.sec.xbrl.statement_view.v2'||s.profile!==p.profile||!s.source_contexts||typeof s.source_contexts!=='object'||Array.isArray(s.source_contexts)||Object.keys(s.source_contexts).length>512||!s.source_units||typeof s.source_units!=='object'||Array.isArray(s.source_units)||Object.keys(s.source_units).length>128||!Array.isArray(s.periods)||s.periods.length>12)bad();
 // Reuse unchanged V1 structural admission on a detached projection. The actual
 // V2 data and raw facts remain untouched and their own hashes are verified below.
 const projected=structuredClone(p) as unknown as XbrlCompany;projected.schema='gig.backend.company_xbrl.v1';projected.statement_view.schema='gig.sec.xbrl.statement_view.v1';
 for(let i=0;i<s.periods.length;i++){
  const period=s.periods[i];if(!Array.isArray(period.rows)||period.rows.length>128||!Array.isArray(period.calculations)||period.calculations.length>128)bad();
  for(let j=0;j<period.rows.length;j++){
   const row=period.rows[j],m=row?.statement_mapping;if(!row||!m||m.concept!==row.concept||m.accounting_metric!==null||m.basis!=='SUPPLIED_DECLARATION_AND_EFFECTIVE_PRESENTATION_ONLY'||!['SUPPLIED_EXTENSION_DECLARATION','SUPPLIED_STANDARD_DECLARATION'].includes(m.kind)||m.role!==s.role||typeof m.root!=='boolean'||!Array.isArray(m.relationship_indices)||m.relationship_indices.length>4096||new Set(m.relationship_indices).size!==m.relationship_indices.length||!Array.isArray(m.declaration_documents)||m.declaration_documents.length===0||m.declaration_documents.length>16||!Array.isArray(row.mapping_diagnostics)||row.mapping_diagnostics.length>16||row.mapping_diagnostics.some(v=>!text(v,256))||!Array.isArray(row.numeric_facts)||row.numeric_facts.length>8||!Array.isArray(row.facts)||row.facts.length>8)bad();
   if((m.kind==='SUPPLIED_STANDARD_DECLARATION')!==/^\{https?:\/\/fasb\.org\/us-gaap\/[0-9]{4}\}/.test(row.concept))bad();
   for(const doc of m.declaration_documents)if(!s.source_documents.some(d=>d.uri===doc.uri&&d.sha256===doc.sha256))bad();
   for(const n of m.relationship_indices)if(!Number.isInteger(n)||!s.relationships?.[n]||s.relationships[n].to!==row.concept)bad();
   const derived=new Map(row.numeric_facts.map(f=>[f.source_fact_id,f]));if(derived.size!==row.numeric_facts.length)bad();
   const reported=['REPORTED','REPORTED_EXTENSION'].includes(row.status);if(new Set(row.facts.map(f=>f.source_fact_id)).size!==row.facts.length)bad();
   for(const f of row.facts){
    if(!f||!hash(f.source_fact_id)||f.concept!==row.concept||!text(f.lexical_value,16384)||typeof f.nil!=='boolean'||(f.value!==null&&typeof f.value!=='string'))bad();
    const d=derived.get(f.source_fact_id),context=s.source_contexts[f.context_ref];if(!context||!hash(context.semantic_sha256)||context.period?.start!==period.start||context.period?.end!==period.end||!Array.isArray(context.dimensions)||!Array.isArray(context.opaque_segment))bad();
    if(d){if(d.concept!==row.concept||d.filing_accession!==s.source_filing?.accession||d.instance_sha256!==s.selected_instance_sha256||d.numeric_profile!=='NUMERIC_SIMPLE_CONTENT_V2'||d.derived_from!=='ORIGINAL_LEXICAL_FACT_PLUS_SUPPLIED_DTS'||!text(d.declared_type)||!text(d.resolved_numeric_base)||(d.value!==null&&typeof d.value!=='string')||f.nil!==(d.value===null))bad();if(!f.nil){const a=decimalFraction(f.lexical_value),b=decimalFraction(d.value!);if(a[0]*b[1]!==b[0]*a[1])bad();}}
    if(reported){if(!d||d.value===null||context.dimensions.length||context.opaque_segment.length||!f.unit_ref||!s.source_units[f.unit_ref]||!row.unit||s.source_units[f.unit_ref].semantic_sha256!==row.unit.semantic_sha256||JSON.stringify(s.source_units[f.unit_ref].numerator)!==JSON.stringify(row.unit.numerator)||JSON.stringify(s.source_units[f.unit_ref].denominator)!==JSON.stringify(row.unit.denominator))bad();}
   }
   if(row.numeric_facts.some(d=>!row.facts.some(f=>f.source_fact_id===d.source_fact_id)))bad();
   if(row.status==='REPORTED_EXTENSION'&&m.kind!=='SUPPLIED_EXTENSION_DECLARATION'||row.status==='REPORTED'&&m.kind==='SUPPLIED_EXTENSION_DECLARATION')bad();
   if(reported){if(!row.accuracy||derived.size!==row.facts.length)bad();accuracy(row.accuracy,row);}else if(row.accuracy!==null)bad();
   const dup=row.duplicate_diagnostic;
   if(dup){if(dup.profile!=='DUPLICATE_ACCURACY_DIAGNOSTICS_V1'||!['NIL_ONLY','MIXED_NIL_CONFLICT','ACCURACY_UNAVAILABLE','NUMERICALLY_IDENTICAL','OVERLAPPING_ACCURACY_AMBIGUOUS','DISJOINT_ACCURACY_DUPLICATES'].includes(dup.status)||!Array.isArray(dup.source_fact_ids)||dup.source_fact_ids.length!==row.facts.length||new Set(dup.source_fact_ids).size!==dup.source_fact_ids.length||dup.source_fact_ids.some(id=>!row.facts.some(f=>f.source_fact_id===id))||!Array.isArray(dup.facts)||dup.facts.length!==row.facts.length||new Set(dup.facts.map(f=>f.source_fact_id)).size!==dup.facts.length||!text(dup.selection_policy))bad();
    for(const f of dup.facts){const d=derived.get(f.source_fact_id);if(!d||f.reported_value!==d.value)bad();if(f.interval)interval(f.interval);}
    if(dup.intersection_interval)interval(dup.intersection_interval);
    if(dup.status==='OVERLAPPING_ACCURACY_AMBIGUOUS'&&(!dup.intersection_interval||row.status!=='CONFLICT'||dup.numeric_values_equal!==false)||dup.status==='DISJOINT_ACCURACY_DUPLICATES'&&(dup.intersection_interval!==null||row.status!=='CONFLICT')||dup.status==='NUMERICALLY_IDENTICAL'&&dup.numeric_values_equal!==true)bad();
   }
   const target=projected.statement_view.periods[i].rows[j];if(reported){target.status='REPORTED';target.facts=target.facts.map(f=>({...f,value:derived.get(f.source_fact_id)!.value}));}else target.facts=[];
  }
  for(const c of period.calculations){
   if(!c||!['ROUNDING_COMPATIBLE','DEFINITELY_INCONSISTENT','INCOMPLETE','UNSUPPORTED_ACCURACY','UNSUPPORTED'].includes(c.status))bad();
   const a=c.accuracy_validation;if(c.status==='UNSUPPORTED'){if(a!==null)bad();continue;}
   if(!a||a.profile!=='CLOSED_REPORTED_ACCURACY_V1'||a.status!==c.status||!Array.isArray(a.terms)||a.terms.length>128)bad();
   for(const term of a.terms){if(!text(term.concept)||![-1,1].includes(term.weight)||!Array.isArray(term.source_fact_ids)||term.source_fact_ids.length>8||term.source_fact_ids.some(id=>!hash(id)))bad();interval(term.weighted_interval);}
   if(['ROUNDING_COMPATIBLE','DEFINITELY_INCONSISTENT'].includes(c.status)){if(!a.parent_interval||!a.weighted_sum_interval||!a.residual_interval||!c.exact_diagnostic)bad();interval(a.parent_interval);interval(a.weighted_sum_interval);interval(a.residual_interval);const disjoint=compare(a.parent_interval.lower,a.weighted_sum_interval.upper)>0||compare(a.parent_interval.upper,a.weighted_sum_interval.lower)<0;if(disjoint!==(c.status==='DEFINITELY_INCONSISTENT'))bad();}
   if(c.exact_diagnostic){if(!['EXACT_MATCH','EXACT_DIFFERENCE'].includes(c.exact_diagnostic.status))bad();for(const n of[c.exact_diagnostic.reported,c.exact_diagnostic.weighted_sum,c.exact_diagnostic.residual])rat(n);}
  }
  projected.statement_view.periods[i].calculations=[];
 }
 validateXbrl(projected,symbol,cik);return p;
}
export async function verifyAccuracyXbrl(raw:unknown,symbol:string,cik:string|null){const p=validateAccuracyXbrl(raw,symbol,cik);await verifyXbrlDigest(p as unknown as Record<string,unknown>);await verifyXbrlDigest(p.statement_view as unknown as Record<string,unknown>);return p;}

export async function verifyStatementProfile(raw:unknown,symbol:string,cik:string|null,expected?:string){
 const version=(raw as {schema?:string})?.schema;
 if(expected!==undefined&&(!['legacy-v1','accuracy-extension-v2'].includes(expected)||(expected==='accuracy-extension-v2')!==(version==='gig.backend.company_xbrl.v2')))throw Error('Requested XBRL profile not returned');
 return version==='gig.backend.company_xbrl.v2'?verifyAccuracyXbrl(raw,symbol,cik):verifyXbrl(raw,symbol,cik);
}
