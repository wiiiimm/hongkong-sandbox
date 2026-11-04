"""Supplement obscured retained views using the same exact atomic fixture and terrain.

This is camera-only evidence, not a replacement for the complete region checks
or prior full desktop/mobile run. No geometry, visibility or approval changes.
"""
import argparse,copy,functools,http.server,os,subprocess,sys,threading,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for key in ['batch','fixture']:p.add_argument('--'+key,required=True)
 p.add_argument('--uid',action='append',required=True);p.add_argument('--direction',nargs=3,type=float,required=True);p.add_argument('--owned',action='store_true');a=p.parse_args()
 assert 0<len(a.uid)==len(set(a.uid))<=4 and all(__import__('math').isfinite(x)for x in a.direction)and a.direction[1]>0
 base=ROOT/'docs/astra-city/government-import';out=base/a.batch;local=HERE/'local'/a.batch;lp=local/'reservation.json';assert a.batch.startswith('government-xl-')and'/'not in a.batch and not out.exists()
 receipt,pins=authenticate(base/a.fixture);assert receipt['onlyCatalogueFieldAdded']=='activationGroup'and not receipt['installationApproved'];stage=HERE/'local'/a.fixture;refs=[Path(__file__),base/a.fixture/'result.json']
 def take(path):
  assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);return read(path)
 cfg=take(stage/'config.json');assert set(a.uid)<=set(cfg['additionalRetainedUids'])and cfg['retainedNativeOwnViews']
 assert cfg['viewerURL']=='http://127.0.0.1:4177/city.html';sources={m['uid']:m['sha256']for m in take(stage/'catalogue.json')['models']}
 for m in read(stage/'catalogue.json')['models']:
  path=stage/m['asset'];assert digest(path.read_bytes())==m['sha256'];refs.append(path)
 take(stage/'source-forms.json');manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==pins[str(manifest.relative_to(ROOT))];before=manifest.read_bytes();refs.append(manifest)
 resources=sorted(set(receipt['leaseResources'])|{'server:127.0.0.1:4177'})
 if not a.owned:
  assert not local.exists();c=reservations.claim('original-retained-camera-'+str(uuid.uuid4()),resources,batch=a.batch,ttl=3600);assert c['ok'],c
  return execute_reserved(c['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
 lease=read(lp);assert reservations.owns(lease)and set(resources)==set(lease['resources'])
 cfg.update(additionalRetainedUids=a.uid,retainedCaptureDirectionByModel={u:a.direction for u in a.uid},failureTestUids=[])
 class Handler(http.server.SimpleHTTPRequestHandler):
  def log_message(self,*unused):pass
  def copyfile(self,source,target):
   try:super().copyfile(source,target)
   except (BrokenPipeError,ConnectionResetError):pass
 server=http.server.ThreadingHTTPServer(('127.0.0.1',4177),functools.partial(Handler,directory=str(ROOT/'3d-viewer')));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
 try:
  out.mkdir();tool=HERE/'ronsdale_three_live_browser_v15_20261026.mjs';refs.append(tool)
  for width in [1280,390]:
   config=copy.deepcopy(cfg);config.update(viewportWidths=[width],doc=str((out/str(width)).relative_to(ROOT))+'/');path=local/('config-'+str(width)+'.json');save(path,config);refs.append(path)
   with(out/('browser-'+str(width)+'.log')).open('w')as log:proc=subprocess.run(['node',str(tool),'staged',str(path.relative_to(ROOT))],cwd=ROOT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},stdout=log,stderr=subprocess.STDOUT,timeout=1200)
   assert proc.returncode==0 and reservations.owns(lease);report=read(out/str(width)/'staged-browser.json');assert report['passed']and not report['errors']
   assert {v['uid']for v in report['retainedNativeOwnViews']}==set(a.uid)and len(report['retainedNativeOwnViews'])==2*len(a.uid)
  assert manifest.read_bytes()==before and reservations.owns(lease)
  result=dict(uids=sorted(sources),sourceSHA256ByUid=sources,retainedSupplementUids=a.uid,sourceFixture=a.fixture,fullRegionChecksReplaced=False,geometryChanges=0,sourcePoseChanges=0,terrainChanges=0,visibilityOverrides=False,physicalAcceptance=False,visualAcceptance=False,installationApproved=False,publication=False,qualification=__doc__)
  save(out/'summary.json',result);module('retained_camera_supplement_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'same-original-fixture-retained-camera-supplement-only',refs,result)
 finally:server.shutdown();server.server_close();thread.join(timeout=5)
if __name__=='__main__':main()
