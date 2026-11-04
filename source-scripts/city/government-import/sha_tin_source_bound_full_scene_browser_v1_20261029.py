"""Observe the private source-bound fixture on desktop/mobile, no publication."""
import argparse,functools,http.server,os,subprocess,sys,threading,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-sha-tin-'
FIXTURE=PREFIX+'source-bound-full-scene-fixture-v2-20261029'
BATCH=PREFIX+'source-bound-full-scene-browser-v1-20261029'


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--owned',action='store_true');a=p.parse_args()
    out=BASE/BATCH;local=HERE/'local'/BATCH;lp=local/'reservation.json';assert not out.exists()
    _,pins=authenticate(BASE/FIXTURE);inp=BASE/FIXTURE/'fixture-inputs.json';assert digest(inp.read_bytes())==pins[str(inp.relative_to(ROOT))];inputs=read(inp);resources=inputs['resources']
    if not a.owned:
        assert not local.exists();claim=reservations.claim('sha-tin-private-browser-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim
        return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(resources)<=set(lease['resources'])
    refs=[Path(__file__),BASE/FIXTURE/'result.json',inp]
    for path,sha in pins.items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
    cfgpath=ROOT/inputs['configPath'];config=read(cfgpath);refs.append(cfgpath)
    assert config['diagnosticOnly']and config['publication']is False and config['viewerURL']=='http://127.0.0.1:4177/city.html'
    assert len(config['browserUids'])==7 and len(config['terrain'])==1 and config['failureTestUids']==[]
    assert sum(len(t['changes'])for t in config['privateSourceBoundTileOverlays'])==4
    tool=HERE/'ronsdale_three_live_browser_v20_20261029.mjs';old=HERE/'ronsdale_three_live_browser_v19_20261028.mjs';addition="\n await (await import('./private_source_bound_browser_routes_v1_20261029.mjs')).bindPrivateSourceBoundRoutes(page,config,root,mode,report);"
    assert tool.read_text().replace(addition,'')==old.read_text();refs.extend([tool,old,HERE/'private_source_bound_browser_routes_v1_20261029.mjs'])
    out.mkdir();server_log=(out/'private-server.log').open('w')
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,fmt,*args):server_log.write((fmt%args)+'\n');server_log.flush()
    server=http.server.ThreadingHTTPServer(('127.0.0.1',4177),functools.partial(Handler,directory=str(ROOT/'3d-viewer')))
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();commands=[]
    try:
        preflight=local/'preflight-config.json';save(preflight,dict(config,doc=str(out.relative_to(ROOT))+'/'));refs.append(preflight)
        subprocess.run(['node',str(tool),'preflight',str(preflight.relative_to(ROOT))],cwd=ROOT,check=True)
        for width in [1280,390]:
            assert reservations.owns(lease);cfg=local/('browser-config-'+str(width)+'.json');save(cfg,dict(config,viewportWidths=[width],doc=str((out/str(width)).relative_to(ROOT))+'/'));refs.append(cfg)
            print(dict(width=width,phase='private-source-bound-seven-start'),flush=True)
            with(out/('browser-'+str(width)+'.log')).open('w')as log:
                result=subprocess.run(['node',str(tool),'staged',str(cfg.relative_to(ROOT))],cwd=ROOT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},stdout=log,stderr=subprocess.STDOUT,timeout=2400)
            report_path=out/str(width)/'staged-browser.json';report=read(report_path)if report_path.exists()else{}
            commands.append(dict(width=width,exitCode=result.returncode,reportPresent=report_path.exists(),diagnosticPassed=result.returncode==0 and report.get('passed')is True,privateSourceBoundExperiment=report.get('privateSourceBoundExperiment')))
            save(out/('command-'+str(width)+'.json'),commands[-1]);print(commands[-1],flush=True)
            if report_path.exists():refs.append(report_path)
            if result.returncode:break
        for path,sha in pins.items():assert digest((ROOT/path).read_bytes())==sha
        result=dict(uids=config['browserUids'],commands=commands,allBrowserDiagnosticsPassed=len(commands)==2 and all(c['diagnosticPassed']for c in commands),diagnosticOnly=True,privateBasicContinuations=3,estimatedCanopyPostBottoms=1,sourceGeometryChanges=0,sourcePoseChanges=0,productionFilesWritten=0,availabilityAcceptance=False,failureTestsDeliberatelyDeferred=True,physicalAccepted=False,collisionReviewApproved=False,visualReviewApproved=False,installationApproved=False,publication=False,qualification='Actual viewer on private loopback with exact original geometry, validated static terrain, three private BASIC continuation hints, post-bottom-only canopy fallback and conditional duplicate canopy suppression. Every original V19 assertion remains. Source geometry is immutable and no production modules or tile bytes are written. Initial desktop/mobile observations only: atomic failure/Base-only/eviction lifecycle and physical/visual/publication acceptance remain separate. ROOT must inspect exports.')
        save(out/'summary.json',result);assert reservations.owns(lease)
        module('sha_tin_private_browser_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-seven-original-source-bound-basic-full-scene-browser',list(dict.fromkeys(refs)),result)
    finally:
        server.shutdown();server.server_close();thread.join(timeout=5);server_log.close()


if __name__=='__main__':main()
