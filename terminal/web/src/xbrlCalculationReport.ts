/** Offline source-bound calculation diagnostics; no source authentication claim. */
import {verifyXbrlDigest} from './xbrlStatements.ts';import {acceptanceNanoseconds} from './acceptanceContract.ts';
type R={numerator:string;denominator:string};type I={lower:R;upper:R;lower_closed:boolean;upper_closed:boolean};
type Point={profile:string;rounding_mode:string;status:string;interval:I|null;source_fact_ids:string[];selected_reported_value:null};
type Check={status:string;parent_interval:I|null;weighted_sum_interval:I|null;residual_interval:I|null;terms:{concept:string;weight:R;source_fact_ids:string[];weighted_interval:I}[]};
type Axis={dimension:string;member:string};
type SourceDocument={uri:string;sha256:string};
type DefaultSource={member:string;role:string;arc_index:number;source_uri:string;source_sha256:string};
type Binding={aspect_sha256?:string;source_context_sha256s?:string[];parent:string;aspects:{issuer_cik:string;context_sha256?:string;unit_sha256:string;period:{kind:string;start:string|null;end:string};dimensions:Axis[];effective_dimension_values?:Axis[];unit:{numerator:string[];denominator:string[];semantic_sha256:string}};data_points:Record<string,Point>;missing_concepts:string[];calculation:Check;relationship_provenance:unknown[]};
export type CalculationPacket={schema:string;weight_profile?:string;dimensional_profile?:string;numeric_profile?:string|null;instrument:{symbol:string;cik:string|null};as_of:string;cutoff_ns:string;form_family:string;role:string|null;rounding_mode:string;collection_sha256:string;status:string;reason:string|null;read_only:true;provider_requested:false;complete_statements:false;lineage:null|{issuer_cik:string;collection_sha256:string;as_of:string;cutoff_ns:string;status:string;complete_history:false;sources:{source:{accession:string;source_sha256:string;accepted_at:string;issuer_cik:string;form:string;filed:string;amends_accession:string|null};parsed_sha256:string}[];sha256:string};report:null|{schema:string;dimensional_profile?:string;numeric_profile?:string;definition_role?:string;drs_proof_sha256?:string;definition_sha256?:string;global_default_dimensions?:Record<string,string>;default_provenance?:Record<string,DefaultSource>;definition_documents?:SourceDocument[];profile:string;sha256:string;role:string;rounding_mode:string;status:string;parsed_sha256:string;dts_sha256:string;relationships_sha256:string;source_filing:{accession:string;issuer_cik:string;source_sha256:string;accepted_at:string};bindings:Binding[];fact_provenance:Record<string,{concept:string;context_ref:string;unit_ref:string;declaration_documents:SourceDocument[];aspect_sha256?:string;source_context_sha256?:string;source_unit_sha256?:string;reported_dimensions?:Axis[];implicit_default_dimensions?:Record<string,string>;numeric_type_provenance?:{base_type:string;derivation_path:string[];documents:SourceDocument[]}}>;selected_reported_value:null};sha256:string};
function fail():never{throw Error('Invalid source-bound calculation report')}const hash=(v:unknown)=>typeof v==='string'&&/^[a-f0-9]{64}$/.test(v);const ids=(a:unknown):a is string[]=>Array.isArray(a)&&a.length<=8&&new Set(a).size===a.length&&a.every(hash);
const DIMENSIONS='INHERITED_POSITIVE_EXPLICIT_HYPERCUBES_V3';
const BOUNDS='NUMERIC_BOUND_RESTRICTIONS_V6';
const DECIMAL_WEIGHTS='SOURCE_BOUND_DECIMAL_WEIGHT_CALCULATIONS_V2';
const qname=(value:unknown):value is string=>typeof value==='string'&&/^\{[^{}]{1,512}\}[A-Za-z_][A-Za-z0-9_.-]{0,127}$/.test(value);
function defaultDimensions(report:NonNullable<CalculationPacket['report']>){
 const defaults=report.global_default_dimensions, sources=report.default_provenance, documents=report.definition_documents;
 if(!defaults||Array.isArray(defaults)||!sources||Array.isArray(sources)||!Array.isArray(documents)||!documents.length||documents.length>128||
    !hash(report.drs_proof_sha256)||!hash(report.definition_sha256)||typeof report.definition_role!=='string'||!report.definition_role)fail();
 const docHashes=new Map<string,string>();
 for(const d of documents){
  if(!d||typeof d.uri!=='string'||!d.uri||!hash(d.sha256)||docHashes.has(d.uri))fail();
  docHashes.set(d.uri,d.sha256);
 }
 const axes=Object.keys(defaults);
 if(axes.length>32||axes.length!==Object.keys(sources).length)fail();
 for(const axis of axes){
  const source=sources[axis];
  if(!qname(axis)||!qname(defaults[axis])||!source||source.member!==defaults[axis]||source.role!==report.definition_role||
     !Number.isSafeInteger(source.arc_index)||source.arc_index<0||source.arc_index>=4096||!hash(source.source_sha256)||docHashes.get(source.source_uri)!==source.source_sha256)fail();
 }
 return defaults;
}
function axisValues(axes:Axis[]){
 if(!Array.isArray(axes)||axes.length>32)fail();
 const values=new Map<string,string>();
 for(const axis of axes){
  if(!axis||!qname(axis.dimension)||!qname(axis.member)||values.has(axis.dimension))fail();
  values.set(axis.dimension,axis.member);
 }
 return values;
}
type Q=[bigint,bigint];function q(r:R):Q{if(!r||typeof r.numerator!=='string'||! /^-?[0-9]{1,512}$/.test(r.numerator)||typeof r.denominator!=='string'||!/^[0-9]{1,256}$/.test(r.denominator)||BigInt(r.denominator)<=0n)fail();return [BigInt(r.numerator),BigInt(r.denominator)]}
const cmp=(a:Q,b:Q)=>a[0]*b[1]-b[0]*a[1];const eq=(a:Q,b:Q)=>cmp(a,b)===0n;function add(a:Q,b:Q):Q{let n=a[0]*b[1]+b[0]*a[1],d=a[1]*b[1],x=n<0n?-n:n,y=d;while(y){const r=x%y;x=y;y=r}if(x){n/=x;d/=x}return[n,d]}
function lexicalWeight(value:unknown):Q{
 if(typeof value!=='string'||! /^[+-]?(?:[0-9]{1,24}(?:\.[0-9]{0,12})?|\.[0-9]{1,12})$/.test(value))fail();
 const [whole,part='']=value.replace(/^[+-]/,'').split('.');
 const numerator=BigInt((whole||'0')+part)*(value.startsWith('-')?-1n:1n);
 if(numerator===0n)fail();
 return[numerator,10n**BigInt(part.length)];
}
type Bounds=[Q,Q,boolean,boolean];function interval(i:I):Bounds{if(!i||typeof i.lower_closed!=='boolean'||typeof i.upper_closed!=='boolean')fail();const a=q(i.lower),b=q(i.upper);if(cmp(a,b)>0n||eq(a,b)&&!(i.lower_closed&&i.upper_closed))fail();return[a,b,i.lower_closed,i.upper_closed]}
function same(i:I|null,b:Bounds){if(!i)fail();const v=interval(i);if(!eq(v[0],b[0])||!eq(v[1],b[1])||v[2]!==b[2]||v[3]!==b[3])fail()}
export async function verifyCalculationPacket(raw:unknown,symbol:string,cik:string|null):Promise<CalculationPacket>{
 const pending:[unknown,number][]=[[raw,0]];let nodes=0;while(pending.length){const [v,d]=pending.pop()!;if(++nodes>40000||d>32)fail();if(typeof v==='string'&&v.length>16384)fail();if(v&&typeof v==='object')for(const x of Object.values(v))pending.push([x,d+1])}
 const p=raw as CalculationPacket;const dimensional=p?.schema==='gig.backend.company_dimensional_calculations.v1';
 const reweighted=p?.schema==='gig.backend.company_weighted_calculations.v1';
 if(!p||(!dimensional&&!reweighted&&p.schema!=='gig.backend.company_calculations.v1')||p.instrument?.symbol!==symbol||p.instrument.cik!==cik||p.read_only!==true||p.provider_requested!==false||p.complete_statements!==false||!hash(p.collection_sha256)||!['AVAILABLE','UNAVAILABLE'].includes(p.status)||!['10-K','10-Q'].includes(p.form_family)||!['round-to-nearest','truncation'].includes(p.rounding_mode)||acceptanceNanoseconds(p.as_of).toString()!==p.cutoff_ns)fail();await verifyXbrlDigest(p as unknown as Record<string,unknown>);
 if(p.weight_profile!==(reweighted?DECIMAL_WEIGHTS:undefined))fail();
 if(dimensional&&(p.dimensional_profile!==DIMENSIONS||p.numeric_profile!==null&&p.numeric_profile!==BOUNDS))fail();
 const l=p.lineage;if(l){await verifyXbrlDigest(l as unknown as Record<string,unknown>);if(l.issuer_cik!==cik||l.collection_sha256!==p.collection_sha256||l.as_of!==p.as_of||l.cutoff_ns!==p.cutoff_ns||l.complete_history!==false||!['SUPPLIED_CHAIN_RESOLVED','UNRESOLVED'].includes(l.status)||!Array.isArray(l.sources)||l.sources.length>32)fail();for(const s of l.sources)if(!hash(s.parsed_sha256)||!hash(s.source.source_sha256)||!/^[0-9]{10}-[0-9]{2}-[0-9]{6}$/.test(s.source.accession)||s.source.issuer_cik!==cik||acceptanceNanoseconds(s.source.accepted_at)>BigInt(p.cutoff_ns))fail()}
 const r=p.report;if(!r){if(p.status!=='UNAVAILABLE')fail();return p}
 await verifyXbrlDigest(r as unknown as Record<string,unknown>);if(!l||l.status!=='SUPPLIED_CHAIN_RESOLVED'||!l.sources.length||!hash(r.parsed_sha256)||!hash(r.source_filing.source_sha256)||r.role!==p.role||r.rounding_mode!==p.rounding_mode||r.status!==p.status||r.selected_reported_value!==null||!hash(r.dts_sha256)||!hash(r.relationships_sha256)||r.parsed_sha256!==l.sources[0]?.parsed_sha256||r.source_filing.accession!==l.sources[0]?.source.accession||r.source_filing.source_sha256!==l.sources[0]?.source.source_sha256||r.source_filing.issuer_cik!==cik||r.source_filing.accepted_at!==l.sources[0]?.source.accepted_at||!Array.isArray(r.bindings)||r.bindings.length>128||!r.fact_provenance||Object.keys(r.fact_provenance).length>4096)fail();
 const bounded=dimensional&&p.numeric_profile===BOUNDS;
 if(dimensional){
  if(r.dimensional_profile!==DIMENSIONS||r.numeric_profile!==(bounded?BOUNDS:undefined)||
     r.schema!==(bounded?'gig.sec.xbrl.dimensional_calculation_report.v2':'gig.sec.xbrl.dimensional_calculation_report.v1')||
     r.profile!==(bounded?'POSITIVE_EXPLICIT_DIMENSIONAL_BOUND_NUMERIC_CALCULATIONS_V2':'POSITIVE_EXPLICIT_DIMENSIONAL_CALCULATIONS_V1'))fail();
 }else if(r.schema!==(reweighted?'gig.sec.xbrl.calculation_report.v2':'gig.sec.xbrl.calculation_report.v1')||
          r.profile!==(reweighted?DECIMAL_WEIGHTS:'SOURCE_BOUND_CALCULATIONS_V1'))fail();
 const defaults=dimensional?defaultDimensions(r):null;
 const sourceKeys=new Set<string>();for(let i=0;i<l.sources.length;i++){const current=l.sources[i].source,next=l.sources[i+1]?.source;if(sourceKeys.has(current.accession)||current.form.replace(/\/A$/,'')!==p.form_family)fail();sourceKeys.add(current.accession);if(next){if(!current.form.endsWith('/A')||current.amends_accession!==next.accession||acceptanceNanoseconds(next.accepted_at)>acceptanceNanoseconds(current.accepted_at))fail()}else if(current.form.endsWith('/A')||current.amends_accession!==null)fail()}
 for(const [id,f]of Object.entries(r.fact_provenance)){if(!hash(id)||typeof f.concept!=='string'||!/^\{[^{}]{1,512}\}[A-Za-z_][A-Za-z0-9_.-]{0,127}$/.test(f.concept)||!Array.isArray(f.declaration_documents)||f.declaration_documents.length>16||!f.declaration_documents.length||f.declaration_documents.some(d=>typeof d.uri!=='string'||!hash(d.sha256)))fail()}
 for(const b of r.bindings){if(!b||typeof b.parent!=='string'||b.aspects?.issuer_cik!==cik||!hash(b.aspects.unit_sha256)||!Array.isArray(b.aspects.dimensions)||(!dimensional&&b.aspects.dimensions.length>0)||!Array.isArray(b.missing_concepts)||b.missing_concepts.length>128||!b.data_points||Object.keys(b.data_points).length>129||!Array.isArray(b.relationship_provenance)||b.relationship_provenance.length>128)fail();
  const per=b.aspects.period;const date=(v:unknown):v is string=>typeof v==='string'&&/^[0-9]{4}-[0-9]{2}-[0-9]{2}$/.test(v)&&Number(v.slice(0,4))>=1&&Number.isFinite(Date.parse(v))&&new Date(v).toISOString().startsWith(v);if(!per||!date(per.end)||!(per.kind==='instant'&&per.start===null||per.kind==='duration'&&date(per.start)&&per.start<=per.end))fail();
  const reported=axisValues(b.aspects.dimensions);
  const sourceContexts=new Set<string>();
  if(defaults){
   if(!hash(b.aspect_sha256)||b.aspects.context_sha256!==undefined||!b.aspects.effective_dimension_values)fail();
   const derived=new Map(Object.entries(defaults));
   for(const [axis,member]of reported){
    if(defaults[axis]===member)fail();
    derived.set(axis,member);
   }
   const effective=axisValues(b.aspects.effective_dimension_values);
   if(derived.size!==effective.size||[...derived].some(([axis,member])=>effective.get(axis)!==member))fail();
   await verifyXbrlDigest({...b.aspects,sha256:b.aspect_sha256});
  }else{
   if(!hash(b.aspects.context_sha256))fail();
   await verifyXbrlDigest({issuer_cik:cik,period:per,dimensions:[],opaque_segment:[],sha256:b.aspects.context_sha256});
  }
  const u=b.aspects.unit;if(!u||!Array.isArray(u.numerator)||!u.numerator.length||u.numerator.length>8||!Array.isArray(u.denominator)||u.denominator.length>8||u.semantic_sha256!==b.aspects.unit_sha256||[...u.numerator,...u.denominator].some(v=>typeof v!=='string'||!/^\{[^{}]{1,512}\}[A-Za-z_][A-Za-z0-9_.-]{0,127}$/.test(v)))fail();await verifyXbrlDigest({numerator:u.numerator,denominator:u.denominator,sha256:b.aspects.unit_sha256});
  for(const [concept,a]of Object.entries(b.data_points)){if(a.profile!=='EXACT_CALCULATION_INTERVALS_V2'||a.rounding_mode!==p.rounding_mode||a.selected_reported_value!==null||!['INTERVAL_COMPATIBLE','UNAVAILABLE','INCONSISTENT_DUPLICATES'].includes(a.status)||(a.interval!==null)!==(a.status==='INTERVAL_COMPATIBLE')||!ids(a.source_fact_ids)||!a.source_fact_ids.length||a.source_fact_ids.some(id=>r.fact_provenance[id]?.concept!==concept))fail();if(a.interval)interval(a.interval)}
  if(defaults){
   const expectedImplicit=Object.entries(defaults).filter(([axis])=>!reported.has(axis));
   for(const point of Object.values(b.data_points))for(const id of point.source_fact_ids){
    const f=r.fact_provenance[id];
    if(!f||f.aspect_sha256!==b.aspect_sha256||f.source_unit_sha256!==b.aspects.unit_sha256||
       typeof f.source_context_sha256!=='string'||!hash(f.source_context_sha256)||
       !f.reported_dimensions||!f.implicit_default_dimensions||Array.isArray(f.implicit_default_dimensions))fail();
    const sourceAxes=axisValues(f.reported_dimensions), implicit=f.implicit_default_dimensions;
    if(sourceAxes.size!==reported.size||[...sourceAxes].some(([axis,member])=>reported.get(axis)!==member)||
       Object.keys(implicit).length!==expectedImplicit.length||expectedImplicit.some(([axis,member])=>implicit[axis]!==member))fail();
    if(bounded){
     const numeric=f.numeric_type_provenance;
     if(!numeric||!qname(numeric.base_type)||!Array.isArray(numeric.derivation_path)||numeric.derivation_path.length>8||
        new Set(numeric.derivation_path).size!==numeric.derivation_path.length||!numeric.derivation_path.every(qname)||
        !Array.isArray(numeric.documents)||numeric.documents.length>16||
        Boolean(numeric.documents.length)!==Boolean(numeric.derivation_path.length)||
        new Set(numeric.documents.map(d=>d?.uri)).size!==numeric.documents.length||
        numeric.documents.some(d=>!d||typeof d.uri!=='string'||!d.uri||!hash(d.sha256)))fail();
    }
    sourceContexts.add(f.source_context_sha256);
   }
   if(!Array.isArray(b.source_context_sha256s)||!sourceContexts.size||
      JSON.stringify(b.source_context_sha256s)!==JSON.stringify([...sourceContexts].sort()))fail();
  }
  const relationshipWeights:Q[]=[];
  if(reweighted){
   for(const line of b.relationship_provenance){
    if(!Array.isArray(line)||!line.length||line.length>4096)fail();
    let weight:Q|undefined;
    for(const ref of line){
     if(!ref||typeof ref.source_uri!=='string'||!ref.source_uri||!hash(ref.source_sha256))fail();
     const candidate=lexicalWeight(ref.weight_lexical);
     if(weight&&!eq(weight,candidate))fail();
     weight=candidate;
    }
    if(!weight)fail();
    relationshipWeights.push(weight);
   }
  }
  const c=b.calculation;if(!c||!['CALCULATION_COMPATIBLE','DEFINITELY_INCONSISTENT','INCOMPLETE','UNSUPPORTED_ACCURACY'].includes(c.status)||!Array.isArray(c.terms)||c.terms.length>128)fail();
  if(['CALCULATION_COMPATIBLE','DEFINITELY_INCONSISTENT'].includes(c.status)){const parent=b.data_points[b.parent]?.interval;if(!parent||b.missing_concepts.length||reweighted&&relationshipWeights.length!==c.terms.length)fail();const a=interval(parent);same(c.parent_interval,a);let lo:Q=[0n,1n],hi:Q=[0n,1n],lc=true,uc=true;const concepts=new Set<string>();
   for(const [i,t] of c.terms.entries()){
    if(concepts.has(t.concept))fail();concepts.add(t.concept);
    const point=b.data_points[t.concept];
    if(!point?.interval||!ids(t.source_fact_ids)||JSON.stringify(t.source_fact_ids)!==JSON.stringify(point.source_fact_ids))fail();
    const v=interval(point.interval),w=q(t.weight);
    if(reweighted?!eq(w,relationshipWeights[i]):w[1]!==1n||![-1n,1n].includes(w[0]))fail();
    const scale=(a:Q):Q=>[a[0]*w[0],a[1]*w[1]];
    const weighted:Bounds=w[0]>0n?[scale(v[0]),scale(v[1]),v[2],v[3]]:[scale(v[1]),scale(v[0]),v[3],v[2]];
    same(t.weighted_interval,weighted);lo=add(lo,weighted[0]);hi=add(hi,weighted[1]);lc&&=weighted[2];uc&&=weighted[3];
   }

   same(c.weighted_sum_interval,[lo,hi,lc,uc]);same(c.residual_interval,[add(a[0],[-hi[0],hi[1]]),add(a[1],[-lo[0],lo[1]]),a[2]&&uc,a[3]&&lc]);const lower=cmp(a[0],lo)>0n?a[0]:lo,upper=cmp(a[1],hi)<0n?a[1]:hi;const closedLower=(!eq(lower,a[0])||a[2])&&(!eq(lower,lo)||lc),closedUpper=(!eq(upper,a[1])||a[3])&&(!eq(upper,hi)||uc);const compatible=cmp(lower,upper)<0n||eq(lower,upper)&&closedLower&&closedUpper;if(compatible!==(c.status==='CALCULATION_COMPATIBLE'))fail();
  }else if(c.parent_interval!==null||c.weighted_sum_interval!==null||c.residual_interval!==null)fail();
 }
 return p;
}
