"""Nominate current actors using the complete four-stream original source bounds."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-olympic-station-foreign-scope-plan-v1-20261022'
def main():
 doc=BASE/BATCH;assert not doc.exists();refs=[Path(__file__)];pins={}
 def take(batch,name):
  folder=BASE/batch;_,p=authenticate(folder);path=folder/name;assert digest(path.read_bytes())==p[str(path.relative_to(ROOT))];refs.extend([folder/'result.json',path]);return read(path)
 rows=take('government-xl-olympic-station-band-runtime-v1-20261022','selection.json.gz')['rows'];row=rows[0];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset);original=decode_original_world_triangles(asset.read_bytes());a=take('government-xl-olympic-station-original-attributes-v1-20261022','attributes.json.gz')['rows'][0];allpositions=[original.reshape(-1,3)]+[np.asarray(a[k]).reshape(-1,3)for k in ['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']];lo=np.minimum.reduce([p.min(0)for p in allpositions]);hi=np.maximum.reduce([p.max(0)for p in allpositions]);domain=shapely.box(lo[0],lo[2],hi[0],hi[2]);inventory=take('government-xl-after-aquarium-current-inventory-v1-20261022','complete-bounds.json.gz');manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);assert digest(manifestpath.read_bytes())==read(BASE/'government-xl-olympic-station-band-runtime-v1-20261022/selection.json.gz')['manifestSHA256'];refs.append(manifestpath);native={r['uid']:r for r in inventory['rows']};touch=[]
 for r in inventory['rows']:
  bounds=np.asarray(r['completeFourWorldBounds']);hit=any(not(np.any(b[0]>hi)or np.any(b[1]<lo))for b in bounds)
  if hit:touch.append(r)
 forms=[];selection=[];found={};catalogues={}
 for url in manifest['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;refs.append(path)
  for e in read(path)['models']:
   assert e['uid']in native and native[e['uid']]['sourceSHA256']==e['sha256'];catalogues[e['uid']]=(e,path)
 for entry in manifest['tiles']:
  path=ROOT/'3d-viewer'/entry['url'];assert digest(path.read_bytes())==inventory['currentFormTileHashes'][str(path.relative_to(ROOT))];refs.append(path)
  for f in read(path)['buildings']:
   points=np.asarray([p for ring in f.get('rings',[])for p in ring])
   if not len(points):continue
   low,high=points.min(0),points.max(0);bbox=shapely.box(low[0],low[1],high[0],high[1])
   if domain.intersects(bbox)and f['uid']!='landsd/81242:0':forms.append(dict(building=f,tile=entry['url'],tileSHA256=digest(path.read_bytes()),isInstalledNative=f['uid']in native))
   if any(r['uid']==f['uid']for r in touch):found[f['uid']]=dict(building=f,tile=entry['url'],tileSHA256=digest(path.read_bytes()))
 for r in touch:
  e,catpath=catalogues[r['uid']];assetpath=catpath.parent/e['asset'];assert digest(assetpath.read_bytes())==e['sha256'];refs.append(assetpath);selection.append(dict(uid=r['uid'],sourceSHA256=e['sha256'],triangles=e['triangles'],candidate=dict(path=str(assetpath.relative_to(ROOT)),entry=e),source=found[r['uid']],native=dict(model=dict(triangles=e['triangles']))))
 save(doc/'selection.json.gz',dict(rows=selection,manifestSHA256=digest(manifestpath.read_bytes()),qualification='Existing installed actor renderer capture only; synthetic native.model.triangles repeats current catalogue count and is not a native-stage acceptance claim.'));save(doc/'forms.json.gz',forms);save(doc/'touching-native-bounds.json.gz',touch)
 result=dict(uids=['landsd/81242:0'],completeSourceFourStreamBounds=[lo.tolist(),hi.tolist()],allCurrentNativeActors=len(native),touchingNativeUids=[r['uid']for r in touch],candidateForeignForms=len(forms),embeddedForeignForms=[r['building']['uid']for r in forms if r['building'].get('modelGeometry')],completeCurrentTileHashesVerified=True,sourceGeometryChanges=0,installationApproved=False,newlyInstalled=0);save(doc/'summary.json',result);refs.append(HERE/'exact_packed_world_geometry_20261009.py');module('aquarium_foreign_plan_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-source-current-foreign-actor-nomination',refs,result);print(result)
if __name__=='__main__':main()
