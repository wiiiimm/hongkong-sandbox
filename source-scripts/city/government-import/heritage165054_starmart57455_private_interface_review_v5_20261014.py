"""ROOT-only opaque original-source interface review; raw crossings stay held."""
from pathlib import Path
import json,gzip,hashlib,sys,subprocess,uuid,importlib.util
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from heritage_saved_interface_schema_v1_20261014 import validate_saved_contacts
from heritage_saved_export_refs_v1_20261014 import saved_export_refs
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent;BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-heritage165054-starmart57455-private-interface-review-v5-20261014';DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';RUNTIME=HERE/'heritage165054_starmart57455_private_source_pair_v4_20261014.mjs'
CURRENT='12971667a74b07de90ce5ee29999f44a6bf297de84ec7916a629bc42725cd82c';SNAPSHOT='be5f7671a989392d';CURRENT_JOB='a5cb467f8db00847459bf00ae403d7abc4781d02ac49b8f581c53f926f561122'
OLD=BASE/'government-xl-heritage-starmart-eight-original-contact-context-draft-v2-20261014';CONTRACT=OLD/'input-contract.json'
MUSEUM_CAPTURE=BASE/'government-xl-heritage165054-starmart57455-current-finite-collision-draft-v2-20261014/collision-output-v2/complete-current-star-and-museum-geometry.json.gz'
STAR_FOLDER=BASE/'government-xl-heritage-starmart-original91-acquisition-contact-draft-v2-20261014/original-source-contact-output-v2';STAR_CAPTURE=STAR_FOLDER/'complete-star-original-current-geometry.json.gz'
ORIGINAL_CONTACTS=STAR_FOLDER/'diagnostic.json.gz';BASIC_CONTACTS=BASE/'government-xl-heritage165054-starmart57455-current-finite-collision-draft-v3-20261014/collision-output-v3/diagnostic.json.gz'
RECEIPTS={
 'government-xl-heritage165054-current-typed-identity-receipt-v3-20261014':'fdbe6836f75e6e2a8d0951c91d974b88f8441e21093626e0997ba1481d246f41',
 'government-xl-heritage165054-starmart57455-current-finite-collision-receipt-v3-20261014':'387fac7aa4b2f6dbc3ca6c1c4dc46531e963bb737d9aecd4edd9e233057e2f6f',
 'government-xl-heritage-starmart-original91-acquisition-contact-v2-20261014':'aecbb82d260cb55411134ac84fa951817acb71bf5fed1020ce7357850cef2273',
 'government-xl-heritage-starmart-eight-original-contact-context-v2-20261014':'49fc87bc1f2a7a3a2dcf0682aa93cc178134631c21b62380365179699546cfc0'}
FAILED_V4_DOC=BASE/'government-xl-heritage165054-starmart57455-private-interface-review-v4-20261014';FAILED_V4_PREP=BASE/'government-xl-heritage165054-starmart57455-private-interface-review-v4-20261014-proposal';FAILED_V4_LOCAL=HERE/'local/government-xl-heritage165054-starmart57455-private-interface-review-v4-20261014'
FAILED_V3_DOC=BASE/'government-xl-heritage165054-starmart57455-private-interface-review-v3-20261014';FAILED_V3_PREP=BASE/'government-xl-heritage165054-starmart57455-private-interface-review-v3-20261014-proposal';FAILED_V3_LOCAL=HERE/'local/government-xl-heritage165054-starmart57455-private-interface-review-v3-20261014'
FAILED_V2_DOC=BASE/'government-xl-heritage165054-starmart57455-private-interface-review-v2-20261014';FAILED_V2_PREP=BASE/'government-xl-heritage165054-starmart57455-private-interface-review-v2-20261014-proposal';FAILED_V2_LOCAL=HERE/'local/government-xl-heritage165054-starmart57455-private-interface-review-v2-20261014'
FAILED_DOC=BASE/'government-xl-heritage165054-starmart57455-private-interface-review-v1-20261014';FAILED_PREP=BASE/'government-xl-heritage165054-starmart57455-private-interface-review-v1-20261014-proposal';FAILED_LOCAL=HERE/'local/government-xl-heritage165054-starmart57455-private-interface-review-v1-20261014'
RESOURCES=['building:landsd/104467:0','building:landsd/165054:0','building:landsd/57455:0','native-model:aaf93675f4a7641051dfa64cb636c75ec7de43f13d5fbebd3218a9673400c02e/B370872650701063C0','native-model:aaf93675f4a7641051dfa64cb636c75ec7de43f13d5fbebd3218a9673400c02e/B371252646701063C0','immutable-source-proof:'+BATCH]
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def check(q):
    p=(ROOT/q['path']).resolve();assert p.is_relative_to(ROOT)and ref(p)==q;return p
def save(p,o):
    b=json.dumps(o,sort_keys=True,separators=(',',':'),allow_nan=False).encode();p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb')as f:f.write(gzip.compress(b,mtime=0)if p.suffix=='.gz'else b+b'\n')
def encoded(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def source_inputs():
    c=read(CONTRACT);m=read(MUSEUM_CAPTURE);s=read(STAR_CAPTURE);basic=read(BASIC_CONTACTS);original=read(ORIGINAL_CONTACTS);summary=validate_saved_contacts(basic,original)
    assert m['sourceSHA256']==c['museumSourceSHA256']and s['sourceSHA256']==c['starSourceSHA256']
    assert m['completeOriginalFaceCount']==15140 and s['completeOriginalFaceCount']==91 and s['pose']['exactLoaderTransformContractMatched']and s['pose']['unitScale']==[1,1,1]
    forms=read(ROOT/c['currentFormsPath']);refs=[ref(p)for p in [CONTRACT,MUSEUM_CAPTURE,STAR_CAPTURE,BASIC_CONTACTS,ORIGINAL_CONTACTS,ROOT/c['currentFormsPath'],ROOT/c['lookupPath']]]
    for f in forms:
        p=ROOT/f['sourceTile'];assert ref(p)['sha256']==f['sourceTileSHA256'];assert encoded([b for b in read(p)['buildings']if b['uid']==f['form']['uid']])==encoded([f['form']]);refs.append(ref(p))
    manifest=read(ROOT/'3d-viewer/city/data/manifest.json');assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT;refs.append(ref(ROOT/'3d-viewer/city/data/manifest.json'))
    pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';assert read(pointer)['snapshotId']==SNAPSHOT;refs.append(ref(pointer));refs.append(ref(ROOT/read(pointer)['inventory']))
    native=[]
    for path in manifest['officialModelCatalogues']:
        p=ROOT/'3d-viewer'/path;refs.append(ref(p));native+=read(p)['models']
    assert len(native)==6653 and len({r['uid']for r in native})==6653
    for uid in ['landsd/165054:0','landsd/57455:0']:
        assert not any(r['uid']==uid or uid in r.get('suppressesBuildingUids',[])for r in native)
    for patch in manifest['terrainPatches']:refs.append(ref(ROOT/'3d-viewer'/patch['url']))
    for name,job in RECEIPTS.items():
        r=read(BASE/name/'result.json');v=read(BASE/name/'ROOT-VERIFIED.json');assert r['jobId']==v['jobId']==job and v['exactNeonReadback']and v['allEvidenceHashesVerified']and(v.get('leaseReleased')or v.get('leasesReleased'));refs +=[ref(BASE/name/'result.json'),ref(BASE/name/'ROOT-VERIFIED.json')]
        if 'typed-identity'in name:assert v['identityAccepted']
    install=BASE/'government-xl-aqua-marine193086-original-installed-v1-20261014';r=read(install/'result.json');v=read(install/'ROOT-VERIFIED.json');assert r['jobId']==v['jobId']==CURRENT_JOB and v['exactNeonReadback']and v['allEvidenceHashesVerified']and v['leaseReleased'];refs +=[ref(install/'result.json'),ref(install/'ROOT-VERIFIED.json')]
    lookup=read(ROOT/c['lookupPath'])['rows'][0]['model'];star_entry={**lookup['asset'],'uid':'landsd/57455:0','label':'Star Mart PRIVATE original source comparison','modelId':lookup['modelId'],'buildingCSUID':'3708726507T20050430','sourceTile':'7-SW-15D','objectId':57455,'triangles':91,'rootTranslation':[-834500,0,816500],'worldBounds':lookup['worldBounds'],'recordedBaseHeight':5.1,'recordedTopHeight':8.9}
    sources=[]
    for uid,entry,asset in [(m['uid'],m['entry'],ROOT/c['originalAssetPath']),(s['uid'],star_entry,STAR_FOLDER/'packed/assets'/lookup['asset']['asset'].split('/')[-1])]:
        assert ref(asset)['sha256']==entry['sha256'];refs.append(ref(asset));entry={**entry,'priority':'landmark','proceduralWindows':False,'privateSourceInterpretationOnly':True,'sourceIdentityReviewed':False,'placementReviewed':False,'publicationApproved':False};sources.append(dict(uid=uid,entry=entry,faces=entry['triangles'],asset=ref(asset),currentForm=next(f['form']for f in forms if f['form']['uid']==uid)))
    failure=read(FAILED_DOC/'actual-render-log.json');assert failure['exitCode']==1 and 'Timeout 90000ms' in failure['stderr'];failed_report=read(FAILED_DOC/'actual-private-interface-preview.json');assert failed_report['views']==[]and failed_report['scenarios']==[]
    terminal=read(PROPOSAL/'V1-TERMINAL-RELEASE-CONTEXT.json');assert terminal['rootReportedTerminalExitCode']==1 and terminal['rootReportedLeaseReleased']and not terminal['modelDefectInferred'];check(terminal['preservedCompleteROOTLog'])
    refs +=read(FAILED_PREP/'draft-pins.json')['codeRefs']+[ref(q)for folder in [FAILED_DOC,FAILED_PREP]for q in folder.rglob('*')if q.is_file()]+[ref(FAILED_LOCAL/'reservation.json'),ref(PROPOSAL/'V1-TERMINAL-RELEASE-CONTEXT.json'),terminal['preservedCompleteROOTLog']]
    failure2=read(FAILED_V2_DOC/'actual-render-log.json');assert failure2['exitCode']==1 and 'Timeout 90000ms' in failure2['stderr'];report2=read(FAILED_V2_DOC/'actual-private-interface-preview.json');assert report2['views']==[]and report2['assetRequests']==[]
    rows=report2['loadingDiagnostics'];assert len(rows)==2 and all(not r['modelKnown']and r['buildingLoaded']and not r['schedulerError']for r in rows)and rows[-1]['official']['loadingPaused']is False;assert all(any('private-source-review'in e for e in r['official']['errors'])for r in rows)
    release2=read(PROPOSAL/'V2-TERMINAL-RELEASE-CONTEXT.json');assert release2['rootReportedTerminalExitCode']==1 and release2['rootReportedLeaseReleased']and not release2['modelDefectInferred']
    refs +=read(FAILED_V2_PREP/'draft-pins.json')['codeRefs']+[ref(q)for folder in [FAILED_V2_DOC,FAILED_V2_PREP]for q in folder.rglob('*')if q.is_file()]+[ref(FAILED_V2_LOCAL/'reservation.json'),ref(PROPOSAL/'V2-TERMINAL-RELEASE-CONTEXT.json')]
    failure3=read(FAILED_V3_DOC/'actual-render-log.json');assert failure3['exitCode']==1;report3=read(FAILED_V3_DOC/'actual-private-interface-preview.json');assert not report3['errors']and len(report3['views'])==3 and len(report3['scenarios'])==1
    good=report3['scenarios'][0];assert good['scenario']=='current-BASIC'and good['currentBASICDrawnFaces']==24 and good['sources'][0]['faces']==15140 and good['sources'][0]['sourceSHA256']==c['museumSourceSHA256']
    last=report3['loadingDiagnostics'][-1];assert last['uid']=='landsd/57455:0'and last['modelKnown']and last['buildingLoaded']and not last['detailedActive']and 'Official model does not fit its matched footprint'in last['cacheError']and not last['official']['loadingPaused']
    release3=read(PROPOSAL/'V3-TERMINAL-RELEASE-CONTEXT.json');assert release3['rootReportedTerminalExitCode']==1 and release3['rootReportedLeaseReleased']and not release3['sourceCorruptionInferred']
    refs +=read(FAILED_V3_PREP/'draft-pins.json')['codeRefs']+[ref(q)for folder in [FAILED_V3_DOC,FAILED_V3_PREP]for q in folder.rglob('*')if q.is_file()]+[ref(FAILED_V3_LOCAL/'reservation.json'),ref(PROPOSAL/'V3-TERMINAL-RELEASE-CONTEXT.json')]
    assert FAILED_V4_DOC.is_dir()and not list(FAILED_V4_DOC.iterdir());release4=read(PROPOSAL/'V4-TERMINAL-RELEASE-CONTEXT.json');assert release4['rootReportedTerminalExitCode']==1 and release4['rootReportedLeaseReleased']and release4['noRendererStarted']and not release4['modelDefectInferred']
    refs +=read(FAILED_V4_PREP/'draft-pins.json')['codeRefs']+[ref(q)for q in FAILED_V4_PREP.rglob('*')if q.is_file()]+[ref(FAILED_V4_LOCAL/'reservation.json'),ref(PROPOSAL/'V4-TERMINAL-RELEASE-CONTEXT.json')]+saved_export_refs(ROOT,report3['views'],ref)
    refs=distinct_refs(refs)
    for q in refs:check(q)
    return dict(batch=BATCH,currentManifest=ref(ROOT/'3d-viewer/city/data/manifest.json'),currentSnapshot=SNAPSHOT,museumCapture=ref(MUSEUM_CAPTURE),starCapture=ref(STAR_CAPTURE),savedOriginalContacts=ref(ORIGINAL_CONTACTS),savedBASICContacts=ref(BASIC_CONTACTS),sources=sources,museumInterfaceFaceIDs=[12150,12151,12346,12347,12348,12349],summary=summary),refs

def load():
    p=read(PROPOSAL/'draft-pins.json');assert p['caller']==ref(Path(__file__))
    for q in p['codeRefs']+p['inputRefs']:check(q)
    data,refs=source_inputs();assert distinct_refs(p['inputRefs'])==distinct_refs(refs);return p,data

def owned():
    from run import connect,reservations
    from timed_owned_lease_pulse_v1_20261014 import TimedOwnedLeasePulse
    p,data=load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__));lease=read(LEASE);assert lease['resources']==sorted(RESOURCES) and reservations.owns(lease)and not DOC.exists()
    pulse=TimedOwnedLeasePulse(lambda:reservations.owns(lease),lambda:reservations.heartbeat(lease,ttl=3600));refs=distinct_refs(p['codeRefs']+p['inputRefs']+prep['evidenceRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'actual-readonly-preparation.json')])
    def fence():
        pulse(force=True)
        for q in distinct_refs(refs):check(q);pulse()
        assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT;pulse(force=True)
    def receipts():
        with connect()as db:
            db.execute('SET TRANSACTION READ ONLY')
            for name,job in RECEIPTS.items():assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(job,)).fetchone()==('complete',read(BASE/name/'result.json'))
            install=BASE/'government-xl-aqua-marine193086-original-installed-v1-20261014';assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(CURRENT_JOB,)).fetchone()==('complete',read(install/'result.json'))
    fence();receipts();assert not reservations.owns(read(FAILED_LOCAL/'reservation.json'))and not reservations.owns(read(FAILED_V2_LOCAL/'reservation.json'))and not reservations.owns(read(FAILED_V3_LOCAL/'reservation.json'))and not reservations.owns(read(FAILED_V4_LOCAL/'reservation.json'));DOC.mkdir();save(DOC/'preserved-V4-before-renderer-path-construction-failure.json',dict(terminalReleaseContextVerbatim=read(PROPOSAL/'V4-TERMINAL-RELEASE-CONTEXT.json'),emptyPriorDOCVerified=True,priorLeaseCurrentlyNotOwned=True,priorCodeAndPreparationRetained=True,noModelDefectOrAcceptanceInferred=True));save(DOC/'reused-successful-current-BASIC-exports-and-rejected-Star-runtime.json',dict(currentSuccessfulSourceAndBASICBindingsVerbatim=read(FAILED_V3_DOC/'actual-private-interface-preview.json')['scenarios'][0],allSixCurrentExportRefs=saved_export_refs(ROOT,read(FAILED_V3_DOC/'actual-private-interface-preview.json')['views'],ref),currentFirstScenarioNotRepeated=True,sourcePairDisplayIsNotCurrentVisibilityProof=True,rejectedOriginalStarLoaderDiagnosticsVerbatim=read(FAILED_V3_DOC/'actual-private-interface-preview.json')['loadingDiagnostics'],actualRejectedCommandVerbatim=read(FAILED_V3_DOC/'actual-render-log.json'),productionFootprintGuardUnchanged=True,StarIdentityAndRuntimeHeld=True,terminalReleaseContextVerbatim=read(PROPOSAL/'V3-TERMINAL-RELEASE-CONTEXT.json')));save(DOC/'preserved-V2-catalogue-setup-failure.json',dict(failedActualCommandVerbatim=read(FAILED_V2_DOC/'actual-render-log.json'),failedLoaderReportVerbatim=read(FAILED_V2_DOC/'actual-private-interface-preview.json'),terminalReleaseContextVerbatim=read(PROPOSAL/'V2-TERMINAL-RELEASE-CONTEXT.json'),priorLeaseCurrentlyNotOwned=True,noSourceOrModelDefectInferred=True));save(DOC/'preserved-V1-setup-failure.json',dict(failedActualCommandVerbatim=read(FAILED_DOC/'actual-render-log.json'),failedEmptyImageReportVerbatim=read(FAILED_DOC/'actual-private-interface-preview.json'),terminalReleaseContextVerbatim=read(PROPOSAL/'V1-TERMINAL-RELEASE-CONTEXT.json'),priorLeaseCurrentlyNotOwned=True,noSourceOrModelDefectInferred=True));save(DOC/'preview-input.json',{**data,'executionRefs':refs})
    save(DOC/'exact-historical-contact-and-current-binding.json.gz',dict(historicalOldManifestSHA256=read(CONTRACT)['currentManifestSHA256'],historicalFourViewCurrentBASICVerbatim=read(BASIC_CONTACTS),historicalFourViewOriginalStarVerbatim=read(ORIGINAL_CONTACTS),typedIdentityReceiptVerbatim=read(BASE/next(iter(RECEIPTS))/'result.json'),currentManifestSHA256=CURRENT,currentSnapshot=SNAPSHOT,currentCatalogueCount=6653,unchangedExactThreeCurrentForms=True,noOldMutableHashRelabelled=True,StarOriginalIdentityAndPlacementRemainHeld=True,sourceRoleAccepted=False,physicalAccepted=False,installationApproved=False))
    command=['node',str(RUNTIME),str(DOC.relative_to(ROOT))+'/'];r=subprocess.run(command,cwd=ROOT,capture_output=True,text=True);save(DOC/'actual-render-log.json',dict(command=command,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr));assert r.returncode==0
    report=read(DOC/'actual-private-interface-preview.json');assert not report['errors']and len(report['views'])==3 and report['isolatedOriginalSourceScene']and report['currentTerrainAndProxiesExcludedFromThisDisplay']and report['productionStarMatchedFootprintRejectionRetained']and len(report['actualOriginalSourceBindings'])==2
    from PIL import Image
    for view in report['views']:
        for field in ['cleanSolidImage','markedImage']:
            path=ROOT/view[field]
            with Image.open(path)as im:assert im.size==(1600,1100)
    refs=distinct_refs(refs+[ref(q)for q in DOC.rglob('*')if q.is_file()]);fence();receipts()
    freezer=HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py';spec=importlib.util.spec_from_file_location('heritage_interface_freezer',freezer);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.freeze(BATCH,'private-source-interface-opaque-comparison-no-role-or-physical-approval',[check(q)for q in refs],dict(uids=['landsd/165054:0','landsd/57455:0'],sourceOnly=True,newlyInstalled=0,physicalAccepted=False))
def main():
    if '--schema-only'in sys.argv:
        p,d=load();print(json.dumps(dict(passed=True,caller=ref(Path(__file__)),summary=d['summary'],currentManifestSHA256=CURRENT,currentCatalogueCount=6653,noGeometryCalculationRendererDBLease=True)));return
    if '--owned'in sys.argv:return owned()
    assert '--capture-private-source-interface-only'in sys.argv and not DOC.exists()and not LOCAL.exists();load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))
    from run import reservations
    claim=reservations.claim('heritage-private-interface-'+str(uuid.uuid4()),RESOURCES,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
    try:
        save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
