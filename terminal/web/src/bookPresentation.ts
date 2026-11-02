import type {Level} from './contracts.ts';
/** Exact presentation totals only;native order priority,state and metrics are untouched. */
export function displayedLadder(levels:Level[],limit:number){
 if(!Number.isInteger(limit)||limit<1||limit>40)throw Error('Invalid displayed ladder bound');
 let cumulative=0n;
 return levels.slice(0,limit).map(level=>{
  const quantity=BigInt(level.quantity);if(quantity<0n)throw Error('Invalid displayed quantity');
  cumulative+=quantity;return {...level,cumulative:cumulative.toString()};
 });
}
