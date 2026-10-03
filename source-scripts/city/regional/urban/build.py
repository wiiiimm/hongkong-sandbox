#!/usr/bin/env python3
"""Build sourced urban visit arrivals and renderable public-space surfaces.
No network is used. Run fetch.py separately to refresh retained OSM sources.
"""
import collections,csv,gzip,hashlib,json,math,pathlib,sys
from shapely.geometry import Point,Polygon,LineString
from shapely.ops import unary_union
from shapely.strtree import STRtree
from pyproj import Transformer
HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE.parents[1]))
from build_city import xy,coords,geometry,packed,polys,ORIGIN
OUT=ROOT/'3d-viewer/city/data/regional/urban.json'
DOC=ROOT/'docs/astra-city/regional/urban'
INVERSE=Transformer.from_crs(2326,4326,always_xy=True)
DISTRICTS={'Central and Western District':'01','Wan Chai District':'02','Eastern District':'03','Southern District':'04','Yau Tsim Mong District':'05','Sham Shui Po District':'06','Kowloon City District':'07','Wong Tai Sin District':'08','Kwun Tong District':'09'}

def load_sources():
 records={};sources=[];record_dates={}
 files=[ROOT/'source-scripts/city/snapshots'/f'{n}.json.gz' for n in ['island-west','island-east','kowloon','nt-central']]
 files+=sorted((HERE/'snapshots').glob('*.json.gz'))
 for path in files:
  raw=path.read_bytes();data=json.loads(gzip.decompress(raw))
  sources.append({'file':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest(),'timestampOSM':data.get('osm3s',{}).get('timestamp_osm_base'),'elements':len(data['elements'])})
  for e in data['elements']:
   oid=f'{e["type"]}/{e["id"]}';stamp=data.get('osm3s',{}).get('timestamp_osm_base','')
   if stamp>=record_dates.get(oid,''):records[oid]=e;record_dates[oid]=stamp
 return records,sources

def shape(e):
 if e['type']=='node':return Point(xy(e['lon'],e['lat']))
 if e.get('geometry') and (len(e['geometry'])<4 or e['geometry'][0]!=e['geometry'][-1]):return LineString(coords(e['geometry']))
 return geometry(e)

class Arrivals:
 """Same triangle, clearance and local-slope rules as build_places.py."""
 def __init__(self,records):
  self.dem=json.loads((ROOT/'3d-viewer/city/data/terrain.json').read_text());self.g=self.dem['meta']['georef'];self.w=self.dem['w']
  self.blocks=[];self.heights=[];self.paths=[];self.pathids=[]
  manifest=json.loads((ROOT/'3d-viewer/city/data/manifest.json').read_text())
  for meta in manifest['tiles']:
   for b in json.loads((ROOT/'3d-viewer'/meta['url']).read_text())['buildings']:
    polygon=Polygon(b['rings'][0],b['rings'][1:]).buffer(0)
    if not polygon.is_empty:self.blocks.append(polygon);self.heights.append((b['base']+b['minimum'],b['base']+b['height']))
  self.blocktree=STRtree(self.blocks)
  for oid,e in records.items():
   t=e.get('tags',{})
   if t.get('highway') not in ('footway','pedestrian','path','living_street') or t.get('access') in ('private','no','customers','permit','destination') or t.get('foot') in ('private','no','customers','permit','destination') or t.get('area')=='yes' or t.get('location')=='underground' or t.get('tunnel') in ('yes','building_passage') or t.get('bridge')=='yes' or t.get('layer','0') not in ('0',0) or t.get('indoor')=='yes':continue
   if e.get('geometry') and len(e['geometry'])>1:self.paths.append(LineString(coords(e['geometry'])));self.pathids.append(oid)
  self.pathtree=STRtree(self.paths)
 def ground(self,x,z):
  c=(x+ORIGIN[0]-self.g['bE'])/self.g['aE'];r=(ORIGIN[1]-z-self.g['bN'])/self.g['aN']
  if not (0<=c<self.w-1 and 0<=r<self.dem['h']-1):return -1000
  i,j=int(c),int(r);u,v=c-i,r-j
  a,b,d,e=[self.dem['elev'][idx] for idx in (j*self.w+i,j*self.w+i+1,(j+1)*self.w+i,(j+1)*self.w+i+1)]
  return a+(b-a)*u+(d-a)*v if u+v<=1 else e+(d-e)*(1-u)+(b-e)*(1-v)
 def land_triangle(self,x,z):
  c=(x+ORIGIN[0]-self.g['bE'])/self.g['aE'];r=(ORIGIN[1]-z-self.g['bN'])/self.g['aN']
  if not (0<=c<self.w-1 and 0<=r<self.dem['h']-1):return False
  i,j=int(c),int(r);u,v=c-i,r-j
  indices=(j*self.w+i,j*self.w+i+1,(j+1)*self.w+i) if u+v<=1 else (j*self.w+i+1,(j+1)*self.w+i,(j+1)*self.w+i+1)
  return all(self.dem['elev'][idx]>0 for idx in indices)
 def valid(self,p):
  y=self.ground(p.x,p.y)
  if y<=.8 or not self.land_triangle(p.x,p.y):return False
  disc=p.buffer(1.2)
  for i in self.blocktree.query(disc):
   lo,hi=self.heights[i]
   if y+1.8>lo and y<hi and self.blocks[i].intersects(disc):return False
  return all(self.land_triangle(p.x+dx,p.y+dz) and abs(self.ground(p.x+dx,p.y+dz)-y)<1.5 for dx,dz in [(2,0),(-2,0),(0,2),(0,-2)])
 def near(self,centre):
  candidates=[]
  for i in self.pathtree.query(centre.buffer(1000)):
   path=self.paths[i];near=path.project(centre)
   for shift in [0,-5,5,-15,15,-40,40,-90,90,-180,180]:
    p=path.interpolate(max(0,min(path.length,near+shift)));p=Point(round(p.x,1),round(p.y,1));distance=p.distance(centre)
    if distance<=1000:candidates.append((distance,self.pathids[i],p))
  for distance,oid,p in sorted(candidates,key=lambda x:(x[0],x[1])):
   if self.valid(p):return distance,oid,p
  return None

def main():
 records,sources=load_sources();config=list(csv.DictReader((HERE/'places.tsv').open(),delimiter='\t'))
 assert len(config)==56 and len({r['sectionId'] for r in config})==56
 arrival=Arrivals(records);places=[];sections=[];evidence=[];gaps=[]
 for row in config:
  ref=row['ref'];source=None
  if ref.startswith('seed:'):
   lat,lon=map(float,ref.removeprefix('seed:').split(','));centre=Point(xy(lon,lat))
  else:
   if ref.startswith('name:'):
    name=ref.removeprefix('name:')
    matches=[(oid,e) for oid,e in records.items() if name in [e.get('tags',{}).get(k) for k in ['name:en','name','official_name:en']]]
    matches.sort(key=lambda pair:('geometry' not in pair[1] and 'members' not in pair[1],pair[0]))
    if not matches:gaps.append({'sectionId':row['sectionId'],'reason':'No retained named geometry for '+name});continue
    source,element=matches[0]
   else:source,element=ref,records[ref]
   geo=shape(element)
   if geo is None or geo.is_empty:gaps.append({'sectionId':row['sectionId'],'reason':'Empty source geometry '+source});continue
   centre=geo.centroid if geo.geom_type in ('Polygon','MultiPolygon') else geo.interpolate(.5,normalized=True) if geo.geom_type=='LineString' else geo
  found=arrival.near(centre)
  if source is None:
   if found is None:gaps.append({'sectionId':row['sectionId'],'reason':'No public path at search seed'});continue
   source=found[1];centre=found[2]
  lon,lat=INVERSE.transform(centre.x+ORIGIN[0],ORIGIN[1]-centre.y)
  place={'id':'section-'+row['sectionId'].replace('.','-'),'region':'island' if int(row['sectionId'][:2])<=4 else 'kowloon','title':row['title'],'zh':row['zh'],'sectionId':row['sectionId'],'lat':round(lat,7),'lon':round(lon,7),'description':row['description'],'source':'https://www.openstreetmap.org/'+source,'target':[round(centre.x,1),round(max(35,arrival.ground(centre.x,centre.y)+45),1),round(centre.y,1)],'offset':[1050,900,-1300]}
  note='One sourced visit point; detailed section modelling and route review remain open.'
  record={'sectionId':row['sectionId'],'source':source,'centreWorld':[round(centre.x,1),round(centre.y,1)]}
  if found:
   distance,oid,p=found;place.update(spawn=[p.x,p.y],arrivalSource='https://www.openstreetmap.org/'+oid,terrainY=round(arrival.ground(p.x,p.y),3),arrivalVerified=True)
   record.update(arrivalWorld=place['spawn'],arrivalSource=oid,centreOffsetMetres=round(p.distance(centre),2),terrainY=place['terrainY'],dryTriangle=True,buildingClearanceMetres=1.2,actorHeightMetres=1.8,localSlopeCheck=True)
  else:
   place.update(aerialOnly=True);note+=' No verified dry public-path arrival within 1 km; aerial-only.';record['aerialOnly']=True
  places.append(place);evidence.append(record);sections.append({'id':row['sectionId'],'status':'partial','note':note,'sources':[place['source']]+([place['arrivalSource']] if found else [])})
  print(row['sectionId'],source,'arrival',round(found[0]) if found else 'aerial only',flush=True)
 district_polys={};district_sources={}
 for oid,e in records.items():
  t=e.get('tags',{});name=t.get('name:en',t.get('name',''))
  if name in DISTRICTS and t.get('boundary')=='administrative':
   p=geometry(e)
   if p is not None and not p.is_empty:district_polys[DISTRICTS[name]]=p;district_sources[DISTRICTS[name]]='https://www.openstreetmap.org/'+oid
 if len(district_polys)!=9:raise RuntimeError('Need sourced boundary geometry for all nine districts: '+str(district_sources))
 surfaces=[];skips=collections.Counter();members={m['ref'] for e in records.values() if e.get('tags',{}).get('type')=='multipolygon' and (e.get('tags',{}).get('man_made')=='pier' or e.get('tags',{}).get('natural')=='beach' or e.get('tags',{}).get('leisure')=='pitch' or e.get('tags',{}).get('highway')=='pedestrian') for m in e.get('members',[]) if m.get('role','outer')=='outer'}
 for oid,e in records.items():
  t=e.get('tags',{});kind='pier' if t.get('man_made')=='pier' else 'beach' if t.get('natural')=='beach' else 'pitch' if t.get('leisure')=='pitch' else 'plaza' if t.get('highway')=='pedestrian' and t.get('area')=='yes' else None
  if not kind or e['type']=='node':continue
  if e['type']=='way' and e['id'] in members:skips['multipolygon_member']+=1;continue
  if t.get('location') in ('underground','roof') or t.get('tunnel') in ('yes','building_passage') or t.get('indoor')=='yes' or t.get('building') or t.get('building:part') or (kind!='pier' and (t.get('bridge')=='yes' or t.get('layer','0') not in ('0',0))):skips['building_or_non_ground']+=1;continue
  p=geometry(e)
  if p is None or p.is_empty or p.geom_type not in ('Polygon','MultiPolygon'):skips['no_closed_polygon']+=1;continue
  for index,original in enumerate(polys(p)):
   c=original.representative_point();district=next((d for d,poly in district_polys.items() if poly.covers(c)),None)
   if not district:skips['outside_urban_districts']+=1;continue
   if original.area<12 or original.area>200000:skips['area_bounds']+=1;continue
   polygon=original.simplify(.25,preserve_topology=True)
   if kind in ('plaza','pitch'):
    intersecting=[arrival.blocks[i].intersection(polygon) for i in arrival.blocktree.query(polygon) if arrival.blocks[i].intersects(polygon)]
    if intersecting and unary_union(intersecting).area/polygon.area>.1:skips['overlaps_building_over_10_percent']+=1;continue
   rings=packed(polygon)
   if not rings or any(len(r)<4 for r in rings) or sum(map(len,rings))>2000:skips['invalid_or_excess_vertices']+=1;continue
   options=[place for place in places if place['sectionId'].startswith(district+'.')]
   closest=min(options,key=lambda place:c.distance(Point(place['target'][0],place['target'][2])))
   surface={'id':'urban-'+oid.replace('/','-')+'-'+str(index),'kind':kind,'rings':rings,'source':'https://www.openstreetmap.org/'+oid,'name':t.get('name:en',t.get('name','')),'sectionId':closest['sectionId'],'area':round(polygon.area,1),'tags':{k:t[k] for k in ['sport','surface','access','operator','leisure','man_made','natural','highway','area'] if k in t}}
   surfaces.append(surface)
 surfaces.sort(key=lambda s:s['id'])
 for gap in gaps:sections.append({'id':gap['sectionId'],'status':'pending','note':gap['reason']+'; detailed section review remains open.','sources':[]})
 sections.sort(key=lambda s:tuple(map(int,s['id'].split('.'))))
 counts=collections.Counter(s['kind'] for s in surfaces);persection=collections.Counter(s['sectionId'] for s in surfaces)
 for section in sections:section['note']+=' '+str(persection[section['id']])+' source polygons associated by nearest visit point within the district; this is not a section boundary.'
 result={'schemaVersion':1,'regionGroup':'urban','places':places,'surfaces':surfaces,'buildingOverrides':[],'sections':sections}
 assert len({s['id'] for s in surfaces})==len(surfaces)
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n')
 audit={'source':'OpenStreetMap contributors','licence':'ODbL-1.0','crs':'EPSG:2326','origin':ORIGIN,'axes':'x=easting-834500; z=816500-northing','placeCount':len(places),'verifiedArrivals':sum(bool(p.get('arrivalVerified')) for p in places),'aerialOnly':sum(bool(p.get('aerialOnly')) for p in places),'sectionCount':len(sections),'surfaceCount':len(surfaces),'surfaceKinds':dict(counts),'surfaceVertices':sum(len(r) for s in surfaces for r in s['rings']),'maximumSurfaceVertices':max((sum(map(len,s['rings'])) for s in surfaces),default=0),'maximumSurfaceArea':max((s['area'] for s in surfaces),default=0),'surfaceSkips':dict(skips),'surfaceSectionAssignment':'Nearest visit point within OSM district boundary, not a survey or section border.','districtSources':district_sources,'sources':sources,'arrivals':evidence,'gaps':gaps,'byteCount':OUT.stat().st_size}
 DOC.mkdir(parents=True,exist_ok=True);(DOC/'verification.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:v for k,v in audit.items() if k not in ('sources','arrivals','districtSources')},indent=2),flush=True)
if __name__=='__main__':main()
