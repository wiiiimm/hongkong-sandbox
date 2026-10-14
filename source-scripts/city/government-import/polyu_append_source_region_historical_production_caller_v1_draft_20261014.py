"""UNEXECUTED compact historical-scene actual production viability only."""
from pathlib import Path
import json,sys,uuid,time,subprocess,shutil
import numpy as np
from run import ROOT,HERE,read,save,connect,reservations
import polyu_parent_cell_actual_production_capture_v4_draft_20261014 as capture
import polyu_append_historical_capture_binding_v1_draft_20261014 as binding
from polyu_compact_runtime_mesh_projection_v1_draft_20261014 import mesh_binding,project,verify
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-polyu-append-source-region-historical-production-v1-20261014'
DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
NOM=BASE/'government-xl-polyu-append-source-region-residual-repair-v1-20261014';JOB='22f69c119f28eb85478f89feb6f1b6d8f1fd5ba2d90148052d11ca55dc09dd2e'
CAPTURE_JOB='59491c7701e48dca8e907808ea8e0b487feaa5f6d8a8b6fbb57ca57fc733c6b2'
UPTON=BASE/'government-xl-upton-joint-original-functional-installed-v2-20261014'
UPTON_JOB='f099afe8572e53c2fe16f5a185b475cf21ba8541f6f1bbb2cf148d0ad214d3a0'
RUNTIME=HERE/'polyu_append_source_region_historical_production_runtime_v1_draft_20261014.mjs'
ref,check=capture.ref,capture.check

def load():
    pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))and pins['runtime']==ref(RUNTIME)
    for q in distinct_refs(pins['codeRefs']+pins['inputRefs']):check(q)
    receipt=read(NOM/'result.json');cert=read(NOM/'ROOT-VERIFIED.json')
    assert receipt['jobId']==cert['jobId']==JOB and cert['exactNeonReadback']and cert['allEvidenceHashesVerified']and cert['leaseReleased']
    old_receipt=read(capture.DOC/'result.json');old_cert=read(capture.DOC/'ROOT-VERIFIED.json')
    assert old_receipt['jobId']==old_cert['jobId']==CAPTURE_JOB
    assert old_cert['exactNeonReadback']and old_cert['allEvidenceHashesVerified']and old_cert['leaseReleased']
    upton_cert=read(UPTON/'ROOT-VERIFIED.json');assert upton_cert['jobId']==UPTON_JOB and upton_cert['exactNeonReadback']and upton_cert['allEvidenceHashesVerified']and upton_cert['leaseReleased']
    archive=binding.historical_manifest(read(UPTON/'historical-input-context.json'));check(archive)
    old_input=read(capture.DOC/'input.json.gz');old_patch=read(capture.DOC/'private-native-terrain-candidate.json.gz')
    assert old_input['currentManifestSHA256']==binding.HISTORICAL
    nom=read(NOM/'private-append-only-source-region-nomination.json.gz');assert nom['previousFullNomination']==old_input['newNomination'];check(nom['previousFullNomination'])
    old_mesh={k:old_patch['nativeMesh'][k]for k in ['position','index']};raw=binding.validate_append(nom,old_mesh,old_input['completeMeshBinding'],pins['completeMeshBinding'])
    assert len(raw)==148459 and len(nom['appendAccount']['appendedFaces'])==1363 and len(nom['appendAccount']['exactExistingRepresentations'])==30 and len(nom['sourceRegionAccounts'])==336
    assert nom['newCompleteMeshBinding']['completePositionVertices']==587502
    domain=binding.grid_domain(old_patch);assert domain==old_input['fullParentDomain']==nom['fullParentDomain']==[2002.5,-2067.5,2212.5,-1927.5]
    assert old_patch['w']*old_patch['h']==1247 and old_patch['coarseCells']==[521,420,524,422]and not old_patch['nativeMesh'].get('sourceOverlap')
    assert not nom['physicalAccepted']and not nom['currentAcceptance']and nom['unchanged8011LiteralAndSourceOutsideFacets']and nom['unchanged1485First832Prefix']and nom['completeOldMappingCount']==3214
    actors=read(capture.PREVIOUS_CAPTURE/'complete-fresh-current-native59527-and24-BASIC.json.gz');original=read(capture.PREVIOUS_CAPTURE/'native59527-unchanged-provider-original-world.json.gz')
    assert actors['startEndAllInputsVerified']and actors['currentManifestSHA256']==binding.HISTORICAL and len(actors['basicRows'])==24 and actors['nativeRow']['completeFaces']==59527
    source_refs=distinct_refs([binding.resolve_source_ref(dict(path=p,sha256=h),archive,ROOT)for p,h in actors['inputHashes'].items()])
    assert original['completeFaces']==59527 and original['originalWorldSHA256']=='4f527cba16bd9e54f70c773fdcf7febec3e7c3d6d005bfed5b1f62df8fc315b8'
    assert capture.nomination.feasibility.sha(original['completeWorldTriangles'])==original['originalWorldSHA256']
    guards=old_input['previousOriginalGuardRows'];proof=old_input['complete25SourceEvidence']
    assert [q['uid']for q in guards]==[q['uid']for q in proof['rows']]==capture.prior.UIDS
    nine=[q for q in guards if q['reasons']==['increased-neighbour-ground-gap']];assert len(nine)==9 and sum(q['checks']for q in nine)==3366
    resources=sorted(['building:'+u for u in capture.prior.UIDS]+['terrain-patch:'+u for u in capture.prior.UIDS]+['immutable-source-proof:'+BATCH]);assert len(resources)==51
    return pins,receipt,nom,old_input,old_patch,archive,source_refs,resources

def schema_only():
    pins,_,nom,old_input,patch,archive,source_refs,resources=load()
    return dict(passed=True,caller=ref(Path(__file__)),runtime=ref(RUNTIME),completeMeshBinding=nom['newCompleteMeshBinding'],newFacets=148459,newPositions=587502,
        preservedPriorFacets=147096,preservedPositionSlotsIncludingUnused=583413,appendedFaces=1363,exactExistingRepresentations=30,completeSourceRegions=336,
        fullParentDomain=old_input['fullParentDomain'],grid=dict(width=patch['w'],height=patch['h'],nodes=1247),historicalSceneManifestReference=archive,resolvedSourceInputRefs=source_refs,
        canonicalResources=resources,noSourceDecodePackingFiniteCaptureDBLeaseOrCurrentAcceptance=True)

def owned():
    lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
    def pulse():
        nonlocal last
        if time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
    pins,receipt,nom,old_input,old_patch,archive,source_refs,resources=load();assert lease['resources']==resources
    prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))and prep['runtime']==ref(RUNTIME)
    validation=read(check(prep['bindingValidationRef']));assert validation['passedTests']==6 and validation['failedTests']==0 and validation['exitCode']==0
    assert validation['executedCodeRefs']==[ref(Path(binding.__file__)),ref(HERE/'test_polyu_append_historical_capture_binding_v1_draft_20261014.py')]
    refs=distinct_refs(pins['codeRefs']+pins['inputRefs']+source_refs+prep['evidenceRefs']+validation['evidenceRefs']+[prep['bindingValidationRef'],ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'actual-readonly-preparation.json')])
    for folder,jid in [(NOM,JOB),(capture.DOC,CAPTURE_JOB),(UPTON,UPTON_JOB)]:
        with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',read(folder/'result.json'))
    def fence():
        for q in distinct_refs(refs):check(q);pulse()
        assert reservations.owns(lease)
    fence();DOC.mkdir();nomref=ref(NOM/'private-append-only-source-region-nomination.json.gz')
    preservation=dict(unchangedPriorFacets=147096,unchangedOldMappings=3214,unchangedPrefixFacets=1485,retainedPriorPositionVertices=583413)
    projection=project(nom['newNativeMesh'],nomref,nom['newCompleteMeshBinding'],preservation);verify(projection,nomref,nom['newCompleteMeshBinding'],preservation)
    save(DOC/'compact-runtime-mesh-projection.json.gz',projection);projection_ref=ref(DOC/'compact-runtime-mesh-projection.json.gz');refs=distinct_refs(refs+[projection_ref])
    oldcandidate=ref(capture.DOC/'private-native-terrain-candidate.json.gz')
    save(DOC/'input.json.gz',dict(schema='polyu-append-source-region-historical-production-v1',historicalReplay=True,currentAcceptance=False,physicalAccepted=False,historicalCapturedManifestSHA256=binding.HISTORICAL,
        historicalSceneManifestReference=archive,completedNominationJob=JOB,newNomination=nomref,previousFullNomination=nom['previousFullNomination'],runtimeProjection=projection_ref,completeMeshBinding=nom['newCompleteMeshBinding'],explicitPreservationCounts=preservation,
        previousPrivateCandidate=oldcandidate,completeNewNativeFacets=148459,completeNewPositionVertices=587502,fullParentDomain=old_input['fullParentDomain'],complete25SourceEvidence=old_input['complete25SourceEvidence'],
        exact25CurrentForms=old_input['exact25CurrentForms'],previousOriginalGuardRows=old_input['previousOriginalGuardRows'],originalGuardDefinition=old_input['originalGuardDefinition'],allInputRefs=refs,
        sourceInputEpochRemainsHistoricalNotCurrent6652=True,UptonCurrentAcceptanceRequiresSeparateExactDisjointDeltaRebind=True))
    for name in ['complete-fresh-current-native59527-and24-BASIC.json.gz','native59527-unchanged-provider-original-world.json.gz']:
        source=capture.PREVIOUS_CAPTURE/name;target=DOC/name;shutil.copyfile(source,target);assert ref(target)['sha256']==ref(source)['sha256']
    save(DOC/'historical-source-input-reuse.json',dict(sourceRefs=[ref(capture.PREVIOUS_CAPTURE/name)for name in ['complete-fresh-current-native59527-and24-BASIC.json.gz','native59527-unchanged-provider-original-world.json.gz']],resolvedSourceInputRefs=source_refs,
        genuineHistoricalContextReference=ref(UPTON/'historical-input-context.json'),sameSourceFormModuleAttributeMatrixBytes=True,noSourceRecapture=True,currentAcceptance=False))
    command=['node',str(RUNTIME),str(DOC.relative_to(ROOT))]
    with(DOC/'actual-production-replay.log').open('xb')as log:p=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    save(DOC/'actual-runtime-command.json',dict(command=command,exitCode=p.returncode,noLiveChanges=True,historicalReplay=True))
    if p.returncode==0:
        replay=read(DOC/'actual-production-replay.json.gz');assert replay['historicalCapturedManifestSHA256']==binding.HISTORICAL and not replay['currentAcceptance']and replay['startEndAllInputsVerified']and replay['currentExteriorXYZOrderedHashMatched']
        refs=distinct_refs(refs+[dict(path=p,sha256=h)for p,h in replay['inputHashes'].items()])
        candidate=read(DOC/'private-native-terrain-candidate.json.gz');assert mesh_binding({k:candidate['nativeMesh'][k]for k in ['position','index']})==nom['newCompleteMeshBinding']
        assert binding.grid_domain(candidate)==old_input['fullParentDomain']
        validator=capture.prior.module('append_historical_unchanged_validator',capture.VALIDATOR);failure=None
        try:validator.validate_patch(candidate,read(ROOT/'3d-viewer/city/data/terrain.json'))
        except (AssertionError,ValueError)as e:failure=dict(type=type(e).__name__,message=str(e))
        save(DOC/'real-validator-outcome.json',dict(passed=failure is None,actualFailure=failure,unchangedValidator=ref(capture.VALIDATOR),noOldGeometryBoundOverlapApproval=True,noToleranceChanges=True,historicalReplay=True,currentAcceptance=False,physicalAccepted=False))
    else:save(DOC/'real-validator-outcome.json',dict(passed=False,notExecuted=True,actualRuntimeExitCode=p.returncode,noSamplerErrorWaiver=True,currentAcceptance=False))
    save(DOC/'diagnostic.json',dict(runtimeExitCode=p.returncode,wholeHistorical25GuardAndRectangleSamplerViabilityOnly=True,completeOwned10536FourWorldNative59527And24BASICNewGroundFiniteStillPending=True,
        independentFourGuardActors=capture.nomination.CONFLICTS,nativeFullMeshCheckStillPending=True,oldGeometryBoundOverlapApprovalNotTransferred=True,currentAcceptance=False,physicalAccepted=False,newlyInstalled=0))
    refs=distinct_refs(refs+[ref(p)for p in DOC.rglob('*')if p.is_file()]);fence()
    result=capture.prior.module('append_historical_viability_freezer',capture.prior.FREEZER).freeze(BATCH,'historical-saved-scene-append-private-production-viability-only',[check(q)for q in refs],dict(uids=capture.prior.UIDS,sourceOnly=True,privateCandidate=True,
        historicalCapturedManifestSHA256=binding.HISTORICAL,currentAcceptance=False,physicalAccepted=False,installationApproved=False,newlyInstalled=0,runtimeExitCode=p.returncode,newNativeFacets=148459))
    fence();print(json.dumps(dict(jobId=result['jobId'],result=ref(DOC/'result.json'),runtimeExitCode=p.returncode,currentAcceptance=False)),flush=True)

def main():
    if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
    if '--owned'in sys.argv:return owned()
    assert '--capture-append-historical-private-candidate-only'in sys.argv and not DOC.exists()and not LOCAL.exists()
    *_,resources=load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))and prep['runtime']==ref(RUNTIME)
    claim=reservations.claim('polyu-append-historical-production-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
    try:
        save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
