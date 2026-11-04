"""ROOT-only fresh full-parent/all25 production capture of new PolyU nominee.

Requires final exact successful nominee receipt/pins. No old capture rerun,
source geometry edit, tolerance waiver, MAX or installation approval.
"""
from pathlib import Path
import sys,json,uuid,time,subprocess,shutil
import numpy as np
import polyu_five_eligible_current_parent_nomination_v3_20261014 as nomination
from polyu_saved_parent_cell_capture_binding_v3_draft_20261014 import validate_binding
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from run import ROOT,HERE,read,save,connect,reservations
ref,check=nomination.ref,nomination.check;prior=nomination.prior
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-polyu-parent-cell-actual-production-capture-v3-20261014'
DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
RUNTIME=HERE/'polyu_parent_cell_actual_production_runtime_v3_draft_20261014.mjs'
ACTORS=HERE/'polyu_five_parent_complete_current_actor_capture_v2_20261014.mjs'
PREVIOUS_CAPTURE=BASE/'government-xl-polyu-five-current-parent-actual-production-capture-v2-20261014'
NOMINATION_DOC=BASE/'government-xl-polyu-saved-parent-cell-repacking-v1-20261014'
PREVIOUS_CAPTURE_JOB='8f204d9c83bc0cc6ca45bb56da6da2fb8b70255c5af6c7dd37f346f73aceae9e'
CURRENT='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7'
OLD_DOC=BASE/'government-xl-polyu-sports305582-saved-private-candidate-runtime-only-v1-20261013';OLD_JOB='ce2589c6c43d007f527d6bc78e51204abf4344a261fd41b0436dc1c6234d316f'
VALIDATOR=HERE/'resolve-pass-indexed-parent-clipping.py'

def load():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))and pins['runtime']==ref(RUNTIME)
 for q in distinct_refs(pins['codeRefs']+pins['inputRefs']):check(q)
 receipt=read(NOMINATION_DOC/'result.json');assert receipt['jobId']==pins['completedNominationJob']and not receipt['physicalAccepted']and not receipt['installationApproved']
 verification=read(NOMINATION_DOC/'ROOT-VERIFIED.json');assert verification['jobId']==receipt['jobId']and verification['exactNeonReadback']and verification['allEvidenceHashesVerified']and verification['leaseReleased']
 old_capture=read(PREVIOUS_CAPTURE/'result.json');assert old_capture['jobId']==PREVIOUS_CAPTURE_JOB
 old_input=read(PREVIOUS_CAPTURE/'input.json.gz');previous=read(check(old_input['newNomination']))
 nom=read(NOMINATION_DOC/'private-saved-parent-cell-repacked-nomination.json.gz')
 assert nom['previousCompleteV3Nomination']==old_input['newNomination']and nom['previousPrivateCandidate']==old_input['previousPrivateCandidate']
 assert nom['eligibleUIDs']==previous['eligibleUIDs']and nom['all25AffectedActors']==previous['all25AffectedActors']==prior.UIDS
 records=read(nomination.DOC/'complete-five-mask-partition-diagnostic.json.gz')['allEligibleMaskOccurrences']
 raw=validate_binding(nom,previous,records,old_input['fullParentDomain'])
 assert len(raw)==pins['completeNewNativeFacets']and nomination.feasibility.sha(raw)==pins['completeNewRawSHA256']
 assert len(nom['newNativeMesh']['position'])//3==pins['completeNewPositionVertices']
 assert nomination.feasibility.sha(raw[:1485])==nomination.PREFIX_PACKED_SHA
 patch=read(check(old_input['previousPrivateCandidate']));base=read(nomination.BUILD/'full-computed-private-candidate-and-account.json.gz')
 result=read(nomination.feasibility.DOC/'complete-nine-parent-restoration-feasibility.json.gz')
 proof=old_input['complete25SourceEvidence'];guards=old_input['previousOriginalGuardRows']
 assert [r['uid']for r in guards]==prior.UIDS and [r['uid']for r in proof['rows']]==prior.UIDS
 assert len([r for r in guards if r['reasons']==['increased-neighbour-ground-gap']])==9
 assert sum(r['checks']for r in guards if r['reasons']==['increased-neighbour-ground-gap'])==3366
 actors=read(PREVIOUS_CAPTURE/'complete-fresh-current-native59527-and24-BASIC.json.gz')
 assert actors['startEndAllInputsVerified']and actors['currentManifestSHA256']==CURRENT and len(actors['basicRows'])==24 and actors['nativeRow']['completeFaces']==59527
 for path,h in actors['inputHashes'].items():check(dict(path=path,sha256=h))
 original=read(PREVIOUS_CAPTURE/'native59527-unchanged-provider-original-world.json.gz')
 assert original['completeFaces']==59527 and original['originalWorldSHA256']=='4f527cba16bd9e54f70c773fdcf7febec3e7c3d6d005bfed5b1f62df8fc315b8'
 assert nomination.feasibility.sha(original['completeWorldTriangles'])==original['originalWorldSHA256']
 assert original['source']==old_input['targetedNativeSource']['asset']
 resources=sorted(['building:'+u for u in prior.UIDS]+['terrain-patch:'+u for u in prior.UIDS]+['immutable-source-proof:'+BATCH]);assert len(resources)==51
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT
 return pins,receipt,nom,raw,base,patch,result,proof,guards,resources

def schema_only():
 pins,receipt,nom,raw,base,patch,result,proof,guards,resources=load()
 return dict(passed=True,caller=ref(Path(__file__)),runtime=ref(RUNTIME),completedNominationJob=receipt['jobId'],completeNewNativeFacets=len(raw),completeNewRawSHA256=nomination.feasibility.sha(raw),oldPrivate3214MappingComplete=True,currentParent12MappingComplete=True,parentCell8011UnchangedAnd24448RegionsBound=True,allOriginalPositionIncludingUnusedPrefixRetained=True,completeActors=25,canonicalResources=resources,wholeNative59527BeforeAfterPending=True,wholeOwned10536FourWorldAnd752Negatives21RolesRetained=True,allOriginalNine3366GuardSitesNeedActualReplay=True,fullParentGridNodes=1247,noProductionImportCaptureSourceCalculationDBLeaseWorker=True,fullParentCellProofReferencesResolved=True,complete832And1485PrefixHashPreserved=True)

def owned():
 lease=read(LEASE);assert reservations.owns(lease) and not DOC.exists();last=time.monotonic()
 def pulse():
  nonlocal last
  if time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok'] and reservations.owns(lease);last=time.monotonic()
 pins,receipt,nom,raw,base,patch,result,proof,guards,resources=load();assert lease['resources']==resources
 prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed'] and prep['caller']==ref(Path(__file__)) and prep['runtime']==ref(RUNTIME)
 binding_validation=read(check(prep['bindingValidationRef']));assert binding_validation['passedTests']==8 and binding_validation['failedTests']==0 and binding_validation['exitCode']==0
 assert binding_validation['executedCodeRefs']==[ref(HERE/'polyu_saved_parent_cell_capture_binding_v3_draft_20261014.py'),ref(HERE/'test_polyu_saved_parent_cell_capture_binding_v3_draft_20261014.py')]
 refs=pins['codeRefs']+pins['inputRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'METHOD.md'),ref(PROPOSAL/'actual-readonly-preparation.json')]+prep['evidenceRefs']+[prep['bindingValidationRef']]+binding_validation['evidenceRefs']
 for folder,job in [(NOMINATION_DOC,receipt['jobId']),(PREVIOUS_CAPTURE,PREVIOUS_CAPTURE_JOB)]:
  q=read(folder/'result.json')
  with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(job,)).fetchone()==('complete',q)
  refs+=[ref(folder/'result.json')]+q['evidenceRefs']
 refs=distinct_refs(refs)
 def fence():
  for q in refs:check(q);pulse()
  assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT and reservations.owns(lease)
 fence();DOC.mkdir();g=patch['meta']['georef'];domain=[g['bE']-834500,816500-g['bN'],g['bE']+(patch['w']-1)*g['aE']-834500,816500-(g['bN']+(patch['h']-1)*g['aN'])]
 save(DOC/'input.json.gz',dict(schema='polyu-parent-cell-actual-production-capture-v3',currentManifestSHA256=CURRENT,completedNominationJob=receipt['jobId'],newNomination=ref(NOMINATION_DOC/'private-saved-parent-cell-repacked-nomination.json.gz'),previousPrivateCandidate=nom['previousPrivateCandidate'],completeNewNativeFacets=len(raw),completeNewPositionVertices=len(nom['newNativeMesh']['position'])//3,fullParentDomain=domain,exact25CurrentForms=[r['currentForm']for r in proof['rows']],complete25SourceEvidence=proof,previousOriginalGuardRows=guards,originalGuardDefinition=ref(HERE/'check-neighbours.mjs'),targetedNativeSource=dict(uid='landsd/305793:0',entry=base['account']['installedPodiumFalseHoldVerbatim']['entry'],asset=base['account']['installedPodiumFalseHoldVerbatim']['asset']),allInputRefs=refs,all752Negatives21Bodies=result['all752FourModeNegativesAndWhole21SourceRolesRetained'],native59527WholeBeforeAfterStillPending=True,physicalAccepted=False))
 # Source/matrix/attributes are unchanged by private terrain packing. Reuse
 # only the exact complete current source tuple under current/start-end fences.
 for name in ['complete-fresh-current-native59527-and24-BASIC.json.gz','native59527-unchanged-provider-original-world.json.gz']:
  source=PREVIOUS_CAPTURE/name;target=DOC/name;shutil.copyfile(source,target);assert ref(target)['sha256']==ref(source)['sha256']
 save(DOC/'complete-source-input-reuse.json',dict(completedCaptureJob=PREVIOUS_CAPTURE_JOB,sourceRefs=[ref(PREVIOUS_CAPTURE/name)for name in ['complete-fresh-current-native59527-and24-BASIC.json.gz','native59527-unchanged-provider-original-world.json.gz']],sourceCurrentFormModuleAttributeMatrixTupleUnchanged=True,noNewSourceDecodeOrActorCapture=True,noOldGroundProofOrApprovalTransfer=True))
 command=['node',str(RUNTIME),str(DOC.relative_to(ROOT))]
 with (DOC/'actual-production-replay.log').open('xb')as log:r=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 save(DOC/'actual-runtime-command.json',dict(command=command,exitCode=r.returncode,noLiveChanges=True))
 if r.returncode==0:
  replay=read(DOC/'actual-production-replay.json.gz');assert replay['currentManifestSHA256']==CURRENT and replay['startEndAllInputsVerified'] and replay['currentExteriorXYZOrderedHashMatched']
  for path,h in replay['inputHashes'].items():refs.append(dict(path=path,sha256=h))
  captured=read(DOC/'private-native-terrain-candidate.json.gz');assert captured['nativeMesh']['position']==nom['newNativeMesh']['position'] and captured['nativeMesh']['index']==nom['newNativeMesh']['index']
  validator=prior.module('polyu_five_actual_unchanged_raw_validator',VALIDATOR);failure=None
  try:validator.validate_patch(captured,read(ROOT/'3d-viewer/city/data/terrain.json'))
  except (AssertionError,ValueError)as e:failure=dict(type=type(e).__name__,message=str(e))
  save(DOC/'real-validator-outcome.json',dict(passed=failure is None,actualFailure=failure,unchangedValidator=ref(VALIDATOR),noOldOverlapApproval=True,noToleranceChanges=True,notPhysicalAcceptance=True))
 else:save(DOC/'real-validator-outcome.json',dict(passed=False,notExecuted=True,actualRuntimeExitCode=r.returncode,noSamplerErrorWaiver=True))
 save(DOC/'diagnostic.json.gz',dict(completedNomination=ref(NOMINATION_DOC/'result.json'),runtimeExitCode=r.returncode,privateActualProductionCapture=True,complete25ScopeAnd51ResourcesRetained=True,targetedNative59527And24BASICExactInputReuse=True,reusedCaptureJob=PREVIOUS_CAPTURE_JOB,current305582BASICSeparateFromOwned10536Source=True,completeOriginalGuardDefinitionAndNine3366CountRetained=True,all752NegativesAnd21SourceRolesVerbatim=result['all752FourModeNegativesAndWhole21SourceRolesRetained'],independentFourConflictActorsVerbatim=nomination.CONFLICTS,native59527WholeBeforeAfterFinitePending=True,actualViewerFiniteOverlapMAXSeamRuntimeBrowserGatesPending=True,bodyZeroCrossingContextNotAdditionalEngineeringAdmissionGate=True,physicalAccepted=False,installationApproved=False,newlyInstalled=0))
 refs=distinct_refs(refs+[ref(p)for p in DOC.rglob('*')if p.is_file()]);fence()
 prior.module('polyu_five_actual_capture_freezer',prior.FREEZER).freeze(BATCH,'private-five-mask-fresh-whole-parent-actual-production-capture-only',[check(q)for q in refs],dict(uids=prior.UIDS,sourceOnly=True,privateCandidate=True,physicalAccepted=False,newlyInstalled=0))

def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--capture-five-current-parent-private-candidate-only'in sys.argv and not DOC.exists() and not LOCAL.exists()
 *_,resources=load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed'] and prep['caller']==ref(Path(__file__)) and prep['runtime']==ref(RUNTIME)
 claim=reservations.claim('polyu-parent-cell-production-v3-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
