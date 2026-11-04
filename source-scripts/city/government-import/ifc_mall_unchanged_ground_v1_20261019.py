"""Fresh current-map IFC capture without any terrain replacement."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ifc-mall-unchanged-ground-v1-20261019';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
SRC=BASE/'government-xl-ifc-mall-private-ground-v2-20261019';ATTR=BASE/'government-xl-ifc-mall-actual-render-attributes-v1-20261019'
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [SRC,ATTR]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for path,h in pins.items():assert digest((ROOT/path).read_bytes())==h,path
 rows=read(SRC/'selection.json.gz')['rows'];assert len(rows)==1 and rows[0]['uid']=='landsd/64856:0'
 for row in rows:
  raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];asset=LOCAL/row['candidate']['entry']['asset'];asset.parent.mkdir(parents=True,exist_ok=True);asset.write_bytes(raw);row['candidate']['path']=str(asset.relative_to(ROOT));refs.append(asset)
 save(DOC/'selection.json.gz',dict(rows=rows,manifestSHA256=digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())))
 save(DOC/'terrain-candidates.json',[])
 tool=HERE/'acceptance-metrics-multi-retained.mjs'
 subprocess.run(['node',str(tool),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str(LOCAL.relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))],cwd=ROOT,check=True)
 metrics=read(DOC/'metrics.json');assert len(metrics['rows'])==1 and not metrics['rows'][0].get('error')
 for path,h in {**pins,**metrics['inputHashes']}.items():assert digest((ROOT/path).read_bytes())==h,path;refs.append(ROOT/path)
 refs.extend([tool,LOCAL/'runtime-geometry.json.gz'])
 module('ifc_current_capture_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'ifc-fresh-unchanged-installed-terrain-capture',list(dict.fromkeys(refs)),dict(uids=['landsd/64856:0'],metrics=metrics['rows'],terrainReplacements=0,neighbourTerrainChanges=0,installationApproved=False))
if __name__=='__main__':main()
