"""Named104 current-role proposal; no source modelling or whole-building acceptance.

39/44 retain exact finite exposed interfaces to a strictly clear authored cap.
43 is an independent open lateral post skin with genuine closed grade ring and
complete exposed upper perimeter. No invented top, volume or canopy load path.
"""
import importlib.util,json,sys,uuid,subprocess
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from king_cheung_complete_ancillary_proposal_20261011 import UID,SOURCE_SHA,ROLE_IDS,PART_FACES
from king_cheung_named_open_post_skin_20261011 import verify as open_post
BASE=ROOT/'docs/astra-city/government-import'
INPUT=BASE/'government-xl-king-cheung-95691-current-actual-ground-capture-v1-20261011'
GRADE=BASE/'government-xl-king-cheung-95691-canopy-current-grade-cause-v1-20261011'
IDENTITY=BASE/'government-xl-king-cheung-95691-current-ancillary-identity-v1-20261011'
BATCH='government-xl-king-cheung-95691-current-canopy-post-role-proposal-v1-20261011';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [INPUT,GRADE,IDENTITY]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
   refs.append(folder/'result.json')
   for pin in r['evidenceRefs']:
    p=ROOT/pin['path'];assert digest(p.read_bytes())==pin['sha256'];refs.append(p)
 data=read(INPUT/'complete-four-stream-ground-inputs.json.gz');capt=read(INPUT/'complete-current-actual-source-and-ground.json.gz');grade=read(GRADE/'diagnostic.json.gz')
 assert data['uid']==UID and data['sourceSHA256']==SOURCE_SHA
 ground=np.asarray(data['completeDrawnGround'],dtype='<f8');assert digest(ground.tobytes())==data['completeDrawnGroundSHA256']
 assert set(ground[:,:,1].reshape(-1))=={14.0} # Named actual current planar ground, no other-ground extrapolation.
 manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();assert digest(before)==capt['inputHashes']['3d-viewer/city/data/manifest.json']
 rows=[]
 for mode,stream in data['completeWorldStreams'].items():
  world=np.asarray(stream['completeWorldTriangles'],dtype='<f8');assert world.shape==(18742,3,3)and digest(world.tobytes())==stream['completeWorldTriangleSHA256']
  old=next(r for r in grade['rows']if r['arithmetic']==mode);assert old['localFaceToOriginalSourceFace']==ROLE_IDS and old['completeWorldSHA256']==stream['completeWorldTriangleSHA256']
  t=world[PART_FACES[43]];binding=dict(completePartSHA256=digest(t.tobytes()),completeGroundSHA256=digest(ground.tobytes()))
  post=open_post(t,ground,source_face_ids=PART_FACES[43],interpreted_role='King Cheung original ancillary isolated post43 lateral skin',expected_binding=binding,current_binding=binding)
  paths=[]
  for path in old['strictClearCapPathProof']['paths']:
   original=ROLE_IDS[path['sourceFace']]
   if original in PART_FACES[43]:
    assert not path['hasExactOriginalStrictClearCapRoofPath'];continue
   assert path['hasExactOriginalStrictClearCapRoofPath']and path['rawFaceExposurePositive']
   assert path['strictClearNonWallFaces']
   chain=path['originalPath'];edges=[]
   for a,b in zip(chain,chain[1:]):
    candidates=[c for c in old['complete104PairInterfaces']['contacts']if {c['sourceFaceA'],c['sourceFaceB']}=={a,b}and c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2]
    assert candidates
    # Every participating complete face has exact finite ground projection coverage.
    assert all(old['complete104FaceInventory'][i]['completeFiniteClearanceAndExposure']['groundProjectionCovered']for i in [a,b])
    exposed=[]
    for contact in candidates:
     pts=[tuple(F(v)for v in p)for p in contact['exactPoints']]
     top=max(pts,key=lambda p:p[1]);other=next((p for p in pts if p!=top),None)
     if top[1]<=14 or other is None:continue
     if other[1]>14: end=other
     else:
      height=(top[1]+14)/2;alpha=(height-top[1])/(other[1]-top[1]);end=tuple(top[k]+alpha*(other[k]-top[k])for k in range(3))
     assert top!=end and min(top[1],end[1])>14
     exposed.append(dict(completeOriginalContactVerbatim=contact,exactPositiveDimensionalExposedSubsegment=[[str(v)for v in p]for p in [top,end]],
                         exactExposureLowerBoundM=str(min(top[1],end[1])-14),finiteGroundCoverageImpliedByCompleteFaceCoverage=True))
    assert exposed,'No actual exposed positive-dimensional interface on strict-cap path'
    edges.append(dict(originalSourceFacePair=[ROLE_IDS[a],ROLE_IDS[b]],exposedOriginalInterfaces=exposed))
   for cap in path['strictClearNonWallFaces']:
    ctx=old['complete104FaceInventory'][cap]['completeFiniteClearanceAndExposure'];assert ctx['groundProjectionCovered']and F(ctx['exactCertifiedLowerClearanceM'])>0
   paths.append(dict(originalSourceFace=original,fullOriginalPath=[ROLE_IDS[i]for i in chain],completeExposedInterfaces=edges,strictClearCapSourceFaces=[ROLE_IDS[i]for i in path['strictClearNonWallFaces']],rawPathVerbatim=path))
  expected_failed={f['originalSourceFace']for f in old['complete104FaceInventory']if f['completeSourceComponent']in [39,44]and not f['rawOrdinaryFiniteBoundProved']}
  actual_path_ids=[p['originalSourceFace']for p in paths]
  assert len(paths)==len(set(actual_path_ids))==60 and set(actual_path_ids)==expected_failed
  group_ids=set(PART_FACES[39]+PART_FACES[44])
  actual_group_grade=[c for c in old['completeActualGradeIntersection']['contacts']if ROLE_IDS[c['sourceFaceA']]in group_ids and c['dimension']==1 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2]
  assert actual_group_grade and {ROLE_IDS[c['sourceFaceA']]for c in actual_group_grade}&set(PART_FACES[39])
  assert {ROLE_IDS[c['sourceFaceA']]for c in actual_group_grade}&set(PART_FACES[44])
  rows.append(dict(arithmetic=mode,completeWholeSourceWorldSHA256=stream['completeWorldTriangleSHA256'],completeOriginalRoleFaces=104,
                   complete39And44ExposedOriginalCapPaths=paths,complete39And44ActualGradeContacts=actual_group_grade,namedIsolatedOpenPost43Proof=post,
                   original43MainbodyContactAbsent=True,rawWholePartFootingFailuresRetained=True,
                   sourceBackedCurrentRoleProposed=True,fullPhysicalAcceptance=False,installationApproved=False))
 save(DOC/'proposal.json.gz',dict(uids=[UID],sourceSHA256=SOURCE_SHA,rows=rows,completeGroundSHA256=data['completeDrawnGroundSHA256'],
      complete104FaceInventoryPreserved=True,remaining18638NotCertified=True,groundRootProposedOnlyForNamed104=True,
      newTerrainProposed=False,sourceGeometryChanges=0,closedSolidClaim=False,loadBearingClaim=False,physicalAccepted=False,currentAcceptance=False,installationApproved=False))
 assert reservations.owns(lease)and manifest.read_bytes()==before
 for p,h in capt['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 refs +=[HERE/n for n in ['king_cheung_named_open_post_skin_20261011.py','test_king_cheung_named_open_post_skin_20261011.py','king_cheung_complete_ancillary_proposal_20261011.py','exact_original_finite_triangle_contacts_20261010.py','exact_original_face_conservative_clearance_v5_20261010.py','exact_original_projection_coverage_v2_20261010.py']]
 s=importlib.util.spec_from_file_location('king_post_role_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 r=m.freeze(BATCH,'named104-four-stream-canopy-clear-cap-exposed-interfaces-and-original-open-post-grade-ring-proposal',refs+[DOC/'proposal.json.gz'],dict(uids=[UID],completeRoleFaces=104,fullCurrentAcceptance=False,newlyInstalled=0))
 print(json.dumps(dict(jobId=r['jobId'],completeExposedPathsPerStream=60,openOriginalPostSkin43=True)),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists()
 claim=reservations.claim('king-cheung-current104-role-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
