"""Consolidate this explicit 231-source run only after all acceptance attempts end."""
import json,subprocess,sys,time
from run import ROOT,HERE,read

def main():
 folders=['government-xl-sustained-131-installation-20261006','government-xl-sustained-final-acceptance-20261006']
 root=ROOT/'docs/astra-city/government-import';deadline=time.monotonic()+10800
 while not all((root/folder/'commands.json').exists() for folder in folders):
  assert time.monotonic()<deadline,'Known acceptance workers did not complete';time.sleep(5)
 command=[sys.executable,str(HERE/'xl-explicit-checkpoint.py'),'--batch','government-xl-sustained-231-checkpoint-20261006']
 for name in ['government-xl-sustained-100-20261006','government-xl-sustained-131-20261006']:command+=['--primary',str((root/name).relative_to(ROOT))]
 for name in ['government-xl-sustained-100-inputs-20261006','government-xl-sustained-131-inputs-20261006']:command+=['--base',str((root/name).relative_to(ROOT))]
 for name in ['government-xl-sustained-followthrough-20261006','government-xl-sustained-supports-20261006','government-xl-sustained-131-followthrough-20261006']:command+=['--followups',str((root/name).relative_to(ROOT))]
 for name in ['government-xl-sustained-festival-secondary-seam-20261006','government-xl-sustained-star-house-retained-child-20261006',
              'government-xl-sustained-star-house-support-20261006','government-xl-sustained-support-identity-256113-20261006',
              'government-xl-sustained-support-identity-255646-20261006','government-xl-sustained-support-identity-256116-20261006',
              'government-xl-sustained-jubilation-float32-20261006','government-xl-sustained-block8-float32-20261006',
              'government-xl-sustained-one-peking-retained-child-20261006']:command+=['--extra-stage',str((root/name).relative_to(ROOT))]
 for folder in folders:
  command+=['--installation-commands',str((root/folder).relative_to(ROOT))]
  for row in read(root/folder/'commands.json')['rows']:
   for step in row.get('steps',[]):
    if not step['result']:continue
    assert step['returncode']==0
    flag='--installation' if step['result'].get('installedUids') else '--extra-stage'
    command += [flag,str((root/step['batch']).relative_to(ROOT))]
 print(json.dumps({'command':command}),flush=True)
 subprocess.run(command,cwd=ROOT,check=True)

if __name__=='__main__':main()
