"""Run both exact original pier captures under existing source/terrain leases."""
import argparse,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BATCH='government-xl-disneyland-piers-current-runtime-sequence-v1-20261029';BASE=ROOT/'docs/astra-city/government-import'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--owned',action='store_true');a=ap.parse_args();out=BASE/BATCH;lp=HERE/'local'/BATCH/'reservation.json';assert not out.exists()
    uids=['landsd/75642:0','landsd/75643:0'];resources=['building:'+u for u in uids]+['terrain:city/data/terrain.json']
    if not a.owned:
        assert not lp.parent.exists();claim=reservations.claim('disneyland-piers-current-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim
        return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease);out.mkdir();refs=[Path(__file__)];completed=[]
    interface=HERE/'disneyland_piers_feature_interface_v1_20261029.mjs';report=out/'feature-interface.json'
    subprocess.run(['node',str(interface),str(report)],cwd=ROOT,check=True);assert read(report)['passed'];refs.extend([interface,report])
    for uid in uids:
        sid=uid.split('/')[1].split(':')[0];selection='government-xl-disneyland-pier-'+sid+'-scoped-selection-v1-20261029';batch='government-xl-disneyland-pier-'+sid+'-current-runtime-v1-20261029'
        authenticate(BASE/selection);assert reservations.owns(lease)
        log=out/(sid+'-runtime.log');script=HERE/'selected_original_current_capture_v3.py'
        with log.open('w')as stdout:proc=subprocess.run([sys.executable,str(script),'--batch',batch,'--capture',selection,'--uid',uid],cwd=ROOT,stdout=stdout,stderr=subprocess.STDOUT)
        refs.extend([script,log]);record=dict(uid=uid,batch=batch,exitCode=proc.returncode)
        if proc.returncode:completed.append(record);break
        receipt,_=authenticate(BASE/batch);record['jobId']=receipt['jobId'];refs.append(BASE/batch/'result.json');completed.append(record);print(record,flush=True)
    result=dict(uids=uids,completed=completed,allRuntimeCapturesCompleted=len(completed)==2 and all(r['exitCode']==0 for r in completed),sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,publication=False,qualification='Two source-specific identity extent scopes and exact current production geometry capture only. Real terrain/placement warnings stay recorded, not waived. No native geometry modelling, suppression, source installation or optimisation.')
    save(out/'summary.json',result);assert reservations.owns(lease);module('disneyland_runtime_sequence_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'two-current-original-pier-runtime-captures-under-existing-leases',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
