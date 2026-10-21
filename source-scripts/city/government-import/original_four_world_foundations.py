"""Reusable whole-source foundation checks in original and three renderer coordinates."""
import argparse
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import'
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for key in ['batch','runtime','attributes','uid']:p.add_argument('--'+key,required=True)
 a=p.parse_args();out=BASE/a.batch;assert not out.exists();refs=[Path(__file__)];cached={}
 def take(batch,path):
  if batch not in cached:cached[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  assert digest(path.read_bytes())==cached[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 selection=take(a.runtime,BASE/a.runtime/'selection.json.gz');r=next(r for r in selection['rows']if r['uid']==a.uid)
 runtime=take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz');g=next(r for r in runtime['rows']if r['uid']==a.uid)
 attributes=take(a.attributes,BASE/a.attributes/'attributes.json.gz');assert attributes['startEndAllInputsVerified'];attr=next(r for r in attributes['rows']if r['uid']==a.uid)
 asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256']==g['sourceSHA256']==attr['sourceSHA256'];refs.append(asset)
 worlds={'original':decode_original_world_triangles(asset.read_bytes())}
 for mode,field in [('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]=np.asarray(attr[field],dtype='<f8').reshape(-1,3)[np.asarray(attr['completeOriginalIndex']).reshape(-1,3)]
 captured=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];assert np.array_equal(captured,worlds['literal'])
 ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);b=r['source']['building'];polygon=Polygon(b['rings'][0],b['rings'][1:]);tool=module('four_world_foundation',HERE/'xl-final-script-pass.py');rows=[]
 for mode,triangles in worlds.items():
  assert len(triangles)==r['triangles'];f=tool.foundation_context(triangles,ground,polygon)
  row=dict(uid=a.uid,mode=mode,sourceWorldSHA256=digest(triangles.astype('<f8').tobytes()),foundation=f);save(out/(mode+'.json'),row)
  summary=dict(uid=a.uid,mode=mode,**{k:v for k,v in f.items()if k!='components'});rows.append(summary);print(summary,flush=True)
  assert f['completeTerrainTriangles']==f['triangles'] and f['fullyBuriedTriangles']==f['fullyBuriedUpwardTriangles']==0
 summary=dict(uids=[a.uid],rows=rows,installationApproved=False,sourceGeometryChanges=0);save(out/'summary.json',summary);refs.extend([HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py'])
 module('four_world_foundation_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-four-world-original-foundations',refs,summary)
if __name__=='__main__':main()
