"""Nominate exact cached originals for the current twelve HKUST base-form regressions."""
import sys,uuid
from run import ROOT,HERE,read,reservations
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
P='government-xl-academic309823-after-carpark-'
BATCH=P+'flagged-original-lookup-v2-20261101'
def main():
    local=HERE/'local'/BATCH/'reservation.json';assert not local.parent.exists()
    report=read(ROOT/'docs/astra-city/government-import'/(P+'native-neighbours-v1-20261101')/'summary.json')
    uids=sorted(r['uid']for r in report['basicFlags'])
    claim=reservations.claim('academic-flagged-original-lookup-'+str(uuid.uuid4()),['building:'+u for u in uids]+['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'],claim
    command=[sys.executable,str(HERE/'flagged_neighbour_original_lookup_v3_20261101.py'),'--batch',BATCH,'--capture',P+'current-runtime-v1-20261101','--scope',P+'patch-scope-v1-20261101','--form-checks',P+'native-neighbours-v1-20261101','--extra-sheet','12-NW-6A','--extra-sheet','12-NW-6C']
    return execute_reserved(claim['reservation'],local,command)
if __name__=='__main__':main()
