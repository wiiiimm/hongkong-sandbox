"""Recover byte-identical original roof asset from its government archive, no modelling."""
from pathlib import Path
import gzip,json,zipfile,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-grandiose-roof-recover-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
SRC=BASE/'government-xl-grandiose-roof-source-v1-20261021';GROUND=BASE/'government-xl-grandiose-adjoining-ground-v1-20261021'
assert not DOC.exists();refs=[Path(__file__)];pins={}
with connect()as db:
 db.execute('SET TRANSACTION READ ONLY')
 for folder in [SRC,GROUND]:
  r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
def take(p):
 assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
source=take(SRC/'sources.json.gz')['rows'][0];m=source['model'];assert m['candidate']['uid']=='landsd/81731:0'
folder=HERE/'local'/GROUND.name/'sheets/11-NE-25B/directory';directory=take(folder/'result.json');raw=folder/'zip-directory.bin';assert digest(raw.read_bytes())==pins[str(raw.relative_to(ROOT))];refs.append(raw)
directory['models']=[x for x in directory['models']if x['modelId']==m['modelId']];assert len(directory['models'])==1
claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:landsd/81731:0'],batch=BATCH,ttl=1800);assert claim['ok'];lease=claim['reservation']
try:
 helper=module('roof_acquire',HERE/'xl-second-pass.py');helper.acquire(directory,raw,LOCAL/'original',include_terrain=False)
 with zipfile.ZipFile(LOCAL/'original'/(directory['sheet']+'.zip'))as z:
  for member in directory['models'][0]['members']:
   name=member['name'];p=LOCAL/'source'/helper.safe(name);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(name));refs.append(p)
 sourcePath=LOCAL/'source'/m['sourceEntry'];packer=module('roof_exact_packer',HERE.parent/'central-completion/pack_models.py');packed,stats=packer.pack(sourcePath);compressed=gzip.compress(packed,mtime=0);compressed=compressed[:9]+bytes([255])+compressed[10:]
 assert digest(compressed)==m['asset']['sha256'],'Recovered source differs from indexed original; retain for revision review'
 assert stats['triangles']==m['triangles']==1941;asset=LOCAL/m['asset']['asset'];asset.parent.mkdir(parents=True,exist_ok=True);asset.write_bytes(compressed)
 save(DOC/'recovered-source.json',dict(native=source,assetPath=str(asset.relative_to(ROOT)),assetSHA256=digest(compressed),geometryChanges=0))
 refs.extend(p for p in LOCAL.rglob('*')if p.is_file());refs.extend([HERE/'xl-second-pass.py',HERE.parent/'central-completion/pack_models.py'])
 summary=dict(uids=['landsd/81731:0'],modelId=m['modelId'],triangles=m['triangles'],assetSHA256=digest(compressed),exactIndexedAssetRecovered=True,installationApproved=False,newlyInstalled=0)
 module('roof_recovery_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'byte-identical-original-roof-recovery',list(dict.fromkeys(refs)),summary);print(summary)
finally:
 if reservations.owns(lease):assert reservations.release(lease)['ok']
