"""Recover one exact original pool component; no acceptance or publication."""
import sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from primrose_compound_foundation_v2_20261015 import module
sys.path.insert(0,str(HERE.parent/'enhancement-screening'))
from shape_prepare import prepare
BATCH='government-xl-sham-shui-po-pool-tower-acquire-v1-20261016'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
UID='landsd/271043:0'
def main():
 assert not DOC.exists() and not LOCAL.exists()
 source=HERE/'local/government-xl-sham-shui-po-pool-tower-lookup-v1-20261016/input.json.gz'
 e=read(source);o=e['native'][0]
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  actual=c.execute('SELECT r.result_sha,r.result FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,o['cacheKey'])).fetchone()
 assert actual[0]==o['resultSha'] and o['model'] in actual[1]['models']
 manifest=ROOT/'3d-viewer/city/data/manifest.json';forms={}
 for t in read(manifest)['tiles']:
  p=ROOT/'3d-viewer'/t['url']
  for b in read(p)['buildings']:
   if b['uid']==UID:forms[UID]=dict(building=b,tile=t['url'],tileSHA256=digest(p.read_bytes()))
 assert len(forms)==1
 e['sources']=forms
 claim=reservations.claim('pool-original-component-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();save(DOC/'input.json.gz',e)
  result=prepare(DOC/'input.json.gz',LOCAL,allow_source=True,workers=1,reservation_receipt=lease)
  assert not result['errors'] and len(result['rows'])==1,result['errors']
  r=result['rows'][0];asset=Path(r['candidate']['path']);assert digest(asset.read_bytes())==o['model']['asset']['sha256']
  row=dict(uid=UID,modelId=o['model']['modelId'],native=o,sourceSHA256=o['model']['asset']['sha256'],triangles=o['model']['triangles'],source=forms[UID],candidate=dict(entry=r['candidate']['entry'],path=str(asset.relative_to(ROOT))))
  save(DOC/'selection.json.gz',dict(rows=[row],manifestSHA256=digest(manifest.read_bytes())))
  refs=[Path(__file__),source,manifest,ROOT/'3d-viewer'/forms[UID]['tile'],HERE.parent/'enhancement-screening/shape_prepare.py']+[p for p in LOCAL.rglob('*') if p.is_file() and p.name!='reservation.json']
  frozen=module('pool_acquire_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-pool-tower-acquisition-v1',refs,dict(uids=[UID],sourceSHA256=row['sourceSHA256'],newlyInstalled=0,fullAcceptance=False,originalGeometryChanges=0))
  print(dict(jobId=frozen['jobId'],recovered=UID,triangles=row['triangles']),flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
