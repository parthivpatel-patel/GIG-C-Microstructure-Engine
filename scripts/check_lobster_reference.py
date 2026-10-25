#!/usr/bin/env python3
"""Independent authored LOBSTER parser oracle. Never opens private market files."""
from decimal import Decimal, InvalidOperation
import hashlib
import json
import re
import subprocess
import sys


def message(line):
    try:
        f=line.rstrip('\r\n').split(',')
        if len(f)!=6 or not re.fullmatch(r'[0-9]{1,5}(?:\.[0-9]{1,9})?',f[0]):return None
        ns=Decimal(f[0])*10**9
        if not 0<=ns<86400*10**9:return None
        if not all(re.fullmatch(r'[0-9]+',x) for x in f[1:4]) or not all(re.fullmatch(r'-?[0-9]+',x) for x in f[4:]):return None
        code,order,quantity,price,side=map(int,f[1:])
        if not(0<=code<2**32 and 0<=order<2**64 and 0<=quantity<2**64 and -2**63<=price<2**63 and -2**63<=side<2**63):return None
        kind={1:0,2:1,3:2,4:3,5:4,7:5}.get(code,6)
        if code==7:
            if order or quantity or side!=-1 or price not in (-1,0,1):return None
        elif code in (1,2,3,4,5):
            if quantity==0 or price<=0 or side not in (-1,1) or (code!=5 and order==0):return None
        return [int(ns),code,order,quantity,price,side,kind]
    except (ValueError,InvalidOperation):return None


def reference(line):
    fields=line.rstrip('\r\n').split(',')
    if len(fields)!=20 or not all(re.fullmatch(r'[0-9]+' if i%2 else r'-?[0-9]+',v) for i,v in enumerate(fields)):return None
    values=list(map(int,fields));levels=[];missing=0;zero=False
    for i in range(5):
        row=values[i*4:i*4+4]
        for side in (0,2):
            price,qty=row[side:side+2];sentinel=9999999999 if side==0 else -9999999999
            if not(-2**63<=price<2**63 and 0<=qty<2**64):return None
            if price==sentinel:
                if qty:return None
                missing+=1
            else:
                if price<=0 or price==9999999999:return None
                zero|=qty==0
            if i:
                old=levels[-1][side]
                if old==sentinel and price!=sentinel:return None
                if price!=sentinel and (price<=old if side==0 else price>=old):return None
        levels.append(row)
    a,b=levels[0][0],levels[0][2];both=a!=9999999999 and b!=-9999999999
    return levels+[missing,int(both and a==b),int(both and b>a),int(zero)]


def main(driver):
    plain='110,10,100,20,120,11,90,21,130,12,80,22,140,13,70,23,150,14,60,24'
    cases=[]
    for code in (1,2,3,4,5,6,7,8,2**32-1):
        for side in (-1,0,1):cases.append(('M',f'34200.123456789,{code},19,10,100,{side}'))
    for price in (-1,0,1,2):cases.append(('M',f'34200,7,0,0,{price},-1'))
    for time in ('0','86399.999999999','86400','1e2','-1','1.0000000001','1.','nan'):
        cases.append(('M',f'{time},1,1,1,100,1'))
    for order in ('0','-1',str(2**64-1),str(2**64)):
        cases.append(('M',f'1,1,{order},1,100,1'))
    cases+=[('M','1,1,1,1,100,1,2'),('M','1,1,1,1,100'),('M','1,1,1,-1,100,1'),('M','1,1,1,0,100,1')]
    cases+=[('R',plain),('R',','.join(['9999999999,0,-9999999999,0']*5))]
    for index in range(20):
        f=plain.split(',');f[index]='-1' if index%2 else '0';cases.append(('R',','.join(f)))
    for i,value in [(0,'9999999999'),(2,'9999999999'),(4,'109'),(6,'101'),(1,str(2**64)),(1,'0'),(2,'110'),(2,'115')]:
        f=plain.split(',');f[i]=value;cases.append(('R',','.join(f)))
    cases.extend([('R',plain+',0'),('R',plain.rsplit(',',1)[0])])
    cases.extend([('M','1,-0,0,0,0,0'),('M','1,5,-0,1,100,1'),('R',','.join(['9999999999,-0,-9999999999,0']*5))])
    expected=[message(row) if kind=='M' else reference(row) for kind,row in cases]
    data=''.join(k+':'+s+'\n' for k,s in cases)
    p=subprocess.run([driver,'--parser-fixtures'],input=data,text=True,capture_output=True,timeout=30)
    assert p.returncode==0 and not p.stderr,p.stderr
    actual=[json.loads(line) for line in p.stdout.splitlines()];assert len(actual)==len(expected)
    for i,(a,b) in enumerate(zip(actual,expected)):assert a==b,('authored_parser_case',i,a,b)
    digest=hashlib.sha256(json.dumps(expected,separators=(',',':')).encode()).hexdigest()
    print(json.dumps(dict(scope='authored independent LOBSTER parser',cases=len(cases),canonical_sha256=digest,observed_processed=False),sort_keys=True))
    return dict(cases=len(cases),canonical_sha256=digest)

if __name__=='__main__':main(sys.argv[1])
