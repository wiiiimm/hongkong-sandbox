"""Run unchanged strict support checker on the two original government sources."""
from pathlib import Path
import json,uuid,subprocess
from run import ROOT,HERE,read,save,digest,connect,reservations,jobs,Jsonb,dict_row
from publication_lock import locked_publication
BATCH='government-xl-west-wing26195-cgo-original-interface-v1-20261015';DOC=ROOT/'docs/astra-city/government-import'/BATCH
UIDS=['landsd/26195:0','landsd/322270:0'];SHA=['50da67a3a009c3c832d2bfdbd08640c89d958ef8cf077d1c172e7059900f8af9','b1ce8e22f43eb51bda3d6728c74b6e43fa0511e223fc42ed2fd078c8c89254ef']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();claim=reservations.claim('west-wing-cgo-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=1800);assert claim['ok'];lease=claim['reservation'];job=None
 try:
  with locked_publication(ROOT):
   mp=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(mp);tile=ROOT/'3d-viewer/city/data/tiles/0_0.json';forms={f['uid']:f for f in read(tile)['buildings']};sources={};refs=[ref(Path(__file__)),ref(mp),ref(tile)]
   for url in manifest['officialModelCatalogues']:
    p=ROOT/'3d-viewer'/url;cat=read(p)
    for e in cat['models']:
     u=e['uid']
     if u not in UIDS:continue
     assert u not in sources and e['sha256']==SHA[UIDS.index(u)];asset=p.parent/e['asset'];assert ref(asset)['sha256']==e['sha256'];refs.extend([ref(p),ref(asset)])
     sources[u]=dict(uid=u,sourceSHA256=e['sha256'],source=dict(building=forms[u]),candidate=dict(path=str(asset.relative_to(ROOT)),entry={**e,'rootTranslation':cat['rootTranslation'],'coordinatePolicy':cat.get('coordinatePolicy'),'datasetId':cat.get('datasetId')}))
   assert set(sources)==set(UIDS);assert forms[UIDS[0]]['parent']==forms[UIDS[1]]['parent']=='relation/8366346'
   for s in sources.values():assert s['candidate']['entry']['rootTranslation']==[-834500,0,816500]
   save(DOC/'support-inputs.json',dict(sources=list(sources.values()),pairs=[dict(uid=UIDS[1],supportUid=UIDS[0])]))
  tool=HERE/'original-support-closure-interfaces.mjs';assert reservations.heartbeat(lease)['ok']
  with (DOC/'terminal.log').open('w')as log:
   subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=900)
  data=read(DOC/'support-checks.json.gz');assert len(data['rows'])==1;row=data['rows'][0];assert row['uid']==UIDS[1]and row['supportUid']==UIDS[0]and row['sourceSHA256']==SHA[1]and row['supportSHA256']==SHA[0]
  for p,h in data['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(dict(path=p,sha256=h))
  refs.extend(ref(DOC/f)for f in ['support-checks.json.gz','terminal.log'])
  for q in refs:assert ref(ROOT/q['path'])==q
  assert reservations.heartbeat(lease)['ok'];kind='west-wing-cgo-unchanged-strict-original-interface-v1';jid=jobs.enqueue(BATCH,kind,dict(uids=UIDS));job=jobs.claim(BATCH,lease['owner'],[kind],lease_seconds=1800);assert job and job['id']==jid
  interface=row['interface'];result=dict(jobId=jid,sourceOnly=True,newlyInstalled=0,installationApproved=False,geometryChanges=0,interfacePassed=interface['passed'],strictContacts=interface['strictContacts'],samples=interface['samples'],wallIntersections=interface['wallIntersections'],unresolved=len(interface['unresolved']),evidenceRefs=refs)
  with connect()as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease);assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);print(json.dumps({k:v for k,v in result.items()if k!='evidenceRefs'}),flush=True)
 except Exception as e:
  if job:jobs.finish(job,error=str(e))
  raise
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
