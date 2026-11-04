"""Run unchanged current-scene checks for the explicit original source pair."""
from pathlib import Path
import subprocess,sys
from run import ROOT,HERE,read,save
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
B='government-xl-source118003-pair-current-v1-20261022';BASE=ROOT/'docs/astra-city/government-import';D=BASE/B
PATCH='government-xl-source118003-pair-terrain-v1-20261022';CAP='government-xl-source118003-pair-capture-v1-20261022';INV='government-xl-after-tung-ping-current-inventory-v1-20261022'
assert not D.exists();r,_=authenticate(BASE/PATCH);assert r['status']=='private-terrain-validator-passed'and set(r['uids'])=={'landsd/118003:0','landsd/118128:0'}
D.mkdir();refs=[Path(__file__),BASE/PATCH/'result.json'];phases=[]
steps=[('runtime','selected_original_patch_runtime_v2.py',['--patch',PATCH,'--capture',CAP]),('identity','selected_original_identity_v3.py',['--capture',B+'-runtime']),('scope','selected_original_patch_scope_v1.py',['--patch',PATCH,'--inventory',INV]),('neighbours','selected_bounded_native_neighbours_v1.py',['--scope',B+'-scope','--inventory',INV,'--patch',PATCH])]
for phase,script,tail in steps:
 with (D/(phase+'.log')).open('w')as log:subprocess.run([sys.executable,str(HERE/script),'--batch',B+'-'+phase,*tail],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 result,_=authenticate(BASE/(B+'-'+phase));refs.extend([HERE/script,BASE/(B+'-'+phase)/'result.json']);phases.append(dict(phase=phase,jobId=result['jobId']));print(phases[-1],flush=True)
summary=dict(uids=r['uids'],completed=phases,installationApproved=False,sourceGeometryChanges=0,qualification='Complete unchanged current checks only; raw identity/physical failures remain, no approval.')
save(D/'summary.json',summary);module('pair_current_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(B,'explicit-original-pair-current-checks',refs,summary)
