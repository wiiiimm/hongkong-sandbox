"""Private original-only atomic availability and retained illustrative canopy test."""
import argparse,copy,functools,http.server,json,os,shutil,subprocess,sys,threading,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-villa-premiere89917-'
BATCH=P+'five-atomic-canopy-lifecycle-v2-20261031';PREVIEW=P+'five-ramp-canopy-private-preview-v1-20261031';SCOPE=P+'ramp-return-scope-v1-20261030';CANOPY=P+'canopy-post-foundation-v1-20261030'

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--owned',action='store_true');a=ap.parse_args();out=BASE/BATCH;local=HERE/'local'/BATCH;lp=local/'reservation.json';assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    forms=take(SCOPE,BASE/SCOPE/'form-obligations.json.gz');assert len(forms)==47
    resources=sorted({('building:'if b['uid'].startswith('landsd/')else'source-form:')+b['uid']for b in forms}|{'server:127.0.0.1:4177','terrain:city/data/terrain.json'})
    if not a.owned:
        assert not local.exists();claim=reservations.claim('villa-premiere-atomic-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim
        return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(resources)==set(lease['resources']);oldstage=HERE/'local'/PREVIEW
    cfg=take(PREVIEW,oldstage/'browser-config-390.json');cat=take(PREVIEW,oldstage/'catalogue.json');uids=sorted(m['uid']for m in cat['models']);assert len(uids)==5
    for entry in cat['models']:
        assert all(entry[k]is False for k in ['publicationApproved','placementReviewed','identityReviewApproved','sourceIdentityReviewed'])
        assert not entry.get('activationGroup')and not entry.get('suppressesBuildingUids');entry['activationGroup']=uids
        asset=oldstage/entry['asset'];assert digest(asset.read_bytes())==entry['sha256'];refs.append(asset);target=local/entry['asset'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(asset,target)
    save(local/'catalogue.json',cat);save(local/'source-forms.json',take(PREVIEW,oldstage/'source-forms.json'))
    cfg.update(stage=str(local.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',diagnosticOnly=True,publication=False,expectedCanopyPostCount=8)
    assert len(cfg['privateSourceBoundTileOverlays'])==1 and cfg['expectedPrivateOverlayUids']==['landsd/325786:0']
    for overlay in cfg['privateSourceBoundTileOverlays']:
        path=ROOT/overlay['source'];assert digest(path.read_bytes())==overlay['afterSHA256'];refs.append(path)
    for t in cfg['terrain']:
        path=ROOT/t['source'];assert digest(path.read_bytes())==t['sha256'];refs.append(path)
    activity=ROOT/'3d-viewer/city/data/activity/-7_-9.json';refs.append(activity);cfg['expectedCanopyActivity']=dict(url=str(activity.relative_to(ROOT/'3d-viewer')),sha256=digest(activity.read_bytes()))
    save(local/'config.json',cfg);refs.extend([local/'config.json',local/'catalogue.json',local/'source-forms.json'])
    b=take(CANOPY,BASE/CANOPY/'input.json')['building'];proposal=take(CANOPY,BASE/CANOPY/'proposal.json');assert b in forms
    manifest=ROOT/'3d-viewer/city/data/manifest.json';refs.append(manifest);before=manifest.read_bytes();hashes={str(manifest.relative_to(ROOT)):digest(before)}
    for form in forms:
        tile=ROOT/'3d-viewer/city/data/tiles'/(form['tile']+'.json');assert next(x for x in read(tile)['buildings']if x['uid']==form['uid'])==form;hashes[str(tile.relative_to(ROOT))]=digest(tile.read_bytes());refs.append(tile)
    save(out/'collision-input.json',dict(building=b,foundationBase=proposal['foundationBase'],currentForms=forms,expectedFormCount=len(forms),inputHashes=hashes))
    collision=HERE/'basic_canopy_runtime_collision_v2_20261031.mjs';refs.append(collision)
    subprocess.run(['node',str(collision),str((out/'collision-input.json').relative_to(ROOT)),str((out/'collision.json').relative_to(ROOT))],cwd=ROOT,check=True)
    for path,sha in read(out/'collision.json')['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
    tool=HERE/'original_canopy_atomic_lifecycle_browser_v2_20261031.mjs';refs.extend([tool,HERE/'model_atomic_lifecycle_browser_v2_20261027.mjs',HERE/'production_source_bound_tile_routes_v2_20261031.mjs'])
    out.mkdir(exist_ok=True)
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',4177),functools.partial(Handler,directory=str(ROOT/'3d-viewer')));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        print('Starting desktop success and five independent mobile failures; complete assembly fallback and retained canopy.',flush=True)
        with(out/'browser.log').open('w')as log:
            result=subprocess.run(['node',str(tool),str((local/'config.json').relative_to(ROOT)),str((out/'browser').relative_to(ROOT))],cwd=ROOT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},stdout=log,stderr=subprocess.STDOUT,timeout=3300)
        report_path=out/'browser/report.json';report=read(report_path)if report_path.exists()else{};passed=result.returncode==0 and report.get('passed')is True and len(report.get('cases',[]))==6
        assert manifest.read_bytes()==before
        summary=dict(uids=uids,browserPassed=passed,exitCode=result.returncode,cases=len(report.get('cases',[])),expectedCases=6,leaseResources=resources,sourceGeometryChanges=0,sourcePoseChanges=0,privateAtomicAvailabilityGroup=uids,retainedCanopyUid=b['uid'],collisionProbes=read(out/'collision.json')['probes'],physicalAcceptance=False,identityAccepted=False,installationApproved=False,publication=False,qualification='Existing atomic activation metadata only, exact five immutable government sources. Desktop success and each independently failed mobile source must preserve complete BASIC assembly, then retry/Base-only/Auto/eviction must remain atomic. At every phase the unrelated unsurveyed canopy stays visible with exact recorded fields, unchanged roof top and eight actual production post collision bottoms. Full47-form production collision probe preserves roofs and all46other forms. No production file/geometry writes or source acceptance.')
        save(out/'summary.json',summary);refs.extend(p for p in local.rglob('*')if p.is_file()and p.name!='reservation.json');assert reservations.owns(lease)
        module('villa_premiere_atomic_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-five-original-atomic-availability-and-retained-canopy-lifecycle',list(dict.fromkeys(refs)),summary)
        assert passed,'Atomic lifecycle failed; negative evidence retained'
    finally:server.shutdown();server.server_close();thread.join(timeout=5)

if __name__=='__main__':main()
