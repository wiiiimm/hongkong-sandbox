"""Bounded current original/literal carrier interfaces; no whole-native acceptance."""
import importlib.util,json
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from exact_original_face_conservative_clearance_v5_20261010 import verify
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261010-cullinan-west-current-carrier-chain-finite-v2';DOC=BASE/BATCH
PROBE=BASE/'government-xl-terrain-recovery-cullinan-west-three-complete-original-current-probe-v2-20261010';GRAPH=BASE/'xl-terrain-recovery-20261010-cullinan-west-three-current-original-complete-support-v1';ROOTS=[BASE/f'government-xl-terrain-recovery-cullinan-west-literal-ordinary-rendered-root-{i}-v1-20261010'for i in [11,51]]
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))]
 for folder in [PROBE,GRAPH,*ROOTS]:
  r=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(ref(folder/'result.json'))
 graph=read(GRAPH/'diagnostic.json.gz');selection=read(PROBE/'selection.json.gz');runtimepath=HERE/'local'/PROBE.name/'runtime-geometry.json.gz';rt=read(runtimepath);assets=[ROOT/r['candidate']['path']for r in selection['rows']]
 for p,r in zip(assets,selection['rows']):assert digest(p.read_bytes())==r['sourceSHA256']
 original=np.concatenate([decode_original_world_triangles(p.read_bytes())for p in assets]);literal=np.concatenate([np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)]for r in rt['rows']]);ground=np.asarray(rt['rows'][0]['drawnGroundGeometry']).reshape(-1,3,3)
 assert original.shape==literal.shape==(154603,3,3) and digest(original.tobytes())==graph['binding']['completeOriginalWorldTrianglesSHA256'];assert len(ground)==4755
 assert graph['groundRootedComponentParents']['264']==0 and graph['groundRootedComponentParents']['279']==0 and graph['groundRootedComponentParents']['0']==25 and graph['groundRootedComponentParents']['25']==51
 pairs=[w for w in graph['contactWitnesses']if set(w['components'])in [{0,25},{25,51},{0,264},{0,279}]];assert len(pairs)==4
 componentof={f:i for i,c in enumerate(graph['components'])for f in c['globalOriginalFaces']};assert len(componentof)==154603
 caps=[77581,78233];assert all(componentof[i]==0 for i in caps);faces=sorted({f for w in pairs for f in w['globalOriginalFaces']}|set(caps));rows=[]
 for name,world in [('providerOriginal',original),('actualLiteral',literal)]:
  faceproofs=[];contacts=[]
  for i in faces:
   proof=verify(world[i],ground);n=np.cross(world[i,1]-world[i,0],world[i,2]-world[i,0]);norm=float(np.linalg.norm(n));positive=proof['groundProjectionCovered'] and F(proof['exactCertifiedLowerClearanceM'])>0
   faceproofs.append(dict(globalOriginalFace=i,component=componentof[i],normalYRatio=float(n[1]/norm)if norm else None,strictlyAboveCompleteFiniteGround=positive,completeFiniteProof=proof));print(json.dumps(dict(mode=name,face=i,strictClear=positive)),flush=True)
  for w in pairs:
   a,b=w['globalOriginalFaces'];assert {componentof[a],componentof[b]}==set(w['components']);ps=intersection_points(rational_face(world[a]),rational_face(world[b]));positive=len(ps)>=2
   contacts.append(dict(components=w['components'],globalOriginalFaces=[a,b],exactIntersectionPoints=[[str(v)for v in p]for p in ps],positiveDimensionOriginalContact=positive));print(json.dumps(dict(mode=name,components=w['components'],positiveDimension=positive)),flush=True)
  capproof=[p for p in faceproofs if p['globalOriginalFace']in caps];rows.append(dict(mode=name,completeWorldSHA256=digest(world.tobytes()),completeCurrentGroundSHA256=digest(ground.tobytes()),interfaces=contacts,faceProofs=faceproofs,allSelectedPositiveContacts=all(c['positiveDimensionOriginalContact']for c in contacts),allTwoCarrierCapsStrictlyExposed=all(p['strictlyAboveCompleteFiniteGround'] and p['normalYRatio']>.15 for p in capproof)))
 refs.extend(ref(p)for p in [*assets,runtimepath,PROBE/'selection.json.gz',GRAPH/'diagnostic.json.gz',*[r/'diagnostic.json.gz'for r in ROOTS],HERE/'exact_original_face_conservative_clearance_v5_20261010.py',HERE/'exact_original_projection_coverage_v2_20261010.py',HERE/'exact_original_projection_coverage_20261009.py',HERE/'exact_original_closed_projection_intersection_20261010.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_packed_world_geometry_20261009.py'])
 for r in refs:assert ref(ROOT/r['path'])==r
 result=dict(uids=[r['uid']for r in selection['rows']],rows=rows,claimedNativeCarrierComponents=[0,25,51],claimedNativeRoot=51,ordinaryActualRootReceipt=ref(ROOTS[1]/'result.json'),completeNativeComponents=264,legacyUnresolvedNativeComponents=[i for i,c in enumerate(graph['components'])if c['actorUID']=='landsd/262871:0'and i not in graph['resolvedOriginalComponents']],allLegacyNativeNegativesPreserved=True,nativeReacceptance=False,noNewRootsOrBridges=True,diagnosticOnly=True,fullAcceptance=False,sourceGeometryChanges=0,newlyInstalled=0,evidenceRefs=refs)
 save(DOC/'diagnostic.json.gz',result);s=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'bounded-current-original-literal-native-carrier-chain-finite-interfaces-v2',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=result['uids'],allSelectedContactsPositive=all(r['allSelectedPositiveContacts']for r in rows),bothSourceLiteralCapsStrictlyExposed=all(r['allTwoCarrierCapsStrictlyExposed']for r in rows),nativeReacceptance=False,fullAcceptance=False))
if __name__=='__main__':main()
