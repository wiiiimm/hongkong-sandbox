from pathlib import Path
import hashlib,json,subprocess,datetime,sys,os
R=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city');H=R/'source-scripts/city/government-import';D=R/'docs/astra-city/government-import/government-xl-polyu-sports305582-authentic-terrain-feasibility-draft-v2-20261013/receipt-only-freezer-draft-v2';C=H/'xl-polyu-sports305582-authentic-terrain-feasibility-receipt-only-freeze-draft-v2-20261013.py';O=D/'execution-logs-freeze-v1';BATCH='government-xl-polyu-sports305582-authentic-terrain-feasibility-source-context-v2-20261013'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return dict(path=str(p.relative_to(R)),sha256=sha(p))
def save(p,x):
 with p.open('x')as f:json.dump(x,f,sort_keys=True,indent=2);f.write('\n')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
assert sha(C)=='41162f2f533eee77fa4907354b4e087a748123f23416d65f6ec4e3903e9bf3c5'and not (R/'docs/astra-city/government-import'/BATCH).exists();O.mkdir();(O/'execution-wrapper.py').write_bytes(Path(__file__).read_bytes())
prep=D/'actual-readonly-preparation-v1/validation.json';v=json.loads(prep.read_text());assert sha(prep)=='836be9573477058b434949a5aa686f724f3a3b7d0e83df5a05c396685a89d512'and v['allPassed'];pins={p['path']:p['sha256']for p in v['beforeEndLiteralPins']+v['transitiveImportedCodePins']}
for p,h in pins.items():assert sha(R/p)==h,p
argv=['/tmp/astra-city-venv/bin/python','-u',str(C)];start=now()
with(O/'execution.log').open('x')as log:
 p=subprocess.Popen(argv,cwd=R,stdout=log,stderr=subprocess.STDOUT);save(O/'launch.json',dict(argv=argv,wrapperPID=os.getpid(),producerPID=p.pid,startedAt=start,batch=BATCH,caller=ref(C),prep=ref(prep)));print(json.dumps(dict(wrapperPID=os.getpid(),producerPID=p.pid,startedAt=start,batch=BATCH)),flush=True);exitcode=p.wait()
end=[dict(path=p,expectedSHA256=h,actualSHA256=sha(R/p),unchanged=sha(R/p)==h)for p,h in sorted(pins.items())]
terminal=dict(exitCode=exitcode,startedAt=start,endedAt=now(),wrapperPID=os.getpid(),producerPID=p.pid,producerAbsent=not Path('/proc',str(p.pid)).exists(),allLiteralPinsUnchanged=all(p['unchanged']for p in end),beforeEndPinCount=len(pins),currentManifestSHA256=sha(R/'3d-viewer/city/data/manifest.json'),log=ref(O/'execution.log'),caller=ref(C),batch=BATCH,receiptOnly=True,noNumericalReplay=True)
save(O/'actual-end-input-pins.json',end);save(O/'terminal.json',terminal);print(json.dumps(terminal),flush=True);sys.exit(exitcode if exitcode else (0 if terminal['allLiteralPinsUnchanged']else 1))
