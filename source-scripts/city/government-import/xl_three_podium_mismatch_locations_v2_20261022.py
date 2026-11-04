"""Map source-specific extent and coverage mismatches to exact cached form evidence."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-three-podium-mismatch-locations-v2-20261022';DOC=BASE/BATCH;UIDS={'landsd/277890:0','landsd/23296:0','landsd/290878:0'}
def main():
 assert not DOC.exists();src=BASE/'government-xl-remaining-forty-podium-identity-v1-20261021';_,pins=authenticate(src);refs=[Path(__file__),src/'result.json'];rows=[]
 def take(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 selection=take(src/'selection.json.gz')['rows']
 for row in selection:
  if row['uid']not in UIDS:continue
  context=take(src/row['uid'].split('/')[1]/'context.json');asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']==pins[str(asset.relative_to(ROOT))];refs.append(asset);tri=decode_original_world_triangles(asset.read_bytes());polys=shapely.polygons(tri[:,:,[0,2]]);projection=shapely.union_all(polys[shapely.area(polys)>1e-10]);b=row['source']['building'];target=shapely.make_valid(shapely.Polygon(b['rings'][0],b['rings'][1:]));excess=projection.difference(target);missing=target.difference(projection);hits=[];seen=set()
  for name,h in context['neighbourTileHashes'].items():
   p=ROOT/'3d-viewer'/name;assert name.startswith('city/data/tiles/') and digest(p.read_bytes())==h;refs.append(p)
   for f in read(p)['buildings']:
    if f['uid']in seen or f['uid']==row['uid']or not f.get('rings'):continue
    seen.add(f['uid']);foot=shapely.make_valid(shapely.Polygon(f['rings'][0],f['rings'][1:]));area=excess.intersection(foot).area
    if area>1e-8:hits.append(dict(uid=f['uid'],name=f.get('name',''),parent=f.get('parent'),sameRecordedParent=bool(b.get('parent'))and f.get('parent')==b['parent'],structureType=f.get('structureType'),base=f.get('base'),top=f.get('base',0)+f.get('height',0),excessOverlapM2=area))
  result=dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],excessAreaM2=excess.area,missingAreaM2=missing.area,excessWKT=excess.wkt,missingWKT=missing.wkt,overlappingForms=sorted(hits,key=lambda f:-f['excessOverlapM2']),installationApproved=False);save(DOC/(row['uid'].split('/')[1]+'.json'),result);rows.append(result);print(row['uid'],[(f['uid'],f['name'],round(f['excessOverlapM2'],2))for f in hits],flush=True)
 refs.append(HERE/'exact_packed_world_geometry_20261009.py');module('podium_mismatch_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-podium-footprint-mismatch-locations',list(dict.fromkeys(refs)),dict(uids=sorted(UIDS),rows=rows,installationApproved=False,sourceGeometryChanges=0))
if __name__=='__main__':main()
