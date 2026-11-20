from pathlib import Path,PurePosixPath
import subprocess,tarfile,hashlib,json
w=Path('work/nov20-delivery');source=(w/'runtime-sha.txt').read_text().strip();archive=w/'packages/gig_microstructure-0.1.1.tar.gz';expected=set(subprocess.check_output(['git','ls-tree','-r','--name-only',source],text=True).splitlines());seen=set();all_members=set();target=w/'extracted';target.mkdir()
with tarfile.open(archive)as t:
 members=t.getmembers()
 for member in members:
  path=PurePosixPath(member.name);assert not path.is_absolute()and'..'not in path.parts and(member.isdir()or member.isfile()),member.name
  assert member.name not in all_members,member.name;all_members.add(member.name)
  if member.isdir():continue
  assert path.parts[0]=='gig_microstructure-0.1.1'
  name=str(PurePosixPath(*path.parts[1:]));assert name not in seen;seen.add(name)
  if name=='PKG-INFO':continue
  assert name in expected,name
  raw=t.extractfile(member).read()
  assert raw==(w/'package-source'/name).read_bytes(),name
  assert raw==subprocess.check_output(['git','show',source+':'+name]),name
 assert seen==expected|{'PKG-INFO'},(expected-seen,seen-expected)
 t.extractall(target,filter='data')
data=archive.read_bytes();receipt={'source':source,'members':len(members),'tracked_files':len(expected),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()};(w/'archive.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
