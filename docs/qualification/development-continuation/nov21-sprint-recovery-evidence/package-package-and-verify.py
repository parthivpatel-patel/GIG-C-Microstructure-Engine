"""Fresh safe archived source and default/streaming wheels. No network or app.

Archive explicitly refuses a dirty/wrong source. Work and outputs are new/exclusive.
Run verify only after the exact source receipt has been captured.
"""
from pathlib import Path,PurePosixPath
import argparse,hashlib,io,json,os,re,subprocess,sys,tarfile
ROOT=Path('/workspace/gig-development')
W=Path(__file__).resolve().parent
PY=ROOT/'work/venv/bin/python'
EXPECTED_GUARD=1153
EXPECTED_SOURCE=873
EXPECTED_STREAMING=33

def hashed(path):
 return {'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

def command(args,log,*,cwd=ROOT,env=None):
 with (W/log).open('x')as output:
  result=subprocess.run([str(a)for a in args],cwd=cwd,env=env,stdout=output,stderr=subprocess.STDOUT)
 if result.returncode:raise RuntimeError(f'{log}:return code {result.returncode}')
 print(json.dumps({'log':log,'status':'PASS'}),flush=True)

def archive(source,guard,accessibility):
 assert re.fullmatch('[0-9a-f]{40}',source or'')
 assert type(accessibility)is int and 1<=accessibility<=100
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==source
 assert not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT)
 counts=json.loads(next(line.partition('=')[2]for line in guard.read_text().splitlines()if line.startswith('NO_LAUNCH_COUNTS=')))
 assert counts['tests']==counts['expected']==EXPECTED_GUARD
 assert counts['errors']==counts['failures']==counts['skipped']==0
 assert not counts['application_constructed']and not counts['app_factory_allowed']and not counts['socket_attempts_allowed']
 target=W/'package-source';target.mkdir()
 raw=subprocess.check_output(['git','archive','--format=tar',source],cwd=ROOT)
 seen=set()
 with tarfile.open(fileobj=io.BytesIO(raw))as tar:
  for member in tar.getmembers():
   path=PurePosixPath(member.name)
   assert not path.is_absolute()and'..'not in path.parts and(member.isdir()or member.isfile()),member.name
   assert member.name not in seen,member.name
   seen.add(member.name)
  tar.extractall(target,filter='data')
 prior=json.loads((target/'docs/qualification/development-continuation/COMPLETION_RECOVERY_EVIDENCE.json').read_text())
 names=list(prior['clean_source_packaging']['profiles']['default']['source']['selected_names'])
 names+=['terminal.providers.test_kraken_coordinator','terminal.stocks.test_xbrl_inherited_cross_role','terminal.stocks.test_xbrl_statement_comparison']
 assert len(set(names))==len(names)and set(names)<=set(counts['selected_names'])
 assert 'terminal.test_itch_completion_capsule'not in names
 config={'schema':'gig.nov21.packaging.configuration.v1','source':source,'guard_counts':counts,
  'source_test_names':names,'expected_source_tests':EXPECTED_SOURCE,'expected_streaming_tests':EXPECTED_STREAMING,
  'expected_accounting_ui_tests':148,'expected_accessibility_tests':accessibility,'expected_ui_tests':148+accessibility,
  'fixture':str(ROOT/'build/recovery-release/gig_itch_durable_checkpoint_tests')}
 assert Path(config['fixture']).is_file()
 with(W/'configuration.json').open('x')as out:out.write(json.dumps(config,indent=2)+'\n')
 report={'source':source,'archive_sha256':hashlib.sha256(raw).hexdigest(),'members':len(seen),
  'tracked_files':len(subprocess.check_output(['git','ls-tree','-r','--name-only',source],cwd=ROOT,text=True).splitlines()),'clean_tree_at_capture':True}
 with(W/'package-source.log').open('x')as out:out.write(json.dumps(report,sort_keys=True)+'\n')
 with(W/'runtime-sha.txt').open('x')as out:out.write(source+'\n')
 print('ARCHIVE_CAPTURED='+source,flush=True)

def verify_archive(source):
 file=W/'packages/gig_microstructure-0.1.1.tar.gz'
 expected=set(subprocess.check_output(['git','ls-tree','-r','--name-only',source],cwd=ROOT,text=True).splitlines())
 target=W/'extracted';target.mkdir();seen=set();all_members=set()
 with tarfile.open(file)as tar:
  members=tar.getmembers()
  for member in members:
   path=PurePosixPath(member.name)
   assert not path.is_absolute()and'..'not in path.parts and(member.isdir()or member.isfile()),member.name
   assert member.name not in all_members,member.name
   all_members.add(member.name)
   if member.isdir():continue
   assert path.parts[0]=='gig_microstructure-0.1.1'
   name=str(PurePosixPath(*path.parts[1:]));assert name not in seen;seen.add(name)
   if name=='PKG-INFO':continue
   assert name in expected,name
   data=tar.extractfile(member).read()
   assert data==(W/'package-source'/name).read_bytes(),name
   assert data==subprocess.check_output(['git','show',source+':'+name],cwd=ROOT),name
  assert seen==expected|{'PKG-INFO'},(expected-seen,seen-expected)
  tar.extractall(target,filter='data')
 receipt={'source':source,'members':len(members),'tracked_files':len(expected),**hashed(file)}
 with(W/'archive.json').open('x')as out:out.write(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps({'archive':receipt}),flush=True)

def verify():
 config=json.loads((W/'configuration.json').read_text());source=config['source']
 package=W/'packages';package.mkdir()
 base={**os.environ,'PATH':'/workspace/gig-tools/bin:'+os.environ['PATH'],'CC':'/usr/bin/gcc','CXX':'/usr/bin/g++',
  'PIP_NO_INDEX':'1','PIP_DISABLE_PIP_VERSION_CHECK':'1','PYTHONNOUSERSITE':'1','CMAKE_BUILD_PARALLEL_LEVEL':'2',
  'CMAKE_ARGS':'-DCMAKE_MAKE_PROGRAM=/workspace/gig-tools/bin/ninja'}
 command([PY,'-m','build','--sdist','--no-isolation','--outdir',package,W/'package-source'],'sdist.log',env=base)
 verify_archive(source)
 extracted=W/'extracted/gig_microstructure-0.1.1'
 for profile in('default','streaming'):
  out=package/profile;out.mkdir();env=base.copy()
  if profile=='streaming':env['CMAKE_ARGS']+=' -DGIG_BUILD_ITCH_STREAMING=ON'
  command([PY,'-m','build','--wheel','--no-isolation','--outdir',out,extracted],profile+'-wheel.log',env=env)
  wheels=list(out.glob('*.whl'));assert len(wheels)==1
  installed=W/('installed-'+profile)
  command([PY,'-m','pip','install','--no-deps','--no-index','--target',installed,wheels[0]],profile+'-install.log',env=base)
  env={**base,'PYTHONPATH':str(installed)+':'+str(extracted),'GIG_TEST_SOURCE_COMMIT':source,
   'GIG_ITCH_FIXTURE':config['fixture'],'GIG_RECOVERY_CONFIG':str(W/'configuration.json'),'GIG_RECOVERY_INSTALLED':str(installed)}
  command([PY,W/'installed-checks.py','sdk'],profile+'-sdk.log',cwd=extracted,env=env)
  command([PY,W/'installed-checks.py','source'if profile=='default'else'streaming'],profile+'-source.log',cwd=extracted,env=env)
  if profile=='default':
   contracts={'v2':'check_xbrl_accuracy_contract.py','vintages':'check_xbrl_vintage_contract.py',
    'calculation':'check_xbrl_calculation_report_contract.py','ingress':'check_offline_import_contract.py',
    'statements':'check_statement_set_contract.py','accounting':'check_accounting_statements_contract.py'}
   for short,name in contracts.items():command([PY,extracted/'terminal/tests'/name],'installed-'+short+'.log',cwd=extracted,env=env)
   # Dependency link is added only after every source archive byte has been verified.
   (extracted/'terminal/web/node_modules').symlink_to(ROOT/'terminal/web/node_modules',target_is_directory=True)
   env['GIG_TEST_PYTHON']=str(PY)
   modules=['src/sourceAccounting.test.ts','src/sourceAccountingChecks.test.ts','src/financialSourceContract.test.ts','src/accessibilityNavigation.test.ts']
   command(['node','--experimental-strip-types','--test',*modules],'installed-source-ui.log',cwd=extracted/'terminal/web',env=env)
 records={}
 for profile in('default','streaming'):
  records[profile]={key:json.loads((W/(profile+'-'+key+'.log')).read_text().splitlines()[-1])for key in('sdk','source')}
  for result in records[profile].values():
   assert result['failures']==result['errors']==result['skipped']==0
   assert not result['application_constructed']and not result['app_factory_allowed']and not result['socket_attempts_allowed']
 contracts={short:json.loads((W/('installed-'+short+'.log')).read_text().splitlines()[-1])for short in('v2','vintages','calculation','ingress','statements','accounting')}
 ui=(W/'installed-source-ui.log').read_text();ui_count=config['expected_ui_tests']
 for name,count in [('tests',ui_count),('pass',ui_count),('fail',0),('skipped',0)]:assert re.search(r'ℹ '+name+' '+str(count)+r'\b',ui),(name,count)
 receipt={'schema':'gig.nov21.recovery.clean_source_packaging.v1','source':source,
  'archive':json.loads((W/'archive.json').read_text()),'profiles':records,
  'authored_fixture_generator':{'path':config['fixture'],**hashed(Path(config['fixture']))},
  'installed_contracts':contracts,'installed_ui':{'tests':ui_count,'passed':ui_count,'failed':0,'skipped':0,
   'source_accounting':148,'accessibility':config['expected_accessibility_tests']},
  'packages':{str(path.relative_to(package)):hashed(path)for path in sorted(package.rglob('*'))if path.is_file()},
  'logs':{path.name:hashed(path)for path in sorted(W.glob('*.log'))},
  'scope':'Fresh default and streaming GCC wheels from byte-verified source; isolated SDK and extracted-source checks. Existing locked JavaScript dependencies linked only after archive verification. External explicitly hashed fixture generates authored input only,never substitutes SDK. No full compiler-wheel matrix/browser/provider/target qualification.',
  'application_started':False,'provider_requested':False,'spend_usd':0,'progress_stream_sealed_after_exit':False}
 with(W/'packaging-verification.json').open('x')as out:out.write(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps({'receipt':str(W/'packaging-verification.json'),'source':source}),flush=True)

parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['archive','verify'])
parser.add_argument('--source');parser.add_argument('--guard-log',type=Path);parser.add_argument('--accessibility-tests',type=int)
args=parser.parse_args()
if args.stage=='archive':archive(args.source,args.guard_log,args.accessibility_tests)
else:verify()
