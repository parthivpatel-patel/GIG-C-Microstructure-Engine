import copy
import hashlib
import io
import json
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
import zipfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from lobster_synthetic import rows,write,manifest
import run_lobster_validation as runner
import lobster_archive
DRIVER=sys.argv.pop(1) if len(sys.argv)>1 else str(ROOT/'build/phase9-clean-debug/gig_lobster_validate')

class Workflow(unittest.TestCase):
    def setUp(self):self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name);self.messages,self.books=rows()
    def execute(self,messages=None,books=None,**kwargs):
        m,mp,bp=write(self.root/str(len(list(self.root.iterdir()))),self.messages if messages is None else messages,self.books if books is None else books)
        return runner.run(m,mp,bp,DRIVER,**kwargs)
    def test_baseline(self):
        out=self.execute();s=out['statistics'];self.assertEqual((s['rows'],s['native'],s['unknown_order'],s['unsupported'],s['blocked']),(10,5,1,1,1));self.assertEqual((s['quantity_eligible'],s['quantity_matches'],s['depth_eligible'],s['depth_matches']),(6,6,8,8));self.assertEqual(s['lower_bound_violations'],0);self.assertFalse(s['full_l3_complete']);self.assertEqual(s['shares_min'],0);self.assertEqual(s['shares_max'],10);self.assertEqual(sum(s['share_histogram']),10)
    def test_permission_closed_before_file_access(self):
        m=manifest(b'',b'');m['origin']='observed';r=runner.run(m,'not-opened-messages','not-opened-reference','not-executed-driver');self.assertEqual(r['status'],'BLOCKED_PERMISSION');self.assertIs(r['input_opened'],False)
        r=lobster_archive.inspect('not-opened.zip',m,'0'*64);self.assertFalse(r['input_opened'])
    def test_false_initialization(self):
        m=manifest(b'',b'');m['initialization']='complete'
        with self.assertRaises(ValueError):runner.run(m,'not-opened','not-opened','not-executed')
    def test_missing_duplicate_events(self):
        m=self.messages[:1]+self.messages[2:];b=self.books[:1]+self.books[2:];s=self.execute(m,b)['statistics'];self.assertIsNotNone(s['first_mismatch'])
        m=self.messages[:2]+[self.messages[1]]+self.messages[2:];b=self.books[:2]+[self.books[1]]+self.books[2:];s=self.execute(m,b)['statistics'];self.assertGreater(s['inconsistent'],0);self.assertIsNotNone(s['first_mismatch'])
    def test_quantity_price_type_mutations(self):
        for index,value in ((3,'6'),(4,'101'),(1,'5')):
            m=self.messages.copy();f=m[1].split(',');f[index]=value;m[1]=','.join(f);s=self.execute(m,self.books)['statistics'];self.assertIsNotNone(s['first_mismatch'])
    def test_timestamp_and_corrupt_reference(self):
        m=self.messages.copy();m[1]='0,'+m[1].split(',',1)[1]
        with self.assertRaisesRegex(ValueError,'row_index=1'):self.execute(m,self.books)
        b=copy.deepcopy(self.books);b[1][4]=109
        with self.assertRaises(ValueError):self.execute(self.messages,b)
    def test_alignment_shift_and_missing_line(self):
        b=self.books[1:]+self.books[:1];s=self.execute(self.messages,b)['statistics'];self.assertIsNotNone(s['first_mismatch'])
        with self.assertRaises(ValueError):self.execute(self.messages,self.books[:-1])
    def test_missing_order_reference(self):
        m=self.messages.copy();f=m[2].split(',');f[2]='888';m[2]=','.join(f);s=self.execute(m,self.books)['statistics'];self.assertGreaterEqual(s['unknown_order'],1);self.assertEqual(s['first_unknown_order'],2);self.assertGreater(s['inconsistent'],0)
    def test_limits(self):
        for kwargs in (dict(max_rows=1),dict(max_bytes=20),dict(max_memory=4096),dict(max_line=10)):
            with self.assertRaises(ValueError):self.execute(**kwargs)
    def test_checksums(self):
        m,mp,bp=write(self.root/'hash',self.messages,self.books);m['message_sha256']='0'*64
        with self.assertRaises(ValueError):runner.run(m,mp,bp,DRIVER)
    def test_determinism(self):
        a=self.execute()['statistics'];b=self.execute()['statistics']
        for field in ('analysis_ns','pmr_peak_bytes','allocations'):a.pop(field);b.pop(field)
        self.assertEqual(a,b)
    def test_safe_zip_and_extraction(self):
        p=self.root/'authored.zip'
        with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:z.writestr('authored.txt','independently authored archive')
        m=manifest(b'',b'');sha=hashlib.sha256(p.read_bytes()).hexdigest();out=self.root/'extracted';r=lobster_archive.inspect(p,m,sha,out);self.assertEqual(r['status'],'INTEGRITY_VERIFIED');self.assertEqual((out/'authored.txt').read_text(),'independently authored archive')
        with self.assertRaises(ValueError):lobster_archive.inspect(p,m,sha,out)
    def test_zip_paths_symlinks_ratio_crc(self):
        for i,name in enumerate(('../escape','/escape','C:escape','a\\b')):
            p=self.root/f'bad{i}.zip'
            with zipfile.ZipFile(p,'w') as z:z.writestr(name,'authored')
            with self.assertRaises(ValueError):lobster_archive.inspect(p,manifest(b'',b''),hashlib.sha256(p.read_bytes()).hexdigest())
        p=self.root/'link.zip'
        with zipfile.ZipFile(p,'w') as z:
            item=zipfile.ZipInfo('link');item.external_attr=(stat.S_IFLNK|0o777)<<16;z.writestr(item,'target')
        with self.assertRaises(ValueError):lobster_archive.inspect(p,manifest(b'',b''),hashlib.sha256(p.read_bytes()).hexdigest())
        p=self.root/'crc.zip'
        with zipfile.ZipFile(p,'w',zipfile.ZIP_STORED) as z:z.writestr('authored.txt','authored-crc-marker')
        data=bytearray(p.read_bytes());at=data.index(b'authored-crc-marker');data[at]^=1;p.write_bytes(data)
        output=self.root/'must-not-publish'
        with self.assertRaises(ValueError):lobster_archive.inspect(p,manifest(b'',b''),hashlib.sha256(data).hexdigest(),output)
        self.assertFalse(output.exists());self.assertFalse(list(self.root.glob('.lobster-staging-*')))
        p=self.root/'ratio.zip'
        with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:z.writestr('expansion','0'*100000)
        with self.assertRaises(ValueError):lobster_archive.inspect(p,manifest(b'',b''),hashlib.sha256(p.read_bytes()).hexdigest())

if __name__=='__main__':unittest.main()
