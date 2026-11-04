"""Continue three available XL originals while preserving all previous source holds."""
from concurrent.futures import ThreadPoolExecutor
import os
import subprocess
import sys
from run import ROOT,HERE,read,save
from next_three_current_repairs_v1_20261023 import work as current_work

BASE=ROOT/'docs/astra-city/government-import'
DOC=BASE/'government-xl-next-available-three-source-trials-driver-v1-20261023'
GROUPS=[('university-hall-93417',['landsd/93417:0'],'government-xl-remaining-178-v3-current-scene-v1-20261023-chunk-02-runtime'),
        ('beverly-sung-fung',['landsd/256334:0','landsd/79098:0'],'government-xl-remaining-178-v3-current-scene-v1-20261023-chunk-04-runtime')]
ROWS=[('university-hall-93417','landsd/93417:0','university-hall-93417','government-xl-all-200-original-terrain-batch-v2-20261022'),
      ('beverly-hill-f-256334','landsd/256334:0','beverly-sung-fung','government-xl-all-200-original-terrain-batch-v2-20261022'),
      ('sung-fung-court-79098','landsd/79098:0','beverly-sung-fung','government-xl-fresh-terrain-eighteen-originals-v1-20261023')]


def call(name,script,args):
    with (DOC/(name+'.log')).open('w')as log:r=subprocess.run([sys.executable,str(HERE/script),*args],cwd=ROOT,env=os.environ,stdout=log,stderr=subprocess.STDOUT)
    save(DOC/(name+'.json'),dict(script=script,args=args,exitCode=r.returncode));return r.returncode


def trial(row):
    label,uid,group,terrain=row;prefix='government-xl-next-repairs-'+label;capture='government-xl-next-repairs-'+group+'-runtime-v1-20261023';subset=prefix+'-terrain-subset-v1-20261023';patch=prefix+'-original-terrain-trial-v1-20261023'
    commands=[('subset','selected_original_terrain_subset_v1_20261023.py',['--batch',subset,'--terrain',terrain,'--capture',capture,'--uid',uid]),
              ('construct','selected_original_terrain_patch_v2.py',['--batch',patch,'--terrain-check',subset,'--capture',capture])]
    for phase,script,args in commands:
        code=call(label+'-'+phase,script,args)
        if code:return dict(uid=uid,status='script-investigation',phase=phase,exitCode=code)
    receipt=read(BASE/patch/'result.json')
    if receipt['status']!='private-terrain-validator-passed':return dict(uid=uid,status=receipt['status'],reason=receipt.get('reason'))
    follow=prefix+'-original-terrain-followthrough-v1-20261023'
    code=call(label+'-follow','selected_retained_patch_followthrough_v2_20261023.py',['--batch',follow,'--patch',patch,'--capture',capture,'--inventory','government-xl-after-two-basic-supported-current-inventory-v1-20261023','--uid',uid])
    if code:return dict(uid=uid,status='followthrough-script-investigation',exitCode=code)
    receipt=read(BASE/follow/'result.json')
    code=call(label+'-all-worlds','selected_original_prephysical_suite_v5_20261023.py',['--batch',prefix+'-prephysical-v1-20261023','--runtime',follow+'-runtime','--uid',uid])
    return dict(uid=uid,currentSceneStatus=receipt['status'],allWorldDriverExitCode=code,installationApproved=False)


if __name__=='__main__':
    assert not DOC.exists();DOC.mkdir()
    with ThreadPoolExecutor(max_workers=2)as pool:
        futures=[pool.submit(current_work,g)for g in GROUPS]
        for future in futures:print(future.result(),flush=True)
    with ThreadPoolExecutor(max_workers=2)as pool:
        futures=[pool.submit(trial,r)for r in ROWS]
        results=[f.result()for f in futures]
    save(DOC/'summary.json',dict(rows=results,sourceGeometryChanges=0,installationApproved=False,publication=False));print(results,flush=True)
