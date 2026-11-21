"""Compact identities plus one actual authored export; full generated log stays in work."""
from pathlib import Path
from collections import Counter
import hashlib,json
root=Path(__file__).resolve().parent
raw=root/'installed-comparison-exports.log'
values=json.loads(raw.read_text())
def hashed(p):return {'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
assert len(values)==19
changed=next(packet for name,packet in values if name=='changed')
example=root/'authored-changed-comparison.json'
with example.open('x')as out:out.write(json.dumps(changed,separators=(',',':'))+'\n')
variants=[]
for name,packet in values:
 variants.append({'name':name,'schema':packet['schema'],'profile':packet['profile'],'sha256':packet['sha256'],'collection_sha256':packet['collection_sha256'],'cutoffs':[{'as_of':entry['as_of'],'cutoff_ns':entry['cutoff_ns'],'source_packet_sha256':entry['sha256'],'accession':entry['accounting']['source_filing']['accession']if entry['accounting']['source_filing']else None,'original_source_sha256':entry['source']['source']['source_sha256']if entry['source']else None,'source_origin':entry['source']['origin']if entry['source']else None}for entry in packet['entries']],'adjacent_comparisons':len(packet['comparisons']),'row_status_counts':dict(sorted(Counter(row['status']for comparison in packet['comparisons']for section in comparison['statements'].values()for row in section['rows']).items()))})
receipt={'schema':'gig.nov21.engineering.authored_comparison_variants.v1','source':json.loads((root/'configuration.json').read_text())['source'],'full_generated_file':{'name':raw.name,**hashed(raw),'retained_in_work':True},'variants':variants,'example':{'name':example.name,**hashed(example),'packet_sha256':changed['sha256']},'source_origin':'HISTORICAL_SYNTHETIC','provider_requested':False,'independent_issuer_authentication':False}
with(root/'comparison-variant-identities.json').open('x')as out:out.write(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'source':receipt['source'],'full_generated_file':receipt['full_generated_file'],'variants':len(variants),'example':receipt['example'],'receipt':hashed(root/'comparison-variant-identities.json')},sort_keys=True))
