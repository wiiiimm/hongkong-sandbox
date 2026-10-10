"""Complete unchanged Block 6 vs one independently checked carrier cap; no acceptance."""
from pathlib import Path
import sys,json
import numpy as np
from fractions import Fraction as F
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from exact_original_face_conservative_clearance_v5_20261010 import verify
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-parkview-block6-bounded-original-clear-cap-probe-v1-20261011'
DOC=BASE/BATCH
RANK=BASE/'xl-terrain-recovery-20261010-next-current-native-cap-source-only-ranking-v1'
CARRIER=BASE/'xl-terrain-recovery-20261011-parkview-current-bounded-carrier-grade-cap-v1'
EDGE=BASE/'xl-terrain-recovery-20261011-parkview-authentic-carrier-edge-census-v1'
PROBE=BASE/'government-xl-terrain-recovery-parkview-block11-complete-original-proposed-current-probe-v4-20261011'
CAP=58400;UID='landsd/255438:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists()
 rank=read(RANK/'diagnostic.json.gz');r=next(x for x in rank['rows']if x['uid']==UID)
 ownpath=ROOT/r['cachedSource']['path'];assert ref(ownpath)==r['cachedSource']
 own=decode_original_world_triangles(ownpath.read_bytes());assert len(own)==r['completeOriginalFaces']
 s=next(x for x in read(PROBE/'selection.json.gz')['rows']if x['uid']=='landsd/254491:0')
 natpath=ROOT/s['candidate']['path'];assert digest(natpath.read_bytes())==s['sourceSHA256']
 native=decode_original_world_triangles(natpath.read_bytes());e=read(EDGE/'diagnostic.json.gz')['rows'][0]
 assert digest(native.tobytes())==e['completeSourceWorldSHA256'] and CAP in e['capNonzeroEdgeBodyFaces']
 runtime=HERE/'local'/PROBE.name/'runtime-geometry.json.gz';rt=next(x for x in read(runtime)['rows']if x['uid']=='landsd/254491:0')
 ground=np.asarray(rt['drawnGroundGeometry'],float).reshape(-1,3,3)
 carrier=read(CARRIER/'diagnostic.json.gz');ctx=next(x for x in carrier['rows']if x['mode']=='providerOriginal')
 assert digest(ground.tobytes())==ctx['completeGroundSHA256'] and digest(native.tobytes())==ctx['completeNativeWorldSHA256']
 edge=census(own,list(range(len(own))))
 contact=exact_finite_contacts(native,[CAP],own,list(range(len(own))))
 capproof=verify(native[CAP],ground)
 compmap={f:i for i,fs in enumerate(edge['sharedEdgeConnectedComponents'])for f in fs}
 reached=sorted({compmap[p['sourceFaceB']]for p in contact['contacts']if p['dimension']>0 and p['sourceFaceB']in compmap})
 participating=sorted({p['sourceFaceB']for p in contact['contacts']if p['dimension']>0})
 ownproofs=[]
 for f in participating:
  ownproofs.append(dict(face=f,proof=verify(own[f],ground)))
  print(json.dumps(dict(participatingFace=f)),flush=True)
 old=BASE/'government-xl-extended-255438-20261005/guard-failure.json'
 refs=[ref(p)for p in [Path(__file__),RANK/'diagnostic.json.gz',ownpath,ROOT/r['cachedSelection']['path'],natpath,PROBE/'selection.json.gz',runtime,CARRIER/'diagnostic.json.gz',CARRIER/'result.json',EDGE/'diagnostic.json.gz',old,ROOT/'3d-viewer/city/data/manifest.json',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_shared_edge_component_census_v2_20261011.py',HERE/'exact_original_finite_triangle_contacts_20261010.py',HERE/'exact_original_face_conservative_clearance_v5_20261010.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py']]
 result=dict(uids=[UID,'landsd/254491:0'],completeOriginalOwnedFaces=len(own),completeOriginalOwnedWorldSHA256=digest(own.tobytes()),completeOriginalNativeFaces=len(native),completeOriginalNativeWorldSHA256=digest(native.tobytes()),qualifiedContextJob=read(CARRIER/'result.json')['jobId'],capOriginalFace=CAP,capInExactContextNativeEdgeBody=True,capWholeFiniteCurrentGroundProof=capproof,completeOwnedToOneCapContacts=contact,completeOwnedNonzeroEdgeCensus=edge,reachedOwnedEdgeBodyIDs=reached,positiveContactOwnedFacetsCurrentGroundProofs=ownproofs,completeCurrentGroundFaces=len(ground),completeCurrentGroundSHA256=digest(ground.tobytes()),historicalReasons=r['historicalReasons'],separateHistoricalGuardFailure=read(old),evidenceRefs=refs,sourceOnly=True,installationApproved=False,currentAcceptance=False,wholeOwnedCurrentFiniteProved=False,ownedLiteralOrF32Examined=False,newlyInstalled=0,sourceGeometryChanges=0,nativeReacceptance=False)
 save(DOC/'diagnostic.json.gz',result)
 print(json.dumps(dict(faces=len(own),edgeBodies=len(edge['sharedEdgeConnectedComponents']),contacts=len(contact['contacts']),reached=reached,capClear=capproof.get('exactCertifiedLowerClearanceM'),capCovered=capproof['groundProjectionCovered'],allParticipatingClear=all(p['proof']['existingOrdinaryClearanceBoundProved'] for p in ownproofs))),flush=True)
if __name__=='__main__':main()
