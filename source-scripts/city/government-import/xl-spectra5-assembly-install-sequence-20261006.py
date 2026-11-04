"""Serial fresh Spectra Tower5 acceptance with complete current assembly framing."""
import json, subprocess, sys, time
from pathlib import Path
from run import ROOT, HERE, read, save, digest
BATCH='government-xl-spectra5-assembly-install-sequence-20261006'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
AFTER=ROOT/'docs/astra-city/government-import/government-xl-hoi-wing-complete-proof-sequence-20261006/commands.json'
BASE='docs/astra-city/government-import/government-xl-sustained-100-inputs-20261006'
PREVIOUS='docs/astra-city/government-import/government-xl-full-cell-34-sequence-20261006-265310-0'
UID='landsd/265310:0'
assert not (DOC/'commands.json').exists()
LOCAL.mkdir(parents=True,exist_ok=True)
while not AFTER.exists():time.sleep(10)
prior=read(AFTER);assert prior['activeWorkers']==0 and prior['queuedFollowups']==0
phases=[]
def phase(batch,command):
    log=LOCAL/(batch+'.log')
    with log.open('w') as out:status=subprocess.run(command,cwd=ROOT,stdout=out,stderr=subprocess.STDOUT).returncode
    path=ROOT/'docs/astra-city/government-import'/batch/'result.json'
    result=read(path) if path.exists() else None
    phases.append({'command':command,'returncode':status,'result':result,'log':str(log.relative_to(ROOT))})
    return status,result
batch='government-xl-spectra5-assembly-current-20261006'
status,result=phase(batch,[sys.executable,str(HERE/'xl-cell-installation-recheck.py'),'--previous',PREVIOUS,'--batch',batch,'--base',BASE])
if status==0 and result and result['scriptChecksPassed']:
    installed='government-xl-spectra5-assembly-installed-20261006'
    status,result=phase(installed,[sys.executable,str(HERE/'xl-explicit-cell-assembly-install.py'),'--uid',UID,'--batch',installed,'--source','docs/astra-city/government-import/'+batch,'--base',BASE])
    if result and result.get('installedUids')==[UID]:save(DOC/'commit-required-265310-0.json',{'uid':UID,'installation':installed})
save(DOC/'commands.json',{'batch':BATCH,'rows':phases,'newlyInstalled':int(bool(result and result.get('installedUids')==[UID])),
     'activeWorkers':0,'queuedFollowups':0,'precedingSequenceSHA256':digest(AFTER.read_bytes()),'modelGeometryChanges':0,'scriptExternalAICalls':0})
print(json.dumps({'completed':BATCH,'installed':bool(result and result.get('installedUids')==[UID])}),flush=True)
