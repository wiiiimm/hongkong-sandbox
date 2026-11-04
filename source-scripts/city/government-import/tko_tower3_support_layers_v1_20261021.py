"""Diagnose original TKO Tower 3 support layers without changing acceptance."""
from pathlib import Path
import subprocess, uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-tko-tower3-support-layers-v1-20261021'
DOC=BASE/BATCH
PRIOR=BASE/'government-xl-next-twenty-current-terrain-v6-20261021'
def main():
 assert not DOC.exists()
 receipt=read(PRIOR/'result.json'); refs=[Path(__file__),PRIOR/'result.json']; pins={}
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for e in receipt['evidenceRefs']:
  assert e['path'] not in pins or pins[e['path']]==e['sha256']
  pins[e['path']]=e['sha256']
 for p,h in pins.items():
  assert digest((ROOT/p).read_bytes())==h,p
  refs.append(ROOT/p)
 tower=next(r for r in read(PRIOR/'selection.json.gz')['rows'] if r['uid']=='landsd/32147:0')
 old=BASE/'government-xl-georef-tko3a-original-support-20261008/support-inputs.json'
 support=next(r for r in read(old)['sources'] if r['uid']=='landsd/265489:0')
 refs.append(old)
 # Bind recovered historical source to exact authoritative native-stage bytes.
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  native=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(support['native']['cacheKey'],)).fetchone()
  assert native[0]==support['native']['resultSha']
  assert support['native']['model'] in native[1]['models']
 manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);refs.append(manifestpath)
 matches=[]
 for tile in manifest['tiles']:
  path=ROOT/'3d-viewer'/tile['url']
  for b in read(path)['buildings']:
   if b['uid']==support['uid']:matches.append((b,tile['url'],path))
 assert len(matches)==1
 b,tile,path=matches[0];refs.append(path)
 assert b['objectId']==support['candidate']['entry']['objectId'] and b['buildingCSUID']==support['candidate']['entry']['buildingCSUID']
 assert b['parent']==tower['source']['building']['parent']
 support['source']=dict(building=b,tile=tile)
 inputs=dict(sources=[tower,support],pairs=[dict(uid=tower['uid'],supportUid=support['uid'])])
 for path in refs:
  pins[str(path.relative_to(ROOT))]=digest(path.read_bytes())
 uids=sorted(r['uid'] for r in inputs['sources'])
 assert uids==['landsd/265489:0','landsd/32147:0']
 claim=reservations.claim('tko-tower3-support-layers-'+str(uuid.uuid4()),['building:'+u for u in uids],batch=BATCH,ttl=1800)
 assert claim['ok']; lease=claim['reservation']
 try:
  DOC.mkdir();save(DOC/'support-inputs.json',inputs)
  tool=HERE/'disney_hotel_support_layers_v1_20261016.mjs'
  with (DOC/'worker.log').open('w') as log:
   subprocess.run(['/home/williamli/.nvm/versions/node/v24.18.0/bin/node',str(tool),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=1200)
  checked=read(DOC/'support-checks.json.gz');assert len(checked['rows'])==1
  for p,h in {**pins,**checked['inputHashes']}.items():
   assert digest((ROOT/p).read_bytes())==h,p
   refs.append(ROOT/p)
  row=checked['rows'][0];f=row['interface']
  summary=dict(uids=uids,passed=f['passed'],samples=f['samples'],strictContacts=f['strictContacts'],unresolved=len(f['unresolved']),layerClassifications={k:sum(x['classification']==k for x in row['layerDiagnostic']['rows']) for k in sorted({x['classification'] for x in row['layerDiagnostic']['rows']})},installationApproved=False,newlyInstalled=0)
  save(DOC/'summary.json',summary)
  result=module('tko_tower3_layers_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-support-layer-diagnostic',list(dict.fromkeys(refs)),summary)
  print(dict(jobId=result['jobId'],summary=summary),flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
