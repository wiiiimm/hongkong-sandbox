"""Close installed Ko Fung stage/live files; archived metadata stays a leaf."""
import gzip,json,hashlib,subprocess
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ko-fung-two-atomic-installed-v2-20261010';DOC=BASE/BATCH;OUT=BASE/'xl-terrain-recovery-20261010-ko-fung-stage-live-closure-v1'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not OUT.exists();r=read(DOC/'result.json');assert r['publication'] and r['newlyInstalled']==2 and set(r['installedUids'])=={'landsd/79097:0','landsd/110480:0'};sync=read(DOC/'neon-sync.json');assert sync['jobId']==r['jobId'] and sync['resultVerified']
 with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 scope=read(BASE/'xl-terrain-recovery-20261010-ko-fung-current-role-closed-scope-v3/closed-scope.json');leaf=set(scope['metadataLeafPaths']);paths=set();versions=[];queue=[];seen=set();aliases=[scope['historicalManifestAlias'],dict(originalPath='3d-viewer/city/data/manifest.json',sha256=r['manifestBeforeSHA256'],archive=ref(HERE/'local'/BATCH/'manifest-before-installation.json'))];alias={(a['originalPath'],a['sha256']):ROOT/a['archive']['path'] for a in aliases}
 def add(p):
  p=Path(p);assert p.exists(),str(p);rel=str(p.relative_to(ROOT))
  if rel not in paths:paths.add(rel);queue.append(p)
 for k in [1,2,3]:
  d=BASE/f'government-xl-terrain-recovery-ko-fung-two-typed-stage-v{k}-20261010';a=HERE/'accepted'/d.name
  for parent in [d,a]:
   if parent.exists():
    for p in parent.rglob('*'):
     if p.is_file():add(p)
  add(HERE/f'xl-terrain-recovery-20261010-ko-fung-two-stage-install-v{k}.py')
 for p in DOC.rglob('*'):
  if p.is_file():add(p)
 for n in [1,2]:add(HERE/f'xl-terrain-recovery-20261010-ko-fung-two-live-install-v{n}.py')
 add(Path(__file__));add(HERE/'local'/BATCH/'manifest-before-installation.json')
 pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';add(pointer);inventory=ROOT/read(pointer)['inventory'];add(inventory);leaf.update([str(pointer.relative_to(ROOT)),str(inventory.relative_to(ROOT))])
 for p in [ROOT/'3d-viewer/city/data/manifest.json',ROOT/'3d-viewer/city/data/building-progress.json',ROOT/'3d-viewer/data/building-progress.json']:
  if p.exists():add(p);leaf.add(str(p.relative_to(ROOT)))
 plan=read(DOC/'atomic-plan.json')
 for a in plan['areas']:
  add(ROOT/'3d-viewer'/a['destination']);cat=ROOT/'3d-viewer'/a['destination']
  for m in read(cat)['models']:
   source=cat.parent/m['asset'];assert digest(source.read_bytes())==m['sha256'];add(source)
 for t in plan['topLevelTerrainPatches']:add(ROOT/'3d-viewer'/t['destination']);assert digest((ROOT/'3d-viewer'/t['destination']).read_bytes())==t['sha256']
 def references(v):
  if isinstance(v,dict):
   if isinstance(v.get('path'),str) and isinstance(v.get('sha256'),str) and len(v['sha256'])==64:
    e=dict(path=v['path'],sha256=v['sha256']);p=ROOT/e['path'];actual=digest(p.read_bytes()) if p.exists() else None
    if actual!=e['sha256']:p=alias.get((e['path'],e['sha256']));assert p is not None and digest(p.read_bytes())==e['sha256'],'Unbound changed reference:'+e['path']
    versions.append(e);add(p)
   for x in v.values():references(x)
  elif isinstance(v,list):
   for x in v:references(x)
 while queue:
  p=queue.pop();rel=str(p.relative_to(ROOT))
  if rel in seen:continue
  seen.add(rel)
  if rel in leaf or 'manifest-before-installation.json' in rel or p.name=='historical-manifest.json':continue
  if p.name.endswith('.json') or p.name.endswith('.json.gz'):
   references(read(p))
 bindings=[ref(ROOT/p) for p in sorted(paths)];tracked=set(subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines());result=dict(closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=bindings,referenceVersions=sorted({(e['path'],e['sha256']):e for e in versions}.values(),key=lambda e:(e['path'],e['sha256'])),historicalManifestAliases=aliases,metadataLeafPaths=sorted(leaf),newFiles=[p for p in sorted(paths) if p not in tracked],installedNeon=r['jobId'],snapshotId=r['snapshotId'],qualification='All failed/final staged receipts, guarded publisher, all solid staged/live exports and deployed exact two sources/native terrain are verified. Full numeric Ko source proof is separately committed. Global catalogues/terrain/progress/inventory preserve exact serialized bytes as nonrecursive historical metadata leaves; no unrelated raw archive is silently imported.')
 save(OUT/'closed-scope.json',result);print(json.dumps(dict(paths=len(paths),referenceVersions=len(result['referenceVersions']),newFiles=len(result['newFiles']),jobId=r['jobId'])),flush=True)
if __name__=='__main__':main()
