"""Continue one verified live seam-cap producer without restarting its work."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import subprocess
import sys
import time
from run import ROOT,HERE,read,save
from china_ferry_current_foundations_v1_20261020 import authenticate

PREFIX='government-xl-next-repairs-hanford-plaza-276187'
CAPS=PREFIX+'-domain-caps-v1-20261023'
PATCH=PREFIX+'-domain-capped-terrain-v1-20261023'
RUNTIME=PREFIX+'-domain-capped-runtime-v1-20261023'
BASE=ROOT/'docs/astra-city/government-import'
DOC=BASE/(PREFIX+'-domain-capped-followthrough-v1-20261023')


def call(name,script,args):
    with (DOC/(name+'.log')).open('w')as log:p=subprocess.run([sys.executable,str(HERE/script),*args],cwd=ROOT,env=os.environ,stdout=log,stderr=subprocess.STDOUT)
    save(DOC/(name+'.json'),dict(script=script,args=args,exitCode=p.returncode));assert p.returncode==0,(name,p.returncode)
    print(name,'complete',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--producer-pid',type=int,required=True);a=parser.parse_args();assert not DOC.exists();DOC.mkdir()
    expected=str(HERE/'original_terrain_domain_caps_v1_20261023.py')
    commandpath=Path('/proc')/str(a.producer_pid)/'cmdline'
    while commandpath.exists():
        command=commandpath.read_bytes().split(b'\0')
        if not any(command):break
        parts=[c.decode()for c in command if c];assert expected in parts and CAPS in parts,'Producer PID was reused; refuse dependent processing'
        print(dict(verifiedLiveProducer=a.producer_pid),flush=True);time.sleep(10)
    receipt,_=authenticate(BASE/CAPS);assert receipt['allDomainFacesCovered'] and receipt['sourceGeometryChanges']==0
    call('construct','selected_original_domain_capped_patch_v1_20261023.py',['--batch',PATCH,'--domain-caps',CAPS,'--terrain-check',PREFIX+'-terrain-subset-v1-20261023','--capture','government-xl-next-repairs-hanford-west-kowloon-runtime-v1-20261023'])
    receipt,_=authenticate(BASE/PATCH)
    if receipt['status']!='private-terrain-validator-passed':
        save(DOC/'stopped.json',dict(status=receipt['status'],reason=receipt.get('reason'),installationApproved=False));sys.exit(0)
    call('runtime','selected_original_patch_runtime_v2.py',['--batch',RUNTIME,'--patch',PATCH,'--capture','government-xl-next-repairs-hanford-west-kowloon-runtime-v1-20261023'])
    with ThreadPoolExecutor(max_workers=2)as pool:
        futures=[pool.submit(call,'prephysical','selected_original_prephysical_suite_v5_20261023.py',['--batch',PREFIX+'-domain-capped-prephysical-v1-20261023','--runtime',RUNTIME,'--uid','landsd/276187:0']),
                 pool.submit(call,'scope','selected_original_scope_followthrough_v2_20261023.py',['--batch',PREFIX+'-domain-capped-current-scope-v1-20261023','--inventory','government-xl-after-two-basic-supported-current-inventory-v1-20261023','--candidate',','.join(['landsd/276187:0',PATCH,RUNTIME,'government-xl-next-repairs-hanford-west-kowloon-identity-v1-20261023'])])]
        for f in futures:f.result()
