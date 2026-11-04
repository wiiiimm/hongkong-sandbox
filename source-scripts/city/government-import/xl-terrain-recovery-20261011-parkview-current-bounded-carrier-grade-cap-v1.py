"""Complete pinned current ground interfaces for one unchanged native carrier.

Only wall60989, clear cap57951 and its exact original attachment to owned
face0 are measured. Whole native failures and all original vertices remain;
this diagnostic does not approve the native, ground-root other components,
change source geometry, or grant installation acceptance.
"""
from fractions import Fraction as F
from pathlib import Path
import importlib.util,json,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_upper_ground_interfaces_20261009 import exact_upper_ground_interfaces
from original_bound_facet_wall_context_v3_20261010 import best_original_vertex_exposure
from exact_original_face_conservative_clearance_v5_20261010 import verify as finite
from exact_original_rational_interface_segment_clearance_20261011 import verify as segment
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from exact_original_component_contacts_20261009 import contact_measure
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-parkview-current-bounded-carrier-grade-cap-v1';DOC=BASE/BATCH
PROBE=BASE/'government-xl-terrain-recovery-parkview-block11-complete-original-proposed-current-probe-v4-20261011'
PHYSICAL=BASE/'government-xl-terrain-recovery-parkview-block11-authentic-retained-current-physical-v2-20261011'
PROPOSAL=BASE/'xl-terrain-recovery-20261011-parkview-authentic-current-retained-terrain-proposal-v3'
OWNED=BASE/'xl-terrain-recovery-20261011-parkview-owned-current-four-stream-finite-v1'
ACTUAL=BASE/'xl-terrain-recovery-20261011-parkview-owned-actual-render-capture-v1'
EDGE=BASE/'xl-terrain-recovery-20261011-parkview-authentic-carrier-edge-census-v1'
LEGACY=BASE/'xl-terrain-recovery-20261010-parkview-authentic-two-TIN-complete-conservative-v3'
UID='landsd/254491:0';OWN='landsd/255647:0';WALL=60989;CAP=57951
MANIFEST=ROOT/'3d-viewer/city/data/manifest.json'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def fenced(folder):
 r=read(folder/'result.json')
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 return r

def recheck():
 refs=[ref(Path(__file__))];start=ref(MANIFEST)
 for name in ['exact_packed_world_geometry_20261009.py','exact_original_shared_edge_component_census_v2_20261011.py','exact_original_upper_ground_interfaces_20261009.py','original_bound_facet_wall_context_v3_20261010.py','original_bound_facet_wall_context_v2_20261010.py','exact_original_face_conservative_clearance_v5_20261010.py','exact_original_rational_interface_segment_clearance_20261011.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py']:refs.append(ref(HERE/name))
 for folder in [PROBE,PHYSICAL,PROPOSAL,OWNED,ACTUAL,EDGE,LEGACY]:fenced(folder);refs.append(ref(folder/'result.json'))
 selection=read(PROBE/'selection.json.gz')['rows'];assert {r['uid']for r in selection}=={UID,OWN}
 runtimepath=HERE/'local'/PROBE.name/'runtime-geometry.json.gz';runtime=read(runtimepath)['rows'];nr=next(r for r in runtime if r['uid']==UID);wr=next(r for r in runtime if r['uid']==OWN)
 ground=np.asarray(nr['drawnGroundGeometry'],float).reshape(-1,3,3);assert len(ground)==25167 and digest(ground.tobytes())=='bba71625b8cff1e25e3d220ccaeab0d902bfdcce3c73eac6d76f1053b4255140'
 row=next(r for r in selection if r['uid']==UID);ownrow=next(r for r in selection if r['uid']==OWN);assets=[ROOT/r['candidate']['path']for r in [row,ownrow]]
 for r,a in zip([row,ownrow],assets):assert digest(a.read_bytes())==r['sourceSHA256']
 original=decode_original_world_triangles(assets[0].read_bytes());originalown=decode_original_world_triangles(assets[1].read_bytes());literal=np.asarray(nr['position'],float).reshape(-1,3)[np.asarray(nr['index'],int).reshape(-1,3)]
 assert original.shape==literal.shape==(63133,3,3)and originalown.shape==(10679,3,3)
 nativebounds=PROPOSAL/'current-native-bounds.json';native=next(r for r in read(nativebounds)['rows']if r['uid']==UID);assert native['sourceSHA256']==row['sourceSHA256'];streams=[]
 for key in ['leftAssociatedPerMultiplyAddFloat32WorldPosition','balancedPerMultiplyAddFloat32WorldPosition']:
  streams.append(np.concatenate([np.asarray(m[key],float).reshape(-1,3)[np.asarray(m['completeOriginalIndex'],int).reshape(-1,3)]for m in native['actualRenderMeshes']]))
 actualpath=ACTUAL/'actual-render-geometry.json.gz';actual=read(actualpath)['row'];assert actual['uid']==wr['uid']==ownrow['uid']==OWN and actual['sourceSHA256']==ownrow['sourceSHA256'];ix=np.asarray(actual['completeOriginalIndex'],int).reshape(-1,3)
 ownedworlds=[originalown,np.asarray(wr['position'],float).reshape(-1,3)[np.asarray(wr['index'],int).reshape(-1,3)],np.asarray(actual['completeExplicitLeftAssociatedFloat32WorldPosition'],float).reshape(-1,3)[ix],np.asarray(actual['completeExplicitBalancedFloat32WorldPosition'],float).reshape(-1,3)[ix]]
 proofpath=OWNED/'diagnostic.json.gz';ownedproof=read(proofpath);assert ownedproof['uid']==OWN and ownedproof['allOwnedFullFiniteBoundsProved']is True
 edgepath=EDGE/'diagnostic.json.gz';edges=read(edgepath);body=edges['rows'][0]['capNonzeroEdgeBodyFaces'];assert len(body)==20370 and WALL in body and CAP in body
 refs.extend(ref(p)for p in [*assets,runtimepath,nativebounds,actualpath,proofpath,edgepath,PROBE/'selection.json.gz',PHYSICAL/'selection.json.gz',PHYSICAL/'terrain-candidates.json',LEGACY/'diagnostic.json.gz',MANIFEST])
 rows=[];names=['providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix']
 for mode,world,own,ownedrow in zip(names,[original,literal,*streams],ownedworlds,ownedproof['rows']):
  assert world.shape==(63133,3,3)and np.isfinite(world).all();assert digest(own.tobytes())==ownedrow['completeWorldSHA256']and len(ownedrow['allFaces'])==10679
  assert [p['sourceFace']for p in ownedrow['allFaces']]==list(range(10679))
  for p in ownedrow['allFaces']:
   assert p['proof']['groundProjectionCovered']is True and p['proof']['existingOrdinaryClearanceBoundProved']is True and F(p['proof']['exactCertifiedLowerClearanceM'])>=F(-1,2)and p['proof']['sourceFaceSHA256']==digest(own[p['sourceFace']].tobytes())
  same=next((r for r in rows if r['completeNativeWorldSHA256']==digest(world.tobytes())and r['completeOwnedWorldSHA256']==digest(own.tobytes())),None)
  if same is not None:computed={k:v for k,v in same.items()if k not in ['mode','completeNativeWorldSHA256','completeOwnedWorldSHA256']};print(json.dumps(dict(mode=mode,exactWorldAndGroundReused=True)),flush=True)
  else:
   edgeproof=census(world,body);assert len(edgeproof['sharedEdgeConnectedComponents'])==1 and edgeproof['completeRenderableFaceIds']==body and not edgeproof['exactNonrenderingOriginalFaces']
   wallproof=finite(world[WALL],ground);capproof=finite(world[CAP],ground);assert capproof['groundProjectionCovered']is True and capproof['existingOrdinaryClearanceBoundProved']is True and F(capproof['exactCertifiedLowerClearanceM'])>0
   assert np.cross(world[CAP,1]-world[CAP,0],world[CAP,2]-world[CAP,0])[1]>0
   interfaces=exact_upper_ground_interfaces(world,[WALL],ground);assert interfaces and all(p['sourceFace']==WALL and p['exactActiveUpperGroundIntervals']for p in interfaces)
   exposure=best_original_vertex_exposure(world[WALL],ground);assert F(exposure['exactExposureLowerBoundM'])>0
   shared=sorted(set(map(tuple,world[WALL]))&set(map(tuple,world[CAP])));assert len(shared)==2
   sharedproof=segment([[str(F(float(v)))for v in p]for p in shared],ground);assert sharedproof['strictlyExposedWholePositiveInterface']is True
   points=intersection_points(rational_face(world[CAP]),rational_face(own[0]));measure=contact_measure(points);assert measure['dimension']>0
   # Both complete participating facets are strictly clear, so their exact
   # intersection subset cannot be hidden under either actual ground surface.
   ownproof=ownedrow['allFaces'][0]['proof'];assert F(ownproof['exactCertifiedLowerClearanceM'])>0
   computed=dict(exactWholeNativeBodyEdgeCensus=edgeproof,rawWallWholeFiniteProof=wallproof,strictClearCapWholeFiniteProof=capproof,completeFiniteGroundFaces=len(ground),completeGroundSHA256=digest(ground.tobytes()),exactPositiveUpperGroundInterfaces=interfaces,completeOriginalVertexExposure=exposure,wallToCapOriginalSharedEdge=sharedproof,capToOwnedFace0OriginalContact=dict(nativeFace=CAP,ownedFace=0,combinedGlobalOwnedFace=63133,exactIntersectionPoints=[[str(v)for v in p]for p in sorted(points)],measure=measure,wholeNativeCapStrictlyExposed=True,wholeOwnedFaceStrictlyExposed=True,ownedWholeFiniteProof=ownproof),wholeNativeReaccepted=False,diagnosticOnlyNoNewRootOrInstallationCredit=True)
  rows.append(dict(mode=mode,completeNativeWorldSHA256=digest(world.tobytes()),completeOwnedWorldSHA256=digest(own.tobytes()),**computed));print(json.dumps(dict(mode=mode,groundInterfaces=len(computed['exactPositiveUpperGroundInterfaces']),wallExposure=computed['completeOriginalVertexExposure']['exactExposureLowerBoundM'],capMinimum=computed['strictClearCapWholeFiniteProof']['exactCertifiedLowerClearanceM'],contactDimension=computed['capToOwnedFace0OriginalContact']['measure']['dimension'])),flush=True)
 assert ref(MANIFEST)==start
 for p in refs:assert ref(ROOT/p['path'])==p
 return dict(uids=[UID,OWN],rows=rows,currentManifest=start,evidenceRefs=refs,rawWholeNativeFailuresRef=ref(LEGACY/'diagnostic.json.gz'),allOtherNativePartsRemainUncreditedAndPresent=True,explicitArithmeticNotUniversalGPUCameraGuarantee=True,sourceGeometryChanges=0,nativeReacceptance=False,currentAcceptance=False,fullAcceptance=False,newlyInstalled=0)
def main():
 assert not DOC.exists();claim=reservations.claim('parkview-bounded-grade-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  result=json.loads(json.dumps(recheck()));assert reservations.heartbeat(lease)['ok'];save(DOC/'diagnostic.json.gz',result);s=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'current-parkview-bounded-original-literal-two-render-F32-exposed-grade-wall-clear-cap-interface-v1',[ROOT/p['path']for p in result['evidenceRefs']]+[DOC/'diagnostic.json.gz'],dict(uids=result['uids'],completeNativeFaces=63133,completeOwnedFaces=10679,wholeNativeReaccepted=False,currentAcceptance=False,sourceGeometryChanges=0,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
