"""Continue the exact running scene into retained-context, review and private browsers."""
import os,subprocess,sys,time
from pathlib import Path
from run import ROOT,HERE,read,save
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-island-cheong-shing-repaired-acceptance-chain-v1-20261023';out=base/batch;assert not out.exists();out.mkdir();scene='government-xl-island-cheong-shing-repaired-scene-suite-v1-20261023';patch='government-xl-island-industrial-paired-surface-binding-v6-20261023';native='government-xl-island-cheong-shing-four-source-current-neighbours-v2-20261023';physical='government-xl-island-cheong-shing-physical-review-v1-20261023';refs=[Path(__file__)];completed=[];env=dict(os.environ);env['PATH']='/home/williamli/.nvm/versions/node/v24.18.0/bin:'+env.get('PATH','');env['OPENBLAS_NUM_THREADS']='1';env['PYTHONDONTWRITEBYTECODE']='1'
    state=read(base/'government-xl-scripted-continuation-20261023/island-cheong-shing-repaired-scene-worker-v1.json');pid=state['pid'];deadline=time.monotonic()+3600
    while not(base/scene/'result.json').exists():
        command=Path('/proc')/str(pid)/'cmdline'
        assert command.exists()and b'island_cheong_shing_repaired_scene_suite_v1_20261023.py'in command.read_bytes(),'Scene worker terminal/missing without a receipt; no restart or acceptance'
        assert time.monotonic()<deadline,'Observation window expired; do not infer source failure or restart'
        time.sleep(5)
    r,_=authenticate(base/scene);refs.append(base/scene/'result.json');assert r['status']=='complete-current-scene-evidence-awaiting-physical-browser-publication'
    p,_=authenticate(base/patch);refs.append(base/patch/'result.json');retained=sorted({u for m in p['members']for u in m['replaces']['retainedUids']})
    steps=[('unchanged','unchanged_coordinated_installed_native_context_v1_20261023.py','government-xl-island-cheong-shing-hoi-yu-unchanged-context-v2-20261023',['--owner','landsd/20270:0','--uid','landsd/177605:0','--support','landsd/177604:0','--patch',patch,'--inventory','government-xl-after-fu-tor-loy-current-inventory-v1-20261023','--neighbours',native]),('physical','island_cheong_shing_physical_review_v1_20261023.py',physical,[]),('browser','selected_original_coordinated_staged_browser_v1_20261023.py','government-xl-island-cheong-shing-four-original-private-browser-v1-20261023',['--runtime','government-xl-island-cheong-shing-four-original-runtime-v4-20261023','--patch',patch,'--review',physical,'--support','landsd/20270:0,landsd/159422:0','--support','landsd/274231:0,landsd/269430:0',*[x for u in retained for x in ['--retain-native',u]]])]
    for phase,script,child,args in steps:
        assert not(base/child).exists();log=out/(phase+'.log');command=[sys.executable,str(HERE/script)]
        if phase!='physical':command+=['--batch',child]
        command+=args
        with log.open('w')as f:proc=subprocess.run(command,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT)
        refs.extend([HERE/script,log])
        if proc.returncode:result=dict(uids=p['uids'],status='source-or-script-review-required',stoppedAt=phase,exitCode=proc.returncode,completed=completed,installationApproved=False,sourceGeometryChanges=0);break
        receipt,_=authenticate(base/child);refs.append(base/child/'result.json');completed.append(dict(phase=phase,batch=child,jobId=receipt['jobId']));save(out/'progress.json',dict(completed=completed,installationApproved=False));print(completed[-1],flush=True)
    else:result=dict(uids=p['uids'],status='private-browser-evidence-awaiting-actual-root-image-review-and-guarded-publication',completed=completed,installationApproved=False,sourceGeometryChanges=0)
    save(out/'summary.json',result);module('acceptance_chain_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-repaired-scene-original-review-and-private-browser-continuation',refs,result)

if __name__=='__main__':main()
