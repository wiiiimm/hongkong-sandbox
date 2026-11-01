"""Complete established four-world foundation diagnostics for three unchanged HKUST originals."""
import sys,uuid,subprocess
from run import ROOT,HERE,read,reservations
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
P='government-xl-academic309823-after-carpark-'
BATCH=P+'four-world-sequence-v1-20261101'
LOCAL=HERE/'local'/BATCH
ATTR=P+'patch-attributes-v1-20261101'
UIDS=['landsd/309823:0','landsd/309829:0','landsd/336320:0']
def owned():
    commands=[('attributes',[sys.executable,str(HERE/'selected_original_render_attributes_v1.py'),'--batch',ATTR,'--capture',P+'patch-runtime-v1-20261101'])]
    for uid in UIDS:
        suffix=uid.split('/')[1].replace(':','-')
        commands.append((suffix,[sys.executable,str(HERE/'original_four_world_foundation_context_v1_20261025.py'),'--batch',P+'four-world-'+suffix+'-v1-20261101','--runtime',P+'patch-runtime-v1-20261101','--attributes',ATTR,'--uid',uid]))
    for name,command in commands:
        assert reservations.owns(read(LOCAL/'reservation.json'))
        with (LOCAL/(name+'.log')).open('w')as log:subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=10800)
        print(name+' complete',flush=True)
if __name__=='__main__':
    if '--owned'in sys.argv:owned()
    else:
        assert not LOCAL.exists()
        claim=reservations.claim('academic-current-four-world-'+str(uuid.uuid4()),['building:'+u for u in UIDS]+['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'],claim
        execute_reserved(claim['reservation'],LOCAL/'reservation.json',[sys.executable,__file__,'--owned'])
