import gzip,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
import sys
payload=json.loads(Path(sys.argv[1]).read_bytes())
scope=payload if isinstance(payload,list) else payload.get('closedPaths',payload.get('paths'))
aliases={(r["path"],r["sha256"]):r["archivePath"] for r in payload.get("aliases",[])} if isinstance(payload,dict) else {}
leaf_paths=set(payload.get("leafPaths",[])) if isinstance(payload,dict) else set()
paths=set()
for item in scope:
 p=ROOT/item
 if not p.exists():
  if item.endswith('government-native-202994-0-203433-0.json'):continue
  raise AssertionError(item)
 paths.update(str(q.relative_to(ROOT)) for q in ([p] if p.is_file() else p.rglob('*')) if q.is_file() and '__pycache__' not in str(q))
queue=list(paths);scanned=set();verified=set();historic={}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def check(path,pin):
 path=('3d-viewer/'+path) if path.startswith('city/') else path
 p=(ROOT/path).resolve();assert p.is_relative_to(ROOT),path;rel=str(p.relative_to(ROOT));key=(rel,pin)
 if key in verified:return
 assert p.is_file(),rel
 if sha(p.read_bytes())!=pin and key in aliases:
  archive=ROOT/aliases[key];assert archive.is_file() and sha(archive.read_bytes())==pin
  historic[key]='archive:'+aliases[key];paths.add(aliases[key])
 if sha(p.read_bytes())!=pin and key not in historic:
  candidates=['HEAD','03799b01^']+subprocess.check_output(['git','log','--all','--format=%H','--',rel],cwd=ROOT,text=True).splitlines()
  for rev in candidates:
   x=subprocess.run(['git','show',rev+':'+rel],cwd=ROOT,capture_output=True)
   if x.returncode==0 and sha(x.stdout)==pin:historic[key]=rev;break
  else:raise AssertionError((rel,pin,'changed frozen evidence'))
 verified.add(key)
 tracked=subprocess.run(['git','ls-files','--error-unmatch',rel],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
 if key not in historic and rel not in scanned and not tracked:queue.append(rel)
 if rel not in paths and subprocess.run(['git','ls-files','--error-unmatch',rel],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode:
  paths.add(rel)
def walk(v):
 if isinstance(v,dict):
  if isinstance(v.get('path'),str) and isinstance(v.get('sha256'),str) and len(v['sha256'])==64:check(v['path'],v['sha256'])
  for k,c in v.items():
   if k in ('inputHashes','hashes','neighbourTileHashes') and isinstance(c,dict):
    for path,pin in c.items():
     if isinstance(pin,str) and len(pin)==64:check(path,pin)
   else:walk(c)
 elif isinstance(v,list):
  for c in v:walk(c)
while queue:
 rel=queue.pop()
 if rel in scanned:continue
 scanned.add(rel);p=ROOT/rel
 if rel in leaf_paths or rel in ['docs/astra-city/landmark-completion-audit/neon-snapshot.json','3d-viewer/scripts/building-progress/review-proof.json','3d-viewer/scripts/building-progress/screening-proof.json'] or p.name.startswith('source-review-inventory-') or p.name in ('full-xl-current-count.json','manifest.json','manifest-before-installation.json') or p.name.endswith('manifest.json') or p.name=='closure.json':continue
 if p.name.endswith(('.json','.json.gz')):
  try:raw=p.read_bytes();data=json.loads(gzip.decompress(raw) if p.name.endswith('.gz') else raw)
  except (ValueError,OSError):continue
  try:walk(data)
  except Exception:
   print('REFERENCE_ORIGIN',rel,flush=True);raise
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='codex/astra-hong-kong-city'
assert 'docs/astra-city/government-import/government-xl-safe-boundary-recovery-sequence-20261006/working-commands.json' not in paths
out={'paths':sorted(paths),'verifiedReferenceVersions':len(verified),'historicalReferences':[dict(path=p,sha256=s,gitRevision=r) for (p,s),r in historic.items()],'bytes':sum((ROOT/p).stat().st_size for p in paths)}
Path(sys.argv[2]).write_text(json.dumps(out,indent=2))
print(json.dumps({k:v for k,v in out.items() if k!='paths'}))
