"""Resume only lifecycle after verified V3 visual commands; no repeated exports."""
import argparse,functools,http.server,json,subprocess,sys,threading,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
P='government-xl-academic309823-after-harbour-'
PREVIEW=P+'joint-foundation-private-preview-v3-20261102'
BATCH=P+'joint-foundation-lifecycle-recovery-v2-20261102'

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--owned',action='store_true');a=ap.parse_args()
    out=BASE/BATCH;local=HERE/'local'/BATCH;assert not out.exists()
    refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    scope=P+'repaired-floor-retention-scope-v1-20261102';forms=take(scope,BASE/scope/'form-obligations.json.gz');sr=take(scope,BASE/scope/'scope.json')
    resources={('building:'if b['uid'].startswith('landsd/')else'source-form:')+b['uid']for b in forms};resources.update('building:'+u for u in sr['uids']);resources.update('terrain:'+r['url']for r in sr['terrainContacts']);resources.update(['terrain:city/data/terrain.json','server:127.0.0.1:4177'])
    leasefile=local/'reservation.json'
    if not a.owned:
        assert not local.exists();claim=reservations.claim('hkust-resume-lifecycle-'+str(uuid.uuid4()),sorted(resources),batch=BATCH,ttl=3600);assert claim['ok'],claim
        return execute_reserved(claim['reservation'],leasefile,[sys.executable,__file__,'--owned'])
    lease=read(leasefile);assert reservations.owns(lease)and set(lease['resources'])==resources
    runtime=P+'repaired-floor-runtime-v1-20261102';selection=take(runtime,BASE/runtime/'selection.json.gz')
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    sources={r['uid']:r['sourceSHA256']for r in selection['rows']};assert set(sources)=={'landsd/309823:0','landsd/309829:0','landsd/336320:0'}
    stage=HERE/'local'/PREVIEW;doc=BASE/PREVIEW;cat=read(stage/'catalogue.json');assert {m['uid']:m['sha256']for m in cat['models']}==sources
    for m in cat['models']:
        assert m['activationGroup']==sorted(sources)and m['proceduralWindows']is False
        assert all(m[k]is False for k in ['publicationApproved','placementReviewed','identityReviewApproved','sourceIdentityReviewed'])
        asset=stage/m['asset'];assert digest(asset.read_bytes())==sources[m['uid']];refs.append(asset)
    cfg=read(stage/'browser-config-390.json');assert cfg['diagnosticOnly']is True and cfg['failureTestUids']==[] and cfg['jointUids']==list(sources)
    assert cfg['additionalRetainedUids']==['landsd/26949:0']and not cfg.get('estimatedBaseUpdates')
    for overlay in cfg['privateFoundationTileOverlays']:
        tile=ROOT/'3d-viewer'/overlay['tile'];assert digest(tile.read_bytes())==overlay['tileSHA256'];refs.append(tile)
        for u in overlay['updates']:
            assert next(b for b in read(tile)['buildings']if b['uid']==u['uid'])==u['before']
    collision=take(P+'joint-basic-collision-v1-20261102',BASE/(P+'joint-basic-collision-v1-20261102')/'input.json')
    expected={p['uid']:(p['building'],p['foundationBase'])for p in collision['proposals']}
    assert {u['uid']:(u['before'],u['foundationBase'])for o in cfg['privateFoundationTileOverlays']for u in o['updates']}==expected
    terrain=cfg['terrain'];assert len(terrain)==1
    ground=ROOT/terrain[0]['source'];assert digest(ground.read_bytes())==terrain[0]['sha256'];refs.append(ground)
    boundterrain=take(P+'bounded-floor-v2-20261102',BASE/(P+'bounded-floor-v2-20261102')/'summary.json')
    assert terrain[0]['replacesMany']==boundterrain['replacedNativeTerrain']and terrain[0]['sha256']==boundterrain['candidate']['sha256']
    exports=[]
    for width in [1280,390]:
        assert read(doc/f'command-{width}.json')['exitCode']==0
        report=read(doc/str(width)/'staged-browser.json');assert report['passed']and not report['errors']
        assert read(stage/f'browser-config-{width}.json')['privateFoundationTileOverlays']==cfg['privateFoundationTileOverlays']
        images=list((doc/str(width)).glob('*.png'));assert len(images)==8
        exports.extend(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in images)
    refs.extend(p for p in doc.rglob('*')if p.is_file());refs.extend(p for p in stage.rglob('*')if p.is_file()and p.name!='reservation.json')
    tool=HERE/'original_foundation_atomic_lifecycle_v2_20261102.mjs'
    refs.extend(HERE/n for n in ['hkust_current_foundation_private_preview_v3_20261102.py','original_foundation_private_browser_v2_20261102.mjs','original_foundation_atomic_lifecycle_v2_20261102.mjs','private_foundation_tile_routes_v1_20261102.mjs','qualified_source_bound_tile_routes_v1_20261029.mjs','source_bound_basic_lifecycle_checks_v1_20261029.mjs','elegant_live_fallback_checks_v1_20261028.mjs'])
    save(out/'reused-visual-exports.json',dict(images=exports,desktopAndMobileCommandsPassed=True,visualAcceptance=False,qualification='Exact complete V3 exports reused after its post-view duplicate-keyword orchestration failure; no claim of image inspection.'))
    collision_report=take(P+'joint-basic-collision-v1-20261102',BASE/(P+'joint-basic-collision-v1-20261102')/'collision.json')
    production_hashes={p.removeprefix('3d-viewer/'):h for p,h in collision_report['inputHashes'].items()if p.startswith('3d-viewer/city/')and p.endswith('.js')}
    assert production_hashes
    refs.append(HERE/'original_foundation_group_lifecycle_checks_v1_20261102.mjs')
    path=local/'config.json';save(path,{**cfg,'diagnosticOnly':True,'publication':False,'privateSourceBoundTileOverlays':[],'productionGeometryInputHashes':production_hashes});refs.append(path)
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
        def copyfile(self,source,outputfile):
            try:super().copyfile(source,outputfile)
            except(BrokenPipeError,ConnectionResetError):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',4177),functools.partial(Handler,directory=str(ROOT/'3d-viewer')));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        with(out/'worker.log').open('w')as log:subprocess.run(['node',str(tool),str(path.relative_to(ROOT)),str((out/'lifecycle').relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=3600)
        report=read(out/'lifecycle/report.json');assert report['passed']and len(report['cases'])==4 and not report['pageErrors']
        assert {r['failedUid']for r in report['cases']if r['width']==390}==set(sources)
        assert reservations.owns(lease)and digest(manifest.read_bytes())==selection['manifestSHA256']
        result=dict(uids=sorted(sources),sourceSHA256ByUid=sources,desktopMobileDayNightCommandsPassed=True,actualAtomicLifecyclePassed=True,lifecycleCases=4,reusedVisualExports=len(exports),visualAcceptance=False,physicalAcceptance=False,installationApproved=False,publication=False,sourceGeometryChanges=0,sourcePoseChanges=0,qualification='V3 exact successful visual commands reused and existing per-peer atomic lifecycle independently completed under fresh complete leases. Original source BASIC fallback fields are unchanged; no source-bound continuation hints are proposed. Image inspection, bounded physical review and fenced publication remain separate.')
        save(out/'summary.json',result);module('hkust_lifecycle_resume_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-current-original-visual-command-reuse-and-complete-atomic-lifecycle',list(dict.fromkeys(refs)),result)
    finally:server.shutdown();server.server_close();thread.join(timeout=10)
if __name__=='__main__':main()
