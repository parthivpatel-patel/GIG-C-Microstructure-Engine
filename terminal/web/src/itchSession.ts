import type {TerminalState} from './contracts';
// Display only the server-owned bounded book identities,never guessed stock scenes.
export function itchBookChoices(state:TerminalState):{index:number;label:string}[]{
 const rows=state.capabilities?.itch_book_selection;
 if(!Array.isArray(rows)||rows.length<1||rows.length>2)return [];
 const result:{index:number;label:string}[]=[];
 for(let i=0;i<rows.length;i++){
  const row=rows[i];
  if(typeof row!=='object'||row===null||row.index!==String(i)||typeof row.stock!=='string'||row.stock.length!==8||!/^[\x20-\x7e]+$/.test(row.stock)||!row.stock.trim())return [];
  result.push({index:i,label:row.stock.trim()});
 }
 return result;
}
export function replayMinimum(state:TerminalState):number {
 const value=state.replay_min_position;
 if(value===undefined)return 0;
 if(typeof value!=='number'||!Number.isSafeInteger(value)||value<0||value>state.position||value>state.event_count)throw new Error('Invalid checkpoint replay boundary');
 return value;
}

export function replayProgress(state:TerminalState):number {
 const minimum=replayMinimum(state);
 return state.event_count>minimum?(state.position-minimum)/(state.event_count-minimum)*100:state.event_count?100:0;
}
