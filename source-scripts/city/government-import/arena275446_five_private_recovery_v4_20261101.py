"""Recover remaining mobile atomic cases; retain exact completed browser phases.

No guard, asset, geometry, placement or production change. Complete-six-case
report explicitly records its verified prior desktop and fresh mobile origins.
"""
import argparse,copy,functools,http.server,os,shutil,subprocess,sys,threading,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-arena275446-after-palazzo-';BATCH=P+'five-private-preview-v4-20261101';PRIOR=P+'five-private-preview-v2-20261101'

def check_case(case,models):
    assert case['baseOnlyRestoredCompleteGroup']and case['completeGroupEvicted']and case['testWarmRetentionDisabledForEviction']
    assert case['audit']['frames']>0 and case['audit']['violations']==[] and case['audit']['transitions'][-1]['active']==[] and any(len(r['active'])==len(models)for r in case['audit']['transitions'])
    assert {r['uid']:(r['sha256'],r['triangles'])for r in case['sources']}=={m['uid']:(m['sha256'],m['triangles'])for m in models}and all(r['active']for r in case['sources'])
    assert case['capture']['fullyFramed']and case['capture']['withinUnchangedInitialLoadRanges']and all(r['distance']<=r['limit']for r in case['capture']['ranges'])
    if case['failedUid']:assert case['failureKeptAllBasics']

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--owned',action='store_true');a=ap.parse_args();out=BASE/BATCH;local=HERE/'local'/BATCH;lp=local/'reservation.json';planpath=BASE/(P+'five-current-ground-parallel-plan-v1-20261101.json');scopebatch=BASE/(P+'five-original-model-scope-v1-20261101');_,scopepins=authenticate(scopebatch);scopepath=scopebatch/'summary.json';assert digest(scopepath.read_bytes())==scopepins[str(scopepath.relative_to(ROOT))];wide=read(scopepath);assert wide['currentManifestSHA256']==digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes());scopepaths=[scopepath,scopebatch/'result.json'];scopeuids=set()
    for row in wide['rows']:
        scopeuids.update(r['uid']for r in row['nearbyNativeActors']);path=scopebatch/(row['uid'].split('/')[1]+'-forms.json.gz');assert digest(path.read_bytes())==scopepins[str(path.relative_to(ROOT))];scopepaths.append(path);scopeuids.update(r['building']['uid']for r in read(path))
    resources=sorted(set(read(planpath)['resources'])|{('building:'if u.startswith('landsd/')else'source-form:')+u for u in scopeuids}|{'server:127.0.0.1:4177'})
    assert set(resources)==set(read(HERE/'local'/PRIOR/'reservation.json')['resources']),'Complete terrain+source-only scope must match the earlier full browser lease'
    if not a.owned:
        assert not out.exists()and not local.exists();c=reservations.claim('kai-tak-private-recovery-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==set(resources)and not out.exists();prior=BASE/PRIOR;priorlocal=HERE/'local'/PRIOR;refs=[Path(__file__),planpath];before={}
    def pin(path):
        name=str(path.relative_to(ROOT));sha=digest(path.read_bytes());assert name not in before or before[name]==sha;before[name]=sha;refs.append(path);return read(path)
    for scopepath in scopepaths:pin(scopepath)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';mp=pin(manifest);_,rpins=authenticate(BASE/(P+'five-original-retained-parent-runtime-v2-20261101'));selpath=BASE/(P+'five-original-retained-parent-runtime-v2-20261101')/'selection.json.gz';assert digest(selpath.read_bytes())==rpins[str(selpath.relative_to(ROOT))];selection=pin(selpath);assert before[str(manifest.relative_to(ROOT))]==selection['manifestSHA256'];refs.append(BASE/(P+'five-original-retained-parent-runtime-v2-20261101')/'result.json')
    stage=priorlocal/'atomic';cat=pin(stage/'catalogue.json');models=cat['models'];uids=sorted(m['uid']for m in models);assert len(uids)==5 and {r['uid']:r['sourceSHA256']for r in selection['rows']}=={m['uid']:m['sha256']for m in models};assert all(m['activationGroup']==uids and all(m[k]is False for k in ['publicationApproved','placementReviewed','identityReviewApproved','sourceIdentityReviewed'])for m in models)
    forms=pin(stage/'source-forms.json');assert {r['uid']:r for r in forms}=={r['uid']:r['source']['building']for r in selection['rows']}
    for m in models:
        asset=stage/m['asset'];assert digest(asset.read_bytes())==m['sha256'];before[str(asset.relative_to(ROOT))]=m['sha256'];refs.append(asset)
    cfg=pin(priorlocal/'atomic-config.json');assert cfg['stage']==str(stage.relative_to(ROOT))+'/' and cfg['diagnosticOnly']and cfg['publication']is False and not cfg['privateSourceBoundTileOverlays']
    for t in cfg['terrain']:
        path=ROOT/t['source'];assert digest(path.read_bytes())==t['sha256'];before[str(path.relative_to(ROOT))]=t['sha256'];refs.append(path)
    oldatomic=pin(prior/'atomic-browser/report.json');assert oldatomic['pageErrors']==[] and len(oldatomic['cases'])==1;desktop=oldatomic['cases'][0];assert desktop['width']==1280 and desktop['failedUid']is None;check_case(desktop,models)
    assert cfg['atomicCaptureDirectionByViewport']['1280']==[-1,1.6,1]
    out.mkdir();closure=HERE/'private_viewer_runtime_closure_v1_20261028.mjs';tool=HERE/'model_atomic_lifecycle_browser_v4_20261101.mjs';refs.extend([closure,tool,HERE/'model_atomic_lifecycle_browser_v3_20261101.mjs',HERE/'arena275446_five_private_preview_v1_20261101.py',HERE/'arena275446_five_private_preview_v2_20261101.py']);cp=out/'runtime-input-closure.json';subprocess.run(['node',str(closure),'capture',str(cp.relative_to(ROOT))],cwd=ROOT,check=True);current=pin(cp);oldclosure=pin(prior/'runtime-input-closure.json');assert current['inputHashes']==oldclosure['inputHashes'];subprocess.run(['node',str(closure),'verify',str((prior/'runtime-input-closure.json').relative_to(ROOT))],cwd=ROOT,check=True)
    for name,sha in current['inputHashes'].items():assert digest((ROOT/name).read_bytes())==sha;before[name]=sha;refs.append(ROOT/name)
    for width in [1280,390]:
        report=pin(prior/str(width)/'staged-browser.json');assert report['passed']and report['errors']==[] and len(report['retainedNativeOwnViews'])==2
        views=[r for r in report['views']if r.get('file')];assert {(r['uid'],r['width'],r['time'])for r in views}=={(u,width,h)for u in uids for h in ['15:00','22:00']}
        for r in views:assert r['sourceSHA256']==next(m['sha256']for m in models if m['uid']==r['uid'])and r['active']and r['fullyFramed']and r['pick']==r['uid']and r['collision']==r['uid']and r['fallbackFaces']==0 and all(r['meshVisibility'])and not any(r['wireframeFlags'])and all(o==1 for o in r['materialOpacities'])
        if width==390:assert pin(prior/'command-390.json')['exitCode']==0 and len([r for r in report['views']if r.get('phase')=='failed-download'])==5
        shutil.copytree(prior/str(width),out/str(width))
        for path in (prior/str(width)).iterdir():assert digest(path.read_bytes())==digest((out/str(width)/path.name).read_bytes());before[str(path.relative_to(ROOT))]=digest(path.read_bytes());refs.append(path)
    pin(prior/'desktop-reuse.json');pin(priorlocal/'browser-config-1280.json');pin(priorlocal/'browser-config-390.json')
    # The single retained native is verified against its current exact catalogue,
    # immutable asset and frozen current entry, independently of candidate claims.
    _,npins=authenticate(BASE/(P+'five-current-native-contacts-v1-20261101'));npath=BASE/(P+'five-current-native-contacts-v1-20261101')/'summary.json';assert digest(npath.read_bytes())==npins[str(npath.relative_to(ROOT))];native=pin(npath)['rows'][0]
    found=[]
    for url in mp['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url
        for m in read(path)['models']:
            if m['uid']==native['nativeUid']:found.append((m,path))
    assert len(found)==1 and found[0][0]==native['rawCurrentNativeEntry'];entry,catpath=found[0];pin(catpath);asset=catpath.parent/entry['asset'];assert digest(asset.read_bytes())==entry['sha256']==native['nativeSHA256'];before[str(asset.relative_to(ROOT))]=entry['sha256'];refs.append(asset)
    cfg=copy.deepcopy(cfg);cfg['viewportWidths']=[390];cfg['atomicCaptureDirectionByViewport']['390']=[0,1.6,-1];configpath=local/'atomic-config.json';save(configpath,cfg);refs.append(configpath)
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
        def copyfile(self,source,outputfile):
            try:super().copyfile(source,outputfile)
            except(BrokenPipeError,ConnectionResetError):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',4177),functools.partial(Handler,directory=str(ROOT/'3d-viewer')));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        with(out/'mobile-atomic.log').open('w')as log:result=subprocess.run(['node',str(tool),str(configpath.relative_to(ROOT)),str((out/'mobile-atomic').relative_to(ROOT))],cwd=ROOT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},stdout=log,stderr=subprocess.STDOUT,timeout=3300)
        mobile=read(out/'mobile-atomic/report.json');assert result.returncode==0 and mobile['passed']and mobile['pageErrors']==[] and mobile['testedViewportWidths']==[390]and len(mobile['cases'])==5 and {r['failedUid']for r in mobile['cases']}==set(uids)
        for case in mobile['cases']:check_case(case,models)
        combined=dict(diagnosticOnly=True,physicalAcceptance=False,installationApproved=False,publication=False,performanceAcceptance=False,passed=True,pageErrors=[],cases=[desktop,*mobile['cases']],composedFromVerifiedCompletedCases=True,desktopExecutedAgain=False,mobileExecutedAgain=True,originalDesktopReport=dict(path=str((prior/'atomic-browser/report.json').relative_to(ROOT)),sha256=before[str((prior/'atomic-browser/report.json').relative_to(ROOT))]),freshMobileReport=dict(path=str((out/'mobile-atomic/report.json').relative_to(ROOT)),sha256=digest((out/'mobile-atomic/report.json').read_bytes())))
        assert {(r['width'],r['failedUid'])for r in combined['cases']}=={(1280,None)}|{(390,u)for u in uids};save(out/'atomic-browser/report.json',combined)
        src=prior/'atomic-browser/1280-success.png';dest=out/'atomic-browser'/src.name;shutil.copyfile(src,dest);assert digest(src.read_bytes())==digest(dest.read_bytes());before[str(src.relative_to(ROOT))]=digest(src.read_bytes());refs.append(src)
        for name,sha in before.items():assert digest((ROOT/name).read_bytes())==sha,name
        assert reservations.owns(lease);subprocess.run(['node',str(closure),'verify',str(cp.relative_to(ROOT))],cwd=ROOT,check=True)
        summary=dict(diagnosticOnly=True,uids=uids,sourceSHA256ByUid={m['uid']:m['sha256']for m in models},leaseResources=resources,testedStage=str(stage.relative_to(ROOT))+'/',testedAtomicConfig=str(configpath.relative_to(ROOT)),desktopMobileBrowserPassed=True,allBrowserDiagnosticsPassed=True,atomicCases=6,desktopAndIndividualMobileReusedExactly=True,fiveAtomicMobileCasesExecutedHere=True,allAtomicCapturesInsideUnchangedRanges=True,sourceGeometryChanges=0,sourcePoseChanges=0,qualifiedForLiveVerification=False,physicalAcceptance=False,visualAcceptance=False,installationApproved=False,publication=False,qualification=__doc__+' Complete24individual day/night/retained-native exports retain exact completed prior bytes and viewer inputs. Completed desktop atomic case retains every source/hash/framing/range/Base-only/eviction/audit assertion. Five cold-context mobile deny/retry cases execute on unchanged exact atomic catalogue using a full-bounds north-facing camera; complete six-case aggregate preserves both evidence origins. No runtime limit or functional assertion is relaxed.')
        save(out/'summary.json',summary);module('kai_tak_private_recovery_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-five-original-complete-browser-and-six-atomic-case-recovery',refs,summary)
    finally:server.shutdown();server.server_close();thread.join(timeout=5)

if __name__=='__main__':main()
