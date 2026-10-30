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

export type ResearchUnit='number'|'return'|'variance'|'likelihood';
function researchDisplay(n:bigint,d:bigint,unit:ResearchUnit):string{
 const suffix=unit==='return'?'%':unit==='variance'?' return²':unit==='likelihood'?' log L':'';
 if(n===0n)return '0'+suffix;
 const negative=n<0n;n=negative?-n:n;if(unit==='return')n*=100n;
 let exponent=n.toString().length-d.toString().length;
 let a=n*(exponent<0?10n**BigInt(-exponent):1n),b=d*(exponent>0?10n**BigInt(exponent):1n);
 if(a<b){a*=10n;exponent--}
 let rounded=(a*1000n+b/2n)/b;
 if(rounded>=10000n){rounded/=10n;exponent++}
 const mantissa=Number(rounded)/1000;
 const text=exponent>=-3&&exponent<=5?new Intl.NumberFormat('en-US',{maximumSignificantDigits:4}).format(mantissa*10**exponent):String(mantissa)+'e'+(exponent>=0?'+':'')+exponent;
 return '≈ '+(negative?'-':'')+text+suffix;
}
/** Presentation only:four significant digits;exact/backend values stay in details. */
export function researchFraction(value:Fraction|null|undefined,unit:ResearchUnit='number'):string{
 if(!value||typeof value.numerator!=='string'||typeof value.denominator!=='string'||value.numerator.length>1235||value.denominator.length>1234||!/^(0|-?[1-9][0-9]*)$/.test(value.numerator)||!/^[1-9][0-9]*$/.test(value.denominator))return 'Unavailable';
 return researchDisplay(BigInt(value.numerator),BigInt(value.denominator),unit);
}
export function researchNumber(value:unknown,unit:ResearchUnit='number'):string{
 if(typeof value!=='number'||!Number.isFinite(value))return 'Unavailable';
 const [mantissa,exponent='0']=String(value).split('e'),[whole,decimal='']=mantissa.split('.');
 let n=BigInt(whole+decimal),d=10n**BigInt(decimal.length),e=Number(exponent);
 if(e>=0)n*=10n**BigInt(e);else d*=10n**BigInt(-e);
 return researchDisplay(n,d,unit);
}
