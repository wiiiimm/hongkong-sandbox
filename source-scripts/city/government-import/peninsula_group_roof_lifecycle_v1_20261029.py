"""Verify exact pair atomic activation and conditional OSM roof restoration privately."""
from pathlib import Path
import functools,http.server,json,os,subprocess,threading,uuid
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-peninsula-group-roof-lifecycle-v1-20261029';PREVIEW='government-xl-peninsula-group-roof-private-fixture-v1-20261029'
def main():
    out=BASE/BATCH;local=HERE/'local'/BATCH;assert not out.exists()and not local.exists();receipt,pins=authenticate(BASE/PREVIEW);assert receipt['previewOnly']and not receipt['installationApproved'];stage=HERE/'local'/PREVIEW;refs=[Path(__file__),BASE/PREVIEW/'result.json']
    for filename in ['catalogue.json','source-forms.json','browser-config-390.json']:
        p=stage/filename;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p)
    catalogue=read(stage/'catalogue.json');uids=sorted(m['uid']for m in catalogue['models']);assert uids==['landsd/266543:0','landsd/270876:0'];owner=next(m for m in catalogue['models']if m['uid']=='landsd/270876:0');roof='way/709674357:0';assert owner['suppressesBuildingUids']==[roof]
    assert all(m['activationGroup']==uids for m in catalogue['models'])and all(all(m[k]is False for k in ['publicationApproved','placementReviewed','identityReviewApproved','sourceIdentityReviewed'])for m in catalogue['models'])
    for m in catalogue['models']:
        p=stage/m['asset'];assert digest(p.read_bytes())==m['sha256'];refs.append(p)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';original=manifest.read_bytes();refs.append(manifest);cfg=read(stage/'browser-config-390.json');assert cfg['terrain']==[];cfg.update(diagnosticOnly=True,publication=False,expectedOwnerUid=owner['uid'],expectedSourceSHA256=owner['sha256'],expectedCanopyUid=roof)
    tool=HERE/'peninsula_group_roof_lifecycle_browser_v1_20261029.mjs';refs.append(tool);resources=['building:'+u for u in uids]+['source-form:'+roof,'server:127.0.0.1:4177'];claim=reservations.claim('peninsula-roof-lifecycle-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation'];server=None;thread=None
    try:
        out.mkdir();save(local/'reservation.json',json.loads(json.dumps(lease,default=str)));save(local/'browser-config.json',cfg)
        class Handler(http.server.SimpleHTTPRequestHandler):
            def log_message(self,*args):pass
            def copyfile(self,source,outputfile):
                try:super().copyfile(source,outputfile)
                except(BrokenPipeError,ConnectionResetError):pass
        server=http.server.ThreadingHTTPServer(('127.0.0.1',4177),functools.partial(Handler,directory=str(ROOT/'3d-viewer')));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        cmd=['node',str(tool),str((local/'browser-config.json').relative_to(ROOT)),str(out.relative_to(ROOT))]
        with(out/'browser.log').open('w')as log:process=subprocess.run(cmd,cwd=ROOT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},stdout=log,stderr=subprocess.STDOUT,timeout=3300)
        save(out/'command.json',dict(command=cmd,exitCode=process.returncode));assert manifest.read_bytes()==original and reservations.owns(lease);report=read(out/'report.json');passed=process.returncode==0 and report.get('passed')is True and not report['pageErrors']
        if passed:
            assert len(report['cases'])==3 and {(r['width'],r['failedUid'])for r in report['cases']}=={(1280,None),(390,uids[0]),(390,uids[1])}
            for case in report['cases']:
                assert not case['audit']['violations']and case['completeGroupEvicted']and case['baseOnlyRestoredCompleteGroup']
                assert sorted(r['uid']for r in case['sources'])==uids
                expected={'original-active','base-only','auto-restored','evicted-return-base-only'}|({'failed-download'}if case['failedUid']else set());assert {r['phase']for r in case['canopyLifecycle']}==expected
                for phase in case['canopyLifecycle']:
                    active=phase['phase']in ['original-active','auto-restored'];assert phase['ownerActive']is active and phase['basicCanopyVisible']is not active
        save(out/'summary.json',dict(uids=uids,passed=passed,sourceSHA256ByUid={m['uid']:m['sha256']for m in catalogue['models']},completeAtomicPairAndRoofLifecycleVerified=passed,installationApproved=False,publication=False,sourceGeometryChanges=0,sourcePoseChanges=0,qualification='Every rendered frame audited for complete pair activation; exact source bytes/faces, desktop success and individual mobile download failures, Base/Auto, eviction/return and conditional roof restoration tested. No source geometry edit, physical/identity/source-role/device-performance or publication approval.'))
        refs.extend([local/'browser-config.json',out/'report.json']);module('peninsula_roof_lifecycle_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-exact-Peninsula-pair-and-OSM-roof-complete-atomic-restoration-lifecycle',refs,read(out/'summary.json'))
    finally:
        if server is not None:server.shutdown();server.server_close();thread.join(timeout=10)
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
