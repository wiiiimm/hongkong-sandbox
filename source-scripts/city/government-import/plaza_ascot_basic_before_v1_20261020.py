"""Correct capture-domain limits without changing source meshes or acceptance thresholds."""
from pathlib import Path
import subprocess
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'; BATCH='government-xl-plaza-ascot-basic-before-v1-20261020'; DOC=BASE/BATCH
BASIC=BASE/'government-xl-plaza-ascot-basic-support-v1-20261020'; PATCH=BASE/'government-xl-plaza-ascot-terrain-validation-v2-20261020'
def main():
 assert not DOC.exists(); refs=[Path(__file__)]; pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [BASIC,PATCH]:
   r=read(folder/'result.json'); assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
   refs.append(folder/'result.json'); pins.update({e['path']:e['sha256'] for e in r['evidenceRefs']})
 for p in [BASIC/'basic-geometry.json',PATCH/'terrain-candidates.json']:
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p)
 save(DOC/'no-patches.json',[]); save(DOC/'input.json',dict(basicGeometry=str((BASIC/'basic-geometry.json').relative_to(ROOT)),patches=str((DOC/'no-patches.json').relative_to(ROOT))))
 tool=HERE/'plaza_ascot_basic_ground_v2_20261020.mjs'; subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))],cwd=ROOT,check=True);refs.append(tool)
 cap=read(DOC/'ground.json.gz');podium=np.asarray(read(BASIC/'input.json.gz')['podium']);assert digest((BASIC/'input.json.gz').read_bytes())==pins[str((BASIC/'input.json.gz').relative_to(ROOT))];refs.append(BASIC/'input.json.gz')
 final=module('ascot_complete_basic_foundation',HERE/'xl-final-script-pass.py');refs.append(HERE/'xl-final-script-pass.py');rows=[]
 for r in cap['rows']:
  t=np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)];ground=np.asarray(r['drawnGroundGeometry']).reshape(-1,3,3);b=r['currentBuilding'];f=final.foundation_context(t,ground,Polygon(b['rings'][0],b['rings'][1:]));save(DOC/(r['uid'].split('/')[1]+'-foundation.json'),f);item=dict(uid=r['uid'],**{k:v for k,v in f.items() if k!='components'});rows.append(item);print(item,flush=True)
 for p,h in cap['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 result=dict(uids=[r['uid'] for r in rows],rows=rows,installationApproved=False,sourceGeometryChanges=0,productionTerrainChanges=0)
 save(DOC/'summary.json',result);module('ascot_basic_ground_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-rendered-basic-neighbour-before-terrain',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
