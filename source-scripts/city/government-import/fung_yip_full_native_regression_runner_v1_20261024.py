"""Supervise existing whole-region checks under the complete current resource lease."""
import subprocess,sys,json,uuid
from run import ROOT,HERE,read,save,reservations
P='government-xl-fung-yip-full-native-domain-';BATCH=P+'native-regression-v1-20261024'
def main():
 scope=P+'scope-v1-20261024';base=ROOT/'docs/astra-city/government-import';forms=read(base/scope/'form-obligations.json.gz');old='city/data/government-native-upton-certified6170-joint-original-dimension-v2-20261014.json'
 keys=sorted([('building:'if f['uid'].startswith('landsd/')else'source-form:')+f['uid']for f in forms]+['terrain:city/data/terrain.json','terrain:'+old]);claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),keys,batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation'];path=HERE/'local'/BATCH/'reservation.json';save(path,json.loads(json.dumps(lease,default=str)))
 command=[sys.executable,str(HERE/'selected_retained_native_neighbours_v8_20261024.py'),'--batch',BATCH,'--scope',scope,'--inventory','government-xl-after-royal-green8-current-inventory-v1-20261024','--patch',P+'replacement-binding-v1-20261024','--bindings',P+'dependency-bindings-v1-20261024','--lease-file',str(path)]
 try:subprocess.run([sys.executable,str(HERE/'bounded_reserved_runner_v2_20261022.py'),str(path),*command],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
