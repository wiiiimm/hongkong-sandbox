"""ROOT-only Museum ordinary physical checks on unchanged current terrain."""
from pathlib import Path
import json,gzip,hashlib,sys,copy,subprocess,uuid,importlib.util
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from timed_owned_lease_pulse_v1_20261014 import TimedOwnedLeasePulse
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent;BASE=ROOT/'docs/astra-city/government-import';UID='landsd/165054:0';SOURCE='1a978cdc751afa70933802e2faf090b2435250967e63b68f348ed232aeb1837f';WORLD='258ac5cbe505d4f78f8cd334e1b6bbd3e3a56bcd6ef4e1854865f1dade75e8c7';CURRENT='12971667a74b07de90ce5ee29999f44a6bf297de84ec7916a629bc42725cd82c';SNAPSHOT='be5f7671a989392d'
BATCH='government-xl-heritage165054-current-ordinary-physical-v1-20261014';DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';FREEZER=HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py';CLOSURE=HERE/'aqua_marine193086_ordinary_runtime_closure_v2_20261014.mjs'
ROW=BASE/'government-xl-heritage165054-starmart57455-current-finite-collision-draft-v1-20261014/exact-source-row-current-form.json';IDENTITY_FOLDER=BASE/'government-xl-heritage165054-current-typed-identity-draft-v3-20261014/current-identity-output-v3';IDENTITY=IDENTITY_FOLDER/'typed-current-identity.json';CONTEXT=IDENTITY_FOLDER/'current-context.json';INTERFACE=BASE/'government-xl-heritage165054-starmart57455-private-interface-review-v5-20261014';JUNCTION=BASE/'government-xl-heritage165054-six-facet-authored-junction-review-v1-20261014'
RECEIPTS={BASE/'government-xl-heritage165054-current-typed-identity-receipt-v3-20261014':'fdbe6836f75e6e2a8d0951c91d974b88f8441e21093626e0997ba1481d246f41',INTERFACE:'f1fd2d0887c7635b0725f786c9e05a55deb56083e91b95d8415cfed7fe4933c4',BASE/'government-xl-aqua-marine193086-original-installed-v1-20261014':'a5cb467f8db00847459bf00ae403d7abc4781d02ac49b8f581c53f926f561122'}
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def check(q):
    p=(ROOT/q['path']).resolve();assert p.is_relative_to(ROOT)and ref(p)==q;return p
def save(p,o):
    p.parent.mkdir(parents=True,exist_ok=True);b=json.dumps(o,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
    with p.open('xb')as f:f.write(gzip.compress(b,mtime=0)if p.suffix=='.gz'else b+b'\n')
def encoded(o):return json.dumps(o,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def module(p,name):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def bind_saved_identity(row,identity,context,forms,tiles):
    assert row['uid']==identity['uid']==context['uid']==UID and row['sourceSHA256']==identity['sourceSHA256']==context['sourceSHA256']==SOURCE
    assert identity['passed']and not identity['reasons']and identity['completeOriginalFaceCount']==row['triangles']==15140 and identity['worldTrianglesSHA256']==WORLD
    assert encoded(row['candidate']['entry']['worldBounds'])==encoded(row['native']['model']['worldBounds'])
    assert identity['proof']==dict(exactBuildingCSUID=True,exactObjectId=True,identityAccepted=True,uniqueViewerMatch=True)
    assert identity['StarMartForeignPreserved']and not identity['physicalSupportExemption']and not identity['runtimeExemption']
    assert encoded(forms)==encoded(identity['allCurrentFormsRetained'])and encoded(tiles)==encoded(context['neighbourTileHashes'])
    assert next(f for f in forms if f['uid']==UID)==row['source']['building']
    return dict(identityPassed=True,exactCompleteSourceAndLocalFormsTileHashesUnchanged=True,rawIdentityVerbatim=identity,noIdentityCalculationsRepeated=True,noForeignCollisionOrRuntimeExemption=True)

def inputs():
    row=read(ROW);identity=read(IDENTITY);context=read(CONTEXT);forms=identity['allCurrentFormsRetained'];tiles=context['neighbourTileHashes'];assert len(forms)==10 and len({f['uid']for f in forms})==10
    refs=[ref(p)for p in [ROW,IDENTITY,CONTEXT,IDENTITY_FOLDER/'result.json',JUNCTION/'proposed-six-facet-source-context-disposition.json',JUNCTION/'REVIEW.md',INTERFACE/'reused-successful-current-BASIC-exports-and-rejected-Star-runtime.json',INTERFACE/'actual-private-interface-preview.json']]
    for url,h in tiles.items():
        p=ROOT/'3d-viewer'/url;assert ref(p)['sha256']==h;tile=read(p)
        for f in forms:
            if f['tile']==tile['id']:assert encoded([b for b in tile['buildings']if b['uid']==f['uid']])==encoded([f])
        refs.append(ref(p))
    bind_saved_identity(row,identity,context,forms,tiles);asset=ROOT/row['candidate']['path'];assert ref(asset)['sha256']==SOURCE;refs.append(ref(asset));manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)['sha256']==CURRENT;refs.append(ref(manifest));m=read(manifest);native=[]
    for url in m['officialModelCatalogues']:
        p=ROOT/'3d-viewer'/url;refs.append(ref(p));native+=read(p)['models']
    assert len(native)==6653 and len({r['uid']for r in native})==6653 and not any(r['uid']==UID or UID in r.get('suppressesBuildingUids',[])for r in native)
    for q in m['terrainPatches']:refs.append(ref(ROOT/'3d-viewer'/q['url']))
    refs +=[ref(ROOT/'3d-viewer/city/data/terrain.json'),ref(HERE/'accepted/government-xxl-20260911/catalogue.json')];pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';assert read(pointer)['snapshotId']==SNAPSHOT;refs.append(ref(pointer))
    for folder,job in RECEIPTS.items():
        r=read(folder/'result.json');v=read(folder/'ROOT-VERIFIED.json');assert r['jobId']==v['jobId']==job and v['exactNeonReadback']and v['allEvidenceHashesVerified']and(v.get('leaseReleased')or v.get('leasesReleased'));refs +=[ref(folder/'result.json'),ref(folder/'ROOT-VERIFIED.json')]
    refs=distinct_refs(refs)
    for q in refs:check(q)
    return row,identity,context,forms,tiles,{r['uid']for r in native},refs

def load():
    p=read(PROPOSAL/'draft-pins.json');assert p['caller']==ref(Path(__file__))
    for q in p['codeRefs']+p['inputRefs']:check(q)
    data=inputs();assert distinct_refs(data[-1])==p['inputRefs'];return p,data

def owned():
    from run import connect,reservations,NATIVE_RUN
    import numpy as np
    from shapely.geometry import Polygon
    p,data=load();row,identity,context,forms,tiles,native,refs=data;prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__));lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();refs=distinct_refs(refs+p['codeRefs']+prep['evidenceRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'actual-readonly-preparation.json')]);pulse=TimedOwnedLeasePulse(lambda:reservations.owns(lease),lambda:reservations.heartbeat(lease,ttl=3600))
    def fence():
        pulse(force=True)
        for q in distinct_refs(refs):check(q);pulse()
        assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT;pulse(force=True)
    fence()
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        for folder,job in RECEIPTS.items():assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(job,)).fetchone()==('complete',read(folder/'result.json'))
        assert db.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key)WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
    final=module(HERE/'xl-final-script-pass.py','heritage_ordinary_final');lo,hi=row['candidate']['entry']['worldBounds'];loaded=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);current_forms=[f for f,_,_ in loaded];current_tiles={url:ref(ROOT/'3d-viewer'/url)['sha256']for _,_,url in loaded};reuse=bind_saved_identity(row,identity,context,current_forms,current_tiles)
    DOC.mkdir();save(DOC/'exact-saved-current-local-identity-reuse.json',{**reuse,'currentManifestSHA256':CURRENT,'currentSnapshot':SNAPSHOT,'historicalManifestSHA256':read(IDENTITY_FOLDER/'result.json')['allInputHashes']['3d-viewer/city/data/manifest.json']});save(DOC/'identity.json',identity)
    own=(ROOT/row['candidate']['path']).read_bytes();asset=LOCAL/row['candidate']['entry']['asset'];asset.parent.mkdir(parents=True,exist_ok=True);asset.write_bytes(own);assert ref(asset)['sha256']==SOURCE;current_row=copy.deepcopy(row);current_row['candidate']['path']=str(asset.relative_to(ROOT));cat=read(HERE/'accepted/government-xxl-20260911/catalogue.json');cat.update(area=BATCH,models=[row['candidate']['entry']],counts=dict(packedModels=1));save(LOCAL/'catalogue.json',cat);save(LOCAL/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));save(LOCAL/'source-forms.json',{UID:row['source']});save(DOC/'selection.json.gz',dict(rows=[current_row],batch=BATCH,manifestSHA256=CURRENT,nativeRun=NATIVE_RUN));save(DOC/'terrain-candidates.json',[]);save(DOC/'neighbour-inputs.json.gz',dict(rows=[dict(building=f,existingNative=f['uid']in native,patchIndexes=[])for f in current_forms],inputHashes={'3d-viewer/'+url:h for url,h in current_tiles.items()},candidateIds=[UID],patches=[]))
    def call(command,allowed=(0,)):
        fence();log=DOC/('command-'+str(len(list(DOC.glob('command-*.json')))).zfill(3)+'.json');r=subprocess.run(command,cwd=ROOT,capture_output=True,text=True);save(log,dict(command=command,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr));fence();assert r.returncode in allowed,log
    rel=lambda p:str(p.relative_to(ROOT));call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(LOCAL),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json'),'--geometry-out',rel(LOCAL/'runtime-geometry.json.gz')]);call(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(LOCAL),'--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'validation.json')],(0,1));call(['node',str(HERE/'check-neighbours.mjs'),rel(DOC)+'/']);call(['node',str(HERE/'check-native-neighbours.mjs'),rel(DOC)+'/'])
    actual=read(LOCAL/'runtime-geometry.json.gz')['rows'];assert len(actual)==1 and actual[0]['uid']==UID;a=actual[0];tri=np.asarray(a['position'],dtype='<f8').reshape(-1,3)[np.asarray(a['index'],dtype=np.int64).reshape(-1,3)];ground=np.asarray(a['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);assert tri.shape==(15140,3,3)and np.isfinite(tri).all()and np.isfinite(ground).all();b=row['source']['building'];f=final.foundation_context(tri,ground,Polygon(b['rings'][0],b['rings'][1:]));accepted=f['completeTerrainTriangles']==f['triangles']and not f['fullyBuriedUpwardTriangles']and f['fullyBuriedAreaFraction']==0;save(DOC/'foundation.json',dict(rows=[dict(uid=UID,sourceSHA256=SOURCE,foundation=f,strictFoundationAccepted=accepted)],terrainGeometryChanges=0))
    metrics=read(DOC/'metrics.json');validation=read(DOC/'validation.json');policy=module(HERE/'acceptance-policy.py','heritage_ordinary_policy');reasons=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=SOURCE,identityProof=identity['proof']),metrics['rows'][0],metrics['profiles']['mobile']);save(DOC/'diagnostic.json.gz',dict(uid=UID,currentManifestSHA256=CURRENT,currentSnapshot=SNAPSHOT,ordinaryNumericReasons=reasons,strictFoundationAccepted=accepted,rawRuntimeRows=validation['results'],loaderAccepted=validation['loaderAccepted'],runtimeChecksPassed=validation['checksPassed'],runtimeExceptions=validation['exceptions'],neighbourRegressionReasons=[r for r in read(DOC/'neighbour-checks.json')['rows']if r['reasons']],nativeNeighbourChecks=read(DOC/'native-neighbour-checks.json'),completeOriginalFaces=15140,completeActualDrawnGroundFaces=len(ground),actualLiteralWorldSHA256=hashlib.sha256(tri.tobytes()).hexdigest(),sourceOnlyAuthoredJunctionContext=ref(JUNCTION/'proposed-six-facet-source-context-disposition.json'),all14BASICAnd8OriginalCrossingsRetainedAsSourceContext=True,noForeignCollisionWaiver=True,originalStarFootprintRuntimeRejectedAndNotInstallTarget=True,terrainGeometryChanges=0,sourceGeometryChanges=0,physicalAccepted=False,installationApproved=False,newlyInstalled=0))
    for name in ['metrics.json','validation.json','neighbour-checks.json','native-neighbour-checks.json']:
        out=read(DOC/name);refs=distinct_refs(refs+[dict(path=p,sha256=h)for p,h in(out.get('inputHashes')or out.get('hashes')or{}).items()])
    refs=distinct_refs(refs+[ref(p)for folder in [DOC,LOCAL]for p in folder.rglob('*')if p.is_file()and p.name!='reservation.json']);fence();module(FREEZER,'heritage_ordinary_freezer').freeze(BATCH,'one-original-unchanged-current-ordinary-physical-no-invented-crossing-gate',[check(q)for q in refs],dict(uids=[UID],sourceOnly=True,terrainGeometryChanges=0,physicalAccepted=False,newlyInstalled=0))
def main():
    if '--schema-only'in sys.argv:
        p,data=load();print(json.dumps(dict(passed=True,caller=ref(Path(__file__)),currentManifestSHA256=CURRENT,currentSnapshot=SNAPSHOT,completeCurrentCatalogueModels=6653,sourceFaces=15140,savedIdentityPassed=True,exactTenLocalFormsAndTwoTileHashesPreserved=True,ordinaryPhysicalNotYetMeasured=True,noGeometrySourceDecodeDBLeaseWorker=True)));return
    if '--owned'in sys.argv:return owned()
    assert '--check-museum-on-unchanged-current-terrain-only'in sys.argv and not DOC.exists()and not LOCAL.exists();p,data=load();assert read(PROPOSAL/'actual-readonly-preparation.json')['passed'];scope=sorted(f['uid']for f in data[3]);resources=['building:'+u for u in scope]+['terrain-patch:'+u for u in scope]+['immutable-source-proof:'+BATCH]
    from run import reservations
    claim=reservations.claim('heritage-current-ordinary-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
    try:save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
