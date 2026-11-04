"""Probe installed podiums against the unchanged candidate hotel source."""
from pathlib import Path
import subprocess,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-disney-hotel-podium-support-v1-20261016';DOC=BASE/BATCH
HOTEL='landsd/236354:0';UIDS=['landsd/169147:0','landsd/169148:0']
def main():
 assert not DOC.exists()
 prior=BASE/'government-xl-disney-hotel-native-regression-v1-20261016';receipt=read(prior/'result.json');refs=[Path(__file__),prior/'result.json']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for ref in receipt['evidenceRefs']:
  p=ROOT/ref['path'];assert digest(p.read_bytes())==ref['sha256'];refs.append(p)
 forms={r['building']['uid']:r['building'] for r in read(prior/'neighbour-inputs.json.gz')['rows']}
 original=BASE/'government-xl-disney-hotel-current-ground-v1-20261015/selection.json.gz';hotel=read(original)['rows'][0];assert hotel['uid']==HOTEL and hotel['source']['building']==forms[HOTEL];sources=[hotel];refs.append(original)
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json')
 for url in manifest['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;cat=read(p)
  for e in cat['models']:
   if e['uid'] in UIDS:
    asset=p.parent/e['asset'];assert digest(asset.read_bytes())==e['sha256'];refs += [p,asset]
    sources.append(dict(uid=e['uid'],sourceSHA256=e['sha256'],source=dict(building=forms[e['uid']]),candidate=dict(path=str(asset.relative_to(ROOT)),entry={**e,'rootTranslation':cat['rootTranslation']})))
 assert {r['uid'] for r in sources}==set(UIDS+[HOTEL]) and len(sources)==3
 claim=reservations.claim('hotel-podium-support-'+str(uuid.uuid4()),['building:'+u for u in UIDS+[HOTEL]],batch=BATCH,ttl=1800);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();save(DOC/'support-inputs.json',dict(sources=sources,pairs=[dict(uid=u,supportUid=HOTEL) for u in UIDS]))
  tool=HERE/'original-support-closure-interfaces.mjs'
  with(DOC/'worker.log').open('w') as log:subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=1200)
  checked=read(DOC/'support-checks.json.gz');assert len(checked['rows'])==2
  for p,h in checked['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
  summary=[]
  for row in checked['rows']:
   f=row['interface'];summary.append(dict(uid=row['uid'],supportUid=HOTEL,**{k:f[k] for k in ['passed','samples','strictContacts','wallIntersections']},unresolved=len(f['unresolved'])))
  save(DOC/'summary.json',summary)
  result=module('hotel_podium_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-hotel-supports-installed-podiums-v1',list(dict.fromkeys(refs)),dict(uids=UIDS+[HOTEL],summary=summary,fullAcceptance=False,newlyInstalled=0))
  print(dict(jobId=result['jobId'],summary=summary),flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
