"""DRAFT additive fresh official70279 lookup and K/P held revisit context; execute after both jobs frozen.
Keeps prior v3 exact aliases/leaves/four typed pointers/audit contracts unchanged.
No mutable capture, new metadata routing exception, stage or installation evidence.
"""
import ast,json,subprocess,time
from pathlib import Path
from run import ROOT,HERE,read,save,digest
B=ROOT/'docs/astra-city/government-import';PRIOR=B/'government-xl-beverly-elm-actual-original-tin-causal-additive-scope-v3-20261011/declared-scope.json';DOC=B/'government-xl-beverly-k-p-fresh70279-held-revisit-additive-scope-v4-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 start=time.monotonic();assert not DOC.exists();prior=read(PRIOR);assert prior['declaredReferencesClosed']and not prior['unboundExactReferenceVersions'];aliases=prior['historicalManifestAliases'];leaves=set(prior['metadataLeafPaths']);pointers=prior['metadataLeafJsonPointers'];pointermap={(x['path'],x['boundary']['pointer']):x for x in pointers};archive={(a['originalPath'],a['sha256']):ROOT/a['archive']['path']for a in aliases};tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0'));initial=set(prior['closedPaths']);paths=set();queue=[];seen=set();hashes={};versions={};cached={};unknown=[];audit={r['path']:r for r in prior['auditDeclarationContextRefs']};audit[str(PRIOR.relative_to(ROOT))]=ref(PRIOR)
 for p in (B/'government-xl-beverly-k-p-fresh70279-held-revisit-context-v1-20261011').rglob('*'):
  if p.is_file():audit[str(p.relative_to(ROOT))]=ref(p)
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
 folders=['government-xl-beverly-70279-fresh-official-source-index-directory-search-v1-20261011','government-xl-beverly-k-p-fresh70279-held-revisit-context-v2-20261011']
 for folder in folders:
  r=read(B/folder/'result.json');assert not r.get('currentAcceptance',False)
  for base in [B/folder,HERE/'local'/folder]:
   if base.exists():
    for p in base.rglob('*'):
     if p.is_file()and '__pycache__'not in str(p):initial.add(str(p.relative_to(ROOT)))
 for p in (B/'government-xl-beverly-70279-fresh-official-source-search-method-v1-20261011').rglob('*'):
  if p.is_file():initial.add(str(p.relative_to(ROOT)))
 for n in ['beverly_70279_fresh_official_source_index_directory_search_v1_20261011.py','beverly_70279_freeze_fresh_official_source_index_directory_search_v1_20261011.py','beverly_k_p_fresh70279_held_revisit_context_v1_20261011.py','beverly_k_p_fresh70279_held_revisit_context_v2_20261011.py',Path(__file__).name]:initial.add(str((HERE/n).relative_to(ROOT)))
 for rel in sorted(initial):add(ROOT/rel)
 for r in prior['referenceVersions']:bind(r['path'],r['sha256'],'exact inherited v3 referenceVersions')
 for r in prior['exactReferencedTrackedInputs']:bind(r['path'],r['sha256'],'exact inherited v3 tracked cache')
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
 assert not(initial&leaves);out=dict(closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p)for p in sorted(paths)],referenceVersions=sorted(versions.values(),key=lambda x:(x['path'],x['sha256'])),exactReferencedTrackedInputs=sorted(cached.values(),key=lambda x:x['path']),historicalManifestAliases=aliases,metadataLeafPaths=sorted(leaves),metadataLeafJsonPointers=pointers,auditDeclarationContextRefs=sorted(audit.values(),key=lambda x:x['path']),unboundExactReferenceVersions=unknown,declaredReferencesClosed=not unknown,explicitInitialPaths=sorted(initial),sourceOnly=True,currentAcceptance=False,installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges=0,newMetadataLeaves=False,newHistoricalAliases=False,newMetadataPointerContract=False,currentCaptureCreated=False,priorV3CurrentManifestHistoricalOnly=prior['priorV2CurrentManifestHistoricalOnly'],explicitUIDs=['landsd/233218:0','landsd/255543:0','landsd/255939:0','landsd/70279:0'],allBeverlyPriorEvidenceAndSeparateHeldStatePreserved=True,existingHeldSnapshotId='1ef9e76176f13d45',modelReviewWrites=0,stableCSUIDObjectRenumberingPreserved=True,boundedFreshDirectoryAbsenceOnly=True,rootIndependentClosureRequired=True,elapsedSeconds=time.monotonic()-start,qualification='Additive actual fresh official2D queries/two3D index families and complete16 directory metadata search plus linked source-context held revisit note only. StableCSUID3716415011T20080220 is active under object70234 versus saved BASIC70279; no remap or substitution authorized. Recorded source base/top null and fresh3D absence bounded to listed revisions/ETags/scope. Prior exact source/current K/Pheld, Elm authenticTIN/causal negatives, aliases and tracked-cache pins retained. No mutable ground capture, model member acquisition, candidate terrain, model-review/pointer writes, current/grade/root acceptance or body omission. Existing exact metadata contracts only; all actual new data/producers/raw HTTP outputs explicit, reused committed byte-pinned inputs not unfolded into unrelated histories.')
 save(DOC/'declared-scope.json',out);print(json.dumps(dict(initial=len(initial),closedPaths=len(paths),tracked=len(cached),versions=len(versions),unknown=len(unknown),firstUnknown=unknown[:5],elapsedSeconds=out['elapsedSeconds'])),flush=True)
if __name__=='__main__':main()
