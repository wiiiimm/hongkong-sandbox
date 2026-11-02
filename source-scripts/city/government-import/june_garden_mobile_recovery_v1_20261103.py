"""Fresh full mobile checks plus exact reuse of authenticated completed desktop.

Uses existing V20 visible-camera and ordinary selected-actor capture support.
No production, geometry, budget, ownership or placement changes. Desktop flat
captures and failed mobile evidence remain recorded; this grants no approval.
"""
import argparse,os,shutil,socket,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from observed_reserved_runner_v2_20261103 import execute_reserved
from june_garden_publisher_hooks_v1_20261103 import SOURCES

BASE=ROOT/'docs/astra-city/government-import';PORT=4197
ARCHIVE='government-xl-june-garden-desktop-complete-mobile-held-v2-20261103'
BATCH='government-xl-june-garden-mobile-recovery-v1-20261103'
PLAN=BASE/'government-xl-tower3-june-garden-six-originals-current-v1-20261102-plan.json'


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--owned',action='store_true');a=ap.parse_args()
    archive,pins=authenticate(BASE/ARCHIVE);assert archive['desktopDiagnosticsPassed'] and not archive['mobileDiagnosticsPassed']
    assert archive['sourceSHA256ByUid']==SOURCES and len(archive['retainedUids'])==69
    assert digest(PLAN.read_bytes())==pins[str(PLAN.relative_to(ROOT))]
    resources=sorted(set(read(PLAN)['resources'])|{f'server:127.0.0.1:{PORT}'})
    out,local=BASE/BATCH,HERE/'local'/BATCH;lp=local/'reservation.json'
    if not a.owned:
        assert not out.exists() and not local.exists()
        c=reservations.claim('june-mobile-recovery-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease) and set(lease['resources'])==set(resources)
    refs=[Path(__file__),PLAN,BASE/ARCHIVE/'result.json',BASE/ARCHIVE/'summary.json',
        HERE/'ronsdale_three_live_browser_v20_20261027.mjs',HERE/'source_pixel_visibility_witness_v1_20261027.mjs',
        HERE/'observed_reserved_runner_v2_20261103.py',HERE/'reservation_action_diagnostic_v1_20261103.py']
    def take(path):
        assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);return read(path)
    old=archive['sourceBrowserBatch'];prior=HERE/'local'/old
    catalogue=take(prior/'catalogue.json');forms=take(prior/'source-forms.json');config=take(prior/'config.json')
    assert {m['uid']:m['sha256'] for m in catalogue['models']}==SOURCES
    save(local/'catalogue.json',catalogue);save(local/'source-forms.json',forms)
    for m in catalogue['models']:
        asset=prior/m['asset'];assert digest(asset.read_bytes())==pins[str(asset.relative_to(ROOT))]==m['sha256']
        refs.append(asset);target=local/m['asset'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(asset,target)
    out.mkdir()
    for name in ['complete-unapproved-source-entries.json','source-tile-provenance.json']:
        path=BASE/old/name;take(path);shutil.copyfile(path,out/name);refs.append(out/name)
    original=ROOT/archive['desktopReport']['path'];desktop=take(original)
    assert digest(original.read_bytes())==archive['desktopReport']['sha256'] and desktop['passed'] and not desktop['errors']
    copied=out/'1280';copied.mkdir()
    for row in [*desktop['views'],*desktop['retainedNativeOwnViews']]:
        path=original.parent/row['file'];assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))]
        target=copied/row['file'];shutil.copyfile(path,target);assert digest(target.read_bytes())==digest(path.read_bytes());refs.extend([path,target])
    shutil.copyfile(original,copied/'staged-browser.json');refs.append(copied/'staged-browser.json')
    config.update(stage=str(local.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',
        viewerURL=f'http://127.0.0.1:{PORT}/city.html',doc=str((out/'390').relative_to(ROOT))+'/',viewportWidths=[390],
        autoVisibleCamera=True,keepSelectedForRetainedCapture=['landsd/160070:0'])
    assert set(config['additionalRetainedUids'])==set(archive['retainedUids']) and not config['failureTestUids']
    cfg=local/'config.json';save(cfg,config);refs.extend([cfg,local/'catalogue.json',local/'source-forms.json'])
    for p,sha in pins.items():assert digest((ROOT/p).read_bytes())==sha
    bound={str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in refs}
    with socket.socket() as probe:probe.bind(('127.0.0.1',PORT))
    server=None
    with (out/'server.log').open('w') as serverlog,(out/'browser.log').open('w') as browserlog:
        try:
            server=subprocess.Popen([sys.executable,'-m','http.server',str(PORT),'--bind','127.0.0.1','--directory',str(ROOT/'3d-viewer')],stdout=serverlog,stderr=subprocess.STDOUT)
            import time,urllib.request
            for attempt in range(50):
                assert server.poll() is None
                try:
                    with urllib.request.urlopen(config['viewerURL'],timeout=1) as r:assert r.status==200
                    break
                except OSError:time.sleep(.1)
            else:raise RuntimeError('Own diagnostic server did not become ready')
            subprocess.run(['node',str(HERE/'ronsdale_three_live_browser_v20_20261027.mjs'),'staged',str(cfg.relative_to(ROOT))],cwd=ROOT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},stdout=browserlog,stderr=subprocess.STDOUT,check=True,timeout=7200)
        finally:
            if server is not None:
                server.terminate()
                try:server.wait(timeout=10)
                except subprocess.TimeoutExpired:server.kill();server.wait(timeout=10)
    reportpath=out/'390/staged-browser.json';report=read(reportpath)
    assert report['passed'] and not report['errors'] and len(report['views'])==12
    assert {(r['uid'],r['time']) for r in report['views']}=={(u,t) for u in SOURCES for t in ['15:00','22:00']}
    own=report['retainedNativeOwnViews'];assert len(own)==138
    assert {(r['uid'],r['time']) for r in own}=={(u,t) for u in archive['retainedUids'] for t in ['15:00','22:00']}
    for r in [*report['views'],*own]:
        assert r['active'] and r['visible'] and r['fallbackFaces']==0 and r['sourcePixelVisibility']['visiblePixels']>=32
    refs.extend([reportpath,out/'browser.log',out/'server.log'])
    for path,sha in bound.items():assert digest((ROOT/path).read_bytes())==sha
    for path,sha in pins.items():assert digest((ROOT/path).read_bytes())==sha
    assert reservations.owns(lease)
    refs.extend(out.rglob('*.png'))
    reused=dict(archiveBatch=ARCHIVE,archiveResultSHA256=digest((BASE/ARCHIVE/'result.json').read_bytes()),
        originalReport=archive['desktopReport'],exactCurrentInputRebind=True,sourceViews=12,retainedViews=138,
        desktopFlatCapturesStillNeedSupplement=True,originalFilesUnchanged=True)
    save(out/'reused-desktop-evidence.json',reused);refs.append(out/'reused-desktop-evidence.json')
    summary=dict(uids=sorted(SOURCES),sourceSHA256ByUid=SOURCES,passed=True,retainedNativeActors=69,
        desktopDiagnosticsPassed=True,mobileDiagnosticsPassed=True,reusedDesktopEvidence=reused,
        sourceGeometryChanges=0,sourcePoseChanges=0,productionChanges=0,newlyInstalled=0,
        physicalAcceptance=False,visualAcceptance=False,installationApproved=False,publication=False,qualification=__doc__)
    save(out/'summary.json',summary)
    module('june_mobile_recovery_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'completed-desktop-reused-exact-inputs-full-mobile-source-pixel-diagnostic',refs,summary)


if __name__=='__main__':main()
