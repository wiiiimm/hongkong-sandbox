"""Capture clean private BASIC fallback canvases; visual review remains separate."""
import argparse,functools,http.server,os,subprocess,sys,threading,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-sha-tin-'
FIXTURE=PREFIX+'source-bound-full-scene-fixture-v2-20261029';BATCH=PREFIX+'source-bound-fallback-canvas-views-v1-20261029'


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--owned',action='store_true');a=p.parse_args();out=BASE/BATCH;local=HERE/'local'/BATCH;lp=local/'reservation.json';assert not out.exists()
    _,pins=authenticate(BASE/FIXTURE);inp=BASE/FIXTURE/'fixture-inputs.json';assert digest(inp.read_bytes())==pins[str(inp.relative_to(ROOT))];inputs=read(inp);resources=inputs['resources']
    if not a.owned:
        assert not local.exists();claim=reservations.claim('sha-tin-base-canvas-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=1800);assert claim['ok'],claim
        return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(resources)<=set(lease['resources']);refs=[Path(__file__),BASE/FIXTURE/'result.json',inp]
    for path,sha in pins.items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
    config=ROOT/inputs['configPath'];tool=HERE/'source_bound_basic_fallback_views_v1_20261029.mjs';refs.extend([config,tool,HERE/'source_bound_basic_lifecycle_checks_v1_20261029.mjs',HERE/'private_source_bound_browser_routes_v1_20261029.mjs',HERE/'elegant_live_fallback_checks_v1_20261028.mjs'])
    closure=HERE/'private_viewer_runtime_closure_v1_20261028.mjs';out.mkdir();cp=out/'runtime-input-closure.json';refs.extend([closure,cp]);subprocess.run(['node',str(closure),'capture',str(cp.relative_to(ROOT))],cwd=ROOT,check=True)
    server_log=(out/'private-server.log').open('w')
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,fmt,*args):server_log.write((fmt%args)+'\n');server_log.flush()
    server=http.server.ThreadingHTTPServer(('127.0.0.1',4177),functools.partial(Handler,directory=str(ROOT/'3d-viewer')));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        with(out/'browser.log').open('w')as log:command=subprocess.run(['node',str(tool),str(config.relative_to(ROOT)),str((out/'browser').relative_to(ROOT))],cwd=ROOT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},stdout=log,stderr=subprocess.STDOUT,timeout=1800)
        report_path=out/'browser/report.json';report=read(report_path)if report_path.exists()else{};passed=command.returncode==0 and report.get('passed')is True and len(report.get('views',[]))==8
        subprocess.run(['node',str(closure),'verify',str(cp.relative_to(ROOT))],cwd=ROOT,check=True)
        for path in read(cp)['inputHashes']:refs.append(ROOT/path)
        for path,sha in pins.items():assert digest((ROOT/path).read_bytes())==sha
        result=dict(uids=inputs['uids'],browserPassed=passed,exitCode=command.returncode,expectedViews=8,exportedViews=report.get('views',[]),sourceGeometryChanges=0,sourcePoseChanges=0,diagnosticOnly=True,productionFilesWritten=0,physicalAccepted=False,collisionReviewApproved=False,visualReviewApproved=False,installationApproved=False,publication=False,qualification='Actual UI-free Base-only canvas exports of each of three private BASIC continuations and one canopy at1280/390. Source-bounded full BASIC bounds are verified framed and native owner inactive; all four real fallback render/collision contracts run per viewport. No UI is edited in production. ROOT must inspect actual PNGs before any visual acceptance; existing eight independent lifecycle cases remain separate.')
        save(out/'summary.json',result)
        if report_path.exists():refs.append(report_path)
        assert reservations.owns(lease);module('sha_tin_fallback_visual_capture_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'actual-private-base-only-source-bound-fallback-canvases',list(dict.fromkeys(refs)),result)
        assert passed,'Private fallback capture failed; negative receipt retained'
    finally:server.shutdown();server.server_close();thread.join(timeout=5);server_log.close()


if __name__=='__main__':main()
