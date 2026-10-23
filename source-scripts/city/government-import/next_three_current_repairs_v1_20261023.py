"""Fresh current-scene diagnostics for three identity-positive unfinished originals."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import os
import subprocess
import sys
from run import ROOT,HERE,save

GROUPS=[
    ('yoho-mall-ii-273672',['landsd/273672:0'],'government-xl-remaining-178-v3-current-scene-v1-20261023-chunk-01-runtime'),
    ('hanford-west-kowloon',['landsd/276187:0','landsd/255415:0'],'government-xl-remaining-178-v3-current-scene-v1-20261023-chunk-02-runtime'),
]


def work(group):
    label,uids,old=group
    prefix='government-xl-next-repairs-'+label
    base=ROOT/'docs/astra-city/government-import'
    commands=base/(prefix+'-driver-v1-20261023');assert not commands.exists();commands.mkdir()
    selection=prefix+'-selection-v1-20261023'
    runtime=prefix+'-runtime-v1-20261023'
    identity=prefix+'-identity-v1-20261023'
    arguments=[arg for uid in uids for arg in ['--uid',uid]]
    rows=[['selected_original_refresh_selection_v1.py','--batch',selection,'--capture',old,*arguments],
          ['selected_original_current_capture_v3.py','--batch',runtime,'--capture',selection,*arguments],
          ['selected_original_identity_v3_20261023.py','--batch',identity,'--capture',runtime]]
    for index,command in enumerate(rows):
        with (commands/('command-'+str(index)+'.log')).open('w')as log:
            result=subprocess.run([sys.executable,str(HERE/command[0]),*command[1:]],cwd=ROOT,env=os.environ,stdout=log,stderr=subprocess.STDOUT)
        save(commands/('command-'+str(index)+'.json'),dict(command=command,exitCode=result.returncode))
        assert result.returncode==0,(label,index)
        print(label,'completed',command[0],flush=True)
    return dict(uids=uids,runtime=runtime,identity=identity,installationApproved=False)


if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=2)as pool:
        print(list(pool.map(work,GROUPS)),flush=True)
