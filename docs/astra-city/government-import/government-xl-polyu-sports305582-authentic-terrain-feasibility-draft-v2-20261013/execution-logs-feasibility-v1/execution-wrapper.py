from pathlib import Path
import hashlib,json,subprocess,datetime,sys,os
R=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city');H=R/'source-scripts/city/government-import';D=R/'docs/astra-city/government-import/government-xl-polyu-sports305582-authentic-terrain-feasibility-draft-v2-20261013';C=H/'xl-polyu-sports305582-authentic-terrain-feasibility-draft-v2-20261013.py';O=D/'execution-logs-feasibility-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return dict(path=str(p.relative_to(R)),sha256=sha(p))
def save(p,x):
 with p.open('x')as f:json.dump(x,f,sort_keys=True,indent=2);f.write('\n')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
assert sha(C)=='5c1d38ba5dd253011f6c9e0e29c40f502baf3e5b9dd86a4dea1b5202521fab65';assert not (D/'calculation-v1').exists();O.mkdir()
(O/'execution-wrapper.py').write_bytes(Path(__file__).read_bytes());prep=D/'actual-readonly-preparation-v1/validation.json';v=json.loads(prep.read_text());assert sha(prep)=='980ae40818f142fd33101de817c43a0c03acbecbe26c755af685f1dea1ce2cea'and v['allPassed']
pins={p['path']:p['sha256']for p in v['beforeEndLiteralPins']+v['transitiveImportedCodePins']}
for p,h in pins.items():assert sha(R/p)==h,p
argv=['/tmp/astra-city-venv/bin/python','-u',str(C),'--calculate-authentic-source-feasibility-only'];start=now()
with(O/'execution.log').open('x')as log:
 p=subprocess.Popen(argv,cwd=R,stdout=log,stderr=subprocess.STDOUT)
 launch=dict(argv=argv,wrapperPID=os.getpid(),producerPID=p.pid,startedAt=start,noDB=True,noLease=True,caller=ref(C),prep=ref(prep),beforeEndPins=[dict(path=p,sha256=h)for p,h in sorted(pins.items())])
 save(O/'launch.json',launch);print(json.dumps(dict(wrapperPID=os.getpid(),producerPID=p.pid,startedAt=start)),flush=True);exitcode=p.wait()
actual_end=[dict(path=p,expectedSHA256=h,actualSHA256=sha(R/p),unchanged=sha(R/p)==h)for p,h in sorted(pins.items())]
terminal=dict(exitCode=exitcode,startedAt=start,endedAt=now(),wrapperPID=os.getpid(),producerPID=p.pid,producerAbsent=not Path('/proc',str(p.pid)).exists(),allLiteralPinsUnchanged=all(p['unchanged']for p in actual_end),beforeEndPinCount=len(pins),currentManifestSHA256=sha(R/'3d-viewer/city/data/manifest.json'),log=ref(O/'execution.log'),caller=ref(C),noDB=True,noLease=True)
save(O/'terminal.json',terminal);save(O/'actual-end-input-pins.json',actual_end);print(json.dumps(terminal),flush=True);sys.exit(exitcode if exitcode else (0 if terminal['allLiteralPinsUnchanged']else 1))
