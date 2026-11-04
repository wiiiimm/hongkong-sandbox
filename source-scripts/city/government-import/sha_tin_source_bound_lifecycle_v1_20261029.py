"""Test seven original downloads, whole-group fallback, retry and eviction."""
import argparse,functools,http.server,os,subprocess,sys,threading,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-sha-tin-'
FIXTURE=PREFIX+'source-bound-full-scene-fixture-v2-20261029';BATCH=PREFIX+'source-bound-atomic-lifecycle-v1-20261029'


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--owned',action='store_true');a=p.parse_args()
    out=BASE/BATCH;local=HERE/'local'/BATCH;lp=local/'reservation.json';assert not out.exists()
    _,pins=authenticate(BASE/FIXTURE);inp=BASE/FIXTURE/'fixture-inputs.json';assert digest(inp.read_bytes())==pins[str(inp.relative_to(ROOT))];inputs=read(inp);resources=inputs['resources']
    if not a.owned:
        assert not local.exists();claim=reservations.claim('sha-tin-source-bound-lifecycle-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim
        return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(resources)<=set(lease['resources']);refs=[Path(__file__),BASE/FIXTURE/'result.json',inp]
    for path,sha in pins.items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
    config=ROOT/inputs['configPath'];cfg=read(config);assert cfg['diagnosticOnly']and cfg['publication']is False and len(cfg['browserUids'])==7 and cfg['viewerURL']=='http://127.0.0.1:4177/city.html'
    tool=HERE/'source_bound_atomic_lifecycle_browser_v1_20261029.mjs';prior=HERE/'model_atomic_lifecycle_browser_v2_20261027.mjs';insertions=HERE/'source-bound-atomic-insertions-v1-20261029.json'
    text=tool.read_text()
    for insertion in reversed(read(insertions)):assert text.count(insertion)==1;text=text.replace(insertion,'',1)
    assert text==prior.read_text()
    refs.extend([tool,prior,insertions,config,HERE/'private_source_bound_browser_routes_v1_20261029.mjs',HERE/'source_bound_basic_lifecycle_checks_v1_20261029.mjs',HERE/'elegant_live_fallback_checks_v1_20261028.mjs'])
    closure=HERE/'private_viewer_runtime_closure_v1_20261028.mjs';out.mkdir();cp=out/'runtime-input-closure.json';refs.extend([closure,cp]);subprocess.run(['node',str(closure),'capture',str(cp.relative_to(ROOT))],cwd=ROOT,check=True)
    server_log=(out/'private-server.log').open('w')
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,fmt,*args):server_log.write((fmt%args)+'\n');server_log.flush()
    server=http.server.ThreadingHTTPServer(('127.0.0.1',4177),functools.partial(Handler,directory=str(ROOT/'3d-viewer')));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        print('Starting desktop success and7independent mobile failures, exact BASIC/canopy fallback, Base-only/retry/eviction.',flush=True)
        with(out/'browser.log').open('w')as log:command=subprocess.run(['node',str(tool),str(config.relative_to(ROOT)),str((out/'browser').relative_to(ROOT))],cwd=ROOT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},stdout=log,stderr=subprocess.STDOUT,timeout=3600)
        report_path=out/'browser/report.json';report=read(report_path)if report_path.exists()else{};passed=command.returncode==0 and report.get('passed')is True and len(report.get('cases',[]))==8
        subprocess.run(['node',str(closure),'verify',str(cp.relative_to(ROOT))],cwd=ROOT,check=True)
        for path in read(cp)['inputHashes']:refs.append(ROOT/path)
        for path,sha in pins.items():assert digest((ROOT/path).read_bytes())==sha
        result=dict(uids=cfg['browserUids'],browserPassed=passed,exitCode=command.returncode,cases=len(report.get('cases',[])),expectedCases=8,sourceGeometryChanges=0,sourcePoseChanges=0,diagnosticOnly=True,allPriorLifecycleAssertionsRetained=True,originalPriorHarness=str(prior.relative_to(ROOT)),productionFilesWritten=0,physicalAccepted=False,collisionReviewApproved=False,visualReviewApproved=False,installationApproved=False,publication=False,qualification='Eight real browser cases: desktop and each independently failed mobile original, actual full-group BASIC preservation, real canopy restoration/suppression, measured three BASIC continuation render endpoints and actual tile collision volumes/probes, Base-only, retry and complete-group eviction. Every baseline V2 lifecycle assertion retained; private routes and observations only added. No original geometry edits, measured performance claim or physical/visual/publication acceptance. ROOT must inspect actual exports.')
        save(out/'summary.json',result)
        if report_path.exists():refs.append(report_path)
        assert reservations.owns(lease);module('sha_tin_source_bound_lifecycle_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'actual-private-seven-original-all-failures-source-bound-basic-lifecycle',list(dict.fromkeys(refs)),result)
        assert passed,'Private lifecycle failed; negative receipt retained'
    finally:server.shutdown();server.server_close();thread.join(timeout=5);server_log.close()


if __name__=='__main__':main()
