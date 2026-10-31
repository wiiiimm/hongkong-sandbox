"""Run actual atomic/failure/Base-only suppression tests on the private supported fixture."""
import argparse,sys,uuid,os,subprocess,functools,http.server,threading
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-elegant-garden-';FIXTURE=PREFIX+'supported-activation-fixture-v2-20261028'
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args();assert a.batch.startswith(PREFIX)and '/'not in a.batch
 out=BASE/a.batch;local=HERE/'local'/a.batch;lp=local/'reservation.json';assert not out.exists();fixture,pins=authenticate(BASE/FIXTURE);ip=BASE/FIXTURE/'fixture-inputs.json';assert digest(ip.read_bytes())==pins[str(ip.relative_to(ROOT))];inputs=read(ip);resources=set(inputs['resources'])
 if not a.owned:
  assert not local.exists();claim=reservations.claim('actual-supported-atomic-browser-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=3600);assert claim['ok']
  return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
 lease=read(lp);assert reservations.owns(lease)and resources<=set(lease['resources']);refs=[Path(__file__),BASE/FIXTURE/'result.json',ip]
 for path,sha in pins.items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
 config=ROOT/inputs['configPath'];cfg=read(config);assert cfg['diagnosticOnly']and not cfg['publication']and cfg['viewerURL']=='http://127.0.0.1:4177/city.html';assert len(cfg['browserUids'])==16 and len(cfg['terrain'])==2 and sum(len(o['changes'])for o in cfg['privateFoundationTileOverlays'])==3
 out.mkdir();tool=HERE/'elegant_supported_atomic_lifecycle_browser_v1_20261028.mjs';prior=HERE/'model_atomic_lifecycle_browser_v2_20261027.mjs';closure=HERE/'private_viewer_runtime_closure_v1_20261028.mjs';cp=out/'runtime-input-closure.json';refs.extend([tool,prior,closure,config]);subprocess.run(['node',str(closure),'capture',str(cp.relative_to(ROOT))],cwd=ROOT,check=True);refs.append(cp)
 server_log=(out/'private-server.log').open('w')
 class Handler(http.server.SimpleHTTPRequestHandler):
  def log_message(self,fmt,*args):server_log.write((fmt%args)+'\n');server_log.flush()
 server=http.server.ThreadingHTTPServer(('127.0.0.1',4177),functools.partial(Handler,directory=str(ROOT/'3d-viewer')));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
 try:
  print('Starting actual supported16model desktop/mobile lifecycle, all16independent mobile download failures, Base-only and canopy restoration.',flush=True)
  with(out/'browser.log').open('w')as log:command=subprocess.run(['node',str(tool),str(config.relative_to(ROOT)),str((out/'browser').relative_to(ROOT))],cwd=ROOT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},stdout=log,stderr=subprocess.STDOUT,timeout=3600)
  report_path=out/'browser/report.json';report=read(report_path)if report_path.exists()else{};passed=command.returncode==0 and report.get('passed')is True
  subprocess.run(['node',str(closure),'verify',str(cp.relative_to(ROOT))],cwd=ROOT,check=True)
  for path in read(cp)['inputHashes']:refs.append(ROOT/path)
  for path,sha in pins.items():assert digest((ROOT/path).read_bytes())==sha
  save(out/'summary.json',dict(uids=inputs['uids'],browserPassed=passed,exitCode=command.returncode,cases=len(report.get('cases',[])),expectedCases=17,sourceGeometryChanges=0,sourcePoseChanges=0,diagnosticOnly=True,physicalAccepted=False,visualReviewApproved=False,installationApproved=False,publication=False,qualification='Actual production viewer with private exact16model support/atomic metadata, two terrain members and three BASIC foundation overlays. The baseline atomic diagnostics are extended with exact foundation-only tile routing, retained surveyed Rex support and real canopy suppression/restoration assertions. Every independent mobile source failure/retry, full group Base-only/basic-face restoration and reactivation is required. Software evidence is not measured performance or whole-group publication approval. Exported images need ROOT inspection.'))
  if report_path.exists():refs.append(report_path)
  assert reservations.owns(lease);module('supported_atomic_browser_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'actual-supported-original-atomic-group-failure-base-only-and-suppression-runtime',list(dict.fromkeys(refs)),read(out/'summary.json'))
  assert passed,'Private browser checks failed; negative receipt retained, no approval'
 finally:server.shutdown();server.server_close();thread.join(timeout=5);server_log.close()
if __name__=='__main__':main()
