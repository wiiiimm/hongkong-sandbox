"""DRAFT additive completed Science Museum fresh source search/acquisition/comparison; execute after both jobs frozen.
Keeps prior v3 exact aliases/leaves/four typed pointers/audit contracts unchanged.
No mutable capture, new metadata routing exception, stage or installation evidence.
"""
import ast,json,subprocess,time
from pathlib import Path
from run import ROOT,HERE,read,save,digest
B=ROOT/'docs/astra-city/government-import';PRIOR=B/'government-xl-science-museum-original-visual-uv-source-checkpoint-v3-20261011/declared-scope.json';DOC=B/'government-xl-science-museum-original-mount-grade-source-checkpoint-v4-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 start=time.monotonic();assert not DOC.exists();prior=read(PRIOR);assert prior['declaredReferencesClosed']and not prior['unboundExactReferenceVersions'];aliases=prior['historicalManifestAliases'];leaves=set(prior['metadataLeafPaths']);pointers=prior['metadataLeafJsonPointers'];pointermap={(x['path'],x['boundary']['pointer']):x for x in pointers};archive={(a['originalPath'],a['sha256']):ROOT/a['archive']['path']for a in aliases};tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0'));initial=set(prior['closedPaths']);paths=set();queue=[];seen=set();hashes={};versions={};cached={};unknown=[];audit={r['path']:r for r in prior['auditDeclarationContextRefs']};audit[str(PRIOR.relative_to(ROOT))]=ref(PRIOR)
 for p in (B/'government-xl-science-museum-original-open-sided-source-checkpoint-v1-20261011').rglob('*'):
  if p.is_file():audit[str(p.relative_to(ROOT))]=ref(p)
 audit[str((HERE/'science_museum_original_open_sided_source_checkpoint_scope_v1_20261011.py').relative_to(ROOT))]=ref(HERE/'science_museum_original_open_sided_source_checkpoint_scope_v1_20261011.py')
 for p in (B/'government-xl-science-museum-open-sided-original-gltf-identity-comparison-v2-20261011').rglob('*'):
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
 folders=['government-xl-science-museum-original171-cross-body-contact-inventory-v1-20261011','government-xl-science-museum-original171-bounded-mount-grade-context-v1-20261011','government-xl-science-museum-open-sided-fresh-official-allclass-directory-search-v1-20261011','government-xl-science-museum-open-sided-original-gltf-members-acquisition-v1-20261011','government-xl-science-museum-open-sided-original-gltf-identity-comparison-v3-20261011','government-xl-science-museum-original-open-sided-contact-topology-attribution-v1-20261011','government-xl-science-museum-original-raw-uv-body-atlas-registration-v1-20261011']
 for folder in folders:
  r=read(B/folder/'result.json');assert not r.get('currentAcceptance',False)
  for base in [B/folder,HERE/'local'/folder]:
   if base.exists():
    for p in base.rglob('*'):
     if p.is_file()and '__pycache__'not in str(p):initial.add(str(p.relative_to(ROOT)))
 visual=B/'government-xl-science-museum-original-source-visual-registration-context-v1-20261011';assert read(visual/'context.json')['sourceOnly']and not read(visual/'context.json')['currentAcceptance']
 for p in visual.rglob('*'):
  if p.is_file():initial.add(str(p.relative_to(ROOT)))
 for p in (B/'government-xl-science-museum-sampler-primary-entrance-source-review-v1-20261011').rglob('*'):
  if p.is_file():initial.add(str(p.relative_to(ROOT)))
 for folder in ['government-xl-science-museum-original171-bounded-mount-grade-method-v1-20261011','government-xl-science-museum-open-sided-fresh-official-allclass-source-search-method-v1-20261011','government-xl-science-museum-open-sided-original-source-acquisition-method-v1-20261011','government-xl-science-museum-open-sided-original-source-comparison-method-v2-20261011','government-xl-science-museum-open-sided-original-source-comparison-method-v3-20261011','government-xl-science-museum-original-open-sided-contact-topology-method-v1-20261011','government-xl-science-museum-primary-existing-plan-entrance-registration-method-v1-20261011']:
  for p in (B/folder).rglob('*'):
   if p.is_file():initial.add(str(p.relative_to(ROOT)))
 for n in ['science_museum_original171_cross_body_contact_inventory_v1_20261011.py','science_museum_freeze_original171_cross_body_contact_inventory_v1_20261011.py','science_museum_original171_bounded_mount_grade_context_v1_20261011.py','science_museum_freeze_original171_bounded_mount_grade_context_v1_20261011.py','science_museum_open_sided_fresh_official_allclass_directory_search_v1_20261011.py','science_museum_freeze_fresh_official_allclass_directory_search_v1_20261011.py','science_museum_open_sided_original_gltf_members_acquisition_v1_20261011.py','science_museum_open_sided_original_gltf_identity_comparison_v1_20261011.py','science_museum_open_sided_original_gltf_identity_comparison_v2_20261011.py','science_museum_open_sided_original_gltf_identity_comparison_v3_20261011.py','science_museum_freeze_original_gltf_acquisition_comparison_v1_20261011.py','science_museum_freeze_original_gltf_acquisition_comparison_v2_20261011.py','science_museum_freeze_original_gltf_acquisition_comparison_v3_20261011.py','test_science_museum_original_gltf_decoder_v3_20261011.py','science_museum_original_open_sided_contact_topology_attribution_v1_20261011.py','science_museum_freeze_original_contact_topology_attribution_v1_20261011.py','test_science_museum_contact_relative_interior_v1_20261011.py','science_museum_original_source_visual_registration_context_v1_20261011.py','science_museum_original_raw_uv_body_atlas_registration_v1_20261011.py','science_museum_freeze_original_raw_uv_body_atlas_registration_v1_20261011.py',Path(__file__).name]:initial.add(str((HERE/n).relative_to(ROOT)))
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
 assert not(initial&leaves);out=dict(closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p)for p in sorted(paths)],referenceVersions=sorted(versions.values(),key=lambda x:(x['path'],x['sha256'])),exactReferencedTrackedInputs=sorted(cached.values(),key=lambda x:x['path']),historicalManifestAliases=aliases,metadataLeafPaths=sorted(leaves),metadataLeafJsonPointers=pointers,auditDeclarationContextRefs=sorted(audit.values(),key=lambda x:x['path']),unboundExactReferenceVersions=unknown,declaredReferencesClosed=not unknown,explicitInitialPaths=sorted(initial),sourceOnly=True,currentAcceptance=False,installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges=0,newMetadataLeaves=False,newHistoricalAliases=False,newMetadataPointerContract=False,currentCaptureCreated=False,priorV3CurrentManifestHistoricalOnly=prior['priorV3CurrentManifestHistoricalOnly'],explicitUIDs=['landsd/80343:0','landsd/83471:0'],allPriorEvidenceAndSeparateHeldStatePreserved=True,modelReviewWrites=0,pointerWrites=0,stableCSUIDObjectRenumberingPreserved=True,sourceFamilyCoverageDifferencePreserved=True,sourceTexturesPreserved=True,rootIndependentClosureRequired=True,elapsedSeconds=time.monotonic()-start,qualification='Distinct additive complete original171 cross-body finite inventory, all17 proper internal crossing face/UV attributions, complete5body original shell/self-intersection and reviewed minimum-opening failures, historical-only24Museumbody minimum-edge grade context. No whole-native/body/root/current/architecture role approval. All original raw self-intersections, nonmanifold/winding/opening failures retained. Prior actual unchanged source scientific plan/3D context plots and complete171face rawUV/index/material/image bindings, preserving5body+3zero53crossing/primary-registration obligations. Atlas and originalgeometry unmodified; no pixelwarp/source-role/physical-attachment/current acceptance. Inherited source-only Science Museum exact stableCSUID fresh official index/directory search, unique individualised original four-member acquisition with full textures, preserved v2 unsigned-byte parser failure, corrected independently tested complete171face v3 raw original source comparison. Complete5nonzero source bodies and3zero faces,76noncoplanar/20coplanar contacts including53both-relative-interior surface-crossing diagnostics (not solid penetration/attachment claims), primary context and exact historicalBASIC footprint/estimatedheight attribution, all96positive surface pairs,16point pairs,90.75percent official footprint coverage,63historical overlapfaces and1.855m2 raw guard retained. No packing/source pose change/current capture/identity acceptance/role/model-review/pointer/installation credit. Reuse exact inherited metadata contracts only, with all actual new source and numerical dependencies recursively bound.')
 save(DOC/'declared-scope.json',out);print(json.dumps(dict(initial=len(initial),closedPaths=len(paths),tracked=len(cached),versions=len(versions),unknown=len(unknown),firstUnknown=unknown[:5],elapsedSeconds=out['elapsedSeconds'])),flush=True)
if __name__=='__main__':main()
