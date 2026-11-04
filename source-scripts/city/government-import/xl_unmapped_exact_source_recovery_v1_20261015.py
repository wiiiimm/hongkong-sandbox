"""Restore four exact unmapped originals using existing source acquisition/conversion."""
import sys,json,uuid,zipfile,concurrent.futures
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations,jobs,Jsonb,dict_row,NATIVE_RUN
sys.path.insert(0,str(HERE.parent/'enhancement-screening'))
from shape_prepare import scan,acquire,_convert_one,canonical_bytes
BATCH='government-xl-unmapped-exact-source-recovery-v1-20261015';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH
INPUT=ROOT/'docs/astra-city/government-import/government-xl-unmapped-full-bounds-provider-v1-20261015/native-inputs.json'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists()and not LOCAL.exists();records=read(INPUT)['rows'];assert len(records)==4;keys=[r['sourceKey'].split('/')[0]for r in records]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');stages={k:(sheet,sha)for k,sheet,sha in c.execute('SELECT i.cache_key,i.sheet,r.result_sha FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results r USING(cache_key) JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND i.cache_key=ANY(%s)',(NATIVE_RUN,keys)).fetchall()};sheets=sorted({v[0]for v in stages.values()});directories=dict(c.execute("SELECT DISTINCT ON(sheet)sheet,result-'models' FROM astra_modelling.city_source_directories WHERE sheet=ANY(%s) ORDER BY sheet,created_at DESC",(sheets,)).fetchall())
 for r in records:assert stages[r['sourceKey'].split('/')[0]][1]==r['nativeResultSHA256']
 claim=reservations.claim('unmapped-original-recovery-'+str(uuid.uuid4()),['native-model:'+r['sourceKey']for r in records],batch=BATCH,ttl=1800);assert claim['ok'];lease=claim['reservation'];job=None
 try:
  DOC.mkdir();LOCAL.mkdir(parents=True);save(DOC/'input-bindings.json',dict(nativeRecords=records,stages=stages,directories=directories));assets=LOCAL/'assets';assets.mkdir()
  grouped={sheet:[r for r in records if stages[r['sourceKey'].split('/')[0]][0]==sheet]for sheet in sheets}
  def work(item):
   sheet,items=item;folder=LOCAL/sheet;prior=directories[sheet];folder.mkdir()
   try:
    row,_=scan(dict(SHEETNO=sheet,Format_glTF=prior['sourceURL'],REVISIONDATE=prior['revision']),folder/'directory');assert row['etag']==prior['etag']and row['directorySHA256']==prior['directorySHA256'],'Source revision changed'
    wanted={r['model']['modelId']for r in items};row['models']=[m for m in row['models']if m['modelId']in wanted];assert {m['modelId']for m in row['models']}==wanted
    acquisition=acquire(row,folder/'directory/zip-directory.bin',folder/'original');packed=folder/'packed';packed.mkdir();out=[]
    with zipfile.ZipFile(folder/'original'/f'{sheet}.zip')as z:
     for r in items:
      m=r['model'];h=m['asset']['sha256'];v=_convert_one(z,z.getinfo(m['sourceEntry']),folder/'decoded',packed,{},dict(modelId=m['modelId']));raw=canonical_bytes((packed/v['asset']['asset']).read_bytes(),h);assert len(raw)==m['asset']['bytes'];path=assets/(h+'.glb.gz');path.write_bytes(raw)
      original=json.loads(z.read(m['sourceEntry']));save(DOC/(m['modelId']+'-original-metadata.json'),dict(asset=original.get('asset'),extras=original.get('extras'),nodes=[{k:n[k]for k in ('name','extras')if k in n}for n in original.get('nodes',[])]))
      out.append(dict(sourceKey=r['sourceKey'],modelId=m['modelId'],sourceSHA256=h,triangles=m['triangles'],asset=ref(path),method='existing-verified-government-recovery',identityAccepted=False,installationApproved=False))
    return out
   except Exception as e:return [dict(sourceKey=r['sourceKey'],modelId=r['model']['modelId'],error=type(e).__name__+': '+str(e)[:180],identityAccepted=False,installationApproved=False)for r in items]
  rows=[]
  with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:
   for future in concurrent.futures.as_completed([pool.submit(work,item)for item in grouped.items()]):rows.extend(future.result());assert reservations.heartbeat(lease)['ok'];print(json.dumps(dict(completed=len(rows),total=4)),flush=True)
  save(DOC/'recovery.json',dict(rows=rows,sourceGeometryChanges=0,newlyInstalled=0));refs=[ref(Path(__file__)),ref(INPUT),ref(HERE.parent/'enhancement-screening/shape_prepare.py'),ref(HERE.parent/'citywide-native/convert.py'),ref(HERE.parent/'citywide-native/download.py'),ref(HERE.parent/'citywide-source/discover.py')]+[ref(p)for p in DOC.iterdir()if p.is_file()]+[r['asset']for r in rows if r.get('asset')]
  refs.extend(ref(p)for p in LOCAL.rglob('download.json'))
  for q in refs:assert ref(ROOT/q['path'])==q
  kind='unmapped-exact-original-source-recovery-v1';jid=jobs.enqueue(BATCH,kind,dict(sourceKeys=[r['sourceKey']for r in records]));job=jobs.claim(BATCH,lease['owner'],[kind],lease_seconds=1800);assert job and job['id']==jid
  result=dict(jobId=jid,sourceOnly=True,newlyInstalled=0,geometryChanges=0,installationApproved=False,rows=rows,evidenceRefs=refs)
  with connect()as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease);assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);print(json.dumps(dict(jobId=jid,recovered=sum('asset'in r for r in rows),errors=[r for r in rows if 'error'in r])),flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
