"""Immediately run reproducible source/foundation evidence; never approve a model."""
import argparse,subprocess,sys
from pathlib import Path
from run import ROOT,HERE,read,save
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','uid']:p.add_argument('--'+k,required=True)
    a=p.parse_args();assert a.batch.startswith('government-xl-')and'/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists()
    receipt,_=authenticate(base/a.runtime);assert receipt['uids']==[a.uid]
    names={k:a.batch+'-'+k for k in ['attributes','foundations','plots','boundary','continuous','coverage','rims']}
    steps=[
        ('attributes','selected_original_render_attributes_v1.py',['--capture',a.runtime]),
        ('foundations','original_four_world_foundations.py',['--runtime',a.runtime,'--attributes',names['attributes'],'--uid',a.uid]),
        ('plots','selected_original_identity_plot_v1.py',['--capture',a.runtime,'--uid',a.uid]),
        ('boundary','selected_original_boundary_context_v1.py',['--capture',a.runtime,'--uid',a.uid]),
        ('continuous','selected_original_continuous_ground_context_v1.py',['--runtime',a.runtime]),
        ('coverage','selected_original_exact_residual_coverage_v1.py',['--runtime',a.runtime,'--context',names['continuous']]),
        ('rims','original_four_world_exact_rims_v2.py',['--runtime',a.runtime,'--attributes',names['attributes'],'--continuous',names['continuous'],'--coverage',names['coverage'],'--uid',a.uid]),
    ]
    out.mkdir();refs=[Path(__file__),base/a.runtime/'result.json'];completed=[]
    result=dict(uids=[a.uid],batches=names,installationApproved=False,publication=False,sourceGeometryChanges=0)
    for phase,script,tail in steps:
        assert not(base/names[phase]).exists()
        logpath=out/(phase+'.log')
        with logpath.open('w')as log:
            code=subprocess.run([sys.executable,str(HERE/script),'--batch',names[phase],*tail],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT).returncode
        refs.extend([HERE/script,logpath])
        if code:
            result.update(status='script-or-physical-investigation',stoppedAt=phase,exitCode=code)
            break
        r,_=authenticate(base/names[phase]);refs.append(base/names[phase]/'result.json');completed.append(dict(phase=phase,jobId=r['jobId']))
        print(dict(phase=phase,jobId=r['jobId']),flush=True)
    else:result['status']='prephysical-evidence-complete-awaiting-identity-and-browser'
    result['completed']=completed
    save(out/'summary.json',result)
    module('prephysical_suite_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'immediate-original-source-prephysical-evidence-suite',refs,result)

if __name__=='__main__':main()
