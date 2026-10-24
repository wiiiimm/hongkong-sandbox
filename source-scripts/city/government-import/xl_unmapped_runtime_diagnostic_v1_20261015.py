"""Run real loader against candidate identities without changing native match records."""
import subprocess,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations,jobs,Jsonb,dict_row
BATCH='government-xl-unmapped-runtime-diagnostic-v1-20261015'
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
INPUT=BASE/'government-xl-unmapped-two-primary-evidence-v1-20261015/viewer-bindings.json'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists()and not LOCAL.exists()
 binding=read(INPUT)
 for r in binding['evidenceRefs']:assert ref(ROOT/r['path'])==r
 native={r['model']['modelId']:r for r in read(BASE/'government-xl-unmapped-full-bounds-provider-v1-20261015/native-inputs.json')['rows']}
 recovered={r['modelId']:r for r in read(BASE/'government-xl-unmapped-exact-source-recovery-v1-20261015/recovery.json')['rows']}
 uids=[b['viewerUID']for r in binding['rows']for b in r['bindings']]
 resources=['building:'+u for u in uids]+['native-model:'+r['sourceKey']for r in binding['rows']]
 claim=reservations.claim('unmapped-runtime-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=1800);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();LOCAL.mkdir(parents=True);folder=LOCAL/'candidates';(folder/'assets').mkdir(parents=True)
  cat={k:v for k,v in read(HERE.parent/'kai-tak-port/staged/catalogue.json').items()if k not in ('models','counts','area')};cat.update(area=BATCH,models=[],counts={'packedModels':len(uids)})
  forms={}
  stages=read(BASE/'government-xl-unmapped-exact-source-recovery-v1-20261015/input-bindings.json')['stages']
  for row in binding['rows']:
   model=native[row['modelId']]['model'];source=recovered[row['modelId']];raw=(ROOT/source['asset']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];(folder/model['asset']['asset']).write_bytes(raw)
   for b in row['bindings']:
    f=b['viewerForm'];tile='city/data/tiles/'+f['tile']+'.json';path=ROOT/'3d-viewer'/tile;assert next(x for x in read(path)['buildings']if x['uid']==f['uid'])==f
    forms[f['uid']]={'building':f,'tile':tile,'tileSHA256':digest(path.read_bytes())}
    cat['models'].append({**model['asset'],'uid':f['uid'],'objectId':f['objectId'],'buildingCSUID':f['buildingCSUID'],'recordedBaseHeight':f['baseHeightHKPD'],'recordedTopHeight':f['topHeightHKPD'],'modelId':row['modelId'],'worldBounds':model['worldBounds'],'triangles':model['triangles'],'sourceTile':stages[row['sourceKey'].split('/')[0]][0],'priority':'unreviewed','placementReviewed':False,'identityReviewApproved':False,'publicationApproved':False,'proceduralWindows':False})
  save(folder/'catalogue.json',cat);save(folder/'catalogue-index.json',{'models':len(uids),'catalogues':['catalogue.json']});save(LOCAL/'source-forms.json',forms)
  stage='candidate-csuid-original-runtime-diagnostic-v1';jid=jobs.enqueue(BATCH,stage,{'uids':uids,'binding':ref(INPUT)});job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
  cmd=['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',str(folder),'--source-forms',str(LOCAL/'source-forms.json'),'--out',str(DOC/'validation.json')]
  p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);save(DOC/'execution.json',{'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr});assert p.returncode in (0,1) and (DOC/'validation.json').exists()
  validation=read(DOC/'validation.json');assert {r['uid']for r in validation['results']}==set(uids)
  refs=[ref(INPUT),ref(Path(__file__))]+[ref(p)for p in DOC.iterdir()if p.is_file()]+[ref(LOCAL/'source-forms.json'),ref(folder/'catalogue.json'),ref(folder/'catalogue-index.json')]
  for r in binding['evidenceRefs']:assert ref(ROOT/r['path'])==r
  result={'jobId':jid,'uids':uids,'rows':validation['results'],'evidenceRefs':refs,'sourceOnly':True,'newlyInstalled':0,'sourceGeometryChanges':0,'publicationApproved':False,'qualification':'Hypothetical UID runtime diagnostics only. Hotel tested under each candidate form separately; not two installations. Native matching records unchanged; identity and whole-source physical acceptance outstanding.'}
  with connect()as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
   assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);print(result,flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
