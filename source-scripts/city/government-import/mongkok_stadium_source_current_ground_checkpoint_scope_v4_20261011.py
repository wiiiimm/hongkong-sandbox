"""DRAFT additive completed Stadium current ground/finite/plane/cachedTIN slice.
One actual archived d152manifest alias; existing typedmetadata/leaf/cache contracts unchanged.
No future proposal/seam/stage/installation credit.
"""
import ast,json,subprocess,time
from pathlib import Path
from run import ROOT,HERE,read,save,digest
B=ROOT/'docs/astra-city/government-import';PRIOR=B/'government-xl-mongkok-stadium-source-primary-checkpoint-v3-20261011/declared-scope.json';DOC=B/'government-xl-mongkok-stadium-source-current-ground-checkpoint-v4-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 start=time.monotonic();assert not DOC.exists();prior=read(PRIOR);assert prior['declaredReferencesClosed']and not prior['unboundExactReferenceVersions'];aliases=list(prior['historicalManifestAliases']);archiveproof=read(HERE/'local/government-xl-mongkok-stadium240332-actual-current-byte-archives-v1-20261011/archive-proof.json');actualarchive=ROOT/archiveproof['actualArchive']['path'];assert ref(actualarchive)==archiveproof['actualArchive'] and archiveproof['historicalSHA256']=='d152dca423d23b3bdb21a06786dd01980a5ab86b8bab75646d2ee6cd0a387c43';newalias=dict(originalPath=archiveproof['originalPath'],sha256=archiveproof['historicalSHA256'],archive=archiveproof['actualArchive']);assert not any(a['originalPath']==newalias['originalPath']and a['sha256']==newalias['sha256']for a in aliases);aliases.append(newalias);leaves=set(prior['metadataLeafPaths']);pointers=prior['metadataLeafJsonPointers'];pointermap={(x['path'],x['boundary']['pointer']):x for x in pointers};archive={(a['originalPath'],a['sha256']):ROOT/a['archive']['path']for a in aliases};tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0'));initial=set(prior['closedPaths']);paths=set();queue=[];seen=set();hashes={};versions={};cached={};unknown=[];audit={r['path']:r for r in prior['auditDeclarationContextRefs']};audit[str(PRIOR.relative_to(ROOT))]=ref(PRIOR)
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
 folders=['government-xl-mongkok-stadium240332-complete-current-ground-capture-v1-20261011','government-xl-mongkok-stadium240332-complete-current-finite-ground-diagnostic-v1-20261011','government-xl-mongkok-stadium240332-buried-original-body-plane-attribution-v1-20261011','government-xl-mongkok-stadium240332-complete-original-authentic-tin-finite-v1-20261011']
 for folder in folders:
  r=read(B/folder/'result.json');assert r['sourceOnly']and not r.get('currentAcceptance',False)
  for base in [B/folder,HERE/'local'/folder]:
   if base.exists():
    for p in base.rglob('*'):
     if p.is_file()and '__pycache__'not in str(p):initial.add(str(p.relative_to(ROOT)))
 for folder in ['government-xl-mongkok-stadium-all14body-current-grounding-acceptance-or-hold-method-v1-20261011','government-xl-mongkok-stadium240332-complete-original-authentic-tin-method-v1-20261011','government-xl-mongkok-stadium240332-original-buried-groups-current-ground-context-v1-20261011']:
  for p in (B/folder).rglob('*'):
   if p.is_file():initial.add(str(p.relative_to(ROOT)))
 for folder in ['government-xl-mongkok-stadium240332-current-ground-reservation-v1-20261011','government-xl-mongkok-stadium240332-current-finite-reservation-v1-20261011','government-xl-mongkok-stadium240332-actual-current-byte-archives-v1-20261011']:
  for p in (HERE/'local'/folder).rglob('*'):
   if p.is_file():initial.add(str(p.relative_to(ROOT)))
 for n in ['mongkok_stadium240332_complete_current_ground_capture_v1_20261011.py','mongkok_stadium240332_current_actual_render_attributes_v1_20261011.mjs','mongkok_stadium240332_capture_module_closures_v1_20261011.mjs','mongkok_stadium240332_freeze_complete_current_ground_v1_20261011.py','mongkok_stadium240332_complete_current_finite_ground_diagnostic_v1_20261011.py','mongkok_stadium240332_freeze_complete_current_finite_ground_v1_20261011.py','mongkok_stadium240332_buried_original_body_plane_attribution_v1_20261011.py','mongkok_stadium240332_freeze_buried_original_body_plane_attribution_v1_20261011.py','mongkok_stadium240332_complete_original_authentic_tin_finite_v1_20261011.py','mongkok_stadium240332_freeze_complete_original_authentic_tin_finite_v1_20261011.py','mongkok_stadium240332_original_buried_groups_current_ground_context_v1_20261011.py',Path(__file__).name]:initial.add(str((HERE/n).relative_to(ROOT)))
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
 assert not(initial&leaves);out=dict(closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p)for p in sorted(paths)],referenceVersions=sorted(versions.values(),key=lambda x:(x['path'],x['sha256'])),exactReferencedTrackedInputs=sorted(cached.values(),key=lambda x:x['path']),historicalManifestAliases=aliases,metadataLeafPaths=sorted(leaves),metadataLeafJsonPointers=pointers,auditDeclarationContextRefs=sorted(audit.values(),key=lambda x:x['path']),unboundExactReferenceVersions=unknown,declaredReferencesClosed=not unknown,explicitInitialPaths=sorted(initial),sourceOnly=True,currentAcceptance=False,installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges=0,newMetadataLeaves=False,newHistoricalAliases=True,newMetadataPointerContract=False,currentCaptureCreated=False,completedCurrentCaptureIncluded=True,priorD152CapturedBaselineHistoricalOnly=True,priorV3CurrentManifestHistoricalOnly=prior['priorV3CurrentManifestHistoricalOnly'],explicitUIDs=['landsd/240332:0'],protectedDistinctInstalledUID='landsd/240527:0',allPriorEvidenceAndSeparateHeldStatePreserved=True,modelReviewWrites=0,pointerWrites=0,rootIndependentClosureRequired=True,elapsedSeconds=time.monotonic()-start,qualification='Completed whole15456original/14body/15zero actual current217ground/fourstream capture; allfour streams retain783ordinaryfinite negatives, coverage0/min-2.036625m. Exact original plane/body/Y attribution gives no foundation intent/role credit. Complete original15456 versus cached11NW14D sourceTIN640selected from109339whole source passesordinary finite withzero failures/coveragefailures; coarse488strict-uncertified is not actualburial. Actualfailedsource/currentground context plots separately viewed, no universalfoundation inference or lowering approval. Four completedsource-only frozenjobs only; allprior original62extent/350.641outside/14body/propercrossings/foreign/native/runtime and installed240527 protections retained. Actuald152manifest bytes independently archived as one new exacthistorical alias; no new metadata leaf/pointer contract. No future causal55domain/proposal/seam diagnostic evidence included, no mesh/sourceheight/terrain/identity/role/currentacceptance edits.')
 save(DOC/'declared-scope.json',out);print(json.dumps(dict(initial=len(initial),closedPaths=len(paths),tracked=len(cached),versions=len(versions),unknown=len(unknown),firstUnknown=unknown[:5],elapsedSeconds=out['elapsedSeconds'])),flush=True)
if __name__=='__main__':main()
