"""ROOT-only accepted exact applicability adapter/private stage, never live writes."""
from pathlib import Path
import copy,json,sys,time,uuid,subprocess,shutil
from run import ROOT,HERE,read,save,connect,reservations
import upton_joint_original_wall_band_functional_packet_v1_20261014 as functional
import upton_joint_original_private_source_review_v2_20261014 as display
from upton_original_functional_applicability_adapter_v1_20261014 import apply,OWNED,POLICY
from dependency_preflight import from_catalogues
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
physical=functional.physical;ref,check=physical.ref,physical.check
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-upton-joint-original-functional-private-stage-v1-20261014';DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');STAGE=HERE/'accepted'/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';BROWSER=HERE/'upton_functional_joint_resolution_browser_v1_20261014.mjs'
FUNCTIONAL_JOB='6f9fcb979b6f4c1773c2066d3b540af2c736e60113e8f5d000fcf569f39e7715'

def reviewed_inputs():
    packet=read(functional.DOC/'proposed-functional-wall-band-disposition.json');images=read(display.DOC/'actual-private-source-preview.json')
    assert len(images['views'])==6 and not images['errors']and images['actualGround']['sha256']==functional.review.GROUND and images['actualGround']['faces']==11645
    for v in images['views']:assert v['selectionClosed'];assert v['id']not in ['assembly','foot-plan']or v['indexedSourceFraming']
    refs=[ref(ROOT/path)for v in images['views']for path in [v['image'],v['cleanSolidImage']]]
    return packet,ref(functional.DOC/'exact36-four-world-source-face-descriptors.json.gz'),ref(display.DOC/'actual-private-source-preview.json'),refs,ref(functional.DOC/'proposed-functional-wall-band-disposition.json')

def load():
    pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
    for q in pins['codeRefs']+pins['inputRefs']:check(q)
    for folder,expected in [(functional.DOC,FUNCTIONAL_JOB),(display.DOC,pins['completedDisplayV2Job']),(physical.DOC,'0f54a6b738ee33b15ad94ecaa71848dbcf981f2a204e2e86c6a0628e1f6aa572')]:
        r=read(folder/'result.json');v=read(folder/'ROOT-VERIFIED.json');assert r['jobId']==v['jobId']==expected and v['exactNeonReadback']and v['allEvidenceHashesVerified']and v['leaseReleased']
    review=read(check(pins['acceptedROOTReview']));packet,descriptors,images,image_refs,packet_ref=reviewed_inputs()
    raw=read(physical.DOC/'current-physical-raw-gates.json');strict=read(physical.DOC/'support-checks.json.gz')['rows'][0]['interface']
    adapted=apply(decision=review,packet=packet,descriptor_ref=descriptors,display_ref=images,image_refs=image_refs,packet_ref=packet_ref,raw_reasons=raw['rawReasons'],strict=strict)
    assert packet['scope']['currentManifestSHA256']==physical.CURRENT and packet['scope']['completeActualGroundSHA256']==functional.review.GROUND and packet['scope']['completeActualDrawnGroundFaces']==11645 and packet['scope']['terrainSHA256']==functional.review.TERRAIN
    rows=read(physical.DOC/'selection.json.gz')['rows'];assert [r['uid']for r in rows]==OWNED
    for r in rows:assert ref(ROOT/r['candidate']['path'])['sha256']==r['sourceSHA256']==r['candidate']['entry']['sha256']
    foundations=read(physical.DOC/'foundation.json');assert all(r['strictFoundationAccepted']for r in foundations['rows'])
    decisions=read(physical.DOC/'support-ground-resolution.json')['rows'];podium=next(r for r in decisions if r['uid']==OWNED[0]);assert not podium['remainingPolicyReasons']and not podium['remainingDiagnosticReasons']
    native=read(physical.DOC/'native-neighbour-checks.json');assert not set(native['blocked'])-set(native['resolved'])
    neighbours=read(physical.DOC/'neighbour-checks.json');assert not any(r['reasons']for r in neighbours['rows']if r['uid']not in set(native['resolved']))
    validate=read(physical.DOC/'validation.json');assert validate['checksPassed']==validate['loaderAccepted']==2 and validate['exceptions']==0
    candidates=read(physical.DOC/'terrain-candidates.json');assert len(candidates)==1;c=candidates[0];assert c['sha256']==functional.review.TERRAIN and ref(ROOT/c['path'])['sha256']==c['sha256']
    old=c['replaces'];assert old['retainedUids']==[physical.RETAINED]and ref(ROOT/'3d-viewer'/old['url'])['sha256']==old['sha256']
    retained=next(r for r in native['rows']if r['uid']==physical.RETAINED);assert retained['passed']and retained['terrain']['newlyWhollyBuried']==retained['terrain']['newlyUpwardWhollyBuried']==0
    assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==physical.CURRENT
    return pins,adapted,rows,c,read(ROOT/c['path'])

def schema_only():
    p,a,r,c,t=load();return dict(passed=True,caller=ref(Path(__file__)),acceptedROOTReview=p['acceptedROOTReview'],strictInterfacePassed=False,sourceScopedApplicabilityAccepted=True,noGeometryStageCopyBrowserDBLeaseOrWorker=True)

def owned():
    lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists()and not STAGE.exists();last=time.monotonic()
    def pulse(force=False):
        nonlocal last
        if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
    pins,adapted,rows,c,patch=load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
    refs=distinct_refs(pins['codeRefs']+pins['inputRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'METHOD.md'),ref(PROPOSAL/'actual-readonly-preparation.json')]+prep['evidenceRefs'])
    def fence():
        for q in distinct_refs(refs):check(q);pulse()
        assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==physical.CURRENT;pulse(True)
    for folder in [functional.DOC,display.DOC,physical.DOC]:
        result=read(folder/'result.json')
        with connect()as con:con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
    fence();DOC.mkdir(parents=True);STAGE.mkdir(parents=True);save(DOC/'source-scoped-physical-applicability.json',adapted)
    models=[]
    for row in rows:
        entry=copy.deepcopy(row['candidate']['entry']);entry.update(priority='landmark',proceduralWindows=False,sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,suppressesBuildingUids=[],aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,placementReview='Exact unchanged Upton originals; full current source/ordinary clearance/compound foundations/neighbours/runtime pass. ROOT accepted narrowly source-bound authored lower facade-band applicability; raw strict97/138+41 remains failed. No geometry, pose, numeric threshold or foreign-support exemption.')
        entry['supportDependencies']=[]if row['uid']==OWNED[0]else[dict(uid=OWNED[0],state='candidate',csuid=rows[0]['candidate']['entry']['buildingCSUID'],sha256=rows[0]['sourceSHA256'])]
        dest=STAGE/entry['asset'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/row['candidate']['path'],dest);assert ref(dest)['sha256']==row['sourceSHA256'];models.append(entry)
    catalogue=read(physical.LOCAL/'catalogue.json');catalogue.update(models=models,counts=dict(packedModels=2),area='Upton two unchanged original government sources');save(STAGE/'catalogue.json',catalogue);save(STAGE/'catalogue-index.json',dict(models=2,catalogues=['catalogue.json']));save(STAGE/'source-forms.json',[r['source']['building']for r in rows])
    copied=STAGE/'government-native-upton-certified6170-joint-original-v1-20261014.json';shutil.copyfile(ROOT/c['path'],copied);assert ref(copied)['sha256']==c['sha256']
    replacement=dict(status='approved-for-integration',supersededURL=c['replaces']['url'],supersededSHA256=c['replaces']['sha256'],replacementSHA256=c['sha256'],sourceGeometryChanged=False,aiCalls=0,modelGeometryChanges=0,retainedUids=c['replaces']['retainedUids'],replacementTargetUids=patch['meta']['targetUids'],fullMeshCheck=ref(physical.DOC/'native-neighbour-checks.json'),sourceFunctionalReview=pins['acceptedROOTReview'],terrainNumericAndSourceProvenanceBytesExactlyUnchanged=True);save(DOC/'native-replacement-review.json',replacement)
    terrain=dict(source=str(copied.relative_to(ROOT)),sha256=c['sha256'],destination='city/data/'+copied.name,resolution=patch['cell'],area=catalogue['area']+' qualified computed terrain',replaces=c['replaces'],nativeReview=ref(DOC/'native-replacement-review.json'))
    destination='city/data/official-models/'+BATCH+'/catalogue.json';save(STAGE/'plan.json',dict(areas=[dict(area=catalogue['area'],catalogue=str((STAGE/'catalogue.json').relative_to(ROOT)),destination=destination)],topLevelTerrainPatches=[terrain]))
    deps=from_catalogues(ROOT/'3d-viewer/city/data/manifest.json',[STAGE/'catalogue.json']);assert not any(r['blockers']for r in deps['rows']);save(DOC/'dependencies.json',deps);refs +=[dict(path=p,sha256=h)for p,h in deps['inputHashes'].items()]
    bounds=[[min(m['worldBounds'][0][i]for m in models)for i in range(3)],[max(m['worldBounds'][1][i]for m in models)for i in range(3)]]
    save(STAGE/'browser-config.json',dict(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=destination,terrain=[terrain],fitBox=True,captureBoundsByModel={u:bounds for u in OWNED},browserUids=OWNED,failureTestUids=OWNED,nativeSupportUidsByModel={OWNED[0]:[physical.RETAINED],OWNED[1]:[OWNED[0],physical.RETAINED]},retainedBuildingUidsByModel={u:[physical.SECONDARY]for u in OWNED},retained79882VisibilityGuardIsNotNewPhysicalSupportClaim=True))
    save(DOC/'stage.json',dict(batch=BATCH,uids=OWNED,sourceSHA256s={r['uid']:r['sourceSHA256']for r in rows},scriptChecksPassed=True,checksPassed=True,physicalApplicability=ref(DOC/'source-scoped-physical-applicability.json'),rawPhysicalVerbatim=ref(physical.DOC/'result.json'),ROOTFunctionalReview=pins['acceptedROOTReview'],plan=ref(STAGE/'plan.json'),browserConfig=ref(STAGE/'browser-config.json'),strictInterfacePassed=False,privateCatalogueFlagsOnly=True,publication=False,modelGeometryChanges=0,scriptExternalAICalls=0,newlyInstalled=0,stagedLiveBrowserStillRequired=True))
    refs +=[ref(p)for folder in [DOC,STAGE]for p in folder.rglob('*')if p.is_file()];fence();physical.module(physical.FREEZER,'upton_joint_functional_stage_freezer').freeze(BATCH,'ROOT-accepted-exact-original-facade-applicability-private-stage-no-install',[check(q)for q in distinct_refs(refs)],dict(uids=OWNED,currentManifestSHA256=physical.CURRENT,sourceOnly=True,sourceGeometryChanges=0,newlyInstalled=0,publication=False))

def main():
    if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
    if '--owned'in sys.argv:return owned()
    assert '--prepare-private-joint-original-stage-only'in sys.argv and not DOC.exists()and not STAGE.exists()and not LOCAL.exists();load();uids=functional.review.scope_uids();resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH];claim=reservations.claim('upton-joint-stage-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
    try:save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
