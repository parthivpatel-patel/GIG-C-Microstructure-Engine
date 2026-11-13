"""Fixed-host read-only XML/JSON wire;used only through explicit ingestion gates."""
from contextlib import asynccontextmanager
from urllib.parse import urlsplit
import httpx
from .sec_config import user_agent_valid
from .sec_filing_ingest import IngestError
class SECReadWire:
 def __init__(self,transport=None):self.transport=transport
 @asynccontextmanager
 async def open(self,url,headers,*,timeout):
  u=urlsplit(url)
  if u.scheme!='https'or u.netloc not in('www.sec.gov','data.sec.gov','www.xbrl.org','xbrl.sec.gov','xbrl.fasb.org')or u.query or u.fragment or '%'in url or '\\'in url or '..'in u.path:raise IngestError('sec_ingest_wire_url')
  if set(headers)!={'User-Agent','Accept-Encoding'}or not user_agent_valid(headers['User-Agent'])or headers['Accept-Encoding']!='identity':raise IngestError('sec_ingest_wire_headers')
  if type(timeout)not in(int,float)or not 0<timeout<=8:raise IngestError('sec_ingest_wire_timeout')
  try:
   async with httpx.AsyncClient(transport=self.transport,follow_redirects=False,timeout=timeout,limits=httpx.Limits(max_connections=1),trust_env=self.transport is None)as client:
    async with client.stream('GET',url,headers=headers)as response:
     yield Reply(response)
  except httpx.TimeoutException:raise TimeoutError('sec_ingest_wire_timeout')from None
  except httpx.HTTPError:raise IngestError('sec_ingest_wire_failure')from None
class Reply:
 def __init__(self,response):
  self.url=str(response.url);self.status=response.status_code;self.headers=response.headers;self.iterator=response.aiter_raw(chunk_size=65536);self.buffer=b'';self.done=False
 async def read(self,n):
  if type(n)is not int or not 1<=n<=65536:raise IngestError('sec_ingest_wire_read_budget')
  if not self.buffer and not self.done:
   try:self.buffer=await anext(self.iterator)
   except StopAsyncIteration:self.done=True
  out=self.buffer[:n];self.buffer=self.buffer[n:];return out
