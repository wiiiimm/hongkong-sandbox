"""Bounded original-support browser diagnostics; never publication approval."""
import argparse,json,os,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row
from publication_lock import locked_publication

SCOPES={
 'tung-yip':('landsd/12854:0','landsd/12852:0','government-xl-tung-yip-complete-installed-20261007','resolution-tung-yip-cold-arrival-diagnostic.mjs'),
}


def ref(path):return {'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes())}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--scope',choices=SCOPES,required=True);p.add_argument('--batch',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args()
 assert Path(a.batch).name==a.batch and a.batch.startswith('government-xl-')
 uid,support,prior,script=SCOPES[a.scope];doc=ROOT/'docs/astra-city/government-import'/a.batch;local=HERE/'local'/a.batch;lease=local/'reservation.json'
 if not a.owned:
  assert not doc.exists(),'Preserve prior diagnostics'
  claim=reservations.claim('codex-supported-browser-diagnostic-'+str(uuid.uuid4()),['building:'+uid,'building:'+support,'building:landsd/12851:0'],batch=a.batch);assert claim['ok'],claim
  save(lease,json.loads(json.dumps(claim['reservation'],default=str)))
  subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(lease),'--',sys.executable,__file__,*sys.argv[1:],'--owned'],cwd=ROOT,check=True);return
 with locked_publication(ROOT):
  receipt=read(lease);assert reservations.owns(receipt)
  stage=HERE/'accepted'/prior;config=read(stage/'browser-config.json');assert config['browserUids']==[uid] and config['nativeSupportUidsByModel']=={uid:['landsd/12851:0','landsd/12852:0']}
  config['doc']=str(doc.relative_to(ROOT))+'/'
  save(local/'browser-config.json',config)
  manifest=ROOT/'3d-viewer/city/data/manifest.json';pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json'
  inputs=[manifest,pointer,stage/'catalogue.json',stage/'source-forms.json',local/'browser-config.json',HERE/script,Path(__file__)]
  for entry in read(stage/'catalogue.json')['models']:inputs.append(stage/entry['asset'])
  references=[ref(f) for f in inputs]
  save(doc/'inputs.json',{'uid':uid,'supportUid':support,'diagnosticOnly':True,'publication':False,'inputs':references})
  command=['node',str(HERE/script),'staged',str((local/'browser-config.json').relative_to(ROOT))]
  code=subprocess.run(command,cwd=ROOT,env={**os.environ,'CHROME_PATH':'/home/williamli/.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell'}).returncode
  assert reservations.owns(receipt)
  for item in references:assert digest((ROOT/item['path']).read_bytes())==item['sha256']
  browser=read(doc/'staged-browser.json');assert browser['diagnosticOnly'] is True
  evidence=[ref(f) for f in sorted(doc.iterdir()) if f.is_file()]
  payload={'uid':uid,'supportUid':support,'evidenceRefs':evidence,'inputRefs':references}
  stage_name='original-support-browser-diagnostic-v1';jobid=jobs.enqueue(a.batch,stage_name,payload);job=jobs.claim(a.batch,receipt['owner'],[stage_name],lease_seconds=1800);assert job and job['id']==jobid
  result={**payload,'jobId':jobid,'exitCode':code,'diagnosticOnly':True,'browserPassed':bool(browser.get('passed')),'publication':False,'newlyInstalled':0,'modelGeometryChanges':0,'scriptExternalAICalls':0,'requiresAI':False,'requiresHumanDecision':False,'reasons':browser['errors']}
  with connect() as con:
   con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,receipt)
   for item in evidence+references:assert digest((ROOT/item['path']).read_bytes())==item['sha256']
   assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jobid,job['owner'],job['token'])).rowcount==1
  with connect() as con:
   con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jobid,)).fetchone()==('complete',result)
  save(doc/'result.json',result);save(doc/'neon-sync.json',{'jobId':jobid,'resultVerified':True});print(json.dumps({'uid':uid,'diagnosticOnly':True,'browserPassed':result['browserPassed'],'jobId':jobid,'neonVerified':True}),flush=True)

if __name__=='__main__':main()
