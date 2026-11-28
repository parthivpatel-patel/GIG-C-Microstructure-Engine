/** Adjacent supplied vintages. Browser contract validation is not issuer authentication. */
import {verifySourceAccounting} from './financialSourceContract.ts';
import type {SourceAccountingPacket,AccountingRow} from './financialSourceContract.ts';
import {parseBoundedOfflineJson,readBoundedOfflineJson} from './offlineJson.ts';
export const MAX_COMPARISON_BYTES=4*1024*1024;
const KINDS=['balance_sheet','income_statement','cash_flow_statement'] as const;
type Packet=SourceAccountingPacket;
type Section=Packet['accounting']['statements'][string];
type Calculation=Section['periods'][number]['calculations'][number];
type Side={entry_index:number;source_packet_sha256:string;row_sha256:string;accession:string;source_sha256:string;original_parsed_sha256:string|null;dts_sha256:string|null;status:string;reason:string|null;reported_value:string|null;unit:AccountingRow['unit'];source_facts:AccountingRow['facts'];numeric_facts:AccountingRow['numeric_facts'];equivalence_status:string;essence_concept:string|null};
export type ComparisonRow={concept:string;period:{start:string|null;end:string};status:string;reported_values_comparable:boolean;underlying_value_equality_established:false;restatement_established:false;previous:Side|null;current:Side|null;previous_calculations:Calculation[];current_calculations:Calculation[]};
type Role={presentation_role:string|null;accounting_role:string|null}|null;
type ComparisonSection={previous_status:string|null;current_status:string|null;previous_reason:string|null;current_reason:string|null;previous_role_binding:Role;current_role_binding:Role;status:string;rows:ComparisonRow[]};
type Comparison={previous_entry_index:number;current_entry_index:number;source_relation:string;restatement_established:false;statements:Record<typeof KINDS[number],ComparisonSection>};
export type StatementComparisonPacket={schema:'gig.backend.statement_vintage_comparison.v1';profile:'ORIGINAL_SOURCE_ADJACENT_VINTAGES_V1'|'ORIGINAL_SOURCE_CALCULATION_COMPATIBLE_VINTAGES_V2';instrument:Packet['instrument'];form_family:string;collection_sha256:string;entries:Packet[];comparisons:Comparison[];status:'ANALYZED_BOUNDED_SUPPLIED_VINTAGES';complete_history:false;complete_statements:false;restatements_inferred:false;values_filled:false;gaap_aliases_inferred:false;selected_reported_value:null;read_only:true;provider_requested:false;policy:string;sha256:string};
function bad():never{throw Error('Invalid adjacent original-source statement comparison')}
const order=(a:string,b:string)=>{const aa=Array.from(a,c=>c.codePointAt(0)!),bb=Array.from(b,c=>c.codePointAt(0)!);for(let i=0;i<Math.min(aa.length,bb.length);i++)if(aa[i]!==bb[i])return aa[i]-bb[i];return aa.length-bb.length};
export function comparisonCanonical(x:unknown):string{if(x===null||typeof x!=='object')return JSON.stringify(x).replace(/[\u007f-\uffff]/g,c=>'\\u'+c.charCodeAt(0).toString(16).padStart(4,'0'));if(Array.isArray(x))return '['+x.map(comparisonCanonical).join(',')+']';return '{'+Object.keys(x).sort(order).map(k=>comparisonCanonical(k)+':'+comparisonCanonical((x as Record<string,unknown>)[k])).join(',')+'}'}
const same=(a:unknown,b:unknown)=>comparisonCanonical(a)===comparisonCanonical(b);
async function digest(x:unknown){return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(comparisonCanonical(x)))),b=>b.toString(16).padStart(2,'0')).join('')}
export const parseStatementComparisonJson=(text:string)=>parseBoundedOfflineJson(text,MAX_COMPARISON_BYTES,320000,36);
export const readStatementComparisonJson=(file:Pick<Blob,'size'|'arrayBuffer'>,signal?:AbortSignal)=>readBoundedOfflineJson(file,MAX_COMPARISON_BYTES,320000,36,signal);
function rows(s:Section){const result=new Map<string,{start:string|null;end:string;row:AccountingRow}>();for(const p of s.periods)for(const row of p.rows){const key=comparisonCanonical([p.start,p.end,row.concept]);if(result.has(key))bad();result.set(key,{start:p.start,end:p.end,row})}return result}
async function side(index:number,p:Packet,row:AccountingRow|undefined):Promise<Side|null>{if(!row)return null;const source=p.accounting.source_filing;if(!source)bad();return {entry_index:index,source_packet_sha256:p.sha256,row_sha256:await digest(row),accession:source.accession,source_sha256:source.source_sha256,original_parsed_sha256:p.accounting.original_parsed_sha256,dts_sha256:p.accounting.dts_sha256,status:row.status,reason:row.reason,reported_value:row.value,unit:row.unit,source_facts:row.facts,numeric_facts:row.numeric_facts,equivalence_status:row.equivalence_status,essence_concept:row.essence_concept}}
function aspects(p:Packet,r:AccountingRow){if(!p.source)bad();return new Set(r.facts.map(f=>{const c=p.source!.contexts[f.context_ref];return comparisonCanonical({issuer_cik:c.issuer_cik,identifier_lexical:c.identifier_lexical,period:c.period,dimensions:c.dimensions,opaque_segment:c.opaque_segment})}))}
function typeIdentity(p:Packet,concept:string){const g=p.dts;if(!g)bad();const declaration=g.concepts[concept].declaration,path:unknown[]=[],seen=new Set<string>();let current=declaration.type;for(let depth=0;depth<8;depth++){
 if(!current||seen.has(current))bad();seen.add(current);
 if(/^\{http:\/\/www\.w3\.org\/2001\/XMLSchema\}(decimal|integer|nonPositiveInteger|negativeInteger|long|int|short|byte|nonNegativeInteger|unsignedLong|unsignedInt|unsignedShort|unsignedByte|positiveInteger)$/.test(current)||/^\{http:\/\/www\.xbrl\.org\/2003\/instance\}(decimal|monetary|shares|pure|integer|nonNegativeInteger|positiveInteger)ItemType$/.test(current))return {declaration,resolved_base:current,restriction_path:path};
 const d=g.type_declarations?.[current]?.declaration;if(!d||d.unsupported.length||!d.base)bad();path.push({type:current,declaration:d});current=d.base;
 }return bad()}
function relationshipIdentity(r:AccountingRow){return {essence_concept:r.essence_concept,relationships:r.accounting_relationships.map(v=>{const d=v.declaration_constraints as Record<string,unknown>;return {kind:v.kind,role:v.role,from:v.from,to:v.to,declarations:Object.fromEntries(['status','type','period_type','from_declaration','to_declaration'].map(k=>[k,d[k]]))}})}}
function calculations(s:Section,p:Packet){if(!p.source||!p.dts)bad();const contexts=p.source.contexts,parents=new Map<string,Set<string>>(),result=new Map<string,Calculation[]>();for(const n of p.dts.effective_relationships.networks)if(n.kind==='calculation'&&n.role===s.presentation_role)for(const a of n.arcs){const members=parents.get(a.from)??new Set([a.from]);members.add(a.to);parents.set(a.from,members)}
 for(const period of s.periods){const points=new Map(period.rows.map(row=>[row.concept,new Set(row.facts.map(f=>comparisonCanonical([f.context_sha256,f.unit_sha256,contexts[f.context_ref].identifier_lexical])))]));for(const row of period.rows)result.set(comparisonCanonical([period.start,period.end,row.concept]),[]);
 for(const check of period.calculations){const unsupported=check.status==='UNSUPPORTED',members=unsupported?new Set(points.keys()):parents.get(check.parent!)??new Set([check.parent!]),aspect=comparisonCanonical([check.context_sha256,check.unit_sha256,check.identifier_lexical]);for(const concept of members)if(points.has(concept)&&(unsupported||points.get(concept)!.has(aspect)))result.get(comparisonCanonical([period.start,period.end,concept]))!.push(check)}}return result}
function calculationRelationships(packet:Packet,role:string|null){
 const result=new Map<string,Set<string>>();
 for(const network of packet.dts?.effective_relationships.networks??[]){
  if(network.kind!=='calculation'||network.role!==role)continue;
  const groups=new Map<string,{child:string;weight:unknown}[]>();
  for(const arc of network.arcs){
   if(!arc.weight)bad();
   const terms=groups.get(arc.from)??[];
   terms.push({child:arc.to,weight:arc.weight});groups.set(arc.from,terms);
  }
  for(const [parent,terms]of groups){
   terms.sort((a,b)=>order(a.child,b.child));
   const fingerprint=comparisonCanonical({parent,terms,usable:network.usable,issues:[...network.issues].sort()});
   for(const concept of new Set([parent,...terms.map(t=>t.child)])){
    const relationships=result.get(concept)??new Set<string>();
    relationships.add(fingerprint);result.set(concept,relationships);
   }
  }
 }
 return result;
}
function numeric(v:string|null){if(v===null||! /^[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)$/.test(v))bad();const negative=v.startsWith('-'),[a,b='']=v.replace(/^[+-]/,'').split('.');return [BigInt((a||'0')+b)*(negative?-1n:1n),10n**BigInt(b.length)] as const}
function classify(old:Packet,next:Packet,a:AccountingRow|undefined,b:AccountingRow|undefined,roles:boolean,ac:Calculation[],bc:Calculation[],matchingCalculations:boolean):[string,boolean]{
 if(!roles)return ['ROLE_BINDING_CHANGED',false];if(!a)return ['ROW_NOT_IN_PREVIOUS_VIEW',false];if(!b)return ['ROW_NOT_IN_CURRENT_VIEW',false];const states=[a.status,b.status];
 for(const [state,status]of [['CONFLICTING','CONFLICTING_SOURCE_ROW'],['UNSUPPORTED','UNSUPPORTED_SOURCE_ROW']])if(states.includes(state))return [status,false];
 if(states.every(v=>v==='MISSING'))return ['BOTH_SOURCE_ROWS_MISSING',false];if(a.status==='MISSING')return ['PREVIOUS_SOURCE_ROW_MISSING',false];if(b.status==='MISSING')return ['CURRENT_SOURCE_ROW_MISSING',false];if(!states.every(v=>v==='SUPPORTED'))bad();
 const aa=aspects(old,a),bb=aspects(next,b);if(aa.size!==1||bb.size!==1)return ['AMBIGUOUS_SOURCE_ASPECTS',false];if([...aa][0]!==[...bb][0])return ['INCOMPATIBLE_SOURCE_CONTEXT',false];if(!same(a.unit,b.unit))return ['INCOMPATIBLE_SOURCE_UNIT',false];if(!same(typeIdentity(old,a.concept),typeIdentity(next,b.concept)))return ['SOURCE_DECLARATION_CHANGED',false];if(!same(relationshipIdentity(a),relationshipIdentity(b)))return ['ACCOUNTING_RELATIONSHIP_CHANGED',false];if([a,b].some(r=>['CONFLICTING_REPORTED_VALUES','UNSUPPORTED_ASPECTS','AMBIGUOUS_SOURCE_RELATIONSHIPS'].includes(r.equivalence_status)))return ['INCOMPATIBLE_ACCOUNTING_RELATIONSHIP',false];if([a,b].some(r=>r.accounting_relationships.some(v=>v.checks.some(c=>c.status==='REQUIRED_ELEMENT_MISSING'))))return ['ACCOUNTING_REQUIREMENT_UNSATISFIED',false];if([...ac,...bc].some(c=>c.calculation?.status==='DEFINITELY_INCONSISTENT'))return ['CALCULATION_INCONSISTENT',false];if(!matchingCalculations)return ['CALCULATION_RELATIONSHIP_CHANGED',false];const x=numeric(a.value),y=numeric(b.value);return [x[0]*y[1]===y[0]*x[1]?'REPORTED_NUMERIC_VALUE_UNCHANGED':'REPORTED_NUMERIC_VALUE_CHANGED',true];
}
function sourceRelation(a:Packet,b:Packet){if(!a.source||!b.source)return 'SELECTED_ORIGINAL_SOURCE_UNAVAILABLE';const before=a.accounting.source_filing!.accession,after=b.accounting.source_filing!.accession;if(before===after)return 'SAME_SELECTED_FILING';const l=b.accounting.lineage;return l?.status==='SUPPLIED_CHAIN_RESOLVED'&&l.sources.slice(1).some(s=>s.source.accession===before)?'EXPLICIT_SUPPLIED_AMENDMENT_CHAIN':'INDEPENDENT_SELECTED_FILINGS'}
const role=(s:Section|undefined):Role=>s?{presentation_role:s.presentation_role,accounting_role:s.accounting_role}:null;
export async function verifyStatementComparison(raw:unknown,symbol:string,cik:string|null):Promise<StatementComparisonPacket>{
 // Bound direct object callers before canonicalization, then re-enter the strict lexical reader.
 const pending:[unknown,number][]=[[raw,0]];let nodes=0;while(pending.length){const [v,d]=pending.pop()!;if(++nodes>320000||d>36)bad();if(typeof v==='string'&&v.length>16384)bad();if(typeof v==='number'&&(!Number.isSafeInteger(v)||Object.is(v,-0)))bad();if(v&&typeof v==='object'){if(!Array.isArray(v)&&Object.getPrototypeOf(v)!==Object.prototype)bad();for(const w of Object.values(v))pending.push([w,d+1])}else if(v!==null&&!['string','number','boolean'].includes(typeof v))bad()}
 const p=parseStatementComparisonJson(comparisonCanonical(raw)) as StatementComparisonPacket;
 if(p.schema!=='gig.backend.statement_vintage_comparison.v1'||!['ORIGINAL_SOURCE_ADJACENT_VINTAGES_V1','ORIGINAL_SOURCE_CALCULATION_COMPATIBLE_VINTAGES_V2'].includes(p.profile)||p.instrument?.symbol!==symbol||!cik||p.instrument.cik!==cik||!['10-K','10-Q'].includes(p.form_family)||!Array.isArray(p.entries)||p.entries.length<1||p.entries.length>8||!Array.isArray(p.comparisons)||p.comparisons.length!==p.entries.length-1)bad();
 const entries:Packet[]=[];for(const value of p.entries){const packet=await verifySourceAccounting(value,symbol,cik);if(packet.collection_sha256!==p.collection_sha256||packet.accounting.form_family!==p.form_family||entries.length&&BigInt(packet.cutoff_ns)<=BigInt(entries.at(-1)!.cutoff_ns))bad();entries.push(packet)}
 const comparisons:Comparison[]=[];let count=0;
 for(let index=0;index<entries.length-1;index++){const a=entries[index],b=entries[index+1],sections={} as Comparison['statements'];for(const kind of KINDS){const before=a.accounting.statements[kind],after=b.accounting.statements[kind],section:ComparisonSection={previous_status:before?.status??null,current_status:after?.status??null,previous_reason:before?before.reason:a.reason,current_reason:after?after.reason:b.reason,previous_role_binding:role(before),current_role_binding:role(after),status:'UNAVAILABLE_ADJACENT_VIEW',rows:[]};
 if(before&&after&&before.status==='AVAILABLE'&&after.status==='AVAILABLE'){section.status='ANALYZED_SOURCE_ROWS';const left=rows(before),right=rows(after),ac=calculations(before,a),bc=calculations(after,b),keys=[...new Set([...left.keys(),...right.keys()])].sort((x,y)=>{const xx=left.get(x)??right.get(x)!,yy=left.get(y)??right.get(y)!;return order(yy.end,xx.end)||order(yy.start??'',xx.start??'')||order(yy.row.concept,xx.row.concept)});
 const strict=p.profile==='ORIGINAL_SOURCE_CALCULATION_COMPATIBLE_VINTAGES_V2';
 const previousRelationships=strict?calculationRelationships(a,before.presentation_role):null;
 const currentRelationships=strict?calculationRelationships(b,after.presentation_role):null;
 for(const key of keys){if(++count>4096)bad();const l=left.get(key),r=right.get(key),point=l??r!,lc=ac.get(key)??[],rc=bc.get(key)??[];
 const concept=point.row.concept;
 const compatible=!strict||same([...(previousRelationships?.get(concept)??[])].sort(),[...(currentRelationships?.get(concept)??[])].sort());
 const [status,comparable]=classify(a,b,l?.row,r?.row,same(section.previous_role_binding,section.current_role_binding),lc,rc,compatible);section.rows.push({concept:point.row.concept,period:{start:point.start,end:point.end},status,reported_values_comparable:comparable,underlying_value_equality_established:false,restatement_established:false,previous:await side(index,a,l?.row),current:await side(index+1,b,r?.row),previous_calculations:lc,current_calculations:rc})}}
 sections[kind]=section}comparisons.push({previous_entry_index:index,current_entry_index:index+1,source_relation:sourceRelation(a,b),restatement_established:false,statements:sections})}
 if(!same(p.comparisons,comparisons))bad();
 const expected={schema:'gig.backend.statement_vintage_comparison.v1',profile:'ORIGINAL_SOURCE_ADJACENT_VINTAGES_V1',instrument:entries[0].instrument,form_family:p.form_family,collection_sha256:entries[0].collection_sha256,entries,comparisons,status:'ANALYZED_BOUNDED_SUPPLIED_VINTAGES',complete_history:false,complete_statements:false,restatements_inferred:false,values_filled:false,gaap_aliases_inferred:false,selected_reported_value:null,read_only:true,provider_requested:false,policy:'Adjacent exact supplied acceptance cutoffs;exact source concepts and compatible original aspects only;reported-number comparison is not restatement or rounding-based equality'};
 if(!same(p,{...expected,sha256:await digest(expected)}))bad();return p;
}
