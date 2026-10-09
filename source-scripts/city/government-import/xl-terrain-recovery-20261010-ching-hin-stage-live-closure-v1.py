"""Close installed Ching Hin stage/live files; archived metadata stays a leaf."""
import gzip,json,hashlib,subprocess
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-terrain-recovery-ching-hin-installed-v1-20261010';DOC=BASE/BATCH;OUT=BASE/'xl-terrain-recovery-20261010-ching-hin-stage-live-closure-v1'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not OUT.exists();r=read(DOC/'result.json');assert r['publication'] and r['newlyInstalled']==1 and r['installedUids']==['landsd/26653:0'];sync=read(DOC/'neon-sync.json');assert sync['jobId']==r['jobId'] and sync['resultVerified']
 with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 scope=read(BASE/'xl-terrain-recovery-20261010-ching-hin-source-closed-scope-v1/closed-scope.json');pointer_rows=scope['metadataLeafJsonPointers'];pointer_map={}
 for item in pointer_rows:
  assert digest((ROOT/item['path']).read_bytes())==item['documentSHA256'];pointer_map.setdefault(item['path'],[]).append(item['boundary'])
 leaf=set(scope['metadataLeafPaths']);paths=set();versions=[];queue=[];seen=set();aliases=[*scope['historicalManifestAliases'],dict(originalPath='3d-viewer/city/data/manifest.json',sha256=r['manifestBeforeSHA256'],archive=ref(HERE/'local'/BATCH/'manifest-before-installation.json'))];alias={(a['originalPath'],a['sha256']):ROOT/a['archive']['path'] for a in aliases}
 def add(p):
  p=Path(p);assert p.exists(),str(p);rel=str(p.relative_to(ROOT))
  if rel not in paths:paths.add(rel);queue.append(p)
 for k in [1]:
  d=BASE/'government-xl-terrain-recovery-ching-hin-typed-stage-v1-20261010';a=HERE/'accepted'/d.name
  for parent in [d,a]:
   if parent.exists():
    for p in parent.rglob('*'):
     if p.is_file():add(p)
  add(HERE/'xl-terrain-recovery-20261010-ching-hin-stage-install-v1.py')
 for p in DOC.rglob('*'):
  if p.is_file():add(p)
 for n in [1]:add(HERE/'xl-terrain-recovery-20261010-ching-hin-live-install-v1.py')
 add(Path(__file__));add(HERE/'test_original_exact_replacement_routing_metadata_scope_actual_v2_20261010.py');add(HERE/'local'/BATCH/'manifest-before-installation.json');source_scope=BASE/'xl-terrain-recovery-20261010-ching-hin-source-closed-scope-v1/closed-scope.json';add(source_scope);leaf.add(str(source_scope.relative_to(ROOT)))
 pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';add(pointer);inventory=ROOT/read(pointer)['inventory'];add(inventory);leaf.update([str(pointer.relative_to(ROOT)),str(inventory.relative_to(ROOT))])
 for p in [ROOT/'3d-viewer/city/data/manifest.json',ROOT/'3d-viewer/city/data/building-progress.json',ROOT/'3d-viewer/data/building-progress.json']:
  if p.exists():add(p);leaf.add(str(p.relative_to(ROOT)))
 plan=read(DOC/'atomic-plan.json')
 for a in plan['areas']:
  add(ROOT/'3d-viewer'/a['destination']);cat=ROOT/'3d-viewer'/a['destination']
  for m in read(cat)['models']:
   source=cat.parent/m['asset'];assert digest(source.read_bytes())==m['sha256'];add(source)
 for t in plan['topLevelTerrainPatches']:add(ROOT/'3d-viewer'/t['destination']);assert digest((ROOT/'3d-viewer'/t['destination']).read_bytes())==t['sha256']
 def references(v,document,pointer=""):
  from original_disjoint_routing_metadata_scope_20261010 import canonical
  declared={r["pointer"]:r for r in pointer_map.get(document,[])}
  if pointer in declared:assert canonical(v)==declared[pointer]["canonicalSHA256"];return
  if isinstance(v,dict):
   if isinstance(v.get('path'),str) and isinstance(v.get('sha256'),str) and len(v['sha256'])==64:
    e=dict(path=v['path'],sha256=v['sha256']);p=ROOT/e['path'];actual=digest(p.read_bytes()) if p.exists() else None
    if actual!=e['sha256']:p=alias.get((e['path'],e['sha256']));assert p is not None and digest(p.read_bytes())==e['sha256'],'Unbound changed reference:'+e['path']
    versions.append(e);add(p)
   for key,x in v.items():references(x,document,pointer+"/"+str(key).replace("~","~0").replace("/","~1"))
  elif isinstance(v,list):
   for i,x in enumerate(v):references(x,document,pointer+"/"+str(i))
 while queue:
  p=queue.pop();rel=str(p.relative_to(ROOT))
  if rel in seen:continue
  seen.add(rel)
  if rel in leaf or 'manifest-before-installation.json' in rel or p.name=='historical-manifest.json':continue
  if p.name.endswith('.json') or p.name.endswith('.json.gz'):
   references(read(p),rel)
 bindings=[ref(ROOT/p) for p in sorted(paths)];tracked=set(subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines());result=dict(closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=bindings,referenceVersions=sorted({(e['path'],e['sha256']):e for e in versions}.values(),key=lambda e:(e['path'],e['sha256'])),historicalManifestAliases=aliases,metadataLeafPaths=sorted(leaf),metadataLeafJsonPointers=pointer_rows,newFiles=[p for p in sorted(paths) if p not in tracked],installedNeon=r['jobId'],snapshotId=r['snapshotId'],qualification='All failed/final staged receipts, guarded publisher, all solid staged/live exports and deployed exact original source/native terrain are verified. Full numeric Ching Hin source proof is independently closed and reviewed; its source scope must be merged into the installation commit. Global catalogues/terrain/progress/inventory preserve exact serialized bytes as nonrecursive historical metadata leaves; no unrelated raw archive is silently imported.')
 save(OUT/'closed-scope.json',result);print(json.dumps(dict(paths=len(paths),referenceVersions=len(result['referenceVersions']),newFiles=len(result['newFiles']),jobId=r['jobId'])),flush=True)
if __name__=='__main__':main()
