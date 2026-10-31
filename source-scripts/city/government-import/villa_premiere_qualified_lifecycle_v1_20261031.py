"""Verify exact publisher-qualified originals and canopy tile bytes privately."""
import argparse,copy,functools,http.server,os,subprocess,sys,threading,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-villa-premiere89917-';FIXTURE=P+'qualified-stage-v3-20261031';BATCH=P+'qualified-stage-lifecycle-v1-20261031'

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--owned',action='store_true');a=ap.parse_args();out=BASE/BATCH;local=HERE/'local'/BATCH;lp=local/'reservation.json';assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,p):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    summary=take(FIXTURE,BASE/FIXTURE/'summary.json');assert summary['canonicalFullPublisherDryRunPassed']and summary['qualifiedExactStage'];resources=sorted(set(summary['leaseResources'])|{'server:127.0.0.1:4177'})
    if not a.owned:
        assert not local.exists();claim=reservations.claim('villa-qualified-lifecycle-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim
        return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(resources)==set(lease['resources']);stage=HERE/'accepted'/FIXTURE;cat=take(FIXTURE,stage/'catalogue.json');cfg=take(FIXTURE,stage/'live-browser-config.json');plan=take(FIXTURE,stage/'plan.json');report=take(FIXTURE,BASE/FIXTURE/'publisher-dry-run/publication-plan.json')
    previous=P+'five-atomic-canopy-lifecycle-v2-20261031';old=take(previous,HERE/'local'/previous/'catalogue.json');keys={'sourceIdentityReviewed','identityReviewApproved','placementReviewed','publicationApproved','sourceIdentityReview','sourceFunctionalApplicability','placementReview','aiGeometryModelling','sourceEvidenceInterpretationUsedAI'}
    assert len(cat['models'])==len(old['models'])==5
    for before,after in zip(old['models'],cat['models']):
        assert {k:v for k,v in before.items()if k not in keys}=={k:v for k,v in after.items()if k not in keys};assert all(after[k]is True for k in ['sourceIdentityReviewed','identityReviewApproved','placementReviewed','publicationApproved'])
        path=stage/after['asset'];assert digest(path.read_bytes())==after['sha256'];refs.append(path)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();assert digest(before)==summary['currentManifest']['sha256'];refs.append(manifest)
    canonical=module('villa_qualified_publisher_encoding',HERE.parent/'island-detail-integration/publish.py');edits={};stager=module('villa_qualified_canopy_stager',HERE.parent/'island-detail-integration/illustrative_foundations.py');staged_manifest=copy.deepcopy(read(manifest));stager.stage_illustrative_foundations(ROOT,plan,staged_manifest,edits,{},read,lambda p:digest(p.read_bytes()),canonical.encoded)
    assert len(plan['illustrativeFoundations'])==1 and len(cfg['privateSourceBoundTileOverlays'])==1
    overlays=[]
    for overlay in cfg['privateSourceBoundTileOverlays']:
        overlay=copy.deepcopy(overlay);tile=ROOT/'3d-viewer'/overlay['url'];raw=edits[tile];assert digest(raw)==report['after'][str(tile.relative_to(ROOT))];after=__import__('json').loads(raw)
        for change in overlay['changes']:
            b=next(b for b in after['buildings']if b['uid']==change['uid']);assert b==dict(change['after'],foundationPolicy='terrain-derived-illustrative-posts');change['after']=b
        target=local/('qualified-'+tile.name);target.write_bytes(raw);overlay.update(source=str(target.relative_to(ROOT)),afterSHA256=digest(raw));overlays.append(overlay);refs.extend([tile,target])
    cfg.update(qualifiedExactStage=True,privateSourceBoundTileOverlays=overlays,diagnosticOnly=True,publication=False);save(local/'config.json',cfg);refs.extend([local/'config.json',HERE.parent/'island-detail-integration/publish.py',HERE.parent/'island-detail-integration/illustrative_foundations.py'])
    tool=HERE/'original_canopy_atomic_lifecycle_browser_v3_20261031.mjs';closure=HERE/'private_viewer_runtime_closure_v1_20261028.mjs';refs.extend([tool,closure,HERE/'production_source_bound_tile_routes_v3_20261031.mjs']);out.mkdir();cp=out/'runtime-input-closure.json';subprocess.run(['node',str(closure),'capture',str(cp.relative_to(ROOT))],cwd=ROOT,check=True)
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
        def copyfile(self,source,outputfile):
            try:super().copyfile(source,outputfile)
            except(BrokenPipeError,ConnectionResetError):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',4177),functools.partial(Handler,directory=str(ROOT/'3d-viewer')));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        with(out/'browser.log').open('w')as log:result=subprocess.run(['node',str(tool),str((local/'config.json').relative_to(ROOT)),str((out/'browser').relative_to(ROOT))],cwd=ROOT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},stdout=log,stderr=subprocess.STDOUT,timeout=3300)
        rp=out/'browser/report.json';r=read(rp)if rp.exists()else{};passed=result.returncode==0 and r.get('passed')is True and len(r.get('cases',[]))==6;assert manifest.read_bytes()==before
        subprocess.run(['node',str(closure),'verify',str(cp.relative_to(ROOT))],cwd=ROOT,check=True);refs.append(cp)
        for p in read(cp)['inputHashes']:refs.append(ROOT/p)
        for p,h in {p:h for values in pins.values()for p,h in values.items()if ROOT/p in refs}.items():assert digest((ROOT/p).read_bytes())==h
        output=dict(uids=summary['uids'],browserPassed=passed,cases=len(r.get('cases',[])),expectedCases=6,qualifiedExactStage=True,exactPublisherTileBytesTested=True,sourceMetadataDiffLimitedToApprovalKeys=True,sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,publication=False,qualification='Six real atomic browser cases on the exact qualified catalogue and exact one-canopy tile bytes from the complete publisher dry run. Original rendering/placement/dependency/group metadata equals the prior tested catalogue after stripping only explicit approval fields. Actual production modules/runtime closure, canopy source fields/render endpoints/collision posts, all-or-none group, download failure/retry/Base-only/Auto/eviction assertions retained. No live publication or installation credit.')
        save(out/'summary.json',output);assert reservations.owns(lease);module('villa_qualified_lifecycle_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-qualified-five-original-publisher-bytes-private-atomic-lifecycle',list(dict.fromkeys(refs)),output);assert passed,'Qualified lifecycle failed; evidence retained'
    finally:server.shutdown();server.server_close();thread.join(timeout=5)

if __name__=='__main__':main()
