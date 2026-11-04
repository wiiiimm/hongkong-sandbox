"""Complete current-neighbour and all-world checks for Hanford's validated terrain."""
import os
import subprocess
import sys
from run import ROOT,HERE,read,save

PREFIX='government-xl-next-repairs-hanford-plaza-276187'
BATCH=PREFIX+'-bounded-followthrough-v1-20261023'
DOC=ROOT/'docs/astra-city/government-import'/(PREFIX+'-complete-source-driver-v2-20261023')


def call(name,script,args):
    with (DOC/(name+'.log')).open('w')as log:p=subprocess.run([sys.executable,str(HERE/script),*args],cwd=ROOT,env=os.environ,stdout=log,stderr=subprocess.STDOUT)
    save(DOC/(name+'.json'),dict(script=script,args=args,exitCode=p.returncode));assert p.returncode==0,(name,p.returncode)


if __name__=='__main__':
    assert not DOC.exists();DOC.mkdir()
    call('current','selected_retained_patch_followthrough_v2_20261023.py',['--batch',BATCH,'--patch',PREFIX+'-bounded-grade-v2-20261023','--capture','government-xl-next-repairs-hanford-west-kowloon-runtime-v1-20261023','--inventory','government-xl-after-two-basic-supported-current-inventory-v1-20261023','--uid','landsd/276187:0'])
    call('prephysical','selected_original_prephysical_suite_v5_20261023.py',['--batch',PREFIX+'-bounded-prephysical-v1-20261023','--runtime',BATCH+'-runtime','--uid','landsd/276187:0'])
