"""Run existing private original-terrain builder under canonical source leases."""
import sys,uuid
from run import ROOT,HERE,read,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BATCH='government-xl-southside-private-terrain-candidate-v1-20261028';GROUND='government-xl-la-marina-southside-original-terrain-v1-20261028';CAP='government-xl-la-marina-three-original-assembly-v1-20261028-runtime'
def main():
 base=ROOT/'docs/astra-city/government-import';authenticate(base/GROUND);summary=read(base/GROUND/'summary.json');assert summary['uids']==['landsd/315025:0'];resources=['building:landsd/315025:0',*['source-terrain:'+s for s in summary['sheets']]];assert not(base/BATCH).exists()and not(HERE/'local'/BATCH).exists();claim=reservations.claim('southside-private-terrain-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=HERE/'local'/(BATCH+'-runner')/'reservation.json';execute_reserved(claim['reservation'],lease,[sys.executable,str(HERE/'selected_original_terrain_patch_v2.py'),'--batch',BATCH,'--terrain-check',GROUND,'--capture',CAP])
if __name__=='__main__':main()
