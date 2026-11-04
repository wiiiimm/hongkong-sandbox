"""Receipt-only collection repair; every completed Nam check remains immutable."""
import argparse,json,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
import nam_fung79099_existing_basic_current_install_qualification_draft_v3_20261012 as Q
BATCH='government-xl-nam-fung79099-current-install-qualification-receipt-recovery-v1-20261012';DOC=Q.B/BATCH;LOCAL=HERE/'local'/BATCH;PROPOSAL=Q.B/'government-xl-nam-fung79099-current-install-qualification-receipt-recovery-proposal-v1-20261012'
AUDIT=Q.PROPOSAL/'actual-v3-receipt-collector-failure-release-current-state-audit.json'
def inputs():
 pins=read(PROPOSAL/'executable-pins.json');assert Q.Q.ref(Path(__file__))==pins['caller']
 for e in pins['inputs']:assert Q.Q.ref(ROOT/e['path'])==e
 data=Q.pinned_inputs();audit=read(AUDIT);assert audit['actualTerminalExitCode']==1 and audit['numericalAndRuntimeQualificationCompleted']and audit['stagingReady']and audit['releasedAtVerified']and audit['ownsFalse']
 for e in audit['savedOutputs']+[audit['executedCaller'],audit['terminalLog'],audit['lease']]:assert Q.Q.ref(ROOT/e['path'])==e
 d=read(Q.DOC/'qualification.json');assert d['scriptChecksPassed']and d['acceptanceReadyForStaging']and not d['remainingActualBlockers']and not d['installationApproved'];assert d['currentManifest']==data[5]['currentManifest']and d['currentNativeCount']==6649
 v=read(Q.DOC/'validation.json');s=read(Q.DOC/'production-support-budget-loader.json');assert v['loaderAccepted']==v['checksPassed']==1 and v['exceptions']==0 and s['checksPassed']==19 and s['startAndEndInputHashesVerified']and s['ordinaryBudgetLimitsUnchanged']
 for path,h in s['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h
 for path,h in v['hashes'].items():
  p=ROOT/path
  if not p.exists():p=Q.LOCAL/path
  assert digest(p.read_bytes())==h
 return pins,data,audit,d

def main():
 p=argparse.ArgumentParser();p.add_argument('--preflight-only',action='store_true');p.add_argument('--owned',action='store_true');a=p.parse_args();pins,data,audit,outcome=inputs();before=data[6]
 if a.preflight_only:print(json.dumps(dict(exactSavedQualificationAndCurrentReadOnlyPreflightPassed=True,noMathOrLoaderExecuted=True,noWorker=True)));return
 if not a.owned:
  assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim('nam-qualification-receipt-only-'+str(uuid.uuid4()),['building:'+u for u in before['uids']],batch=BATCH,ttl=3600);assert claim['ok'];save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True);return
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);assert reservations.heartbeat(lease)['ok'];inputs();walker=Q.Q.module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','nam_receipt_only_closure');paths=set();walker.local_imports(Path(__file__),paths);walker.declared_refs(outcome,paths)
 # All saved arrays/list-valued JSON files remain explicitly included.
 for folder in [Q.DOC,Q.LOCAL,Q.PROPOSAL,Q.FAILED,Q.FAILED_PROPOSAL,HERE/'local'/Q.FAILED.name,Q.COMPLETED,Q.COMPLETED_PROPOSAL,HERE/'local'/Q.COMPLETED.name,PROPOSAL,LOCAL]:paths.update(p for p in folder.rglob('*')if p.is_file())
 for r in [data[2],data[3],data[4],data[10],data[13]]:paths.update(ROOT/e['path']for e in r['evidenceRefs'])
 paths.update([Q.ROOT_NOTE,Q.BUDGET,Path(__file__),AUDIT])
 for file in Q.DOC.glob('*.json'):
  obj=read(file)
  if isinstance(obj,dict):
   for path in obj.get('inputHashes',{}):paths.add(ROOT/path)
 save(DOC/'receipt-recovery.json',dict(actualCompletedQualification=Q.Q.ref(Q.DOC/'qualification.json'),failedCollectorAudit=Q.Q.ref(AUDIT),allSuccessfulArithmeticAndRuntimeChecksReused=True,noNumericalOrLoaderRerun=True,guardedDictionaryInputHashCollection=True,allListValuedSavedFilesExplicitlyIncluded=True,sourceGeometryChanges=0,terrainGeometryChanges=0,installationApproved=False));paths.add(DOC/'receipt-recovery.json');inputs();assert reservations.owns(lease)
 result=walker.F.freeze(BATCH,'nam-unchanged-original-complete-qualification-receipt-only-no-publication',sorted(paths),dict(uids=[Q.UID,Q.CARRIER],sourceOnly=False,completeFaces=13061,completeOriginalBodies=569,authoredZeroFaces=75,scriptChecksPassed=True,acceptanceReadyForStaging=True,physicalAccepted=True,installationApproved=False,newlyInstalled=0,sourceGeometryChanges=0,terrainGeometryChanges=0,wholeBASICReaccepted=False,modelReviewWrites=0,actualCompletedQualification=Q.Q.ref(Q.DOC/'qualification.json')))
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 for e in result['evidenceRefs']:assert Q.Q.ref(ROOT/e['path'])==e
 inputs();assert reservations.owns(lease);print(json.dumps(dict(jobId=result['jobId'],allRefs=len(result['evidenceRefs']),stagingReady=True,installationApproved=False)))
if __name__=='__main__':main()
