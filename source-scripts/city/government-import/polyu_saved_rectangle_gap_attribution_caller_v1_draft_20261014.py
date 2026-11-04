"""UNEXECUTED historical c00 saved-candidate attribution; no current gate."""
from pathlib import Path
import json,sys,time,uuid,subprocess
import numpy as np
from run import ROOT,HERE,read,save,connect,reservations
import polyu_parent_cell_actual_production_capture_v4_draft_20261014 as capture
import polyu_saved_rectangle_gap_attribution_v1_draft_20261014 as locator
from exact_closed_ground_aabb_pruning_v1_20261011 import CompleteGround
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs

BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-polyu-saved-rectangle-gap-attribution-v1-20261014'
DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
JOB='59491c7701e48dca8e907808ea8e0b487feaa5f6d8a8b6fbb57ca57fc733c6b2'
ref,check=capture.ref,capture.check;HISTORICAL=capture.CURRENT

def load():
    pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))
    for q in distinct_refs(pins['codeRefs']+pins['inputRefs']):check(q)
    receipt=read(capture.DOC/'result.json');assert receipt['jobId']==JOB
    verified=read(capture.DOC/'ROOT-VERIFIED.json');assert verified['jobId']==JOB and verified['exactNeonReadback']and verified['allEvidenceHashesVerified']and verified['leaseReleased']
    inp=read(capture.DOC/'input.json.gz');replay=read(capture.DOC/'actual-production-replay.json.gz')
    assert inp['currentManifestSHA256']==replay['currentManifestSHA256']==HISTORICAL
    assert replay['startEndAllInputsVerified']and replay['currentExteriorXYZOrderedHashMatched']
    assert len(replay['before']['closedDomainDrawnTriplets'])==40 and len(replay['after']['closedDomainDrawnTriplets'])==147124
    assert len(replay['allCandidateGridSamples'])==1247 and not any(r['error']for r in replay['allCandidateGridSamples'])and not replay['allSamplerErrors']
    patch=read(capture.DOC/'private-native-terrain-candidate.json.gz');mesh=patch['nativeMesh'];p=np.asarray(mesh['position'],dtype='<f8').reshape(-1,3);ix=np.asarray(mesh['index'],dtype=np.int64).reshape(-1,3)
    raw=p.astype('<f4').astype('<f8')[ix];assert p.shape==(583413,3)and raw.shape==(147096,3,3)and np.isfinite(p).all()
    inp_ref=inp['newNomination'];nom=read(check(inp_ref));assert len(nom['candidateFaceProvenance'])==len(raw)
    assert mesh['index']==nom['newNativeMesh']['index']and mesh['position']==nom['newNativeMesh']['position']
    g=patch['meta']['georef'];domain=[g['bE']-834500,816500-g['bN'],g['bE']+(patch['w']-1)*g['aE']-834500,816500-(g['bN']+(patch['h']-1)*g['aN'])]
    assert domain==inp['fullParentDomain']==[2002.5,-2067.5,2212.5,-1927.5]
    validator=read(capture.DOC/'real-validator-outcome.json');assert not validator['passed']and validator['actualFailure']['message']=='Native mesh does not cover the exact parent rectangle'
    guards=read(capture.DOC/'all25-original-production-guard-site-replay.json.gz');assert len(guards['rows'])==25 and guards['originalNine3366SitesExactlyRegenerated']and not guards['allSamplerErrors']
    resources=['immutable-source-proof:'+BATCH]
    return pins,receipt,inp,patch,raw,nom,domain,guards,validator,resources

def schema_only():
    _,_,_,_,raw,_,domain,guards,_,resources=load()
    return dict(passed=True,caller=ref(Path(__file__)),savedCaptureJob=JOB,historicalCapturedManifestSHA256=HISTORICAL,
        completeNativeFacets=len(raw),completePositionVerticesIncludingUnused=583413,fullParentDomain=domain,all25SavedGuardRows=25,canonicalResources=resources,
        noLiveManifestOrCurrentSceneAcceptanceGate=True,noUnionPointMathDBLeaseWorker=True)

def owned():
    lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists()
    pins,receipt,inp,patch,raw,nom,domain,guards,validator,resources=load();assert lease['resources']==resources
    prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
    validation=read(check(prep['helperValidationRef']));assert validation['passedTests']==6 and validation['failedTests']==0 and validation['exitCode']==0
    assert validation['executedCodeRefs']==[ref(Path(locator.__file__)),ref(HERE/'test_polyu_saved_rectangle_gap_attribution_v1_draft_20261014.py')]
    refs=distinct_refs(pins['codeRefs']+pins['inputRefs']+prep['evidenceRefs']+validation['evidenceRefs']+[prep['helperValidationRef'],ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'actual-readonly-preparation.json')])
    with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JOB,)).fetchone()==('complete',receipt)
    # Historical live-path refs inside the sealed receipt are recorded, not
    # aliased to today's scene. ROOT verified them at the captured epoch.
    last=time.monotonic()
    def pulse():
        nonlocal last
        if time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
    def fence():
        for q in refs:check(q);pulse()
        assert reservations.owns(lease)
    fence();DOC.mkdir();polygons,measurement,missing,outside=locator.measure(raw,domain);pulse()
    save(DOC/'saved-validator-missing-vs-outside.json.gz',dict(**measurement,actualValidatorOutcomeVerbatim=validator,historicalCaptureInputRef=ref(capture.DOC/'input.json.gz'),currentAcceptance=False))
    complete=CompleteGround(raw);rows=[]
    for kind,geometry in [('missing',missing),('outside',outside)]:
        pieces=locator.regions(geometry)
        for ordinal,component in enumerate(pieces):
            row=locator.attribute_component(component,ordinal,kind,complete,raw,polygons,nom['candidateFaceProvenance']);rows.append(row)
            save(DOC/'region-progress'/(kind+'-'+str(ordinal).zfill(5)+'.json.gz'),row);pulse()
            if (ordinal+1)%16==0:print(json.dumps(dict(kind=kind,componentsCompleted=ordinal+1,total=len(pieces))),flush=True)
    complete.verify_binding()
    summary=[{k:r[k]for k in ['uid','checks','beforeGap','afterGap','maxGroundChange','reasons']}for r in guards['rows']]
    save(DOC/'saved-coverage-region-and-guard-attribution.json.gz',dict(historicalCaptureJob=JOB,historicalCapturedManifestSHA256=HISTORICAL,
        completeNativeFacets=147096,measurement=measurement,regions=rows,all25GuardScalarRows=summary,
        fullGuardRowsReference=ref(capture.DOC/'all25-original-production-guard-site-replay.json.gz'),
        fullNominationReference=inp['newNomination'],allSampledGuardsDistinctFromWholeMeshOrdinary=True,
        GEOSLocatorsNotExactFractionAreaOrApproval=True,noLiveManifestGateOrCurrentAcceptance=True,
        noSourceRepackingCaptureWholeFiniteGeometryOrThresholdChanges=True,physicalAccepted=False,newlyInstalled=0))
    refs=distinct_refs(refs+[ref(p)for p in DOC.rglob('*')if p.is_file()]);fence()
    capture.prior.module('polyu_saved_rectangle_gap_freezer',capture.prior.FREEZER).freeze(BATCH,'historical-c00-saved-private-rectangle-gap-provenance-only',[check(q)for q in refs],dict(uids=capture.prior.UIDS,sourceOnly=True,historicalCapturedManifestSHA256=HISTORICAL,currentAcceptance=False,physicalAccepted=False,newlyInstalled=0))

def main():
    if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
    if '--owned'in sys.argv:return owned()
    assert '--attribute-saved-rectangle-gaps-only'in sys.argv and not DOC.exists()and not LOCAL.exists()
    *_,resources=load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
    claim=reservations.claim('polyu-saved-rectangle-gap-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
    try:
        save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
