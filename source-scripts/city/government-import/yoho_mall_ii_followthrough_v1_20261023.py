"""Run actual-renderer and complete scoped physical checks for Yoho Mall II."""
from concurrent.futures import ThreadPoolExecutor
import os
import subprocess
import sys
from run import ROOT,HERE,save

PREFIX='government-xl-next-repairs-yoho-mall-ii-273672'
PATCH=PREFIX+'-private-inset-v1-20261023'
RUNTIME=PREFIX+'-patch-runtime-v1-20261023'
DOC=ROOT/'docs/astra-city/government-import'/(PREFIX+'-followthrough-v1-20261023')


def call(name,script,tail):
    with (DOC/(name+'.log')).open('w')as log:
        p=subprocess.run([sys.executable,str(HERE/script),*tail],cwd=ROOT,env=os.environ,stdout=log,stderr=subprocess.STDOUT)
    save(DOC/(name+'.json'),dict(script=script,arguments=tail,exitCode=p.returncode))
    assert p.returncode==0,(name,p.returncode)


if __name__=='__main__':
    assert not DOC.exists();DOC.mkdir()
    call('runtime','selected_original_patch_runtime_v2.py',['--batch',RUNTIME,'--patch',PATCH,'--capture',PREFIX+'-runtime-v1-20261023'])
    with ThreadPoolExecutor(max_workers=2)as pool:
        futures=[pool.submit(call,'prephysical','selected_original_prephysical_suite_v5_20261023.py',['--batch',PREFIX+'-prephysical-v1-20261023','--runtime',RUNTIME,'--uid','landsd/273672:0']),
                 pool.submit(call,'scope','selected_original_scope_followthrough_v2_20261023.py',['--batch',PREFIX+'-current-scope-v1-20261023','--inventory','government-xl-after-two-basic-supported-current-inventory-v1-20261023','--candidate',','.join(['landsd/273672:0',PATCH,RUNTIME,PREFIX+'-identity-v1-20261023'])])]
        for future in futures:future.result()
