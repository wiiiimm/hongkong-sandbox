"""Recovered unchanged roof versus exact original podium support check."""
from pathlib import Path
import subprocess,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-grandiose-roof-support-v1-20261021';DOC=BASE/BATCH
ROOF=BASE/'government-xl-grandiose-roof-recover-v1-20261021';POD=BASE/'government-xl-grandiose-original-support-v1-20261021'
assert not DOC.exists();refs=[Path(__file__)];pins={}
with connect()as db:
 db.execute('SET TRANSACTION READ ONLY')
 for folder in [ROOF,POD]:
  r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
def take(p):
 assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
recovered=take(ROOF/'recovered-source.json');native=recovered['native'];m=native['model'];uid=m['candidate']['uid'];podium=next(r for r in take(POD/'support-inputs.json')['sources']if r['uid']=='landsd/246824:0')
mp=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(mp);refs.append(mp);matches=[]
for tile in manifest['tiles']:
 p=ROOT/'3d-viewer'/tile['url']
 for b in read(p)['buildings']:
  if b['uid']==uid:matches.append(dict(building=b,tile=tile['url'],tileSHA256=digest(p.read_bytes())));refs.append(p)
assert len(matches)==1;form=matches[0];assert form['building']['parent']==podium['source']['building']['parent'];assert form['building']['buildingCSUID']==m['candidate']['buildingCSUID'];assert form['building']['objectId']==m['candidate']['objectId']
entry=dict(m['candidate'],rootTranslation=podium['candidate']['entry']['rootTranslation']);row=dict(uid=uid,name=form['building'].get('name'),modelId=m['modelId'],sourceSHA256=m['asset']['sha256'],triangles=m['triangles'],native=native,source=form,candidate=dict(path=recovered['assetPath'],entry=entry))
for source in [row,podium]:
 p=ROOT/source['candidate']['path'];assert digest(p.read_bytes())==source['sourceSHA256'];refs.append(p)
claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=1800);assert claim['ok'];lease=claim['reservation']
try:
 save(DOC/'selection.json.gz',dict(rows=[row],manifestSHA256=digest(mp.read_bytes())));save(DOC/'support-inputs.json',dict(sources=[row,podium],pairs=[dict(uid=uid,supportUid=podium['uid'])]))
 tool=HERE/'disney_hotel_support_layers_v1_20261016.mjs';subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,check=True)
 checked=read(DOC/'support-checks.json.gz');assert len(checked['rows'])==1
 for p,h in checked['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 proof=checked['rows'][0]['interface'];summary=dict(uids=[uid,podium['uid']],passed=proof['passed'],samples=proof['samples'],strictContacts=proof['strictContacts'],unresolved=len(proof['unresolved']),installationApproved=False,newlyInstalled=0);save(DOC/'summary.json',summary);refs.append(tool)
 module('roof_support_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'recovered-original-roof-podium-strict-interface',list(dict.fromkeys(refs)),summary);print(summary)
finally:
 if reservations.owns(lease):assert reservations.release(lease)['ok']
