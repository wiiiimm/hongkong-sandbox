"""Run exact contact attribution for all remaining untried saved support pairs."""
from pathlib import Path
import subprocess,sys
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-saved-support-contact-batch-v1-20261022';DOC=BASE/BATCH
CAP='government-xl-remaining-forty-assembly-runtime-v1-20261021';CHECKS='government-xl-remaining-forty-assembly-support-v1-20261021'
def main():
 assert not DOC.exists();refs=[Path(__file__)];cache={}
 def take(n,p):
  if n not in cache:cache[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
  assert digest(p.read_bytes())==cache[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 n='government-xl-scripted-source-inventory-20261022';inventory=take(n,BASE/n/'inventory.json');pending={r['uid']:r for r in inventory['rows']};manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==inventory['manifestSHA256'];refs.append(manifest)
 reports=take(CHECKS,BASE/CHECKS/'support-checks.json.gz')['rows'];rows=[r for r in reports if r['uid']in pending and r['interface']['unresolved'] and r['uid']!='landsd/256702:0'];assert len(rows)==5
 for row in rows:assert row['sourceSHA256']==pending[row['uid']]['indexedSourceSHA256']
 save(DOC/'selection.json',dict(rows=[dict(uid=r['uid'],supportUid=r['supportUid'],sourceSHA256=r['sourceSHA256'],supportSHA256=r['supportSHA256'],unresolved=len(r['interface']['unresolved']))for r in rows]))
 tool=HERE/'original_support_contact_attribution_v2.py';refs.append(tool);summary=[]
 for row in rows:
  uid=row['uid'];child='government-xl-saved-support-'+uid.split('/')[1].replace(':','-')+'-v1-20261022';log=DOC/(uid.split('/')[1]+'.log');assert not(BASE/child).exists()
  print(dict(uid=uid,state='computing',rawUnresolved=len(row['interface']['unresolved'])),flush=True)
  cmd=[sys.executable,str(tool),'--batch',child,'--capture',CAP,'--checks',CHECKS,'--uid',uid,'--support',row['supportUid']]
  with log.open('w')as stream:run=subprocess.run(cmd,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
  refs.append(log)
  if run.returncode:
   result=dict(uid=uid,status='script-failed',exitCode=run.returncode,log=str(log.relative_to(ROOT)),installationApproved=False)
  else:
   r=take(child,BASE/child/'summary.json');result=dict(uid=uid,status='completed',jobId=read(BASE/child/'result.json')['jobId'],unresolvedWitnesses=r['unresolvedWitnesses'],finiteIncidentContacts=r['finiteIncidentContacts'],installationApproved=False)
  summary.append(result);save(DOC/'progress.json',dict(rows=summary));print(result,flush=True)
 assert digest(manifest.read_bytes())==inventory['manifestSHA256']
 result=dict(uids=[r['uid']for r in rows],rows=summary,scriptExternalAICalls=0,sourceGeometryChanges=0,installationApproved=False);save(DOC/'summary.json',result)
 module('saved_contact_batch_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'remaining-saved-original-support-contact-batch',refs,result)
if __name__=='__main__':main()
