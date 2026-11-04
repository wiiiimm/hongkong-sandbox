"""DRAFT receipt-only correction: keep completed identity numerics and exit1."""
import argparse,json,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
import west_wing26195_current_unchanged_raw_owned_identity_draft_v1_20261012 as Q
BATCH='government-xl-west-wing26195-raw-owned-identity-receipt-only-recovery-v1-20261012'
DOC=Q.W.B/BATCH;LOCAL=HERE/'local'/BATCH
PROPOSAL=Q.W.B/'government-xl-west-wing26195-raw-owned-identity-receipt-recovery-proposal-v1-20261012'
AUDIT=Q.PROPOSAL/'actual-terminal-freezer-failure-release-audit-v1.json'
ref=Q.ref

def inputs():
 for e in read(PROPOSAL/'draft-code-pins.json')['refs']:assert ref(ROOT/e['path'])==e
 p,scope,before,native,_,capture=Q.inputs();audit=read(AUDIT)
 assert audit['exitCode']==1 and audit['freezerOrchestrationFailure']=="KeyError: uids" and audit['numericIdentityOutputsComplete']and audit['failedBeforeEnqueue']
 for e in audit['evidenceRefs']:assert ref(ROOT/e['path'])==e
 oldlease=read(Q.LOCAL/'reservation.json');assert not reservations.owns(oldlease)
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT id,status FROM astra_modelling.jobs WHERE batch=%s',(Q.BATCH,)).fetchall()==[]
  groups=c.execute('SELECT token,released_at FROM astra_modelling.reservation_groups WHERE token=%s OR batch=%s',(oldlease['token'],Q.BATCH)).fetchall()
 assert groups and all(released is not None for _,released in groups)
 d=read(Q.DOC/'identities.json');assert d['uid']==Q.W.UID and d['completeOriginalFaces']==46918 and d['completeOriginalWorldSHA256']==Q.WORLD_SHA and d['sourceOnly']and not d['physicalAccepted']
 assert d['rawFullCellIdentity']['passed']==audit['rawStrictPassed']and d['rawFullCellIdentity']['reasons']==audit['rawReasons']and d['ownedIdentity']['passed']==audit['ownedPassed']and d['ownedIdentity']['reasons']==audit['ownedReasons']
 return scope,before,native,capture,d,audit

def main():
 a=argparse.ArgumentParser();a.add_argument('--owned',action='store_true');a.add_argument('--preflight-only',action='store_true');args=a.parse_args();scope,before,native,capture,d,audit=inputs()
 if args.preflight_only:
  print(json.dumps(dict(receiptOnly=True,noNumericRerun=True,noReservations=True,rawPassed=d['rawFullCellIdentity']['passed'],ownedPassed=d['ownedIdentity']['passed'],allFailedRefsMatch=True)),flush=True);return
 if not args.owned:
  assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim('westwing-identity-receipt-recovery-'+str(uuid.uuid4()),scope['canonicalReservationResources'],batch=BATCH,ttl=1800);assert claim['ok'],claim
  save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
  subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','1800','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True);return
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)and not DOC.exists()
 walker=Q.W.module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','westwing_identity_receipt_closure');code=set();walker.local_imports(Path(__file__),code)
 freezer=Q.W.module(HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py','westwing_identity_receipt_freezer');walker.local_imports(HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py',code)
 refs=[ref(x)for x in sorted(code)]+audit['evidenceRefs']+[ref(AUDIT),ref(PROPOSAL/'METHOD.md'),ref(PROPOSAL/'draft-code-pins.json')]+capture['evidenceRefs']
 def fence():
  assert reservations.owns(lease)and ref(ROOT/'3d-viewer/city/data/manifest.json')==scope['currentManifest']
  for path,h in scope['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h
  for e in refs:assert ref(ROOT/e['path'])==e
  assert Q.native_row()==native and json.loads(json.dumps(Q.W.state(before['uids']),default=str))==before['rows']
 fence();assert reservations.heartbeat(lease)['ok'];save(DOC/'receipt-lineage.json',dict(originalFailedExecution=ref(AUDIT),originalNumericIdentity=ref(Q.DOC/'identities.json'),originalExitCode=1,originalCompletedJobExists=False,noIdentityNumericalRecomputation=True,currentManifest=scope['currentManifest'],rawFullCellIdentity=d['rawFullCellIdentity'],ownedIdentity=d['ownedIdentity'],sourceOnly=True,physicalAccepted=False));fence()
 # The sole result-schema repair is the generic freezer's required uids list.
 result=freezer.freeze(BATCH,'west-wing-completed-negative-identity-receipt-only-recovery',[ROOT/e['path']for e in refs],dict(uids=[Q.W.UID],sourceOnly=True,identityAccepted=False,sourceSHA256=Q.W.SOURCE_SHA,currentManifestSHA256=Q.W.MANIFEST_SHA,nativeCount=6649,completeOriginalFaces=46918,rawStrictPassed=d['rawFullCellIdentity']['passed'],rawReasons=d['rawFullCellIdentity']['reasons'],ownedPassed=d['ownedIdentity']['passed'],ownedReasons=d['ownedIdentity']['reasons'],noIdentityNumericalRecomputation=True,originalFailedExecution=ref(AUDIT),physicalAccepted=False,installationApproved=False,legacyAcceptanceBackfillAllowed=False,modelReviewWrites=0,qualification='Receipt-only orchestration recovery. Original raw/owned negative results, executed86582d bytes and exit1 are immutable. No identity policy/source/pose/terrain/review changes; all physical/root/legacy acceptance holds remain.'))
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 for e in result['evidenceRefs']:assert ref(ROOT/e['path'])==e
 fence();print(json.dumps(dict(jobId=result['jobId'],allRefs=len(result['evidenceRefs']),rawStrictPassed=result['rawStrictPassed'],rawReasons=result['rawReasons'],ownedPassed=result['ownedPassed'],ownedReasons=result['ownedReasons'],noNumericRerun=True)),flush=True)
if __name__=='__main__':main()
