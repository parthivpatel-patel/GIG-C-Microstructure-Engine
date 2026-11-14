/** Bounded offline vintage bundle; each child retains its own signed source view. */
import {acceptanceNanoseconds} from './acceptanceContract.ts';
import {verifyXbrlDigest} from './xbrlStatements.ts';
import {verifyAccuracyXbrl} from './xbrlAccuracy.ts';
import type {AccuracyCompany} from './xbrlAccuracy.ts';
export type VintageBundle={schema:'gig.backend.company_xbrl_vintages.v1';instrument:{symbol:string;cik:string|null};collection_sha256:string;profile:'accuracy-extension-v2';form_family:string;role:string|null;entries:{as_of:string;cutoff_ns:string;transition:string;previous_accession:string|null;packet:AccuracyCompany}[];complete_history:false;read_only:true;provider_requested:false;selection_policy:string;sha256:string};
function fail():never{throw Error('Invalid supplied statement vintages')}
export async function verifyVintages(raw:unknown,symbol:string,cik:string|null):Promise<VintageBundle>{
 const p=raw as VintageBundle;
 if(!p||p.schema!=='gig.backend.company_xbrl_vintages.v1'||p.instrument?.symbol!==symbol||p.instrument.cik!==cik||p.profile!=='accuracy-extension-v2'||!['10-K','10-Q'].includes(p.form_family)||(p.role!==null&&(typeof p.role!=='string'||p.role.length<1||p.role.length>512))||!Array.isArray(p.entries)||p.entries.length<1||p.entries.length>8||p.complete_history!==false||p.read_only!==true||p.provider_requested!==false||!/^([a-f0-9]{64})$/.test(p.collection_sha256)||p.selection_policy!=='Independent acceptance-qualified view per authored cutoff;no additive amendment or cross-filing filling')fail();
 await verifyXbrlDigest(p as unknown as Record<string,unknown>);let prior:bigint|null=null,previous:string|null=null;
 for(const e of p.entries){
  const instant=acceptanceNanoseconds(e.as_of);if(instant===null||e.cutoff_ns!==instant.toString()||(prior!==null&&instant<=prior)||e.previous_accession!==previous)fail();
  const packet=await verifyAccuracyXbrl(e.packet,symbol,cik),s=packet.statement_view;
  if(s.as_of!==e.as_of||s.cutoff_ns!==e.cutoff_ns||s.collection_sha256!==p.collection_sha256||s.form_family!==p.form_family||s.role!==p.role)fail();
  const accession=s.source_filing?.accession??null;
  const transition=s.status==='UNAVAILABLE'?'UNAVAILABLE':s.status==='AMBIGUOUS'?'AMBIGUOUS':previous===null?'FIRST_AVAILABLE':previous===accession?'UNCHANGED_SOURCE':'SOURCE_CHANGED';
  if(e.transition!==transition)fail();prior=instant;previous=accession;
 }
 return p;
}
