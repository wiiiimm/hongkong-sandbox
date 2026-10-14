"""ROOT-only first actual ordinary guards after a retained-constructor setup hold.
Current terrain/all native patches remain unchanged; no component engineering gate.
"""
from pathlib import Path
import copy,json,subprocess,sys,uuid,time,importlib.util
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from aqua_named_original_overhead_identity_20261010 import UID,FOREIGN,SOURCE_SHA,FOREIGN_SHA,WORLD_SHA
import aqua_current_bound_overhead_identity_v3_20261010 as identity_source
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-aqua-marine193086-unchanged-current-ordinary-physical-v1-20261014';DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
INPUT=identity_source.DOC;IDENTITY=BASE/'government-xl-aqua-marine-current-bound-overhead-promotion-v3-20261010';FAILED=BASE/'government-xl-aqua-marine-complete-original-physical-v4-20261010';CURRENT_INSTALL=BASE/'government-xl-upton-joint-original-functional-installed-v2-20261014'
CURRENT='2a4c1ee569254ee5b93026e48454241a963feda3b7048856e672dcd0b1c58bcb';SNAPSHOT='518fca8a56d13208';CURRENT_JOB='f099afe8572e53c2fe16f5a185b475cf21ba8541f6f1bbb2cf148d0ad214d3a0'
RETAINED=['city/data/government-native-242392-0.json','city/data/government-native-76044-0.json'];OLD_MANIFEST='7b6d91add020de441c4a6c9f0fa44ceefa8d97bf459f23c4da8b6922ca674c4c'
FREEZER=HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def check(q):
    p=(ROOT/q['path']).resolve();assert p.is_relative_to(ROOT)and ref(p)==q;return p
def module(p,name):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def encoded(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def reuse_identity(saved, *, original_row, current_row, old_context, current_context,
                   old_forms,current_forms,old_pins,current_pins):
    assert encoded(original_row)==encoded(current_row)
    assert encoded(old_context)==encoded(current_context)
    assert encoded(old_forms)==encoded(current_forms)
    assert encoded(old_pins)==encoded(current_pins)
    assert saved['passed']and not saved['reasons']and saved['uid']==UID and saved['sourceSHA256']==SOURCE_SHA
    assert not saved['physicalAccepted']and not saved['installationApproved']
    assert len(current_forms)==17 and len({f['uid']for f in current_forms})==17
    assert saved['noCommonOwnershipOrSupportClaim']and saved['foreignCollisionExemption']is False
    return dict(savedIdentityVerbatim=saved,exactCompleteSourceGraphStreamWorldFormTileAndEntryTupleReused=True,oldCurrentBindingVerbatim=saved['currentBinding'],compressedSourceBytesAuthenticateSavedCompleteStreams=True,noOldKernelHashRelabel=True,noPhysicalOrSupportCredit=True)

def load():
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)['sha256']==CURRENT
    pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';assert read(pointer)['snapshotId']==SNAPSHOT
    v=read(CURRENT_INSTALL/'ROOT-VERIFIED.json');assert v['jobId']==CURRENT_JOB and v['exactNeonReadback']and v['allEvidenceHashesVerified']and v['leaseReleased']
    installed=read(CURRENT_INSTALL/'result.json');assert installed['jobId']==CURRENT_JOB and installed['snapshotId']==SNAPSHOT and installed['manifest']==ref(manifest)and installed['fullXLCurrentCounts']==dict(total=521,installedVerified=235,remaining=286)
    selection=read(INPUT/'selection.json.gz');assert len(selection['rows'])==1;row=selection['rows'][0];assert row['uid']==UID and row['sourceSHA256']==SOURCE_SHA and row['triangles']==22735
    context=read(INPUT/'context.json.gz')['rows'];assert len(context)==1 and context[0]['uid']==UID;context=context[0]
    capture=read(INPUT/'current-inputs.json.gz');assert capture['manifestSHA256']==OLD_MANIFEST and context['neighbourTileHashes']==capture['tileHashes']
    for url,h in capture['tileHashes'].items():assert ref(ROOT/'3d-viewer'/url)['sha256']==h
    saved=read(IDENTITY/'identity.json');assert saved['currentBinding']['manifestSHA256']==OLD_MANIFEST and saved['passed']
    source=read(INPUT/'source-lookup.json.gz');pins=read(INPUT/'complete-original-stream-pins.json.gz');assert ref(ROOT/row['candidate']['path'])['sha256']==SOURCE_SHA and ref(ROOT/source['originalPaths'][FOREIGN])['sha256']==FOREIGN_SHA
    receipts=[];refs=[];historical=[]
    for folder in [INPUT,IDENTITY,FAILED]:
        result=read(folder/'result.json');receipts.append(dict(folder=str(folder.relative_to(ROOT)),result=result));refs.append(ref(folder/'result.json'))
        for q in result['evidenceRefs']:
            if q['path']=='3d-viewer/city/data/manifest.json':assert q['sha256']==OLD_MANIFEST;historical.append(q)
            else:check(q);refs.append(q)
    failure=read(FAILED/'guard-failure.json');assert 'Requires retained native patch handling'in failure['error']and all(url in failure['error']for url in RETAINED)
    native={};catalogues=[]
    for url in read(manifest)['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url;catalogues.append(ref(path))
        for m in read(path)['models']:assert m['uid']not in native;native[m['uid']]=m
    assert len(native)==6652 and UID not in native
    retain=[]
    for url in RETAINED:
        assert sum(p['url']==url for p in read(manifest)['terrainPatches'])==1;path=ROOT/'3d-viewer'/url;patch=read(path);assert patch.get('nativeMesh');retain.append(dict(url=url,source=ref(path),targetUids=patch['meta']['targetUids']));refs.append(ref(path))
    scope=sorted({f['uid']for f in capture['forms']}|{u for p in retain for u in p['targetUids']})
    return row,context,capture,saved,source,pins,receipts,distinct_refs(refs+catalogues+[ref(manifest),ref(pointer),ref(CURRENT_INSTALL/'result.json'),ref(CURRENT_INSTALL/'ROOT-VERIFIED.json')]),historical,native,retain,scope

def schema_only():
    row,context,capture,saved,source,pins,receipts,refs,historical,native,retain,scope=load()
    return dict(passed=True,caller=ref(Path(__file__)),currentManifestSHA256=CURRENT,currentSnapshot=SNAPSHOT,completeCurrentCatalogueModels=6652,sourceFaces=22735,savedIdentityPassed=True,saved17FormTileBytesExactlyCurrent=True,retainedNativePatches=retain,canonicalUIDScope=scope,historicalOldManifestRefs=historical,noSourceDecodeGeometryNumericalDBLeaseWorker=True)

def owned():
    lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
    row,context,capture,saved,source,pins,receipts,refs,historical,native,retain,scope=load();refs=distinct_refs(refs+prep['codeRefs']+prep['inputRefs']+prep['evidenceRefs']+[ref(PROPOSAL/'actual-readonly-preparation.json')]);last=time.monotonic()
    def pulse():
        nonlocal last
        assert reservations.owns(lease)
        if time.monotonic()-last>20:assert reservations.heartbeat(lease,ttl=3600)['ok'];last=time.monotonic()
    def fence():
        for q in refs:check(q);pulse()
        assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT and read(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json')['snapshotId']==SNAPSHOT
    fence()
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        for receipt in receipts:assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['result']['jobId'],)).fetchone()==('complete',receipt['result'])
        assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(CURRENT_JOB,)).fetchone()==('complete',read(CURRENT_INSTALL/'result.json'))
        assert identity_source.native_rows(db)==source['rows']
        assert db.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key)WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
    DOC.mkdir();own=(ROOT/row['candidate']['path']).read_bytes();foreign=(ROOT/source['originalPaths'][FOREIGN]).read_bytes();assert digest(own)==pins['own']['compressedSHA256']==SOURCE_SHA and digest(foreign)==pins['foreign']['compressedSHA256']==FOREIGN_SHA and pins['own']['completeWorldSHA256']==WORLD_SHA
    # Immutable compressed bytes authenticate every saved complete graph/stream
    # and original-world input; do not decode/recompute the old identity proof.
    current_pins=copy.deepcopy(pins);lo,hi=row['candidate']['entry']['worldBounds'];final=module(HERE/'xl-final-script-pass.py','aqua_ordinary_current_forms');loaded=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);forms=[f for f,_,_ in loaded];tiles={u:ref(ROOT/'3d-viewer'/u)['sha256']for _,_,u in loaded};assert tiles==capture['tileHashes']
    reuse=reuse_identity(saved,original_row=row,current_row=row,old_context=context,current_context={**context,'neighbourTileHashes':tiles},old_forms=capture['forms'],current_forms=forms,old_pins=pins,current_pins=current_pins);save(DOC/'exact-saved-identity-current-reuse.json',dict(**reuse,currentManifestSHA256=CURRENT,currentSnapshot=SNAPSHOT,sourceGeometryChanges=0));save(DOC/'identity.json',saved)
    asset=LOCAL/row['candidate']['entry']['asset'];asset.parent.mkdir(parents=True,exist_ok=True);asset.write_bytes(own);assert ref(asset)['sha256']==SOURCE_SHA;current_row=copy.deepcopy(row);current_row['candidate']['path']=str(asset.relative_to(ROOT));cat=read(HERE/'accepted/government-xxl-20260911/catalogue.json');cat.update(area=BATCH,models=[row['candidate']['entry']],counts=dict(packedModels=1));save(LOCAL/'catalogue.json',cat);save(LOCAL/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));save(LOCAL/'source-forms.json',{UID:row['source']});save(DOC/'selection.json.gz',dict(rows=[current_row],batch=BATCH,manifestSHA256=CURRENT,nativeRun=NATIVE_RUN));save(DOC/'terrain-candidates.json',[])
    save(DOC/'neighbour-inputs.json.gz',dict(rows=[dict(building=f,existingNative=f['uid']in native,patchIndexes=[])for f in forms],inputHashes={'3d-viewer/'+u:h for u,h in tiles.items()},candidateIds=[UID],patches=[]))
    def call(command,allowed=(0,)):
        fence();log=DOC/('command-'+str(len(list(DOC.glob('command-*.json')))).zfill(3)+'.json');p=subprocess.run(command,cwd=ROOT,capture_output=True,text=True);save(log,dict(command=command,exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr));fence();assert p.returncode in allowed,log
    rel=lambda p:str(p.relative_to(ROOT));call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(LOCAL),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json'),'--geometry-out',rel(LOCAL/'runtime-geometry.json.gz')]);call(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(LOCAL),'--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'validation.json')],(0,1));call(['node',str(HERE/'check-neighbours.mjs'),rel(DOC)+'/']);call(['node',str(HERE/'check-native-neighbours.mjs'),rel(DOC)+'/'])
    actual=read(LOCAL/'runtime-geometry.json.gz')['rows'];assert len(actual)==1 and actual[0]['uid']==UID;a=actual[0];tri=np.asarray(a['position'],dtype='<f8').reshape(-1,3)[np.asarray(a['index'],dtype=np.int64).reshape(-1,3)];ground=np.asarray(a['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);assert tri.shape==(22735,3,3)and np.isfinite(tri).all()and np.isfinite(ground).all();b=row['source']['building'];f=final.foundation_context(tri,ground,Polygon(b['rings'][0],b['rings'][1:]));accepted=f['completeTerrainTriangles']==f['triangles']and not f['fullyBuriedUpwardTriangles']and f['fullyBuriedAreaFraction']==0;save(DOC/'foundation.json',dict(rows=[dict(uid=UID,sourceSHA256=SOURCE_SHA,foundation=f,strictFoundationAccepted=accepted)],terrainGeometryChanges=0))
    metrics=read(DOC/'metrics.json');validation=read(DOC/'validation.json');policy=module(HERE/'acceptance-policy.py','aqua_ordinary_unchanged_policy');reasons=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=SOURCE_SHA,identityProof=saved['proof']),metrics['rows'][0],metrics['profiles']['mobile']);save(DOC/'diagnostic.json.gz',dict(uid=UID,currentManifestSHA256=CURRENT,currentSnapshot=SNAPSHOT,ordinaryNumericReasons=reasons,strictFoundationAccepted=accepted,rawRuntimeConcerns=validation['results'],loaderAccepted=validation['loaderAccepted'],runtimeChecksPassed=validation['checksPassed'],runtimeExceptions=validation['exceptions'],neighbourRegressionReasons=[r for r in read(DOC/'neighbour-checks.json')['rows']if r['reasons']],nativeNeighbourChecks=read(DOC/'native-neighbour-checks.json'),completeOriginalFaces=22735,completeActualDrawnGroundFaces=len(ground),actualLiteralWorldSHA256=digest(tri.tobytes()),originalWorldSHA256=WORLD_SHA,completeCatalogueScope=6652,current17WholeForms=17,retainedNativePatchesUnchanged=retain,allSourceOnlyIdentityRawNegativesRetained=True,historicalFailedConstructorAndUnmeasuredTenParts=ref(FAILED/'result.json'),tenUnattachedSourcePartsAloneNotNewViewerFailure=True,fullAffectedFourWorldFiniteAndSourceCollisionAndBrowserStillRequired=True,sourceGeometryChanges=0,terrainGeometryChanges=0,physicalAccepted=False,installationApproved=False,newlyInstalled=0))
    for name in ['metrics.json','validation.json','neighbour-checks.json','native-neighbour-checks.json']:
        report=read(DOC/name);refs=distinct_refs(refs+[dict(path=p,sha256=h)for p,h in (report.get('inputHashes')or report.get('hashes')or{}).items()])
    save(DOC/'historical-source-context.json',dict(oldManifestRefsVerbatim=historical,currentManifestSHA256=CURRENT,allOtherSourceEvidenceRefsUnchanged=True,failedConstructor=ref(FAILED/'guard-failure.json'),oldUnmeasuredAppendedTenPartsReasonRetained=read(FAILED/'result.json')['reasons'],noModelCorruptionOrPermanentRejectionClaim=True));refs=distinct_refs(refs+[ref(p)for folder in [DOC,LOCAL]for p in folder.rglob('*')if p.is_file()and p.name!='reservation.json']);fence();module(FREEZER,'aqua_ordinary_canonical_freezer').freeze(BATCH,'one-original-unchanged-current-first-ordinary-viewer-physical-gates',[check(q)for q in refs],dict(uids=[UID],sourceOnly=True,terrainGeometryChanges=0,physicalAccepted=False,newlyInstalled=0))

def main():
    if '--schema-only'in sys.argv:print(json.dumps(schema_only()));return
    if '--owned'in sys.argv:return owned()
    assert '--check-original-on-unchanged-current-terrain-only'in sys.argv and not DOC.exists()and not LOCAL.exists();*_,scope=load();assert read(PROPOSAL/'actual-readonly-preparation.json')['passed'];resources=['building:'+u for u in scope]+['terrain-patch:'+u for u in scope]+['immutable-source-proof:'+BATCH];claim=reservations.claim('aqua-current-ordinary-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
    try:save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
