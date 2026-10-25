#!/usr/bin/env python3
"""Independent dictionary/decimal transition oracle for authored LOBSTER rows."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from check_lobster_reference import message as parse_message
from lobster_synthetic import rows,book,write
from run_lobster_validation import run


def effect(before,message,after):
    # Independent price->volume maps; no native index/FIFO/recovery code used.
    _,code,_,size,price,direction,_=message
    answer=dict(quantity_eligible=0,quantity_matches=0,best_eligible=0,best_matches=0,depth_eligible=0,depth_matches=0)
    def maps(row):return [{row[i]:row[i+1] for i in range(side,20,4) if row[i]!=(9999999999 if side==0 else -9999999999)} for side in (0,2)]
    prior,current=maps(before),maps(after)
    def best(x):return (min(x[0].items()) if x[0] else None,max(x[1].items()) if x[1] else None)
    zero=lambda row:any(row[i+1]==0 and row[i] not in (9999999999,-9999999999) for i in range(0,20,2))
    crossed=lambda row:row[0]!=9999999999 and row[2]!=-9999999999 and row[2]>=row[0]
    if crossed(before) or crossed(after) or zero(before) or zero(after):return answer
    if code not in (1,2,3,4,5,7):return answer
    if code in (5,7):answer.update(best_eligible=1,best_matches=int(best(prior)==best(current)),depth_eligible=1,depth_matches=int(prior==current));return answer
    side=1 if direction==1 else 0;other=1-side;old=prior[side]
    if price not in old and code!=1:return answer
    if price not in old and len(old)==5 and (price<min(old) if side else price>max(old)):
        answer.update(best_eligible=1,best_matches=int(best(prior)==best(current)),depth_eligible=1,depth_matches=int(prior==current));return answer
    before_qty=old.get(price,0);next_qty=before_qty+(size if code==1 else -size)
    answer['quantity_eligible']=1;answer['quantity_matches']=int(next_qty>=0 and current[side].get(price,0)==next_qty)
    if next_qty<0:return answer
    expected=copy.deepcopy(prior)
    if next_qty:expected[side][price]=next_qty
    else:expected[side].pop(price,None)
    answer['best_eligible']=int(bool(expected[side]));answer['best_matches']=int(bool(expected[side]) and best(expected)==best(current))
    answer['depth_eligible']=int(next_qty>0 or len(old)<5)
    if answer['depth_eligible']:
        expected[side]=dict(sorted(expected[side].items(),reverse=bool(side))[:5]);answer['depth_matches']=int(expected==current)
    return answer


def model(message_rows,reference_rows):
    orders={};seen={};blocked=False;previous=None
    out=dict(rows=0,native=0,external=0,unknown_order=0,inconsistent=0,unsupported=0,blocked=0,native_rejected=0,resource_rejected=0,quantity_eligible=0,quantity_matches=0,best_eligible=0,best_matches=0,depth_eligible=0,depth_matches=0,lower_bound_checks=0,lower_bound_violations=0,equal_level_quantities=0,first_mismatch=None)
    for index,(raw,reference) in enumerate(zip(message_rows,reference_rows)):
        value=parse_message(raw);assert value is not None;time,code,identity,qty,price,side,kind=value
        if previous is not None:
            e=effect(previous,value,reference)
            for k,v in e.items():out[k]+=v
            if any(e[k]>e[k.replace('eligible','matches')] for k in ('quantity_eligible','best_eligible','depth_eligible')) and out['first_mismatch'] is None:out['first_mismatch']=index
        previous=reference;out['rows']+=1
        if code not in (1,2,3,4,5,7):out['unsupported']+=1;blocked=True
        elif code in (5,7):out['external']+=1
        elif blocked:out['blocked']+=1
        elif code!=1 and identity not in orders:
            if seen.get(identity)==True:out['inconsistent']+=1;blocked=True
            else:out['unknown_order']+=1;seen[identity]=False
        elif (code==1 and identity in seen) or (identity in orders and (orders[identity][0:2]!=[side,price] or (qty!=orders[identity][2] if code==3 else qty>orders[identity][2]) or (code==2 and qty==orders[identity][2]))):out['inconsistent']+=1;blocked=True
        else:
            if code==1:
                crossing=any(s!=side and (price>p if side==1 else price<p) for s,p,_ in orders.values())
                if crossing:out['native_rejected']+=1;blocked=True
                else:orders[identity]=[side,price,qty];seen[identity]=True;out['native']+=1
            else:
                orders[identity][2]-=qty;out['native']+=1
                if orders[identity][2]==0:del orders[identity]
        levels={(1,reference[i]):reference[i+1] for i in range(2,20,4)}|{(-1,reference[i]):reference[i+1] for i in range(0,20,4)}
        if not blocked and any((s,p) not in levels for s,p,q in orders.values()):blocked=True
        if not blocked:
            sums={}
            for s,p,q in orders.values():sums[s,p]=sums.get((s,p),0)+q
            for key,known in sums.items():out['lower_bound_checks']+=1;out['lower_bound_violations']+=int(known>levels[key]);out['equal_level_quantities']+=int(known==levels[key])
            if any(q>levels[k] for k,q in sums.items()):
                blocked=True
                if out['first_mismatch'] is None:out['first_mismatch']=index
    out['prefix_blocked']=blocked;return out


def main(driver,report=None):
    fixtures=[];m,b=rows();fixtures.append((m,b))
    fixtures.append((['1,5,0,1,100,1','2,1,77,3,105,1'],[book(),[110,10,105,3,120,11,100,20,130,12,90,21,140,13,80,22,150,14,70,23]]))
    fixtures.append((['1,5,0,1,100,1','2,3,99,20,100,1'],[book(),[110,10,90,21,120,11,80,22,130,12,70,23,140,13,60,24,150,14,50,77]]))
    fixtures.append((['1,1,55,3,50,1','2,2,55,1,50,1'],[book(),book()]))
    fixtures.append((['1,2,99,1,90,1','2,1,99,2,90,1'],[book(),book()]))
    for quantity in (1,2,7,19,21,2**32-1):
        a=book(20+quantity);c=book(20)
        fixtures.append(([f'1,1,11,{quantity},100,1',f'2,4,11,{quantity},100,1'],[a,c]))
    empty=[9999999999,0,-9999999999,0]*5;one=empty.copy();one[2:4]=[100,1]
    fixtures.append((['1,5,0,1,100,1','2,1,33,1,100,1'],[empty,one]))
    canonical=hashlib.sha256();results=[]
    with tempfile.TemporaryDirectory() as temp:
        for i,(messages,books) in enumerate(fixtures):
            expected=model(messages,books);manifest,mp,bp=write(Path(temp)/str(i),messages,books);actual=run(manifest,mp,bp,driver)['statistics']
            for k,v in expected.items():assert actual[k]==v,('authored_reconstruction',i,k,v,actual[k])
            assert actual['full_l3_complete'] is False and actual['initialization']=='unknown'
            canonical.update(json.dumps(expected,sort_keys=True,separators=(',',':')).encode());results.append(expected)
    result=dict(scope='independent authored known-subset and observable reference effects',scenarios=len(fixtures),source_rows=sum(x['rows'] for x in results),canonical_sha256=canonical.hexdigest(),observed_processed=False,full_l3_complete=False,baseline=results[0])
    if report:Path(report).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='baseline'},sort_keys=True));return result

if __name__=='__main__':main(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else None)
