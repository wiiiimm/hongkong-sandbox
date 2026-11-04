"""Query complete native source envelopes; nearby features never establish identity."""
import sys,json,uuid,concurrent.futures
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations,jobs,Jsonb,dict_row,NATIVE_RUN
sys.path.insert(0,str(HERE.parent/'landsd-territory'))
from source import request,BASE
BATCH='government-xl-unmapped-full-bounds-provider-v1-20261015';DOC=ROOT/'docs/astra-city/government-import'/BATCH
COUNT=ROOT/'docs/astra-city/government-import/government-xl-aqua-marine193086-original-installed-v1-20261014/full-xl-current-count.json'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();wanted=[r for r in read(COUNT)['rows']if not r['installedVerified']and r['uid']is None];assert len(wanted)==4;records=[]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for r in wanted:
   key,model=r['sourceKey'].split('/');v=c.execute("SELECT r.result_sha,m FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members n USING(cache_key),LATERAL jsonb_array_elements(r.result->'models')m WHERE n.run_id=%s AND r.cache_key=%s AND m->>'modelId'=%s",(NATIVE_RUN,key,model)).fetchall();assert len(v)==1 and v[0][1]['asset']['sha256']==r['indexedSourceSHA256'];records.append(dict(sourceKey=r['sourceKey'],nativeResultSHA256=v[0][0],model=v[0][1]))
 claim=reservations.claim('unmapped-full-bounds-'+str(uuid.uuid4()),['native-model:'+r['sourceKey']for r in records],batch=BATCH,ttl=1800);assert claim['ok'];lease=claim['reservation'];job=None
 try:
  DOC.mkdir();save(DOC/'native-inputs.json',dict(nativeRun=NATIVE_RUN,rows=records))
  def fetch(r):
   m=r['model'];lo,hi=m['worldBounds'];geometry=dict(xmin=834500+lo[0],xmax=834500+hi[0],ymin=816500-hi[2],ymax=816500-lo[2],spatialReference=dict(wkid=2326));params=dict(f='json',where='1=1',geometry=json.dumps(geometry,separators=(',',':')),geometryType='esriGeometryEnvelope',inSR='2326',spatialRel='esriSpatialRelIntersects',outFields='*',returnGeometry='true',outSR='2326',returnTrueCurves='false',resultRecordCount='1000',orderByFields='OBJECTID');raw,receipt=request(BASE+'/0/query',params);d=json.loads(raw);assert not d.get('error')and not d.get('exceededTransferLimit');features=d['features'];assert len(features)==len({f['attributes']['OBJECTID']for f in features});stem=m['modelId'];(DOC/(stem+'.json')).write_bytes(raw);save(DOC/(stem+'.request.json'),receipt)
   return dict(sourceKey=r['sourceKey'],sourceSHA256=m['asset']['sha256'],nativeResultSHA256=r['nativeResultSHA256'],worldBounds=m['worldBounds'],hk1980Envelope=geometry,featureCount=len(features),features=[f['attributes']for f in features],identityAccepted=False,installationApproved=False)
  with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:rows=list(pool.map(fetch,records))
  assert reservations.heartbeat(lease)['ok'];prior=read(ROOT/'docs/astra-city/government-import/government-xl-identity-search-20261009/unmapped-context.json.gz')['rows'];prior={r['sourceKey']:r for r in prior}
  for r in rows:
   old={f['BuildingCSUID']for f in prior[r['sourceKey']]['nearbyFeatures']};r['additionalFeaturesComparedWithOld60mQuery']=[f for f in r['features']if f['BuildingCSUID']not in old]
  save(DOC/'full-bounds-context.json',dict(rows=rows,qualification='Complete recorded original source envelope queries, current public provider. Added features are research leads; no UID assignment, identity acceptance, geometry edit or installation. Historical ID lineage remains unproven.'))
  refs=[ref(Path(__file__)),ref(COUNT),ref(HERE.parent/'landsd-territory/source.py')]+[ref(p)for p in sorted(DOC.iterdir())if p.is_file()]
  for q in refs:assert ref(ROOT/q['path'])==q
  kind='unmapped-full-original-bounds-provider-context-v1';jid=jobs.enqueue(BATCH,kind,dict(sourceKeys=[r['sourceKey']for r in rows]));job=jobs.claim(BATCH,lease['owner'],[kind],lease_seconds=1800);assert job and job['id']==jid
  result=dict(jobId=jid,sourceOnly=True,newlyInstalled=0,geometryChanges=0,identityAccepted=False,installationApproved=False,evidenceRefs=refs,summary=[dict(sourceKey=r['sourceKey'],features=r['featureCount'],additionalFeatures=len(r['additionalFeaturesComparedWithOld60mQuery']))for r in rows])
  with connect()as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease);assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);print(json.dumps(dict(jobId=jid,summary=result['summary'])),flush=True)
 except Exception as e:
  if job:jobs.finish(job,error=str(e))
  raise
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
