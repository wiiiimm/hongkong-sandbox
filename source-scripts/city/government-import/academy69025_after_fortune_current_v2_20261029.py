"""Advance the Academy administration-block original through current scripted physical evidence.

No acquisition, acceptance, model edits or publication. Existing guards and
reservation runner are used unchanged; per-source failures remain explicit.
"""
import argparse,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved

BATCH='government-xl-academy69025-after-fortune-current-v2-20261029'
CAPTURE='government-xl-six-current-clearance-v1-20261029-runtime'
UIDS=['landsd/69025:0']

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--owned',action='store_true');args=ap.parse_args()
    base=ROOT/'docs/astra-city/government-import';out=base/BATCH;lp=HERE/'local'/BATCH/'reservation.json';assert not out.exists()
    if not args.owned:
        assert not lp.parent.exists()
        claim=reservations.claim('academy-current-clearance-'+str(uuid.uuid4()),['building:'+u for u in UIDS]+['terrain:city/data/terrain.json'],batch=BATCH,ttl=3600);assert claim['ok']
        return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease);out.mkdir();refs=[Path(__file__)];completed=[]
    uidargs=[x for uid in UIDS for x in ['--uid',uid]]
    phases=[('selection','selected_original_refresh_selection_v1.py',['--capture',CAPTURE,*uidargs]),
            ('identity','selected_original_identity_v3_20261023.py',['--capture',BATCH+'-selection']),
            ('runtime','selected_original_current_capture_v3.py',['--capture',BATCH+'-selection',*uidargs]),
            ('attributes','selected_original_render_attributes_v1.py',['--capture',BATCH+'-runtime'])]
    phases += [('foundation-'+u.split('/')[1].replace(':','-'),'original_four_world_foundation_context_v1_20261025.py',['--runtime',BATCH+'-runtime','--attributes',BATCH+'-attributes','--uid',u])for u in UIDS]
    phases += [('model-scope','selected_original_model_only_scope_v1_20261023.py',['--runtime',BATCH+'-runtime','--attributes',BATCH+'-attributes','--inventory','government-xl-after-fortune-current-inventory-v1-20261029'])]
    for phase,script,tail in phases:
        assert reservations.owns(lease);log=out/(phase+'.log')
        with log.open('w')as stream:
            process=subprocess.run([sys.executable,str(HERE/script),'--batch',BATCH+'-'+phase,*tail],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
        record=dict(phase=phase,batch=BATCH+'-'+phase,exitCode=process.returncode);refs.extend([HERE/script,log])
        if process.returncode:
            completed.append(record);print(record,flush=True);break
        receipt,_=authenticate(base/record['batch']);record['jobId']=receipt['jobId'];completed.append(record);refs.append(base/record['batch']/'result.json');print(record,flush=True)
    result=dict(uids=UIDS,completed=completed,allPhasesCompleted=len(completed)==len(phases)and all(r['exitCode']==0 for r in completed),sourceGeometryChanges=0,identityAccepted=False,physicalAccepted=False,installationApproved=False,qualification='Fresh exact-source selection, identity diagnostics, actual current renderer capture, complete four-world attributes/foundations and full installed-actor model scope. All raw failures retained. No source acquisition, model edits, terrain changes, optimisation, suppression or installation.')
    save(out/'summary.json',result);assert reservations.owns(lease)
    module('six_clearance_sequence_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'academy-current-clearance-scripted-evidence-sequence',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
