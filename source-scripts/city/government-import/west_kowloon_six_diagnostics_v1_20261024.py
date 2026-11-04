"""Finish the explicit six-source compute checks serially; never publish or approve."""
from pathlib import Path
import subprocess,sys,traceback
from run import ROOT,HERE,read,save
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';p='government-xl-next-repairs-west-kowloon-bus-';batch=p+'six-compute-sequence-v1-20261024';out=base/batch;assert not out.exists();runtime=p+'six-original-runtime-v2-20261024';authenticate(base/runtime);status=read(base/runtime/'summary.json');assert len(status['rows'])==6 and all(r['status']=='captured'for r in status['rows']);uids=[r['uid']for r in status['rows']]
    attrs=p+'six-original-attributes-v1-20261024';scope=p+'six-original-scope-v1-20261024';low=p+'shaft37934-low-faces-v1-20261024'
    phases=[
        ('attributes','selected_original_render_attributes_v1.py',attrs,['--capture',runtime]),
        ('identity','selected_original_identity_v3.py',p+'six-original-identity-v1-20261024',['--capture',runtime]),
        ('scope','selected_original_model_only_scope_v1_20261023.py',scope,['--runtime',runtime,'--attributes',attrs,'--inventory','government-xl-after-university-hall-current-inventory-v1-20261024']),
        ('foreign','selected_original_model_only_foreign_contacts_v2_20261024.py',p+'six-original-foreign-v1-20261024',['--scope',scope,'--runtime',runtime,'--attributes',attrs]),
        ('shaft-foundation','original_four_world_foundations.py',p+'six-foundation37934-v1-20261024',['--runtime',runtime,'--attributes',attrs,'--uid','landsd/37934:0']),
        ('shaft-low','selected_original_four_world_low_face_context_v1_20261024.py',low,['--runtime',runtime,'--attributes',attrs,'--uid','landsd/37934:0']),
        ('shaft-caps','selected_original_complete_ground_cap_paths_v2_20261024.py',p+'shaft37934-cap-paths-v1-20261024',['--runtime',runtime,'--attributes',attrs,'--low-faces',low,'--uid','landsd/37934:0']),
        ('new-original-pairs','original_assembly_exact_contacts_v1_20261023.py',p+'six-new-original-pairs-v1-20261024',['--capture',runtime,*[v for other in uids if other!='landsd/37934:0'for v in ['--pair','landsd/37934:0,'+other]]]),
        ('plots','original_assembly_context_plot_v3_20261023.py',p+'six-original-plots-v1-20261024',['--runtime',runtime,'--base-height','10']),
    ]
    refs=[Path(__file__),base/runtime/'result.json'];completed=[];out.mkdir();result=dict(uids=uids,sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,publication=False,newlyInstalled=0)
    for phase,script,name,args in phases:
        log=out/(phase+'.log');command=[sys.executable,str(HERE/script),'--batch',name,*args];save(out/(phase+'-command.json'),dict(command=command));assert not(base/name).exists(),'Refuse duplicate or incomplete producer; inspect its receipt/process before resuming'
        with log.open('w')as f:code=subprocess.run(command,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT).returncode
        refs.extend([HERE/script,log,out/(phase+'-command.json')])
        if code:
            result.update(status='held-for-compute-diagnostic-failure',failedPhase=phase,exitCode=code);break
        receipt,_=authenticate(base/name);refs.append(base/name/'result.json');completed.append(dict(phase=phase,batch=name,jobId=receipt['jobId']));print(completed[-1],flush=True)
    else:result['status']='six-source-script-diagnostics-complete-awaiting-root-review'
    result.update(completed=completed,heldForHumanDecision=False,aiGeometryModellingRequired=False,permanentRejection=False,qualification='Explicit immutable originals only, full current source/basic/native scope and new companion contacts. Completed diagnostics preserve every raw negative and transfer no historical approval. No publication, installation, optimisation, geometry edits or relaxed validators. ROOT physical/identity/current-scene and actual desktop/mobile browser review still required.')
    save(out/'summary.json',result);module('west_six_compute_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'explicit-six-original-compute-diagnostic-sequence',refs,result)

if __name__=='__main__':main()
