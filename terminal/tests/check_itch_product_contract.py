"""Real native/product → TypeScript admission. No app,listener,provider or browser."""
import json,os,socket,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
def forbidden(*_a,**_k):raise AssertionError('NO_APPLICATION_OR_NETWORK_ALLOWED')
socket.socket.bind=forbidden;socket.socket.connect=forbidden;socket.socket.connect_ex=forbidden
from terminal.server import app
assert app._application is None
app.create_app=forbidden
import gig_microstructure._native as native
from gig_microstructure.itch_recovery import ItchRecovery,ItchAdmission,ItchSourceAdmission
from terminal.itch_product import build_bundle,digest,implementation_identity,continue_source
from terminal.server.engine import NativeSession
from terminal.test_itch_product import payload,framed
with tempfile.TemporaryDirectory()as directory:
 root=Path(directory);target=root/'image'
 executable=os.environ.get('GIG_ITCH_FIXTURE',str(Path(native.__file__).parents[2]/'gig_itch_durable_checkpoint_tests'))
 result=subprocess.run([executable,'--fixture-source',str(target)],capture_output=True,text=True,check=True,timeout=30);meta=json.loads(result.stdout)
 admission=ItchAdmission(**{k:meta[k]for k in('artifact_sha256','contract_sha256','implementation_sha256','capture','generation')})
 image,admission=ItchRecovery.migrate(target.read_bytes(),admission,implementation_identity());bundle=build_bundle(image,admission,framed(payload(),payload(quantity=2)))
 session=NativeSession.restore_checkpoint(bundle,digest(bundle),implementation_identity());states=[session.state()];session.control('book',1);states.append(session.state());session.control('book',0);session.step();states.append(session.state());unit_target=root/'units';unit_run=subprocess.run([executable,'--fixture-units',str(unit_target)],capture_output=True,text=True,check=True,timeout=30);unit_meta=json.loads(unit_run.stdout);unit_a=ItchAdmission(**{k:unit_meta[k]for k in('artifact_sha256','contract_sha256','implementation_sha256','capture','generation')});unit_image,unit_a=ItchRecovery.migrate(unit_target.read_bytes(),unit_a,implementation_identity());unit_bundle=build_bundle(unit_image,unit_a);unit_session=NativeSession.restore_checkpoint(unit_bundle,digest(unit_bundle),implementation_identity());states.append(unit_session.state());source=root/'states.json';source.write_text(json.dumps(states))
 if hasattr(native,'resume_itch_source'):
  source_bytes=Path(str(target)+'.source').read_bytes();a=ItchSourceAdmission(digest(source_bytes),admission.capture,admission.generation,'binary_file',0,0);empty=build_bundle(image,admission);advanced=continue_source(empty,digest(empty),source_bytes,a);states.append(NativeSession.restore_checkpoint(advanced,digest(advanced),implementation_identity()).state());source.write_text(json.dumps(states))
 program="""import fs from 'node:fs';import assert from 'node:assert/strict';
 const {validateState}=await import(process.argv[2]);const {itchBookChoices,replayMinimum,replayProgress}=await import(process.argv[3]);const states=JSON.parse(fs.readFileSync(process.argv[4],'utf8'));let checks=0;
 const check=(v,label)=>{assert.ok(v,label);checks++};
 for(const s of states){check(validateState(s)===s,'actual native state accepted');check(s.origin==='HISTORICAL_SYNTHETIC','authored provenance');check(s.feed.real_time===false,'never live');check(s.source_timestamp_ns===null&&s.replay_time_ns===null,'no invented UTC or replay clock');check(s.capabilities.recording===false,'no observed capture');}
 check(states[0].instrument==='TEST'&&states[1].instrument==='TWO','exact independent stock selection');check(states[0].book.bids[0].quantity==='8'&&states[1].book.bids[0].quantity==='9'&&states[2].book.bids[0].quantity==='7','real native quantities');check(itchBookChoices(states[0]).map(x=>x.label).join(',')==='TEST,TWO','both readonly choices');check(replayMinimum(states[0])===9&&replayProgress(states[0])===0&&replayProgress(states[2])===50,'honest continuation boundary');check(states[3].book.bids[0].price_ticks==='99'&&states[3].book.bids[0].quantity==='100'&&states[3].metrics.midprice.numerator==='201'&&states[3].metrics.midprice.denominator==='2','exact nonunit native projection');check(states[2].position===10&&states[2].provenance.generation==='17','cursor and generation retained');assert.throws(()=>validateState({...states[0],replay_min_position:10}));checks++;assert.throws(()=>validateState({...states[0],mode:'LIVE'}));checks++;
 const restoredSources=states.filter(s=>s.provenance.source_recovery_history?.length);
 if(restoredSources.length){const s=restoredSources[0];check(s.provenance.source_recovery_history[0].to_source_records==='10'&&s.position===10,'source lineage and cursor');check(s.playing===false&&replayMinimum(s)===10&&replayProgress(s)===0,'source revision restores paused at exact hot boundary');}
 console.log(JSON.stringify({schema:'gig.itch.product_contract.v1',assertions:checks,states:states.length,source_recovery_states:restoredSources.length,application_started:false,browser_started:false}));"""
 script=root/'check.mjs';script.write_text(program)
 command=['node','--experimental-strip-types',str(script),(ROOT/'terminal/web/src/contracts.ts').as_uri(),(ROOT/'terminal/web/src/itchSession.ts').as_uri(),str(source)]
 run=subprocess.run(command,capture_output=True,text=True,timeout=30)
 if run.returncode:raise RuntimeError('authored_contract_failure:'+run.stderr[:4096])
 print(run.stdout.strip())
assert app._application is None
