"""Private Museum stage with exact original source and guarded BASIC estimate.
No publication; retain every raw clearance failure and authored crossing.
"""
from pathlib import Path
import copy,json,shutil,sys,uuid
from run import connect,reservations
import heritage165054_owned_saved_output_finalization_v1_20261014 as original
import heritage128971_corrected_basic_validation_v1_20261015 as shelter
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from timed_owned_lease_pulse_v1_20261014 import TimedOwnedLeasePulse
ROOT=original.ROOT;HERE=original.HERE;BASE=original.BASE;UID=original.UID
BATCH='government-xl-heritage165054-joint-private-stage-v1-20261015';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH;LOCAL=HERE/'local'/BATCH
read=original.read;save=original.save;ref=original.ref;check=original.check
FINITE=BASE/'government-xl-heritage165054-saved-full-actor-finite-v1-20261014'
IDENTITY=BASE/'government-xl-heritage165054-current-typed-identity-draft-v3-20261014/current-identity-output-v3/typed-current-identity.json'
REVIEW18=BASE/'government-xl-heritage165054-exact18-lower-closure-applicability-review-v1-20261014/ROOT-existing-warning-applicability.json'
REVIEW187=BASE/'government-xl-heritage165054-face187-context-v1-20261015/ROOT-exact187-lower-wall-interpretation.json'
EXPECTED=[187,12130,12131,12132,12150,12191,12192,12193,12194,12195,12199,12201,12202,12203,12249,12288,12290,12292,12293]
MODES={'providerOriginal','literal','explicitLeftF32','explicitBalancedF32'}

def qualify(diag,identity,finite,r18,r187,joint,corrected,capture):
 assert diag['uid']==identity['uid']==UID and identity['sourceSHA256']==original.SOURCE
 assert identity['passed']and identity['reasons']==[]and not identity['physicalSupportExemption']and not identity['runtimeExemption']
 assert diag['strictFoundationAccepted']and diag['loaderAccepted']==diag['runtimeChecksPassed']==1 and diag['runtimeExceptions']==0
 assert len(diag['rawRuntimeRows'])==1 and diag['rawRuntimeRows'][0]['uid']==UID and not diag['rawRuntimeRows'][0]['concerns']
 assert diag['ordinaryNumericReasons']==['terrain-intersects-source-over-0.5m']
 assert r18['rootFunctionalReviewAccepted']and r18['sourceInterpretationAccepted']and r18['sourceSHA256']==original.SOURCE
 assert r18['exactFailedSampleSourceFaceIDs']==EXPECTED[1:]and r18['applicableExistingReason']==diag['ordinaryNumericReasons'][0]
 assert not r18['independentStarCollisionExemption']and not r18['rawOrdinaryReasonResolved']
 assert r187['uid']==UID and r187['sourceFaceIDs']==[187]and r187['sourceInterpretationAccepted']and not r187['otherFacesApproved']and not r187['thresholdChanged']
 assert finite['completeOwnedOriginalFaces']==15140 and finite['completeOwnedFourWorlds']and finite['currentBASICActorsIncludingOwnedContext']==23
 owned=[r for r in finite['rows']if r['role']=='complete-owned-original'];assert len(owned)==1 and owned[0]['uid']==UID
 assert {w['mode']for w in owned[0]['worlds']}==MODES and len(owned[0]['worlds'])==4
 for w in owned[0]['worlds']:
  assert w['completeFaces']==15140 and w['findings']['candidateUncovered']==[]and w['findings']['candidateOrdinaryUnproved']==EXPECTED
 basic=[r for r in finite['rows']if r['role']!='complete-owned-original'];uids={r['uid']for r in basic};assert len(basic)==len(uids)==23
 for r in basic:
  assert len(r['worlds'])==3
  for w in r['worlds']:assert not w['findings']['candidateUncovered']and not w['findings']['currentClearCandidateUnproved']
 assert joint['originalBeforeStatePreserved']and not joint['regressions']and {r['uid']for r in joint['rows']}==uids and len(joint['rows'])==23
 assert all(not r['reasons']for r in joint['rows'])
 assert len(corrected['rows'])==3 and {r['mode']for r in corrected['rows']}=={'constructorFloat32World','leftFloat32World','balancedFloat32World'}
 for r in corrected['rows']:
  assert r['completeFaces']==108 and len(r['rows'])==108 and not r['candidateUnproved']and not r['newlyUnproved']
  assert all(x['after']['finite']['ordinaryBoundProved']and x['after']['finite']['projectionCovered']for x in r['rows'])
 assert capture['strictOutsideParentAndActorROIDrawUnchanged']and capture['startEndAllInputsVerified']and capture['completeCurrentBASICActors']==23
 return dict(uid=UID,exactOriginalSourceSHA256=original.SOURCE,rawOrdinaryNumericReasons=diag['ordinaryNumericReasons'],rawStrictFoundationPassed=True,rawFiniteUnprovedSourceFaceIDs=EXPECTED,exactLowerClosureSourceApplicabilityAccepted=True,numericalFailuresRelabelledAsPass=False,completeOwnedFaces=15140,completeOwnedWorlds=4,affectedBasicForms=23,ordinaryNeighbourRegressions=[],finiteIntroducedNeighbourFailures=[],authoredStarCrossingsRetained=True,independentStarSuppressed=False,sourceGeometryChanges=0,sourcePoseChanges=0,privateStageQualified=True,physicalFinalAccepted=False,publication=False,newlyInstalled=0)

def inputs():
 refs=[];receipts=[]
 for folder,job in [(shelter.DOC,'a26113965d4dcab83f44e93d524cd719b2417b7c5c1289fb6dc94f48fae3a47c'),(BASE/'government-xl-heritage165054-current-typed-identity-receipt-v3-20261014','fdbe6836f75e6e2a8d0951c91d974b88f8441e21093626e0997ba1481d246f41')]:
  r=read(folder/'result.json');v=read(folder/'ROOT-VERIFIED.json');assert r['jobId']==v['jobId']==job and v['exactNeonReadback']and v['allEvidenceHashesVerified']and v['leasesReleased' if folder.name=='government-xl-heritage165054-current-typed-identity-receipt-v3-20261014' else 'leaseReleased'];receipts.append(r)
  historical=folder.name=='government-xl-heritage165054-current-typed-identity-receipt-v3-20261014'
  if historical:
   rp=BASE/'government-xl-heritage165054-identity-current-reconciliation-v1-20261015/reconciliation.json';rebind=read(rp)
   assert rebind['historicalReceipt']==ref(folder/'result.json')and rebind['currentManifest']==ref(ROOT/'3d-viewer/city/data/manifest.json')and rebind['allRetainedFormsDeepEqual']
   check(rebind['exactHistoricalManifestBytes']);assert rebind['exactHistoricalManifestBytes']['sha256']==rebind['historicalManifestReference']['sha256']
   assert [q for q in r['evidenceRefs']if q!=rebind['historicalManifestReference']]==rebind['unchangedOtherHistoricalRefs']
   refs+=rebind['unchangedOtherHistoricalRefs']+[rebind['exactHistoricalManifestBytes'],ref(rp),rebind['caller']]+rebind['currentTileRefs']
  else:refs+=r['evidenceRefs']
  refs +=[ref(folder/'result.json'),ref(folder/'ROOT-VERIFIED.json')]
 paths=[original.DOC/'diagnostic.json.gz',IDENTITY,FINITE/'complete-current-candidate-full-actor-finite.json.gz',REVIEW18,REVIEW187,shelter.DOC/'joint-neighbour-comparison.json',shelter.DOC/'complete-corrected-basic-finite.json.gz',shelter.capture.DOC/'actual-production-capture-report.json.gz']
 data=[read(p)for p in paths];review=qualify(*data)
 for d in data[3:5]:refs+=d['evidenceRefs']
 refs +=[ref(p)for p in paths]+[ref(Path(__file__)),ref(HERE.parent/'island-detail-integration/publish.py'),ref(HERE.parent/'island-detail-integration/native_terrain_validation.py')]
 current=ref(ROOT/'3d-viewer/city/data/manifest.json');assert current['sha256']==original.CURRENT
 candidate=data[0]['candidate'];check(dict(path=candidate['path'],sha256=candidate['sha256']));refs.append(current)
 forms=read(shelter.capture.DOC/'input.json.gz')['currentForms'];assert len(forms)==23
 return data,review,candidate,forms,distinct_refs(refs),receipts

def main():
 data,review,candidate,forms,refs,receipts=inputs()
 for q in refs:check(q)
 if '--schema-only'in sys.argv:print(json.dumps(review));return
 assert sys.argv[1:]==['--stage-private-only']and not DOC.exists()and not STAGE.exists()and not LOCAL.exists()
 keys=reservations.normalise([r for r in shelter.capture.resources([f['building']['uid']for f in forms])if not r.startswith('immutable-source-proof:')]+['immutable-source-proof:'+BATCH]);claim=reservations.claim('heritage-joint-stage-'+str(uuid.uuid4()),keys,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)))
 pulse=TimedOwnedLeasePulse(lambda:reservations.owns(lease),lambda:reservations.heartbeat(lease,ttl=3600))
 def fence():
  pulse(force=True)
  for q in refs:check(q);pulse()
 try:
  fence()
  with connect()as db:
   db.execute('SET TRANSACTION READ ONLY')
   for r in receipts:assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  DOC.mkdir();save(DOC/'qualified-existing-source-applicability.json',review)
  pub=original.prior.module(HERE.parent/'island-detail-integration/publish.py','heritage_joint_actual_publisher');patch=read(ROOT/candidate['path']);parent=read(ROOT/'3d-viewer/city/data/terrain.json');pub.validate_patch(patch,parent)
  manifest=read(ROOT/'3d-viewer/city/data/manifest.json');pub.check_patch_overlap(patch,parent.get('patches',[])+[read(ROOT/'3d-viewer'/e['url'])for e in manifest.get('terrainPatches',[])])
  save(DOC/'actual-publisher-terrain-validation.json',dict(passed=True,candidate=candidate,parent=ref(ROOT/'3d-viewer/city/data/terrain.json'),validator=ref(HERE.parent/'island-detail-integration/native_terrain_validation.py'),fullPatchCoverageOverlapAndParentEdgeChecks=True,geometryChanged=False))
  STAGE.mkdir();cat=read(original.prior.LOCAL/'catalogue.json');assert len(cat['models'])==1;entry=cat['models'][0];assert entry['uid']==UID and entry['sha256']==original.SOURCE
  entry.update(priority='landmark',proceduralWindows=False,sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,suppressesBuildingUids=[],supportDependencies=[],aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,sourceFunctionalApplicability=ref(DOC/'qualified-existing-source-applicability.json'),placementReview='Unchanged original at source pose/1x. Exact19 reviewed lower closures retain raw clearance failures; strict whole foundation passes. Complete four-world source and23 current BASIC checks, separate corrected terrain-estimated shelter, and6653 native exterior certificates retained. Original Star crossings remain source context without a collision exemption. Final staged/live browser review required.')
  dest=STAGE/entry['asset'];dest.parent.mkdir(parents=True);shutil.copyfile(original.prior.LOCAL/entry['asset'],dest);assert ref(dest)['sha256']==original.SOURCE and dest.stat().st_size==entry['bytes']
  cat.update(area='Hong Kong Heritage Museum unchanged government original',counts=dict(packedModels=1));save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));save(STAGE/'source-forms.json',[next(f['building']for f in forms if f['building']['uid']==UID)])
  out=STAGE/'government-native-heritage165054-original-v1-20261015.json';shutil.copyfile(ROOT/candidate['path'],out);assert ref(out)['sha256']==candidate['sha256']
  estimate=read(shelter.PROPOSAL);save(STAGE/'estimated-bases.json',dict(parentSha256=ref(ROOT/'3d-viewer/city/data/terrain.json')['sha256'],refinementSha256=candidate['sha256'],buildings=[{k:estimate[k]for k in ['uid','objectId','buildingCSUID','previousBase','base','height','baseSource']}],evidence=ref(shelter.DOC/'ROOT-VERIFIED.json')))
  terrain=dict(source=str(out.relative_to(ROOT)),sha256=candidate['sha256'],destination='city/data/'+out.name,resolution=patch['cell'],area=cat['area']+' source terrain')
  destination='city/data/official-models/'+BATCH+'/catalogue.json';save(STAGE/'plan.json',dict(areas=[dict(area=cat['area'],catalogue=str((STAGE/'catalogue.json').relative_to(ROOT)),destination=destination,estimates=[str((STAGE/'estimated-bases.json').relative_to(ROOT))])],topLevelTerrainPatches=[terrain]))
  save(STAGE/'browser-config.json',dict(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=destination,terrain=[terrain],fitBox=True,browserUids=[UID],failureTestUids=[UID],retainedBuildingUidsByModel={UID:[shelter.UID,'landsd/57455:0','landsd/104467:0']},nativeSupportUidsByModel={},estimatedBases=str((STAGE/'estimated-bases.json').relative_to(ROOT)),currentManifest=ref(ROOT/'3d-viewer/city/data/manifest.json')))
  pub.DOC=DOC/'publisher-dry-run';savedargv=sys.argv;sys.argv=[str(HERE.parent/'island-detail-integration/publish.py'),str((STAGE/'plan.json').relative_to(ROOT))]
  try:pub.main()
  finally:sys.argv=savedargv
  report=read(pub.DOC/'publication-plan.json');assert not report['published']and report['estimatedBases']==[dict(uid=shelter.UID,before=estimate['previousBase'],after=estimate['base'])]
  save(DOC/'stage.json',dict(batch=BATCH,uid=UID,scriptChecksPassed=True,publisherDryRunPassed=True,plan=ref(STAGE/'plan.json'),browserConfig=ref(STAGE/'browser-config.json'),privateCatalogueFlagsOnly=True,publication=False,newlyInstalled=0,stagedLiveBrowserAndActualROOTImageReviewRequired=True))
  refs=distinct_refs(refs+[ref(p)for folder in [DOC,STAGE]for p in folder.rglob('*')if p.is_file()]);fence()
  original.prior.module(original.prior.old.FREEZER,'heritage_joint_stage_freezer').freeze(BATCH,'exact19-source-applicability-joint-terrain-estimate-private-stage-no-install',[check(q)for q in refs],dict(uids=[UID],sourceOnly=True,publisherDryRunPassed=True,physicalAccepted=False,newlyInstalled=0))
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
