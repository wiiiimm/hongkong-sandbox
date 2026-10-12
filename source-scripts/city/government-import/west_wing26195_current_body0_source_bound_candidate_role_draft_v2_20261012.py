"""DRAFT supervised exact current body0 candidate role; no acceptance/backfill."""
import argparse,json,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
import west_wing26195_body0_saved_grade_role_reconciliation_caller_draft_v1_20261012 as R
import west_wing26195_body0_source_bound_grade_role_draft_v1_20261012 as H
import west_wing26195_verified_body0_candidate_certificate_draft_v2_20261012 as C
import west_wing26195_current_typed_visual_surface_roles_draft_v1_20261012 as T
BATCH='government-xl-west-wing26195-current-body0-source-bound-candidate-role-v2-20261012';DOC=R.BASE/BATCH;LOCAL=HERE/'local'/BATCH;PROPOSAL=R.BASE/'government-xl-west-wing26195-current-body0-source-bound-candidate-role-proposal-v2-20261012';ROOT_PROPOSAL=R.PROPOSAL;INTERPRETATION=ROOT_PROPOSAL/'ROOT-bounded-source-interpretation-v1.json';ROOT_RECORD=ROOT_PROPOSAL/'ROOT-source-bound-candidate-reconciliation-v1.json';FREEZER=HERE/'west_wing26195_freeze_current_body0_source_bound_candidate_role_draft_v2_20261012.py';TEST=HERE/'test_west_wing26195_verified_body0_candidate_certificate_draft_v2_20261012.py';ref=T.ref
INTERPRETATION_SHA='c3c8e843f8b6f328df4ec2aeb6f62dc5c44946c75aaa7562dd245ac0b131921e';ROOT_RECORD_SHA='a57a321c8c7ed4ecefabd86e53bf9d6e3acefd3fc6bb4d44d076650153fdae55'
def validation():
 v=read(PROPOSAL/'test-validation.json');assert v['exactTests']==16 and v['exitCode']==0 and v['noDBQueries']and v['noReservations']and v['noNumericRecomputation'];assert v['codeRefs']==[ref(p)for p in [Path(C.__file__),TEST,Path(__file__),FREEZER]];assert ref(ROOT/v['testLog']['path'])==v['testLog'];s=(ROOT/v['testLog']['path']).read_text();assert 'Ran 16 tests'in s and s.rstrip().endswith('OK');return [ref(PROPOSAL/'test-validation.json')]+v['codeRefs']+[v['testLog'],ref(PROPOSAL/'METHOD.md'),ref(R.BASE/'government-xl-west-wing26195-current-body0-source-bound-candidate-role-proposal-v1-20261012/actual-preflight-failure-audit-v1.json')]
def inputs():
 assert ref(INTERPRETATION)['sha256']==INTERPRETATION_SHA and ref(ROOT_RECORD)['sha256']==ROOT_RECORD_SHA
 data=[];receipts=[]
 for name,(job,sha)in R.RECEIPTS.items():
  p=R.BASE/R.P.BATCHES[name]/'result.json';assert ref(p)['sha256']==sha;r=read(p);assert r['jobId']==job and r['sourceOnly']and not r['physicalAccepted']
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(job,)).fetchone()==('complete',r)
  for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
  d,_=R.P.load(name);data.append(d);receipts.append(r)
 _,scope,*_=T.inputs();assert len(scope['canonicalReservationResources'])==15
 visual=read(T.M.VISUAL/'context.json');assert ref(ROOT/visual['source']['path'])['sha256']==H.SOURCE
 captured=read(T.M.D.S.G.P.F.CAP/'actual-render-geometry.json.gz');actual=next(x for x in captured['rows']if x['uid']==H.UID);assert actual['sourceSHA256']==H.SOURCE and actual['loadedGroupScale']==[1,1,1] and actual['sourceGeometryChanges']==0 and captured['startEndAllInputsVerified']
 original=read(T.M.D.S.G.P.F.CAP/'original-full-source-root-context.json.gz');assert original['uid']==H.UID and original['sourceGeometryChanges']==0 and original['completeOriginalWorldSHA256']==data[0]['allFourStreamBindings']['original']['wholeWorldSHA256']
 identity=dict(uid=H.UID,sourceSHA256=H.SOURCE,sourcePreserved=True,unitScale=actual['loadedGroupScale'][0],poseChanges=0,actualGroupMatrixWorldSHA256=H.sha(actual['loadedGroupMatrixWorldFloat64']),actualRootTranslation=actual['cataloguePreparedRootTranslation'],rawInstalledEntrySHA256=H.sha(actual['rawInstalledEntry']),completeOriginalWorldSHA256=original['completeOriginalWorldSHA256'],completeCapturedGroundSHA256=scope['completeActualGroundSHA256'])
 contracts=read(R.BASE/'government-xl-west-wing26195-body0-saved-facet-role-reconciliation-proposal-v1-20261012/existing-carrier-contract-refs.json')
 for e in contracts['codeRefs']:assert ref(ROOT/e['path'])==e
 interpretation=read(INTERPRETATION);root_record=read(ROOT_RECORD)
 for e in interpretation['sourceViewRefs']:assert ref(ROOT/e['path'])=={k:e[k]for k in ['path','sha256']}
 replayed=H.verify(*data,identity,contracts,expected_binding=H.binding(*data,identity,contracts),interpretation=interpretation);certificate=C.verify(replayed,root_record,interpretation)
 return scope,receipts,certificate

def fence(scope,lease,codes):
 assert reservations.owns(lease)and ref(ROOT/'3d-viewer/city/data/manifest.json')==scope['currentManifest']
 for path,h in scope['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h
 for e in codes:assert ref(ROOT/e['path'])==e
 before=read(T.M.D.S.G.P.F.CAP/'protected-state-before.json');assert json.loads(json.dumps(T.M.D.S.G.P.F.state(before['uids']),default=str))==before['rows']
def main():
 a=argparse.ArgumentParser();a.add_argument('--owned',action='store_true');a=a.parse_args();valid=validation();scope,receipts,certificate=inputs();assert not(DOC/'diagnostic.json.gz').exists()
 if not a.owned:
  c=reservations.claim('westwing-body0-candidate-role-'+str(uuid.uuid4()),scope['canonicalReservationResources'],batch=BATCH,ttl=1800);assert c['ok'],c;save(LOCAL/'reservation.json',json.loads(json.dumps(c['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','1800','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True);return
 lease=read(LOCAL/'reservation.json');walker=T.M.D.S.G.P.F.module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','westwingbody0candidateclosure');paths=set();walker.local_imports(Path(__file__),paths);walker.local_imports(FREEZER,paths);codes=[ref(p)for p in sorted(paths)]+valid+[ref(INTERPRETATION),ref(ROOT_RECORD)]
 fence(scope,lease,codes);assert reservations.heartbeat(lease)['ok'];fence(scope,lease,codes)
 save(DOC/'diagnostic.json.gz',dict(sourceOnly=True,physicalAccepted=False,installationApproved=False,modelReviewWrites=0,sourceGeometryChanges=0,terrainGeometryChanges=0,legacyDeliveryAnd15ReviewsUnchanged=True,noCompletedNumericArithmeticRerun=True,currentManifest=scope['currentManifest'],allFourStreamBindings=certificate['allFourStreamBindings'],completeSourceFaces=46918,completeSourceBodies=118,body0CandidateRoleCertificate=certificate,raw42OrdinaryFailuresAnd443StrictWarningsRetained=True,evidenceRefs=codes+[ref(R.BASE/R.P.BATCHES[n]/'result.json')for n in R.RECEIPTS]+[{k:e[k]for k in ['path','sha256']}for e in read(INTERPRETATION)['sourceViewRefs']]))
 print(json.dumps(dict(body0SourceRoleCandidateQualified=True,gradeRootAccepted=False,remainingBodyObligations=117,physicalAccepted=False)),flush=True);subprocess.run([sys.executable,str(FREEZER),'--lease-file',str(LOCAL/'reservation.json')],cwd=ROOT,check=True)
if __name__=='__main__':main()
