"""DRAFT ONLY. Freeze complete diagnostics; no model-review/acceptance writes."""
import argparse,json
from pathlib import Path
from run import ROOT,HERE,read,connect,reservations
from west_wing26195_complete_current_finite_ground_draft_v2_20261012 import BATCH,DOC,LOCAL,CAP,RUNTIME,UID,FACES,CAP_JOB,SOURCE_SHA,MANIFEST_SHA,GROUND_SHA,NAMES,ref,module,state,load_inputs,validation_refs

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--lease-file',required=True);a=parser.parse_args();lease=read(Path(a.lease_file));assert reservations.owns(lease)and not(DOC/'result.json').exists();receipt,scope,selection,streams,ground,unused=load_inputs();validation_refs();d=read(DOC/'diagnostic.json.gz');before=read(CAP/'protected-state-before.json')
 assert d['uid']==UID and d['completeFaces']==FACES and d['completeGroundFaces']==3240 and d['completeGroundSHA256']==GROUND_SHA and d['currentNativeCount']==6649 and d['currentManifest']==scope['currentManifest']and d['ordinaryThresholdM']=='-1/2'
 assert d['sourceOnly']and d['legacyInstalledDeliveryPreserved']and d['legacyAcceptanceGapRetained']and not any(d[k]for k in ['physicalAccepted','installationApproved','sourceGeometryChanges','terrainGeometryChanges','sourceBodyRolesQualified','gradeRootProved','wholeEdgeCapPathsQualified','foreignHoldsDischarged','currentAllNativePhysicalProved'])
 assert set(d['allFourStreamBindings'])==NAMES and d['completeActualUnusedPositionBindings']==unused;top=d['originalBodyCensus'];partition=[i for fs in top['sharedEdgeConnectedComponents']for i in fs]+top['exactNonrenderingOriginalFaces'];assert len(partition)==FACES and sorted(partition)==list(range(FACES))and d['genuineBodyObligations']==len(top['sharedEdgeConnectedComponents'])and d['zeroFaceObligations']==len(top['exactNonrenderingOriginalFaces'])and len(d['completeOriginalPlaneAttribution'])==FACES
 from run import digest
 for name,s in streams.items():
  sh=digest(s.tobytes());key=digest((sh+GROUND_SHA).encode());assert d['allFourStreamBindings'][name]==dict(completeFaces=FACES,wholeWorldSHA256=sh,wholeGroundSHA256=GROUND_SHA,proofTupleSHA256=key);proof=d['distinctCompleteFiniteProofs'][key];rows=proof['allWholeFacetProofs'];assert proof['completeFaces']==FACES and [r['face']for r in rows]==list(range(FACES))
  for r in rows:
   assert r['selection']['completeGroundSHA256']==GROUND_SHA and r['selection']['completeGroundFacetCount']==3240 and r['selection']['everyNoncandidateStrictlyDisjoint']and r['selection']['touchingAndCollapsedProjectionsRetained'];assert r['originalGroundFaceBySelectedKernelFace']==r['selection']['selectedOriginalGroundFaces']
  for field,predicate in [('ordinaryFailingFaces','ordinaryFiniteProved'),('coverageFailingFaces','completeProjectionCovered'),('strictUncertifiedFaces','strictPositiveFiniteProved')]:assert proof[field]==[r['face']for r in rows if not r[predicate]]
 assert set(d['distinctCompleteFiniteProofs'])=={b['proofTupleSHA256']for b in d['allFourStreamBindings'].values()}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(CAP_JOB,)).fetchone()==('complete',receipt)
 assert json.loads(json.dumps(state(before['uids']),default=str))==before['rows'];walker=module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','westwing_finite_freezer');paths=set();walker.local_imports(Path(__file__),paths);walker.local_imports(HERE/'west_wing26195_complete_current_finite_ground_draft_v2_20261012.py',paths)
 for e in d['evidenceRefs']+receipt['evidenceRefs']:assert ref(ROOT/e['path'])==e;paths.add(ROOT/e['path'])
 for path in [DOC/'diagnostic.json.gz',LOCAL/'reservation.json']:paths.add(path);walker.declared_refs(read(path),paths)
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')==scope['currentManifest']and reservations.owns(lease)
 result=walker.F.freeze(BATCH,'existing-west-wing-complete-current-finite-ground-no-root-or-physical-approval',sorted(paths),dict(uids=[UID],sourceSHA256=SOURCE_SHA,sourceOnly=True,currentManifestSHA256=MANIFEST_SHA,nativeCount=6649,completeOriginalFaces=FACES,completeActualGroundFaces=3240,genuineBodyObligations=d['genuineBodyObligations'],zeroFaceObligations=d['zeroFaceObligations'],allFourWorldsComplete=True,legacyInstalledDeliveryPreserved=True,legacyPhysicalAcceptanceGapRetained=True,physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges=0,modelReviewWrites=0,gradeRootProved=False,wholeEdgeCapPathsQualified=False,foreignHoldsDischarged=False))
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 for e in result['evidenceRefs']:assert ref(ROOT/e['path'])==e
 assert json.loads(json.dumps(state(before['uids']),default=str))==before['rows']and ref(ROOT/'3d-viewer/city/data/manifest.json')==scope['currentManifest']and reservations.owns(lease);print(json.dumps(dict(jobId=result['jobId'],allRefs=len(result['evidenceRefs']),physicalAccepted=False)),flush=True)
if __name__=='__main__':main()
