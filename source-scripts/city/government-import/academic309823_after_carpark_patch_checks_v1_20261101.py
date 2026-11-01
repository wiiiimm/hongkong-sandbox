"""Run unchanged whole-current-domain scope and source runtime checks on private HKUST terrain."""
import sys,uuid,subprocess
from run import ROOT,HERE,read,reservations
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
P='government-xl-academic309823-after-carpark-'
BATCH=P+'patch-checks-v1-20261101'
PATCH=P+'private-inset-v2-20261101'
LOCAL=HERE/'local'/BATCH

def owned():
    assert reservations.owns(read(LOCAL/'reservation.json'))
    commands=[('scope',[sys.executable,str(HERE/'selected_original_retained_patch_scope_v3_20261026.py'),'--batch',P+'patch-scope-v1-20261101','--inventory','government-xl-after-hkust-carpark-renderer-bound-inventory-v1-20261101','--patch',PATCH]),('runtime',[sys.executable,str(HERE/'selected_original_patch_runtime_v7_20261029.py'),'--batch',P+'patch-runtime-v1-20261101','--patch',PATCH,'--capture',P+'current-runtime-v1-20261101'])]
    for name,command in commands:
        assert reservations.owns(read(LOCAL/'reservation.json'))
        with (LOCAL/(name+'.log')).open('w')as log:subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=10800)
        print(name+' complete',flush=True)

if __name__=='__main__':
    if '--owned'in sys.argv:owned()
    else:
        assert not LOCAL.exists()
        resources=['building:'+u for u in ['landsd/309823:0','landsd/309829:0','landsd/336320:0','landsd/26949:0']]+['immutable-source-proof:'+BATCH]
        claim=reservations.claim('academic-private-patch-checks-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim
        execute_reserved(claim['reservation'],LOCAL/'reservation.json',[sys.executable,__file__,'--owned'])
