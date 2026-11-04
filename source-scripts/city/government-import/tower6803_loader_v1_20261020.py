"""Private paired unchanged-source catalogue validation; no publication."""
from pathlib import Path
import json,sys,uuid,copy,subprocess
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tower6803-loader-v1-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
CAP=BASE/'government-xl-tower6803-private-terrain-capture-v1-20261020';UIDS=['landsd/15047:0','landsd/6803:0']
def owned():
 assert not DOC.exists();lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);pins={};refs=[Path(__file__)]
 folders=[CAP]
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in folders:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 rows=[r for r in read(CAP/'selection.json.gz')['rows'] if r['uid'] in UIDS];assert {x['uid'] for x in rows}==set(UIDS);entries=[];bindings=[]
 for row in rows:
  e=copy.deepcopy(row['candidate']['entry']);e['proceduralWindows']=False;e['supportDependencies']=([dict(uid='landsd/15047:0',state='candidate',csuid='1504326869P20201028',sha256='c1e20265d097b609ca6d313e5b9ddc1d45c4f12687ad14237bac5180aef2f480')] if row['uid']=='landsd/6803:0' else []);raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];asset=LOCAL/e['asset'];asset.parent.mkdir(parents=True,exist_ok=True);asset.write_bytes(raw)
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');key=row['native']['cacheKey'];assert c.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone()[0]==row['native']['resultSha'];sheet=c.execute('SELECT sheet FROM astra_modelling.native_stage_inputs WHERE cache_key=%s',(key,)).fetchone()[0]
  assert not e.get('sourceTile') or e['sourceTile']==sheet;e['sourceTile']=sheet;entries.append(e);bindings.append(dict(uid=row['uid'],cacheKey=key,resultSha=row['native']['resultSha'],sourceTile=sheet))
 save(DOC/'source-tile-binding.json',bindings)
 save(LOCAL/'catalogue.json',dict(schemaVersion=1,kind='staged-official-model-catalogue',datasetId='landsd_rcd_1742809441342_98380',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],models=entries,counts=dict(packedModels=2),area='Private Tower 1 and original podium'))
 
 for r in rows:r['source']['tileSHA256']=digest((ROOT/'3d-viewer'/r['source']['tile']).read_bytes())
 save(LOCAL/'catalogue-index.json',dict(models=2,catalogues=['catalogue.json']));save(LOCAL/'source-forms.json',{r['uid']:r['source'] for r in rows})
 tool=HERE.parent/'building-batch/validate_candidates.mjs';cmd=['node',str(tool),'--candidates',str(LOCAL.relative_to(ROOT)),'--source-forms',str((LOCAL/'source-forms.json').relative_to(ROOT)),'--out',str((DOC/'validation.json').relative_to(ROOT))]
 with (DOC/'validation.log').open('w') as log:proc=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 save(DOC/'validation-command.json',dict(command=cmd,exitCode=proc.returncode));assert proc.returncode in [0,1];v=read(DOC/'validation.json');refs.append(tool)
 metrics=read(CAP/'metrics.json');policy=module('parkview_two_policy',HERE/'acceptance-policy.py');reasons=[]
 for row in rows:
  if row['uid']=='landsd/6803:0':
   identityPath=BASE/'government-xl-next-twenty-original-identity-v2-20261020/6803:0/identity.json';identity=read(identityPath);assert identity['passed'] and not identity['reasons'] and identity['sourceSHA256']==row['sourceSHA256'];identityReceipt=read(identityPath.parent.parent/'result.json');proof=identity['proof']
  else:
   identityPath=BASE/'government-xl-tower6803-podium-native-yaw-v1-20261020/proof.json';identity=read(identityPath);assert identity['sourceBoundIdentityPassed'] and identity['sourceSHA256']==row['sourceSHA256'];identityReceipt=read(identityPath.parent/'result.json');proof={k:True for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']}
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(identityReceipt['jobId'],)).fetchone()==('complete',identityReceipt)
  identityPins={e['path']:e['sha256'] for e in identityReceipt['evidenceRefs']};assert digest(identityPath.read_bytes())==identityPins[str(identityPath.relative_to(ROOT))];refs.append(identityPath)
  refs.append(identityPath.parent.parent/'result.json' if row['uid']=='landsd/6803:0' else identityPath.parent/'result.json')
  m=next(x for x in metrics['rows'] if x['uid']==row['uid']);reasons.append(dict(uid=row['uid'],reasons=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=row['sourceSHA256'],identityProof=proof),m,metrics['profiles']['mobile'])))

 summary=dict(uids=UIDS,loaderAccepted=v['loaderAccepted'],checksPassed=v['checksPassed'],exceptions=v['exceptions'],ordinaryConcerns=[dict(uid=r['uid'],concerns=r.get('concerns',[])) for r in v['results']],rawPolicyReasons=reasons,installationApproved=False);save(DOC/'summary.json',summary);print(summary,flush=True)
 for p,h in {**pins,**v.get('inputHashes',{}),**v.get('hashes',{})}.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.append(HERE/'acceptance-policy.py');refs.extend(p for p in LOCAL.rglob('*') if p.is_file() and p.name!='reservation.json');assert reservations.owns(lease)
 module('parkview_two_loader_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-pair-loader-checks',list(dict.fromkeys(refs)),dict(uids=UIDS,summary=summary,installationApproved=False))
def main():
 if '--owned' in sys.argv:return owned()
 assert not DOC.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];p=LOCAL/'reservation.json';save(p,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(p),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
