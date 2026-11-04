"""Complete finite source/current/original-ground evidence for the three repairs."""
from concurrent.futures import ThreadPoolExecutor
import os
import subprocess
import sys
from run import ROOT,HERE,save

BASE=ROOT/'docs/astra-city/government-import'
DOC=BASE/'government-xl-next-repairs-three-exact-ground-driver-v1-20261023'
YOHO='government-xl-next-repairs-yoho-mall-ii-273672'
PAIR='government-xl-next-repairs-hanford-west-kowloon-runtime-v1-20261023'
ROWS=[('yoho-mall-ii-273672','landsd/273672:0',YOHO+'-retained-followthrough-v1-20261023-runtime','government-xl-remaining-adjacent-terrain-batch-v1-20261022-273672-0','yoho'),
      ('hanford-plaza-276187','landsd/276187:0',PAIR,'government-xl-remaining-adjacent-terrain-batch-v1-20261022-276187-0','pair'),
      ('west-kowloon-bus-255415','landsd/255415:0',PAIR,'government-xl-all-200-original-terrain-batch-v2-20261022','pair')]


def call(task):
    name,script,args=task
    with (DOC/(name+'.log')).open('w')as log:p=subprocess.run([sys.executable,str(HERE/script),*args],cwd=ROOT,env=os.environ,stdout=log,stderr=subprocess.STDOUT)
    save(DOC/(name+'.json'),dict(script=script,args=args,exitCode=p.returncode));assert p.returncode==0,(name,p.returncode)
    print(name,'complete',flush=True)


if __name__=='__main__':
    assert not DOC.exists();DOC.mkdir()
    tasks=[]
    for label,uid,capture,terrain,context in ROWS:
        batch='government-xl-next-repairs-'+label+'-original-projection-gap-v1-20261023'
        tasks.append(('gap-'+label,'selected_original_terrain_projection_gap_v1_20261023.py',['--batch',batch,'--capture',capture,'--terrain-check',terrain,'--uid',uid]))
    for context,runtime in [('yoho',ROWS[0][2]),('pair',PAIR)]:
        tasks.append(('continuous-'+context,'selected_original_continuous_ground_context_v1.py',['--batch','government-xl-next-repairs-'+context+'-continuous-ground-v1-20261023','--runtime',runtime]))
    with ThreadPoolExecutor(max_workers=2)as pool:
        futures=[pool.submit(call,t)for t in tasks]
        for future in futures:future.result()
    tasks=[]
    for label,uid,runtime,terrain,context in ROWS:
        prefix='government-xl-next-repairs-'+label
        tasks.append(('wall-'+label,'selected_original_source_terrain_wall_comparison_v1_20261023.py',['--batch',prefix+'-source-ground-comparison-v1-20261023','--runtime',runtime,'--continuous','government-xl-next-repairs-'+context+'-continuous-ground-v1-20261023','--discovery',prefix+'-original-projection-gap-v1-20261023','--uid',uid]))
    with ThreadPoolExecutor(max_workers=2)as pool:
        futures=[pool.submit(call,t)for t in tasks]
        for future in futures:future.result()
