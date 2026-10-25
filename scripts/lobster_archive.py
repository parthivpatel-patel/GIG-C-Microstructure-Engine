#!/usr/bin/env python3
"""Permission-gated bounded archive inspection/extraction; no network or row analysis."""
import hashlib
import json
from pathlib import Path,PurePosixPath
import shutil
import stat
import struct
import tempfile
import time
import zipfile
from run_lobster_validation import validate_manifest,ROOT


def inspect(path,manifest,expected_sha256,output=None):
    validate_manifest(manifest)
    if manifest['origin']=='observed' and not manifest['permission']['cloud_processing_approved']:
        return dict(status='BLOCKED_PERMISSION',input_opened=False)
    if manifest['origin']=='observed' and (Path(path).resolve().is_relative_to(ROOT) or (output is not None and Path(output).resolve().is_relative_to(ROOT))):raise ValueError('private archive/data must remain outside Git')
    if output is not None and Path(output).exists():raise ValueError('private output already exists')
    start=time.monotonic();staging=None;total=0
    try:
        with tempfile.TemporaryFile() as snapshot:
            archive_hash=hashlib.sha256();compressed=0
            with Path(path).open('rb') as src:
                while block:=src.read(65536):
                    compressed+=len(block)
                    if compressed>32*1024*1024:raise ValueError('archive byte budget')
                    if time.monotonic()-start>30:raise ValueError('archive deadline')
                    snapshot.write(block);archive_hash.update(block)
            if archive_hash.hexdigest()!=expected_sha256:raise ValueError('archive hash')
            snapshot.seek(max(0,compressed-65557));tail=snapshot.read(65557);at=tail.rfind(b'PK\x05\x06')
            if at<0 or len(tail)-at<22:raise ValueError('ZIP end record')
            disk,cd_disk,local_count,count,cd_bytes,cd_offset,comment=struct.unpack_from('<HHHHIIH',tail,at+4)
            if disk or cd_disk or local_count!=count or not 1<=count<=32 or cd_bytes>1024*1024 or at+22+comment!=len(tail) or cd_offset+cd_bytes>compressed-len(tail)+at:raise ValueError('bounded single-disk central directory')
            if output is not None:
                target=Path(output);target.parent.mkdir(parents=True,exist_ok=True)
                staging=Path(tempfile.mkdtemp(prefix='.lobster-staging-',dir=target.parent));staging.chmod(0o700)
            snapshot.seek(0);seen=set();members=[]
            with zipfile.ZipFile(snapshot) as z:
                infos=z.infolist()
                if len(infos)!=count:raise ValueError('directory count')
                for info in infos:
                    name=PurePosixPath(info.filename);mode=info.external_attr>>16;normalized=str(name).casefold()
                    if name.is_absolute() or '..' in name.parts or '\\' in info.filename or ':' in info.filename or '\0' in info.filename or len(info.filename)>255 or normalized in seen or info.is_dir() or (stat.S_IFMT(mode) not in (0,stat.S_IFREG)) or info.flag_bits&1 or info.compress_type not in (zipfile.ZIP_STORED,zipfile.ZIP_DEFLATED):raise ValueError('unsafe archive member')
                    seen.add(normalized)
                    if info.file_size>64*1024*1024 or info.file_size/max(1,info.compress_size)>200:raise ValueError('member expansion budget')
                    total+=info.file_size
                    if total>128*1024*1024:raise ValueError('archive expansion budget')
                    count_bytes=0;h=hashlib.sha256();writer=None
                    try:
                        if staging:
                            dest=staging.joinpath(*name.parts);dest.parent.mkdir(parents=True,exist_ok=True);writer=dest.open('xb');dest.chmod(0o600)
                        with z.open(info) as f:
                            while data:=f.read(65536):
                                count_bytes+=len(data)
                                if count_bytes>info.file_size or time.monotonic()-start>30:raise ValueError('member/deadline budget')
                                h.update(data)
                                if writer:writer.write(data)
                    finally:
                        if writer:writer.close()
                    if count_bytes!=info.file_size:raise ValueError('member size')
                    members.append(dict(filename=info.filename,bytes=count_bytes,sha256=h.hexdigest(),crc_verified=True))
            if staging:
                if Path(output).exists():raise ValueError('output appeared during extraction')
                staging.rename(output);staging=None
            return dict(status='INTEGRITY_VERIFIED',origin=manifest['origin'],archive_sha256=archive_hash.hexdigest(),archive_bytes=compressed,uncompressed_bytes=total,members=members,extracted=output is not None)
    except zipfile.BadZipFile:
        raise ValueError('ZIP structure/CRC refusal') from None
    finally:
        if staging:shutil.rmtree(staging)


def main():
    import argparse
    from run_lobster_validation import load_manifest
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('manifest');p.add_argument('archive');p.add_argument('--sha256',required=True);p.add_argument('--extract-to');p.add_argument('--report');a=p.parse_args()
    try:
        m=load_manifest(a.manifest)
        if m['origin']=='observed' and a.report and Path(a.report).resolve().is_relative_to(ROOT):raise ValueError('private report must remain outside Git')
        result=inspect(a.archive,m,a.sha256,a.extract_to)
        if a.report:
            with Path(a.report).open('xb') as f:f.write((json.dumps(result,sort_keys=True,indent=2)+'\n').encode())
        print(json.dumps(result,sort_keys=True));return 2 if result['status']=='BLOCKED_PERMISSION' else 0
    except (ValueError,OSError,KeyError,TypeError,RecursionError) as e:p.exit(2,'archive refused: '+str(e)+'\n')

if __name__=='__main__':raise SystemExit(main())
