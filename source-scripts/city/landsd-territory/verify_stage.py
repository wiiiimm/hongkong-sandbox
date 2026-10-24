"""Independent offline checks of staged artefacts against retained source records."""
import collections,math,json
from shapely.geometry import Polygon
from retain import iter_features
from source import HERE,ROOT,DOCS,read_json,digest,save_json


def main():
 manifest=read_json(ROOT/'3d-viewer/city/data/landsd-territory/manifest.json');uids=set();records=collections.defaultdict(list);counts=collections.Counter();largest=0
 assert manifest['stagingOnly'] and manifest['noOSMMerge'];assert manifest['tileSize']==2000
 for tile in manifest['tiles']:
  path=ROOT/'3d-viewer'/tile['url'];raw=path.read_bytes();assert len(raw)==tile['bytes'];assert digest(raw)==tile['sha256'];data=json.loads(raw);assert data['id']==tile['id'];assert len(data['buildings'])==tile['counts']['buildings'];largest=max(largest,len(raw))
  x0,z0,x1,z1=tile['bounds']
  for b in data['buildings']:
   assert b['tile']==tile['id'];assert b['uid'] not in uids;uids.add(b['uid']);assert b['id']==f'landsd/{b["objectId"]}'
   assert 'sourceAttributes' not in b and b['sourceDataset']=='landsd-territory'
   assert all(isinstance(n,(int,float)) and math.isfinite(n) for n in [b['base'],b['height'],b['renderTopHeight']]);assert b['height']>0;assert abs(b['base']+b['height']-b['renderTopHeight'])<.00001
   assert all(ring[0]==ring[-1] for ring in b['rings']);assert all(x0<=x<=x1 and z0<=z<=z1 for ring in b['rings'] for x,z in ring)
   p=Polygon(b['rings'][0],b['rings'][1:]);assert p.is_valid and not p.is_empty and p.area>0,b['uid']
   records[b['objectId']].append({key:b[key] for key in ['uid','buildingCSUID','structureType','baseHeightHKPD','topHeightHKPD','base','height','heightSource']});counts['components']+=1;counts['height:'+b['heightSource']]+=1
 checked=set()
 for feature in iter_features(HERE/'landsd-hong-kong-source.geojson.gz'):
  a=feature['properties'];oid=a['OBJECTID'];assert oid in records;checked.add(oid)
  for b in records[oid]:
   assert b['buildingCSUID']==a['BuildingCSUID'];assert b['structureType']==a['BuildingBlockType'];assert b['baseHeightHKPD']==a['BaseHeight'];assert b['topHeightHKPD']==a['TopHeight']
   if b['heightSource']=='landsd':assert b['base']==a['BaseHeight'] and abs(b['height']-(a['TopHeight']-a['BaseHeight']))<.00001
 assert checked==set(records)==set(read_json(HERE/'query-object-ids.json')['objectIds']);assert counts['components']==manifest['counts']['components']
 result={'result':'passed','tiles':len(manifest['tiles']),'sourceIDs':len(checked),'components':counts['components'],'largestTileBytes':largest,'checks':['every tile size/hash/count matches manifest','every component is finite, closed and topologically valid','all footprint coordinates stay within whole-component tile bounds','unique source/component IDs and exactly all advertised source IDs','source CSUID/type/base/top fields identical to retained GeoJSON','recorded render elevations unchanged','sourceAttributes omitted from compact staging records'],'counts':dict(counts)}
 save_json(DOCS/'staging-independent-verification.json',result);print(json.dumps(result,indent=2))

if __name__=='__main__':main()
