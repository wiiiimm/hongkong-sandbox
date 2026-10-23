"""Try authentic original TIN rather than a below-clamp current-parent template."""
from concurrent.futures import ThreadPoolExecutor
import os
import subprocess
import sys
from run import ROOT,HERE,save


def work(row):
    label,uid,terrain=row;prefix='government-xl-next-repairs-'+label
    subset=prefix+'-terrain-subset-v1-20261023';patch=prefix+'-original-terrain-trial-v1-20261023'
    capture='government-xl-next-repairs-hanford-west-kowloon-runtime-v1-20261023'
    doc=ROOT/'docs/astra-city/government-import'/(prefix+'-original-terrain-driver-v1-20261023');assert not doc.exists();doc.mkdir()
    commands=[['selected_original_terrain_subset_v1_20261023.py','--batch',subset,'--terrain',terrain,'--capture',capture,'--uid',uid],
              ['selected_original_terrain_patch_v2.py','--batch',patch,'--terrain-check',subset,'--capture',capture]]
    for i,cmd in enumerate(commands):
        with (doc/(str(i)+'.log')).open('w')as log:r=subprocess.run([sys.executable,str(HERE/cmd[0]),*cmd[1:]],cwd=ROOT,env=os.environ,stdout=log,stderr=subprocess.STDOUT)
        save(doc/(str(i)+'.json'),dict(command=cmd,exitCode=r.returncode))
        if r.returncode:return dict(uid=uid,stoppedAt=i,exitCode=r.returncode)
    return dict(uid=uid,patch=patch,installationApproved=False)


if __name__=='__main__':
    rows=[('hanford-plaza-276187','landsd/276187:0','government-xl-remaining-adjacent-terrain-batch-v1-20261022-276187-0'),('west-kowloon-bus-255415','landsd/255415:0','government-xl-all-200-original-terrain-batch-v2-20261022')]
    with ThreadPoolExecutor(max_workers=2)as pool:print(list(pool.map(work,rows)),flush=True)
