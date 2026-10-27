"""Explicit bounded submissions shards;no arbitrary URLs or automatic full-history crawl."""
import asyncio,copy,datetime,re
from . import sec
MAX_FILINGS=1024

def advertised(payload,cik):
    files=payload.get('filings',{}).get('files',[])
    if type(files) is not list or len(files)>128:raise ValueError('sec_shard_budget')
    seen=set();out=[]
    for row in files:
        if type(row) is not dict:raise ValueError('sec_shard_metadata')
        name=row.get('name')
        if type(name) is not str or not re.fullmatch('CIK'+re.escape(cik)+r'-submissions-\d{3,6}\.json',name) or name in seen:raise ValueError('sec_shard_name')
        count=row.get('filingCount')
        if type(count) is not int or not 0<=count<=10000:raise ValueError('sec_shard_count')
        start,end=sec.date(row.get('filingFrom')),sec.date(row.get('filingTo'))
        if start>end:raise ValueError('sec_shard_interval')
        seen.add(name);out.append({**row,'name':name})
    return sorted(out,key=lambda row:(row['filingTo'],row['name']),reverse=True)

def combine(parts):
    rows={};duplicates=0
    for part in parts:
        for row in part['filings']:
            key=row['accession']
            if key in rows:
                if rows[key]!=row:raise ValueError('sec_contradictory_historical_filing')
                duplicates+=1
            rows[key]=row
    ordered=sorted(rows.values(),key=lambda r:(r['filed'],r['accession']),reverse=True)
    return ordered[:MAX_FILINGS],{'parsed_unique_retained_union':len(rows),'overlap_duplicates':duplicates,'selected_rows':min(MAX_FILINGS,len(rows)),'truncated':len(rows)>MAX_FILINGS or any(p['integrity']['truncated'] for p in parts)}

async def load(workspace,ticker,max_shards):
    if type(max_shards) is not int or not 0<=max_shards<=2:raise ValueError('sec_shard_request_budget')
    company=workspace.resolve(ticker);cik=company['cik'];headers=workspace.permission('sec')
    if cik is None:raise ValueError('sec_issuer_identity_unavailable')
    if workspace.lock.locked():raise ValueError('upstream_refresh_busy')
    async with workspace.lock:
        async with asyncio.timeout(25):
            current_url=f'https://data.sec.gov/submissions/CIK{cik}.json';payload,digest=await workspace.fetch('sec',current_url,headers)
            parts=[sec.filings(payload,cik,limit=MAX_FILINGS)];files=advertised(payload,cik);sources=[{'component':'filings_current','url':current_url,'sha256':digest}]
            for descriptor in files[:max_shards]:
                await asyncio.sleep(1.01)
                url='https://data.sec.gov/submissions/'+descriptor['name'];raw,digest=await workspace.fetch('sec',url,headers)
                if type(raw) is not dict or type(raw.get('filingDate')) is not list or len(raw['filingDate'])!=descriptor['filingCount']:raise ValueError('sec_shard_count_mismatch')
                if any(not descriptor['filingFrom']<=sec.date(d)<=descriptor['filingTo'] for d in raw['filingDate']):raise ValueError('sec_shard_date_mismatch')
                parts.append(sec.filings({'cik':cik,'filings':{'recent':raw}},cik,limit=MAX_FILINGS));sources.append({'component':'filings_shard','url':url,'sha256':digest})
            rows,integrity=combine(parts);previous=workspace.cache.get(ticker,{})
            result=copy.deepcopy(previous.get('sec',{}));now=datetime.datetime.now(datetime.timezone.utc).isoformat()
            old_sources=[r for r in result.get('source_records',[]) if r.get('component')=='financials']
            result.update({'status':'AVAILABLE' if result.get('financials') else 'PARTIAL','filings':rows,'integrity':integrity,'coverage':'Bounded advertised submissions shards;not complete filing or XBRL history','historical_coverage':{'advertised_shards':len(files),'requested_shards':max_shards,'accepted_shards':len(sources)-1,'remaining_shards':max(0,len(files)-max_shards),'max_filings':MAX_FILINGS,'source_records':sources},'source_records':old_sources+[{**r,'received_at':now} for r in sources],'received_at':result.get('received_at',now),'filings_received_at':now,'origin':workspace.origin,'timeline':[{'event':r['form'],'published_at':r['accepted_at'],'filing_date':r['filed'],'url':r['url'],'source':'SEC EDGAR'} for r in rows[:64]],'reason':'Explicit bounded filing history;financial-fact and full-history coverage remain separate'})
            result['source_urls']=[r['url'] for r in result['source_records']];result['response_sha256']=[r['sha256'] for r in result['source_records']]
            result['components']={**result.get('components',{}),'filings':{'status':'AVAILABLE'},'financials':{'status':'AVAILABLE' if result.get('financials') else 'UNAVAILABLE'}}
            # Build all accepted state before the sole cache publication.
            candidate={**previous,'sec':result};workspace.cache[ticker]=candidate;workspace.cache.move_to_end(ticker)
            while len(workspace.cache)>8:workspace.cache.popitem(last=False)
    return workspace.view(ticker)
