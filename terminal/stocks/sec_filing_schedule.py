"""Bounded supplied-submissions planning; no transport or automatic execution."""
import re
from . import sec
FORMS={'10-K','10-K/A','10-Q','10-Q/A'}

def query(start,end,max_shards,max_filings):
 sec.date(start);sec.date(end)
 if start>end or type(max_shards)is not int or not 0<=max_shards<=4 or type(max_filings)is not int or not 1<=max_filings<=8:raise ValueError('sec_schedule_query')

def shards(payload,cik,start,end):
 rows=payload.get('filings',{}).get('files',[])
 if type(rows)is not list or len(rows)>128:raise ValueError('sec_schedule_shard_budget')
 out=[];seen=set()
 for row in rows:
  if type(row)is not dict:raise ValueError('sec_schedule_shard')
  name=row.get('name');count=row.get('filingCount')
  if type(name)is not str or not re.fullmatch('CIK'+cik+r'-submissions-[0-9]{3}\.json',name)or name in seen:raise ValueError('sec_schedule_shard_name')
  seen.add(name)
  if type(count)is not int or not 0<=count<=10000:raise ValueError('sec_schedule_shard_count')
  low=sec.date(row.get('filingFrom'));high=sec.date(row.get('filingTo'))
  if low>high:raise ValueError('sec_schedule_shard_dates')
  if low<=end and high>=start:out.append({'name':name,'count':count,'start':low,'end':high})
 return sorted(out,key=lambda r:(r['end'],r['start'],r['name']),reverse=True)

def schedule(groups,start,end,limit):
 unique={}
 for rows,source in groups:
  for row in rows:
   key=row['accession']
   if key in unique:
    if unique[key]['filing']!=row:raise ValueError('sec_schedule_contradictory_filing')
    unique[key]['metadata_sources'].append(source)
   else:unique[key]={'filing':row,'metadata_sources':[source]}
 eligible=[v for v in unique.values()if start<=v['filing']['filed']<=end and v['filing']['form']in FORMS]
 eligible.sort(key=lambda v:(v['filing']['filed'],v['filing']['accession']),reverse=True)
 return eligible[:limit],len(eligible)>limit

def historical_rows(payload,columns,name,cik):
 advertised=[r for r in shards(payload,cik,'0001-01-01','9999-12-31')if r['name']==name]
 if len(advertised)!=1:raise ValueError('sec_schedule_shard_not_advertised')
 item=advertised[0]
 if type(columns)is not dict or type(columns.get('form'))is not list or len(columns['form'])!=item['count']:raise ValueError('sec_schedule_shard_count_binding')
 parsed=sec.filings({'cik':cik,'filings':{'recent':columns}},cik,limit=1024)
 if any(not item['start']<=r['filed']<=item['end']for r in parsed['filings']):raise ValueError('sec_schedule_shard_date_binding')
 return parsed
