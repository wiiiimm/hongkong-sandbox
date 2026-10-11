"""Read-only diagnostic of retained Mui Wo OSM sources and committed building tiles."""
import collections,gzip,hashlib,json,pathlib,sys
HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'source-scripts/city'))
from build_city import geometry,xy,number,polys
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union

BBOX=[113.97922444961371,22.249711576500182,114.0180525556901,22.28564402349982]  # Exact user envelope: west,south,east,north

def bbox_intersects(bounds):
 if not bounds:return False
 return bounds['maxlon']>=BBOX[0] and bounds['minlon']<=BBOX[2] and bounds['maxlat']>=BBOX[1] and bounds['minlat']<=BBOX[3]

def main():
 out=ROOT/'3d-viewer/city/data';manifest=json.loads((out/'manifest.json').read_text())
 w,s,e,n=BBOX;roi=Polygon([xy(w,s),xy(e,s),xy(e,n),xy(w,n)])
 sources=[];records={}
 for source in sorted(manifest['sources'],key=lambda s:s['snapshot']):
  south,west,north,east=source['bbox']
  if not (east>=w and west<=e and north>=s and south<=n):continue
  raw=gzip.decompress((ROOT/source['file']).read_bytes());data=json.loads(raw)
  kept=[]
  for feature in data['elements']:
   if bbox_intersects(feature.get('bounds')):records[f'{feature["type"]}/{feature["id"]}']=feature;kept.append(feature)
  sources.append({**source,'roiElements':len(kept),'sha256Matches':hashlib.sha256(raw).hexdigest()==source['sha256']})
 buildings=[];tiles=[];tile_sources=collections.defaultdict(list)
 for tile in manifest['tiles']:
  x0,z0,x1,z1=tile['bounds'];bounds=Polygon([(x0,z0),(x1,z0),(x1,z1),(x0,z1)])
  if not roi.intersects(bounds):continue
  data=json.loads((ROOT/'3d-viewer'/tile['url']).read_text());intersecting=[]
  for building in data['buildings']:
   geom=Polygon(building['rings'][0],building['rings'][1:])
   if roi.intersects(geom):buildings.append(building);tile_sources[building['id']].append(building);intersecting.append(building['uid'])
  tiles.append({'id':tile['id'],'url':tile['url'],'allForms':len(data['buildings']),'formsIntersectingStudy':len(intersecting),'uids':intersecting})
 source_forms=[];not_emitted=[];landuse=[];named=[]
 for oid,feature in sorted(records.items()):
  tags=feature.get('tags',{});geom=geometry(feature)
  if geom is None or geom.is_empty or not roi.intersects(geom):continue
  if tags.get('landuse')=='residential':landuse.append({'source':oid,'name':tags.get('name:en',tags.get('name','')),'area':round(geom.intersection(roi).area,1),'bounds':list(geom.bounds),'rings':[[list(p) for p in geom.exterior.coords]] if geom.geom_type=='Polygon' else None})
  if not (tags.get('building') or tags.get('building:part')):continue
  count=len(polys(geom));name=tags.get('name:en',tags.get('name',''))
  entry={'id':oid,'name':name,'kind':tags.get('building'),'part':tags.get('building:part'),'components':count,'area':round(geom.area,2),'bounds':list(geom.bounds),'tags':tags,'generatedUIDs':[b['uid'] for b in tile_sources[oid]]}
  source_forms.append(entry)
  if name:named.append({'id':oid,'name':name,'lat':(feature['bounds']['minlat']+feature['bounds']['maxlat'])/2,'lon':(feature['bounds']['minlon']+feature['bounds']['maxlon'])/2})
  if not tile_sources[oid]:
   reason='needs-inspection'
   if tags.get('building') in ('roof','no','construction'):reason='intentionally omitted building='+tags['building']
   elif tags.get('building:part')=='no':reason='intentionally omitted building:part=no'
   elif tags.get('location')=='underground' or tags.get('parking')=='underground' or str(tags.get('layer','')).startswith('-'):reason='intentionally omitted underground/negative layer'
   elif all(p.area<8 for p in polys(geom)):reason='below8m2minimum'
   elif any(b.get('parent')==oid for b in buildings):reason='outline replaced by mapped building parts'
   else:
    height=number(tags.get('height'));levels=number(tags.get('building:levels',tags.get('building:part:levels')));minimum=number(tags.get('min_height')) or (number(tags.get('building:min_level')) or 0)*3.2
    if (height and not 0<height<600) or (height and minimum>=height) or (levels and minimum>=levels*3.2):reason='invalid height/minimum interval'
   not_emitted.append({**entry,'reason':reason})
 report={'bboxWGS84':BBOX,'selection':'Footprints intersecting the projected user-supplied Mui Wo study rectangle, not an official village boundary.','manifestSha256':hashlib.sha256((out/'manifest.json').read_bytes()).hexdigest(),'manifestForms':manifest['counts']['buildings'],'sources':sources,'counts':{'retainedSourceBuildingObjects':len(source_forms),'generatedBuildingForms':len(buildings),'generatedSourceIds':sum(bool(forms) for forms in tile_sources.values()),'sourceObjectsNotEmitted':len(not_emitted),'omissionReasons':dict(collections.Counter(e['reason'] for e in not_emitted)),'generatedKinds':dict(collections.Counter(b['kind'] for b in buildings)),'generatedHeightSources':dict(collections.Counter(b['heightSource'] for b in buildings))},'tiles':tiles,'sourceObjectsNotEmitted':not_emitted,'residentialAreas':landuse,'namedBuildingAnchors':named,'generatedBuildings':buildings}
 (HERE/'current-building-diagnostic.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(report['counts'],indent=2));print('Tiles',[(t['id'],t['formsIntersectingStudy']) for t in tiles]);print('Residential areas',[(p['name'],p['area']) for p in landuse]);print('Unexplained omissions',[(b['id'],b['name']) for b in not_emitted if b['reason']=='needs-inspection'])
if __name__=='__main__':main()
