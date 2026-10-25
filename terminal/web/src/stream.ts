import {request} from './api';
export async function browserStream(origin:string,host:string,protocol:string){
 const url=`${protocol==='https:'?'wss':'ws'}://${host}/api/v1/stream`;
 const result=await request<{ticket:string;protocol:string}>('/stream-ticket',{browser_origin:origin,websocket_url:url,attempt_id:crypto.randomUUID()});
 if(result.protocol!=='gig-stream-v1'||!/^[A-Za-z0-9_-]{43}$/.test(result.ticket))throw new Error('Invalid stream handshake proof');
 return new WebSocket(url,[result.protocol,`gig-ticket.${result.ticket}`]);
}
