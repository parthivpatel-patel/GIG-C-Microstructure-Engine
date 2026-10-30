import type {Observation} from './LiveMarket';
export type GeometryMode='quotes'|'comparison'|'volatility'|'trades';
export type ResearchPoint={row:Observation;side:string;price:string;size:string;value:number;measure:string;lane:number};
/** Approximate visual coordinates only;original wire strings stay on every point. */
export function researchPoints(rows:Observation[],symbols:string[],mode:GeometryMode):ResearchPoint[]{
 const result:ResearchPoint[]=[];
 symbols.slice(0,4).forEach((symbol,lane)=>{let base:number|undefined;const mids:number[]=[];
  for(const row of rows.slice(-256).filter(r=>r.symbol===symbol&&!r.out_of_order)){
   if(row.kind==='trade'&&mode==='trades'){const size=Number(row.data.size),price=Number(row.data.price);if(Number.isFinite(size)&&size>0&&Number.isFinite(price)&&price>0)result.push({row,side:'trade',price:row.data.price,size:row.data.size,value:Math.log1p(size),measure:'log(1 + source trade size)',lane});continue}
   if(row.kind!=='quote'||mode==='trades')continue;const bid=Number(row.data.bid),ask=Number(row.data.ask);if(!Number.isFinite(bid)||!Number.isFinite(ask)||bid<=0||ask<bid)continue;const mid=bid+(ask-bid)/2;if(base===undefined)base=mid;mids.push(mid);
   if(mode==='quotes')for(const side of ['bid','ask'])result.push({row,side,price:row.data[side],size:row.data[side+'_size'],value:Number(row.data[side]),measure:'source price',lane});
   if(mode==='comparison'){const value=(mid/base-1)*10000;if(Number.isFinite(value))result.push({row,side:'mid',price:String(mid),size:'not applicable',value,measure:'mid change from first retained valid quote (basis points)',lane})}
   if(mode==='volatility'&&mids.length>=9){const window=mids.slice(-9);const sum=window.slice(1).reduce((n,m,i)=>n+(Math.log(m)-Math.log(window[i]))**2,0);result.push({row,side:'variation',price:String(mid),size:'not applicable',value:Math.sqrt(sum),measure:'sqrt(sum of 8 squared log-mid changes);not annualized',lane})}
  }
 });return result;
}

/** Compute each scale once per window,not once per point. */
export function researchBounds(points:ResearchPoint[],perSymbol:boolean):Map<number,[number,number]>{
 const bounds=new Map<number,[number,number]>();for(const p of points){const lane=perSymbol?p.lane:-1,old=bounds.get(lane);bounds.set(lane,old?[Math.min(old[0],p.value),Math.max(old[1],p.value)]:[p.value,p.value])}return bounds;
}
