"""Completed Vancor evidence additive declaration only.
Exact inherited Beverly v4 aliases/leaves/typed pointers are unchanged.
All new source/current numerical references recurse; no future pair acceptance.
"""
import ast,json,subprocess,time
from pathlib import Path
from run import ROOT,HERE,read,save,digest
B=ROOT/'docs/astra-city/government-import';PRIOR=B/'government-xl-beverly-k-p-fresh70279-held-revisit-additive-scope-v4-20261011/declared-scope.json';DOC=B/'government-xl-vancor-completed-evidence-additive-scope-v1-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 start=time.monotonic();assert not DOC.exists();prior=read(PRIOR);assert prior['declaredReferencesClosed']and not prior['unboundExactReferenceVersions'];aliases=prior['historicalManifestAliases'];leaves=set(prior['metadataLeafPaths']);pointers=prior['metadataLeafJsonPointers'];pointermap={(x['path'],x['boundary']['pointer']):x for x in pointers};archive={(a['originalPath'],a['sha256']):ROOT/a['archive']['path']for a in aliases};tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0'));initial=set(prior['closedPaths']);paths=set();queue=[];seen=set();hashes={};versions={};cached={};unknown=[];audit={r['path']:r for r in prior['auditDeclarationContextRefs']};audit[str(PRIOR.relative_to(ROOT))]=ref(PRIOR)
 audit[str((B/'government-xl-beverly-fresh-source-held-revisit-root-closure-v4-20261011/root-closed-scope.json').relative_to(ROOT))]=ref(B/'government-xl-beverly-fresh-source-held-revisit-root-closure-v4-20261011/root-closed-scope.json')
 def hashed(p):
  if p not in hashes:hashes[p]=digest(p.read_bytes())if p.is_file()else None
  return hashes[p]
 def is_audit(p):return p.name in ['declared-scope.json','closed-scope.json','root-closed-scope.json']
 def add(p):
  p=Path(p);rel=str(p.relative_to(ROOT));assert p.is_file(),rel
  if is_audit(p):audit[rel]=ref(p);return
  if rel in tracked and rel not in initial:cached[rel]=ref(p);return
  if rel not in paths:paths.add(rel);queue.append(p)
 def bind(path,h,origin):
  p=Path(path)if Path(path).is_absolute()else ROOT/path
  if not p.exists()and path.startswith('city/'):p=ROOT/'3d-viewer'/path
  rel=str(p.relative_to(ROOT))
  if hashed(p)!=h:
   p=archive.get((rel,h))
   if p is None:unknown.append(dict(path=rel,sha256=h,origin=origin));return
  assert hashed(p)==h;versions[(rel,h)]=dict(path=rel,sha256=h);add(p)
 def refs(v,origin,pointer=''):
  boundary=pointermap.get((origin,pointer))
  if boundary:assert hashed(ROOT/origin)==boundary['documentSHA256']and digest(json.dumps(v,sort_keys=True,separators=(',',':')).encode())==boundary['boundary']['canonicalSHA256'];return
  if isinstance(v,dict):
   if isinstance(v.get('path'),str)and isinstance(v.get('sha256'),str)and len(v['sha256'])==64:bind(v['path'],v['sha256'],origin)
   for k,x in v.items():
    if k in ['inputHashes','hashes','neighbourTileHashes','currentTileHashes','nativeCatalogueInputHashes','sourceInputHashes']and isinstance(x,dict):
     for p,h in x.items():
      if isinstance(p,str)and isinstance(h,str)and len(h)==64:bind(p,h,origin)
    else:refs(x,origin,pointer+'/'+str(k).replace('~','~0').replace('/','~1'))
  elif isinstance(v,list):
   for i,x in enumerate(v):refs(x,origin,pointer+'/'+str(i))
 folders=sorted(p.name for p in B.iterdir()if p.is_dir()and p.name.startswith('government-xl-vancor-')and (p/'result.json').is_file())
 assert 'government-xl-vancor-90824-current-original-identity-v1-20261011'in folders
 assert 'government-xl-vancor-retained-upper-complete-current-regression-v1-20261011'in folders
 for folder in folders:
  r=read(B/folder/'result.json');assert not r.get('currentAcceptance',False)
  for base in [B/folder,HERE/'local'/folder]:
   if base.exists():
    for p in base.rglob('*'):
     if p.is_file()and '__pycache__'not in str(p):initial.add(str(p.relative_to(ROOT)))
 for folder in ['government-xl-vancor-complete-current-foreign-basic-context-v1-20261011','government-xl-vancor-post-mount-orchestration-v2-input-schema-failure-20261011']:
  base=B/folder;assert base.exists()
  for p in base.rglob('*'):
   if p.is_file():initial.add(str(p.relative_to(ROOT)))
 for n in ['xl-vancor-complete-current-foreign-basic-context-v1-20261011.py','xl-vancor-complete-current-foreign-basic-geometry-v1-20261011.mjs','xl-vancor-post-mount-fresh-current-inputs-v2-20261011.py',Path(__file__).name]:initial.add(str((HERE/n).relative_to(ROOT)))
 # Source code and actual tests become explicit only when pinned by a completed receipt.
 for folder in folders:
  for r in read(B/folder/'result.json')['evidenceRefs']:
   p=ROOT/r['path']
   if p.is_file()and p.suffix in ['.py','.mjs','.js']:initial.add(str(p.relative_to(ROOT)))
 for rel in sorted(initial):add(ROOT/rel)
 for r in prior['referenceVersions']:bind(r['path'],r['sha256'],'exact inherited Beverly v4 referenceVersions')
 for r in prior['exactReferencedTrackedInputs']:bind(r['path'],r['sha256'],'exact inherited Beverly v4 tracked cache')
 while queue:
  p=queue.pop();rel=str(p.relative_to(ROOT))
  if rel in seen:continue
  seen.add(rel)
  if rel in leaves:continue
  if p.name.endswith(('.json','.json.gz')):refs(read(p),rel)
  if p.suffix=='.py':
   for n in ast.walk(ast.parse(p.read_text())):
    names=[n.module]if isinstance(n,ast.ImportFrom)and n.module else[a.name for a in n.names]if isinstance(n,ast.Import)else[]
    for name in names:
     q=HERE/(name.split('.')[0]+'.py')
     if q.exists():add(q)
 assert not(initial&leaves);out=dict(closedPaths=sorted(paths),presentFileBindings=[ref(ROOT/p)for p in sorted(paths)],referenceVersions=sorted(versions.values(),key=lambda x:(x['path'],x['sha256'])),exactReferencedTrackedInputs=sorted(cached.values(),key=lambda x:x['path']),historicalManifestAliases=aliases,metadataLeafPaths=sorted(leaves),metadataLeafJsonPointers=pointers,auditDeclarationContextRefs=sorted(audit.values(),key=lambda x:x['path']),unboundExactReferenceVersions=unknown,declaredReferencesClosed=not unknown,explicitInitialPaths=sorted(initial),sourceOnly=True,currentAcceptance=False,installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges='Changed terrain diagnostic proposals preserved, never installed',newMetadataLeaves=False,newHistoricalAliases=False,newMetadataPointerContract=False,priorV3CurrentManifestHistoricalOnly=prior['priorV3CurrentManifestHistoricalOnly'],explicitUIDs=['landsd/147956:0','landsd/90824:0','landsd/186864:0','landsd/236490:0','landsd/253697:0'],completedEvidenceBatches=folders,modelReviewWrites=0,newlyInstalled=0,rootIndependentClosureRequired=True,elapsedSeconds=time.monotonic()-start,qualification='Completed evidence only: unchanged669source, all historical v1-v4 explicitly changed terrain/packing failures and v4positive seams; fresh d152 current ordinary physical/full4stream genuine roots,6642 actual native bounds/strict separation,77 actual BASIC actors including real90824 penetration, untouched646recovery/fresh rawidentity foreign90825hold/primaryrelations/complete pairinterfaces;840 retained236490 before-after legacy regression proof. No future two-original terrain/support/identity/stage acceptance. Exact inherited Beverly v4 metadata contracts unchanged; every actual new source/current numerical reference recursive. Current captures historical if live changes after their immutable fence.')
 save(DOC/'declared-scope.json',out);print(json.dumps(dict(initial=len(initial),closedPaths=len(paths),tracked=len(cached),versions=len(versions),unknown=len(unknown),firstUnknown=unknown[:5],elapsedSeconds=out['elapsedSeconds'])),flush=True)
if __name__=='__main__':main()
