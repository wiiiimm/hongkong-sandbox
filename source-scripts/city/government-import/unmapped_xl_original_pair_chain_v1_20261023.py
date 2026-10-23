"""Acquire the two exact unmapped original source keys serially; never install."""
from pathlib import Path
import subprocess,sys
from run import ROOT,HERE,save
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-unmapped-two-original-acquisition-chain-v1-20261023';out=base/batch;assert not out.exists();out.mkdir();refs=[Path(__file__)];rows=[];script=HERE/'unmapped_xl_original_acquire_v1_20261023.py';refs.append(script)
    for model in ['B349971856402063C0','B352981210001063C0']:
        child='government-xl-unmapped-'+model[1:11]+'-original-acquire-v1-20261023';assert not(base/child).exists();log=out/(model+'.log')
        with log.open('w')as f:p=subprocess.run([sys.executable,str(script),'--model-id',model],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
        refs.append(log);row=dict(modelId=model,exitCode=p.returncode)
        if not p.returncode:r,_=authenticate(base/child);refs.append(base/child/'result.json');row.update(jobId=r['jobId'],sourceRecovered=r['sourceRecovered'],status=r['status'])
        rows.append(row);save(out/'progress.json',dict(rows=rows,installationApproved=False));print(row,flush=True)
    result=dict(uids=[],rows=rows,sourceGeometryChanges=0,sourceIdentityAccepted=False,installationApproved=False,newlyInstalled=0,permanentRejection=False);save(out/'summary.json',result);module('unmapped_pair_chain_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'unmapped-original-pair-source-only-acquisition-chain',refs,result)

if __name__=='__main__':main()
