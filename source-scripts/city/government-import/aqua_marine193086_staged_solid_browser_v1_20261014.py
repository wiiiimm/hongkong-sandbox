"""ROOT-only ordinary publisher dry-run and solid staged browser; no apply/live."""
from pathlib import Path
import sys,json,subprocess,uuid,os
from urllib.request import urlopen
import aqua_marine193086_original_private_stage_v1_20261014 as stage
from run import ROOT,HERE,read,save,connect,reservations
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from timed_owned_lease_pulse_v1_20261014 import TimedOwnedLeasePulse
A=stage.A;ref,check,module=stage.ref,stage.check,stage.module
BATCH='government-xl-aqua-marine193086-staged-solid-browser-v1-20261014';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
def load(job):
    data,finite_result,p,adapted,refs=stage.load();r=read(stage.DOC/'result.json');v=read(stage.DOC/'ROOT-VERIFIED.json');assert r['jobId']==v['jobId']==job and v['exactNeonReadback']and v['allEvidenceHashesVerified']and v['leaseReleased'];s=read(stage.DOC/'stage.json');assert s['uids']==[A.prior.UID]and s['scriptChecksPassed']and s['remainingActualExistingViewerReasons']==[]and not s['rawStrictFoundationPassed']and not s['publication']and s['newlyInstalled']==0
    plan=read(stage.STAGE/'plan.json');assert plan['topLevelTerrainPatches']==[]and len(plan['areas'])==1;models=read(stage.STAGE/'catalogue.json')['models'];assert len(models)==1 and models[0]['uid']==A.prior.UID and models[0]['sha256']==A.prior.SOURCE_SHA and models[0]['supportDependencies']==models[0]['suppressesBuildingUids']==[];assert ref(stage.STAGE/models[0]['asset'])['sha256']==A.prior.SOURCE_SHA
    refs=distinct_refs(refs+r['evidenceRefs']+[ref(stage.DOC/'result.json'),ref(stage.DOC/'ROOT-VERIFIED.json'),ref(Path(__file__)),ref(HERE/'integrate.py'),ref(HERE/'publication_lock.py')])
    for q in refs:check(q)
    return data,r,adapted,refs

def schema_only(job):
    data,r,a,refs=load(job);return dict(passed=True,caller=ref(Path(__file__)),stageJob=job,stagedOnly=True,ordinaryPublisher=ref(stage.PUB),solidBrowser=ref(stage.BROWSER),scope=data[-1],uids=[A.prior.UID],terrainPlan=[],ROOTImageInspectionStillRequired=True,noPublisherBrowserDBLeaseWorker=True)

def report():
    r=module(HERE/'integrate.py','aqua_actual_staged_browser_contract').browser_verified(DOC/'staged-browser.json',{A.prior.UID});views=[v for v in r['views']if 'time'in v];assert len(views)==4
    for v in views:
        assert v['fullyFramed']and v['selectionClosed']and v['solidAppearance']and v['sourceSHA256']==A.prior.SOURCE_SHA and v['originalTriangles']==22735 and v['fallbackFaces']==0 and all(v['meshVisibility'])and not any(v['wireframeFlags'])and all(x==1 for x in v['materialOpacities']);foreign=v['retained'][A.prior.FOREIGN];assert foreign['loaded']and not foreign['detailedActive']and not foreign['hidden']
    assert r['unchangedTerrain'];return r

def owned(job):
    lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))and prep['stageJob']==job;data,r,adapted,refs=load(job);refs=distinct_refs(refs+prep['codeRefs']+prep['inputRefs']+prep['evidenceRefs']+[ref(PROPOSAL/'actual-readonly-preparation.json')]);pulse=TimedOwnedLeasePulse(lambda:reservations.owns(lease),lambda:reservations.heartbeat(lease,ttl=3600));before=(ROOT/'3d-viewer/city/data/manifest.json').read_bytes()
    def fence():
        pulse(force=True)
        for q in refs:check(q);pulse()
        assert (ROOT/'3d-viewer/city/data/manifest.json').read_bytes()==before and A.prior.digest(before)==A.prior.CURRENT;pulse(force=True)
    fence()
    with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(job,)).fetchone()==('complete',r)
    config=read(stage.STAGE/'browser-config.json')
    for url,expected in [('city/data/manifest.json',config['currentManifest']['sha256']),('city/app.js',config['servedApp']['sha256'])]:
        with urlopen('http://127.0.0.1:4176/'+url,timeout=20)as response:assert response.status==200 and A.prior.digest(response.read())==expected
    DOC.mkdir();config={**config,'doc':str(DOC.relative_to(ROOT))+'/'};save(LOCAL/'browser-config.json',config)
    def call(command):
        fence();p=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,env={**os.environ,'CHROME_PATH':os.environ.get('CHROME_PATH','/opt/google/chrome/chrome')});save(DOC/('command-'+str(len(list(DOC.glob('command-*.json')))).zfill(3)+'.json'),dict(command=command,exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr));fence();assert p.returncode==0
    # Existing source ownership publisher, no --apply, no terrain plan/overrides.
    call([sys.executable,str(stage.PUB),str((stage.STAGE/'plan.json').relative_to(ROOT)),'--receipt',str(LEASE),'--phase',BATCH])
    dry=ROOT/'docs/astra-city/model-integration-20260909'/BATCH/'publication-plan.json';d=read(dry);assert not d['published'];assert set(d['after'])=={'3d-viewer/city/data/manifest.json','3d-viewer/'+config['catalogueURL']};assert not d.get('topLevelTerrainPatches')and not d.get('estimatedBases')
    call(['node',str(stage.BROWSER),'staged',str((LOCAL/'browser-config.json').relative_to(ROOT))]);rpt=report()
    save(DOC/'staged-acceptance.json',dict(batch=BATCH,uids=[A.prior.UID],sourceSHA256=A.prior.SOURCE_SHA,passed=True,checksPassed=True,publication=False,newlyInstalled=0,sourceGeometryChanges=0,terrainGeometryChanges=0,rawStrictFoundationPassed=False,sourceApplicabilityVerbatim=adapted,sourceStage=ref(stage.DOC/'result.json'),ordinaryPublisherDryRun=ref(dry),stagedBrowser=ref(DOC/'staged-browser.json'),browserConfig=ref(LOCAL/'browser-config.json'),actualExportedViews=[dict(uid=v['uid'],width=v['width'],time=v['time'],image=ref(DOC/v['file']))for v in rpt['views']if 'time'in v],ROOTActuallyInspectedExportedImages=False,ROOTImageReviewAndLiveBrowserStillRequired=True,noInstallApproval=True))
    refs=distinct_refs(refs+[ref(q)for q in DOC.rglob('*')if q.is_file()]+[ref(LOCAL/'browser-config.json'),ref(dry)]);fence();module(A.prior.FREEZER,'aqua_staged_browser_freezer').freeze(BATCH,'unchanged-original-solid-staged-runtime-browser-no-live-install',[check(q)for q in refs],dict(uids=[A.prior.UID],sourceOnly=True,sourceGeometryChanges=0,terrainGeometryChanges=0,newlyInstalled=0,publication=False))
def main():
    job=sys.argv[sys.argv.index('--stage-job')+1]
    if '--schema-only'in sys.argv:print(json.dumps(schema_only(job)));return
    if '--owned'in sys.argv:
        from publication_lock import locked_publication
        with locked_publication(ROOT):return owned(job)
    assert '--staged-browser-only'in sys.argv and not DOC.exists()and not LOCAL.exists();data,*_=load(job);scope=data[-1];prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))and prep['stageJob']==job;resources=['building:'+u for u in scope]+['terrain-patch:'+u for u in scope]+['immutable-source-proof:'+BATCH];claim=reservations.claim('aqua-staged-browser-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
    try:save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--stage-job',job,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
