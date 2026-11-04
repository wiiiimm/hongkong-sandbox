"""Rebuild NT section places and mapped surfaces using retained OSM snapshots.
/tmp/astra-city-venv/bin/python source-scripts/city/regional/nt/build.py
No network requests, invented surface footprints or inferred building heights.
"""
from __future__ import annotations
import collections,gzip,hashlib,json,math,pathlib,sys
HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'source-scripts/city'))
from build_city import xy,coords,geometry,packed,polys,ORIGIN
from pyproj import Transformer
from shapely.geometry import Point,Polygon,LineString
from shapely.strtree import STRtree
OUT=ROOT/'3d-viewer/city/data'
DOC=ROOT/'docs/astra-city/regional/nt'
INVERSE=Transformer.from_crs(2326,4326,always_xy=True)
DISTRICTS={'11':('ntwest','tw'),'12':('ntwest','ki'),'13':('nteast','st'),'14':('nteast','tp'),'15':('nteast','sk'),'16':('ntwest','tm'),'17':('ntwest','yl'),'18':('ntnorth','no')}
RESTRICTED={'private','no','permit','customers','military','restricted'}

def configuration():
 entries=[]
 for row in (HERE/'places.tsv').read_text().splitlines():
  if not row or row.startswith('#'):continue
  section,id,oid,title,zh,description,note=row.split('|')
  entries.append(dict(sectionId=section,id='nt-'+id,feature=oid,title=title,zh=zh,description=description,accessNote=note))
 return entries

def read_sources():
 records={};provenance=[];origins={}
 for path in sorted((ROOT/'source-scripts/city/snapshots').glob('*.json.gz'))+[HERE/'surfaces-osm.json.gz']:
  if path.name.startswith('activity-'):continue
  raw=path.read_bytes();obj=json.loads(gzip.decompress(raw));url=str(path.relative_to(ROOT))
  provenance.append(dict(file=url,sha256=hashlib.sha256(raw).hexdigest(),timestamp=obj.get('osm3s',{}).get('timestamp_osm_base'),elements=len(obj['elements'])))
  for e in obj['elements']:
   oid=f'{e["type"]}/{e["id"]}';records[oid]=e;origins[oid]=url
 return records,origins,provenance

def centre_of(e):
 if e['type']=='node':return Point(xy(e['lon'],e['lat']))
 p=geometry(e)
 if p is not None and not p.is_empty:return p.representative_point()
 if e.get('geometry'):return LineString(coords(e['geometry'])).interpolate(.5,normalized=True)
 raise ValueError('No usable source geometry: '+str(e['id']))

class Arrivals:
 """Same triangle interpolation and conservative public-path checks as build_places.py."""
 def __init__(self,records):
  self.dem=json.loads((OUT/'terrain.json').read_text());self.g=self.dem['meta']['georef'];self.w=self.dem['w']
  self.blocks=[];self.heights=[]
  manifest=json.loads((OUT/'manifest.json').read_text());self.tile_hashes={}
  for tile in manifest['tiles']:
   path=ROOT/'3d-viewer'/tile['url'];raw=path.read_bytes();self.tile_hashes[tile['url']]=hashlib.sha256(raw).hexdigest()
   for b in json.loads(raw)['buildings']:
    p=Polygon(b['rings'][0],b['rings'][1:]).buffer(0)
    if not p.is_empty:self.blocks.append(p);self.heights.append((b['base']+b['minimum'],b['base']+b['height']))
  self.blocktree=STRtree(self.blocks);self.paths=[];self.pathids=[]
  for oid,e in records.items():
   t=e.get('tags',{})
   if t.get('highway') not in ('footway','pedestrian','path','living_street') or t.get('access') in RESTRICTED or t.get('foot') in RESTRICTED or t.get('area')=='yes' or t.get('location')=='underground' or t.get('tunnel') in ('yes','building_passage') or t.get('bridge')=='yes' or str(t.get('layer','0'))!='0' or t.get('indoor')=='yes':continue
   if e.get('geometry') and len(e['geometry'])>1:self.paths.append(LineString(coords(e['geometry'])));self.pathids.append(oid)
  self.pathtree=STRtree(self.paths)
 def cell(self,x,z):
  g=self.g;c=(x+ORIGIN[0]-g['bE'])/g['aE'];r=(ORIGIN[1]-z-g['bN'])/g['aN']
  if not (0<=c<self.w-1 and 0<=r<self.dem['h']-1):return None
  return int(c),int(r),c-int(c),r-int(r)
 def ground(self,x,z):
  cell=self.cell(x,z)
  if cell is None:return -1000
  i,j,u,v=cell;w=self.w;a,b,d,e=[self.dem['elev'][idx] for idx in (j*w+i,j*w+i+1,(j+1)*w+i,(j+1)*w+i+1)]
  return a+(b-a)*u+(d-a)*v if u+v<=1 else e+(d-e)*(1-u)+(b-e)*(1-v)
 def dry(self,x,z):
  cell=self.cell(x,z)
  if cell is None:return False
  i,j,u,v=cell;w=self.w;indices=(j*w+i,j*w+i+1,(j+1)*w+i) if u+v<=1 else (j*w+i+1,(j+1)*w+i,(j+1)*w+i+1)
  return all(self.dem['elev'][idx]>0 for idx in indices)
 def valid(self,p):
  y=self.ground(p.x,p.y)
  if y<=.8 or not self.dry(p.x,p.y):return False
  disc=p.buffer(1.2)
  for i in self.blocktree.query(disc):
   lo,hi=self.heights[i]
   if y+1.8>lo and y<hi and self.blocks[i].intersects(disc):return False
  return all(self.dry(p.x+dx,p.y+dz) and abs(self.ground(p.x+dx,p.y+dz)-y)<1.5 for dx,dz in [(2,0),(-2,0),(0,2),(0,-2)])
 def find(self,centre):
  candidates=[]
  for i in self.pathtree.query(centre.buffer(1000)):
   path=self.paths[i];near=path.project(centre)
   for shift in [0,-5,5,-15,15,-40,40,-90,90,-180,180]:
    # Validate the rounded coordinates that will actually be used by the viewer.
    point=path.interpolate(max(0,min(path.length,near+shift)));point=Point(round(point.x,1),round(point.y,1))
    if point.distance(centre)<=1000 and self.valid(point):candidates.append((point.distance(centre),self.pathids[i],point))
  return min(candidates,key=lambda c:(c[0],c[1])) if candidates else None

def main():
 entries=configuration();records,origins,provenance=read_sources();arrivals=Arrivals(records);boundary=geometry(records['relation/913110'])
 places=[];audit=[];centres=[]
 for entry in entries:
  oid=entry['feature'];source=records[oid];centre=centre_of(source);centres.append(centre)
  assert boundary.covers(centre), 'Destination outside retained Hong Kong boundary: '+entry['id']
  lon,lat=INVERSE.transform(centre.x+ORIGIN[0],ORIGIN[1]-centre.y)
  region,district=DISTRICTS[entry['sectionId'].split('.')[0]]
  place={k:entry[k] for k in ('id','title','zh','sectionId','description')}
  place.update(region=region,lat=round(lat,7),lon=round(lon,7),source='https://www.openstreetmap.org/'+oid,offset=[1100,850,1400],target=[round(centre.x,1),round(max(80,arrivals.ground(centre.x,centre.y)+45),1),round(centre.y,1)])
  result=None if entry['accessNote'] else arrivals.find(centre)
  record=dict(id=entry['id'],sectionId=entry['sectionId'],source=oid,sourceFile=origins[oid],sourceTags=source.get('tags',{}),featureWorld=[round(centre.x,1),round(centre.y,1)])
  if result:
   distance,path,point=result;place.update(spawn=[point.x,point.y],arrivalSource='https://www.openstreetmap.org/'+path,terrainY=round(arrivals.ground(point.x,point.y),2),arrivalVerified=True)
   record.update(arrivalSource=path,arrivalWorld=place['spawn'],offsetMetres=round(distance,1),terrainY=place['terrainY'],checks=dict(dryTerrainTriangle=True,buildingClearanceMetres=1.2,terrainNeighbourhoodStepMetres=2,maxNeighbourRiseMetres=1.5,publicPathTags=records[path]['tags']))
  else:
   reason=entry['accessNote'] or 'Aerial overview only; the current terrain/building data has no verified dry public-path arrival within 1 km.'
   place.update(aerialOnly=True,description=place['description']+' '+reason);record.update(aerialOnly=True,reason=reason)
  places.append(place);audit.append(record)
  print(entry['sectionId'],entry['id'],'aerial' if place.get('aerialOnly') else str(record['offsetMetres'])+' m to path',flush=True)
 surfaces=[];rejections=collections.Counter();seen=set()
 # Select real, closed source polygons near these curated section destinations.
 # Nearest destination gives a browsing association, never an administrative boundary.
 for oid,e in sorted(records.items()):
  t=e.get('tags',{});kind='beach' if t.get('natural')=='beach' else 'pier' if t.get('man_made')=='pier' else 'pitch' if t.get('leisure')=='pitch' else 'plaza' if t.get('highway')=='pedestrian' and t.get('area')=='yes' else None
  if not kind:continue
  if t.get('access') in RESTRICTED or t.get('foot') in RESTRICTED or t.get('location')=='underground' or t.get('indoor')=='yes' or str(t.get('layer','0'))!='0':rejections['restrictedOrElevated']+=1;continue
  p=geometry(e)
  if p is None or p.is_empty:rejections['noClosedPolygon']+=1;continue
  p=p.intersection(boundary).buffer(0)
  if p.is_empty:rejections['outsideHongKongBoundary']+=1;continue
  centre=p.representative_point();nearest=min(range(len(centres)),key=lambda i:centres[i].distance(centre));distance=centres[nearest].distance(centre)
  if distance>750:continue
  # Keep this workstream north of the urban Kowloon edge, except Tsing Yi/Ma Wan
  # and the separately assigned Sai Kung peninsula/islands.
  lon,lat=INVERSE.transform(centre.x+ORIGIN[0],ORIGIN[1]-centre.y)
  if lat<22.345 and not (lon<114.112 or lon>114.25):continue
  for number,polygon in enumerate(polys(p)):
   if not 12<polygon.area<180000:rejections['areaOutsideRange']+=1;continue
   # Rooftop/covered courts cannot be placed at terrain height without a deck elevation.
   if kind!='pier' and sum(arrivals.blocks[i].intersection(polygon).area for i in arrivals.blocktree.query(polygon))>polygon.area*.15:
    rejections['buildingOverlap']+=1;continue
   polygon=polygon.simplify(.45,preserve_topology=True);rings=packed(polygon)
   if not Polygon(rings[0],rings[1:]).is_valid:rejections['roundingInvalid']+=1;continue
   if sum(len(r) for r in rings)>600:rejections['tooManyVertices']+=1;continue
   # A repeated relation/way geometry should only create one visible surface.
   key=(kind,round(polygon.centroid.x),round(polygon.centroid.y),round(polygon.area))
   if key in seen:continue
   seen.add(key);surface=dict(id='nt-'+oid.replace('/','-')+'-'+str(number),kind=kind,rings=rings,source='https://www.openstreetmap.org/'+oid,sectionId=entries[nearest]['sectionId'],area=round(polygon.area,1))
   if t.get('name'):surface['name']=t.get('name:en',t['name'])
   surface['tags']={k:t[k] for k in ('sport','surface','access','foot','name:zh','natural','leisure','man_made','highway','area') if k in t}
   surfaces.append(surface)
 sections=[]
 for sid in sorted({e['sectionId'] for e in entries},key=lambda s:tuple(map(int,s.split('.')))):
  pp=[p for p in places if p['sectionId']==sid];ss=[s for s in surfaces if s['sectionId']==sid];walk=sum(bool(p.get('arrivalVerified')) for p in pp);code=DISTRICTS[sid.split('.')[0]][1]
  sources=sorted({p['source'] for p in pp}|{s['source'] for s in ss})+['https://www.gohk.gov.hk/en/districts/'+code+'.php']
  note=f'{len(pp)} sourced exploration point(s), {walk} terrain/building-checked mapped public-path arrival(s), {len(ss)} mapped surface polygon(s). Landmark modelling and full section review remain open.'
  if not walk:note+=' Aerial browsing only; no verified unrestricted walking arrival.'
  sections.append(dict(id=sid,status='regional-detail-pass' if walk else 'aerial-reference',note=note,sources=sources))
 output=dict(schemaVersion=1,regionGroup='nt',places=places,surfaces=surfaces,buildingOverrides=[],sections=sections)
 (OUT/'regional').mkdir(exist_ok=True);(OUT/'regional/nt.json').write_text(json.dumps(output,ensure_ascii=False,separators=(',',':'))+'\n')
 summary=dict(producer='Codex Astra NT subagent',schemaVersion=1,counts=dict(places=len(places),verifiedArrivals=sum(bool(p.get('arrivalVerified')) for p in places),aerialOnly=sum(bool(p.get('aerialOnly')) for p in places),sections=len(sections),districts=len({p['sectionId'].split('.')[0] for p in places}),surfaces=len(surfaces),surfaceKinds=dict(collections.Counter(s['kind'] for s in surfaces))),sources=provenance,arrivalChecks=audit,surfaceRejections=dict(rejections),boundarySource='https://www.openstreetmap.org/relation/913110',countsByRegion={region:dict(places=sum(p['region']==region for p in places),verifiedArrivals=sum(p['region']==region and bool(p.get('arrivalVerified')) for p in places),surfaces=sum(DISTRICTS[s['sectionId'].split('.')[0]][0]==region for s in surfaces)) for region in ['ntwest','nteast','ntnorth']},terrainSHA256=hashlib.sha256((OUT/'terrain.json').read_bytes()).hexdigest(),tileSHA256=arrivals.tile_hashes)
 DOC.mkdir(parents=True,exist_ok=True);(DOC/'verification.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(summary['counts']),flush=True)
 return output,summary
if __name__=='__main__':main()
