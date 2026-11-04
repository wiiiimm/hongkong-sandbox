"""Complete two explicit follow-ons after the sequential installation worker."""
import json,subprocess,sys,time
from run import ROOT,HERE,read,save

BATCH='government-xl-sustained-final-acceptance-20261006'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
BASE='docs/astra-city/government-import/government-xl-sustained-131-inputs-20261006'
WAIT=ROOT/'docs/astra-city/government-import/government-xl-sustained-131-installation-20261006/commands.json'

def main():
 assert not DOC.exists(),'Fresh continuation only'
 deadline=time.monotonic()+10800
 while not WAIT.exists():
  assert time.monotonic()<deadline,'Known installation worker did not complete';time.sleep(5)
 sources=[('landsd/274320:0','docs/astra-city/government-import/government-xl-sustained-131-installation-20261006-274320-0-recheck',
           'docs/astra-city/government-import/government-xl-sustained-131-installation-20261006-274320-0-installed'),
          ('landsd/190440:0','docs/astra-city/government-import/government-xl-sustained-jubilation-float32-20261006',None)]
 rows=[];local=HERE/'local'/BATCH;local.mkdir(parents=True,exist_ok=True)
 for uid,previous,retry in sources:
  token=uid.split('/')[1].replace(':','-');recheck=BATCH+'-'+token+'-recheck';installed=BATCH+'-'+token+'-installed'
  commands=[('recheck',[sys.executable,str(HERE/'xl-recheck-candidate-evidence.py'),'--previous',previous,'--batch',recheck]),
            ('installed',[sys.executable,str(HERE/'xl-explicit-root-install.py'),'--uid',uid,'--batch',installed,'--source','docs/astra-city/government-import/'+recheck,'--base',BASE]+(['--retry-of',retry] if retry else []))]
  steps=[]
  for phase,command in commands:
   log=local/(token+'-'+phase+'.log');print(json.dumps({'starting':uid,'phase':phase}),flush=True)
   with log.open('w') as out:process=subprocess.run(command,cwd=ROOT,stdout=out,stderr=subprocess.STDOUT)
   directory=ROOT/'docs/astra-city/government-import'/(recheck if phase=='recheck' else installed)
   result=read(directory/'result.json') if (directory/'result.json').exists() else None
   steps.append({'phase':phase,'command':command,'returncode':process.returncode,'batch':directory.name,'result':result,'log':str(log.relative_to(ROOT))})
   if process.returncode or result is None or phase=='recheck' and not result['scriptChecksPassed']:break
  rows.append({'uid':uid,'steps':steps,'result':steps[-1]['result']});save(DOC/'working-commands.json',{'batch':BATCH,'rows':rows})
  print(json.dumps({'completed':uid,'installed':bool(steps[-1]['result'] and steps[-1]['result'].get('installedUids')),'returncode':steps[-1]['returncode']}),flush=True)
 save(DOC/'commands.json',{'batch':BATCH,'rows':rows,'modelGeometryChanges':0,'scriptExternalAICalls':0,
                          'qualification':'Current recheck and full staged/live acceptance. Interrupted approval does not give installed credit. Commit each verified publication.'})

if __name__=='__main__':main()
