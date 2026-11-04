"""Prepare one unchanged source for staging; serial publication remains root-owned.
Every source/current gate is replayed before composing the narrow named role.
"""
from pathlib import Path
import importlib.util,json,subprocess,sys,uuid
from run import ROOT,HERE,read,save,digest,reservations
import lippo_tower_current_basic_complete_role_current_bound_v2_20261011 as bound
BATCH='government-xl-lippo-tower-only-current-complete-role-acceptance-v2-20261011';DOC=bound.BASE/BATCH;LOCAL=HERE/'local'/BATCH
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists() and not LOCAL.exists();inp=read(bound.INPUT/'input.json.gz')
 resources=['building:'+r['building']['uid'] for r in inp['completeCurrentForms']]
 claim=reservations.claim('lippo-current-role-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim
 try:
  result,entry=bound.verify_files(LOCAL)
  row=inp['rows'][0];raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==entry['sha256']
  destination=LOCAL/entry['asset'];destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(raw)
  catalogue=read(bound.PHYSICAL_LOCAL/'catalogue.json');assert len(catalogue['models'])==1;catalogue.update(area=BATCH,models=[entry]);save(LOCAL/'catalogue.json',catalogue)
  save(LOCAL/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));save(DOC/'staged-entry.json',entry)
  js=HERE/'xl-lippo-tower-current-basic-support-availability-budget-v2-20261011.mjs'
  proc=subprocess.run(['node',str(js),str(DOC/'staged-entry.json'),str(DOC/'production-support-budget-loader.json')],cwd=ROOT,capture_output=True,text=True)
  save(DOC/'production-support-budget-loader-command.json',dict(exitCode=proc.returncode,stdout=proc.stdout,stderr=proc.stderr));assert proc.returncode==0,proc.stderr
  support=read(DOC/'production-support-budget-loader.json')
  assert support['checksPassed']==19 and support['startAndEndInputHashesVerified'] and support['ordinaryBudgetLimitsUnchanged']
  assert support['currentManifest']==inp['currentManifest'] and support['sourceSHA256']==entry['sha256']
  result.update(productionSupportAvailabilityAndBudgetProof=ref(DOC/'production-support-budget-loader.json'),stageCandidateCatalogue=ref(LOCAL/'catalogue.json'),stageCandidateSource=ref(destination),sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,stageBrowserRequired=True,livePublicationAndBrowserRequired=True)
  save(DOC/'acceptance.json',result)
  tests=[]
  for filename in ['test_lippo_tower_current_basic_complete_role_policy_v2_20261011.py','test_lippo_tower_current_basic_complete_role_current_bound_v2_20261011.py']:
   p=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(HERE),'-p',filename,'-v'],cwd=ROOT,capture_output=True,text=True)
   tests.append(dict(file=filename,exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr,hermeticActualCapturedSourceCounterexamples=True));assert p.returncode==0,p.stderr
  save(DOC/'tests.json',dict(tests=tests,separateUnmockedProductionIdentityNativeAndNeonReplayBeforeTests=True,productionSupportMethodsAndSourceLoaderExecutedSeparately=True))
  bound.assert_live(inp,read(bound.INPUT/'complete-current-geometry.json.gz'));assert reservations.owns(claim['reservation'])
  refs=[Path(__file__),HERE/'lippo_tower_current_basic_complete_role_current_bound_v2_20261011.py',HERE/'lippo_tower_current_basic_complete_role_policy_v2_20261011.py',js,*[HERE/t['file'] for t in tests],*[p for p in LOCAL.rglob('*') if p.is_file()]]
  for folder in [bound.INPUT,bound.IDENTITY,bound.PHYSICAL,bound.ROLE,bound.SEPARATION,bound.DELTA]:
   receipt=read(folder/'result.json');bound.receipt_pins(receipt);refs.append(folder/'result.json');refs += [ROOT/r['path'] for r in receipt['evidenceRefs']]
  refs += [ROOT/p for p in support['inputHashes']]
  refs += [HERE/'exact_current_delta_catalogue_reference_binding_20261011.py',HERE/'test_exact_current_delta_catalogue_reference_binding_20261011.py']
  spec=importlib.util.spec_from_file_location('lippo_current_complete_role_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');freezer=importlib.util.module_from_spec(spec);spec.loader.exec_module(freezer)
  receipt=freezer.freeze(BATCH,'lippo-tower-complete-current-named-mainbody-join-basic-grade-clear-cap-acceptance-ready-for-staging-only',refs,dict(uids=[entry['uid']],currentManifest=inp['currentManifest'],scriptChecksPassed=True,physicalAccepted=True,acceptanceReadyForStaging=True,sourceGeometryChanges=0,terrainGeometryChanges=0,wholeBasicReaccepted=False,originalGovernmentPodiumUsedAsSupport=False,completeOwnedFaces=3597,completeRealOwnedComponents=5,completeForeignCurrentActors=19,completeCurrentNativeActualPositionActors=6639,stageBrowserRequired=True,livePublicationAndBrowserRequired=True))
  print(json.dumps(dict(jobId=receipt['jobId'],acceptanceReadyForStaging=True,installationApproved=False,newlyInstalled=0)),flush=True)
 finally:assert reservations.release(claim['reservation'])['ok']
if __name__=='__main__':main()
