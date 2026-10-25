import type {Fraction} from './contracts.ts';
export function rational(value:Fraction|null|undefined,scale='1'):string {
 if(!value)return '—';
 try {let n=BigInt(value.numerator),d=BigInt(value.denominator)*BigInt(scale);if(d<=0n)return '—';const negative=n<0n;n=negative?-n:n;const whole=n/d;let rem=n%d,out=whole.toString();if(rem){out+='.';let digits=0;while(rem&&digits<8){rem*=10n;out+=(rem/d).toString();rem%=d;digits++}if(rem)out+='…'}return (negative?'-':'')+out;}catch{return '—'}
}
export function price(ticks:string|undefined,scale:string):string{return ticks===undefined?'—':rational({numerator:ticks,denominator:'1'},scale)}
export function percent(f:Fraction|null|undefined):string{return f?rational({numerator:(BigInt(f.numerator)*100n).toString(),denominator:f.denominator})+'%':'—'}
export function fractionTitle(f:Fraction|null|undefined,scale='1'):string{return f?`${f.numerator} / (${f.denominator} × ${scale}) exact; display bounded to 8 decimal digits`:'Unavailable for current state'}
export function pretty(value:unknown):string{return JSON.stringify(value,null,2)}
export function chartRatio(value:bigint,maximum:bigint):number {if(maximum<=0n)return 0;return Number(value*1000000n/maximum)/1000000}
export function boundedTickOffset(value:string,anchor:bigint,span:bigint):number{return chartRatio(BigInt(value)-anchor,span)}
