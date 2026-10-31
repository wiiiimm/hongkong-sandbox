"""Queue targeted clean source/retained views after the exact live lifecycle worker."""
import argparse,sys,uuid,os,time,subprocess,functools,http.server,threading
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved,process_identity
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-elegant-garden-';FIXTURE=PREFIX+'supported-activation-fixture-v2-20261028';LIFECYCLE=PREFIX+'supported-activation-browser-v3-20261028'
TARGETS=['landsd/100673:0']
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--after-pid',type=int);p.add_argument('--owned',action='store_true');a=p.parse_args();assert a.batch.startswith(PREFIX)and '/'not in a.batch
 out=BASE/a.batch;local=HERE/'local'/a.batch;lp=local/'reservation.json';assert not out.exists()
 fixture,pins=authenticate(BASE/FIXTURE);ip=BASE/FIXTURE/'fixture-inputs.json';assert digest(ip.read_bytes())==pins[str(ip.relative_to(ROOT))];inputs=read(ip);resources=set(inputs['resources'])
 if not a.owned:
  assert not local.exists()
  if a.after_pid:
   identity=process_identity(a.after_pid);assert identity and b'elegant_supported_activation_browser_v3_20261028.py'in identity[1]
   local.mkdir(parents=True);save(local/'predecessor.json',dict(pid=a.after_pid,startTicks=identity[0],expectedCompleteBatch=LIFECYCLE,workQueued=True,sourceGeometryChanges=0))
   print('Waiting only for verified exact lifecycle PID; no overlapping reservation claimed.',flush=True)
   while process_identity(a.after_pid)==identity:time.sleep(30)
  completed,_=authenticate(BASE/LIFECYCLE);assert completed['browserPassed']and completed['cases']==completed['expectedCases']==17,'Lifecycle incomplete/failed; no competing continuation or acceptance'
  claim=reservations.claim('clean-original-context-views-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=3600);assert claim['ok']
  return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,'--batch',a.batch,'--owned'])
 lease=read(lp);assert reservations.owns(lease)and resources<=set(lease['resources']);completed,life_pins=authenticate(BASE/LIFECYCLE);assert completed['browserPassed']and completed['cases']==17
 refs=[Path(__file__),BASE/FIXTURE/'result.json',BASE/LIFECYCLE/'result.json',BASE/LIFECYCLE/'summary.json',ip]
 for path,sha in pins.items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
 cfgpath=ROOT/inputs['configPath'];cfg=read(cfgpath);assert cfg['diagnosticOnly']and not cfg['publication'];out.mkdir();tool=HERE/'elegant_exact_camera_views_v1_20261028.mjs';prior=HERE/'elegant_targeted_camera_diagnostic_v1_20261028.mjs';closure=HERE/'private_viewer_runtime_closure_v1_20261028.mjs';cp=out/'runtime-input-closure.json';refs.extend([cfgpath,tool,prior,closure]);subprocess.run(['node',str(closure),'capture',str(cp.relative_to(ROOT))],cwd=ROOT,check=True);refs.append(cp)
 server_log=(out/'private-server.log').open('w')
 class Handler(http.server.SimpleHTTPRequestHandler):
  def log_message(self,fmt,*args):server_log.write((fmt%args)+'\n');server_log.flush()
 server=http.server.ThreadingHTTPServer(('127.0.0.1',4177),functools.partial(Handler,directory=str(ROOT/'3d-viewer')));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();commands=[]
 try:
  for width in [1280,390]:
   config=local/('config-'+str(width)+'.json');save(config,dict(cfg,failureTestUids=[],targetedVisualUids=TARGETS,viewportWidths=[width],doc=str((out/str(width)).relative_to(ROOT))+'/'));refs.append(config)
   print('Targeted clean unselected context',width,flush=True)
   with(out/('browser-'+str(width)+'.log')).open('w')as log:command=subprocess.run(['node',str(tool),'staged',str(config.relative_to(ROOT))],cwd=ROOT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},stdout=log,stderr=subprocess.STDOUT,timeout=2400)
   report_path=out/str(width)/'staged-browser.json';report=read(report_path)if report_path.exists()else{};passed=command.returncode==0 and report.get('passed')is True and len(report.get('cameraDiagnostics',[]))==len(TARGETS);commands.append(dict(width=width,exitCode=command.returncode,passed=passed));print(commands[-1],flush=True)
   if not passed:break
  subprocess.run(['node',str(closure),'verify',str(cp.relative_to(ROOT))],cwd=ROOT,check=True)
  for path in read(cp)['inputHashes']:refs.append(ROOT/path)
  for path,sha in pins.items():assert digest((ROOT/path).read_bytes())==sha
  result=dict(uids=TARGETS,commands=commands,allPassed=len(commands)==2 and all(c['passed']for c in commands),sourceGeometryChanges=0,sourcePoseChanges=0,diagnosticOnly=True,visualReviewApproved=False,installationApproved=False,publication=False,qualification='Tiny source100673exact rendered-camera/mesh-bound observation in both viewports; camera and lookAt restored immediately before render and their matrices/bounds recorded. Exact supported16source activation, current native catalogues,2terrain and3BASIC overlays. Actual tested camera positions must agree after controls update; no orbit minimum or source geometry changes. Current complete lifecycle is a prerequisite. Ray visibility/occlusion and camera collisions remain explicit, exports require ROOT review, and no claim of every surface visible or mobile performance follows.')
  save(out/'summary.json',result);assert reservations.owns(lease);module('exact_camera_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'targeted-clean-unselected-original-and-retained-context-after-complete-lifecycle',list(dict.fromkeys(refs)),read(out/'summary.json'));assert result['allPassed'],'Negative clean context receipt retained; no approval'
 finally:server.shutdown();server.server_close();thread.join(timeout=5);server_log.close()
if __name__=='__main__':main()
