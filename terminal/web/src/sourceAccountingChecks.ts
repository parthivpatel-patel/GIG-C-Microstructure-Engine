/** Re-derive accounting claims from admitted original facts; this is not issuer authentication. */
import type {SourceAccountingPacket, SourceFact} from './financialSourceContract.ts';

const X='http://www.xbrl.org/2003/instance', XS='http://www.w3.org/2001/XMLSchema';
type Source=NonNullable<SourceAccountingPacket['source']>;
type Graph=NonNullable<SourceAccountingPacket['dts']>;
type RecordValue=Record<string,unknown>;
type Numeric={fixed:string;coefficient:bigint;scale:number};
type Facet={kind:string;value:string;fixed?:boolean};
function bad():never{throw Error('Invalid original-source accounting relationship checks')}
function canonical(v:unknown):string{
 if(v===null||typeof v!=='object')return JSON.stringify(v);
 if(Array.isArray(v))return '['+v.map(canonical).join(',')+']';
 return '{'+Object.keys(v).sort().map(k=>JSON.stringify(k)+':'+canonical((v as RecordValue)[k])).join(',')+'}';
}
function equal(a:unknown,b:unknown){if(canonical(a)!==canonical(b))bad()}
function numeric(lexical:string):Numeric{
 const v=lexical.replace(/^[\t\r\n ]+|[\t\r\n ]+$/g,'');
 if(v.length>64||!/^[-+]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)$/.test(v))bad();
 const negative=v.startsWith('-'),unsigned=v.replace(/^[-+]/,''),[whole,fraction='']=unsigned.split('.');
 const integer=whole.replace(/^0+/,'')||'0';
 const fixed=(negative?'-':'')+integer+(unsigned.includes('.')&&fraction.length?'.'+fraction:'');
 let coefficient=BigInt(integer+fraction)*(negative?-1n:1n),scale=fraction.length;
 while(scale&&coefficient%10n===0n){coefficient/=10n;scale--}
 return {fixed,coefficient,scale};
}
function compare(a:Numeric,b:Numeric):bigint{return a.coefficient*10n**BigInt(b.scale)-b.coefficient*10n**BigInt(a.scale)}
const integerBounds:Record<string,[bigint|null,bigint|null]>={
 integer:[null,null],nonPositiveInteger:[null,0n],negativeInteger:[null,-1n],
 long:[-(2n**63n),2n**63n-1n],int:[-(2n**31n),2n**31n-1n],short:[-32768n,32767n],byte:[-128n,127n],
 nonNegativeInteger:[0n,null],unsignedLong:[0n,2n**64n-1n],unsignedInt:[0n,2n**32n-1n],unsignedShort:[0n,65535n],unsignedByte:[0n,255n],positiveInteger:[1n,null],
};
type Resolved={base:string;kind:string;bounds:[bigint|null,bigint|null]|null;facets:Facet[][]};
function resolve(type:string|null,g:Graph):Resolved|null{
 const visited=new Set<string>(),facets:Facet[][]=[];
 for(let depth=0;depth<8;depth++){
  if(!type||visited.has(type))bad();visited.add(type);
  if(type.startsWith('{'+XS+'}')){
   const local=type.slice(XS.length+2);
   if(local==='decimal')return {base:type,kind:'decimal',bounds:null,facets};
   if(Object.hasOwn(integerBounds,local))return {base:type,kind:'integer',bounds:integerBounds[local],facets};
  }
  if(type.startsWith('{'+X+'}')){
   const local=type.slice(X.length+2);
   if(['decimalItemType','monetaryItemType','sharesItemType','pureItemType'].includes(local))return {base:type,kind:local,bounds:null,facets};
   if(['integerItemType','nonNegativeIntegerItemType','positiveIntegerItemType'].includes(local))return {base:type,kind:'integer',bounds:integerBounds[local.replace('ItemType','')],facets};
  }
  const decl=g.type_declarations?.[type]?.declaration;
  if(!decl||decl.unsupported.length||!decl.base)return null;
  if(!Array.isArray(decl.facets)||decl.facets.length>128)bad();facets.unshift(decl.facets);type=decl.base;
 }
 bad();
}
function baseNumeric(lexical:string,resolved:Resolved):Numeric{
 const value=numeric(lexical);
 if(resolved.bounds){
  if(!/^[+-]?[0-9]+$/.test(lexical.trim()))bad();
  const [lo,hi]=resolved.bounds;
  if((lo!==null&&value.coefficient<lo)||(hi!==null&&value.coefficient>hi))bad();
 }
 return value;
}
function digitLimit(facet:Facet):number{
 if(!/^[0-9]+$/.test(facet.value)||facet.value.length>4)bad();
 return Number(facet.value);
}
function checkFacets(value:Numeric,facets:Facet[][]):void{
 const unsigned=value.fixed.replace(/^[-+]/,''),[whole,fraction='']=unsigned.split('.'),trimmedFraction=fraction.replace(/0+$/,'');
 const totalDigits=Math.max(1,(whole.replace(/^0+/,'')+trimmedFraction).replace(/^0+/,'').length);
 for(const group of facets){
  const enums=group.filter(v=>v.kind==='enumeration');
  if(enums.length&&!enums.some(v=>compare(value,numeric(v.value))===0n))bad();
  for(const facet of group){
   if(facet.kind==='whiteSpace'||facet.kind==='enumeration')continue;
   if(['totalDigits','fractionDigits'].includes(facet.kind)){
    const limit=digitLimit(facet);if((facet.kind==='totalDigits'?totalDigits:trimmedFraction.length)>limit)bad();continue;
   }
   if(!['minInclusive','maxInclusive','minExclusive','maxExclusive'].includes(facet.kind))bad();
   const c=compare(value,numeric(facet.value));
   if(facet.kind==='minInclusive'&&c<0n||facet.kind==='maxInclusive'&&c>0n||facet.kind==='minExclusive'&&c<=0n||facet.kind==='maxExclusive'&&c>=0n)bad();
  }
 }
}
function checkRestrictionDefinitions(resolved:Resolved):void{
 const digits=new Map<string,number>(),fixed=new Map<string,number>();
 type Bound={value:Numeric;inclusive:boolean};
 const limits=resolved.bounds;
 let lower:Bound|undefined=limits&&limits[0]!==null?{value:numeric(String(limits[0])),inclusive:true}:undefined;
 let upper:Bound|undefined=limits&&limits[1]!==null?{value:numeric(String(limits[1])),inclusive:true}:undefined;
 if(resolved.bounds){digits.set('fractionDigits',0);fixed.set('fractionDigits',0);}
 for(const [index,group] of resolved.facets.entries()){
  const byKind=new Map(group.map(facet=>[facet.kind,facet]));
  if((byKind.has('minInclusive')&&byKind.has('minExclusive'))||
     (byKind.has('maxInclusive')&&byKind.has('maxExclusive')))bad();
  for(const key of ['totalDigits','fractionDigits']){
   const facet=byKind.get(key);
   if(!facet)continue;
   const limit=digitLimit(facet),parent=digits.get(key);
   if((fixed.has(key)&&fixed.get(key)!==limit)||(parent!==undefined&&limit>parent))bad();
   digits.set(key,limit);
   if(facet.fixed===true)fixed.set(key,limit);
  }
  if((digits.get('fractionDigits')??0)>(digits.get('totalDigits')??Infinity))bad();
  const lowerFacet=byKind.get('minInclusive')??byKind.get('minExclusive');
  const upperFacet=byKind.get('maxInclusive')??byKind.get('maxExclusive');
  function narrowed(facet:Facet,parent:Bound|undefined,minimum:boolean):Bound{
   const value=baseNumeric(facet.value,resolved),inclusive=facet.kind.endsWith('Inclusive');
   const order=parent?compare(value,parent.value):0n;
   if(parent&&((minimum?order<0n:order>0n)||order===0n&&inclusive&&!parent.inclusive))bad();
   if(!parent||inclusive||parent.inclusive||order!==0n){
    checkFacets(value,resolved.facets.slice(0,index));
   }
   return {value,inclusive};
  }
  if(lowerFacet)lower=narrowed(lowerFacet,lower,true);
  if(upperFacet)upper=narrowed(upperFacet,upper,false);
  if(lower&&upper){
   const order=compare(lower.value,upper.value);
   if(order>0n||order===0n&&!(lower.inclusive&&upper.inclusive))bad();
   if(limits&&lower.value.coefficient+(lower.inclusive?0n:1n)>upper.value.coefficient-(upper.inclusive?0n:1n))bad();
  }
  for(const facet of group)if(facet.kind==='enumeration'){
   checkFacets(baseNumeric(facet.value,resolved),resolved.facets.slice(0,index));
  }
 }
}
function checkedNumeric(f:SourceFact,s:Source,resolved:Resolved):Numeric{
 const value=baseNumeric(f.lexical_value,resolved),unit=s.units[f.unit_ref!];
 if(resolved.kind==='monetaryItemType'&&(unit.denominator.length||unit.numerator.length!==1||!/^\{http:\/\/www.xbrl.org\/2003\/iso4217\}[A-Z]{3}$/.test(unit.numerator[0])))bad();
 for(const kind of ['shares','pure'])if(resolved.kind===kind+'ItemType'&&(unit.denominator.length||unit.numerator.length!==1||unit.numerator[0]!==`{${X}}${kind}`))bad();
 checkFacets(value,resolved.facets);
 return value;
}
function member(f:SourceFact,s:Source,g:Graph):{record:RecordValue;reason:string|null;valueKey:string|null;exact:boolean}{
 const decl=g.concepts[f.concept]?.declaration,ctx=s.contexts[f.context_ref];if(!decl||!ctx||decl.abstract||ctx.period.kind!=='forever'&&ctx.period.kind!==decl.period_type)bad();
 const record:RecordValue={source_fact_id:f.source_fact_id,context_ref:f.context_ref,context_sha256:f.context_sha256,unit_ref:f.unit_ref,unit_sha256:f.unit_sha256,lexical_value:f.lexical_value,decimals:f.decimals,precision:f.precision,nil:f.nil,reported_value:null};
 if(f.nil){if(!decl.nillable)bad();return {record,reason:'NIL_PARTICIPANT',valueKey:null,exact:true}}
 if(decl.type===`{${X}}stringItemType`){
  if(f.unit_ref!==null)return {record,reason:'NONNUMERIC_UNIT_UNSUPPORTED',valueKey:null,exact:true};
  if(f.decimals!==null||f.precision!==null)return {record,reason:'NONNUMERIC_ACCURACY_ATTRIBUTES_UNSUPPORTED',valueKey:null,exact:true};
  record.reported_value=f.lexical_value;record.value_kind='string';return {record,reason:null,valueKey:'string:'+f.lexical_value,exact:true};
 }
 if(decl.type===`{${X}}dateItemType`){
  if(f.unit_ref!==null)return {record,reason:'NONNUMERIC_UNIT_UNSUPPORTED',valueKey:null,exact:true};
  if(f.decimals!==null||f.precision!==null)return {record,reason:'NONNUMERIC_ACCURACY_ATTRIBUTES_UNSUPPORTED',valueKey:null,exact:true};
  const lexical=f.lexical_value.replace(/^[\t\r\n ]+|[\t\r\n ]+$/g,'');
  const match=/^([0-9]{4}-[0-9]{2}-[0-9]{2})(Z|[+-][0-9]{2}:[0-9]{2})?$/.exec(lexical);
  const time=match?Date.parse(match[1]):NaN;
  if(!match||match[1].startsWith('0000')||!Number.isFinite(time)||new Date(time).toISOString().slice(0,10)!==match[1]){
   return {record,reason:'DATE_LEXICAL_UNSUPPORTED',valueKey:null,exact:true};
  }
  const zone=match[2];
  if(zone){
   if(zone!=='Z'){
    const hours=Number(zone.slice(1,3)),minutes=Number(zone.slice(4));
    if(hours>14||minutes>59||hours===14&&minutes!==0)return {record,reason:'DATE_LEXICAL_UNSUPPORTED',valueKey:null,exact:true};
   }
   return {record,reason:'DATE_TIMEZONE_EQUALITY_UNSUPPORTED',valueKey:null,exact:true};
  }
  record.reported_value=lexical;record.value_kind='date';
  return {record,reason:null,valueKey:'date:'+lexical,exact:true};
 }
 if(decl.type===`{${X}}booleanItemType`){
  if(f.unit_ref!==null)return {record,reason:'NONNUMERIC_UNIT_UNSUPPORTED',valueKey:null,exact:true};
  if(f.decimals!==null||f.precision!==null){
   return {record,reason:'NONNUMERIC_ACCURACY_ATTRIBUTES_UNSUPPORTED',valueKey:null,exact:true};
  }
  const lexical=f.lexical_value.replace(/^[\t\r\n ]+|[\t\r\n ]+$/g,'');
  if(!['true','false','1','0'].includes(lexical)){
   return {record,reason:'BOOLEAN_LEXICAL_UNSUPPORTED',valueKey:null,exact:true};
  }
  const value=lexical==='true'||lexical==='1'?'true':'false';
  record.reported_value=value;
  record.value_kind='boolean';
  return {record,reason:null,valueKey:'boolean:'+value,exact:true};
 }
 const resolved=resolve(decl.type,g);
 if(!resolved)return {record,reason:'ITEM_TYPE_VALUE_SEMANTICS_UNSUPPORTED',valueKey:null,exact:true};
 if(!f.unit_ref||!s.units[f.unit_ref])return {record,reason:'NUMERIC_UNIT_MISSING',valueKey:null,exact:true};
 checkRestrictionDefinitions(resolved);
 const value=checkedNumeric(f,s,resolved);record.reported_value=value.fixed;record.value_kind='numeric';
 return {record,reason:null,valueKey:`numeric:${value.coefficient}/${value.scale}`,exact:f.decimals==='INF'||f.precision==='INF'};
}
function checks(from:string,to:string,kind:string,s:Source,g:Graph):RecordValue[]{
 const left=s.facts.filter(f=>f.concept===from),right=s.facts.filter(f=>f.concept===to);
 if(kind==='requires-element')return [{status:left.length&&right.length?'SATISFIED':left.length?'REQUIRED_ELEMENT_MISSING':'NOT_TRIGGERED',source_fact_ids:[...left,...right].map(f=>f.source_fact_id),from_fact_ids:left.map(f=>f.source_fact_id),to_fact_ids:right.map(f=>f.source_fact_id),scope:'Global concept occurrence;no context,unit,value or tuple-location comparison',selected_reported_value:null}];
 if(!left.length&&!right.length)return [{status:'MISSING_COUNTERPART',reason:'NEITHER_CONCEPT_REPORTED',source_fact_ids:[],essence_facts:[],alias_facts:[],selected_reported_value:null}];
 const groups=new Map<string,{context:string;identifier:string;left:SourceFact[];right:SourceFact[]}>();
 for(const [side,facts] of [['left',left],['right',right]] as const)for(const f of facts){
  const ctx=s.contexts[f.context_ref];if(!ctx)bad();const key=JSON.stringify([ctx.semantic_sha256,ctx.identifier_lexical]);
  if(!groups.has(key))groups.set(key,{context:ctx.semantic_sha256,identifier:ctx.identifier_lexical,left:[],right:[]});groups.get(key)![side].push(f);
 }
 return [...groups.values()].sort((a,b)=>a.context<b.context?-1:a.context>b.context?1:a.identifier<b.identifier?-1:a.identifier>b.identifier?1:0).map(group=>{
  const lm=group.left.map(f=>member(f,s,g)),rm=group.right.map(f=>member(f,s,g)),members=[...lm,...rm],facts=[...group.left,...group.right],reasons=new Set<string>();
  for(const m of members)if(m.reason)reasons.add(m.reason);
  for(const f of facts){const ctx=s.contexts[f.context_ref];if(ctx.dimensions.length||ctx.opaque_segment.length||ctx.period.kind==='forever')reasons.add('DIMENSIONAL_OPAQUE_OR_FOREVER_CONTEXT_UNSUPPORTED')}
  const units=[...new Set(facts.filter(f=>f.unit_ref!==null).map(f=>{const unit=s.units[f.unit_ref!];if(!unit)bad();return unit.semantic_sha256}))].sort();
  if(units.length>1)reasons.add('UNIT_SEMANTIC_CONFLICT');
  const check:RecordValue={context_sha256:group.context,identifier_lexical:group.identifier,source_fact_ids:facts.map(f=>f.source_fact_id),essence_facts:lm.map(m=>m.record),alias_facts:rm.map(m=>m.record),selected_reported_value:null,comparison_policy:'EXACT_REPORTED_VALUES_ONLY_NOT_ROUNDING_V_EQUAL',standards_value_equality_established:false,unit_sha256s:units};
  if(reasons.size){check.status='UNSUPPORTED_ASPECTS';check.reason=[...reasons].sort().join(',')}
  else if(!lm.length||!rm.length){check.status='MISSING_COUNTERPART';check.reason=!lm.length?'ESSENCE_NOT_REPORTED':'ALIAS_NOT_REPORTED'}
  else if(new Set(members.map(m=>m.valueKey)).size!==1){check.status='CONFLICTING_REPORTED_VALUES';check.reason='DIFFERING_REPORTED_VALUES_NO_SELECTION_OR_ROUNDING_INFERENCE'}
  else{check.status='SUPPORTED_EQUAL';check.standards_value_equality_established=members.every(m=>m.exact)}
  return check;
 });
}

/** Mirror the backend's bounded numeric row admission; throws for unsupported facts. */
export function accountingNumericValue(f:SourceFact,s:Source,g:Graph):string|null{
 const d=g.concepts[f.concept]?.declaration,c=s.contexts[f.context_ref];
 if(!d||!c||d.abstract||d.substitution_group!==`{${X}}item`||c.period.kind!==d.period_type||c.period.end===null||c.dimensions.length||c.opaque_segment.length||!f.unit_ref||!s.units[f.unit_ref]||f.nil&&!d.nillable)bad();
 const resolved=resolve(d.type,g);if(!resolved)bad();checkRestrictionDefinitions(resolved);return f.nil?null:checkedNumeric(f,s,resolved).fixed;
}

/** Called after packet/source/DTS identity validation. No reported equality claim is trusted. */
export function verifyAccountingSourceChecks(packet:SourceAccountingPacket):void{
 const report=packet.accounting.accounting_report;if(!report)return;
 const s=packet.source,g=packet.dts;if(!s||!g||s.facts.length>4096||report.networks.length>64)bad();
 for(const network of report.networks){
  if(!['essence-alias','requires-element'].includes(network.kind)||network.arcrole!==`http://www.xbrl.org/2003/arcrole/${network.kind}`||network.arcs.length>4096)bad();
  for(const arc of network.arcs){
   const a=g.concepts[arc.from],b=g.concepts[arc.to];if(!a||!b||a.declaration.substitution_group!==`{${X}}item`||b.declaration.substitution_group!==`{${X}}item`)bad();
   const essence=network.kind==='essence-alias';
   if(essence&&(!a.declaration.type||a.declaration.type!==b.declaration.type||!['instant','duration'].includes(a.declaration.period_type!)||a.declaration.period_type!==b.declaration.period_type||a.declaration.balance&&b.declaration.balance&&a.declaration.balance!==b.declaration.balance))bad();
   equal(arc.declaration_constraints,{status:'SUPPORTED_DECLARATIONS',type:essence?a.declaration.type:null,period_type:essence?a.declaration.period_type:null,from_declaration:a.declaration,to_declaration:b.declaration,from_sources:a.source_documents,to_sources:b.source_documents});
   equal(arc.checks,checks(arc.from,arc.to,network.kind,s,g));
  }
 }
}
