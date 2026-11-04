"""Current/source-bound changed terrain core/apron proposal, no physical approval."""
import importlib.util,json
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from native_parent_child_flat_composition_20261010 import faces
from vancor_current_basic_parent_apron_candidate_v2_20261011 import propose
from exact_original_slab_projection_coverage_20261010 import slab_coverage
from exact_original_polygon_triangle_partition_20261010 import exact_partition
from exact_native_upper_surface_pair_seam_v3_20261010 import verify_pair
import native_patch_resolution as patches
BATCH='government-xl-vancor-basic-parent-core-apron-terrain-proposal-v2-20261011';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH
BASE=DOC.parent;PHYSICAL=BASE/'government-xl-vancor-authentic-tin-retained-pak-shing-current-physical-v1-20261011';INPUT=BASE/'government-xl-vancor-authentic-tin-retained-pak-shing-current-inputs-v1-20261011';BASIC=BASE/'government-xl-vancor-basic-253697-whole-projection-diagnostic-v1-20261011';ACTUAL=BASE/'government-xl-vancor-own-retained-actual-render-capture-v1-20261011';CLIP=BASE/'government-xl-vancor-basic253697-exact-parent-clip-feasibility-v1-20261011'
MANIFEST='b61c0bc2d706793c7d436ef3334ccb41e93675d3d50c29818a2dca3b56f8830e'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists()and not LOCAL.exists();manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==MANIFEST
 receipts=[read(p/'result.json')for p in [PHYSICAL,INPUT,BASIC,ACTUAL,CLIP]]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for r in receipts:assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 required=[PHYSICAL/'terrain-candidates.json',PHYSICAL/'neighbour-checks.json',INPUT/'check-selection.json.gz',INPUT/'proposal-input.json',BASIC/'complete-current-basic-geometry.json.gz',BASIC/'diagnostic.json.gz',ACTUAL/'complete-actual-render-geometry.json.gz',ACTUAL/'diagnostic.json',CLIP/'diagnostic.json.gz']
 for p in required:assert any(ref(p)in r['evidenceRefs']for r in receipts),p
 original=read(PHYSICAL/'terrain-candidates.json');assert len(original)==1;original=original[0];candidatepath=ROOT/original['path'];assert ref(candidatepath)['sha256']==original['sha256'];candidate=read(candidatepath)
 inp=read(INPUT/'proposal-input.json');parentpath=ROOT/inp['retainedParent']['path'];assert ref(parentpath)==inp['retainedParent'];parent=read(parentpath)
 selection=read(INPUT/'check-selection.json.gz')['rows'][0];sourcepath=ROOT/selection['candidate']['path'];raw=sourcepath.read_bytes();assert digest(raw)==selection['sourceSHA256'];source=decode_original_world_triangles(raw);assert len(source)==669
 actual=read(ACTUAL/'complete-actual-render-geometry.json.gz');own=[r for r in actual['rows']if r['uid']==selection['uid']];assert len(own)==1;own=own[0];idx=np.asarray(own['completeOriginalIndex'],int).reshape(-1,3);assert len(idx)==669;streams={'providerOriginal':source}
 for mode,key in [('actualLiteral','completeLiteralWorldPosition'),('explicitLeftAssociatedF32ModelMatrix','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32ModelMatrix','completeExplicitBalancedFloat32WorldPosition')]:streams[mode]=np.asarray(own[key],dtype='<f8').reshape(-1,3)[idx]
 bc=read(BASIC/'complete-current-basic-geometry.json.gz');actor=bc['actor'];assert actor['uid']=='landsd/253697:0';position=np.asarray(actor['completePosition'],dtype='<f8').reshape(-1,3);index=np.asarray(actor['completeIndex'],int).reshape(-1,3);basic=position[index];assert len(basic)==48
 for captured in [actual,bc]:
  for p,h in captured['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p
 proposed,proof=propose(candidate,parent,streams,basic,actor['currentForm']['rings']);final=faces(proposed);assert len(final)==proof['finalTerrainFacets']<=100000
 basic_coverage=[dict(currentBasicFace=i,proof=slab_coverage(t,final))for i,t in enumerate(basic)]
 ringpoly=shapely.Polygon();
 for ring in actor['currentForm']['rings']:ringpoly=ringpoly.symmetric_difference(shapely.Polygon(ring))
 triangles=[list(t.exterior.coords)[:3]for t in shapely.get_parts(shapely.constrained_delaunay_triangles(ringpoly))];rings=[list(ringpoly.exterior.coords),*[list(r.coords)for r in ringpoly.interiors]];partition=exact_partition(rings,triangles);guard_coverage=[dict(currentGuardFootprintFace=i,proof=slab_coverage(np.asarray([[x,0,z]for x,z in t]),final))for i,t in enumerate(triangles)]
 outer=shapely.from_geojson(proof['declaredOuterEnvelopeGeoJSON']);seams=[]
 for ring_id,ring in enumerate([outer.exterior,*outer.interiors]):
  coordinates=list(ring.coords)
  for edge_id,(a,b)in enumerate(zip(coordinates,coordinates[1:])):seams.append(dict(completeOuterEnvelopeRing=ring_id,completeOuterEnvelopeEdge=edge_id,proof=verify_pair(np.asarray([[a[0],0,a[1]],[b[0],0,b[1]]]),faces(candidate),final)))
 # These are measured diagnostics, not acceptance assertions or waived gaps.
 complete_basic_covered=all(r['proof']['exactProjectionCovered']for r in basic_coverage);complete_guard_covered=all(r['proof']['exactProjectionCovered']for r in guard_coverage);outer_seam=all(r['proof']['passedCompleteFiniteUpperSeam']for r in seams)
 proposed['nativeMesh']['source']['currentBasicParentCoreApronChangedTerrain']=dict(currentBasicUID=actor['uid'],parent=ref(parentpath),priorCandidate=ref(candidatepath),completeActualRenderCapture=ref(ACTUAL/'complete-actual-render-geometry.json.gz'),declaredTransitionWidthM=.01,exactOriginalParentPlanePreservationClaimed=False,sourceBuildingGeometryChanges=0)
 target=LOCAL/'government-native-147956-0.json';save(target,proposed);auditpath=DOC/'explicit-changed-terrain-overlap-audit.json';sources=read(PHYSICAL/'terrain.json')['sourceFiles'];audit=patches.approve_original_overlap(proposed,target,auditpath,sources)
 audit['policy']='Explicit changed clipped-parent core and constrained apron use the highest current native surface; no exact original-plane preservation claim.';audit['float32HighestRayAgreement']['method']='Independent barycentric sampler and vertical plane-ray equations inside actual packed changed terrain facets; complete finite domain/seam/physical checks remain independent.';audit['changedTerrainProvenance']=dict(parent=ref(parentpath),priorCandidate=ref(candidatepath),constructor=ref(HERE/'vancor_current_basic_parent_apron_candidate_v2_20261011.py'),maxCorePackedParentHeightDeviationM=proof['maxCorePackedParentHeightDeviationM'],exactOriginalParentPlanePreservationClaimed=False)
 save(auditpath,audit);patches.finalize_overlap_evidence(proposed,auditpath);save(target,proposed)
 assert len(proposed['nativeMesh']['index'])//3==proof['finalTerrainFacets']<=100000
 revised={**original,'path':str(target.relative_to(ROOT)),'sha256':digest(target.read_bytes()),'triangles':proof['finalTerrainFacets']};save(DOC/'terrain-candidates.json',[revised]);out=dict(currentManifest=start,changedTerrainProposal=ref(target),proof=proof,rawPriorNeighbourFailure=read(PHYSICAL/'neighbour-checks.json')['rows'],completeActualBasicCoverage=basic_coverage,completeCurrentGuardFootprintPartition=partition,completeCurrentGuardFootprintCoverage=guard_coverage,completeOuterEnvelopeUpperSeams=seams,completeActualBasicCovered=complete_basic_covered,completeGuardFootprintCovered=complete_guard_covered,completeOuterEnvelopeUpperSeamWithinUnchanged2mm=outer_seam,sourceStreamSHA256s={k:digest(t.astype('<f8').tobytes())for k,t in streams.items()},actualSourceFiniteAndWholeNativeChecksStillRequired=True,sourceGeometryChanges=0,terrainGeometryProposalChanged=True,currentAcceptance=False,installationApproved=False)
 out['firstProposalFailure']=ref(BASE/'government-xl-vancor-basic-parent-core-apron-terrain-proposal-v1-20261011/diagnostic.json.gz');out['fixedEnvelopeNewZeroAlphaCollarWidthM']=.002
 save(DOC/'diagnostic.json.gz',out);assert ref(manifest)==start
 refs=[BASE/'government-xl-vancor-basic-parent-core-apron-terrain-proposal-v1-20261011/result.json',BASE/'government-xl-vancor-basic-parent-core-apron-terrain-proposal-v1-20261011/diagnostic.json.gz',Path(__file__),target,auditpath,candidatepath,parentpath,sourcepath,*required,*[p/'result.json'for p in [PHYSICAL,INPUT,BASIC,ACTUAL,CLIP]],HERE/'vancor_current_basic_parent_apron_candidate_v2_20261011.py',HERE/'test_vancor_current_basic_parent_apron_candidate_v2_20261011.py',HERE/'exact_original_slab_projection_coverage_20261010.py',HERE/'exact_original_polygon_triangle_partition_20261010.py',HERE/'exact_native_upper_surface_pair_seam_v3_20261010.py',HERE/'native_patch_resolution.py',*[ROOT/p for p in actual['inputHashes']],*[ROOT/p for p in bc['inputHashes']]]
 spec=importlib.util.spec_from_file_location('vancor_changed_parent_candidate_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'explicit-changed-basic-parent-core-apron-full-finite-domain-seam-proposal-v2',refs,dict(uids=[selection['uid'],actor['uid']],completeActualBasicCovered=complete_basic_covered,completeGuardFootprintCovered=complete_guard_covered,completeOuterEnvelopeUpperSeamWithinUnchanged2mm=outer_seam,sourceBuildingGeometryChanges=0,terrainProposalCreated=True,terrainProposalRepresentationChanged=True,currentAcceptance=False,newlyInstalled=0))
 print(json.dumps(dict(facets=proof['finalTerrainFacets'],coreParentPlaneDeviationM=proof['maxCorePackedParentHeightDeviationM'],basicCovered=complete_basic_covered,guardCovered=complete_guard_covered,outerSeamPassed=outer_seam,currentAcceptance=False)))
if __name__=='__main__':main()
