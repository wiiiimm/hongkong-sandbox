from pathlib import Path
import ast,json,hashlib,subprocess,datetime,sys
R=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city');H=R/'source-scripts/city/government-import';D=R/'docs/astra-city/government-import/government-xl-southside-private-authentic-terrain-draft-v2-20261012/selective13-parent-restoration-draft-v1/certified-width-constructor-draft-v1/domain-first-exact-union-construction-draft-v4';O=D/'immutable-fixtures-and-import-v1';O.mkdir(exist_ok=False);PY='/tmp/astra-city-venv/bin/python';helper=H/'southside_domain_first_exact_core_union_construction_draft_v4_20261013.py';test=H/'test_southside_domain_first_exact_core_union_construction_draft_v4_20261013.py'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pins={}
def walk(value):
 if isinstance(value,dict):
  if 'path'in value and 'sha256'in value:
   assert value['path']not in pins or pins[value['path']]==value['sha256'];pins[value['path']]=value['sha256']
  for v in value.values():walk(v)
 elif isinstance(value,list):
  for v in value:walk(v)
walk(json.loads((D/'review-pins.json').read_bytes()));pins[str((D/'review-pins.json').relative_to(R))]=sha(D/'review-pins.json')
seen=set();dirs=[H,H.parent/'shared-modelling']
def collect(p):
 p=p.resolve()
 if p in seen:return
 seen.add(p);pins[str(p.relative_to(R))]=sha(p)
 for n in ast.walk(ast.parse(p.read_bytes())):
  names=[x.name for x in n.names]if isinstance(n,ast.Import)else [n.module]if isinstance(n,ast.ImportFrom)and n.module else []
  for name in names:
   for d in dirs:
    candidate=d/(name.replace('.','/')+'.py')
    if candidate.is_file():collect(candidate);break
collect(helper);collect(test)
for p,h in pins.items():assert sha(R/p)==h,p
before=[dict(path=p,sha256=h)for p,h in sorted(pins.items())];(O/'actual-before-pins.json').write_text(json.dumps(before,indent=2)+'\n')
code="import sys,importlib.util,json,hashlib;from pathlib import Path;sys.path.insert(0,"+repr(str(H))+");p=Path("+repr(str(helper))+");s=importlib.util.spec_from_file_location('reviewed_south_domain_first_v4',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);r=Path("+repr(str(R))+");rows=[{'path':str(Path(x.__file__).resolve().relative_to(r)),'sha256':hashlib.sha256(Path(x.__file__).resolve().read_bytes()).hexdigest()}for x in list(sys.modules.values())if getattr(x,'__file__',None)and Path(x.__file__).resolve().is_relative_to(r)and Path(x.__file__).resolve().is_file()];print(json.dumps(rows,sort_keys=True))"
a=subprocess.run([PY,'-c',code],cwd=R,capture_output=True,text=True);(O/'import.log').write_text(a.stdout+a.stderr)
if a.returncode==0:
 imported=json.loads(a.stdout);assert all(pins[r['path']]==r['sha256']for r in imported)
else:imported=[]
r=subprocess.run([PY,'-m','unittest','discover','-s',str(H),'-p',test.name,'-v'],cwd=R,capture_output=True,text=True);(O/'tests.log').write_text(r.stdout+r.stderr)
for p,h in pins.items():assert sha(R/p)==h,p
assert 'Ran 25 tests'in r.stdout+r.stderr,'actual-count-mismatch'
validation=dict(tests=25,exitCode=r.returncode,passed=r.returncode==0,importExitCode=a.returncode,allPassed=r.returncode==0 and a.returncode==0,testLogSHA256=sha(O/'tests.log'),importLogSHA256=sha(O/'import.log'),orderedCodePins=[dict(path=str(p.relative_to(R)),sha256=sha(p))for p in [helper,test,*sorted(seen-{helper.resolve(),test.resolve()})]],beforeAfterLiteralPins=before,actualImportedLocalClosure=imported,noDB=True,noLease=True,noRealMaskOrTerrainConstruction=True,currentManifestSHA256=sha(R/'3d-viewer/city/data/manifest.json'),checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat());(O/'validation.json').write_text(json.dumps(validation,indent=2,sort_keys=True)+'\n');print(json.dumps(dict(tests=25,exitCode=r.returncode,importExitCode=a.returncode,pins=len(pins),transitiveLocalClosure=len(imported),orderedCodePins=len(validation['orderedCodePins']),logSHA=sha(O/'tests.log'),validationSHA=sha(O/'validation.json'),path=str(O.relative_to(R)))));sys.exit(0 if validation['allPassed']else 1)
