"""Test authentic full provider TIN and automatically run current whole-scene diagnostics.

No public writes or approval. Each stage uses existing validators and exact leases.
"""
import sys,uuid,subprocess
from run import ROOT,HERE,read,reservations
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
P='government-xl-academic309823-after-carpark-'
PATCH=P+'private-full-tin-v1-20261101'
BATCH=PATCH+'-sequence'
BASE=ROOT/'docs/astra-city/government-import'
LOCAL=HERE/'local'/BATCH
SCOPE=P+'full-tin-scope-v1-20261101'
RUNTIME=P+'full-tin-runtime-v1-20261101'
BINDINGS=P+'full-tin-installed-bindings-v1-20261101'
ATTR=P+'full-tin-attributes-v1-20261101'

def owned():
    lease=LOCAL/'reservation.json'
    commands=[('terrain',[sys.executable,str(HERE/'selected_original_local_full_tin_v22_20261101.py'),'--batch',PATCH,'--capture',P+'current-runtime-v1-20261101','--terrain-check','government-xl-after-disneyland-piers-next-three-terrain-paths-v1-20261030','--uid','landsd/309823:0','--companion','landsd/309829:0','--companion','landsd/336320:0','--cover-native','city/data/government-native-hkust-carpark-original-v1-20261101.json','--parent-capture',P+'private-inset-v2-20261101','--protection-scope',P+'patch-scope-v1-20261101','--protect-form','landsd/309839:0','--protect-form','landsd/339022:0']),('scope',[sys.executable,str(HERE/'selected_original_retained_patch_scope_v3_20261026.py'),'--batch',SCOPE,'--inventory','government-xl-after-hkust-carpark-renderer-bound-inventory-v1-20261101','--patch',PATCH]),('runtime',[sys.executable,str(HERE/'selected_original_patch_runtime_v7_20261029.py'),'--batch',RUNTIME,'--patch',PATCH,'--capture',P+'current-runtime-v1-20261101']),('bindings',[sys.executable,str(HERE/'selected_current_installed_dependency_bindings_v2_20261028.py'),'--batch',BINDINGS,'--scope',SCOPE]),('neighbours',[sys.executable,str(HERE/'selected_retained_native_neighbours_v10_20261101.py'),'--batch',P+'full-tin-native-neighbours-v1-20261101','--scope',SCOPE,'--inventory','government-xl-after-hkust-carpark-renderer-bound-inventory-v1-20261101','--patch',PATCH,'--bindings',BINDINGS,'--lease-file',str(lease)]),('attributes',[sys.executable,str(HERE/'selected_original_render_attributes_v1.py'),'--batch',ATTR,'--capture',RUNTIME])]
    for uid in ['landsd/309823:0','landsd/309829:0','landsd/336320:0']:
        suffix=uid.split('/')[1].replace(':','-')
        commands.append(('four-world-'+suffix,[sys.executable,str(HERE/'original_four_world_foundation_context_v1_20261025.py'),'--batch',P+'full-tin-four-world-'+suffix+'-v1-20261101','--runtime',RUNTIME,'--attributes',ATTR,'--uid',uid]))
    for name,command in commands:
        assert reservations.owns(read(lease))
        if name!='terrain':assert read(BASE/PATCH/'result.json')['status']=='private-terrain-validator-passed'
        with (LOCAL/(name+'.log')).open('w')as log:subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=10800)
        print(name+' complete',flush=True)

if __name__=='__main__':
    if '--owned'in sys.argv:owned()
    else:
        assert not LOCAL.exists()and not (BASE/PATCH).exists()
        forms=read(BASE/(P+'patch-scope-v1-20261101')/'form-obligations.json.gz')
        resources={('building:'if f['uid'].startswith('landsd/')else'source-form:')+f['uid']for f in forms}
        resources.update('building:'+uid for uid in ['landsd/309823:0','landsd/309829:0','landsd/336320:0','landsd/26949:0'])
        resources.update(['terrain:city/data/terrain.json','terrain:city/data/government-native-hkust-carpark-original-v1-20261101.json','immutable-source-proof:'+BATCH])
        claim=reservations.claim('academic-full-original-tin-'+str(uuid.uuid4()),sorted(resources),batch=BATCH,ttl=3600);assert claim['ok'],claim
        execute_reserved(claim['reservation'],LOCAL/'reservation.json',[sys.executable,__file__,'--owned'])
