"""Quantify each rejected exact-GeoRef pair without relaxing the match screen."""
from run import HERE, DOC, load, dump, existing_folders
from shapely.geometry import MultiPoint
from prepare_model_sample import model_geometry
from compare_official import official_shape

def main():
 features={f['attributes']['OBJECTID']:f for f in load(HERE.parent/'mui-wo-buildings/landsd-mui-wo.json.gz')['features']}
 folders={load(p/'manifest.json')['tile']:p for p in existing_folders()}
 folders.update({p.name:p for p in (HERE/'staged').iterdir()});rows=[]
 for r in load(DOC/'ledger.json')['rows']:
  if r['reason']!='source-georef-present-but-geometric-or-component-match-rejected':continue
  shape=official_shape(features[int(r['uid'].split('/')[1].split(':')[0])])
  for c in r['sameGeoRefModels']:
   folder=folders[c['sheet']];m=load(folder/'manifest.json');s=next(x for x in m['models'] if x['id']==c['id']);file=folder/s['url'];data=load(file);positions,_=model_geometry(data,lambda uri:(file.parent/uri).read_bytes());hull=MultiPoint(positions[:,[0,2]]).convex_hull
   rows.append({'uid':r['uid'],'modelId':s['id'],'sheet':c['sheet'],'overlapOfSmallerFootprint':hull.intersection(shape).area/min(hull.area,shape.area),'centroidDistanceMetres':hull.centroid.distance(shape.centroid),'sourceFootprintArea':shape.area,'sourceModelHullArea':hull.area,'worldBounds':s['worldBounds']})
 dump(DOC/'rejected-match-measurements.json',rows)
 print('Measured rejected model/footprint pairs:',len(rows))
if __name__=='__main__':main()
