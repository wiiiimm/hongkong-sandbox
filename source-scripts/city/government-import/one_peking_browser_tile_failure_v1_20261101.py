"""Reserved loopback scene controls for BASIC tile activation failure; no approval."""
import functools,http.server,threading,subprocess,sys,uuid,json,os
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-one-peking-after-twin-';BATCH=P+'browser-tile-failure-v1-20261101'
def owned(leasepath):
 lease=read(leasepath);assert reservations.owns(lease);out=BASE/BATCH;assert not out.exists();cfg=HERE/'local'/(P+'cycle-private-browser-v3-20261101')/'browser-config-1280.json';config=read(cfg);assert config['viewerURL']=='http://127.0.0.1:4177/city.html';out.mkdir();refs=[Path(__file__),cfg]
 class Handler(http.server.SimpleHTTPRequestHandler):
  def log_message(self,*args):pass
  def copyfile(self,source,outputfile):
   try:super().copyfile(source,outputfile)
   except(BrokenPipeError,ConnectionResetError):pass
 server=http.server.ThreadingHTTPServer(('127.0.0.1',4177),functools.partial(Handler,directory=str(ROOT/'3d-viewer')));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
 try:
  tool=HERE/'one_peking_browser_tile_failure_v1_20261101.mjs'
  with(out/'worker.log').open('w')as log:subprocess.run(['node',str(tool),str(cfg.relative_to(ROOT)),str(out.relative_to(ROOT))+'/'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'})
  proof=read(out/'diagnostic.json')
  for path,sha in proof['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
  refs.append(tool);module('one_peking_tile_failure_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'three-current-immutable-browser-scene-controls-and-basic-tile-error',list(dict.fromkeys(refs)),dict(uids=['landsd/233985:0','landsd/240487:0'],cases=proof['cases'],installationApproved=False,physicalAcceptance=False,sourceGeometryChanges=0))
 finally:server.shutdown();server.server_close();thread.join(timeout=10)
def main():
 if '--owned'in sys.argv:return owned(Path(sys.argv[sys.argv.index('--lease')+1]))
 resources=read(HERE/'local'/(P+'cycle-private-browser-v3-20261101')/'reservation.json')['resources'];claim=reservations.claim('one-peking-browser-tile-controls-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim;path=HERE/'local'/(BATCH+'-control')/'reservation.json';execute_reserved(claim['reservation'],path,[sys.executable,__file__,'--owned','--lease',str(path)])
if __name__=='__main__':main()
