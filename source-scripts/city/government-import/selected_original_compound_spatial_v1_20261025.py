"""Measure four-world compound spatial limits for an explicit original selection; no approval."""
import argparse
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for k in ['batch','runtime','attributes','terrain-scope']:p.add_argument('--'+k,required=True)
 a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.runtime,a.attributes,a.terrain_scope])and not out.exists();refs=[Path(__file__)];pins={}
 def take(n,path):
  if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
  assert digest(path.read_bytes())==pins[n][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 selected=take(a.runtime,base/a.runtime/'selection.json.gz');attrs=take(a.attributes,base/a.attributes/'attributes.json.gz');assert attrs['startEndAllInputsVerified'];attributes={r['uid']:r for r in attrs['rows']}
 scope=take(a.terrain_scope,base/a.terrain_scope/'scope.json');forms={r['uid']:r for r in take(a.terrain_scope,base/a.terrain_scope/'form-obligations.json.gz')}
 sources={r['uid']:r for r in selected['rows']};assert len(sources)==len(selected['rows'])and set(scope['uids'])==set(sources)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256']==pins[a.terrain_scope][str(manifest.relative_to(ROOT))];refs.append(manifest)
 geometry={r['uid']:r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']};worlds={};hashes={}
 for u,r in sources.items():
  assert forms[u]==r['source']['building'];attr=attributes[u];g=geometry[u];asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256']==attr['sourceSHA256']==g['sourceSHA256'];refs.append(asset);ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
  worlds[u]={'original':decode_original_world_triangles(asset.read_bytes()),**{m:np.asarray(attr[k]).reshape(-1,3)[ix]for m,k in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]}}
  assert all(len(t)==r['triangles']for t in worlds[u].values())and np.array_equal(worlds[u]['literal'],np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)])
  hashes[u]=r['sourceSHA256']
 polygon=lambda f:shapely.Polygon(f['rings'][0],f['rings'][1:]);target=shapely.union_all([polygon(forms[u])for u in sources]);foreign=shapely.union_all([polygon(f)for u,f in forms.items()if u not in sources]);measures=[]
 for mode in ['original','literal','leftF32','balancedF32']:
  tri=np.concatenate([worlds[u][mode]for u in sources]);projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));coverage=projection.intersection(target).area/target.area;extent=float(shapely.distance(shapely.points(tri[:,:,[0,2]].reshape(-1,2)),target).max());excess=projection.difference(target).intersection(foreign).area
  measures.append(dict(mode=mode,compoundTargetCoverage=coverage,maximumExtentM=extent,unrelatedExcessM2=excess,passed=bool(coverage>=.95 and extent<=10 and excess<=1)))
 result=dict(uids=sorted(sources),sourceSHA256ByUid=hashes,requiredOriginalAssembly=hashes,rows=measures,allFourSpatialLimitsPassed=all(r['passed']for r in measures),limits=dict(minimumTargetCoverage=.95,maximumExtentM=10,maximumUnrelatedExcessM2=1),unrelatedCurrentForms=len(forms)-len(sources),sourceGeometryChanges=0,identityAccepted=False,installationApproved=False,qualification='Explicit complete selected-source projections only; raw individual identity/cell failures remain. Compound limits are unchanged95percent/10m/1m2. No same-parent/permit ownership exemption, source-role or publication approval is inferred; source assembly must be reviewed separately.')
 save(out/'summary.json',result);refs.append(HERE/'exact_packed_world_geometry_20261009.py');module('compound_original_spatial_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'explicit-original-assembly-four-world-spatial-measures',refs,result);print(measures,flush=True)
if __name__=='__main__':main()
