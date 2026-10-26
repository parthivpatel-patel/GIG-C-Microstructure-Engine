export type SecFacts={status:string;reason?:string;received_at?:string;freshness?:string;last_refresh_error?:string|null;financials?:{history:Record<string,unknown[]>}};
export function secState(config:{ready?:boolean;last_error?:string|null},facts:SecFacts,refresh?:{status:string}){
 const reported=Object.values(facts.financials?.history||{}).some(rows=>Array.isArray(rows)&&rows.length>0);
 if(!config.ready)return {state:'BLOCKED',reported};
 if(refresh?.status==='ERROR'||facts.last_refresh_error||config.last_error)return {state:'ERROR',reported};
 if(facts.freshness==='STALE_CACHE')return {state:'STALE',reported};
 if(refresh?.status==='RUNNING')return {state:'LOADING',reported};
 if(facts.status==='PARTIAL')return {state:'PARTIAL',reported};
 if(!reported)return {state:'UNAVAILABLE',reported};
 return {state:facts.status==='PARTIAL'?'PARTIAL':'REPORTED',reported};
}
