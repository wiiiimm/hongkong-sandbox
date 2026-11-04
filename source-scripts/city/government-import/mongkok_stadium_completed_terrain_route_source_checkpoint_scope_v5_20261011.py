"""DRAFT completed-only additive terrain-route/source checkpoint.
Exact priorv4 aliases/leaf/typedmetadata contracts, no future drafts or acceptance.
"""
import ast,json,subprocess,time
from pathlib import Path
from run import ROOT,HERE,read,save,digest
B=ROOT/'docs/astra-city/government-import';PRIOR=B/'government-xl-mongkok-stadium-source-current-ground-checkpoint-v4-20261011/declared-scope.json';DOC=B/'government-xl-mongkok-stadium-completed-terrain-route-source-checkpoint-v5-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 start=time.monotonic();assert not DOC.exists();prior=read(PRIOR);assert prior['declaredReferencesClosed']and not prior['unboundExactReferenceVersions'];aliases=list(prior['historicalManifestAliases']);leaves=set(prior['metadataLeafPaths']);pointers=prior['metadataLeafJsonPointers'];pointermap={(x['path'],x['boundary']['pointer']):x for x in pointers};archive={(a['originalPath'],a['sha256']):ROOT/a['archive']['path']for a in aliases};tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0'));initial=set(prior['closedPaths']);paths=set();queue=[];seen=set();hashes={};versions={};cached={};unknown=[];audit={r['path']:r for r in prior['auditDeclarationContextRefs']};audit[str(PRIOR.relative_to(ROOT))]=ref(PRIOR)
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
 folders=['government-xl-mongkok-stadium240332-causal55-original-tin-domain-seam-diagnostic-v1-20261011', 'government-xl-mongkok-stadium240332-atomic-domain-one-ring-inventory-v1-20261011', 'government-xl-mongkok-stadium240332-atomic-ring-outer-ground-capture-v1-20261011', 'government-xl-mongkok-stadium240332-one-ring-inner-outer-anchor-feasibility-v1-20261011', 'government-xl-mongkok-stadium240332-pinch-local-positive-edge-layer-inventory-v1-20261011', 'government-xl-mongkok-stadium240332-ten-metre-clipped-transition-candidate-v1-20261011', 'government-xl-mongkok-stadium240332-complete-outer-layer-encoding-inventory-v1-20261011', 'government-xl-mongkok-stadium240332-completed-native-projection-audit-v1-20261011', 'government-xl-mongkok-stadium240332-actual-native-union-authentic-core-inventory-v2-20261011']
 for folder in folders:
  r=read(B/folder/'result.json');assert r['sourceOnly']and not r.get('currentAcceptance',False)
  for base in [B/folder,HERE/'local'/folder]:
   if base.exists():
    for p in base.rglob('*'):
     if p.is_file()and '__pycache__'not in str(p)and not p.name.endswith('.tmp'):initial.add(str(p.relative_to(ROOT)))
 # Own interrupted attempt histories and all native/partial source chunks are
 # actual evidence, not successful full source qualification or exemptions.
 for name in ['government-xl-mongkok-stadium240332-merged-protected-patch-authentic-core-inventory-v1-20261011','government-xl-mongkok-stadium240332-merged-protected-patch-authentic-core-inventory-v2-20261011','government-xl-mongkok-stadium240332-merged-protected-patch-authentic-core-inventory-v3-20261011']:
  for p in (HERE/'local'/name).rglob('*'):
   if p.is_file()and '__pycache__'not in str(p)and not p.name.endswith('.tmp'):initial.add(str(p.relative_to(ROOT)))
 initial.add(str(Path(__file__).relative_to(ROOT)))
 for rel in sorted(initial):add(ROOT/rel)
 for r in prior['referenceVersions']:bind(r['path'],r['sha256'],'exact inherited v4 referenceVersions')
 for r in prior['exactReferencedTrackedInputs']:bind(r['path'],r['sha256'],'exact inherited v4 tracked cache')
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
 assert not(initial&leaves);out=dict(closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p)for p in sorted(paths)],referenceVersions=sorted(versions.values(),key=lambda x:(x['path'],x['sha256'])),exactReferencedTrackedInputs=sorted(cached.values(),key=lambda x:x['path']),historicalManifestAliases=aliases,metadataLeafPaths=sorted(leaves),metadataLeafJsonPointers=pointers,auditDeclarationContextRefs=sorted(audit.values(),key=lambda x:x['path']),unboundExactReferenceVersions=unknown,declaredReferencesClosed=not unknown,explicitInitialPaths=sorted(initial),sourceOnly=True,currentAcceptance=False,installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges=0,newMetadataLeaves=False,newHistoricalAliases=False,newMetadataPointerContract=False,currentCaptureCreated=False,completedCurrentCaptureIncluded=False,priorD152CapturedBaselineHistoricalOnly=True,priorV3CurrentManifestHistoricalOnly=prior['priorV3CurrentManifestHistoricalOnly'],explicitUIDs=['landsd/240332:0'],protectedDistinctInstalledUID='landsd/240527:0',allPriorEvidenceAndSeparateHeldStatePreserved=True,modelReviewWrites=0,pointerWrites=0,rootIndependentClosureRequired=True,elapsedSeconds=time.monotonic()-start,qualification='Completed-only nine additional historical-source terrain-route jobs: causal55 exact seams; atomic one-ring and actual outer-ground; necessary anchors; failed coarse pinch-local layer; strict clipped10m candidate rejection; complete outer exact/F32 layer encoding; completed native-only cached audit; actual finite native-union original source coverage/topology. All raw307 source/current seams, incompatible pinches/branches, two real F32 node conflicts,771 native overlaps and50 east-fringe coverage/494 originalsource overlap failures remain exact and unwaived. Unknown earlier interruptions and explicit agent-controlled v3 SIGTERM remain distinct; completed1797 native chunks receive native-only audit credit while partialsource chunks receive no full qualification. Source640/109339 original provenance and current15456/783 failures, 14body obligations, protected240527 and all affected actors remain unchanged. No successful terrain candidate, current/identity/root/role/native/support/installation approval, new model/terrain geometry or current capture. Only actually completed frozen jobs and their true numerical/source dependencies are included; future adjacent-directory/494-plane attribution or candidate drafts are excluded. Exact priorv4 historical aliases/typedmetadata/leaves/cache contracts inherited without additions.')
 save(DOC/'declared-scope.json',out);print(json.dumps(dict(initial=len(initial),closedPaths=len(paths),tracked=len(cached),versions=len(versions),unknown=len(unknown),firstUnknown=unknown[:5],elapsedSeconds=out['elapsedSeconds'])),flush=True)
if __name__=='__main__':main()
