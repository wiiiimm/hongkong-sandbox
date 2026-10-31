"""Expose exact already-verified provider terrain paths to existing inset tools."""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for k in ['batch','donor','capture']:p.add_argument('--'+k,required=True)
 a=p.parse_args();assert all(v.startswith('government-xl-')and'/'not in v for v in vars(a).values());base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();pins={};refs=[Path(__file__)]
 def take(batch,path):
  if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
  assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 selection=take(a.capture,base/a.capture/'selection.json.gz');records=take(a.donor,base/a.donor/'source-records.json');rows=[]
 for row in selection['rows']:
  uid=row['uid'];record=records[uid];assert record['cacheKey']==row['native']['cacheKey']and record['resultSHA256']==row['native']['resultSha']
  foundation=take(a.donor,base/a.donor/(uid.split('/')[1]+'.json'));assert foundation['sourceSHA256']==row['sourceSHA256']
  ground=take(a.donor,HERE/'local'/a.donor/(uid.split('/')[1]+'-ground.json.gz'));assert digest(np.asarray(ground['completeOriginalTerrain'],dtype='<f8').tobytes())==foundation['terrainWorldSHA256']
  path=ROOT/ground['sourcePath'];assert digest(path.read_bytes())==pins[a.donor][str(path.relative_to(ROOT))];refs.append(path);gltf=read(path)
  for b in gltf['buffers']:
   f=path.parent/b['uri'];assert digest(f.read_bytes())==pins[a.donor][str(f.relative_to(ROOT))];refs.append(f)
  rows.append(dict(uid=uid,sourceSHA256=row['sourceSHA256'],nativeResultSHA256=record['resultSHA256'],sourceTerrainPaths=[str(path.relative_to(ROOT))],status='original-terrain-checked',originalTerrainFoundation=foundation['foundation'],installationApproved=False))
 result=dict(uids=[r['uid']for r in rows],rows=rows,sourceGeometryChanges=0,terrainGeometryChanges=0,publication=False,installationApproved=False,qualification='Schema binding of already independently measured same-native-result terrain. Exact glTF/buffer hashes and full decoded terrain hash verified; no source/terrain edits or acceptance transfer.')
 save(out/'summary.json',result);module('cached_terrain_path_binding',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'hash-bound-original-terrain-paths-and-foundation-context',refs,result)
if __name__=='__main__':main()
