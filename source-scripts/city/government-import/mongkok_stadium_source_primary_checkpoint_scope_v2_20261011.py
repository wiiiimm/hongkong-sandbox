"""DRAFT completed Stadium original attribution/plots and bounded four-resource LCSD primary context.
Keeps prior v3 exact aliases/leaves/four typed pointers/audit contracts unchanged.
No mutable capture, new metadata routing exception, stage or installation evidence.
"""
import ast,json,subprocess,time
from pathlib import Path
from run import ROOT,HERE,read,save,digest
B=ROOT/'docs/astra-city/government-import';PRIOR=B/'government-xl-mongkok-stadium-source-primary-checkpoint-v1-20261011/declared-scope.json';DOC=B/'government-xl-mongkok-stadium-source-primary-checkpoint-v2-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 start=time.monotonic();assert not DOC.exists();prior=read(PRIOR);assert prior['declaredReferencesClosed']and not prior['unboundExactReferenceVersions'];aliases=prior['historicalManifestAliases'];leaves=set(prior['metadataLeafPaths']);pointers=prior['metadataLeafJsonPointers'];pointermap={(x['path'],x['boundary']['pointer']):x for x in pointers};archive={(a['originalPath'],a['sha256']):ROOT/a['archive']['path']for a in aliases};tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0'));initial=set(prior['closedPaths']);paths=set();queue=[];seen=set();hashes={};versions={};cached={};unknown=[];audit={r['path']:r for r in prior['auditDeclarationContextRefs']};audit[str(PRIOR.relative_to(ROOT))]=ref(PRIOR)
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
 folders=['government-xl-mongkok-stadium-original62-face-profile-primary-registration-v2-20261011','government-xl-mongkok-stadium-complete-original-far-extent-body-attribution-v1-20261011','government-xl-mongkok-stadium-bounded-official-lcsd-primary-context-v1-20261011']
 for folder in folders:
  r=read(B/folder/'result.json');assert not r.get('currentAcceptance',False)
  for base in [B/folder,HERE/'local'/folder]:
   if base.exists():
    for p in base.rglob('*'):
     if p.is_file()and '__pycache__'not in str(p):initial.add(str(p.relative_to(ROOT)))
 for folder in ['government-xl-mongkok-stadium-original62-face-profile-primary-registration-method-v2-20261011','government-xl-mongkok-stadium-complete-original-source-visual-context-v2-20261011','government-xl-mongkok-stadium-original-extent-membership-method-v1-20261011','government-xl-mongkok-stadium-original-source-visual-primary-method-v2-20261011','government-xl-mongkok-stadium-source-primary-checkpoint-method-v1-20261011']:
  for p in (B/folder).rglob('*'):
   if p.is_file():initial.add(str(p.relative_to(ROOT)))
 for n in ['mongkok_stadium_original62_face_profile_primary_registration_v2_20261011.py','mongkok_stadium_freeze_original62_face_profile_primary_registration_v2_20261011.py','mongkok_stadium_complete_original_far_extent_body_attribution_v1_20261011.py','mongkok_stadium_freeze_complete_original_far_extent_body_attribution_v1_20261011.py','mongkok_stadium_complete_original_source_visual_context_v2_20261011.py','mongkok_stadium_bounded_official_lcsd_primary_context_v1_20261011.py','mongkok_stadium_freeze_bounded_official_lcsd_primary_context_v1_20261011.py',Path(__file__).name]:initial.add(str((HERE/n).relative_to(ROOT)))
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
 assert not(initial&leaves);out=dict(closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p)for p in sorted(paths)],referenceVersions=sorted(versions.values(),key=lambda x:(x['path'],x['sha256'])),exactReferencedTrackedInputs=sorted(cached.values(),key=lambda x:x['path']),historicalManifestAliases=aliases,metadataLeafPaths=sorted(leaves),metadataLeafJsonPointers=pointers,auditDeclarationContextRefs=sorted(audit.values(),key=lambda x:x['path']),unboundExactReferenceVersions=unknown,declaredReferencesClosed=not unknown,explicitInitialPaths=sorted(initial),sourceOnly=True,currentAcceptance=False,installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges=0,newMetadataLeaves=False,newHistoricalAliases=False,newMetadataPointerContract=False,currentCaptureCreated=False,priorV3CurrentManifestHistoricalOnly=prior['priorV3CurrentManifestHistoricalOnly'],explicitUIDs=['landsd/240332:0'],protectedDistinctInstalledUID='landsd/240527:0',allPriorEvidenceAndSeparateHeldStatePreserved=True,modelReviewWrites=0,pointerWrites=0,rootIndependentClosureRequired=True,elapsedSeconds=time.monotonic()-start,qualification='Completed exact original62face Fraction plane/104edge rise profile plus complete15456-facet14-body15zero source footprint accounting, preserving full350.641m2 outside union and nonadditive per-facet/body areas; original descriptive projection union area>1e-10 mask retained with all excluded IDs and all source facets separately accounted, no numerical finite-credit exemption. Five bodies0/3/11/12/13 have outside projections, nine bodies zerooutside but allroles/mounts unqualified. Add actual frozen source-only profile job only; no future cross-body inventory/current proof. Completed original Stadium15456face14genuinebody15zero62far-face attribution, unchanged whole original source plots with explicit southwest orientation erratum, and four exact LCSD resources/two HTTP readers/four unwarped original page exports. All geometric paths are descriptive only. Primary images actually viewed separately; original feature correspondence, UID/height/function/ownership/support and extent qualification remain unresolved. Full historical identity failure12.871m/62farfacets/350.641m2source excess survives; no current membership/ground/foreign/native/runtime capture or installation credit. Separate installed240527 protected. Exact Museumv6 aliases/leaves/four metadata contracts inherited unchanged; all new actual source/numerical/primary HTTP/image/producer inputs explicitly recursively closed.')
 save(DOC/'declared-scope.json',out);print(json.dumps(dict(initial=len(initial),closedPaths=len(paths),tracked=len(cached),versions=len(versions),unknown=len(unknown),firstUnknown=unknown[:5],elapsedSeconds=out['elapsedSeconds'])),flush=True)
if __name__=='__main__':main()
