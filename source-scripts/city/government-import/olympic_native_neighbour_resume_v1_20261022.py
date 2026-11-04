"""Resume native-only diagnostics under the existing heartbeat supervisor."""
import json,subprocess,sys,uuid
from run import ROOT,HERE,read,save,digest,reservations
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-olympic-station-retained-neighbours-v4-20261022';PRIOR='government-xl-olympic-station-retained-neighbours-v3-20261022'
def main():
 prior=BASE/PRIOR;old=read(prior/'neighbour-inputs.json.gz');report=read(prior/'neighbour-checks.json');audit=read(prior/'termination-audit.json');assert audit['exitCode']==143 and not audit['exactWorkerPidsAlive'];assert len(report['rows'])==len(old['rows'])==613
 for p,h in {**report['inputHashes'],**report['sourceInputHashes']}.items():assert digest((ROOT/p).read_bytes())==h
 assert not(BASE/BATCH).exists();keys=[('building:'if r['building']['uid'].startswith('landsd/')else'source-form:')+r['building']['uid']for r in old['rows']]+['terrain:city/data/terrain.json']
 for p in old['patches']:
  for r in p.get('replacesMany')or[p['replaces']]:keys.append('terrain:'+r['url'])
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),keys,batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=json.loads(json.dumps(claim['reservation'],default=str));path=HERE/'local'/BATCH/'reservation.json';save(path,lease)
 args=['--batch',BATCH,'--scope','government-xl-olympic-station-retained-scope-v1-20261022','--inventory','government-xl-after-aquarium-current-inventory-v1-20261022','--patch','government-xl-81242-retained-native-candidate-v1-20261022','--bindings','government-xl-olympic-installed-dependency-bindings-v3-20261022','--resume-from',PRIOR,'--lease-file',str(path)]
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(path),'--ttl','3600','--',sys.executable,str(HERE/'selected_retained_native_neighbours_v6.py'),*args],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
