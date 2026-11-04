"""Actual eight-original renderer/terrain metrics in private files only."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lai-chi-kok-eight-runtime-v2-20261019';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
SRC=BASE/'government-xl-lai-chi-kok-eight-render-attributes-v1-20261019';TERR=BASE/'government-xl-lai-chi-kok-full-terrain-metrics-v5-20261019'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [SRC,TERR]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 selection=read(SRC/'selection.json.gz');manifest=ROOT/'3d-viewer/city/data/manifest.json';selection['manifestSHA256']=digest(manifest.read_bytes());assert len(selection['rows'])==8
 for row in selection['rows']:
  raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];p=LOCAL/row['candidate']['entry']['asset'];assert p.resolve().is_relative_to(LOCAL.resolve());p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);row['candidate']['path']=str(p.relative_to(ROOT));refs.append(p)
 save(DOC/'selection.json.gz',selection);candidates=read(TERR/'terrain-candidates.json');save(DOC/'terrain-candidates.json',candidates)
 tool=HERE/'acceptance-metrics-multi-retained.mjs';cmd=['/home/williamli/.nvm/versions/node/v24.18.0/bin/node',str(tool),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str(LOCAL.relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))]
 with (DOC/'worker.log').open('w')as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=900)
 metrics=read(DOC/'metrics.json');assert len(metrics['rows'])==8
 for p,h in metrics['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 refs.extend([tool,manifest,LOCAL/'runtime-geometry.json.gz']);save(DOC/'summary.json',dict(rows=metrics['rows'],installationApproved=False))
 module('eight_runtime_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'eight-originals-current-terrain-actual-runtime',list(dict.fromkeys(refs)),dict(uids=[r['uid']for r in selection['rows']],rows=metrics['rows'],installationApproved=False))
if __name__=='__main__':main()
