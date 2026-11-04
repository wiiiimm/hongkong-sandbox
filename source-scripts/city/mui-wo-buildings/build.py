"""Stage full official Mui Wo building fallback; never mutate city tiles.
Run with /tmp/astra-city-venv/bin/python source-scripts/city/mui-wo-buildings/build.py
Source geometry is not simplified, clipped or raised to the current terrain mesh.
"""
from __future__ import annotations
import collections,gzip,hashlib,json,math,pathlib,sys
from shapely import make_valid
from shapely.geometry import Polygon,Point,box
from shapely.ops import unary_union
from shapely.strtree import STRtree
HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'source-scripts/city'))
from build_city import xy,ORIGIN,polys
OUT=ROOT/'3d-viewer/city/data/mui-wo-buildings.json'
DOC=ROOT/'docs/astra-city/mui-wo-buildings'
SPEC='https://static.csdi.gov.hk/csdi-webpage/view/common/6eda6a766520bcffe13206378c060a59bdb54a3c6f92480b1f01174d25fd7194'
SOURCE='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer/0'
DEFAULT_HEIGHTS={'Tower':9.6,'Podium':4.5,'Temporary Structure':3.5,'Open-sided Structure':3.0}

def dump(path,obj,pretty=False):
 raw=json.dumps(obj,ensure_ascii=False,indent=2 if pretty else None,separators=None if pretty else (',',':')).encode()
 path.write_bytes(gzip.compress(raw,mtime=0) if str(path).endswith('.gz') else raw+b'\n')
def read(path):return json.loads(gzip.decompress(path.read_bytes()) if str(path).endswith('.gz') else path.read_bytes())
def fingerprint(path):return dict(file=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest())
def pack(p):
 # Projection can create narrow valid details that millimetre formatting closes.
 # Never discard or alter source topology merely to reduce numeric precision.
 for decimals in [3,6,None]:
  rings=[[[round(x,decimals) if decimals is not None else x,round(z,decimals) if decimals is not None else z] for x,z in ring.coords] for ring in [p.exterior,*p.interiors]]
  candidate=Polygon(rings[0],rings[1:])
  if candidate.is_valid and not candidate.is_empty and candidate.area>0:return rings
 raise ValueError('Cannot serialise invalid source polygon without changing topology')

def official_geometry(feature):
 """ESRI rings with arbitrary winding: containment parity preserves nested holes."""
 rings=[Polygon([(e-ORIGIN[0],ORIGIN[1]-n) for e,n,*_ in ring]) for ring in feature['geometry']['rings'] if len(ring)>=4]
 rings=sorted(rings,key=lambda p:p.area,reverse=True)
 parents=[];depth=[]
 for i,p in enumerate(rings):
  candidates=[j for j in range(i) if rings[j].covers(p.representative_point())]
  parent=min(candidates,key=lambda j:rings[j].area) if candidates else None
  parents.append(parent);depth.append(0 if parent is None else depth[parent]+1)
 blocks=[Polygon(p.exterior.coords,[rings[j].exterior.coords for j in range(i+1,len(rings)) if parents[j]==i]) for i,p in enumerate(rings) if depth[i]%2==0]
 repaired=any(not p.is_valid for p in blocks)
 geometry=unary_union([make_valid(p) for p in blocks])
 if geometry.geom_type=='GeometryCollection':geometry=unary_union([p for g in geometry.geoms for p in polys(g)])
 return geometry,repaired

class Terrain:
 """Exact extrema of the existing piecewise-linear 70 m terrain over each footprint."""
 def __init__(self,bounds):
  self.path=ROOT/'3d-viewer/city/data/terrain.json';self.dem=read(self.path);self.g=self.dem['meta']['georef'];self.w=self.dem['w'];g=self.g
  x0,z0,x1,z1=bounds
  c0,c1=sorted([(x0+ORIGIN[0]-g['bE'])/g['aE'],(x1+ORIGIN[0]-g['bE'])/g['aE']]);r0,r1=sorted([(ORIGIN[1]-z0-g['bN'])/g['aN'],(ORIGIN[1]-z1-g['bN'])/g['aN']])
  self.triangles=[]
  for r in range(max(0,math.floor(r0)-1),min(self.dem['h']-1,math.ceil(r1)+1)):
   for c in range(max(0,math.floor(c0)-1),min(self.w-1,math.ceil(c1)+1)):
    p=[(g['aE']*cc+g['bE']-ORIGIN[0],ORIGIN[1]-(g['aN']*rr+g['bN'])) for cc,rr in [(c,r),(c+1,r),(c,r+1),(c+1,r+1)]]
    self.triangles.extend([Polygon([p[0],p[1],p[2]]),Polygon([p[1],p[3],p[2]])])
  self.tree=STRtree(self.triangles)
 def ground(self,x,z):
  g=self.g;c=(x+ORIGIN[0]-g['bE'])/g['aE'];r=(ORIGIN[1]-z-g['bN'])/g['aN'];i=min(self.w-2,max(0,int(c)));j=min(self.dem['h']-2,max(0,int(r)));u=c-i;v=r-j
  a,b,d,e=[self.dem['elev'][idx] for idx in (j*self.w+i,j*self.w+i+1,(j+1)*self.w+i,(j+1)*self.w+i+1)]
  return a+(b-a)*u+(d-a)*v if u+v<=1 else e+(d-e)*(1-u)+(b-e)*(1-v)
 def extrema(self,p):
  values=[]
  for i in self.tree.query(p):
   for clipped in polys(self.triangles[i].intersection(p)):
    values.extend(self.ground(x,z) for ring in [clipped.exterior,*clipped.interiors] for x,z in ring.coords)
  if not values:raise ValueError('Footprint does not intersect terrain')
  return dict(min=round(min(values),3),max=round(max(values),3),centre=round(self.ground(p.centroid.x,p.centroid.y),3),method='Extrema at footprint/terrain-triangle intersection vertices; existing 70 m mesh')

def render_elevations(attributes,terrain):
 """Keep source fields immutable; explicitly estimate only unavailable/invalid rendering values."""
 base,top=attributes.get('BaseHeight'),attributes.get('TopHeight');levels=attributes.get('Storeys');kind=attributes['BuildingBlockType']
 finite=lambda n:isinstance(n,(int,float)) and math.isfinite(n)
 estimated_height=round(levels*3.2,3) if finite(levels) and 0<levels<180 else DEFAULT_HEIGHTS.get(kind,9.6)
 estimate_basis='Recorded Storeys × 3.2 m assumed floor height' if finite(levels) and 0<levels<180 else f'Visual fallback for {kind}: {estimated_height} m; no surveyed height or occupancy inferred'
 if finite(base) and finite(top) and top>base:
  return dict(base=base,height=round(top-base,6),heightSource='landsd',baseSource='landsd',heightRule='Recorded TopHeight − BaseHeight; both approximate elevations above HKPD',renderTopHeight=top)
 if finite(base):
  return dict(base=base,height=estimated_height,heightSource='estimated',baseSource='landsd',heightRule=estimate_basis+('; recorded TopHeight is non-increasing and is retained separately' if finite(top) else '; TopHeight absent'),renderTopHeight=round(base+estimated_height,6))
 if finite(top):
  return dict(base=round(top-estimated_height,6),height=estimated_height,heightSource='estimated',baseSource='estimated-from-top',heightRule=estimate_basis+'; base inferred below recorded TopHeight',renderTopHeight=top)
 base=terrain['min']
 return dict(base=base,height=estimated_height,heightSource='estimated',baseSource='terrain-estimated',heightRule=estimate_basis+'; both source elevations absent, base from current terrain minimum',renderTopHeight=round(base+estimated_height,6))

def build_record(a,p,index,terrain_extrema,geometry_repaired=False,tile_size=2000):
 """Reusable single-component converter. Terrain extrema must be supplied explicitly."""
 t=dict(terrain_extrema);heights=render_elevations(a,t);top=heights['renderTopHeight'];base=heights['base']
 t.update(baseMinusMin=round(base-t['min'],3),baseMinusMax=round(base-t['max'],3),roofMinusMin=round(top-t['min'],3),roofMinusMax=round(top-t['max'],3),roofWhollyBelowTerrain=top<t['min']-.1,roofPartlyBelowTerrain=top<t['max']-.1,baseWhollyAboveTerrain=base>t['max']+.5)
 oid=f'landsd/{a["OBJECTID"]}';source_url=SOURCE+'/query?f=pjson&objectIds='+str(a['OBJECTID'])+'&outFields=*&returnGeometry=true&outSR=2326'
 return dict(id=oid,uid=f'{oid}:{index}',tile=f'{math.floor(p.centroid.x/tile_size)}_{math.floor(p.centroid.y/tile_size)}',name=a.get('BuildingNameEN') or '',zh=a.get('BuildingNameTC') or '',kind={'Temporary Structure':'shed','Open-sided Structure':'roof'}.get(a['BuildingBlockType'],'yes'),**heights,levels=a.get('Storeys'),minimum=0,part=a['BuildingBlockType']=='Podium',material='',rings=pack(p),centre=[round(p.centroid.x,3),round(p.centroid.y,3)],source='Lands Department, Hong Kong SAR Government',sourceUrl=source_url,objectId=a['OBJECTID'],buildingCSUID=a['BuildingCSUID'],buildingId=a.get('BuildingID'),structureType=a['BuildingBlockType'],baseHeightHKPD=a.get('BaseHeight'),topHeightHKPD=a.get('TopHeight'),sourceAttributes=dict(a),terrain=t,geometryRepaired=geometry_repaired,sourceArea=round(p.area,3))

def stage_feature(feature,terrain_sampler,tile_size=2000):
 """Yield source-complete component records, suitable for territory batch/tile streaming.
 terrain_sampler(polygon) -> {min,max,centre,method}; never guesses a datum.
 This function performs no I/O and retains no global feature collection.
 """
 geo,repaired=official_geometry(feature)
 for index,p in enumerate(polys(geo)):
  rings=pack(p);p=Polygon(rings[0],rings[1:])
  if p.is_empty or not p.is_valid or p.area<=0:raise ValueError('Invalid staged footprint '+str(feature['attributes']['OBJECTID']))
  yield build_record(feature['attributes'],p,index,terrain_sampler(p),repaired,tile_size)


def capture_baseline(bounds):
 path=HERE/'osm-baseline.json.gz'
 if path.exists():return read(path)
 entries=[];files=[];manifest=read(ROOT/'3d-viewer/city/data/manifest.json');study=box(*bounds).buffer(5)
 for tile in manifest['tiles']:
  if not box(*tile['bounds']).intersects(study):continue
  p=ROOT/'3d-viewer'/tile['url'];files.append(fingerprint(p))
  for b in read(p)['buildings']:
   if b['id'].startswith('landsd/'):continue
   geo=Polygon(b['rings'][0],b['rings'][1:])
   if geo.intersects(study):entries.append(b)
 data=dict(note='Frozen current rendered OSM forms intersecting the user envelope plus 5 m; source-layer comparison before official integration',tiles=files,buildings=entries)
 dump(path,data);return data

def main():
 data=read(HERE/'landsd-mui-wo.json.gz');bbox=data['bboxWGS84'];corners=[xy(lon,lat) for lon,lat in [(bbox[0],bbox[1]),(bbox[2],bbox[1]),(bbox[2],bbox[3]),(bbox[0],bbox[3])]];study=Polygon(corners);terrain=Terrain(study.buffer(300).bounds)
 baseline=capture_baseline(study.bounds);osm=baseline['buildings'];osm_polys=[Polygon(b['rings'][0],b['rings'][1:]) for b in osm];osm_tree=STRtree(osm_polys)
 nodes=read(ROOT/'source-scripts/city/regional/nt/surfaces-osm.json.gz')['elements']
 villages=[e for e in nodes if e['type']=='node' and e.get('tags',{}).get('place') in ('hamlet','village','suburb','town') and bbox[0]<=e.get('lon',0)<=bbox[2] and bbox[1]<=e.get('lat',0)<=bbox[3]]
 village_points=[Point(xy(e['lon'],e['lat'])) for e in villages]
 buildings=[];rejected=[];counts=collections.Counter();cluster_counts=collections.defaultdict(collections.Counter)
 for feature in data['features']:
  a=feature['attributes'];geometry,repaired=official_geometry(feature);parts=polys(geometry)
  if not parts:rejected.append(dict(objectId=a['OBJECTID'],reason='No polygon geometry after validity repair'));continue
  for index,p in enumerate(parts):
   rings=pack(p);p=Polygon(rings[0],rings[1:])
   if p.is_empty or not p.is_valid or p.area<=0:raise ValueError('Invalid staged footprint '+str(a['OBJECTID']))
   oid=f'landsd/{a["OBJECTID"]}';uid=f'{oid}:{index}';t=terrain.extrema(p);heights=render_elevations(a,t)
   overlaps=[]
   for i in osm_tree.query(p):
    intersection=p.intersection(osm_polys[i]).area
    if intersection>.01:
     overlap=intersection/p.area;other=intersection/osm_polys[i].area;iou=intersection/(p.area+osm_polys[i].area-intersection)
     overlaps.append(dict(uid=osm[i]['uid'],id=osm[i]['id'],area=round(intersection,3),officialFraction=round(overlap,5),osmFraction=round(other,5),iou=round(iou,5),substantial=overlap>=.1 or other>=.1 or intersection>=4,name=osm[i].get('name',''),zh=osm[i].get('zh','')))
   overlaps.sort(key=lambda match:match['area'],reverse=True)
   substantial=[m for m in overlaps if m['substantial']]
   # Any retained sliver is explicit; missing additions never silently clip source geometry.
   classification='overlaps-osm' if substantial else 'edge-overlap' if overlaps else 'missing'
   if village_points:
    nearest=min(range(len(village_points)),key=lambda i:p.centroid.distance(village_points[i]));v=villages[nearest];distance=p.centroid.distance(village_points[nearest]);locality=dict(name=v['tags'].get('name:en',v['tags'].get('name','')),zh=v['tags'].get('name:zh',''),source='https://www.openstreetmap.org/node/'+str(v['id']),distance=round(distance,1),method='Nearest mapped settlement point; not a village boundary')
   else:locality=None
   top=heights['renderTopHeight'];base=heights['base'];t.update(baseMinusMin=round(base-t['min'],3),baseMinusMax=round(base-t['max'],3),roofMinusMin=round(top-t['min'],3),roofMinusMax=round(top-t['max'],3),roofWhollyBelowTerrain=top<t['min']-.1,roofPartlyBelowTerrain=top<t['max']-.1,baseWhollyAboveTerrain=base>t['max']+.5)
   b=build_record(a,p,index,t,repaired)
   b.update(coverage=dict(classification=classification,osmMatches=overlaps),locality=locality)
   buildings.append(b);counts[classification]+=1;counts['height:'+b['heightSource']]+=1;counts['type:'+b['structureType']]+=1
   if locality:cluster_counts[locality['name']][classification]+=1;cluster_counts[locality['name']]['total']+=1
 counts.update(dict(sourceRecords=len(data['features']),polygonComponents=len(buildings),sourceIds=len({b['objectId'] for b in buildings}),rejectedSourceRecords=len(rejected),baselineOSMForms=len(osm),baselineOSMFormsWithinUserEnvelope=sum(p.intersects(study) for p in osm_polys),unnamed=sum(not b['name'] and not b['zh'] for b in buildings),roofWhollyBelowTerrain=sum(b['terrain']['roofWhollyBelowTerrain'] for b in buildings),roofPartlyBelowTerrain=sum(b['terrain']['roofPartlyBelowTerrain'] for b in buildings),baseWhollyAboveTerrain=sum(b['terrain']['baseWhollyAboveTerrain'] for b in buildings)))
 source=dict(provider='Lands Department',attribution='Lands Department, Hong Kong SAR Government; Common Spatial Data Infrastructure (CSDI) Portal. Government intellectual property acknowledged; data available under CSDI terms of use.',datasetId=data['datasetId'],datasetVersion=data['datasetVersion'],sourceUrl=SOURCE,metadataUrl='https://portal.csdi.gov.hk/csdi-webpage/metadata/landsd_rcd_1637211194312_35158/html',specificationUrl=SPEC,retrievedAt=data['retrievedAt'],bboxWGS84=bbox,licenceUrl='https://portal.csdi.gov.hk/csdi-webpage/doc/TNC',**fingerprint(HERE/'landsd-mui-wo.json.gz'))
 output=dict(schemaVersion=1,title='Mui Wo official building fallback',issue='HKS-164',origin=ORIGIN,crs='EPSG:2326',verticalDatum='HKPD',bboxWGS84=bbox,source=source,supplementalSources=[source],queryVerification=dict(returnCountOnly=read(HERE/'query-count.json')['count'],completeObjectIds=len(read(HERE/'query-object-ids.json')['objectIds']),uniqueReturnedObjectIds=len({f['attributes']['OBJECTID'] for f in data['features']}),allAdvertisedIdsReturned=sorted(read(HERE/'query-object-ids.json')['objectIds'])==sorted(f['attributes']['OBJECTID'] for f in data['features'])),coveragePolicy='Full intersecting official source polygons; no clipping to the user envelope and no source-geometry simplification. OSM overlap classification is advisory for official-primary integration.',heightPolicy='Recorded approximate BaseHeight and TopHeight remain absolute HKPD. Missing/invalid render values are explicitly estimated; sourceAttributes and baseHeightHKPD/topHeightHKPD retain originals. No automatic terrain lifting.',structurePolicy='All official types, unnamed forms and null heights retained. Open-sided Structure must remain distinguishable from enclosed buildings; geometry alone does not supply detailed posts or roofs.',overlapPolicy='Intersection > 0.01 square metres retained. Substantial if >= 10% of either footprint or >= 4 square metres; smaller intersections labelled edge-overlap, never discarded silently.',terrainPolicy='Actual extrema of current 70 m mesh over footprint, not a new surveyed elevation. Root integration chooses any visual terrain reconciliation explicitly.',counts=dict(counts),buildings=buildings,missingBuildingUids=[b['uid'] for b in buildings if b['coverage']['classification']=='missing'],rejected=rejected)
 dump(OUT,output)
 audit=dict(counts=dict(counts),queryCount=read(HERE/'query-count.json')['count'],queryIds=len(read(HERE/'query-object-ids.json')['objectIds']),clusters={k:dict(v) for k,v in sorted(cluster_counts.items())},sourceFiles=[fingerprint(HERE/name) for name in ['landsd-mui-wo.json.gz','query-object-ids.json','query-count.json','requests.json','simplified-data-specification.html','osm-baseline.json.gz']],terrain=fingerprint(terrain.path),baselineTiles=baseline['tiles'],terrainConflicts=[dict(uid=b['uid'],structureType=b['structureType'],name=b['name'],locality=b['locality'],base=b['base'],top=b['renderTopHeight'],heightSource=b['heightSource'],terrain=b['terrain']) for b in buildings if b['terrain']['roofPartlyBelowTerrain']])
 dump(DOC/'audit.json',audit,True);print(json.dumps(audit['counts'],indent=2))
if __name__=='__main__':main()
