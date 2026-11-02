"""Run the unchanged per-peer atomic lifecycle harness on an authenticated private original fixture."""
import argparse,functools,http.server,os,subprocess,sys,threading,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for key in ['batch','fixture']:p.add_argument('--'+key,required=True)
 p.add_argument('--owned',action='store_true');a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch;stage=HERE/'local'/a.fixture;lp=HERE/'local'/(a.batch+'-lease')/'reservation.json'
 assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.fixture])and not out.exists()
 receipt,pins=authenticate(base/a.fixture);assert receipt['onlyCatalogueFieldAdded']=='activationGroup'and receipt['approvalFlagChanges']==receipt['supportDependencyChanges']==receipt['terrainChanges']==receipt['sourceGeometryChanges']==receipt['sourcePoseChanges']==0
 resources=sorted(set(receipt['leaseResources'])|{'server:127.0.0.1:4177'})
 if not a.owned:
  assert not lp.parent.exists();claim=reservations.claim('original-atomic-lifecycle-'+str(uuid.uuid4()),resources,batch=a.batch,ttl=3600);assert claim['ok'],claim
  return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
 lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==set(resources);refs=[Path(__file__),base/a.fixture/'result.json']
 def take(path):
  assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);return read(path)
 cat=take(stage/'catalogue.json');uids=sorted(receipt['sourceSHA256ByUid']);assert {m['uid']:m['sha256']for m in cat['models']}==receipt['sourceSHA256ByUid']
 for m in cat['models']:
  assert m['activationGroup']==uids and m['publicationApproved']is False and m['placementReviewed']is False
  path=stage/m['asset'];assert digest(path.read_bytes())==m['sha256'];refs.append(path)
 cfg=take(stage/'config.json');assert cfg['viewportWidths']==[1280,390]and cfg['diagnosticOnly']and cfg['publication']is False and cfg['viewerURL']=='http://127.0.0.1:4177/city.html'
 take(stage/'source-forms.json');manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==pins[str(manifest.relative_to(ROOT))];before=manifest.read_bytes();refs.append(manifest)
 for t in cfg['terrain']:
  path=ROOT/t['source'];assert digest(path.read_bytes())==t['sha256'];refs.append(path)
 class Handler(http.server.SimpleHTTPRequestHandler):
  def log_message(self,*unused):pass
  def copyfile(self,source,target):
   try:super().copyfile(source,target)
   except (BrokenPipeError,ConnectionResetError):pass
 server=http.server.ThreadingHTTPServer(('127.0.0.1',4177),functools.partial(Handler,directory=str(ROOT/'3d-viewer')));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
 try:
  out.mkdir();tool=HERE/'model_atomic_lifecycle_browser_v4_20261101.mjs';refs.append(tool)
  with(out/'browser.log').open('w')as log:process=subprocess.run(['node',str(tool),str((stage/'config.json').relative_to(ROOT)),str(out.relative_to(ROOT))],cwd=ROOT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},stdout=log,stderr=subprocess.STDOUT,timeout=3300)
  save(out/'command.json',dict(exitCode=process.returncode));assert process.returncode==0 and reservations.owns(lease)and manifest.read_bytes()==before
  report=read(out/'report.json');assert report['passed']and not report['pageErrors']
  assert {(c['width'],c['failedUid'])for c in report['cases']}=={(1280,None)}|{(390,u)for u in uids}
  for c in report['cases']:
   assert c['baseOnlyRestoredCompleteGroup']and c['completeGroupEvicted']and c['audit']['frames']>0 and not c['audit']['violations']
   if c['failedUid']:assert c['failureKeptAllBasics']
   assert {s['uid']:s['sha256']for s in c['sources']}==receipt['sourceSHA256ByUid']
  result=dict(uids=uids,sourceSHA256ByUid=receipt['sourceSHA256ByUid'],passed=True,independentPerPeerFailuresPassed=True,completeAtomicLifecyclePassed=True,sourceGeometryChanges=0,sourcePoseChanges=0,terrainChanges=0,physicalAcceptance=False,visualAcceptance=False,installationApproved=False,publication=False,qualification=__doc__+' Success, every independent peer failure/retry, Base-only, Auto and eviction/return must retain coherent whole-group state. No performance, physical or publication approval.')
  save(out/'summary.json',result);assert reservations.owns(lease);module('original_atomic_lifecycle_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'private-exact-original-per-peer-atomic-lifecycle',refs,result)
 finally:server.shutdown();server.server_close();thread.join(timeout=5)
if __name__=='__main__':main()
