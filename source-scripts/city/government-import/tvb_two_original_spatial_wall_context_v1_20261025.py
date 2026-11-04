"""Measure exact TVB compound spatial bounds and face60; no acceptance or edits."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-tvb-two-original-spatial-wall-context-v1-20261025'
RUNTIME='government-xl-tvb-two-original-private-runtime-v2-20261025'
ATTRS='government-xl-tvb-two-original-private-attributes-v2-20261025'
SOURCES={'landsd/9778:0':'268fa418585fc618d40a9c603e7dbcb579f36a6326d6d79711ac4943f5dadabf','landsd/132578:0':'fd6c6ecd8d665b34aa2844a8f22bbfbd892d84515056cb347484e8fabdbbfa0f'}

def main():
 out=BASE/BATCH;assert not (out/'result.json').exists()
 refs=[Path(__file__)];pins={}
 def take(batch,name='summary.json'):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  p=BASE/batch/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 rows={r['uid']:r for r in take(RUNTIME,'selection.json.gz')['rows']}
 attrs={r['uid']:r for r in take(ATTRS,'attributes.json.gz')['rows']}
 assert {u:r['sourceSHA256']for u,r in rows.items()}==SOURCES
 worlds={};forms={}
 for u,r in rows.items():
  asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==SOURCES[u]==attrs[u]['sourceSHA256'];refs.append(asset)
  a=attrs[u];ix=np.asarray(a['completeOriginalIndex']).reshape(-1,3)
  worlds[u]={'original':decode_original_world_triangles(asset.read_bytes()),**{m:np.asarray(a[k]).reshape(-1,3)[ix]for m,k in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]}}
  forms[u]=r['source']['building']
 scope='government-xl-tvb-two-original-current-scope-v1-20261025'
 allforms={}
 for r in take(scope)['rows']:
  assert not r['nearbyNativeActors'] and r['currentNativeActorsChecked']==6924
  for f in take(scope,r['uid'].split('/')[1]+'-forms.json.gz'):allforms[f['building']['uid']]=f['building']
 assert set(allforms)==set(SOURCES)|{'way/186639167:0'}
 polygon=lambda f:shapely.Polygon(f['rings'][0],f['rings'][1:])
 target=shapely.union_all([polygon(f)for f in forms.values()]);foreign=polygon(allforms['way/186639167:0'])
 measures=[];walls=[]
 paths='government-xl-tvb132578-ground-root-paths-v1-20261025'
 for mode in ['original','literal','leftF32','balancedF32']:
  tri=np.concatenate([worlds[u][mode]for u in SOURCES]);projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]))
  coverage=projection.intersection(target).area/target.area
  extent=float(shapely.distance(shapely.points(tri[:,:,[0,2]].reshape(-1,2)),target).max())
  excess=projection.difference(target).intersection(foreign).area
  assert coverage>=.95 and extent<=10 and excess<=1
  measures.append(dict(mode=mode,compoundTargetCoverage=coverage,maximumExtentM=extent,unrelatedExcessM2=excess))
  tri=worlds['landsd/132578:0'][mode];face=tri[60];normal=np.cross(face[1]-face[0],face[2]-face[0]);ratio=float(abs(normal[1])/np.linalg.norm(normal))
  assert ratio<.25
  p=take(paths,mode+'.json.gz');assert p['sourceWorldSHA256']==digest(tri.astype('<f8').tobytes())
  assert len(p['originalSourcePaths'])==2
  for r in p['originalSourcePaths']:
   assert r['faces']==[60] and r['hasUnrestrictedFiniteAttachment'] and r['passesExistingEndpointHeight']
   assert r['maximumResidualM']==0 and r['riseAboveEndpointsM']==0
   assert r['witness']['position'][1]==float(face[:,1].min())
  walls.append(dict(mode=mode,face=60,vertices=face.tolist(),absNormalYRatio=ratio,finitePaths=2,pathsEntirelyOnFace60=True,rawDirectRimFailuresPreserved=True))
 result=dict(uids=sorted(SOURCES),sourceSHA256ByUid=SOURCES,compoundSpatialMeasures=measures,wallContext=walls,physicalAcceptance=False,installationApproved=False,sourceGeometryChanges=0,sourcePoseChanges=0,qualification='Bounded numerical source context only. Two raw direct-rim failures remain failures; finite original-wall paths are not engineering or publication approval. Unrelated OSM building is included in foreign excess and remains unchanged.')
 save(out/'summary.json',result)
 refs +=[HERE/'exact_packed_world_geometry_20261009.py']
 module('tvb_spatial_wall_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-tvb-compound-spatial-and-original-wall-path-context',refs,result)
 print(result,flush=True)
if __name__=='__main__':main()
