/** Strict bounded imports for private financial exports. No transport or schema inference. */
export const MAX_OFFLINE_BYTES=256*1024;
const MAX_DEPTH=32,MAX_NODES=40000,MAX_STRING=16384;
function fail():never{throw Error('Invalid or ambiguous offline JSON export')}


function exactIntegerToken(token:string):void{
 if(token.length>128)fail();
 const parts=/^(-?)([0-9]+)(?:\.([0-9]+))?(?:[eE]([+-]?[0-9]+))?$/.exec(token);if(!parts)fail();
 const exponent=BigInt(parts[4]||'0');if(exponent < -128n||exponent>128n)fail();
 const fraction=parts[3]||'',scale=exponent-BigInt(fraction.length);let integer=BigInt(parts[2]+fraction);
 if(scale>=0n)integer*=10n**scale;
 else{const divisor=10n**(-scale);if(integer%divisor!==0n)fail();integer/=divisor}
 // Numeric metadata cannot retain a minus sign on zero after canonical JSON.
 // Reported financial quantities are strings and keep their original spelling.
 if(parts[1]&&integer===0n)fail();
 if(parts[1])integer=-integer;
 if(integer < -9007199254740991n||integer>9007199254740991n)fail();
}

export function parseBoundedOfflineJson(text:string,maxBytes:number,maxNodes:number,maxDepth=MAX_DEPTH):unknown{
 if(!Number.isSafeInteger(maxBytes)||maxBytes<1||maxBytes>4*1024*1024||!Number.isSafeInteger(maxNodes)||maxNodes<1||maxNodes>320000||!Number.isSafeInteger(maxDepth)||maxDepth<1||maxDepth>36)fail();
 if(typeof text!=='string'||!text.length||text.length>maxBytes||new TextEncoder().encode(text).byteLength>maxBytes)fail();
 let pos=0,nodes=0;
 const whitespace=()=>{while(pos<text.length&&' \t\r\n'.includes(text[pos]))pos++};
 const string=():string=>{
  if(text[pos]!== '"')fail();const start=pos++;let length=0;
  while(pos<text.length){const c=text[pos++];if(c==='"'){
    const decoded=JSON.parse(text.slice(start,pos)) as string;
    for(const point of decoded){
     const scalar=point.codePointAt(0)!;
     if(scalar>=0xd800&&scalar<=0xdfff)fail();
    }
    return decoded;
   }
   if(c.charCodeAt(0)<32)fail();
   if(c==='\\'){const escape=text[pos++];if(escape==='u'){if(!/^[0-9a-fA-F]{4}$/.test(text.slice(pos,pos+4)))fail();pos+=4}else if(!escape||!'"\\/bfnrt'.includes(escape))fail()}
   if(++length>MAX_STRING)fail();
  }return fail();
 };
 const number=/-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?/y;
 const value=(depth:number):void=>{
  if(depth>maxDepth||++nodes>maxNodes)fail();whitespace();const c=text[pos];
  if(c==='{'){
   pos++;whitespace();if(text[pos]==='}'){pos++;return}const keys=new Set<string>();
   while(true){whitespace();if(++nodes>maxNodes)fail();const key=string();if(keys.has(key))fail();keys.add(key);whitespace();if(text[pos++]!==':')fail();value(depth+1);whitespace();const next=text[pos++];if(next==='}')return;if(next!==',')fail()}
  }
  if(c==='['){pos++;whitespace();if(text[pos]===']'){pos++;return}while(true){value(depth+1);whitespace();const next=text[pos++];if(next===']')return;if(next!==',')fail()}}
  if(c==='"'){string();return}
  for(const literal of['true','false','null'])if(text.startsWith(literal,pos)){pos+=literal.length;return}
  number.lastIndex=pos;const match=number.exec(text);if(!match)fail();exactIntegerToken(match[0]);pos=number.lastIndex;
 };
 value(0);whitespace();if(pos!==text.length)fail();
 return JSON.parse(text) as unknown;
}

export function parseOfflineJson(text:string):unknown{return parseBoundedOfflineJson(text,MAX_OFFLINE_BYTES,MAX_NODES)}

export async function readBoundedOfflineJson(file:Pick<Blob,'size'|'arrayBuffer'>,maxBytes:number,maxNodes:number,maxDepth=MAX_DEPTH,signal?:AbortSignal):Promise<unknown>{
 if(!Number.isSafeInteger(maxBytes)||maxBytes<1||maxBytes>4*1024*1024)fail();
 if(!Number.isSafeInteger(file.size)||file.size<1||file.size>maxBytes)fail();
 if(signal?.aborted)throw new DOMException('Offline import aborted','AbortError');
 // Browser Blob.size bounds this retained buffer. No claim about arbitrary JS
 // object implementations or global browser memory/prefetch behavior is made.
 const buffer=await file.arrayBuffer();
 if(signal?.aborted)throw new DOMException('Offline import aborted','AbortError');
 if(!(buffer instanceof ArrayBuffer)||buffer.byteLength!==file.size||buffer.byteLength>maxBytes)fail();
 let text:string;try{text=new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(buffer)}catch{return fail()}
 return parseBoundedOfflineJson(text,maxBytes,maxNodes,maxDepth);
}

export async function readOfflineJson(file:Pick<Blob,'size'|'arrayBuffer'>,signal?:AbortSignal):Promise<unknown>{return readBoundedOfflineJson(file,MAX_OFFLINE_BYTES,MAX_NODES,MAX_DEPTH,signal)}
