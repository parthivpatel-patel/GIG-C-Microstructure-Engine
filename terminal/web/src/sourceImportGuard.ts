/** Local-file admission lifetime only; this module has no I/O or financial semantics. */
export type SourceImportKind='accounting'|'inline';
export function createSourceImportGuard(initialIdentity:string){
 let identity=initialIdentity;
 const revisions:Record<SourceImportKind,number>={accounting:0,inline:0};
 const pending:Partial<Record<SourceImportKind,AbortController>>={};
 function invalidate(){for(const kind of ['accounting','inline'] as const){revisions[kind]++;pending[kind]?.abort();delete pending[kind]}}
 return {
  invalidate,
  setIdentity(next:string){if(next!==identity){invalidate();identity=next}},
  begin(kind:SourceImportKind,requestIdentity:string){
   if(requestIdentity!==identity)return null;
   pending[kind]?.abort();const controller=new AbortController(),revision=++revisions[kind];pending[kind]=controller;
   return {signal:controller.signal,isCurrent:()=>identity===requestIdentity&&revisions[kind]===revision&&!controller.signal.aborted};
  }
 };
}
