"""Run full replacement-aware Basic/native regressions under complete affected-source leases."""
import sys,uuid,subprocess
from run import ROOT,HERE,read,reservations
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
P='government-xl-academic309823-after-carpark-'
BATCH=P+'neighbour-sequence-v1-20261101'
BASE=ROOT/'docs/astra-city/government-import'
LOCAL=HERE/'local'/BATCH
SCOPE=P+'patch-scope-v1-20261101'
BINDINGS=P+'installed-bindings-v1-20261101'
PATCH=P+'private-inset-v2-20261101'

def owned():
    lease=LOCAL/'reservation.json'
    commands=[('bindings',[sys.executable,str(HERE/'selected_current_installed_dependency_bindings_v2_20261028.py'),'--batch',BINDINGS,'--scope',SCOPE]),('neighbours',[sys.executable,str(HERE/'selected_retained_native_neighbours_v10_20261101.py'),'--batch',P+'native-neighbours-v1-20261101','--scope',SCOPE,'--inventory','government-xl-after-hkust-carpark-renderer-bound-inventory-v1-20261101','--patch',PATCH,'--bindings',BINDINGS,'--lease-file',str(lease)])]
    for name,command in commands:
        assert reservations.owns(read(lease))
        with (LOCAL/(name+'.log')).open('w')as log:subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=10800)
        print(name+' complete',flush=True)

if __name__=='__main__':
    if '--owned'in sys.argv:owned()
    else:
        assert not LOCAL.exists()
        forms=read(BASE/SCOPE/'form-obligations.json.gz');scope=read(BASE/SCOPE/'scope.json')
        resources={('building:'if f['uid'].startswith('landsd/')else'source-form:')+f['uid']for f in forms}
        resources.update('building:'+uid for uid in scope['uids'])
        resources.update(['terrain:city/data/terrain.json','terrain:city/data/government-native-hkust-carpark-original-v1-20261101.json','immutable-source-proof:'+BATCH])
        claim=reservations.claim('academic-full-current-neighbours-'+str(uuid.uuid4()),sorted(resources),batch=BATCH,ttl=3600);assert claim['ok'],claim
        execute_reserved(claim['reservation'],LOCAL/'reservation.json',[sys.executable,__file__,'--owned'])
