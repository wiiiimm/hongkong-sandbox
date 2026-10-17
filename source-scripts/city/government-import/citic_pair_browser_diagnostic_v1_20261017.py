"""Private CITIC pair desktop/mobile day/night, support fallback and collision checks."""
from pathlib import Path
import os,subprocess,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-citic-pair-browser-diagnostic-v1-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;PRIOR=BASE/'government-xl-citic-pair-private-stage-v2-20261017';STAGE=HERE/'local'/PRIOR.name;UIDS=['landsd/232579:0','landsd/278303:0']
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');refs=[Path(__file__),PRIOR/'result.json']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for q in r['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256'];refs.append(ROOT/q['path'])
 claim=reservations.claim('citic-browser-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();config=read(STAGE/'browser-config.json');config['doc']=str(DOC.relative_to(ROOT))+'/';config['browserWidths']=[390];save(LOCAL/'browser-config.json',config)
  tool=HERE/'citic_dependency_browser_diagnostic_v1_20261017.mjs';cmd=['node',str(tool),'staged',str((LOCAL/'browser-config.json').relative_to(ROOT))]
  with (DOC/'browser.log').open('w') as log:done=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=900)
  save(DOC/'command.json',dict(command=cmd,exitCode=done.returncode,publication=False))
  for q in r['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
  refs.extend([tool,LOCAL/'browser-config.json'])
  result=module('citic_browser_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'citic-private-original-pair-browser-v1',list(dict.fromkeys(refs)),dict(uids=UIDS,browserExitCode=done.returncode,newlyInstalled=0,installationApproved=False));print(dict(jobId=result['jobId'],browserExitCode=done.returncode),flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
