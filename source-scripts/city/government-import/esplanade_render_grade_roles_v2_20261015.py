"""Replay unchanged wall-cap/grade rules with complete certified finite bounds."""
from pathlib import Path
from fractions import Fraction as F
import importlib.util
import numpy as np
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_bound_facet_wall_context_20261010 import canonical,down
from original_strict_clear_cap_wall_paths_20261009 import verify as cap_paths
from exact_original_upper_ground_interfaces_20261009 import exact_upper_ground_interfaces
from exact_original_paired_finite_clearance_v3_20261011 import verify as finite_verify
BATCH='government-xl-esplanade-render-grade-roles-v2-20261015';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;FINITE=BASE/'government-xl-esplanade-render-finite-v2-20261015';PHYSICAL=BASE/'government-xl-esplanade-pair-current-physical-v3-20261015';LOCAL=HERE/'local'/PHYSICAL.name

def main():
 assert not DOC.exists();receipt=read(FINITE/'result.json')
 for r in receipt['evidenceRefs']:assert digest((ROOT/r['path']).read_bytes())==r['sha256']
 row=next(r for r in read(PHYSICAL/'selection.json.gz')['rows']if r['uid']=='landsd/309385:0');raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];original=decode_original_world_triangles(raw);runtime=next(r for r in read(LOCAL/'runtime-geometry.json.gz')['rows']if r['uid']==row['uid']);literal=np.asarray(runtime['position'],float).reshape(-1,3)[np.asarray(runtime['index']).reshape(-1,3)];ground=np.asarray(runtime['drawnGroundGeometry'],float).reshape(-1,3,3);results=[]
 captured=read(FINITE/'attributes.json.gz');captured_record=next(q for q in captured['rows']if q['uid']==row['uid']);ix=np.asarray(captured_record['completeOriginalIndex']).reshape(-1,3)
 for mode,key in [('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]:
  tri=np.asarray(captured_record[key],float).reshape(-1,3)[ix]
  saved=read(FINITE/(mode+'.json.gz'));assert saved['worldSHA256']==digest(tri.tobytes())and saved['groundSHA256']==digest(ground.tobytes());assert len(saved['faces'])==len(tri);contexts=[]
  for i,(face,record) in enumerate(zip(tri,saved['faces'])):
   proof=record['proof'];assert record['sourceFace']==i and proof['sourceFaceSHA256']==digest(face.tobytes())and proof['completeCurrentGroundSHA256']==digest(ground.tobytes());assert proof['groundProjectionCovered']is True
   bound=F(proof['exactCertifiedLowerClearanceM']);assert proof['existingOrdinaryClearanceBoundProved']==(bound>=F(-1,2));lo=face[:,[0,2]].min(axis=0);hi=face[:,[0,2]].max(axis=0);xz=ground[:,:,[0,2]];ids=np.flatnonzero(np.all(xz.max(axis=1)>=lo,axis=1)&np.all(xz.min(axis=1)<=hi,axis=1));assert len(ids)
   assert list(map(int,ids))==proof['sameConstraintOptimizedOrdinaryPrismProof']['allProjectedBoundingCandidateOriginalGroundFacets'];vertex=int(np.argmax(face[:,1]));exposure=F(float(face[vertex,1]))-max(F(float(v))for v in ground[ids,:,1].flat)
   contexts.append(dict(sourceFace=i,groundProjectionCovered=True,minimum=dict(minimumGapM=down(bound),qualification='Certified lower bound, not asserted exact minimum'),maximumObservedGapM=down(exposure),exposureQualification='Conservative lower gap bound at an actual highest source vertex over all bounding candidate terrain facets',exactCertifiedLowerClearanceM=str(bound),actualHighestOriginalVertex=face[vertex].tolist(),allExposureBoundingGroundFacets=ids.tolist(),exactExposureLowerBoundM=str(exposure),finiteFacetProofSHA256=canonical(proof)))
  exposure_proofs=[]
  for i,ctx in enumerate(contexts):
   if F(ctx['exactCertifiedLowerClearanceM'])>=F(-1,2):continue
   vertex=int(np.argmax(tri[i,:,1]));proof=finite_verify(np.repeat(tri[i,vertex][None,:],3,axis=0),ground);assert proof['groundProjectionCovered'];bound=F(proof['exactCertifiedLowerClearanceM']);ctx.update(maximumObservedGapM=down(bound),exposureQualification='Certified exact finite-column lower bound at an unchanged highest vertex; exposure only, not a root',exactVertexExposureLowerBoundM=str(bound));exposure_proofs.append(dict(sourceFace=i,vertex=vertex,proof=proof))
  binding=dict(completeOriginalWorldTrianglesSHA256=digest(tri.tobytes()),completeCurrentFacetContextsSHA256=canonical(contexts),exactOriginalContactListSHA256=canonical([]));paths=cap_paths(tri,contexts,[],expected_binding=binding,current_binding=binding);grade=exact_upper_ground_interfaces(tri,paths['affectedOriginalWallFaces'],ground)
  save(DOC/(mode+'.json.gz'),dict(mode=mode,binding=binding,contexts=contexts,vertexExposureProofs=exposure_proofs,capPaths=paths,gradeInterfaces=grade,groundSHA256=digest(ground.tobytes()),installationApproved=False));results.append(dict(mode=mode,faces=len(tri),affected=paths['affectedOriginalWallFaces'],allHaveCapPaths=paths['allAffectedHavePaths'],exposureFailures=paths['rawExposureFailures'],gradeContactFaces=sorted({r['sourceFace']for r in grade}),gradeIntervals=len(grade)))
 paths=[Path(__file__),FINITE/'result.json',FINITE/'left.json.gz',FINITE/'balanced.json.gz',FINITE/'attributes.json.gz',PHYSICAL/'selection.json.gz',LOCAL/'runtime-geometry.json.gz',ROOT/row['candidate']['path']]+[HERE/n for n in ['exact_original_paired_finite_clearance_v3_20261011.py','exact_original_paired_finite_clearance_v2_20261010.py','original_bound_facet_wall_context_20261010.py','original_strict_clear_cap_wall_paths_20261009.py','exact_original_upper_ground_interfaces_20261009.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py']]
 spec=importlib.util.spec_from_file_location('esplanade_grade_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f);f.freeze(BATCH,'certified-explicit-f32-exposed-grade-cap-paths-v1',paths,dict(uids=[row['uid']],rows=results,fullAcceptance=False,qualification='Two explicit Float32 arithmetic orders, certified finite bounds, exact vertex exposure and cap/grade evidence. No whole-model acceptance or universal GPU guarantee.'));print(results,flush=True)
if __name__=='__main__':main()
