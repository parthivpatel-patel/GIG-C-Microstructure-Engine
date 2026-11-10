export type SECShardCoverage={advertised_shards:number;shard_offset:number;next_shard_offset:number|null;advertisement_sha256:string;batch_policy:string};
/** This cursor is public source metadata,not permission or an arbitrary source URL. */
export function secHistoryRequest(symbol:string,coverage?:SECShardCoverage){
 if(!/^[A-Z][A-Z0-9]{0,9}(?:[.-][A-Z0-9]{1,3})?$/.test(symbol))throw Error('Invalid filing identity');
 if(!coverage)return {symbol,max_shards:1};
 const n=coverage.next_shard_offset;
 if(!Number.isInteger(coverage.advertised_shards)||coverage.advertised_shards<1||coverage.advertised_shards>128||!Number.isInteger(coverage.shard_offset)||coverage.shard_offset<0||!Number.isInteger(n)||n===null||n<=coverage.shard_offset||n>=coverage.advertised_shards||typeof coverage.advertisement_sha256!=='string'||! /^[0-9a-f]{64}$/.test(coverage.advertisement_sha256))throw Error('Filing continuation unavailable;restart bounded history if the source changed');
 return {symbol,max_shards:1,shard_offset:n,advertisement_sha256:coverage.advertisement_sha256};
}
