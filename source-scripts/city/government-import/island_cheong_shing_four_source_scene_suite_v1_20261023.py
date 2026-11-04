"""Fresh four-source terrain binding, actual renderer and full neighbour checks."""
from pathlib import Path
import subprocess,sys
from run import ROOT,HERE,save
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-island-cheong-shing-four-source-scene-suite-v1-20261023';out=base/batch;assert not out.exists();out.mkdir();scope='government-xl-island-cheong-shing-four-source-current-scope-v1-20261023';surface='government-xl-island-industrial-paired-surface-binding-v5-20261023';inventory='government-xl-after-fu-tor-loy-current-inventory-v1-20261023';steps=[
      ('metadata','island_cheong_shing_four_source_terrain_scope_v1_20261023.py','government-xl-island-cheong-shing-four-source-terrain-scope-v1-20261023',[]),
      ('surface','island_industrial_paired_surface_binding_v5_20261023.py',surface,[]),
      ('runtime','selected_original_coordinated_runtime_v3_20261023.py','government-xl-island-cheong-shing-four-original-runtime-v3-20261023',['--patch',surface,'--capture','government-xl-island-cheong-shing-four-original-runtime-v2-20261023']),
      ('scope','selected_original_coordinated_scope_v1_20261023.py',scope,['--inventory',inventory,'--patch',surface]),
      ('neighbours','selected_coordinated_native_neighbours_v1_20261023.py','government-xl-island-cheong-shing-four-source-current-neighbours-v1-20261023',['--scope',scope,'--inventory',inventory,'--patch',surface,'--bindings','government-xl-island-industrial-installed-dependency-bindings-v1-20261023'])]
    refs=[Path(__file__)];completed=[];result=dict(uids=['landsd/20270:0','landsd/159422:0','landsd/269430:0','landsd/274231:0'],sourceGeometryChanges=0,installationApproved=False)
    for phase,script,child,args in steps:
        assert not(base/child).exists();command=[sys.executable,str(HERE/script)]
        if phase not in ['metadata','surface']:command+=['--batch',child]
        command+=args;log=out/(phase+'.log')
        with log.open('w')as f:p=subprocess.run(command,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
        refs.extend([HERE/script,log])
        if p.returncode:result.update(status='scene-script-investigation',stoppedAt=phase,exitCode=p.returncode);break
        r,_=authenticate(base/child);refs.append(base/child/'result.json');completed.append(dict(phase=phase,batch=child,jobId=r['jobId']));save(out/'progress.json',dict(completed=completed,installationApproved=False));print(completed[-1],flush=True)
    else:result['status']='scene-evidence-complete-not-publication-approval'
    result['completed']=completed;save(out/'summary.json',result);module('four_source_scene_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'fresh-four-source-scoped-original-scene-evidence-suite',refs,result)

if __name__=='__main__':main()
