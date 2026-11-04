"""Capture repaired terrain and run shared whole-source four-world evidence once."""
import subprocess,sys
from pathlib import Path
from run import ROOT,HERE,save
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-island-industrial-repaired-evidence-suite-v1-20261023';out=base/batch;assert not out.exists();out.mkdir()
    runtime='government-xl-island-industrial-paired-current-runtime-v2-20261023';attributes='government-xl-island-industrial-three-original-attributes-v1-20261023';continuous='government-xl-island-industrial-repaired-continuous-v1-20261023';coverage='government-xl-island-industrial-repaired-exact-coverage-v1-20261023'
    steps=[('runtime','selected_original_coordinated_runtime_v1_20261023.py',runtime,['--patch','government-xl-island-industrial-paired-surface-binding-v4-20261023','--capture','government-xl-island-industrial-three-original-current-capture-v1-20261023'])]
    for key in ['20270','159422','269430']:steps.append(('foundations-'+key,'original_four_world_foundations.py','government-xl-island-industrial-repaired-foundations-'+key+'-v1-20261023',['--runtime',runtime,'--attributes',attributes,'--uid','landsd/'+key+':0']))
    steps.extend([('continuous','selected_original_continuous_ground_context_v1.py',continuous,['--runtime',runtime]),('coverage','selected_original_exact_residual_coverage_v1.py',coverage,['--runtime',runtime,'--context',continuous])])
    for key in ['20270','159422','269430']:steps.append(('rims-'+key,'original_four_world_exact_rims_v3.py','government-xl-island-industrial-repaired-rims-'+key+'-v1-20261023',['--runtime',runtime,'--attributes',attributes,'--continuous',continuous,'--coverage',coverage,'--uid','landsd/'+key+':0']))
    refs=[Path(__file__)];completed=[];result=dict(uids=['landsd/20270:0','landsd/159422:0','landsd/269430:0'],installationApproved=False,sourceGeometryChanges=0)
    for name,script,child,tail in steps:
        assert not(base/child).exists();log=out/(name+'.log')
        with log.open('w')as handle:p=subprocess.run([sys.executable,str(HERE/script),'--batch',child,*tail],cwd=ROOT,stdout=handle,stderr=subprocess.STDOUT)
        refs.extend([HERE/script,log])
        if p.returncode:result.update(status='physical-or-script-investigation',stoppedAt=name,exitCode=p.returncode);break
        receipt,_=authenticate(base/child);refs.append(base/child/'result.json');completed.append(dict(phase=name,batch=child,jobId=receipt['jobId']));save(out/'progress.json',dict(completed=completed,installationApproved=False));print(completed[-1],flush=True)
    else:result['status']='numerical-evidence-complete-not-model-acceptance'
    result['completed']=completed;save(out/'summary.json',result);module('repair_suite_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'repaired-pair-shared-complete-fourworld-evidence-suite',refs,result)

if __name__=='__main__':main()
