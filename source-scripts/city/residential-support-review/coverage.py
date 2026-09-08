"""Actual native triangle projection coverage for new support models, never bbox-only acceptance."""
import pathlib,json,sys,numpy as np,shapely,sqlite3
from shapely.geometry import Polygon
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/residential-support-review'
sys.path.insert(0,str(ROOT/'docs/astra-city/mui-wo-buildings/review'));from bake_model_geometry import bake
read=lambda p:json.loads(p.read_bytes())
def main():
 accepted=set(read(DOC/'decisions.json')['approvedUids']);packing=read(DOC/'omitted-support/packing.json')['results']+read(DOC/'packing.json')['results'];rows=[];c=sqlite3.connect('file:'+str(ROOT/'source-scripts/city/building-batch/local/buildings.sqlite')+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
 for item in packing:
  uid=item['uid']
  if uid not in accepted or not item.get('record'):continue
  record=item['record'];mp=ROOT/item['proof']['sourceManifest'];manifest=read(mp);spec=next(s for s in manifest['models']if s['id']==record['modelId']);raw=bake(spec,mp.parent);pos=np.array(raw['position']).reshape(-1,3,3);polys=shapely.polygons(pos[:,:,[0,2]]);positive=polys[shapely.area(polys)>1e-8];surface=shapely.union_all(positive);b=c.execute('select rings_json from buildings where uid=?',(uid,)).fetchone();rings=json.loads(b['rings_json']);footprint=Polygon(rings[0],rings[1:]);footprint=footprint if footprint.is_valid else footprint.buffer(0);intersection=surface.intersection(footprint);fraction=intersection.area/footprint.area;rows.append({'uid':uid,'modelId':record['modelId'],'sourceTriangles':raw['triangles'],'projectedNativeArea':surface.area,'sourceFootprintArea':footprint.area,'coveredArea':intersection.area,'footprintCoveredFraction':fraction,'outsideSourceFootprintArea':surface.difference(footprint).area,'reviewFlag':'partial-projection-requires-assembly-review'if fraction<.8 else 'projection-screen-clear','qualification':'Projected roofs/overhangs can cover unsupported interior gaps; this screen does not establish structural support or architectural fidelity.'})
 c.close();(DOC/'coverage.json').write_text(json.dumps({'issue':'HKS-214','rows':rows,'thresholdQualification':'80% is a conservative review trigger, not a completeness assertion; no automatic geometry replacement.'},indent=2)+'\n');print(json.dumps({'checked':len(rows),'flagged':[(r['uid'],round(r['footprintCoveredFraction'],3))for r in rows if r['footprintCoveredFraction']<.8]}))
if __name__=='__main__':main()
