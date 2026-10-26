/** Shared capture ordinal coordinate;never independently stretch each stock's time axis. */
export function captureOffset(receipt:number,first:number,last:number):number {
 if(![receipt,first,last].every(Number.isSafeInteger)||first<0||last<first||receipt<first||receipt>last)throw Error('Invalid capture window');
 return last===first?.5:(receipt-first)/(last-first);
}

/** Historical generations stay diagnostic at the API,not in the current stream plot. */
export function currentGeneration<T extends {generation:number}>(rows:T[],generation:number):T[]{return rows.filter(r=>r.generation===generation)}
