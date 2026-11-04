"""Lease-owned canonical staging of the exact audited original; zero public writes."""
import sys,uuid
from run import ROOT,HERE,read,reservations
from observed_reserved_runner_v4_20261103 import execute_reserved
from parkview256319_installed_support_adapter_v1_20261104 import configure
BATCH='government-xl-parkview256319-reviewed-current-original-qualified-stage-v1-20261104'
def main():
    lp=HERE/'local'/(BATCH+'-control')/'reservation.json';out=ROOT/'docs/astra-city/government-import'/BATCH
    resources=sorted(['building:'+u for u in ['landsd/256319:0','landsd/254491:0','landsd/256116:0']]+['terrain:city/data/terrain.json','immutable-source-proof:'+BATCH])
    if '--owned'not in sys.argv:
        assert not out.exists()and not lp.parent.exists();c=reservations.claim('parkview-canonical-stage-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==set(resources)
    stage=configure();assert stage.BATCH==BATCH;stage.main();assert reservations.owns(lease)
if __name__=='__main__':main()
