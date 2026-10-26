const LIMIT=1024*1024;
export function parseMarketEvent(event:string):unknown|null{
 if(event.length>LIMIT)throw Error('Stock push frame budget exceeded');
 const lines=event.split('\n'),types=lines.filter(x=>x.startsWith('event: ')),data=lines.filter(x=>x.startsWith('data: '));
 if(types.some(x=>x==='event: error'))throw Error('Stock push snapshot rejected');
 if(!data.length)return null;
 if(types.length!==1||types[0]!=='event: state'||data.length!==1)throw Error('Unsupported stock push frame');
 return JSON.parse(data[0].slice(6));
}
export class MarketEventDecoder {
 private buffer='';private decoder=new TextDecoder('utf-8',{fatal:true});
 push(bytes:Uint8Array):unknown[]{
  if(bytes.byteLength>LIMIT)throw Error('Stock push chunk budget exceeded');
  this.buffer+=this.decoder.decode(bytes,{stream:true});
  if(this.buffer.length>LIMIT||new TextEncoder().encode(this.buffer).byteLength>LIMIT)throw Error('Stock push frame budget exceeded');
  const out:unknown[]=[];let end;
  while((end=this.buffer.indexOf('\n\n'))>=0){const frame=this.buffer.slice(0,end);this.buffer=this.buffer.slice(end+2);const data=parseMarketEvent(frame);if(data!==null)out.push(data)}
  return out;
 }
 finish(){this.buffer+=this.decoder.decode();if(this.buffer.trim())throw Error('Truncated stock push frame')}
}
