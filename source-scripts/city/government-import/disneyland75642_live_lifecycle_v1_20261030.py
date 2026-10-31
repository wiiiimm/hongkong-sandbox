"""Read-only real HTTP lifecycle for one installed unchanged western pier."""
import functools,http.server,json,os,subprocess,sys,threading,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
PREFIX='government-xl-disneyland-western75642-independent-original'
INSTALL=PREFIX+'-original-installed-v8-20261030';BATCH=PREFIX+'-live-lifecycle-v2-20261030';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH

def main():
 final,pins=authenticate(BASE/INSTALL);assert final['sourceSHA256ByUid']=={'landsd/75642:0':'49cdebceca290d6ceccf3e1891546efbafa28218ae144da7c389190773c302c0'}
 configpath=HERE/'accepted'/(PREFIX+'-qualified-stage-v2-20261030')/'live-browser-config.json';assert digest(configpath.read_bytes())==pins[str(configpath.relative_to(ROOT))]
 config=read(configpath);config.update(liveInstalled=True,diagnosticOnly=True,publication=False)
 resources=['building:landsd/75642:0','building:landsd/75643:0','source-form:way/334029318:0','terrain:city/data/terrain.json','server:127.0.0.1:4177'];leasepath=LOCAL/'reservation.json'
 if '--owned'not in sys.argv:
  assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];save(leasepath,json.loads(json.dumps(lease,default=str)))
  try:subprocess.run([sys.executable,str(HERE/'bounded_reserved_runner_v2_20261022.py'),str(leasepath),sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
  finally:
   if reservations.owns(lease):assert reservations.release(lease)['ok']
  return
 lease=read(leasepath);assert reservations.owns(lease)and not DOC.exists();save(DOC/'config.json',config)
 class Handler(http.server.SimpleHTTPRequestHandler):
  def log_message(self,*args):pass
  def copyfile(self,source,outputfile):
   try:super().copyfile(source,outputfile)
   except(BrokenPipeError,ConnectionResetError):pass
 assert config['viewerURL']=='http://127.0.0.1:4177/city.html';server=http.server.ThreadingHTTPServer(('127.0.0.1',4177),functools.partial(Handler,directory=str(ROOT/'3d-viewer')));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();tool=HERE/'disneyland75642_live_lifecycle_browser_v1_20261030.mjs'
 try:
  with(DOC/'worker.log').open('w')as log:subprocess.run(['node',str(tool),str((DOC/'config.json').relative_to(ROOT)),str((DOC/'browser').relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=1800)
  report=read(DOC/'browser/report.json');assert report['passed']and not report['pageErrors']and report['liveInstalledHTTP']and not report['catalogueAndTerrainSubstitution'];assert len(report['cases'])==2
  for c in report['cases']:
   assert c['baseOnlyRestoredCompleteGroup']and c['completeGroupEvicted']and c['audit']['frames']>0 and not c['audit']['violations'];assert {s['uid']:s['sha256']for s in c['sources']}==final['sourceSHA256ByUid']
   if c['failedUid']:assert c['failedUid']=='landsd/75642:0'and c['failureKeptAllBasics']
  refs=[Path(__file__),tool,configpath,BASE/INSTALL/'result.json',DOC/'browser/report.json',DOC/'config.json'];assert reservations.owns(lease)
  module('western_lifecycle_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-independent-western-pier-installed-http-lifecycle',refs,dict(uids=['landsd/75642:0'],passed=True,sourceSHA256ByUid=final['sourceSHA256ByUid'],sourceGeometryChanges=0,liveInstalledHTTP=True,catalogueAndTerrainSubstitution=False,cases=2,installationApproved=False,qualification='Actual installed catalogue, terrain and exact asset HTTP bytes; desktop success, mobile503retry, Base-only/Auto, eviction/return and collision-map restoration. No real-device performance approval or additional installation credit.'))
 finally:server.shutdown();server.server_close();thread.join(timeout=5)
if __name__=='__main__':main()
