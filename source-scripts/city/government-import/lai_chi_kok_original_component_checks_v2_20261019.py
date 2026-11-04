"""Refresh original companion contacts against final terrain; no acceptance."""
from pathlib import Path
import subprocess,numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lai-chi-kok-original-component-checks-v2-20261019';DOC=BASE/BATCH
SRC=BASE/'government-xl-lai-chi-kok-original-component-checks-v1-20261019';CAP=BASE/'government-xl-lai-chi-kok-full-terrain-metrics-v9-20261019'
assert not DOC.exists();refs=[Path(__file__)];pins={}
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY')
 for d in [SRC,CAP]:
  r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
for path,h in pins.items():assert digest((ROOT/path).read_bytes())==h;refs.append(ROOT/path)
data=read(SRC/'input.json.gz');g=read(HERE/'local'/CAP.name/'runtime-geometry.json.gz')['rows'][0];pod=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];assert len(pod)==37577 and np.array_equal(np.asarray(data['podium'])[-37577:],pod)
data['podium']=np.concatenate([np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3),pod]).tolist();save(DOC/'input.json.gz',data)
tool=HERE/'wave_retained_basic_support_v1_20261017.mjs';subprocess.run(['/home/williamli/.nvm/versions/node/v24.18.0/bin/node',str(tool),str(DOC.relative_to(ROOT))],cwd=ROOT,check=True);refs.append(tool)
support=read(DOC/'support.json.gz')
for path,h in support['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h;refs.append(ROOT/path)
summary=[dict(uid=r['uid'],strictContacts=r['proof']['strictContacts'],unresolved=len(r['proof']['unresolved']))for r in support['rows']];save(DOC/'summary.json',dict(rows=summary,installationApproved=False))
module('contacts_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'final-terrain-original-component-contact-refresh',list(dict.fromkeys(refs)),dict(uids=[r['uid']for r in data['rows']],rows=summary,installationApproved=False))
