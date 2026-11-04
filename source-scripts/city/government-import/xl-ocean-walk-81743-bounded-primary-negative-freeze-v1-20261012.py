"""UNEXECUTED primary-packet/no-correspondence checkpoint; no numerical retry."""
import importlib.util,json,subprocess,sys,uuid
from pathlib import Path
from PIL import Image
from run import ROOT,HERE,read,save,digest,connect,reservations
BASE=ROOT/'docs/astra-city/government-import'
PACKET=BASE/'government-xl-ocean-walk-bounded-primary-floorplan-v1-20261012'
CAPTURE=BASE/'government-xl-ocean-walk-current-actual-ground-capture-v1-20261012'
PRIOR=BASE/'government-xl-ocean-walk-two-nonsteep-original-counterparts-v1-20261012/result.json'
PRIOR_SHA='b944a8320574b1052f1f33e319a9c15a3db0390aac1f1976495f2e7669bb1dd3'
PRIOR_JOB='8a3cf79a36946e62a54b761d97f99104eff6e460d60d80841dd606cd0c59bda3'
INSPECTION_SHA='6d6fdb55b2695ee2629dbbc7fddb13367c74c991534e43ee7dc56598d9137258'
UID='landsd/81743:0';SOURCE='52e0d6b6341f664cc18ee8a894e1c4c5e5dbc1b05729bb43deb8c109e0fac8cb'
MANIFEST='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
BATCH='government-xl-ocean-walk-bounded-primary-negative-v1-20261012';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
METHOD=BASE/'government-xl-ocean-walk-bounded-primary-negative-draft-v1-20261012/METHOD.md'
def preflight():
 assert not DOC.exists();assert digest(PRIOR.read_bytes())==PRIOR_SHA;prior=read(PRIOR)
 assert prior['jobId']==PRIOR_JOB and prior['uids']==[UID] and len(prior['evidenceRefs'])==768 and prior['currentAcceptance']is False
 inspection_path=PACKET/'actual-inspection-bindings.json';assert digest(inspection_path.read_bytes())==INSPECTION_SHA;inspection=read(inspection_path)
 assert inspection['currentManifestUnchanged']==MANIFEST and inspection['noNeonJob']is True and inspection['architecturalRoleAccepted']is False and inspection['currentAcceptance']is False
 packet_pins=inspection['completeLocalFileBindings'];assert len(packet_pins)==21 and len({p['path']for p in packet_pins})==21
 assert {str(p.relative_to(ROOT))for p in PACKET.iterdir()if p.is_file()}=={p['path']for p in packet_pins}|{str(inspection_path.relative_to(ROOT))}
 refs=[Path(__file__),METHOD,PRIOR,inspection_path,CAPTURE/'capture-inputs.json.gz',CAPTURE/'selection.json.gz']
 for pin in prior['evidenceRefs']+packet_pins:
  p=ROOT/pin['path'];assert digest(p.read_bytes())==pin['sha256'];refs.append(p)
 images=inspection['actualImageInspection'];assert len(images)==4 and len({r['path']for r in images})==4
 for row in images:
  p=ROOT/row['path'];assert p.parent==PACKET and row['actuallyViewed']is True and row['exact6034And6035CorrespondenceAccepted']is False and digest(p.read_bytes())==row['sha256']
  with Image.open(p)as image:assert list(image.size)==row['actualOriginalDimensions']
 selection=read(CAPTURE/'selection.json.gz');assert len(selection['rows'])==1;row=selection['rows'][0]
 assert row['uid']==UID and row['sourceSHA256']==SOURCE;asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==SOURCE;refs.append(asset)
 inputs=read(CAPTURE/'capture-inputs.json.gz');resources=inputs['canonicalResources'];assert len(resources)==30 and len(set(resources))==30 and 'building:'+UID in resources and 'terrain-patch:'+UID in resources and inputs['manifestSHA256']==MANIFEST
 refs.extend(HERE/p for p in ['run.py','xl-popcorn-source-investigations-checkpoints-20261009.py']);refs.extend(HERE.parent/'shared-modelling'/p for p in ['db.py','jobs.py','reservations.py'])
 pins={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in refs};assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==MANIFEST
 return prior,inspection,refs,pins,resources

def owned(state):
 prior,inspection,refs,pins,resources=state;lease=read(LEASE);assert lease['resources']==resources and reservations.owns(lease)
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(PRIOR_JOB,)).fetchone()==('complete',prior)
 finding=dict(uids=[UID],sourceSHA256=SOURCE,capturedManifestSHA256=MANIFEST,priorCompletedCounterpartJob=PRIOR_JOB,priorResultFileSHA256=PRIOR_SHA,primaryPacketInspectionVerbatim=inspection,primaryFindingsVerbatim=(PACKET/'PRIMARY_FINDINGS.md').read_text(encoding='utf-8'),boundedPrimarySearchOnly=True,noExact6034And6035CorrespondenceEstablished=True,sourceFacet6031NotCertifiedExposedTop=True,sourceRoleStillUnknown=True,all306BodyObligationsPreserved=True,all99RawFailuresPreserved=True,twelveNoGradeAndFourteenVacuousRecordsUncredited=True,sixBasicRegressionsPreserved=[203829,203832,203836,204242,336959,336960],elevenSupplierInterfacesPreserved=[32856,83161,203411,203416,203842,203852,308292,203832,203836,336959,336960],videoThumbnailOnlyNotFullVideoReviewed=True,noNumericalPredicateRecomputed=True,sourceEvidenceInterpretationUsedAI=True,sourceGeometryChanges=0,terrainGeometryChanges=0,architecturalRoleAccepted=False,identityAccepted=False,physicalAccepted=False,currentAcceptance=False,installationApproved=False,modelReviewWrites=0,newlyInstalled=0)
 save(DOC/'diagnostic.json.gz',finding);refs.append(DOC/'diagnostic.json.gz')
 def end_fence():
  assert reservations.owns(lease)and digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==MANIFEST
  for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
 end_fence();s=importlib.util.spec_from_file_location('ocean_primary_negative_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 out=m.freeze(BATCH,'bounded-primary-packet-no-exact-source-correspondence-evidence-hold',refs,dict(uids=[UID],sourceSHA256=SOURCE,priorCompletedCounterpartJob=PRIOR_JOB,noExact6034And6035CorrespondenceEstablished=True,all306BodyObligationsPreserved=True,sourceOnly=True,currentAcceptance=False,physicalAccepted=False,installationApproved=False,modelReviewWrites=0,newlyInstalled=0));end_fence();print(json.dumps(dict(jobId=out['jobId'],sourceOnly=True,currentAcceptance=False)),flush=True)
def main():
 state=preflight()
 if '--owned'in sys.argv:return owned(state)
 assert not LOCAL.exists();claim=reservations.claim('ocean-primary-negative-'+str(uuid.uuid4()),state[-1],batch=BATCH,ttl=3600);assert claim['ok'],claim;save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,str(Path(__file__)),'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
