"""Exact current installed Grandiose sources against recovered original podium."""
from pathlib import Path
import subprocess,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-grandiose-original-support-v1-20261021';DOC=BASE/BATCH;SRC=BASE/'government-xl-grandiose-missing-podium-v1-20261021'
UIDS=['landsd/81008:0','landsd/81151:0','landsd/81678:0'];SUPPORT='landsd/246824:0'
def main():
 assert not DOC.exists();receipt=read(SRC/'result.json');refs=[Path(__file__),SRC/'result.json'];pins={e['path']:e['sha256'] for e in receipt['evidenceRefs']}
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 found=read(SRC/'sources.json.gz')['rows'];assert len(found)==1;n=found[0];m=n['model']
 mp=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(mp);refs.append(mp);forms={}
 for tile in manifest['tiles']:
  path=ROOT/'3d-viewer'/tile['url']
  for b in read(path)['buildings']:
   if b['uid'] in UIDS+[SUPPORT]:forms[b['uid']]=dict(building=b,tile=tile['url'],tileSHA256=digest(path.read_bytes()));refs.append(path)
 assert set(forms)==set(UIDS+[SUPPORT]);assert len({r['building']['parent'] for r in forms.values()})==1
 old=BASE/'government-xl-thirty-spatial-original-closures-20261008/support-inputs.json';support=next(r for r in read(old)['sources'] if r['uid']==SUPPORT);refs.append(old)
 assert support['sourceSHA256']==m['asset']['sha256'] and support['modelId']==m['modelId'];support['source']=forms[SUPPORT]
 support['native']=dict(cacheKey=n['cacheKey'],resultSha=n['resultSha'],model=m)
 sources=[support]
 for url in manifest['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;cat=read(path)
  for e in cat['models']:
   if e['uid'] not in UIDS:continue
   asset=path.parent/e['asset'];assert digest(asset.read_bytes())==e['sha256'];refs.extend([path,asset]);sources.append(dict(uid=e['uid'],modelId=e['modelId'],triangles=e['triangles'],sourceSHA256=e['sha256'],source=forms[e['uid']],candidate=dict(path=str(asset.relative_to(ROOT)),entry=dict(e,rootTranslation=cat['rootTranslation']))))
 assert len(sources)==4 and len({r['uid'] for r in sources})==4
 for r in sources:
  e=r['candidate']['entry'];b=r['source']['building'];assert e['buildingCSUID']==b['buildingCSUID'] and e['objectId']==b['objectId'];assert digest((ROOT/r['candidate']['path']).read_bytes())==r['sourceSHA256']==e['sha256'];refs.append(ROOT/r['candidate']['path'])
 for p in refs:pins[str(p.relative_to(ROOT))]=digest(p.read_bytes())
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+u for u in UIDS+[SUPPORT]],batch=BATCH,ttl=1800);assert claim['ok'];lease=claim['reservation']
 try:
  save(DOC/'support-inputs.json',dict(sources=sources,pairs=[dict(uid=u,supportUid=SUPPORT) for u in UIDS]))
  tool=HERE/'disney_hotel_support_layers_v1_20261016.mjs'
  with (DOC/'worker.log').open('w') as log:subprocess.run(['/home/williamli/.nvm/versions/node/v24.18.0/bin/node',str(tool),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,check=True,stdout=log,stderr=subprocess.STDOUT,timeout=1200)
  report=read(DOC/'support-checks.json.gz');assert len(report['rows'])==3
  for p,h in {**pins,**report['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
  rows=[dict(uid=r['uid'],passed=r['interface']['passed'],samples=r['interface']['samples'],strictContacts=r['interface']['strictContacts'],unresolved=len(r['interface']['unresolved'])) for r in report['rows']]
  summary=dict(uids=UIDS+[SUPPORT],rows=rows,installationApproved=False,newlyInstalled=0);save(DOC/'summary.json',summary)
  module('grandiose_support_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-grandiose-original-podium-strict-support',list(dict.fromkeys(refs)),summary);print(summary,flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
