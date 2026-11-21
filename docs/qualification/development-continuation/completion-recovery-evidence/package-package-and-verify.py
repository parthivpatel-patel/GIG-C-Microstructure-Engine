"""Fresh safe source archive and two isolated SDK profiles; no network or app."""
from pathlib import Path,PurePosixPath
import argparse,hashlib,io,json,os,re,subprocess,sys,tarfile
ROOT=Path('/workspace/gig-development');W=ROOT/'work/completion-final';PY=ROOT/'work/venv/bin/python'
def hashed(p):return {'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def command(args,log,*,cwd=ROOT,env=None):
 with (W/log).open('x')as output:
  r=subprocess.run([str(a)for a in args],cwd=cwd,env=env,stdout=output,stderr=subprocess.STDOUT)
 if r.returncode:raise RuntimeError(f'{log}: return code {r.returncode}')
 print(json.dumps({'log':log,'status':'PASS'}),flush=True)
def archive(source,guard):
 assert re.fullmatch('[0-9a-f]{40}',source)
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==source
 assert not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT)
 counts=json.loads(next(line.partition('=')[2]for line in guard.read_text().splitlines()if line.startswith('NO_LAUNCH_COUNTS=')))
 assert counts['tests']==counts['expected'] and counts['errors']==counts['failures']==counts['skipped']==0 and not counts['application_constructed']
 target=W/'package-source';target.mkdir();raw=subprocess.check_output(['git','archive','--format=tar',source],cwd=ROOT)
 seen=set()
 with tarfile.open(fileobj=io.BytesIO(raw))as t:
  for m in t.getmembers():
   p=PurePosixPath(m.name);assert not p.is_absolute()and'..'not in p.parts and(m.isdir()or m.isfile()),m.name
   assert m.name not in seen,m.name;seen.add(m.name)
  t.extractall(target,filter='data')
 known=json.loads((ROOT/'docs/qualification/development-continuation/NOV20_DELIVERY_EVIDENCE.json').read_text())['clean_source_packaging']['installed_source']['selected_names']
 names=[*known,'terminal.stocks.test_xbrl_cross_role','terminal.providers.test_kraken_public_session']
 assert len(set(names))==len(names) and set(names)<=set(counts['selected_names'])
 config={'source':source,'guard_counts':counts,'source_test_names':names,'expected_source_tests':773,'expected_streaming_tests':30,'fixture':str(ROOT/'build/recovery-release/gig_itch_durable_checkpoint_tests')}
 (W/'configuration.json').write_text(json.dumps(config,indent=2)+'\n')
 (W/'package-source.log').write_text(json.dumps({'source':source,'archive_sha256':hashlib.sha256(raw).hexdigest(),'members':len(seen),'tracked_files':len(subprocess.check_output(['git','ls-tree','-r','--name-only',source],cwd=ROOT,text=True).splitlines()),'clean_tree_at_capture':True},sort_keys=True)+'\n')
 (W/'runtime-sha.txt').write_text(source+'\n');print('ARCHIVE_CAPTURED='+source,flush=True)
def verify_archive(source):
 file=W/'packages/gig_microstructure-0.1.1.tar.gz';expected=set(subprocess.check_output(['git','ls-tree','-r','--name-only',source],cwd=ROOT,text=True).splitlines());target=W/'extracted';target.mkdir();seen=set();memberset=set()
 with tarfile.open(file)as t:
  members=t.getmembers()
  for m in members:
   p=PurePosixPath(m.name);assert not p.is_absolute()and'..'not in p.parts and(m.isdir()or m.isfile()),m.name
   assert m.name not in memberset,m.name;memberset.add(m.name)
   if m.isdir():continue
   assert p.parts[0]=='gig_microstructure-0.1.1';name=str(PurePosixPath(*p.parts[1:]));assert name not in seen;seen.add(name)
   if name=='PKG-INFO':continue
   assert name in expected,name
   raw=t.extractfile(m).read();assert raw==(W/'package-source'/name).read_bytes(),name
   assert raw==subprocess.check_output(['git','show',source+':'+name],cwd=ROOT),name
  assert seen==expected|{'PKG-INFO'},(expected-seen,seen-expected)
  t.extractall(target,filter='data')
 receipt={'source':source,'members':len(members),'tracked_files':len(expected),**hashed(file)}
 (W/'archive.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'archive':receipt}),flush=True)
def verify():
 config=json.loads((W/'configuration.json').read_text());source=config['source'];package=W/'packages';package.mkdir()
 base={**os.environ,'PATH':'/workspace/gig-tools/bin:'+os.environ['PATH'],'CC':'/usr/bin/gcc','CXX':'/usr/bin/g++','PIP_NO_INDEX':'1','CMAKE_ARGS':'-DCMAKE_MAKE_PROGRAM=/workspace/gig-tools/bin/ninja'}
 command([PY,'-m','build','--sdist','--no-isolation','--outdir',package,W/'package-source'],'sdist.log',env=base)
 verify_archive(source);extracted=W/'extracted/gig_microstructure-0.1.1'
 for profile in('default','streaming'):
  out=package/profile;out.mkdir();env=base.copy()
  if profile=='streaming':env['CMAKE_ARGS']+=' -DGIG_BUILD_ITCH_STREAMING=ON'
  command([PY,'-m','build','--wheel','--no-isolation','--outdir',out,extracted],profile+'-wheel.log',env=env)
  wheels=list(out.glob('*.whl'));assert len(wheels)==1
  installed=W/('installed-'+profile)
  command([PY,'-m','pip','install','--no-deps','--no-index','--target',installed,wheels[0]],profile+'-install.log',env=base)
  env={**base,'PYTHONPATH':str(installed)+':'+str(extracted),'GIG_TEST_SOURCE_COMMIT':source,'GIG_ITCH_FIXTURE':config['fixture'],'GIG_COMPLETION_CONFIG':str(W/'configuration.json'),'GIG_COMPLETION_INSTALLED':str(installed)}
  command([PY,W/'installed-checks.py','sdk'],profile+'-sdk.log',cwd=extracted,env=env)
  command([PY,W/'installed-checks.py','source'if profile=='default'else'streaming'],profile+'-source.log',cwd=extracted,env=env)
  if profile=='default':
   contracts={'v2':'check_xbrl_accuracy_contract.py','vintages':'check_xbrl_vintage_contract.py','calculation':'check_xbrl_calculation_report_contract.py','ingress':'check_offline_import_contract.py','statements':'check_statement_set_contract.py','accounting':'check_accounting_statements_contract.py'}
   for short,name in contracts.items():command([PY,extracted/'terminal/tests'/name],'installed-'+short+'.log',cwd=extracted,env=env)
   (extracted/'terminal/web/node_modules').symlink_to(ROOT/'terminal/web/node_modules',target_is_directory=True)
   env['GIG_TEST_PYTHON']=str(PY)
   command(['node','--experimental-strip-types','--test','src/sourceAccounting.test.ts','src/sourceAccountingChecks.test.ts','src/financialSourceContract.test.ts'],'installed-source-ui.log',cwd=extracted/'terminal/web',env=env)
 records={}
 for profile in('default','streaming'):
  records[profile]={key:json.loads((W/(profile+'-'+key+'.log')).read_text().splitlines()[-1])for key in('sdk','source')}
  for result in records[profile].values():assert result['failures']==result['errors']==result['skipped']==0 and not result['application_constructed']
 contracts={short:json.loads((W/('installed-'+short+'.log')).read_text().splitlines()[-1])for short in('v2','vintages','calculation','ingress','statements','accounting')}
 ui=(W/'installed-source-ui.log').read_text();assert re.search(r'ℹ tests 148\b',ui)and re.search(r'ℹ pass 148\b',ui)and re.search(r'ℹ fail 0\b',ui)and re.search(r'ℹ skipped 0\b',ui)
 receipt={'schema':'gig.completion.clean_source_packaging.v1','source':source,'archive':json.loads((W/'archive.json').read_text()),'profiles':records,'authored_fixture_generator':{'path':config['fixture'],**hashed(Path(config['fixture']))},'installed_contracts':contracts,'installed_ui':{'tests':148,'passed':148,'failed':0,'skipped':0},'packages':{str(p.relative_to(package)):hashed(p)for p in sorted(package.rglob('*'))if p.is_file()},'logs':{p.name:hashed(p)for p in sorted(W.glob('*.log'))},'scope':'Fresh default and streaming GCC wheels from safe byte-verified source; installed Python consumers and extracted-source contracts/UI; existing locked JS dependencies linked only after archive validation. External fixture executable generates authored native source only,never substitutes SDK. No full compiler matrix/browser/provider/target qualification.','application_started':False,'provider_requested':False,'spend_usd':0}
 (W/'packaging-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'receipt':str(W/'packaging-verification.json'),'source':source}),flush=True)
p=argparse.ArgumentParser();p.add_argument('stage',choices=['archive','verify']);p.add_argument('--source');p.add_argument('--guard-log',type=Path);a=p.parse_args()
if a.stage=='archive':archive(a.source,a.guard_log)
else:verify()
