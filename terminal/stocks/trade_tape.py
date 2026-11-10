"""Pure bounded reference reconciliation,not an exchange-complete or executable tape.

Consumes the existing normalized observation contract in capture order. Cancellation
removal requires an explicit authored-fixture contract;observed action codes remain
unsupported until an authoritative provider profile is qualified. No native mutation.
"""
import copy,hashlib,json,re
from fractions import Fraction
from .prices import decimal

class Rejected(ValueError):pass

def _reference(value):
 if type(value)is not str or not 1<=len(value)<=64 or any(not 32<ord(c)<127 for c in value):raise Rejected('REFERENCE')
 return value

def _amount(value):
 try:return Fraction(decimal(value,True))
 except (ValueError,TypeError,OverflowError):raise Rejected('NUMERIC')from None

def _wire(value):return {'numerator':str(value.numerator),'denominator':str(value.denominator)}

def reconcile(history,symbol,generation,*,cancellation_contract=None):
 if type(history)is not list or len(history)>256:raise ValueError('trade_tape_record_budget')
 if type(symbol)is not str or not re.fullmatch(r'[A-Z][A-Z0-9]{0,9}(?:[.-][A-Z0-9]{1,3})?',symbol) or type(generation)is not int or not 0<=generation<2**53:raise ValueError('trade_tape_scope')
 if cancellation_contract not in (None,'AUTHORED_CANCEL_C_V1'):raise ValueError('trade_tape_cancel_contract')
 active={};retired=set();seen={};parents=[];prior=0;origin=None;session=None;duplicates=corrections=cancels=processed=relevant=0;error=None
 for row in history:
  receipt=None
  try:
   if type(row)is not dict:raise Rejected('SCHEMA')
   if type(row.get('symbol'))is not str or not re.fullmatch(r'[A-Z][A-Z0-9]{0,9}(?:[.-][A-Z0-9]{1,3})?',row['symbol']) or type(row.get('generation'))is not int or not 0<=row['generation']<2**53:raise Rejected('SCOPE')
   if row.get('symbol')!=symbol or row.get('generation')!=generation:continue
   relevant+=1;receipt=row.get('receipt_index')
   capture=row.get('source_session_id')
   if type(capture)is not str or not re.fullmatch('[a-f0-9]{32}',capture)or session not in (None,capture):raise Rejected('SOURCE_SESSION')
   session=capture
   if type(receipt)is not int or not prior<receipt<2**53:raise Rejected('CAPTURE_ORDER')
   prior=receipt
   kind=row.get('kind')
   if kind in ('quote','bar'):processed+=1;continue
   if kind not in ('trade','correction','cancel'):raise Rejected('UNSUPPORTED_KIND')
   current_origin=row.get('origin')
   if current_origin not in ('HISTORICAL_SYNTHETIC','OBSERVED_OFFICIAL_RESPONSE') or origin not in (None,current_origin):raise Rejected('ORIGIN')
   origin=current_origin
   if row.get('provider')!='alpaca' or row.get('feed')!='iex':raise Rejected('SOURCE')
   exchange=_reference(row.get('exchange_codes',{}).get('x'));tape=_reference(row.get('tape_code'))
   stamp=row.get('source_timestamp_ns')
   if type(stamp)is not str or not re.fullmatch(r'\d{1,24}',stamp):raise Rejected('SOURCE_CLOCK')
   identity=row.get('identity_sha256');parent=row.get('source_sha256')
   if any(type(h)is not str or not re.fullmatch('[a-f0-9]{64}',h)for h in (identity,parent)):raise Rejected('PROVENANCE')
   data=row.get('data');conditions=row.get('conditions',{})
   if type(data)is not dict or len(data)>16 or any(type(k)is not str or type(v)is not str or len(k)>64 or len(v)>256 for k,v in data.items()):raise Rejected('DATA')
   if type(conditions)is not dict or len(conditions)>3 or any(k not in ('c','oc','cc') or v is not None and (type(v)is not list or len(v)>32 or any(type(c)is not str or len(c)>16 for c in v))for k,v in conditions.items()):raise Rejected('CONDITIONS')
   if kind=='trade':_reference(row.get('trade_id'))
   elif row.get('trade_id')is not None:raise Rejected('REFERENCE')
   semantic=json.dumps([kind,exchange,tape,stamp,row.get('trade_id'),data,conditions],sort_keys=True,separators=(',',':'))
   if identity in seen:
    if seen[identity]!=semantic:raise Rejected('IDENTITY_CONFLICT')
    duplicates+=1;processed+=1;continue
   seen[identity]=semantic;parents.append(parent)
   scope=(exchange,tape)
   if kind=='trade':
    reference=_reference(row.get('trade_id'));key=(*scope,reference)
    if key in active or key in retired:raise Rejected('REUSED_REFERENCE')
    price,size=_amount(data.get('price')),_amount(data.get('size'))
    active[key]={'trade_id':reference,'exchange':exchange,'tape':tape,'price':data['price'],'size':data['size'],'original_receipt':receipt,'source_timestamp_ns':stamp,'conditions':copy.deepcopy(conditions.get('c')),'lineage_receipts':[receipt]}
   else:
    reference=_reference(data.get('original_id'if kind=='correction'else'trade_id'));key=(*scope,reference)
    if key not in active:raise Rejected('UNKNOWN_REFERENCE')
    original=active[key]
    old_price=_amount(data.get('original_price'if kind=='correction'else'price'));old_size=_amount(data.get('original_size'if kind=='correction'else'size'))
    if old_price!=_amount(original['price'])or old_size!=_amount(original['size']):raise Rejected('ORIGINAL_MISMATCH')
    if kind=='cancel':
     if cancellation_contract!='AUTHORED_CANCEL_C_V1'or origin!='HISTORICAL_SYNTHETIC'or data.get('action')!='C':raise Rejected('UNSUPPORTED_CANCEL_PROFILE')
     del active[key];retired.add(key);cancels+=1
    else:
     replacement=_reference(data.get('corrected_id'));new_key=(*scope,replacement)
     if new_key!=key and(new_key in active or new_key in retired):raise Rejected('REPLACEMENT_COLLISION')
     _amount(data.get('corrected_price'));_amount(data.get('corrected_size'))
     if 'oc'in conditions and conditions['oc']!=original['conditions']:raise Rejected('ORIGINAL_CONDITIONS')
     changed={**original,'trade_id':replacement,'price':data['corrected_price'],'size':data['corrected_size'],'conditions':copy.deepcopy(conditions.get('cc')),'lineage_receipts':original['lineage_receipts']+[receipt]}
     if new_key!=key:del active[key];retired.add(key)
     active[new_key]=changed;corrections+=1
   processed+=1
  except (Rejected,KeyError,TypeError,AttributeError)as exc:
   error={'code':str(exc)if isinstance(exc,Rejected)else'SCHEMA','receipt_index':receipt if type(receipt)is int and 0<=receipt<2**53 else None};break
 trades=sorted(active.values(),key=lambda r:r['original_receipt'])
 result={'schema':'gig.bounded.trade_reconciliation.v2','source_session_id':session,'symbol':symbol,'generation':generation,'state':'UNRESOLVED'if error else'CONSISTENT_RETAINED_WINDOW'if seen else'NO_TRADE_INPUT','origin':origin or'UNAVAILABLE','input_records':len(history),'relevant_records':relevant,'accepted_prefix_records':processed,'duplicate_records':duplicates,'applied_corrections':corrections,'applied_cancels':cancels,'active_count':len(trades),'trades':trades,'error':error,'corrected_size_sum':None if error or not seen else _wire(sum((_amount(r['size'])for r in trades),Fraction())),'source_sha256':parents,'complete_tape':False,'order_book_mutations':0,'cancellation_contract':cancellation_contract,'policy':'Exact normalized references in capture order;source time retained,not reordered. No complete initial tape,exchange sequence,aggressor,lot conversion or L3 state inferred. Observed cancellation codes unqualified.'}
 result['canonical_sha256']=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 return result
