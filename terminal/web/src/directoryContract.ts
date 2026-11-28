export type Security={symbol:string;name:string;exchange:string;cik?:string|null;identity_kind?:string;security_type?:string;listing_status?:string;aliases?:Record<string,string>};
export type Page={schema:string;results:Security[];matches:number;catalog_count:number;source:{authority:string;source_classifications?:string[];received_at?:string;coverage?:string};next_offset:number|null;available_filters?:Record<string,string[]>;filter_options_truncated?:boolean};
export type SECIntegrity={input_rows:number;accepted_rows:number;excluded_rows:number;coverage:'ACCEPTED_ROUTABLE_SUBSET'|'ALL_SOURCE_ROWS_REPRESENTABLE'};
type DirectoryReconciliation={
 schema:'gig.market.directory_reconciliation.v1';
 snapshot_sha256:string;
 previous_snapshot_sha256:string|null;
 status:'FIRST_COMPARABLE_SNAPSHOT'|'SAME_SOURCE_REVISION'|'COMPARED_SOURCE_REVISIONS';
 added:number;no_longer_reported:number;changed:number;unchanged:number;
 alias_matches?:{count:number;same_security_established:false;examples:{
  previous_symbol:string;current_symbol:string;exchange:string;shared_aliases:{field:string;alias:string}[];
 }[]};
 example_symbols:Record<'added'|'no_longer_reported'|'changed',string[]>;
};
export type DirectoryStatus={approved:boolean;catalog_count:number;actual_official_count:number;status:string;last_success:string|null;last_error:string|null;reconciliation?:DirectoryReconciliation;sec_ready?:boolean;sec_identity_count?:number;sec_identity_source?:{integrity?:SECIntegrity}|null;sec_reference_status?:string;asset_reference?:{ready:boolean;status:string;accepted_count:number;observed_provider_count:number;source?:{received_at?:string}|null}};
export function validatePage(x:unknown):Page{const p=x as Page;if(!p||p.schema!=='gig.security.discovery.v2'||!Array.isArray(p.results)||p.results.length>20||!Number.isSafeInteger(p.catalog_count)||p.catalog_count<0||p.catalog_count>150000||!Number.isSafeInteger(p.matches)||p.matches<0||p.matches>p.catalog_count||typeof p.source?.authority!=='string'||p.next_offset!==null&&(!Number.isSafeInteger(p.next_offset)||p.next_offset<0||p.next_offset>150000)||p.results.some(r=>!r||typeof r.symbol!=='string'||! /^[A-Z][A-Z0-9]{0,9}(?:[.-][A-Z0-9]{1,3})?$/.test(r.symbol)||typeof r.name!=='string'||typeof r.exchange!=='string'||r.cik!=null&&(typeof r.cik!=='string'||! /^[0-9]{10}$/.test(r.cik))))throw Error('Directory response rejected');if(p.available_filters!==undefined&&(typeof p.available_filters!=='object'||p.available_filters===null||Object.entries(p.available_filters).some(([k,v])=>!['exchange','security_type','listing_status'].includes(k)||!Array.isArray(v)||v.length>64||v.some(s=>typeof s!=='string'||s.length>64))))throw Error('Directory filters rejected');return p}

export function validateDirectoryStatus(x:unknown):DirectoryStatus{const s=x as DirectoryStatus;if(!s||typeof s.approved!=='boolean'||s.sec_ready!==undefined&&typeof s.sec_ready!=='boolean'||s.sec_identity_count!==undefined&&(!Number.isSafeInteger(s.sec_identity_count)||s.sec_identity_count<0||s.sec_identity_count>50000)||!Number.isSafeInteger(s.catalog_count)||!Number.isSafeInteger(s.actual_official_count)||s.actual_official_count<0||s.catalog_count<s.actual_official_count||typeof s.status!=='string'||s.last_success!==null&&(typeof s.last_success!=='string'||!Number.isFinite(Date.parse(s.last_success))))throw Error('Invalid directory status');const a=s.asset_reference;if(a&&(typeof a.ready!=='boolean'||!Number.isSafeInteger(a.accepted_count)||a.accepted_count<0||a.accepted_count>50000||!Number.isSafeInteger(a.observed_provider_count)||a.observed_provider_count<0||a.observed_provider_count>a.accepted_count))throw Error('Invalid asset reference status');const i=s.sec_identity_source?.integrity;if(i!==undefined&&(!i||[i.input_rows,i.accepted_rows,i.excluded_rows].some(n=>!Number.isSafeInteger(n)||n<0||n>50000)||i.accepted_rows<1||i.input_rows!==i.accepted_rows+i.excluded_rows||i.accepted_rows!==s.sec_identity_count||i.coverage!==(i.excluded_rows?'ACCEPTED_ROUTABLE_SUBSET':'ALL_SOURCE_ROWS_REPRESENTABLE')))throw Error('Invalid SEC reference accounting');if(s.reconciliation!==undefined)validateReconciliation(s.reconciliation,s.catalog_count);return s}

function validateReconciliation(r:DirectoryReconciliation,catalogCount:number){
 const digest=(v:unknown)=>typeof v==='string'&&/^[a-f0-9]{64}$/.test(v);
 const symbols=(v:unknown)=>Array.isArray(v)&&v.length<=20&&new Set(v).size===v.length&&
   v.every(s=>typeof s==='string'&&/^[A-Z][A-Z0-9]{0,9}(?:[.-][A-Z0-9]{1,3})?$/.test(s));
 if(!r||r.schema!=='gig.market.directory_reconciliation.v1'||!digest(r.snapshot_sha256)||
    ![r.added,r.no_longer_reported,r.changed,r.unchanged].every(n=>Number.isSafeInteger(n)&&n>=0&&n<=100000)||
    !r.example_symbols||!['FIRST_COMPARABLE_SNAPSHOT','SAME_SOURCE_REVISION','COMPARED_SOURCE_REVISIONS'].includes(r.status))throw Error('Invalid listing reconciliation');
 for(const change of ['added','no_longer_reported','changed'] as const){
  const examples=r.example_symbols[change];
  if(!symbols(examples)||examples.length!==Math.min(r[change],20))throw Error('Invalid listing reconciliation examples');
 }
 if(r.alias_matches!==undefined){
  const a=r.alias_matches;
  if(!a||r.status!=='COMPARED_SOURCE_REVISIONS'||a.same_security_established!==false||
     !Number.isSafeInteger(a.count)||a.count<0||a.count>Math.min(r.added,r.no_longer_reported)||
     !Array.isArray(a.examples)||a.examples.length!==Math.min(a.count,20)||
     a.examples.some(pair=>!pair||!symbols([pair.previous_symbol,pair.current_symbol])||
      typeof pair.exchange!=='string'||!pair.exchange||pair.exchange.length>64||
      !Array.isArray(pair.shared_aliases)||!pair.shared_aliases.length||pair.shared_aliases.length>2||
      pair.shared_aliases.some(item=>!item||!['CQS Symbol','NASDAQ Symbol'].includes(item.field)||
       typeof item.alias!=='string'||!/^[A-Z][A-Z0-9._+/^-]{0,31}$/.test(item.alias))))throw Error('Invalid listing alias evidence');
  if(new Set(a.examples.map(p=>p.previous_symbol)).size!==a.examples.length||
     new Set(a.examples.map(p=>p.current_symbol)).size!==a.examples.length)throw Error('Ambiguous listing alias evidence');
 }
 if(r.status==='FIRST_COMPARABLE_SNAPSHOT'){
  if(r.previous_snapshot_sha256!==null||r.added||r.no_longer_reported||r.changed||r.unchanged)throw Error('Invalid first listing revision');
 }else if(!digest(r.previous_snapshot_sha256)||r.added+r.changed+r.unchanged!==catalogCount||
    (r.status==='SAME_SOURCE_REVISION')!==(r.previous_snapshot_sha256===r.snapshot_sha256)||
    r.status==='SAME_SOURCE_REVISION'&&(r.added||r.no_longer_reported||r.changed))throw Error('Invalid listing revision comparison');
}
