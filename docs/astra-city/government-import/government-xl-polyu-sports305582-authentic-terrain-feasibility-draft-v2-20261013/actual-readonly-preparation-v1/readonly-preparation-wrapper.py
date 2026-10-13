from pathlib import Path
import hashlib,json,subprocess,sys
R=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city');H=R/'source-scripts/city/government-import';D=R/'docs/astra-city/government-import/government-xl-polyu-sports305582-authentic-terrain-feasibility-draft-v2-20261013';C=H/'xl-polyu-sports305582-authentic-terrain-feasibility-draft-v2-20261013.py';O=D/'actual-readonly-preparation-v1';O.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return dict(path=str(p.relative_to(R)),sha256=sha(p))
def save(p,x):
 with p.open('x')as f:json.dump(x,f,sort_keys=True,indent=2);f.write('\n')
local=O/'readonly-preparation-wrapper.py';local.write_bytes(Path(__file__).read_bytes())
pins=json.loads((D/'review-file-pins.json').read_text())['filePins']+[ref(D/'review-file-pins.json'),ref(local)];assert len(pins)==7555
for p in pins:assert sha(R/p['path'])==p['sha256'],p['path']
assert sha(C)=='5c1d38ba5dd253011f6c9e0e29c40f502baf3e5b9dd86a4dea1b5202521fab65'
importcode="""import sys,importlib.util,json,hashlib,types;from pathlib import Path
R=Path(%r);H=R/'source-scripts/city/government-import';sys.path.insert(0,str(H));s=importlib.util.spec_from_file_location('reviewed_polyu_authentic_feasibility',%r);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
queue=list(sys.modules.values())+[m];seen=set();files=set()
while queue:
 q=queue.pop()
 if not isinstance(q,types.ModuleType)or id(q)in seen:continue
 seen.add(id(q));name=getattr(q,'__file__',None)
 if not name:continue
 p=Path(name).resolve()
 if R not in p.parents or not p.is_file():continue
 files.add(p);queue.extend(v for v in vars(q).values()if isinstance(v,types.ModuleType))
print(json.dumps(dict(importPassed=True,noMainExecuted=True,completeImportedLocalCodePins=[dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())for p in sorted(files)])))
"""%(str(R),str(C))
results=[]
for name,argv in [('import',['/tmp/astra-city-venv/bin/python','-c',importcode]),('preflight',['/tmp/astra-city-venv/bin/python',str(C),'--preflight-only'])]:
 with(O/(name+'.log')).open('x')as log:q=subprocess.run(argv,cwd=R,stdout=log,stderr=subprocess.STDOUT)
 results.append(dict(name=name,argv=argv,exitCode=q.returncode,log=ref(O/(name+'.log'))));print(json.dumps(results[-1]),flush=True)
 if q.returncode!=0:break
for pin in pins:assert sha(R/pin['path'])==pin['sha256'],pin['path']
imports=[];preflight=None
if results[0]['exitCode']==0:imports=json.loads((O/'import.log').read_text())['completeImportedLocalCodePins']
if len(results)==2 and results[1]['exitCode']==0:
 preflight=json.loads((O/'preflight.log').read_text());imports+=preflight['importedCodePins']
imports=sorted({p['path']:p for p in imports}.values(),key=lambda p:p['path'])
for p in imports:assert sha(R/p['path'])==p['sha256'],p['path']
validation=dict(allPassed=len(results)==2 and all(q['exitCode']==0 for q in results),noDB=True,noLease=True,noTerrainDecode=True,noNumericalPredicates=True,beforeEndLiteralPins=pins,transitiveImportedCodePins=imports,commands=results,actualPreflight=preflight,currentManifestSHA256=sha(R/'3d-viewer/city/data/manifest.json'),noCalculationOutput=(not(D/'calculation-v1').exists()))
save(O/'validation.json',validation);print(json.dumps(dict(allPassed=validation['allPassed'],literalPins=len(pins),importedCodePins=len(imports),validation=ref(O/'validation.json'))),flush=True)
raise SystemExit(0 if validation['allPassed']else 1)
