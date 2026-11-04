"""Bind exact original extent to current forms and independent primary footprint."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-murray-house-primary-extent-context-v1-20261021'
DOC=BASE/BATCH
UID='landsd/61216:0'

def main():
 assert not DOC.exists();refs=[Path(__file__)];consumed={}
 def take(batch,file):
  _,pins=authenticate(BASE/batch);path=BASE/batch/file;key=str(path.relative_to(ROOT));assert digest(path.read_bytes())==pins[key];consumed[key]=pins[key];refs.extend([BASE/batch/'result.json',path]);return read(path)
 component=take('government-xl-murray-house-far-components-v1-20261021','components.json')
 row=take('government-xl-murray-current-runtime-v1-20261021','selection.json.gz')['rows'][0]
 forms=take('government-xl-murray-house-regional-scope-v1-20261021','form-obligations.json.gz')
 record=take('government-xl-murray-house-primary-record-v1-20261021','primary-response.json')
 assert len(record['features'])==1 and not record.get('exceededTransferLimit')
 official=record['features'][0];assert official['attributes']['BuildingCSUID']==row['source']['building']['buildingCSUID']=='3965608830T20050430'
 assert official['attributes']['BuildingID']==row['source']['building']['buildingId']==1109347787
 assert record['spatialReference'].get('latestWkid',record['spatialReference'].get('wkid'))==2326
 path=ROOT/row['candidate']['path'];raw=path.read_bytes();assert digest(raw)==component['sourceSHA256']==row['sourceSHA256'];refs.append(path)
 tri=decode_original_world_triangles(raw);assert digest(tri.astype('<f8').tobytes())==component['worldTrianglesSHA256']
 def polygon(rings):
  out=shapely.GeometryCollection()
  for ring in rings:out=out.symmetric_difference(shapely.Polygon(ring))
  assert out.is_valid
  return out
 own=next(f for f in forms if f['uid']==UID);assert own==row['source']['building']
 primary=polygon([[(x-834500,816500-y)for x,y in ring]for ring in official['geometry']['rings']])
 current=polygon(own['rings']);projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]))
 foreign=shapely.union_all([polygon(f['rings'])for f in forms if f['uid']!=UID])
 checks={}
 for label,foot in [('primary',primary),('current',current)]:
  distance=shapely.distance(shapely.points(tri[:,:,[0,2]].reshape(-1,2)),foot).reshape(-1,3)
  far=np.flatnonzero(distance.max(1)>10).tolist();mask=np.ones(len(tri),bool);mask[far]=False
  checks[label]=dict(coverage=float(foot.intersection(projection).area/foot.area),maximumExtentM=float(distance.max()),farFaceIds=far,otherMaximumExtentM=float(distance[mask].max()),foreignExcessM2=float(projection.difference(foot).intersection(foreign).area))
 result=dict(uids=[UID],sourceSHA256=row['sourceSHA256'],worldTrianglesSHA256=component['worldTrianglesSHA256'],checks=checks,currentForms=len(forms),primaryCurrentDifferenceM2=primary.symmetric_difference(current).area,installationApproved=False,identityAccepted=False,nextStep='Review exact walkway and exterior source components with primary context; no general extent threshold change.')
 save(DOC/'summary.json',result)
 for key,h in consumed.items():assert digest((ROOT/key).read_bytes())==h
 refs.append(HERE/'exact_packed_world_geometry_20261009.py')
 module('stone_primary_extent',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-current-primary-extent-context',refs,result)
 print(result,flush=True)
if __name__=='__main__':main()
