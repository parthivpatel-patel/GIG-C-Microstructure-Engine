"""Bounded owner-configured session evidence;absence is UNKNOWN,never inferred closed."""
import hashlib,json,stat,os
from .prices import timestamp
from terminal.providers.kraken import timestamp_ns
from .identity import symbol

class SessionSchedule:
 def __init__(self,raw=None):
  self.rows=[];self.symbols=[];self.source=None;self.digest=None;self.reason='no_authoritative_schedule_configured'
  if raw is None:return
  if type(raw) is not bytes or len(raw)>65536:raise ValueError('session_schedule_budget')
  def pairs(items):
   result={}
   for k,v in items:
    if k in result:raise ValueError('session_duplicate_field')
    result[k]=v
   return result
  try:p=json.loads(raw,object_pairs_hook=pairs)
  except (ValueError,RecursionError):raise ValueError('session_schema') from None
  if type(p) is not dict or set(p)!={'schema','source','symbols','intervals'} or p['schema']!='gig.session.schedule.v1':raise ValueError('session_schema')
  if type(p['source']) is not str or not 1<=len(p['source'])<=256 or any(ord(c)<32 for c in p['source']):raise ValueError('session_source')
  if type(p['symbols']) is not list or not 1<=len(p['symbols'])<=20 or any(type(s) is not str for s in p['symbols']) or len(set(p['symbols']))!=len(p['symbols']):raise ValueError('session_symbols')
  for s in p['symbols']:symbol(s)
  if type(p['intervals']) is not list or not 1<=len(p['intervals'])<=1000:raise ValueError('session_intervals')
  prior=None
  for r in p['intervals']:
   if type(r) is not dict or set(r)!={'start','end','state'} or r['state'] not in ('PRE','REGULAR','POST','CLOSED'):raise ValueError('session_interval')
   timestamp(r['start']);timestamp(r['end']);a,b=int(timestamp_ns(r['start'])),int(timestamp_ns(r['end']))
   if a>=b or prior is not None and a<prior:raise ValueError('session_order')
   self.rows.append((a,b,r['state']));prior=b
  self.symbols=p['symbols'];self.source=p['source'];self.digest=hashlib.sha256(raw).hexdigest();self.reason=None
 @classmethod
 def configured(cls,environment):
  path=environment.get('GIG_MARKET_SESSION_FILE')
  if not path:return cls()
  try:
   with os.fdopen(os.open(path,os.O_RDONLY|os.O_NONBLOCK|getattr(os,'O_NOFOLLOW',0)),'rb') as f:
    if not stat.S_ISREG(os.fstat(f.fileno()).st_mode):raise ValueError('session_file')
    return cls(f.read(65537))
  except (OSError,ValueError,TypeError,KeyError):
   value=cls();value.reason='configured_schedule_invalid';return value
 def at(self,symbol,source_time):
  state='UNKNOWN';ns=int(timestamp_ns(source_time)) if source_time else None
  if symbol in self.symbols and ns is not None:state=next((v for a,b,v in self.rows if a<=ns<b),'UNKNOWN')
  return {'state':state,'authority':'OWNER_CONFIGURED_SCHEDULE_NOT_REALTIME_HALT_AUTHORITY' if self.digest else 'UNAVAILABLE','source':self.source,'schedule_sha256':self.digest,'reason':self.reason if self.reason else 'outside_declared_coverage' if state=='UNKNOWN' else None,'timestamp_basis':'source observation time,not inferred exchange open','limitations':'No real-time halt,auction,holiday or current calendar authority beyond explicit schedule intervals'}
