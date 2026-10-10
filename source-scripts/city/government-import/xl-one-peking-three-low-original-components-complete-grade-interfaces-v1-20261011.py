"""Exact full original low-feature/ground intersections, no root or role credit."""
from pathlib import Path
import importlib.util,json,numpy as np
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from exact_original_shared_edge_component_census_v2_20261011 import census
BATCH='government-xl-one-peking-three-low-original-components-complete-grade-interfaces-v1-20261011';DOC=ROOT/'docs/astra-city/government-import'/BATCH
GRAPH=DOC.parent/'government-xl-one-peking-original-ordinary-ground-graph-diagnostic-v2-20261010'
PHYS=DOC.parent/'government-xl-one-peking-two-original-retained-hullett-child-current-physical-v5-20261010'
def main():
 assert not DOC.exists();graph=read(GRAPH/'diagnostic.json.gz');rows=sorted(read(PHYS/'selection.json.gz')['rows'],key=lambda r:r['uid']);assets=[ROOT/r['candidate']['path'] for r in rows]
 for p,r in zip(assets,rows):assert digest(p.read_bytes())==r['sourceSHA256']
 whole=np.concatenate([decode_original_world_triangles(p.read_bytes()) for p in assets]);assert digest(whole.tobytes())==graph['binding']['completeOriginalWorldTrianglesSHA256']
 ground=np.asarray(read(GRAPH/'complete-historical-ground-facets.json.gz')['triangles'],dtype='<f8');assert digest(ground.tobytes())==graph['binding']['currentDrawnGroundSHA256']
 out=[]
 for k in (12,13,15):
  ids=graph['components'][k]['globalOriginalFaces'];assert graph['components'][k]['actorUID']=='landsd/233985:0'
  topology=census(whole,ids);contact=exact_finite_contacts(whole,ids,ground,range(len(ground)));assert contact['allPairsExamined']
  lines=[r for r in contact['contacts'] if r['dimension']>0 and r['sourcePrimitiveDimensionA']==r['sourcePrimitiveDimensionB']==2]
  out.append(dict(component=k,uid='landsd/233985:0',completeOriginalFaceIDs=ids,completeOriginalFaces=whole[ids].tolist(),completeTopology=topology,completeFiniteGradeContactProof=contact,positiveDimensionalOriginalGradeInterfaces=lines,sourceGroundRootAccepted=False,sourceRoleAccepted=False))
  print(json.dumps(dict(component=k,completeGroundFacets=len(ground),positiveGradeInterfaces=len(lines))),flush=True)
 result=dict(rows=out,uids=sorted(r['uid'] for r in rows),completeOriginalPairFaces=len(whole),completeHistoricalDrawnGroundFacets=len(ground),wholeOriginalSHA256=digest(whole.tobytes()),completeGroundSHA256=digest(ground.tobytes()),historicalCandidateOnly=True,currentRegionalRebindRequired=True,sourceGeometryChanges=0,physicalAccepted=False,installationApproved=False,qualification='Every original low-feature face and historical drawn ground facet participate in exact finite intersection. Positive-dimensional grade contacts are diagnostic, not grounded role, footing, structural support, foreign clearance or current acceptance. Existing failed ordinary rim and strict JS proofs remain unchanged.')
 save(DOC/'diagnostic.json.gz',result)
 refs=[Path(__file__),GRAPH/'result.json',GRAPH/'diagnostic.json.gz',GRAPH/'complete-historical-ground-facets.json.gz',PHYS/'result.json',PHYS/'selection.json.gz',HERE/'exact_original_finite_triangle_contacts_20261010.py',HERE/'exact_original_shared_edge_component_census_v2_20261011.py',HERE/'exact_packed_world_geometry_20261009.py',*assets]
 s=importlib.util.spec_from_file_location('one_low_grade_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 receipt=m.freeze(BATCH,'complete-three-original-low-features-finite-drawn-grade-interfaces-v1',refs,dict(uids=result['uids'],completeOriginalFaces=len(whole),completeGroundFacets=len(ground),positiveGradeInterfaceCounts={str(r['component']):len(r['positiveDimensionalOriginalGradeInterfaces']) for r in out},sourceGeometryChanges=0,physicalAccepted=False,installationApproved=False,currentHeldReason='full-original-and-rendered-source-role-ground-support-current-foreign-runtime-required'))
 print(json.dumps(dict(jobId=receipt['jobId'],physicalAccepted=False)),flush=True)
if __name__=='__main__':main()
