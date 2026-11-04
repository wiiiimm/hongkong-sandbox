#!/usr/bin/env python3
"""Reproducible OSM city import. pip install -r requirements.txt; python build_city.py --fetch.
Retains ODbL source snapshot, projects EPSG:4326 -> EPSG:2326, preserves courtyards,
excludes underground structures, and records height provenance per building.
"""
import argparse, collections, datetime, gzip, json, math, pathlib, re, urllib.parse, urllib.request
from pyproj import Transformer
from shapely.geometry import Polygon, MultiPolygon, LineString, Point, box
from shapely.ops import polygonize, unary_union
from shapely.strtree import STRtree
ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / '3d-viewer/city/data'
SOURCE = pathlib.Path(__file__).with_name('central-osm.json.gz')
BBOX = [22.268,114.125,22.311,114.192]
ORIGIN = [834500,816500]
PROJECT = Transformer.from_crs(4326,2326,always_xy=True)
QUERY = '[out:json][timeout:80];(' + ''.join(f'{s}({",".join(map(str,BBOX))});' for s in ['way["building"]','way["building:part"]','relation["building"]','way["highway"]','way["leisure"="park"]']) + ');out geom;'

def xy(lon,lat):
 e,n=PROJECT.transform(lon,lat);return (e-ORIGIN[0],ORIGIN[1]-n)
def coords(g):return [xy(p['lon'],p['lat']) for p in g]
def rounded(r):return [[round(x,1),round(y,1)] for x,y in r]
def polys(p):return [p] if p.geom_type=='Polygon' else list(p.geoms) if p.geom_type=='MultiPolygon' else []
def packed(p):return [rounded(p.exterior.coords)]+[rounded(r.coords) for r in p.interiors]
def number(value):
 if value is None:return None
 s=str(value).strip();m=re.fullmatch(r'(\d+(?:\.\d+)?)\s*(m|metres|ft|feet)?',s)
 if m:return float(m[1])*(.3048 if m[2] in ('ft','feet') else 1)
 m=re.fullmatch(r'''(\d+)'(?:(\d+(?:\.\d+)?)")?''',s)
 return float(m[1])*.3048+float(m[2] or 0)*.0254 if m else None

def geometry(el):
 if 'geometry' in el:
  c=coords(el['geometry'])
  if len(c)>3 and c[0]==c[-1]:return Polygon(c).buffer(0)
  return None
 lines={'outer':[],'inner':[]}
 for m in el.get('members',[]):
  if m.get('geometry') and m.get('role','outer') in lines:
   lines[m.get('role','outer')].append(LineString(coords(m['geometry'])))
 outer=unary_union(list(polygonize(unary_union(lines['outer']))))
 inner=unary_union(list(polygonize(unary_union(lines['inner']))))
 return outer.difference(inner).buffer(0)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--fetch',action='store_true');ap.add_argument('--input',type=pathlib.Path);args=ap.parse_args()
 if args.fetch:
  req=urllib.request.Request('https://overpass-api.de/api/interpreter',data=urllib.parse.urlencode({'data':QUERY}).encode(),headers={'User-Agent':'HongKongSandbox/1.0 (OSM city import)'})
  with urllib.request.urlopen(req,timeout=100) as response:raw=response.read()
  json.loads(raw)
  SOURCE.write_bytes(gzip.compress(raw,mtime=0))
 elif args.input:SOURCE.write_bytes(gzip.compress(args.input.read_bytes(),mtime=0))
 data=json.loads(gzip.decompress(SOURCE.read_bytes()))
 dem=json.loads((ROOT/'3d-viewer/data/hk-dtm5m.json').read_text());g=json.loads((ROOT/'3d-viewer/data/hk-georef.json').read_text())
 def elevation(x,z):
  c=(x+ORIGIN[0]-g['bE'])/g['aE'];r=(ORIGIN[1]-z-g['bN'])/g['aN']
  c=max(0,min(dem['w']-1.001,c));r=max(0,min(dem['h']-1.001,r));i=int(c);j=int(r);u=c-i;v=r-j
  a,b,d,e=[dem['elev'][n] for n in [j*dem['w']+i,j*dem['w']+i+1,(j+1)*dem['w']+i,(j+1)*dem['w']+i+1]]
  return a+(b-a)*u+(d-a)*v if u+v<=1 else e+(d-e)*(1-u)+(b-e)*(1-v)
 sw=xy(BBOX[1],BBOX[0]);ne=xy(BBOX[3],BBOX[2]);clip=box(sw[0],ne[1],ne[0],sw[1]);features=[];roads=[];parks=[]
 members={m['ref'] for el in data['elements'] if el['type']=='relation' and el.get('tags',{}).get('type')=='multipolygon' for m in el.get('members',[]) if m.get('role')=='outer'}
 for el in data['elements']:
  t=el.get('tags',{});oid=f'{el["type"]}/{el["id"]}';name=t.get('name:en',t.get('name',''))
  if t.get('highway') and el.get('geometry') and t.get('area')!='yes' and t.get('tunnel') not in ('yes','building_passage') and t.get('location')!='underground' and t['highway'] not in ('construction','proposed','elevator'):
   line=LineString(coords(el['geometry'])).intersection(clip)
   for l in ([line] if line.geom_type=='LineString' else list(line.geoms) if line.geom_type=='MultiLineString' else []):
    if l.length>2: roads.append({'id':oid,'kind':t['highway'],'name':name,'bridge':t.get('bridge')=='yes','layer':number(t.get('layer')) or 0,'path':rounded(l.simplify(.7).coords)})
  if not (t.get('building') or t.get('building:part') or t.get('leisure')=='park'):continue
  if t.get('building') in ('no','construction','roof') or t.get('location')=='underground' or t.get('parking')=='underground' or t.get('layer')=='-1':continue
  if el['type']=='relation' and t.get('type')!='multipolygon':continue
  if el['type']=='way' and el['id'] in members and not t.get('building:part'):continue
  geo=geometry(el)
  if geo is None or geo.is_empty:continue
  for p in polys(geo.intersection(clip).simplify(.25,preserve_topology=True)):
   if p.area<8:continue
   if t.get('leisure')=='park':parks.append({'name':name,'rings':packed(p)});continue
   height=number(t.get('height'));levels=number(t.get('building:levels',t.get('building:part:levels')));kind=t.get('building:use',t.get('building','yes'))
   method='tagged' if height else 'levels' if levels else 'estimated'
   height=height or (levels*3.2 if levels else 9 if p.area>8000 else 6 if kind in ('service','shed','garage','garages') else 24)
   minimum=number(t.get('min_height')) or (number(t.get('building:min_level')) or 0)*3.2
   if not 0<height<600 or minimum>=height:continue
   ground=min(elevation(x,z) for x,z in p.exterior.coords)
   features.append({'id':oid,'name':name,'zh':t.get('name:zh-Hant',t.get('name:zh','')),'kind':kind,'height':round(height,1),'heightSource':method,'levels':levels,'minimum':round(minimum,1),'base':round(max(1.2,ground),2),'part':bool(t.get('building:part')),'material':t.get('building:material',''),'rings':packed(p),'centre':rounded([(p.centroid.x,p.centroid.y)])[0]})
 # A building outline enclosing detailed parts is not an additional full-height block.
 parts=[Polygon(f['rings'][0],f['rings'][1:]) for f in features if f['part']]
 tree=STRtree(parts)
 filtered=[];replaced=0
 for f in features:
  p=Polygon(f['rings'][0],f['rings'][1:])
  if not f['part']:
   candidates=[parts[i] for i in tree.query(p) if p.covers(parts[i].representative_point())]
   if candidates and unary_union(candidates).intersection(p).area/p.area>.5:
    # Preserve identity when a named outline is replaced by unnamed 3D parts.
    for child in features:
     if child['part'] and p.covers(Point(child['centre'])):
      if not child['name']:child['name']=f['name']
      if not child['zh']:child['zh']=f['zh']
      child.setdefault('parent',f['id'])
    replaced+=1;continue
  filtered.append(f)
 features=filtered
 # Bundle a coarse full-territory terrain and B50K landcover, in the same CRS.
 lc=json.loads((ROOT/'3d-viewer/data/hk-b50k-landcover.json').read_text());tb=json.loads((ROOT/'3d-viewer/data/hk-texbb.json').read_text())['texbb']
 vegetation=[]
 for k in ('wood','veg'):
  for ring in lc[k]:
   if len(ring)<4:continue
   p=Polygon([(tb['E0']+u*(tb['E1']-tb['E0'])-ORIGIN[0],ORIGIN[1]-(tb['N1']-v*(tb['N1']-tb['N0']))) for u,v in ring]).buffer(0)
   if p.is_empty:continue
   for pp in polys(p):vegetation.append(pp)
 vtree=STRtree(vegetation)
 # Keep the existing 70 m grid for accurate co-registration and triangle sampling.
 vegetation_mask=[]
 for r in range(dem['h']):
  for c in range(dem['w']):
   if dem['elev'][r*dem['w']+c]<=1:vegetation_mask.append(0);continue
   p=Point(g['aE']*c+g['bE']-ORIGIN[0],ORIGIN[1]-(g['aN']*r+g['bN']))
   vegetation_mask.append(1 if any(vegetation[i].covers(p) for i in vtree.query(p)) else 0)
 meta={'title':'Victoria Harbour · first city district','source':'OpenStreetMap contributors','licence':'ODbL-1.0','sourceURL':'https://www.openstreetmap.org/copyright','snapshot':data['osm3s']['timestamp_osm_base'],'bbox':BBOX,'origin':ORIGIN,'crs':'EPSG:2326','axes':'x = easting - originE; y = elevation metres; z = originN - northing','heightPolicy':'OSM height where present; levels × 3.2 m otherwise; unknown = 24 m (large podiums 9 m, service buildings 6 m). Estimates are not surveyed heights.','terrain':'Lands Department DTM, existing 70 m sampled grid; no vertical exaggeration','omittedOutlinesWithParts':replaced,'counts':{'buildings':len(features),'roads':len(roads),'parks':len(parks),'heights':dict(collections.Counter(f['heightSource'] for f in features))}}
 OUT.mkdir(parents=True,exist_ok=True)
 for name,obj in [('central',{'meta':meta,'buildings':features,'roads':roads,'parks':parks}),('terrain',{'meta':{'origin':ORIGIN,'georef':g,'source':'../data/hk-dtm5m.json; hk-b50k-landcover.json'},**dem,'vegetation':vegetation_mask})]:
  (OUT/f'{name}.json').write_text(json.dumps(obj,separators=(',',':'),ensure_ascii=False))
 (OUT/'provenance.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps(meta,indent=2))
if __name__=='__main__':main()
