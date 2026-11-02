"""Camera-only supplemental source-pixel evidence after full browser completion.

Reuses the existing V20 visibility witness. No geometry, production, source
placement, residency or acceptance changes; failed original views are retained.
"""
import argparse,os,socket,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from observed_reserved_runner_v2_20261103 import execute_reserved
from june_garden_publisher_hooks_v1_20261103 import SOURCES,P

BASE=ROOT/'docs/astra-city/government-import';PORT=4197


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ['batch','parent','resources-plan']:ap.add_argument('--'+name,required=True)
    ap.add_argument('--uid',action='append',required=True);ap.add_argument('--owned',action='store_true');a=ap.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n for n in [a.batch,a.parent])
    wanted=set(a.uid);assert len(wanted)==len(a.uid) and not wanted&set(SOURCES)
    out,local=BASE/a.batch,HERE/'local'/a.batch;lp=local/'reservation.json'
    pp=(ROOT/a.resources_plan).resolve();assert pp.is_relative_to(BASE)
    resources=sorted(set(read(pp)['resources'])|{f'server:127.0.0.1:{PORT}'})
    assert {'building:'+u for u in wanted|set(SOURCES)}<=set(resources)
    # A completed frozen parent is mandatory; never run alongside its live lease.
    parent,pins=authenticate(BASE/a.parent)
    supporting=[]
    if parent.get('reusedDesktopEvidence'):
        reuse=parent['reusedDesktopEvidence'];directory=BASE/reuse['archiveBatch']
        assert digest((directory/'result.json').read_bytes())==reuse['archiveResultSHA256']
        archived,oldpins=authenticate(directory);assert archived['sourceSHA256ByUid']==SOURCES
        for path,sha in oldpins.items():
            assert path not in pins or pins[path]==sha
            assert digest((ROOT/path).read_bytes())==sha; pins[path]=sha
        supporting.extend([directory/'result.json',directory/'summary.json'])
    assert digest(pp.read_bytes())==pins[str(pp.relative_to(ROOT))]
    assert parent['passed'] and parent['sourceSHA256ByUid']==SOURCES and parent['retainedNativeActors']==69
    if not a.owned:
        assert not out.exists() and not local.exists()
        c=reservations.claim('june-retained-camera-'+str(uuid.uuid4()),resources,batch=a.batch,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
    lease=read(lp);assert reservations.owns(lease) and set(lease['resources'])==set(resources)
    refs=[*supporting,Path(__file__),pp,BASE/a.parent/'result.json',HERE/'ronsdale_three_live_browser_v20_20261027.mjs',HERE/'source_pixel_visibility_witness_v1_20261027.mjs',HERE/'observed_reserved_runner_v2_20261103.py',HERE/'reservation_action_diagnostic_v1_20261103.py']
    def take(path):
        assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);return read(path)
    prior=HERE/'local'/a.parent
    catalogue=take(prior/'catalogue.json');forms=take(prior/'source-forms.json');config=take(prior/'config.json')
    assert {m['uid']:m['sha256'] for m in catalogue['models']}==SOURCES
    expected={}
    for width in [1280,390]:
        report=take(BASE/a.parent/str(width)/'staged-browser.json');assert report['passed'] and not report['errors']
        rows={r['uid']:r['sourceSHA256'] for r in report['retainedNativeOwnViews']}
        assert len(rows)==69 and wanted<=set(rows)
        assert {'building:'+u for u in rows}<=set(resources)
        for uid in wanted:
            assert uid not in expected or expected[uid]==rows[uid];expected[uid]=rows[uid]
    manifest=ROOT/'3d-viewer/city/data/manifest.json';take(manifest)
    found=set()
    for url in read(manifest)['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url
        entries=take(path)['models']
        for m in entries:
            if m['uid'] not in wanted:continue
            assert m['uid'] not in found and m['sha256']==expected[m['uid']]
            asset=path.parent/m['asset'];assert digest(asset.read_bytes())==m['sha256'];refs.append(asset);found.add(m['uid'])
    assert found==wanted
    save(local/'catalogue.json',catalogue);save(local/'source-forms.json',forms)
    for m in catalogue['models']:
        asset=prior/m['asset'];assert digest(asset.read_bytes())==SOURCES[m['uid']];refs.append(asset)
        target=local/m['asset'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(asset.read_bytes())
    assert not config['availabilityOverlays'] and not config['catalogueReplacements']
    for t in config['terrain']:
        path=ROOT/t['source'];assert digest(path.read_bytes())==t['sha256'];refs.append(path)
    for name in ['app.js','official-models.js','streaming.js','model-group-lifecycle.js','model-activation-groups.js','model-support.js','official-model-assets.js','tile-cache.js','model-variants.js','model-byte-cache.js']:
        take(ROOT/'3d-viewer/city'/name)
    config.update(stage=str(local.relative_to(ROOT))+'/',viewerURL=f'http://127.0.0.1:{PORT}/city.html',
        additionalRetainedUids=sorted(wanted),browserUids=[P],failureTestUids=[],autoVisibleCamera=True)
    bound={str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in refs}
    with socket.socket() as probe:probe.bind(('127.0.0.1',PORT))
    out.mkdir();server=None
    with (out/'server.log').open('w') as serverlog:
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
            for width in [1280,390]:
                path=local/f'config-{width}.json';save(path,dict(config,viewportWidths=[width],doc=str((out/str(width)).relative_to(ROOT))+'/',keepSelectedForRetainedCapture=['landsd/160070:0'] if width==390 and 'landsd/160070:0' in wanted else []));refs.append(path)
                log=out/f'browser-{width}.log'
                with log.open('w') as output:
                    subprocess.run(['node',str(HERE/'ronsdale_three_live_browser_v20_20261027.mjs'),'staged',str(path.relative_to(ROOT))],cwd=ROOT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},stdout=output,stderr=subprocess.STDOUT,check=True,timeout=3600)
                reportpath=out/str(width)/'staged-browser.json';report=read(reportpath)
                assert report['passed'] and not report['errors'] and len(report['views'])==2
                assert {(r['uid'],r['time']) for r in report['views']}=={(P,t) for t in ['15:00','22:00']}
                own=report['retainedNativeOwnViews'];assert len(own)==2*len(wanted)
                assert {(r['uid'],r['time']) for r in own}=={(u,t) for u in wanted for t in ['15:00','22:00']}
                for r in [*report['views'],*own]:
                    assert r['sourcePixelVisibility']['visiblePixels']>=32 and r['active'] and r['visible'] and r['fallbackFaces']==0
                    assert r['sourceSHA256']==(SOURCES if r['uid'] in SOURCES else expected)[r['uid']]
                refs.extend([reportpath,log]);print('Supplement viewport passed',width,flush=True)
        finally:
            if server is not None:
                server.terminate()
                try:server.wait(timeout=10)
                except subprocess.TimeoutExpired:server.kill();server.wait(timeout=10)
    for path,sha in bound.items():assert digest((ROOT/path).read_bytes())==sha
    for path,sha in pins.items():assert digest((ROOT/path).read_bytes())==sha
    assert reservations.owns(lease)
    refs.extend(out.rglob('*.png'))
    summary=dict(uids=sorted(SOURCES),sourceSHA256ByUid=SOURCES,parentBrowserBatch=a.parent,
        retainedUids=sorted(wanted),retainedSourceSHA256ByUid=expected,desktopMobileDiagnosticsPassed=True,
        actualSourcePixelsRequired=True,normalSelectedActorCaptureSupported=True,cameraOnlyChanges=True,sourceGeometryChanges=0,sourcePoseChanges=0,
        physicalAcceptance=False,visualAcceptance=False,installationApproved=False,publication=False)
    save(out/'summary.json',summary)
    module('june_retained_camera_supplement_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'camera-only-retained-original-visibility-supplement',refs,summary)


if __name__=='__main__':main()
