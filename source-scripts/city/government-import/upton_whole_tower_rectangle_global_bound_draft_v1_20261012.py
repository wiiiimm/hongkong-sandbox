"""UNEXECUTED bounded sufficient whole-tower projection/Y proof, no root credit.
The two rectangle triangles are numerical probes, never source/model/terrain.
No near-equal-world reuse: each exact world and full unused bounds is bound.
"""
import argparse,json
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_original_face_conservative_clearance_v5_20261010 import verify as finite
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from exact_original_shared_edge_component_census_v2_20261011 import census
from upton_three_original_complete_current_runtime_capture_draft_v2_20261012 import UIDS,MANIFEST_SHA,state,native,ref,verified_plan,module
B=ROOT/'docs/astra-city/government-import';BATCH='government-xl-upton-whole-tower-rectangle-global-bound-draft-v1-20261012';DOC=B/BATCH;CAP=B/'government-xl-upton-three-original-complete-current-runtime-capture-v2-20261012';RUNTIME=HERE/'local'/CAP.name/'runtime-geometry.json.gz';UID='landsd/338946:0'

def whole_world_proof(triangles,ground,full_unused_position_bounds):
 t=np.asarray(triangles,dtype='<f8');g=np.asarray(ground,dtype='<f8');bounds=np.asarray(full_unused_position_bounds,dtype='<f8')
 assert t.ndim==3 and t.shape[1:]==(3,3)and len(t)>0 and g.ndim==3 and g.shape[1:]==(3,3)and len(g)>0 and bounds.shape==(2,3)
 assert np.isfinite(t).all()and np.isfinite(g).all()and np.isfinite(bounds).all()and np.all(bounds[0]<=bounds[1])
 assert np.all(t>=bounds[0])and np.all(t<=bounds[1]),'Indexed face outside genuine full unused POSITION bounds'
 lo,hi=bounds;source_y=F(float(lo[1]));ground_y=max(F(float(v))for v in g[:,:,1].reshape(-1));gap=source_y-ground_y
 rect=[];probes=[]
 if lo[0]<hi[0]and lo[2]<hi[2]:
  rect=np.asarray([[lo[0],lo[1],lo[2]],[hi[0],lo[1],lo[2]],[hi[0],lo[1],hi[2]],[lo[0],lo[1],hi[2]]],dtype='<f8')
  probes=[finite(rect[[0,1,2]],g),finite(rect[[0,2,3]],g)]
 covered=len(probes)==2 and all(p['groundProjectionCovered']for p in probes);qualified=bool(covered and gap>0)
 return dict(worldSHA256=digest(t.tobytes()),groundSHA256=digest(g.tobytes()),completeSourceFacets=len(t),completeGroundFacets=len(g),wholeUnusedPositionBounds=bounds.tolist(),indexedFaceBounds=[t.min((0,1)).tolist(),t.max((0,1)).tolist()],everyIndexedVertexWithinWholePositionBounds=True,exactMinimumWholeUnusedPositionY=str(source_y),exactMaximumAllCapturedGroundVertexY=str(ground_y),exactConservativeGlobalLowerM=str(gap),rectangleProbesAreNumericalCoverageOnly=True,completeRectangleProjectionProofs=probes,wholeRectangleProjectionCovered=covered,allWholeSourceFacetsOrdinaryFiniteProved=qualified,allWholeSourceFacetsStrictPositiveFiniteProved=qualified,ordinaryThresholdM='-1/2',strongerSufficientBoundStrictlyPositive=True,exactMinimumGapWitnessClaimed=False,gradeRootProved=False,wholeEdgeOrCapRoleQualified=False,physicalAccepted=False,installationApproved=False,qualification='Every original/literal/F32 indexed facet is a convex combination of its complete actual vertices; all are inside the genuine full POSITION XZ rectangle and at or above its exact minY. Both complete rectangle projections must be covered by complete actual ground. Every finite ground point is at or below the maximum of all ground vertex Ys. Positive exact global subtraction then bounds ALL same-XZ source/ground facet gaps. Failure is only failure of this stronger sufficient method, not a negative source/model result. No source/terrain probe is rendered or saved as geometry.')

def main():
 p=argparse.ArgumentParser();p.add_argument('--lease-file',required=True);a=p.parse_args();lease=read(Path(a.lease_file));assert set('building:'+u for u in UIDS)<=set(lease['resources'])and reservations.owns(lease)and not DOC.exists()
 capture=read(CAP/'result.json');assert capture['jobId']=='9ce5921b5373fd94334b8d5236fae4149836e7086cf31357ace1b44c77a28154'and capture['sourceOnly']and not capture['physicalAccepted']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(capture['jobId'],)).fetchone()==('complete',capture)
 for e in capture['evidenceRefs']:assert ref(ROOT/e['path'])==e
 scope=read(CAP/'capture-scope.json');assert scope['currentManifest']['sha256']==MANIFEST_SHA and scope['expectedNativeCount']==6649 and scope['preservedOriginalProperCrossings']==23
 selection=read(CAP/'selection.json.gz')['rows'];before=read(CAP/'protected-state-before.json');native_before=read(CAP/'native-source-state-before.json')['rows'];e=next(r for r in verified_plan()['actors']if r['uid']==UID);r=next(r for r in selection if r['uid']==UID);asset=ROOT/r['candidate']['path'];assert ref(asset)['sha256']==e['sourceSHA256']
 walker=module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','upton_rectangle_dependency_closure');paths=set();walker.local_imports(Path(__file__),paths);code_refs=[ref(p)for p in sorted(paths)]
 def fence():
  assert ref(ROOT/'3d-viewer/city/data/manifest.json')==scope['currentManifest']and reservations.owns(lease)
  for path,h in scope['inputHashes'].items():assert ref(ROOT/path)['sha256']==h
  for x in capture['evidenceRefs']+code_refs:assert ref(ROOT/x['path'])==x
  assert json.loads(json.dumps(state(before['uids']),default=str))==before['rows']and json.loads(json.dumps(native(selection),default=str))==native_before
 fence();raw=asset.read_bytes();original=decode_original_world_triangles(raw);packed=packed_world_bounds(raw);assert original.shape==(11657,3,3)and digest(original.tobytes())==packed['worldTrianglesSHA256']==e['wholeWorldSHA256']and packed['allOriginalPositionVerticesAccounted'];topology=census(original,list(range(len(original))));assert len(topology['sharedEdgeConnectedComponents'])==737 and len(topology['exactNonrenderingOriginalFaces'])==16
 attrs=next(r for r in read(CAP/'actual-render-geometry.json.gz')['rows']if r['uid']==UID);runtime=next(r for r in read(RUNTIME)['rows']if r['uid']==UID);ground=np.asarray(runtime['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);g=next(r for r in scope['completeGroundByActor']if r['uid']==UID);assert len(ground)==176 and digest(ground.tobytes())==g['completeActualGroundSHA256'];index=np.asarray(attrs['completeOriginalIndex'],dtype=int).reshape(-1,3);assert index.shape==(11657,3)and runtime['index']==attrs['completeOriginalIndex']
 worlds={'original':(original,packed['originalWholeSourceBounds'])}
 for name,key in [('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:
  v=np.asarray(attrs[key],dtype='<f8').reshape(-1,3);assert len(v)==packed['completeOriginalPositionVertices']and np.isfinite(v).all()and index.min()>=0 and index.max()<len(v);worlds[name]=(v[index],[v.min(0).tolist(),v.max(0).tolist()])
 proofs={name:whole_world_proof(t,ground,bounds)for name,(t,bounds)in worlds.items()};assert set(proofs)=={'original','literal','explicitLeftF32','explicitBalancedF32'}and all(x['completeSourceFacets']==11657 for x in proofs.values());fence()
 save(DOC/'diagnostic.json',dict(uid=UID,currentManifest=scope['currentManifest'],currentNativeCount=6649,sourceOnly=True,sourceSHA256=e['sourceSHA256'],completeFaces=11657,originalFullUnusedPOSITIONProof=packed,originalBodyCensus=topology,allFourIndependentWorldProofs=proofs,allFourWorldsQualifiedByStrongerSufficientMethod=all(p['allWholeSourceFacetsStrictPositiveFiniteProved']for p in proofs.values()),nearEqualOrUnboundWorldReuse=False,existingPerFaceOriginalAndPartialCheckpointsMustRemainImmutable=True,preservedWholeSourceBodyObligations=737,preservedZeroSourceFacets=16,all23ProperOriginalCrossingsPreserved=True,sourceGeometryChanges=0,terrainGeometryChanges=0,physicalAccepted=False,installationApproved=False,foreignHoldsDischarged=False,gradeRootProved=False,evidenceRefs=code_refs+[ref(p)for p in [CAP/'result.json',CAP/'capture-scope.json',CAP/'selection.json.gz',CAP/'actual-render-geometry.json.gz',CAP/'protected-state-before.json',CAP/'native-source-state-before.json',asset,RUNTIME]]))
 print(json.dumps(dict(batch=BATCH,allWorldsQualified=all(p['allWholeSourceFacetsStrictPositiveFiniteProved']for p in proofs.values()),physicalAccepted=False)),flush=True)
if __name__=='__main__':main()
