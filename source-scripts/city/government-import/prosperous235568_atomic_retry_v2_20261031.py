"""Resume completed six-original browser diagnostics; repair atomic catalogue envelope."""
import argparse,copy,functools,http.server,os,shutil,subprocess,sys,threading,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-prosperous235568-'
PRIOR=P+'six-original-private-preview-v3-20261031';BATCH=P+'six-original-atomic-retry-v2-20261031'
RUNTIME=P+'six-original-patch-runtime-v1-20261031';SCOPE='government-xl-after-villa-premiere-235568-floor-return-scope-v1-20261031'
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--owned',action='store_true');a=ap.parse_args()
    out=BASE/BATCH;local=HERE/'local'/BATCH;lp=local/'reservation.json';assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,name):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        p=BASE/batch/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    rows=take(RUNTIME,'selection.json.gz')['rows'];sources={r['uid']:r['sourceSHA256']for r in rows};uids=sorted(sources);assert len(uids)==6
    forms=take(SCOPE,'form-obligations.json.gz');assert len(forms)==58
    resources=sorted({('building:'if b['uid'].startswith('landsd/')else'source-form:')+b['uid']for b in forms}|{'building:'+u for u in uids}|{'server:127.0.0.1:4177','terrain:city/data/terrain.json'})
    if not a.owned:
        assert not local.exists();claim=reservations.claim('prosperous-atomic-retry-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim
        return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==set(resources)
    old=HERE/'local'/PRIOR;cat=read(old/'catalogue.json');assert {m['uid']:m['sha256']for m in cat['models']}==sources
    refs.extend([HERE/'prosperous235568_private_preview_v3_20261031.py',HERE/'ronsdale_three_live_browser_v13_20261025.mjs',old/'catalogue.json',old/'source-forms.json',old/'validation-forms.json'])
    for width in [1280,390]:
        report=BASE/PRIOR/str(width)/'staged-browser.json';r=read(report);assert r['passed']and not r['errors'];refs.append(report)
        command=BASE/PRIOR/('command-'+str(width)+'.json');assert read(command)['exitCode']==0;refs.append(command)
        cfg=read(old/('browser-config-'+str(width)+'.json'));assert cfg['viewportWidths']==[width]and sorted(cfg['browserUids'])==uids;refs.append(old/('browser-config-'+str(width)+'.json'))
        for uid in uids:
            for hour in ['1500','2200']:
                p=report.parent/('staged-'+uid.replace('/','-').replace(':','-')+'-'+str(width)+'-'+hour+'-canvas.png');assert p.is_file();refs.append(p)
    cfg=read(old/'browser-config-390.json');assert not cfg.get('privateSourceBoundTileOverlays')
    manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();assert digest(before)==read(BASE/RUNTIME/'selection.json.gz')['manifestSHA256'];refs.append(manifest)
    for row in rows:
        p=ROOT/'3d-viewer'/row['source']['tile'];assert digest(p.read_bytes())==row['source']['tileSHA256'];assert next(b for b in read(p)['buildings']if b['uid']==row['uid'])==row['source']['building'];refs.append(p)
    for m in cat['models']:
        assert all(m[k]is False for k in ['publicationApproved','placementReviewed','identityReviewApproved','sourceIdentityReviewed'])and m['proceduralWindows']is False and m['priority']=='landmark'
        assert not m.get('activationGroup')and not m.get('suppressesBuildingUids');m['activationGroup']=uids
        p=old/m['asset'];assert digest(p.read_bytes())==sources[m['uid']]and p.stat().st_size==m['bytes'];refs.append(p);q=local/m['asset'];q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
    # Keep the complete standard catalogue envelope. V3's models-only atomic file was rejected.
    save(local/'catalogue.json',cat);save(local/'source-forms.json',read(old/'source-forms.json'))
    for t in cfg['terrain']:
        p=ROOT/t['source'];assert digest(p.read_bytes())==t['sha256'];refs.append(p)
    cfg.update(stage=str(local.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',diagnosticOnly=True,publication=False);save(local/'config.json',cfg)
    out.mkdir();closure=HERE/'private_viewer_runtime_closure_v1_20261028.mjs';refs.append(closure)
    previousclosure=BASE/PRIOR/'runtime-input-closure.json';subprocess.run(['node',str(closure),'verify',str(previousclosure.relative_to(ROOT))],cwd=ROOT,check=True);refs.append(previousclosure)
    cp=out/'runtime-input-closure.json';subprocess.run(['node',str(closure),'capture',str(cp.relative_to(ROOT))],cwd=ROOT,check=True)
    caps=P+'block5-compound-cap-paths-v1-20261031';tool=HERE/'selected_original_peer_cap_paths_v1_20261031.py';refs.append(tool)
    with(out/'block5-caps.log').open('w')as log:
        subprocess.run([sys.executable,str(tool),'--batch',caps,'--runtime',RUNTIME,'--attributes',P+'six-original-attributes-v1-20261031','--low-faces',P+'block5-compound-lower-context-v1-20261031','--uid','landsd/235119:0','--peer','landsd/235568:0','--lease',str(lp)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    take(caps,'summary.json') # Context only; no approval inferred from cap paths.
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
        def copyfile(self,source,outputfile):
            try:super().copyfile(source,outputfile)
            except(BrokenPipeError,ConnectionResetError):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',4177),functools.partial(Handler,directory=str(ROOT/'3d-viewer')));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        tool=HERE/'model_atomic_lifecycle_browser_v2_20261027.mjs';refs.append(tool)
        with(out/'atomic-browser.log').open('w')as log:
            result=subprocess.run(['node',str(tool),str((local/'config.json').relative_to(ROOT)),str((out/'atomic-browser').relative_to(ROOT))],cwd=ROOT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},stdout=log,stderr=subprocess.STDOUT,timeout=3300)
        report=read(out/'atomic-browser/report.json');assert result.returncode==0 and report['passed']and not report['pageErrors']and len(report['cases'])==7
        assert {(r['width'],r['failedUid'])for r in report['cases']}=={(1280,None)}|{(390,u)for u in uids}
        for r in report['cases']:
            assert r['completeGroupEvicted']and r['baseOnlyRestoredCompleteGroup']and not r['audit']['violations']
            assert {m['uid']:m['sha256']for m in r['sources']}==sources
            if r['failedUid']:assert r['failureKeptAllBasics']
        assert manifest.read_bytes()==before and reservations.owns(lease)
        subprocess.run(['node',str(closure),'verify',str(cp.relative_to(ROOT))],cwd=ROOT,check=True);refs.append(cp);refs.extend(ROOT/p for p in read(cp)['inputHashes'])
        refs.extend(p for p in local.rglob('*')if p.is_file()and p.name!='reservation.json')
        summary=dict(uids=uids,sourceSHA256ByUid=sources,leaseResources=resources,desktopMobileBrowserPassed=True,previousCompletedBrowserBatch=PRIOR,atomicCases=7,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,visualAcceptance=False,installationApproved=False,publication=False,qualification='Completed actual desktop/mobile six-source rendering/picking/collision/download failure records retained. Atomic retry preserves the complete catalogue envelope with only exact all6 activation metadata added; no source/terrain/runtime guard changes or acceptance credit.')
        save(out/'summary.json',summary);module('prosperous_atomic_retry_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'six-original-completed-browser-and-correct-catalogue-atomic-retry',list(dict.fromkeys(refs)),summary)
    finally:server.shutdown();server.server_close();thread.join(timeout=5)
if __name__=='__main__':main()
