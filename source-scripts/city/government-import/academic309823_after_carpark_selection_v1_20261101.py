"""Lease exact cached HKUST originals and rebind them to the current7067actor inventory."""
import sys,uuid
from run import ROOT,HERE,reservations
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BATCH='government-xl-academic309823-after-carpark-current-selection-v1-20261101'
def main():
    local=HERE/'local'/BATCH/'reservation.json'
    assert not local.parent.exists()
    uids=['landsd/309823:0','landsd/309829:0','landsd/336320:0']
    claim=reservations.claim('academic-current-selection-'+str(uuid.uuid4()),['building:'+uid for uid in uids]+['building:landsd/26949:0','immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600)
    assert claim['ok'],claim
    command=[sys.executable,str(HERE/'merge_current_original_selections_v1_20261024.py'),'--batch',BATCH,'--inventory','government-xl-after-hkust-carpark-renderer-bound-inventory-v1-20261101','--capture','government-xl-academic309823-library-podium-selection-v1-20261030']
    for uid in uids:command.extend(['--uid',uid])
    return execute_reserved(claim['reservation'],local,command)
if __name__=='__main__':main()
