import gzip,hashlib,json,subprocess
from pathlib import Path
ROOT=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city')
import sys
tracked_start=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT)
tracked_paths=set(tracked_start.decode().split('\0'))-{''}
head_start=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT)
payload=json.loads(Path(sys.argv[1]).read_bytes())
scope=payload if isinstance(payload,list) else payload.get('closedPaths',payload.get('paths'))
aliases={(r["path"],r["sha256"]):r["archivePath"] for r in payload.get("aliases",[])} if isinstance(payload,dict) else {}
leaf_paths=set(payload.get("leafPaths",payload.get("metadataLeafPaths",[]))) if isinstance(payload,dict) else set()
if isinstance(payload,dict):
 aliases.update({(r["originalPath"],r["sha256"]):r["archive"]["path"] for r in payload.get("historicalManifestAliases",[])})
sys.path.insert(0,str(ROOT/'source-scripts/city/government-import'))
from original_disjoint_routing_metadata_scope_20261010 import verify_boundaries,canonical
from original_complete_role_routing_metadata_scope_20261010 import verify_role_boundaries
from lippo_exact_pending_embedded_geometry_reference_v1_20261011 import BoundResolver,CAPTURE_PATH,CAPTURE_SHA,TILE_PATH,TILE_SHA,POINTERS
resolver=BoundResolver((ROOT/CAPTURE_PATH).read_bytes(),(ROOT/TILE_PATH).read_bytes())
typed_references={}
from lippo_exact_pending_predecessor_routing_copies_v1_20261011 import BoundRoutingCopies,PREVIOUS_PATH,PREVIOUS_SHA,PENDING_PATH,PENDING_SHA
routing=BoundRoutingCopies((ROOT/CAPTURE_PATH).read_bytes(),(ROOT/PREVIOUS_PATH).read_bytes(),(ROOT/PENDING_PATH).read_bytes())
routing_helper=ROOT/'source-scripts/city/government-import/lippo_exact_pending_predecessor_routing_copies_v1_20261011.py'
routing_helper_start=hashlib.sha256(routing_helper.read_bytes()).hexdigest()
verified_duplicate_routing_rows=set()
typed_helper=ROOT/'source-scripts/city/government-import/lippo_exact_pending_embedded_geometry_reference_v1_20261011.py'
typed_helper_start=hashlib.sha256(typed_helper.read_bytes()).hexdigest()
def read_doc(p):
 raw=p.read_bytes();return json.loads(gzip.decompress(raw) if p.name.endswith(".gz") else raw)
pointer_map={}
for r in payload.get('metadataLeafJsonPointers',[]):
 assert r['path'].endswith(('/current-source-terrain-preflight.json','/typed-role.json.gz','/typed-role-publication-recheck.json.gz','/complete-current-role.json.gz')) and r['path'].startswith('docs/astra-city/government-import/')
 assert __import__('hashlib').sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['documentSHA256']
 pointer_map.setdefault(r['path'],[]).append(r['boundary'])
for rel,declared in pointer_map.items():
 d=read_doc(ROOT/rel);is_role=declared[0].get('documentType')=='complete-current-original-role-routing-provenance-v1';sha=d['manifestSHA256'] if is_role else d['currentManifest']['sha256']
 candidates=[r for r in payload['historicalManifestAliases'] if r['sha256']==sha]
 assert candidates
 archive=ROOT/candidates[0]['archive']['path'];assert __import__('hashlib').sha256(archive.read_bytes()).hexdigest()==sha
 if is_role:
  candidate_ref=declared[0]['boundCandidateRef'];candidate=ROOT/candidate_ref['path'];assert hashlib.sha256(candidate.read_bytes()).hexdigest()==candidate_ref['sha256']
  verify_role_boundaries(d,read_doc(archive),read_doc(candidate),declared,candidate_ref=candidate_ref,manifest_ref=dict(path='3d-viewer/city/data/manifest.json',sha256=sha),expected_uids=declared[0]['boundCandidateUIDs'])
 else:verify_boundaries(d,read_doc(archive),declared)

audit_context={r["path"]:r["sha256"] for r in payload.get("auditDeclarationContextRefs",[])}
for rel,pin in audit_context.items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==pin
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
 tracked=rel in tracked_paths
 if key not in historic and rel not in scanned and not tracked:queue.append(rel)
 if rel not in paths and rel not in tracked_paths:
  paths.add(rel)
def walk(v,pointer=""):
 if routing.handles(rel,pointer):
  routing.verify_value(rel,pointer,v);verified_duplicate_routing_rows.add(pointer);return
 declared={x['pointer']:x for x in pointer_map.get(rel,[])}
 if pointer in declared:
  assert canonical(v)==declared[pointer]['canonicalSHA256'];return
 if isinstance(v,dict):
  if isinstance(v.get('path'),str) and isinstance(v.get('sha256'),str) and len(v['sha256'])==64:
   if resolver.handles(rel,pointer):
    proof=resolver.resolve(rel,pointer,v);typed_references[(rel,pointer)]=proof
    check(TILE_PATH,TILE_SHA)
   else:check(v['path'],v['sha256'])
  for k,c in v.items():
   if k in ('inputHashes','hashes','neighbourTileHashes','currentTileHashes','nativeCatalogueInputHashes','sourceInputHashes') and isinstance(c,dict):
    for path,pin in c.items():
     if isinstance(pin,str) and len(pin)==64:check(path,pin)
   else:walk(c,pointer+"/"+str(k).replace("~","~0").replace("/","~1"))
 elif isinstance(v,list):
  for i,c in enumerate(v):walk(c,pointer+"/"+str(i))
# Resolve/report all six embedded references independently of inherited old
# routing traversal, preserving their positive complete-geometry proof.
for pointer in POINTERS:
 reference=resolver.context
 for k in pointer.split('/')[1:]:reference=reference[int(k)] if isinstance(reference,list) else reference[k]
 typed_references[(CAPTURE_PATH,pointer)]=resolver.resolve(CAPTURE_PATH,pointer,reference)
check(TILE_PATH,TILE_SHA)
check(PREVIOUS_PATH,PREVIOUS_SHA);check(PENDING_PATH,PENDING_SHA)
while queue:
 rel=queue.pop()
 if rel in scanned:continue
 scanned.add(rel);p=ROOT/rel
 if rel in audit_context or rel in leaf_paths or rel in ['docs/astra-city/landmark-completion-audit/neon-snapshot.json','3d-viewer/scripts/building-progress/review-proof.json','3d-viewer/scripts/building-progress/screening-proof.json'] or p.name.startswith('source-review-inventory-') or p.name in ('full-xl-current-count.json','manifest.json','manifest-before-installation.json') or p.name.endswith('manifest.json') or p.name=='closure.json':continue
 if p.name.endswith(('.json','.json.gz')):
  try:raw=p.read_bytes();data=json.loads(gzip.decompress(raw) if p.name.endswith('.gz') else raw)
  except (ValueError,OSError):continue
  try:walk(data)
  except Exception:
   print('REFERENCE_ORIGIN',rel,flush=True);raise
assert sha((ROOT/CAPTURE_PATH).read_bytes())==CAPTURE_SHA and sha((ROOT/TILE_PATH).read_bytes())==TILE_SHA
assert sha(typed_helper.read_bytes())==typed_helper_start
assert len(typed_references)==6
assert len(verified_duplicate_routing_rows)==9888
assert sha((ROOT/PREVIOUS_PATH).read_bytes())==PREVIOUS_SHA and sha((ROOT/PENDING_PATH).read_bytes())==PENDING_SHA
assert sha(routing_helper.read_bytes())==routing_helper_start
assert subprocess.check_output(['git','ls-files','-z'],cwd=ROOT)==tracked_start,'Tracked index inventory changed during verification'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT)==head_start,'HEAD changed during verification'
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='codex/astra-hong-kong-city'
assert 'docs/astra-city/government-import/government-xl-safe-boundary-recovery-sequence-20261006/working-commands.json' not in paths
out={'exactPredecessorRoutingCopies':routing.proof(),'typedEmbeddedGeometryReferences':list(typed_references.values()),'typedReferenceHandlingDoesNotExcludeNumericGeometry':True,'paths':sorted(paths),'verifiedReferenceVersions':len(verified),'historicalReferences':[dict(path=p,sha256=s,gitRevision=r) for (p,s),r in historic.items()],'bytes':sum((ROOT/p).stat().st_size for p in paths)}
Path(sys.argv[2]).write_text(json.dumps(out,indent=2))
print(json.dumps({k:v for k,v in out.items() if k!='paths'}))
