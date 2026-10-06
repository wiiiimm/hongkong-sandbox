"""Run this authorised bounded continuation across phase boundaries without AI calls."""
import json
import subprocess
import sys
import time
from run import ROOT,HERE,read,save

BATCH='government-xl-sustained-sequence-20261006'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
BASE100='docs/astra-city/government-import/government-xl-sustained-100-inputs-20261006'
BASE131='docs/astra-city/government-import/government-xl-sustained-131-inputs-20261006'
WAIT=ROOT/'docs/astra-city/government-import/government-xl-sustained-followthrough-20261006/commands.json'
STEPS=[('original-support-diagnostics','xl-explicit-support-continuation.py',
    ['--base',BASE100,'--pairs-file',BASE100+'/support-pairs.json','--batch','government-xl-sustained-supports-20261006']),
    ('remaining-131-primary','xl-explicit-continuation.py',
    ['--base',BASE131,'--batch','government-xl-sustained-131-20261006']),
    ('remaining-131-followups','xl-explicit-followthrough.py',
    ['--base',BASE131,'--primary','docs/astra-city/government-import/government-xl-sustained-131-20261006',
     '--batch','government-xl-sustained-131-followthrough-20261006'])]


def main():
    assert not DOC.exists(), 'Fresh explicit sequence only; completed phases must be reused explicitly'
    LOCAL.mkdir(parents=True,exist_ok=True)
    waiting=time.monotonic()
    print(json.dumps({'waitingFor':str(WAIT.relative_to(ROOT)),'publication':False}),flush=True)
    # Bounded wait for the current known worker, not an unbounded invisible queue.
    while not WAIT.exists():
        assert time.monotonic()-waiting<3600,'Current follow-through did not finish within one hour'
        time.sleep(5)
    read(WAIT)
    outcomes=[]
    for name,script,args in STEPS:
        command=[sys.executable,str(HERE/script),*args]
        log=LOCAL/(name+'.log')
        print(json.dumps({'starting':name,'completedPhases':len(outcomes),'totalPhases':len(STEPS)}),flush=True)
        with log.open('w') as output:proc=subprocess.run(command,cwd=ROOT,stdout=output,stderr=subprocess.STDOUT)
        outcomes.append({'phase':name,'command':command,'returncode':proc.returncode,'log':str(log.relative_to(ROOT))})
        save(DOC/'working-commands.json',{'batch':BATCH,'rows':outcomes})
        print(json.dumps({'completed':name,'returncode':proc.returncode}),flush=True)
        if proc.returncode:
            # Do not silently run a dependent stage against incomplete inputs.
            if name=='remaining-131-primary':break
    save(DOC/'commands.json',{'batch':BATCH,'rows':outcomes,'primarySources':231,
         'scriptExternalAICalls':0,'modelGeometryChanges':0,'publication':False,
         'qualification':'Explicit 100+131 original-source continuation, sequential to avoid shared neighbour/source lease conflicts. Child results and final checkpoint determine actual outcomes; a completed sequence is not installation credit.'})


if __name__=='__main__':main()
