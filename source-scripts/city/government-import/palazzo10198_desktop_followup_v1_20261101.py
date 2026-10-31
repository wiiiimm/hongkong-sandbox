"""Supplement the tightly cropped desktop10198 view with the opposite direction."""
import argparse,copy,functools,http.server,os,subprocess,sys,threading,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-palazzo76610-after-prosperous-';PRIOR=P+'twenty-private-preview-v1-20261101';BATCH=P+'10198-desktop-opposite-view-v1-20261101'
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--owned',action='store_true');a=ap.parse_args();local=HERE/'local'/BATCH;lp=local/'reservation.json';out=BASE/BATCH;old=HERE/'local'/PRIOR
    receipt,pins=authenticate(BASE/PRIOR);resources=receipt['leaseResources']
    assert receipt['desktopMobileBrowserPassed']and receipt['atomicCases']==21
    if not a.owned:
        assert not local.exists();c=reservations.claim('palazzo10198-view-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==set(resources)and not out.exists();refs=[Path(__file__),BASE/PRIOR/'result.json'];cfgpath=old/'browser-config-1280.json';assert digest(cfgpath.read_bytes())==pins[str(cfgpath.relative_to(ROOT))];refs.append(cfgpath);cfg=copy.deepcopy(read(cfgpath));cfg.update(browserUids=['landsd/10198:0'],captureDirectionByModel={'landsd/10198:0':[1,1.6,-1]},failureTestUids=[],doc=str((out/'1280').relative_to(ROOT))+'/');save(local/'config.json',cfg)
    for path in [old/'catalogue.json',old/'source-forms.json',old/'validation-forms.json']:
        assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path)
    for model in read(old/'catalogue.json')['models']:
        asset=old/model['asset'];assert digest(asset.read_bytes())==model['sha256'];refs.append(asset)
    tool=HERE/'ronsdale_three_live_browser_v13_20261025.mjs';closure=HERE/'private_viewer_runtime_closure_v1_20261028.mjs';refs.extend([tool,closure]);out.mkdir();cp=out/'runtime-input-closure.json';subprocess.run(['node',str(closure),'capture',str(cp.relative_to(ROOT))],cwd=ROOT,check=True)
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
        def copyfile(self,source,outputfile):
            try:super().copyfile(source,outputfile)
            except(BrokenPipeError,ConnectionResetError):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',4177),functools.partial(Handler,directory=str(ROOT/'3d-viewer')));threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        with(out/'browser.log').open('w')as log:subprocess.run(['node',str(tool),'staged',str((local/'config.json').relative_to(ROOT))],cwd=ROOT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},stdout=log,stderr=subprocess.STDOUT,check=True,timeout=600)
        report=read(out/'1280/staged-browser.json');assert report['passed']and not report['errors']
        subprocess.run(['node',str(closure),'verify',str(cp.relative_to(ROOT))],cwd=ROOT,check=True)
    finally:server.shutdown();server.server_close()
    assert reservations.owns(lease);refs.append(local/'config.json');result=dict(uids=['landsd/10198:0'],sourceSHA256=receipt['sourceSHA256ByUid']['landsd/10198:0'],desktopFollowupPassed=True,originalTwentyBrowserAcceptanceTransferred=False,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,qualification=__doc__+' Same exact private twenty originals, terrain, fallback/native guard obligations and unchanged browser adapter. Only requested camera direction and one-source capture subset change. Main twenty-source/21atomic evidence remains separately bound; exports still require actual inspection.')
    save(out/'summary.json',result);module('palazzo10198_view_followup_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'supplementary-one-original-desktop-opposite-camera-check',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
