"""Select existing official forms; reuse retained government identity attributes.
The small ESRI-style matching input is explicitly derived, not a new native survey.
Original city footprint vertices are retained by the publisher.
"""
import gzip,hashlib,importlib.util,json,pathlib,sys
from shapely.geometry import box,Polygon
from pyproj import Transformer
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'3d-viewer/city/data'
sys.path.insert(0,str(HERE.parent/'landsd-territory'))
from retain import iter_features

def main():
 config=json.loads((HERE/'config.json').read_text());e0,n0,e1,n1=config['sourceBoundsHK1980'];pad=config['selectionBufferMetres'];bounds=[e0-834500-pad,816500-n1-pad,e1-834500+pad,816500-n0+pad];selection=box(*bounds)
 buildings=[];manifest=json.loads((OUT/'manifest.json').read_text())
 for t in manifest['tiles']:
  if not box(*t['bounds']).intersects(selection):continue
  for b in json.loads((ROOT/'3d-viewer'/t['url']).read_text())['buildings']:
   if b['id'].startswith('landsd/') and selection.intersects(Polygon(b['rings'][0],b['rings'][1:])):buildings.append(b)
 ids={b['objectId'] for b in buildings};source=HERE.parent/'landsd-territory/landsd-hong-kong-source.geojson.gz';found={}
 for f in iter_features(source):
  if f['properties']['OBJECTID'] in ids:found[f['properties']['OBJECTID']]=f
 assert set(found)==ids
 project=Transformer.from_crs(4326,2326,always_xy=True);features=[]
 for oid,f in sorted(found.items()):
  polygons=[f['geometry']['coordinates']] if f['geometry']['type']=='Polygon' else f['geometry']['coordinates']
  rings=[[[*project.transform(*p)] for p in ring] for polygon in polygons for ring in polygon]
  features.append({'attributes':f['properties'],'geometry':{'rings':rings}})
 snapshot={'datasetVersion':'Building_Outline_Public_v20260819','spatialReference':{'wkid':2326},'derivation':'Selected from retained official territory GeoJSON, projected from CRS84 to EPSG:2326 with pyproj. Complete original polygons retained; not a fresh native-coordinate survey.','source':str(source.relative_to(ROOT)),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'features':features}
 (HERE/'official-selection.json.gz').write_bytes(gzip.compress(json.dumps(snapshot,separators=(',',':'),ensure_ascii=False).encode(),mtime=0))
 by_id={f['attributes']['OBJECTID']:f['attributes'] for f in features}
 for b in buildings:b['sourceAttributes']=by_id[b['objectId']]
 # Whole matched components are retained; only the selection extent is approximate.
 inverse=Transformer.from_crs(2326,4326,always_xy=True);corners=[inverse.transform(e,n) for e in [e0-pad,e1+pad] for n in [n0-pad,n1+pad]]
 package={'area':config['area'],'bboxWGS84':[min(p[0] for p in corners),min(p[1] for p in corners),max(p[0] for p in corners),max(p[1] for p in corners)],'sourceBoundsHK1980':config['sourceBoundsHK1980'],'selectionBufferMetres':pad,'buildings':buildings}
 (HERE/'building-selection.json.gz').write_bytes(gzip.compress(json.dumps(package,separators=(',',':'),ensure_ascii=False).encode(),mtime=0))
 print(json.dumps({'officialSourceIds':len(ids),'selectedForms':len(buildings),'worldBounds':bounds,'bboxWGS84':package['bboxWGS84']}))
if __name__=='__main__':main()
