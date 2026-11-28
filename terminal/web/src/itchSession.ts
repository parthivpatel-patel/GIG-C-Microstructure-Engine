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
 if(state.capabilities?.itch_source_finished===true)return 100;
 return state.event_count>minimum?(state.position-minimum)/(state.event_count-minimum)*100:0;
}

type PartialSourceTail = {
 next_frame: string; next_ordinal: string; residual_bytes: string;
 source_offset: string; source_sha256: string; residual_sha256: string;
 decompressed_sha256: string|null;
};

export function partialSourceTail(state:TerminalState):PartialSourceTail|null {
 const lineage=state.provenance.source_recovery_history;
 if(!Array.isArray(lineage)||!lineage.length)return null;
 const row=lineage[lineage.length-1] as Record<string,unknown>|null;
 if(!row)return null;
 const members=row.source_profile==='PARTIAL_GZIP_MEMBERS_V1';
 const gzip=members||row.source_profile==='PARTIAL_SINGLE_GZIP_V1';
 if(!gzip&&row.source_profile!=='PARTIAL_BINARY_FILE_V1')return null;
 const reject=():never=>{throw Error('Invalid partial ITCH source receipt')};
 if(state.mode!=='HISTORICAL_REPLAY'||state.origin!=='HISTORICAL_SYNTHETIC'||
    state.provenance.dataset!=='itch-checkpoint-v1'||lineage.length>4||
    state.provenance.source_recovery_history_encoding!=='DECIMAL_STRINGS_V1'||
    row.container!==(members?'gzip_members':gzip?'single_gzip':'binary_file')||row.capture!==state.provenance.capture||
    row.generation!==state.provenance.generation)reject();
 const number=(key:string):bigint=>{
  const value=row[key];
  if(typeof value!=='string'||!/^(0|[1-9][0-9]{0,19})$/.test(value))return reject();
  const n=BigInt(value);
  if(n>18446744073709551615n)return reject();
  return n;
 };
 for(const key of gzip?['source_sha256','residual_sha256','decompressed_sha256']:['source_sha256','residual_sha256']){
  const value=row[key];
  if(typeof value!=='string'||!/^[a-f0-9]{64}$/.test(value))reject();
 }
 const offset=number(gzip?'decompressed_offset':'source_offset'),residual=number('residual_bytes'),records=number('to_source_records');
 if(residual<1n||residual>65536n||offset+residual>33554432n||
    number('first_frame')+offset!==number('next_frame')||
    number('first_ordinal')+records!==number('next_ordinal')||
    number('from_source_records')>records||records>BigInt(state.position))reject();
 return {
  source_offset:String(offset),residual_bytes:String(residual),next_frame:String(row.next_frame),
  next_ordinal:String(row.next_ordinal),source_sha256:String(row.source_sha256),
  residual_sha256:String(row.residual_sha256),
  decompressed_sha256:gzip?String(row.decompressed_sha256):null,
 };
}

type DecodedPrefix={decoded_bytes:string;decoded_sha256:string};
export function decodedItchPrefix(state:TerminalState):DecodedPrefix|null {
 const lineage=state.provenance.source_recovery_history;
 if(!Array.isArray(lineage)||!lineage.length)return null;
 const row=lineage[lineage.length-1] as Record<string,unknown>|null;
 if(!row||row.source_profile!=='COMPLETE_FRAMES_DECODED_PREFIX_V1')return null;
 const hash=(v:unknown):v is string=>typeof v==='string'&&/^[a-f0-9]{64}$/.test(v);
 const count=(v:unknown):v is string=>typeof v==='string'&&/^(0|[1-9][0-9]{0,19})$/.test(v);
 if(state.mode!=='HISTORICAL_REPLAY'||state.origin!=='HISTORICAL_SYNTHETIC'||
    state.provenance.dataset!=='itch-checkpoint-v1'||lineage.length>4||
    state.provenance.source_recovery_history_encoding!=='DECIMAL_STRINGS_V1'||
    row.capture!==state.provenance.capture||row.generation!==state.provenance.generation||
    !['binary_file','single_gzip','gzip_members'].includes(String(row.container))||
    !count(row.decoded_bytes)||BigInt(row.decoded_bytes)>33554432n||
    !count(row.from_source_records)||!count(row.to_source_records)||
    BigInt(row.from_source_records)>BigInt(row.to_source_records)||BigInt(row.to_source_records)>BigInt(state.position)||
    !hash(row.source_sha256)||!hash(row.decoded_sha256)||
    row.container==='binary_file'&&row.source_sha256!==row.decoded_sha256)throw Error('Invalid decoded ITCH source receipt');
 return {decoded_bytes:row.decoded_bytes,decoded_sha256:row.decoded_sha256};
}

type CompletedSource={
 capsule_sha256:string;
 source_sha256:string;
 checkpoint_sha256:string;
 container:'binary_file'|'single_gzip'|'gzip_members';
 source_records:string;
 exchange_completeness:false;
};

export function completedItchSource(state:TerminalState):CompletedSource|null{
 const source=state.provenance.completed_source as CompletedSource|undefined;
 if(state.capabilities?.itch_source_finished!==true&&source===undefined)return null;
 const validHash=(value:unknown)=>typeof value==='string'&&/^[0-9a-f]{64}$/.test(value);
 if(!source||state.capabilities?.itch_source_finished!==true||state.capabilities?.itch_completion_available!==true||
    state.mode!=='HISTORICAL_REPLAY'||state.origin!=='HISTORICAL_SYNTHETIC'||state.provider!=='authored-itch'||
    state.provenance.dataset!=='itch-completed-v1'||state.provenance.session_segment!==source.capsule_sha256||
    state.playing||state.position!==state.event_count||state.replay_min_position!==state.position||
    state.feed.state!=='COMPLETE'||state.feed.capture_complete!==true||
    !validHash(source.capsule_sha256)||!validHash(source.source_sha256)||!validHash(source.checkpoint_sha256)||
    source.source_records!==String(state.position)||!['binary_file','single_gzip','gzip_members'].includes(source.container)||
    source.exchange_completeness!==false)throw Error('Invalid completed ITCH source receipt');
 return source;
}
