"""Byte-verified current Glorious proof closure, global metadata leaves explicit."""
import subprocess
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
BASE=ROOT/'docs/astra-city/government-import'
ROLE=BASE/'xl-terrain-recovery-20261010-glorious-peak-current-mounted-role-v2'
OUT=BASE/'xl-terrain-recovery-20261010-glorious-peak-current-role-closed-scope-v1'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not OUT.exists();r=read(ROLE/'result.json');typed=read(ROLE/'typed-role.json.gz');assert typed['independentPhysicalChecksPassed'] and typed['completeOriginalFaces']==18944
 with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 # These leaves are serialized global catalogue/terrain context, independently
 # byte-hashed in current acceptance. Current numeric authority is complete
 # actual source/runtime/ground streams and explicit role/context receipts.
 old=read(BASE/'xl-terrain-recovery-20261010-ko-fung-current-role-closed-scope-v3/closed-scope.json');leaf=set(old['metadataLeafPaths']);alias=typed['historicalManifestAlias'];assert ref(ROOT/alias['archive']['path'])==alias['archive']
 aliases=[alias,dict(originalPath='3d-viewer/city/data/manifest.json',sha256='55abaf316152f692bd50dca315e0ee6444638a58375b58ff65877a80ed5d84dd',archive=ref(HERE/'local/government-xl-ko-fung-two-atomic-installed-v2-20261010/manifest-before-installation.json'))];aliasmap={(a['originalPath'],a['sha256']):ROOT/a['archive']['path'] for a in aliases};paths=set();queue=[];versions=[];seen=set()
 def add(p):
  p=Path(p);assert p.exists(),str(p);rel=str(p.relative_to(ROOT))
  if rel not in paths:paths.add(rel);queue.append(p)
 def references(v):
  if isinstance(v,dict):
   if isinstance(v.get('path'),str) and isinstance(v.get('sha256'),str) and len(v['sha256'])==64:
    e=dict(path=v['path'],sha256=v['sha256']);p=ROOT/e['path']
    if not p.exists() or digest(p.read_bytes())!=e['sha256']:
     p=aliasmap.get((e['path'],e['sha256']));assert p is not None,'Unbound version:'+e['path']+':'+e['sha256']
    assert digest(p.read_bytes())==e['sha256'];versions.append(e);add(p)
   for x in v.values():references(x)
  elif isinstance(v,list):
   for x in v:references(x)
 for parent in [ROLE,*BASE.glob('xl-terrain-recovery-20261010-glorious-peak-*'),BASE/'government-xl-terrain-recovery-glorious-peak-original-pair-current-physical-v2-20261010']:
  if parent==OUT or not parent.is_dir():continue
  for p in parent.rglob('*'):
   if p.is_file():add(p)
 add(Path(__file__))
 # Future stage/live scripts belong to their later stage receipt, not the
 # already complete numeric source/current proof.
 while queue:
  p=queue.pop();rel=str(p.relative_to(ROOT))
  if rel in seen:continue
  seen.add(rel)
  if rel in leaf or p.name in ['historical-manifest.json','manifest-before-installation.json']:continue
  if p.name.endswith('.json') or p.name.endswith('.json.gz'):references(read(p))
 tracked=set(subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines())
 result=dict(closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p) for p in sorted(paths)],referenceVersions=sorted({(e['path'],e['sha256']):e for e in versions}.values(),key=lambda e:(e['path'],e['sha256'])),historicalManifestAlias=alias,historicalManifestAliases=aliases,metadataLeafPaths=sorted(leaf),currentRoleNeon=r['jobId'],newFiles=[p for p in sorted(paths) if p not in tracked],currentNumericReplayAuthority='Complete untouched provider sources/root/attributes,18944 source/runtime triangles, complete current drawn ground, exact finite clearance, grade/support graph and mounted roles; all current identities/forms/native/runtime gates.',qualification='Every explicit current proof binding verified. Earlier raw failures retained. Global serialized catalogue/terrain metadata remains independently byte-bound leaf; unrelated raw archive caches are not recursively imported.')
 save(OUT/'closed-scope.json',result);print(dict(paths=len(paths),references=len(result['referenceVersions']),newFiles=len(result['newFiles'])))
if __name__=='__main__':main()
