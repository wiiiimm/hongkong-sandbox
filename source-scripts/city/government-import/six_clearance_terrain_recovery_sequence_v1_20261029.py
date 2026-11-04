"""Try existing original-TIN recovery for three measured upward-burial cases.

Each private proposal retains all current terrain validators. A failed source
does not stop the other sources. Nothing is published or automatically accepted.
"""
import argparse,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved

BATCH='government-xl-six-clearance-terrain-recovery-v1-20261029'
CAPTURE='government-xl-six-current-clearance-v1-20261029-runtime'
UIDS=['landsd/242706:0','landsd/69025:0','landsd/181489:0']

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--owned',action='store_true');a=ap.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/BATCH;lp=HERE/'local'/BATCH/'reservation.json';assert not out.exists()
    if not a.owned:
        assert not lp.parent.exists();claim=reservations.claim('three-original-terrain-recovery-'+str(uuid.uuid4()),['building:'+u for u in UIDS]+['terrain:city/data/terrain.json'],batch=BATCH,ttl=3600);assert claim['ok']
        return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease);out.mkdir();refs=[Path(__file__)];completed=[]
    def run(phase,script,tail):
        assert reservations.owns(lease);batch=BATCH+'-'+phase;log=out/(phase+'.log')
        with log.open('w')as stream:p=subprocess.run([sys.executable,str(HERE/script),'--batch',batch,*tail],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
        item=dict(phase=phase,batch=batch,exitCode=p.returncode);refs.extend([HERE/script,log])
        if p.returncode==0:
            receipt,_=authenticate(base/batch);item['jobId']=receipt['jobId'];refs.append(base/batch/'result.json')
        completed.append(item);print(item,flush=True);return p.returncode==0
    args=[x for uid in UIDS for x in ['--uid',uid]]
    if run('cached-terrain','cached_original_terrain_selected_v1.py',['--capture',CAPTURE,*args]):
        for uid in UIDS:
            part=uid.split('/')[1].replace(':','-');inset=part+'-inset';runtime=part+'-runtime';attrs=part+'-attributes'
            if not run(inset,'selected_original_local_inset_v14_20261029.py',['--capture',CAPTURE,'--terrain-check',BATCH+'-cached-terrain','--uid',uid]):continue
            proposal=read(base/(BATCH+'-'+inset)/'result.json')
            if not proposal.get('candidate'):continue
            if not run(runtime,'selected_original_patch_runtime_v2.py',['--patch',BATCH+'-'+inset,'--capture',CAPTURE]):continue
            if not run(attrs,'selected_original_render_attributes_v1.py',['--capture',BATCH+'-'+runtime]):continue
            run(part+'-foundations','original_four_world_foundation_context_v1_20261025.py',['--runtime',BATCH+'-'+runtime,'--attributes',BATCH+'-'+attrs,'--uid',uid])
    result=dict(uids=UIDS,completed=completed,sourceGeometryChanges=0,physicalAccepted=False,installationApproved=False,publication=False,qualification='Three source-specific original-TIN private proposals and actual renderer/four-world foundation evidence where construction succeeds. Failed proposals and all source identity/contact/terrain/neighbour/browser/publication obligations remain binding. No optimisation, source modelling, or installed credit.')
    save(out/'summary.json',result);assert reservations.owns(lease)
    module('three_original_recovery_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'three-upward-burial-original-tin-private-recovery-sequence',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
