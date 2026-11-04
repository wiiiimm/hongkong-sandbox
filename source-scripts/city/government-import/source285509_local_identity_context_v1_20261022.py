"""Bind source podium failure groups to current neighbouring forms; no ownership inference."""
from pathlib import Path
import numpy as np
import shapely
from pyproj import Transformer
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-source-285509-local-identity-context-v1-20261022';DOC=BASE/BATCH;UID='landsd/285509:0'
def main():
 assert not DOC.exists();refs=[Path(__file__)]
 def take(batch,p):
  _,pins=authenticate(BASE/batch);assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.extend([BASE/batch/'result.json',p]);return read(p)
 cap='government-xl-next-three-terrain-runtime-v1-20261021';row=next(r for r in take(cap,BASE/cap/'selection.json.gz')['rows']if r['uid']==UID);b=row['source']['building'];target=shapely.Polygon(b['rings'][0],b['rings'][1:]);tile=ROOT/'3d-viewer'/row['source']['tile'];assert digest(tile.read_bytes())==row['source']['tileSHA256'];refs.append(tile)
 neighbours=[]
 for f in read(tile)['buildings']:
  if f['uid']==UID or not f.get('rings'):continue
  poly=shapely.make_valid(shapely.Polygon(f['rings'][0],f['rings'][1:]))
  if poly.distance(target)>75:continue
  neighbours.append((f,poly))
 loc='government-xl-source-285509-failure-locations-v1-20261022';groups=take(loc,BASE/loc/'failure-locations.json.gz')['groups'];results=[]
 for g in groups:
  tri=np.asarray(g['triangles']);projection=shapely.union_all([shapely.MultiPoint(f[:,[0,2]]).convex_hull for f in tri]);hits=[]
  for f,poly in neighbours:
   area=projection.intersection(poly).area
   if area>0:hits.append(dict(uid=f['uid'],name=f.get('name',''),structureType=f.get('structureType'),base=f.get('base'),top=f.get('base',0)+f.get('height',0),projectedOverlapM2=area))
  results.append(dict(group=g['group'],runtimeFaces=len(g['canonicalRuntimeFaceIds']),failedBounds=g['bounds'],overlappingCurrentForms=hits))
 centre=b['centre'];lon,lat=Transformer.from_crs(2326,4326,always_xy=True).transform(834500+centre[0],816500-centre[1]);summary=dict(uids=[UID],sourceSHA256=row['sourceSHA256'],recordedStructureType=b['structureType'],recordedBaseHKPD=b['baseHeightHKPD'],recordedTopHKPD=b['topHeightHKPD'],coordinate=dict(latitude=lat,longitude=lon,source='EPSG2326 to EPSG4326 from recorded local centre'),nearbyNamedForms=[dict(uid=f['uid'],name=f.get('name'),base=f.get('base'),top=f.get('base',0)+f.get('height',0))for f,_ in neighbours if f.get('name')],groups=results,installationApproved=False,qualification='Local same-tile context only, not a complete terrain-change neighbour census or certification of ownership/architectural purpose. Government source name remains empty. Spatial association does not resolve buried-face failures.')
 save(DOC/'context.json',summary);module('285509_identity_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-source-local-identity-context',refs,summary);print(dict(groups=len(results),groupsOverlappingOtherForms=sum(bool(r['overlappingCurrentForms'])for r in results),latitude=lat,longitude=lon),flush=True)
if __name__=='__main__':main()
