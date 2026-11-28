"""Bounded explicit-file evidence reads andexclusive private result writes."""
import json
import math
import os
from pathlib import Path
import re
import stat


class EvidenceError(ValueError):
    def __init__(self,code):self.code=code;super().__init__(code)


def digest(value,size=64):
    if type(value)is not str or not re.fullmatch('[0-9a-f]{'+str(size)+'}',value):
        raise EvidenceError('invalid_digest')
    return value


def read_bytes(path,limit=1024*1024):
    path=Path(path).absolute()
    if any(p.is_symlink()for p in (path,*path.parents)):raise EvidenceError('artifact_symlink')
    try:
        fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
        try:
            before=os.fstat(fd)
            if not stat.S_ISREG(before.st_mode):raise EvidenceError('artifact_not_regular')
            if before.st_size>limit:raise EvidenceError('artifact_byte_budget')
            parts=[];remaining=before.st_size
            while remaining:
                block=os.read(fd,min(65536,remaining))
                if not block:raise EvidenceError('artifact_changed')
                parts.append(block);remaining-=len(block)
            after=os.fstat(fd)
            if (before.st_size,before.st_mtime_ns,before.st_ctime_ns)!=(after.st_size,after.st_mtime_ns,after.st_ctime_ns):
                raise EvidenceError('artifact_changed')
            return b''.join(parts)
        finally:os.close(fd)
    except EvidenceError:raise
    except OSError:raise EvidenceError('artifact_read_failed')from None


def _exact_integer(value):
    # Parse the original JSON numeric token, never a rounded binary float.
    if len(value)>128:raise EvidenceError('json_number_budget')
    match=re.fullmatch(r'(-?)([0-9]+)(?:\.([0-9]+))?(?:[eE]([+-]?[0-9]+))?',value)
    if match is None:raise EvidenceError('invalid_json_number')
    exponent=int(match[4] or '0')
    if not -128<=exponent<=128:raise EvidenceError('json_number_budget')
    fraction=match[3] or '';coefficient=int(match[2]+fraction)
    if match[1] and coefficient==0:raise EvidenceError('negative_zero_json')
    scale=exponent-len(fraction)
    if scale>=0:result=coefficient*10**scale
    else:
        result,remainder=divmod(coefficient,10**(-scale))
        if remainder:raise EvidenceError('inexact_json_number')
    if len(str(result))>128:raise EvidenceError('json_number_budget')
    return -result if match[1] else result


def decode(raw,*,numeric_policy='finite-float'):
    # Default evidence readers retain their historical finite-float behavior.
    # Source-sensitive metadata callers opt into exact integer token admission.
    if numeric_policy not in('finite-float','exact-integer'):raise EvidenceError('json_numeric_policy')
    def pairs(rows):
        out={}
        for key,value in rows:
            if key in out:raise EvidenceError('duplicate_json_field')
            out[key]=value
        return out
    def constant(_):raise EvidenceError('nonfinite_json')
    try:
        options={'parse_int':_exact_integer,'parse_float':_exact_integer}if numeric_policy=='exact-integer'else{}
        value=json.loads(raw.decode('utf-8'),object_pairs_hook=pairs,parse_constant=constant,**options)
        # Bound nested metadata before any recursive client interpretation.
        pending=[(value,0)];nodes=0
        while pending:
            item,depth=pending.pop();nodes+=1
            if depth>24 or nodes>20000:raise EvidenceError('json_structure_budget')
            if type(item)is float and not math.isfinite(item):raise EvidenceError('nonfinite_json')
            if type(item)is str:
                item.encode('utf-8')  # Escaped unpaired surrogate code points are not Unicode text.
            if type(item)is dict:
                for key,value in item.items():
                    key.encode('utf-8')
                    pending.append((value,depth+1))
            elif type(item)is list:pending.extend((v,depth+1)for v in item)
        if type(value)is not dict:raise EvidenceError('expected_json_object')
        return value
    except EvidenceError:raise
    except (UnicodeError,ValueError,RecursionError):raise EvidenceError('invalid_json')from None


def write_private(path,value,*,maximum_bytes=256*1024,compact=False):
    path=Path(path).absolute()
    if any(p.is_symlink()for p in (path,*path.parents)):raise EvidenceError('output_symlink')
    if type(maximum_bytes)is not int or not 1<=maximum_bytes<=4*1024*1024 or type(compact)is not bool:
        raise EvidenceError('output_byte_budget')
    if compact:
        raw=json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
    else:
        raw=(json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
    if len(raw)>maximum_bytes:raise EvidenceError('output_byte_budget')
    try:
        fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    except FileExistsError:raise EvidenceError('output_exists')from None
    except OSError:raise EvidenceError('output_create_failed')from None
    try:
        with os.fdopen(fd,'wb')as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
    except OSError:raise EvidenceError('output_write_failed')from None
