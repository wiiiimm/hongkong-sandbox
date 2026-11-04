"""Run full fresh narrow-inset regressions under the existing lease supervisor."""
import json,subprocess,sys,uuid
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-olympic-station-narrow-neighbours-v1-20261022'
def main():
 prior=BASE/'government-xl-olympic-station-retained-neighbours-v4-20261022';_,pins=authenticate(prior);p=prior/'neighbour-inputs.json.gz';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];old=read(p);assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==old['inputHashes']['3d-viewer/city/data/manifest.json'];assert not(BASE/BATCH).exists()
 keys=[('building:'if r['building']['uid'].startswith('landsd/')else'source-form:')+r['building']['uid']for r in old['rows']]+['terrain:city/data/terrain.json']
 for p in old['patches']:
  for r in p.get('replacesMany')or[p['replaces']]:keys.append('terrain:'+r['url'])
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),keys,batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=json.loads(json.dumps(claim['reservation'],default=str));path=HERE/'local'/BATCH/'reservation.json';save(path,lease)
 args=['--batch',BATCH,'--scope','government-xl-olympic-station-narrow-scope-v1-20261022','--inventory','government-xl-after-aquarium-current-inventory-v1-20261022','--patch','government-xl-olympic-narrow-retained-candidate-v1-20261022','--bindings','government-xl-olympic-installed-dependency-bindings-v3-20261022','--lease-file',str(path)]
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(path),'--ttl','3600','--',sys.executable,str(HERE/'selected_retained_native_neighbours_v7.py'),*args],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
