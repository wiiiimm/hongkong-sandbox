"""Continue all three current physical cases using cached original government terrain."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import os
import subprocess
import sys
from run import ROOT,HERE,save

ROWS=[
 ('yoho-mall-ii-273672','landsd/273672:0','government-xl-next-repairs-yoho-mall-ii-273672-runtime-v1-20261023','government-xl-remaining-adjacent-terrain-batch-v1-20261022-273672-0'),
 ('hanford-plaza-276187','landsd/276187:0','government-xl-next-repairs-hanford-west-kowloon-runtime-v1-20261023','government-xl-remaining-adjacent-terrain-batch-v1-20261022-276187-0'),
 ('west-kowloon-bus-255415','landsd/255415:0','government-xl-next-repairs-hanford-west-kowloon-runtime-v1-20261023','government-xl-all-200-original-terrain-batch-v2-20261022'),
]


def work(row):
    label,uid,capture,terrain=row
    batch='government-xl-next-repairs-'+label+'-private-inset-v1-20261023'
    doc=ROOT/'docs/astra-city/government-import'/(batch+'-driver');assert not doc.exists();doc.mkdir()
    command=[sys.executable,str(HERE/'selected_original_local_inset_v7.py'),'--batch',batch,'--capture',capture,'--terrain-check',terrain,'--uid',uid]
    with (doc/'process.log').open('w')as log:
        result=subprocess.run(command,cwd=ROOT,env=os.environ,stdout=log,stderr=subprocess.STDOUT)
    receipt=dict(uid=uid,batch=batch,exitCode=result.returncode,installationApproved=False)
    save(doc/'command.json',dict(command=command,**receipt));print(receipt,flush=True)
    return receipt


if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=2)as pool:
        print(list(pool.map(work,ROWS)),flush=True)
