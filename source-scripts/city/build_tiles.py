"""Build district-streamable OSM geometry from committed regional snapshots.
Buildings keep their full geometry and one owner tile. Lines/parks are split on
2 km boundaries. No live services are needed by either the rebuild or viewer.
"""
import collections,gzip,hashlib,json,math,pathlib
from shapely.geometry import Polygon,Point,LineString,box
from shapely.ops import unary_union
from shapely.strtree import STRtree
from build_city import ROOT,OUT,ORIGIN,xy,coords,geometry,polys,packed,rounded,number
HERE=pathlib.Path(__file__).resolve().parent
SIZE=2000

def cell(x,z):return math.floor(x/SIZE),math.floor(z/SIZE)
def cell_id(x,z):return f'{x}_{z}'
def counts(buildings,roads,parks):return {'buildings':len(buildings),'roads':len(roads),'parks':len(parks),'heights':dict(collections.Counter(b['heightSource'] for b in buildings))}
def split_cells(geom):
 x0,z0,x1,z1=geom.bounds
 for x in range(math.floor(x0/SIZE),math.floor(x1/SIZE)+1):
  for z in range(math.floor(z0/SIZE),math.floor(z1/SIZE)+1):
   clipped=geom.intersection(box(x*SIZE,z*SIZE,(x+1)*SIZE,(z+1)*SIZE))
   if not clipped.is_empty:yield cell_id(x,z),clipped

def main():
 regions=json.loads((HERE/'regions.json').read_text());regions.insert(0,{'id':'central','title':'Original Victoria Harbour snapshot','bbox':[22.268,114.125,22.311,114.192]})
 sources=[];records=[];coverage=[]
 for r in regions:
  path=HERE/'central-osm.json.gz' if r['id']=='central' else HERE/'snapshots'/f'{r["id"]}.json.gz'
  raw=gzip.decompress(path.read_bytes());data=json.loads(raw)
  if data.get('remark'):raise ValueError('Partial source: '+r['id'])
  sources.append({**r,'snapshot':data['osm3s']['timestamp_osm_base'],'file':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest()})
  records.append((data['osm3s']['timestamp_osm_base'],data['elements']))
  s,w,n,e=r['bbox'];coverage.append(Polygon([xy(w,s),xy(e,s),xy(e,n),xy(w,n)]))
 elements={}
 for _,es in sorted(records,key=lambda r:r[0]):
  for e in es:elements[f'{e["type"]}/{e["id"]}']=e
 clip=unary_union(coverage);dem=json.loads((OUT/'terrain.json').read_text());g=dem['meta']['georef']
 def ground(x,z):
  c=max(0,min(dem['w']-1.001,(x+ORIGIN[0]-g['bE'])/g['aE']));r=max(0,min(dem['h']-1.001,(ORIGIN[1]-z-g['bN'])/g['aN']));i,j=int(c),int(r);u,v=c-i,r-j;w=dem['w']
  a,b,d,e=[dem['elev'][idx] for idx in (j*w+i,j*w+i+1,(j+1)*w+i,(j+1)*w+i+1)]
  return max(1.2,a+(b-a)*u+(d-a)*v if u+v<=1 else e+(d-e)*(1-u)+(b-e)*(1-v))
 tiles={}
 def tile(key):
  if key not in tiles:tiles[key]={'id':key,'buildings':[],'roads':[],'parks':[]}
  return tiles[key]
 multipolygon_members={m['ref'] for e in elements.values() if e['type']=='relation' and e.get('tags',{}).get('type')=='multipolygon' and (e.get('tags',{}).get('building') or e.get('tags',{}).get('building:part')) for m in e.get('members',[]) if m.get('role','outer') in ('outer','')}
 features=[];parts=[];part_indices=[]
 for oid,el in sorted(elements.items()):
  t=el.get('tags',{});name=t.get('name:en',t.get('name',''));kind=t.get('highway',t.get('aeroway'));underground=t.get('location')=='underground' or t.get('parking')=='underground'
  if kind and el.get('geometry') and t.get('area')!='yes' and t.get('tunnel') not in ('yes','building_passage') and not underground and kind not in ('construction','proposed','elevator'):
   geom=LineString(coords(el['geometry'])).intersection(clip)
   if not geom.is_empty:
    for key,p in split_cells(geom):
     lines=[p] if p.geom_type=='LineString' else list(p.geoms) if p.geom_type=='MultiLineString' else []
     for line in lines:
      if line.length>1:tile(key)['roads'].append({'id':oid,'kind':kind,'name':name,'bridge':t.get('bridge')=='yes','layer':number(t.get('layer')) or 0,'path':rounded(line.simplify(.7).coords)})
  if not (t.get('building') or t.get('building:part') or t.get('leisure')=='park'):continue
  if underground or t.get('building') in ('no','construction','roof') or t.get('building:part')=='no' or str(t.get('layer','')).startswith('-'):continue
  if el['type']=='relation' and t.get('type')!='multipolygon':continue
  if el['type']=='way' and el['id'] in multipolygon_members and not t.get('building:part'):continue
  geom=geometry(el)
  if geom is None or geom.is_empty:continue
  if t.get('leisure')=='park':
   geom=geom.intersection(clip)
   if not geom.is_empty:
    for key,p in split_cells(geom):
     for park in polys(p):
      if park.area>8:tile(key)['parks'].append({'id':oid,'name':name,'rings':packed(park)})
   continue
  for component,p in enumerate(polys(geom.simplify(.25,preserve_topology=True))):
   if p.area<8 or not clip.intersects(p):continue
   height=number(t.get('height'));levels=number(t.get('building:levels',t.get('building:part:levels')));kind=t.get('building:use',t.get('building','yes'));method='tagged' if height else 'levels' if levels else 'estimated'
   height=height or (levels*3.2 if levels else 9 if p.area>8000 else 6 if kind in ('service','shed','garage','garages') else 24)
   minimum=number(t.get('min_height')) or (number(t.get('building:min_level')) or 0)*3.2
   if not 0<height<600 or minimum>=height:continue
   centre=rounded([(p.centroid.x,p.centroid.y)])[0];key=cell_id(*cell(*centre))
   f={'id':oid,'uid':f'{oid}:{component}','tile':key,'name':name,'zh':t.get('name:zh-Hant',t.get('name:zh','')),'kind':kind,'height':round(height,1),'heightSource':method,'levels':levels,'minimum':round(minimum,1),'base':round(min(ground(x,z) for x,z in p.exterior.coords),2),'part':bool(t.get('building:part')),'material':t.get('building:material',''),'rings':packed(p),'centre':centre}
   if f['part']:parts.append(p);part_indices.append(len(features))
   features.append(f)
 print('Processed',len(features),'building forms',flush=True)
 tree=STRtree(parts);filtered=[];replaced=0
 for f in features:
  p=Polygon(f['rings'][0],f['rings'][1:]).buffer(0)
  if not f['part']:
   matches=[int(i) for i in tree.query(p) if p.covers(parts[i].representative_point())]
   if matches and unary_union([parts[i] for i in matches]).intersection(p).area/max(1,p.area)>.5:
    for i in matches:
     child=features[part_indices[i]]
     if not child['name']:child['name']=f['name']
     if not child['zh']:child['zh']=f['zh']
     child.setdefault('parent',f['id'])
    replaced+=1;continue
  filtered.append(f)
 features=filtered
 for f in features:tile(f['tile'])['buildings'].append(f)
 tile_dir=OUT/'tiles';tile_dir.mkdir(exist_ok=True);metadata=[]
 for key,data in sorted(tiles.items()):
  x,z=map(int,key.split('_'));bounds=[x*SIZE,z*SIZE,(x+1)*SIZE,(z+1)*SIZE]
  for b in data['buildings']:
   for px,pz in b['rings'][0]:bounds=[min(bounds[0],px),min(bounds[1],pz),max(bounds[2],px),max(bounds[3],pz)]
  data['bounds']=bounds
  content=json.dumps(data,separators=(',',':'),ensure_ascii=False).encode();(tile_dir/f'{key}.json').write_bytes(content)
  metadata.append({'id':key,'bounds':bounds,'centre':[(x+.5)*SIZE,(z+.5)*SIZE],'url':f'city/data/tiles/{key}.json','bytes':len(content),'counts':counts(data['buildings'],data['roads'],data['parks'])})
 for old in tile_dir.glob('*.json'):
  if old.stem not in tiles:old.unlink()
 catalog=[{k:b[k] for k in ('id','uid','tile','name','zh','height','heightSource','levels','base','centre')}|({'parent':b['parent']} if 'parent' in b else {}) for b in features if b['name'] or b['zh']]
 (OUT/'catalogue.json').write_text(json.dumps(catalog,separators=(',',':'),ensure_ascii=False))
 overview={key:[b['centre'] for b in data['buildings']] for key,data in tiles.items() if data['buildings']}
 (OUT/'overview.json').write_text(json.dumps(overview,separators=(',',':')))
 manifest={'version':2,'title':'Hong Kong Island · Kowloon · Lantau','origin':ORIGIN,'crs':'EPSG:2326','tileSize':SIZE,'source':'OpenStreetMap contributors','licence':'ODbL-1.0','sourceURL':'https://www.openstreetmap.org/copyright','sources':sources,'snapshot':max(s['snapshot'] for s in sources),'heightPolicy':'OSM tagged height; otherwise levels × 3.2 m; otherwise explicitly labelled fallback.','terrain':'Existing Lands Department 70 m sampled grid; no vertical exaggeration. Historical terrain may not include recent reclamation.','counts':counts(features,[r for t in tiles.values() for r in t['roads']],[p for t in tiles.values() for p in t['parks']]),'omittedOutlinesWithParts':replaced,'catalogue':'city/data/catalogue.json','overview':'city/data/overview.json','tiles':metadata}
 (OUT/'manifest.json').write_text(json.dumps(manifest,separators=(',',':'),ensure_ascii=False))
 print(json.dumps({k:manifest[k] for k in ('title','counts','omittedOutlinesWithParts')},indent=2),flush=True);print(len(tiles),'tiles,',len(catalog),'searchable forms',flush=True)
if __name__=='__main__':main()
