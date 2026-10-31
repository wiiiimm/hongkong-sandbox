"""Resume the already-reviewed Lookout Tower with current source and coastal guards."""
import argparse
import subprocess
import sys
import uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from primrose_compound_foundation_v2_20261015 import module
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BATCH='government-xl-lookout99482-after-sha-tin-v1-20261029'
BASE=ROOT/'docs/astra-city/government-import'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--owned',action='store_true');args=ap.parse_args();out=BASE/BATCH;lp=HERE/'local'/BATCH/'reservation.json';assert not out.exists()
    if not args.owned:
        assert not lp.parent.exists();claim=reservations.claim('lookout99482-current-'+str(uuid.uuid4()),['building:landsd/99482:0','terrain:city/data/terrain.json'],batch=BATCH,ttl=3600);assert claim['ok'],claim
        return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease);out.mkdir();refs=[Path(__file__)];completed=[]
    phases=[('selection','selected_original_refresh_selection_v1.py',['--capture','government-xl-runtime-fit-99482-scoped-current-capture-v3-20261022','--uid','landsd/99482:0']),('runtime','selected_original_current_capture_v3.py',['--capture',BATCH+'-selection','--uid','landsd/99482:0']),('inset','selected_original_local_inset_v14_20261029.py',['--capture',BATCH+'-runtime','--terrain-check','government-xl-runtime-fit-99482-original-terrain-recovery-v4-20261022','--uid','landsd/99482:0'])]
    for phase,script,tail in phases:
        assert reservations.owns(lease);log=out/(phase+'.log')
        with log.open('w')as f:proc=subprocess.run([sys.executable,str(HERE/script),'--batch',BATCH+'-'+phase,*tail],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
        refs.extend([HERE/script,log])
        if proc.returncode:
            result=dict(uids=['landsd/99482:0'],status='script-adapter-investigation',failedPhase=phase,exitCode=proc.returncode,completed=completed,sourceGeometryChanges=0,installationApproved=False,publication=False)
            break
        receipt,pins=authenticate(BASE/(BATCH+'-'+phase));refs.append(BASE/(BATCH+'-'+phase)/'result.json');completed.append(dict(phase=phase,batch=BATCH+'-'+phase,jobId=receipt['jobId']));print(completed[-1],flush=True)
    else:
        inset=read(BASE/(BATCH+'-inset')/'summary.json');result=dict(uids=['landsd/99482:0'],status=inset.get('status'),reason=inset.get('reason'),completed=completed,sourceGeometryChanges=0,installationApproved=False,publication=False,qualification='Resumed existing source scope and cached original terrain, rebound exact current map. New parent-retention constructor preserves coastal and height guards. Inset diagnostics are not installation approval.')
    save(out/'summary.json',result);assert reservations.owns(lease)
    module('lookout_after_sha_tin_sequence_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-reviewed-lookout-original-coastal-terrain-resumption',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
