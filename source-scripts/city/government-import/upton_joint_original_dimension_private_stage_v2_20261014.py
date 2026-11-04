"""ROOT-only fresh private stage, correcting stale descriptive W=29 to43.
No source geometry/renderer/grid/sampler/numerical acceptance changes.
"""
from pathlib import Path
import copy,json,shutil,sys,subprocess,uuid
from run import ROOT,HERE,read,save,connect,reservations
import upton_joint_original_functional_private_stage_v1_20261014 as old
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from upton_georef_dimensions_metadata_v1_20261014 import correct,assert_equivalent,OLD_TERRAIN,encoded
import hashlib
ref,check=old.ref,old.check;physical=old.physical;OWNED=old.OWNED
BATCH='government-xl-upton-joint-original-dimension-private-stage-v2-20261014';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;STAGE=HERE/'accepted'/BATCH;LEASE=LOCAL/'reservation.json';BROWSER=HERE/'upton_dimension_joint_resolution_browser_v2_20261014.mjs'
STAGE_JOB='477a562360f6ad1b22de54000f7e7a1e9b3b9c7a52325fb97abfdadc653085f3'
CONSUMERS=['3d-viewer/city/world.js','3d-viewer/city/geo.js','3d-viewer/city/terrain-patch-index.js']
def load():
    p,a,rows,c,patch=old.load();r=read(old.DOC/'result.json');v=read(old.DOC/'ROOT-VERIFIED.json');assert r['jobId']==v['jobId']==STAGE_JOB and v['exactNeonReadback']and v['allEvidenceHashesVerified']and v['leaseReleased']
    terrain=read(old.STAGE/'plan.json')['topLevelTerrainPatches'][0];assert terrain['sha256']==OLD_TERRAIN and ref(ROOT/terrain['source'])['sha256']==OLD_TERRAIN
    previous=read(ROOT/terrain['source']);approval=previous['nativeMesh']['sourceOverlap'];auditpath=ROOT/approval['evidencePath'];assert ref(auditpath)['sha256']==approval['evidenceSHA256']
    return p,a,rows,c,previous,read(auditpath),r,terrain,auditpath

def load_completed():
    p,a,rows,c,previous,audit,result,terrain,auditpath=load()
    r=read(DOC/'result.json');v=read(DOC/'ROOT-VERIFIED.json');assert r['jobId']==v['jobId']and v['exactNeonReadback']and v['allEvidenceHashesVerified']and v['leaseReleased']
    final=read(STAGE/'plan.json')['topLevelTerrainPatches'][0];patch=read(ROOT/final['source']);assert ref(ROOT/final['source'])['sha256']==final['sha256'];assert_equivalent(previous,patch)
    proof=read(check(final['dimensionMetadataEquivalence']));assert proof['previousQualifiedTerrain']==ref(ROOT/terrain['source'])and proof['completeActualGroundSHA256']==old.functional.review.GROUND and proof['completeActualDrawnGroundFaces']==11645
    approval=patch['nativeMesh']['sourceOverlap'];fresh=read(check(dict(path=approval['evidencePath'],sha256=approval['evidenceSHA256'])));assert fresh['stagedGeometrySha256']==proof['newBareCanonicalSHA256']==hashlib.sha256(encoded(__import__('upton_georef_dimensions_metadata_v1_20261014').bare(patch))).hexdigest()
    return p,a,rows,c,patch

def schema_only():
    *_,patch,audit,result,terrain,auditpath=load()
    # Read-only metadata preparation: no geometry/packing/sampler calculation.
    assert (patch['w'],patch['h'],patch['meta']['georef']['W'],patch['meta']['georef']['H'])==(43,29,29,29)
    corrected,proof=correct(patch,audit);publisher=physical.module(HERE.parent/'island-detail-integration/publish.py','upton_dimension_actual_publisher_grid_preflight');old_failure=None
    try:publisher.validate_grid(patch)
    except AssertionError as error:old_failure=str(error)
    assert old_failure=='Terrain georef dimensions mismatch';publisher.validate_grid(corrected);assert_equivalent(patch,corrected)
    return dict(passed=True,actualPublisherValidateGridPassed=True,previousPublisherFailure=old_failure,newBareCanonicalSHA256=proof['newBareCanonicalSHA256'],unchangedPublisher=ref(HERE.parent/'island-detail-integration/publish.py'),caller=ref(Path(__file__)),oldTerrain=ref(ROOT/terrain['source']),oldAudit=ref(auditpath),oldWidth=29,actualWidth=43,height=29,gridEntries=1247,sourceStageJob=STAGE_JOB,noGeometryTransformNumericalDBLeaseWorker=True)

def owned():
    lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists()and not STAGE.exists()
    prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
    p,a,rows,c,previous,audit,result,terrain,auditpath=load();refs=distinct_refs(prep['codeRefs']+prep['inputRefs']+prep['evidenceRefs']+[ref(PROPOSAL/'actual-readonly-preparation.json')])
    def fence():
        for q in refs:check(q)
        assert reservations.owns(lease)and ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==physical.CURRENT
    fence()
    with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(STAGE_JOB,)).fetchone()==('complete',result)
    DOC.mkdir();STAGE.mkdir();corrected,proof=correct(previous,audit);assert prep['schemaVerbatim']['actualPublisherValidateGridPassed']and prep['schemaVerbatim']['newBareCanonicalSHA256']==proof['newBareCanonicalSHA256']
    failed=BASE/'government-xl-upton-joint-original-functional-staged-browser-v1-20261014';save(DOC/'preserved-failed-publisher-source-context.json',dict(failedCommand=ref(failed/'command-000.json'),ROOTTerminal=ref(failed/'ROOT-TERMINAL.json'),failure='Terrain georef dimensions mismatch',browserNotExecuted=True,noPublication=True,noSourceModelCorruptionClaim=True,previousFunctionalReview=p['acceptedROOTReview']))
    proof.update(previousQualifiedTerrain=ref(ROOT/terrain['source']),previousOverlapAudit=ref(auditpath),completeActualGroundSHA256=old.functional.review.GROUND,completeActualDrawnGroundFaces=11645,sourceFunctionalReview=p['acceptedROOTReview'],sourceStage=ref(old.DOC/'result.json'),runtimeConsumerRefs=[ref(ROOT/f)for f in CONSUMERS],proofScope='Descriptive W corrected only; all renderer/sampler inputs and all existing full-source/numerical proof tuples identical.',strictInterfacePassed=False,publication=False,newlyInstalled=0)
    save(DOC/'dimension-metadata-equivalence.json',proof);proof_ref=ref(DOC/'dimension-metadata-equivalence.json')
    fresh=copy.deepcopy(audit);fresh['stagedGeometrySha256']=proof['newBareCanonicalSHA256'];fresh['dimensionMetadataEquivalence']=proof_ref;fresh['historicalOverlapAudit']=ref(auditpath);fresh['source']['files']=distinct_refs(fresh['source']['files']+[proof_ref,ref(auditpath),ref(ROOT/terrain['source'])]+proof['runtimeConsumerRefs'])
    newaudit=DOC/'geometry-bound-dimension-corrected-overlap-audit.json';save(newaudit,fresh)
    corrected['nativeMesh']['sourceOverlap'].update(evidencePath=str(newaudit.relative_to(ROOT)),evidenceSHA256=ref(newaudit)['sha256']);assert_equivalent(previous,corrected)
    out=STAGE/'government-native-upton-certified6170-joint-original-dimension-v2-20261014.json';save(out,corrected);newsha=ref(out)['sha256']
    for f in ['catalogue.json','catalogue-index.json','source-forms.json']:
        shutil.copyfile(old.STAGE/f,STAGE/f);assert ref(STAGE/f)['sha256']==ref(old.STAGE/f)['sha256']
    for row in rows:
        asset=row['candidate']['entry']['asset'];(STAGE/asset).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(old.STAGE/asset,STAGE/asset);assert ref(STAGE/asset)['sha256']==row['sourceSHA256']
    review=read(old.DOC/'native-replacement-review.json');review.update(replacementSHA256=newsha,dimensionMetadataEquivalence=proof_ref,previousTerrainSHA256=OLD_TERRAIN);save(DOC/'native-replacement-review.json',review)
    plan=read(old.STAGE/'plan.json');plan['areas'][0]['catalogue']=str((STAGE/'catalogue.json').relative_to(ROOT));plan['areas'][0]['destination']='city/data/official-models/'+BATCH+'/catalogue.json';t=plan['topLevelTerrainPatches'][0];t.update(source=str(out.relative_to(ROOT)),sha256=newsha,destination='city/data/'+out.name,nativeReview=ref(DOC/'native-replacement-review.json'),dimensionMetadataEquivalence=proof_ref);save(STAGE/'plan.json',plan)
    config=read(old.STAGE/'browser-config.json');config.update(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=plan['areas'][0]['destination'],terrain=[t],dimensionMetadataCorrection=dict(proof=proof_ref,oldTerrainSHA256=OLD_TERRAIN,newTerrainSHA256=newsha));save(STAGE/'browser-config.json',config)
    save(DOC/'stage.json',dict(batch=BATCH,uids=OWNED,sourceApplicabilityVerbatim=a,strictInterfacePassed=False,previousStage=ref(old.DOC/'result.json'),dimensionMetadataEquivalence=proof_ref,newTerrain=ref(out),plan=ref(STAGE/'plan.json'),browserConfig=ref(STAGE/'browser-config.json'),completeActualGroundSHA256=proof['completeActualGroundSHA256'],completeActualDrawnGroundFaces=11645,newlyInstalled=0,publication=False,realPublisherDryRunAndStagedLiveStillRequired=True))
    refs=distinct_refs(refs+[ref(f)for folder in [DOC,STAGE]for f in folder.rglob('*')if f.is_file()]);fence();physical.module(physical.FREEZER,'upton_dimension_stage_freezer').freeze(BATCH,'exact-descriptive-width-metadata-rebind-private-stage-no-install',[check(q)for q in refs],dict(uids=OWNED,currentManifestSHA256=physical.CURRENT,sourceOnly=True,newlyInstalled=0,publication=False))

def main():
    if '--schema-only'in sys.argv:print(json.dumps(schema_only()));return
    if '--owned'in sys.argv:return owned()
    assert '--prepare-dimension-corrected-private-stage-only'in sys.argv and not DOC.exists()and not STAGE.exists()and not LOCAL.exists();load();assert read(PROPOSAL/'actual-readonly-preparation.json')['passed'];uids=old.functional.review.scope_uids();resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH];claim=reservations.claim('upton-dimension-stage-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
    try:save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
