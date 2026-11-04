"""Recheck the complete four-original scene after exact fourth-source terrain repair."""
from pathlib import Path
import os,subprocess,sys
from run import ROOT,HERE,save
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-island-cheong-shing-repaired-scene-suite-v1-20261023';out=base/batch;assert not out.exists()
    patch='government-xl-island-industrial-paired-surface-binding-v6-20261023';proof,_=authenticate(base/patch);assert proof['status']=='private-coordinated-surface-validator-passed'
    runtime='government-xl-island-cheong-shing-four-original-runtime-v4-20261023';attrs='government-xl-island-cheong-shing-four-original-attributes-v1-20261023';continuous='government-xl-island-cheong-shing-current-continuous-v2-20261023';coverage='government-xl-island-cheong-shing-current-exact-coverage-v2-20261023';scope='government-xl-island-cheong-shing-four-source-current-scope-v2-20261023';inventory='government-xl-after-fu-tor-loy-current-inventory-v1-20261023'
    steps=[('runtime','selected_original_coordinated_runtime_v3_20261023.py',runtime,['--patch',patch,'--capture','government-xl-island-cheong-shing-four-original-runtime-v3-20261023']),('continuous','selected_original_continuous_ground_context_v1.py',continuous,['--runtime',runtime]),('coverage','selected_original_exact_residual_coverage_v1.py',coverage,['--runtime',runtime,'--context',continuous])]
    for number in ['20270','159422','269430','274231']:
        steps.append(('foundations-'+number,'original_four_world_foundations.py','government-xl-island-cheong-shing-current-foundations-'+number+'-v2-20261023',['--runtime',runtime,'--attributes',attrs,'--uid','landsd/'+number+':0']))
    for number in ['159422','269430']:
        steps.append(('rims-'+number,'original_four_world_exact_rims_v3.py','government-xl-island-cheong-shing-current-rims-'+number+'-v2-20261023',['--runtime',runtime,'--attributes',attrs,'--continuous',continuous,'--coverage',coverage,'--uid','landsd/'+number+':0']))
    steps += [('scope','selected_original_coordinated_scope_v1_20261023.py',scope,['--inventory',inventory,'--patch',patch]),('neighbours','selected_coordinated_native_neighbours_v1_20261023.py','government-xl-island-cheong-shing-four-source-current-neighbours-v2-20261023',['--scope',scope,'--inventory',inventory,'--patch',patch,'--bindings','government-xl-island-industrial-installed-dependency-bindings-v1-20261023'])]
    out.mkdir();refs=[Path(__file__),base/patch/'result.json'];completed=[];env=dict(os.environ);env['PATH']='/home/williamli/.nvm/versions/node/v24.18.0/bin:'+env.get('PATH','');env['OPENBLAS_NUM_THREADS']='1';env['PYTHONDONTWRITEBYTECODE']='1'
    for phase,script,child,args in steps:
        assert not(base/child).exists();log=out/(phase+'.log')
        with log.open('w')as f:r=subprocess.run([sys.executable,str(HERE/script),'--batch',child,*args],cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT)
        refs.extend([HERE/script,log])
        if r.returncode:
            result=dict(uids=proof['uids'],status='script-or-physical-investigation',stoppedAt=phase,exitCode=r.returncode,completed=completed,sourceGeometryChanges=0,installationApproved=False);break
        receipt,_=authenticate(base/child);refs.append(base/child/'result.json');completed.append(dict(phase=phase,batch=child,jobId=receipt['jobId']));save(out/'progress.json',dict(completed=completed,installationApproved=False));print(completed[-1],flush=True)
    else:result=dict(uids=proof['uids'],status='complete-current-scene-evidence-awaiting-physical-browser-publication',completed=completed,sourceGeometryChanges=0,installationApproved=False)
    save(out/'summary.json',result);module('repaired_scene_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'complete-four-original-scene-after-exact-terrain-gap-repair',refs,result)

if __name__=='__main__':main()
