"""DRAFT merged authentic source-core provenance/domain inventory; no candidate.
Complete protected240527 actual patch footprint plus original Stadium640 whole TIN.
ROOT full-read before execution; all original model/terrain/current bytes unchanged.
"""
from pathlib import Path
from fractions import Fraction as F
import importlib.util,time,threading,json,numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_compute_transition_mesh_v1_20261011 import faces,project,positive_overlap_inventory
from exact_source_core_ten_metre_transition_domain_v1_20261011 import intersection,separated
from exact_resumable_projected_inventory_v1_20261011 import Checkpoints,overlaps as resumable_overlaps,atomic as resumable_atomic
from exact_original_projection_coverage_v2_20261010 import signed_area,subtract
B=ROOT/'docs/astra-city/government-import';NAME='government-xl-mongkok-stadium240332-merged-protected-patch-authentic-core-inventory-v3-20261011';DOC=B/NAME;LOCAL=HERE/'local'/NAME;AUTH=B/'government-xl-mongkok-stadium240332-complete-original-authentic-tin-finite-v1-20261011';PRE=B/'government-xl-mongkok-stadium240332-ten-metre-clipped-transition-candidate-v1-20261011';OUTER=B/'government-xl-mongkok-stadium240332-complete-outer-layer-encoding-inventory-v1-20261011';TIN=HERE/'local/government-xl-50-second-20260913/sheets/11-NW-14D/terrain/TERRAIN(TB)/T35250204000106E13/T35250204000106E13.gltf';PIN='d152dca423d23b3bdb21a06786dd01980a5ab86b8bab75646d2ee6cd0a387c43'
ARCHIVE=HERE/'local/government-xl-mongkok-stadium240332-actual-current-byte-archives-v1-20261011/manifest-actual-d152dca4.json'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def resolved_ref(e):
 if e==dict(path='3d-viewer/city/data/manifest.json',sha256=PIN):
  a=ref(ARCHIVE);assert a['sha256']==PIN;return a
 p=ROOT/e['path'];assert p.is_file()and ref(p)==e;return e
def serial(x):
 if isinstance(x,F):return str(x)
 if isinstance(x,(list,tuple)):return [serial(v)for v in x]
 if isinstance(x,dict):return {k:serial(v)for k,v in x.items()}
 return x

def fenced_inputs(bindings):
 def check():assert all(ref(ROOT/e['path'])==e for e in bindings),'Changed exact chunk input'
 return check

def main():
 started=time.monotonic();assert not DOC.exists();refs=[ref(Path(__file__)),ref(B/'government-xl-mongkok-stadium240332-merged-authentic-core-method-v1-20261011/METHOD.md'),ref(B/'government-xl-mongkok-stadium240332-resumable-merged-authentic-core-method-v3-20261011/METHOD.md')]
 for folder in [AUTH,PRE,OUTER]:
  r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for e in r['evidenceRefs']:refs.append(resolved_ref(e))
  refs.extend(ref(folder/n)for n in ['result.json','diagnostic.json.gz'])
 manifest=ARCHIVE;before=ref(manifest);assert before['sha256']==PIN;entry=next(e for e in read(manifest)['terrainPatches']if e['url']=='city/data/government-native-240527-0.json');p=ROOT/'3d-viewer'/entry['url'];assert ref(p)['sha256']==entry['sha256'];patch=read(p);assert patch['meta']['targetUids']==['landsd/240527:0']and patch['coarseCells']==[510,388,514,390];assert patch['meta']['source']['nativeSources'][0]['sheet']=='11-NW-14D';refs.extend([before,ref(p),ref(HERE/'local/government-xl-mongkok-stadium240332-actual-current-byte-archives-v1-20261011/archive-proof.json'),ref(HERE/'local/government-xl-mongkok-stadium240332-merged-protected-patch-authentic-core-inventory-v1-20261011/supervised-interrupted-attempt.json'),ref(HERE/'local/government-xl-mongkok-stadium240332-merged-protected-patch-authentic-core-inventory-v2-20261011/supervised-interrupted-attempt.json')])
 g=read(PRE/'complete-current-ground.json.gz');raw=patch['nativeMesh'];position=np.asarray(raw['position'],dtype='<f4').reshape(-1,3);index=np.asarray(raw['index'],dtype='<u4').reshape(-1,3)
 for i,f in enumerate(index):
  a,b,c=position[f].astype('<f8');y=(b[2]-a[2])*(c[0]-a[0])-(b[0]-a[0])*(c[2]-a[2])
  if y<0:index[i,1],index[i,2]=index[i,2],index[i,1]
 mesh=g['completeGlobalActualMeshes'][175];assert len(index)==16297 and digest(position.tobytes())==mesh['actualPositionAttributeSHA256']and digest(index.tobytes())==mesh['actualIndexAttributeSHA256'];actual=position[index].astype('<f8');lo=actual.min((0,1));hi=actual.max((0,1));assert [lo[0],lo[2],hi[0],hi[2]]==[1232.5,-4307.5,1512.5,-4167.5]
 rect=[(F(float(lo[0])),F(float(lo[2]))),(F(float(hi[0])),F(float(lo[2]))),(F(float(hi[0])),F(float(hi[2]))),(F(float(lo[0])),F(float(hi[2])))];af=faces(actual);zero=[i for i,f in enumerate(af)if not signed_area([(q[0],q[2])for q in f])];nonzero=[f for i,f in enumerate(af)if i not in set(zero)];polys=[project(f)for f in nonzero];summed_area=sum(signed_area(q)for q in polys);chunkbindings=[before,ref(p),ref(Path(__file__))]+[ref(HERE/n)for n in ['exact_resumable_projected_inventory_v1_20261011.py','exact_compute_transition_mesh_v1_20261011.py','exact_source_core_ten_metre_transition_domain_v1_20261011.py','exact_original_projection_coverage_v2_20261010.py','exact_atomic_terrain_domain_boundary_ring_v1_20261011.py','run.py']];nativecheck=Checkpoints(LOCAL/'native-projection-checkpoints',polys,chunkbindings,fenced_inputs(chunkbindings));nativebad,nativeaccounting=resumable_overlaps(polys,nativecheck);overlaps=[dict(faces=r['pieces'],exactPositiveProjectedOverlapM2=r['exactPositiveOverlapM2'])for r in nativebad];footprint_proved=not overlaps and summed_area==signed_area(rect)
 # A finite closed projected triangle union contained in the exact rectangle,
 # with no positive overlaps and equal area, covers that closed rectangle.
 # If the native projection fails this theorem, retain every failure; no waiver.
 assert all(lo[0]<=float(q[0])<=hi[0]and lo[2]<=float(q[1])<=hi[2]for poly in polys for q in poly)
 source=read(HERE/'local'/AUTH.name/'complete-original-tin-covering-whole-facets.json.gz');refs.append(ref(HERE/'local'/AUTH.name/'complete-original-tin-covering-whole-facets.json.gz'));assert len(source['completeSelectedFacetIds'])==640 and all(ref(ROOT/e['path'])==e for e in source['sourceFiles']);assert {(e['path'],e['sha256'])for e in source['sourceFiles']}=={(e['path'],e['sha256'])for e in patch['meta']['source']['nativeSources'][0]['sourceFiles']};assert patch['meta']['source']['nativeSources'][0]['sourceETag']==source['sourceETag'];refs.extend(source['sourceFiles']);spec=importlib.util.spec_from_file_location('merged_original_tin_decoder',HERE/'xl-second-pass.py');decoder=importlib.util.module_from_spec(spec);spec.loader.exec_module(decoder);decoder.LOCAL=LOCAL;whole=decoder.terrain_triangles(TIN);assert whole.shape==(109339,3,3)and digest(whole.tobytes())==source['completeOriginalSheetSHA256'];keep=set(source['completeSelectedFacetIds']);patch_positive=[];zero_original_broadphase=[];box=(whole[:,:,0].max(1)>=lo[0])&(whole[:,:,0].min(1)<=hi[0])&(whole[:,:,2].max(1)>=lo[2])&(whole[:,:,2].min(1)<=hi[2])
 for i in np.flatnonzero(box):
  f=faces(whole[i:i+1])[0]
  if not signed_area([(q[0],q[2])for q in f]):zero_original_broadphase.append(int(i));continue
  poly=project(f);area=signed_area(intersection(poly,rect))
  if area:keep.add(int(i));patch_positive.append(dict(originalSheetFacet=int(i),exactPositiveOverlapWithProtectedPatchFootprintM2=area))
 ids=sorted(keep);selected=whole[ids];selected_polys=[project(f)for f in faces(selected)];remaining=[rect]
 for poly in selected_polys:
  remaining=[p for q in remaining for p in ([q]if separated(q,poly)else subtract(q,poly))]
  if not remaining:break
 sourcebindings=chunkbindings+source['sourceFiles'];sourcecheck=Checkpoints(LOCAL/'source-atomic-checkpoints',selected_polys,sourcebindings,fenced_inputs(sourcebindings));topology,sourceaccounting=resumable_atomic(selected_polys,sourcecheck);qualified=footprint_proved and not remaining and topology['projectedTopologyQualified'];save(LOCAL/'merged-authentic-whole-source-facets.json.gz',dict(completeOriginalSheetFacets=109339,completeOriginalSheetSHA256=digest(whole.tobytes()),completeSelectedOriginalSheetFacetIds=ids,completeSelectedOriginalFacets=selected.tolist(),completeSelectedOriginalSHA256=digest(selected.tobytes()),sourceFiles=source['sourceFiles'],sourceRevision=source['sourceRevision'],sourceETag=source['sourceETag'],selection='Every whole authentic facet with positive finite projected intersection against complete protected240527 actual footprint rectangle, union all prior Stadium640 authentic facet IDs. No bounding rectangle invented from actor guesses, source heights changed or source facets clipped.'))
 refs.extend([ref(PRE/'complete-current-ground.json.gz'),ref(LOCAL/'merged-authentic-whole-source-facets.json.gz'),ref(HERE/'xl-second-pass.py'),ref(HERE/'exact_resumable_projected_inventory_v1_20261011.py'),ref(HERE/'test_exact_resumable_projected_inventory_v1_20261011.py')]);refs.extend(ref(q)for q in sorted((LOCAL/'terrain-repairs').rglob('*'))if q.is_file())
 assert ref(manifest)==before and all(ref(ROOT/e['path'])==e for e in refs)
 save(DOC/'diagnostic.json.gz',serial(dict(uid='landsd/240332:0',protectedUID='landsd/240527:0',sourceOnly=True,currentAcceptance=False,terrainCandidateCreated=False,historicalCapturedBaselineOnly=True,historicalManifestBinding=dict(originalPath='3d-viewer/city/data/manifest.json',historicalSHA256=PIN,actualArchive=before),originalSourceGeometryChanges=0,liveTerrainChanges=0,completeProtectedPatchFacets=16297,completePatchActualPositionSHA256=digest(position.tobytes()),completePatchActualIndexSHA256=digest(index.tobytes()),completeProjectedFootprintRectangle=rect,allZeroProjectedNativeFacetIds=zero,completeNonzeroNativeOriginalFacetIds=[i for i in range(len(af))if i not in set(zero)],summedPositiveNativeProjectedAreaM2=summed_area,rectangleProjectedAreaM2=signed_area(rect),allNativePositiveProjectedOverlaps=overlaps,completeNativeProjectionPairAccounting=nativeaccounting,completeSourceAtomicPairAccounting=sourceaccounting,exactResumableChunkSchema='exact-projected-inventory-v1',completeActualPatchClosedRectangleFootprintProved=footprint_proved,completeSourceTINFacets=109339,priorStadiumWholeSourceFacets=640,protectedPatchPositiveOriginalSourceFacets=patch_positive,allZeroProjectedOriginalSourceFacetsInCompletePatchBroadphase=zero_original_broadphase,completeMergedWholeOriginalSourceFacets=len(selected),mergedWholeSourceXZBounds=[selected[:,:,0].min(),selected[:,:,2].min(),selected[:,:,0].max(),selected[:,:,2].max()],allUncoveredProtectedPatchProjectedPolygons=remaining,completeMergedOriginalAtomicTopology=topology,mergedCoreProvenanceAndProjectionQualified=qualified,evidenceRefs=refs,elapsedSeconds=time.monotonic()-started,qualification='Historical source-only complete projected footprint/source provenance inventory at exact archivedd152 baseline, not a fresh current capture/numerical terrain candidate or ground/support/current/native acceptance. Later distantKing publication does not alter these bound source/nativepatch bytes; no current globalunchanged claim. Complete existing protected240527 mesh and masks define the bounded recovered patch; original whole109339-sheet facets remain exact and union prior640source core without newbuilding geometry. Existing rational/F32 outer conflicts and all783failures remain immutable. A later bounded10m compute transition outside this genuine merged core requires new complete production terrain/current forms/native masks capture plus exact source-core3D/actualF32 seams, every full source/protected240527/foreign/native ground/grade/support/water/runtime gate.')))
if __name__=='__main__':
 stopped=threading.Event();started=time.monotonic()
 def progress():
  while not stopped.wait(20):print(json.dumps(dict(activeHistoricalSourceInventory=True,resumableChunks=True,elapsedSeconds=time.monotonic()-started,completed=False,currentAcceptance=False)),flush=True)
 threading.Thread(target=progress,daemon=True).start()
 try:main()
 finally:stopped.set()
