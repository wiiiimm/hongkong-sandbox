"""UNEXECUTED actual current Aqua6653 draw/guard capture of completed four-parent nominee."""
from pathlib import Path
import json,sys,uuid,time,subprocess,shutil,importlib.util
from run import ROOT,HERE,read,save,connect,reservations
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from polyu_compact_runtime_mesh_projection_v1_draft_20261014 import mesh_binding,project,verify
import polyu_four_parent_current_capture_binding_v2_draft_20261014 as binding
from polyu_four_compatible_parent_region_nomination_v1_draft_20261014 import ref,check
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-polyu-four-compatible-parent-current-production-v2-20261014'
DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
RUNTIME=HERE/'polyu_four_parent_current_production_runtime_v2_draft_20261014.mjs'
NOM=BASE/'government-xl-polyu-four-compatible-parent-region-nomination-v1-20261014'
CAPTURE=BASE/'government-xl-polyu-append-source-region-historical-production-v1-20261014'
UPTON=BASE/'government-xl-upton-joint-original-functional-installed-v2-20261014';AQUA=BASE/'government-xl-aqua-marine193086-original-installed-v1-20261014'
FREEZER=HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py';VALIDATOR=HERE/'resolve-pass-indexed-parent-clipping.py'
def module(p,name):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def load():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))and pins['runtime']==ref(RUNTIME)
 for q in distinct_refs(pins['codeRefs']+pins['inputRefs']):check(q)
 receipt=read(NOM/'result.json');cert=read(NOM/'ROOT-VERIFIED.json');assert receipt['jobId']==cert['jobId']==pins['completedNominationJob']and cert['exactNeonReadback']and cert['allEvidenceHashesVerified']and cert['leaseReleased']
 nom=read(NOM/'private-compatible-current-parent-append-nomination.json.gz');old=read(check(nom['previousApprovedCandidate']));complete=binding.append_binding(nom,old)
 assert complete==pins['completeNewMeshBinding']and nom['previousApprovedCandidate']==pins['previousApprovedCandidate']
 source_input=read(CAPTURE/'input.json.gz');archive=source_input['historicalSceneManifestReference'];historical=read(check(archive));assert archive['sha256']==binding.OLD
 manifest_ref=ref(ROOT/'3d-viewer/city/data/manifest.json');assert manifest_ref['sha256']==binding.CURRENT
 current=read(check(manifest_ref));delta=binding.scene_delta(historical,current);domain=binding.grid_domain(old)
 assert domain==source_input['fullParentDomain']==[2002.5,-2067.5,2212.5,-1927.5]
 changed_terrain=[ROOT/'3d-viewer'/p for p in [binding.OLD_PATCH,binding.UPTON_PATCH]]
 delta['completeChangedTerrainBounds']=[dict(source=ref(p),**binding.terrain_disjoint(read(p),domain))for p in changed_terrain]
 oldmodels=[m for url in historical['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']]
 currentmodels=[m for url in current['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']]
 assert len(oldmodels)==len({m['uid']for m in oldmodels})==6650 and len(currentmodels)==len({m['uid']for m in currentmodels})==6653
 assert currentmodels[:6650]==oldmodels and [m['uid']for m in currentmodels[6650:]]==['landsd/12728:0','landsd/338946:0','landsd/193086:0']
 for folder,count in [(UPTON,6652),(AQUA,6653)]:
  c=read(folder/'ROOT-VERIFIED.json');r=read(folder/'result.json');assert c['jobId']==r['jobId']and c['exactNeonReadback']and c['allEvidenceHashesVerified']and c['leaseReleased']
  assert read(folder/'installed-acceptance.json')['manifest']['sha256']==(pins['uptonInstalledManifestSHA256']if count==6652 else binding.CURRENT)
 assert read(AQUA/'ROOT-VERIFIED.json')['snapshotId']=='be5f7671a989392d'
 assert read(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json')['snapshotId']=='be5f7671a989392d'
 actors=read(CAPTURE/'complete-fresh-current-native59527-and24-BASIC.json.gz');forms=source_input['exact25CurrentForms'];prior=source_input['previousOriginalGuardRows'];uids=[b['uid']for b in forms]
 assert len(uids)==len(set(uids))==25 and [p['uid']for p in prior]==uids and len(actors['basicRows'])==24 and actors['nativeRow']['completeFaces']==59527
 assert actors['nativeRow']['rawInstalledEntry']==next(m for m in currentmodels if m['uid']=='landsd/305793:0')
 native_uids={m['uid']for m in currentmodels};assert all(p['existingNative']==(p['uid']in native_uids)for p in prior)
 # Saved forms/source tiles/attributes are rebound only by exact relevant bytes;
 # the old manifest is an authenticated archive, never a current-hash alias.
 for q in pins['relevantActorSourceAndFormRefs']:check(q)
 assert sum(p['checks']for p in prior if p['reasons']==['increased-neighbour-ground-gap'])==3366
 delta['currentModels']=6653;delta['newFarBuildingMeshDomainQualificationStillPending']=True
 resources=sorted(['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH]);assert len(resources)==51
 return pins,receipt,nom,old,complete,source_input,forms,prior,delta,resources
def schema_only():
 p,r,n,o,c,i,f,g,d,resources=load()
 return dict(passed=True,caller=ref(Path(__file__)),runtime=ref(RUNTIME),completedNominationJob=r['jobId'],completeNewMeshBinding=c,
  originalGuardScope=25,originalNineGuardSamples=3366,currentManifestSHA256=binding.CURRENT,currentSnapshot='be5f7671a989392d',currentCatalogueModels=6653,
  currentSceneDelta=d,resources=resources,noDrawGuardFiniteDBLeaseWorker=True)
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
 def pulse():
  nonlocal last
  if time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 pins,receipt,nom,old,complete,source_input,forms,prior,delta,resources=load();assert lease['resources']==resources
 prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))and prep['runtime']==ref(RUNTIME)
 validation=read(check(prep['bindingValidationRef']));assert validation['passedTests']==7 and validation['failedTests']==0 and validation['exitCode']==0
 assert validation['executedCodeRefs']==[ref(Path(binding.__file__)),ref(HERE/'test_polyu_four_parent_current_capture_binding_v2_draft_20261014.py')]
 refs=distinct_refs(pins['codeRefs']+pins['inputRefs']+prep['evidenceRefs']+validation['evidenceRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'actual-readonly-preparation.json')])
 for folder in [NOM,UPTON,AQUA]:
  r=read(folder/'result.json')
  with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 def fence():
  for q in distinct_refs(refs):check(q);pulse()
  assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==binding.CURRENT and reservations.owns(lease)
 fence();DOC.mkdir();nomref=ref(NOM/'private-compatible-current-parent-append-nomination.json.gz')
 preservation=dict(unchangedPriorFacets=148459,unchangedOldMappings=3214,unchangedPrefixFacets=1485,retainedPriorPositionVertices=587502)
 projection=project(nom['newNativeMesh'],nomref,complete,preservation);verify(projection,nomref,complete,preservation)
 save(DOC/'compact-runtime-mesh-projection.json.gz',projection);projection_ref=ref(DOC/'compact-runtime-mesh-projection.json.gz');refs=distinct_refs(refs+[projection_ref])
 save(DOC/'input.json.gz',dict(schema='polyu-four-compatible-parent-current-production-v2',historicalReplay=False,currentAcceptance=False,physicalAccepted=False,
  currentManifestSHA256=binding.CURRENT,currentSnapshot='be5f7671a989392d',currentCatalogueModels=6653,currentSceneDeltaBinding=delta,
  completedNominationJob=receipt['jobId'],newNomination=nomref,runtimeProjection=projection_ref,completeMeshBinding=complete,explicitPreservationCounts=preservation,
  previousPrivateCandidate=nom['previousApprovedCandidate'],completeNewNativeFacets=complete['completeIndexedFaces'],completeNewPositionVertices=complete['completePositionVertices'],
  fullParentDomain=source_input['fullParentDomain'],exact25CurrentForms=forms,complete25SourceEvidence=source_input['complete25SourceEvidence'],previousOriginalGuardRows=prior,
  originalGuardDefinition=ref(HERE/'check-neighbours.mjs'),allInputRefs=refs,noOldGeometryOverlapApprovalTransferred=True))
 for name in ['complete-fresh-current-native59527-and24-BASIC.json.gz','native59527-unchanged-provider-original-world.json.gz']:
  source=CAPTURE/name;target=DOC/name;shutil.copyfile(source,target);assert ref(source)['sha256']==ref(target)['sha256']
 save(DOC/'exact-current-source-family-reuse.json',dict(sourceRefs=[ref(CAPTURE/name)for name in ['complete-fresh-current-native59527-and24-BASIC.json.gz','native59527-unchanged-provider-original-world.json.gz']],
  currentSceneDeltaBinding=delta,relevantActorSourceAndFormRefs=pins['relevantActorSourceAndFormRefs'],sameSourceEntryFormAttributeMatrixBytes=True,
  oldEmbeddedSceneEpochIsHistorical=True,noOldTerrainFiniteOrAcceptanceTransferred=True,wholeNative59527NewGroundStillRequired=True))
 command=['node',str(RUNTIME),str(DOC.relative_to(ROOT))]
 with(DOC/'actual-production-replay.log').open('xb')as log:p=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 save(DOC/'actual-runtime-command.json',dict(command=command,exitCode=p.returncode,noLiveChanges=True))
 if p.returncode==0:
  replay=read(DOC/'actual-production-replay.json.gz');assert replay['currentManifestSHA256']==binding.CURRENT and replay['startEndAllInputsVerified']and replay['currentExteriorXYZOrderedHashMatched']
  refs=distinct_refs(refs+[dict(path=p,sha256=h)for p,h in replay['inputHashes'].items()])
  candidate=read(DOC/'private-native-terrain-candidate.json.gz');assert mesh_binding({k:candidate['nativeMesh'][k]for k in ['position','index']})==complete and not candidate['nativeMesh'].get('sourceOverlap')
  failure=None
  try:module(VALIDATOR,'polyu_four_parent_real_validator').validate_patch(candidate,read(ROOT/'3d-viewer/city/data/terrain.json'))
  except (AssertionError,ValueError)as e:failure=dict(type=type(e).__name__,message=str(e))
  save(DOC/'real-validator-outcome.json',dict(passed=failure is None,actualFailure=failure,unchangedValidator=ref(VALIDATOR),noOldSourceOverlapTransferred=True,noThresholdChange=True))
  guards=read(DOC/'all25-original-production-guard-site-replay.json.gz');pending='existing-native-neighbour-requires-full-mesh-check'
  save(DOC/'guard-first-viability.json',dict(ordinaryGuardFailures=[dict(uid=r['uid'],reasons=[q for q in r['reasons']if q!=pending])for r in guards['rows']if any(q!=pending for q in r['reasons'])],
   allSamplerErrors=guards['allSamplerErrors'],gridErrors=[r for r in replay['allCandidateGridSamples']if r['error']],nativeWarningPreserved=[r for r in guards['rows']if pending in r['reasons']],
   all25RowsRetained=True,original3366SamplesReplayed=True,notWholeNativeOrPhysicalAcceptance=True,newDelta3NativeMeshSeparationStillPending=True))
 else:save(DOC/'real-validator-outcome.json',dict(passed=False,notExecuted=True,actualRuntimeExitCode=p.returncode,noErrorWaiver=True))
 refs=distinct_refs(refs+[ref(p)for p in DOC.rglob('*')if p.is_file()]);fence()
 result=module(FREEZER,'polyu_four_parent_capture_freezer').freeze(BATCH,'current-Aqua6653-private-complete-parent-actual-draw-and25-original-guard-capture',[check(q)for q in refs],
  dict(uids=[f['uid']for f in forms],sourceOnly=True,privateCandidate=True,currentManifestSHA256=binding.CURRENT,physicalAccepted=False,installationApproved=False,newlyInstalled=0,runtimeExitCode=p.returncode))
 fence();print(json.dumps(dict(jobId=result['jobId'],result=ref(DOC/'result.json'),runtimeExitCode=p.returncode)),flush=True)
def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only()));return
 if '--owned'in sys.argv:return owned()
 assert '--capture-current-four-parent-guards-only'in sys.argv and not DOC.exists()and not LOCAL.exists();load()
 prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))and prep['runtime']==ref(RUNTIME)
 *_,resources=load();claim=reservations.claim('polyu-current-four-parent-capture-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
