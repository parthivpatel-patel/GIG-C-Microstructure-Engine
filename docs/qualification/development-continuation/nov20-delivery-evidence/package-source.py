from pathlib import Path,PurePosixPath
import subprocess,tarfile,io,json,hashlib
w=Path('work/nov20-delivery');source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
assert source=='9be1c0d8293444e517af67fe2a57fd1be599277c'
assert not subprocess.check_output(['git','status','--porcelain'])
(w/'runtime-sha.txt').write_text(source+'\n');target=w/'package-source';target.mkdir()
archive=subprocess.check_output(['git','archive','--format=tar',source])
seen=set()
with tarfile.open(fileobj=io.BytesIO(archive))as t:
 for member in t.getmembers():
  path=PurePosixPath(member.name)
  assert not path.is_absolute()and'..'not in path.parts and(member.isdir()or member.isfile()),member.name
  assert member.name not in seen,member.name
  seen.add(member.name)
 t.extractall(target,filter='data')
print(json.dumps({'source':source,'archive_sha256':hashlib.sha256(archive).hexdigest(),'members':len(seen),'target':str(target)}))
