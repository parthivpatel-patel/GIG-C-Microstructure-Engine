/** Keyboard admission for the local search popup; no data request or selection inference. */
export type SearchKey = {key:string;altKey?:boolean;ctrlKey?:boolean;metaKey?:boolean;shiftKey?:boolean;isComposing?:boolean};
export type SearchAction = {kind:'none'}|{kind:'move';index:number}|{kind:'select';index:number}|{kind:'dismiss'};
export function searchKeyboard(event:SearchKey,count:number,active:number):SearchAction{
 if(event.isComposing||event.altKey||event.ctrlKey||event.metaKey||event.shiftKey||!Number.isSafeInteger(count)||count<=0)return {kind:'none'};
 const current=Number.isInteger(active)&&active>=0&&active<count?active:-1;
 if(event.key==='ArrowDown')return {kind:'move',index:current<0?0:(current+1)%count};
 if(event.key==='ArrowUp')return {kind:'move',index:current<0?count-1:(current+count-1)%count};
 if(event.key==='Enter'&&current>=0)return {kind:'select',index:current};
 if(event.key==='Escape')return {kind:'dismiss'};
 return {kind:'none'};
}
export function searchResultId(prefix:string,index:number):string{return `${prefix}-option-${index}`}

export type SearchCursor={signature:string;index:number};
export function searchSignature(query:string,results:{symbol:string;company_name:string}[]):string{return JSON.stringify([query,results])}
export function activeSearchIndex(cursor:SearchCursor,signature:string,count:number):number{
 return cursor.signature===signature&&Number.isInteger(cursor.index)&&cursor.index>=0&&cursor.index<count?cursor.index:-1;
}
