"""Test source-derived HKUST terrain against the fresh current scene; never publish.

Keep installed carpark terrain targets and complete extent explicit. All subsequent
current actor regressions remain required; candidate creation gives no acceptance.
"""
import sys,uuid
from run import HERE,reservations
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BATCH='government-xl-academic309823-after-carpark-private-inset-v2-20261101'
def main():
    # Keep the lease file outside the builder's immutable per-attempt local folder.
    lp=HERE/'local'/(BATCH+'-lease')/'reservation.json'
    assert not lp.parent.exists()
    resources=['building:'+u for u in ['landsd/309823:0','landsd/309829:0','landsd/336320:0','landsd/26949:0']]+['immutable-source-proof:'+BATCH]
    claim=reservations.claim('academic-current-private-inset-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim
    command=[sys.executable,str(HERE/'selected_original_local_inset_v20_20261101.py'),'--batch',BATCH,'--capture','government-xl-academic309823-after-carpark-current-runtime-v1-20261101','--terrain-check','government-xl-after-disneyland-piers-next-three-terrain-paths-v1-20261030','--uid','landsd/309823:0','--companion','landsd/309829:0','--companion','landsd/336320:0','--cover-native','city/data/government-native-hkust-carpark-original-v1-20261101.json','--parent-capture','government-xl-academic309823-after-carpark-private-inset-v1-20261101']
    return execute_reserved(claim['reservation'],lp,command)
if __name__=='__main__':main()
