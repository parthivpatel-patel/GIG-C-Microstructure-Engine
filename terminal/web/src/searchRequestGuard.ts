/** Admission lifetime for the global directory search. No transport or source semantics. */
export type SearchContext={query:string;revision:number;selectionRevision:number};
export function createSearchRequestGuard(initialQuery:string){
 let query=initialQuery,contextRevision=0,requestRevision=0,selectionRevision=0,active=true;
 function invalidate(){contextRevision++;requestRevision++;selectionRevision++}
 function matchesContext(context:SearchContext){return active&&context.query===query&&context.revision===contextRevision}
 return {
  context:():SearchContext=>({query,revision:contextRevision,selectionRevision}),
  matchesContext,
  matchesSelectionContext:(context:SearchContext)=>matchesContext(context)&&context.selectionRevision===selectionRevision,
  changeQuery(next:string){query=next;invalidate()},
  invalidate,
  close(){active=false;requestRevision++},
  activate(){if(!active){active=true;requestRevision++}},
  begin(context:SearchContext){
   if(!matchesContext(context))return null;
   selectionRevision++;
   const requestedQuery=context.query,requestedContext=context.revision,request=++requestRevision;
   return {query:requestedQuery,isCurrent:()=>active&&query===requestedQuery&&contextRevision===requestedContext&&requestRevision===request};
  }
 };
}
export async function runSearchRequest<T>(gate:ReturnType<typeof createSearchRequestGuard>,context:SearchContext,load:(query:string)=>Promise<T>,admit:(value:T)=>void,reject:(error:unknown)=>void):Promise<void>{
 const ticket=gate.begin(context);if(!ticket)return;
 try{const value=await load(ticket.query);if(ticket.isCurrent())admit(value)}
 catch(error){if(ticket.isCurrent())reject(error)}
}

/** A rendered option cannot select after a query, request replacement or unmount. */
export function runSearchSelection(gate:ReturnType<typeof createSearchRequestGuard>,context:SearchContext,symbol:string,select:(symbol:string)=>void):void{
 if(gate.matchesSelectionContext(context))select(symbol);
}
