"""ROOT-only one immutable government source private stage, no terrain/live writes."""
from pathlib import Path
import sys,json,copy,subprocess,uuid,shutil
import aqua_marine193086138449_saved_four_world_guards_v2_20261014 as finite
from aqua_original_private_stage_guard_v1_20261014 import qualify
from run import ROOT,HERE,read,save,connect,reservations
from dependency_preflight import from_catalogues
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from timed_owned_lease_pulse_v1_20261014 import TimedOwnedLeasePulse
A=finite.A;ref,check,module=finite.ref,finite.check,finite.module
BATCH='government-xl-aqua-marine193086-original-private-stage-v1-20261014';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');STAGE=HERE/'accepted'/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';BROWSER=HERE/'aqua_marine193086_solid_original_browser_v1_20261014.mjs';PUB=HERE.parent/'model-integration-20260909/publish.py';FINITE_JOB='8a1002ae824c7ad13f222411e8e70d7f2f7b41237db694ed6fe2539e5f684316';CAPTURE_JOB='0c983d82182d3b6d301d173737d8ef26a1e8b1e34b3c56bb80e989f49449b81e'
def load():
    data,capture_result,p,disposition,refs=finite.load(CAPTURE_JOB);r=read(finite.DOC/'result.json');v=read(finite.DOC/'ROOT-VERIFIED.json');assert r['jobId']==v['jobId']==FINITE_JOB and v['exactNeonReadback']and v['allEvidenceHashesVerified']and v['leaseReleased'];full=read(finite.DOC/'complete-four-world-guard-result.json');diag=read(A.prior.DOC/'diagnostic.json.gz');adapted=qualify(diag,full,p,data[3],disposition,A.prior.UID,A.prior.FOREIGN)
    for c in full['foreignCollisionRows']:
        proof=read(check(c['exactContacts']));assert proof['allContactsVerbatim']['allPairsExamined']and proof['allContactsVerbatim']['sourceFacesOmitted']==0 and proof['allContactsVerbatim']['contacts']==[]and proof['foreignCollisionExemption']is False
        assert proof['wholeOwnedWorldSHA256']==next(x['completeSourceWorldSHA256']for x in full['rows']if x['uid']==A.prior.UID and x['arithmetic']==c['arithmetic'])
    assert read(A.prior.DOC/'terrain-candidates.json')==[];refs=distinct_refs(refs+r['evidenceRefs']+[ref(finite.DOC/'result.json'),ref(finite.DOC/'ROOT-VERIFIED.json'),ref(Path(__file__)),ref(BROWSER),ref(PUB)])
    for q in refs:check(q)
    return data,r,p,adapted,refs

def schema_only():
    data,r,p,a,refs=load();return dict(passed=True,caller=ref(Path(__file__)),FINITE_JOB=FINITE_JOB,CAPTURE_JOB=CAPTURE_JOB,uids=[A.prior.UID],scope=data[-1],privateOnly=True,rawStrictFoundationPassed=False,nativePatchBytesUnchanged=data[10],terrainPlan=[],currentManifestSHA256=A.prior.CURRENT,currentSnapshot=A.prior.SNAPSHOT,noAssetCopyStageBrowserDBLeaseWorker=True)

def owned():
    lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists()and not STAGE.exists();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__));data,r,p,adapted,refs=load();refs=distinct_refs(refs+prep['codeRefs']+prep['inputRefs']+prep['evidenceRefs']+[ref(PROPOSAL/'actual-readonly-preparation.json')]);pulse=TimedOwnedLeasePulse(lambda:reservations.owns(lease),lambda:reservations.heartbeat(lease,ttl=3600))
    def fence():
        pulse(force=True)
        for q in refs:check(q);pulse()
        assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==A.prior.CURRENT;pulse(force=True)
    fence()
    with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(FINITE_JOB,)).fetchone()==('complete',r)
    row=data[0];DOC.mkdir();STAGE.mkdir();save(DOC/'exact-existing-source-warning-applicability.json',adapted);entry=copy.deepcopy(row['candidate']['entry']);assert entry['uid']==A.prior.UID and entry['sha256']==A.prior.SOURCE_SHA
    entry.update(priority='landmark',proceduralWindows=False,sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,suppressesBuildingUids=[],supportDependencies=[],aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,sourceFunctionalApplicability=dict(decision=ref(finite.REVIEW),existingReason=adapted['resolvedExistingReasonByExactSourceReview'],exactFaces=adapted['reviewedFaceIDs'],rawStrictFoundationPassed=False),placementReview='Unchanged original government source, fixed source pose/1x. Exact saved positive overhead identity; complete four-world projection coverage and zero independent foreign source contacts. ROOT reviewed only three authored lower facade closure faces for the existing burial warning. Raw strict false, all278 partials and whole gap remain. No structural/root/watertight or foreign collision/support exemption; staged/live mobile, source images, picking/collision/retry remain required.')
    dest=STAGE/entry['asset'];dest.parent.mkdir(parents=True);shutil.copyfile(ROOT/row['candidate']['path'],dest);assert ref(dest)['sha256']==row['sourceSHA256']and dest.stat().st_size==entry['bytes'];cat=read(A.prior.LOCAL/'catalogue.json');cat.update(area='Aqua Marine unchanged original government source',models=[entry],counts=dict(packedModels=1));save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));save(STAGE/'source-forms.json',[row['source']['building']])
    destination='city/data/official-models/'+BATCH+'/catalogue.json';save(STAGE/'plan.json',dict(areas=[dict(area=cat['area'],catalogue=str((STAGE/'catalogue.json').relative_to(ROOT)),destination=destination)],topLevelTerrainPatches=[]));deps=from_catalogues(ROOT/'3d-viewer/city/data/manifest.json',[STAGE/'catalogue.json']);assert not any(x['blockers']for x in deps['rows']);save(DOC/'dependencies.json',deps);refs=distinct_refs(refs+[dict(path=k,sha256=h)for k,h in deps['inputHashes'].items()])
    save(STAGE/'browser-config.json',dict(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=destination,terrain=[],fitBox=True,browserUids=[A.prior.UID],failureTestUids=[A.prior.UID],retainedBuildingUidsByModel={A.prior.UID:[A.prior.FOREIGN]},nativeSupportUidsByModel={},currentManifest=ref(ROOT/'3d-viewer/city/data/manifest.json'),servedApp=ref(ROOT/'3d-viewer/city/app.js'),retainedNativePatchRefs=[dict(url=x['url'],sha256=x['source']['sha256'])for x in data[10]]))
    save(DOC/'stage.json',dict(batch=BATCH,uids=[A.prior.UID],sourceSHA256=A.prior.SOURCE_SHA,CSUID=entry['buildingCSUID'],scriptChecksPassed=True,remainingActualExistingViewerReasons=[],sourceWarningApplicability=ref(DOC/'exact-existing-source-warning-applicability.json'),ROOTFunctionalReview=ref(finite.REVIEW),positiveIdentityVerbatim=ref(A.prior.IDENTITY/'identity.json'),completeCurrentFourWorldProof=ref(finite.DOC/'result.json'),rawOrdinaryVerbatim=ref(A.prior.DOC/'result.json'),plan=ref(STAGE/'plan.json'),browserConfig=ref(STAGE/'browser-config.json'),retainedNativePatches=data[10],terrainGeometryChanges=0,rawStrictFoundationPassed=False,all278PartialsAndWholeGapRetained=True,privateCatalogueFlagsOnly=True,publication=False,sourceGeometryChanges=0,newlyInstalled=0,stagedLiveBrowserAndActualROOTImageReviewRequired=True))
    refs=distinct_refs(refs+[ref(q)for folder in [DOC,STAGE]for q in folder.rglob('*')if q.is_file()]);fence();module(A.prior.FREEZER,'aqua_private_stage_freezer').freeze(BATCH,'one-original-private-stage-exact-existing-warning-source-applicability-no-terrain-or-install',[check(q)for q in refs],dict(uids=[A.prior.UID],sourceOnly=True,sourceGeometryChanges=0,terrainGeometryChanges=0,newlyInstalled=0,publication=False))
def main():
    if '--schema-only'in sys.argv:print(json.dumps(schema_only()));return
    if '--owned'in sys.argv:return owned()
    assert '--prepare-private-original-stage-only'in sys.argv and not DOC.exists()and not STAGE.exists()and not LOCAL.exists();data,*_=load();scope=data[-1];prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__));resources=['building:'+u for u in scope]+['terrain-patch:'+u for u in scope]+['immutable-source-proof:'+BATCH];claim=reservations.claim('aqua-private-stage-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
    try:save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
