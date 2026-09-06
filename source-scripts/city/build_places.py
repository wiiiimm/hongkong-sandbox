"""Build sourced neighbourhood camera presets and public-path arrivals.
Camera centres are approximate browsing locations, not administrative centroids.
Retained OSM features supply new centres; arrivals must clear the committed
building mesh and stand on the existing terrain. No live requests are made.
"""
import gzip,json,math,pathlib
from pyproj import Transformer
from shapely.geometry import Point,Polygon,LineString
from shapely.strtree import STRtree
from build_city import ROOT,OUT,ORIGIN,xy,geometry,coords
HERE=pathlib.Path(__file__).resolve().parent
INVERSE=Transformer.from_crs(2326,4326,always_xy=True)

def main():
 config=json.loads((HERE/'destinations.json').read_text());manifest=json.loads((OUT/'manifest.json').read_text());records={}
 for source in sorted(manifest['sources'],key=lambda s:s['snapshot']):
  for e in json.loads(gzip.decompress((ROOT/source['file']).read_bytes()))['elements']:records[f'{e["type"]}/{e["id"]}']=e
 dem=json.loads((OUT/'terrain.json').read_text());g=dem['meta']['georef'];w=dem['w']
 def ground(x,z):
  c=(x+ORIGIN[0]-g['bE'])/g['aE'];r=(ORIGIN[1]-z-g['bN'])/g['aN']
  if not (0<=c<w-1 and 0<=r<dem['h']-1):return -1000
  i,j=int(c),int(r);u,v=c-i,r-j
  a,b,d,e=[dem['elev'][idx] for idx in (j*w+i,j*w+i+1,(j+1)*w+i,(j+1)*w+i+1)]
  return a+(b-a)*u+(d-a)*v if u+v<=1 else e+(d-e)*(1-u)+(b-e)*(1-v)
 def land_triangle(x,z):
  c=(x+ORIGIN[0]-g['bE'])/g['aE'];r=(ORIGIN[1]-z-g['bN'])/g['aN']
  if not (0<=c<w-1 and 0<=r<dem['h']-1):return False
  i,j=int(c),int(r);u,v=c-i,r-j
  indices=(j*w+i,j*w+i+1,(j+1)*w+i) if u+v<=1 else (j*w+i+1,(j+1)*w+i,(j+1)*w+i+1)
  return all(dem['elev'][idx]>0 for idx in indices)
 blocks=[];heights=[]
 for meta in manifest['tiles']:
  for b in json.loads((ROOT/'3d-viewer'/meta['url']).read_text())['buildings']:
   p=Polygon(b['rings'][0],b['rings'][1:]).buffer(0)
   if not p.is_empty:blocks.append(p);heights.append((b['base']+b['minimum'],b['base']+b['height']))
 blocktree=STRtree(blocks);paths=[];pathids=[]
 for oid,e in records.items():
  t=e.get('tags',{})
  if t.get('highway') not in ('footway','pedestrian','path','living_street') or t.get('access') in ('private','no') or t.get('foot')=='no' or t.get('area')=='yes' or t.get('location')=='underground' or t.get('tunnel') in ('yes','building_passage') or t.get('bridge')=='yes' or t.get('layer','0') not in ('0',0):continue
  if e.get('geometry') and len(e['geometry'])>1:
   paths.append(LineString(coords(e['geometry'])));pathids.append(oid)
 pathtree=STRtree(paths)
 def valid(point):
  y=ground(point.x,point.y)
  if y<=.8 or not land_triangle(point.x,point.y):return False
  disc=point.buffer(1.2)
  for i in blocktree.query(disc):
   lo,hi=heights[i]
   if y+1.8>lo and y<hi and blocks[i].intersects(disc):return False
  # Reject tiny terrain spikes and steep paths at the coarse grid's shoreline.
  return all(land_triangle(point.x+dx,point.y+dz) and abs(ground(point.x+dx,point.y+dz)-y)<1.5 for dx,dz in [(2,0),(-2,0),(0,2),(0,-2)])
 def arrival_near(centre,id):
  candidates=[]
  for i in pathtree.query(centre.buffer(1000)):
   path=paths[i];near=path.project(centre)
   for shift in [0,-5,5,-15,15,-40,40,-90,90,-180,180]:
    point=path.interpolate(max(0,min(path.length,near+shift)))
    if point.distance(centre)<=1000 and valid(point):candidates.append((point.distance(centre),pathids[i],point))
  if not candidates:raise ValueError('No walkable mapped public path within 1 km of '+id)
  return min(candidates,key=lambda c:(c[0],c[1]))
 output={};provenance={}
 for id,entry in config['places'].items():
  if 'target' in entry:
   p=dict(entry);x,_,z=p['target'];source=None;arrival=None
   if p.pop('repairArrival',False):
    distance,arrival,spawn=arrival_near(Point(p['spawn']),id);p['spawn']=[round(spawn.x,1),round(spawn.y,1)];p['arrivalSource']='https://www.openstreetmap.org/'+arrival
    print(id,'repaired arrival',arrival,'offset',round(distance),'m',flush=True)
  else:
   source=entry.get('source');centre=geometry(records[source]).centroid if source else Point(xy(*entry['seedWGS84']))
   _,arrival,spawn=arrival_near(centre,id);x,z=centre.x,centre.y
   if not source:x,z=spawn.x,spawn.y;source=arrival
   p={k:entry[k] for k in ['region','title','zh','description','offset']}
   p.update(target=[round(x,1),round(max(entry['height'],ground(x,z)+25),1),round(z,1)],spawn=[round(spawn.x,1),round(spawn.y,1)])
   print(id,source,'arrival',arrival,'offset',round(spawn.distance(centre)),'m',flush=True)
  lon,lat=INVERSE.transform(x+ORIGIN[0],ORIGIN[1]-z);p['lat']=round(lat,6);p['lon']=round(lon,6)
  if source:p['source']='https://www.openstreetmap.org/'+source
  output[id]=p
  provenance[id]={'cameraWGS84':[p['lon'],p['lat']],'cameraWorld':p['target'],'arrivalWorld':p['spawn'],'cameraSource':source or 'Retained initial approximate camera preset','arrivalSource':arrival or 'Retained initial approximate arrival','precision':'Approximate camera/arrival position for exploration; not surveyed or an administrative centre.'}
 text='// Generated by source-scripts/city/build_places.py. Coordinates are approximate public-place camera positions.\n'
 text+='export const REGIONS='+json.dumps(config['regions'],ensure_ascii=False,separators=(',',':'))+';\n'
 text+='export const PLACES='+json.dumps(output,ensure_ascii=False,indent=2)+';\n'
 text+="export function closestPlace(x,z){return Object.entries(PLACES).filter(([id])=>id!=='lantaupeaks').sort((a,b)=>Math.hypot(a[1].target[0]-x,a[1].target[2]-z)-Math.hypot(b[1].target[0]-x,b[1].target[2]-z))[0][0];}\n"
 (ROOT/'3d-viewer/city/places.js').write_text(text)
 (OUT/'destinations-provenance.json').write_text(json.dumps({'source':'OpenStreetMap contributors','licence':'ODbL-1.0','configuration':'source-scripts/city/destinations.json','places':provenance},ensure_ascii=False,indent=2)+'\n')
 print('Generated',len(output),'presets with WGS84 observer locations')
if __name__=='__main__':main()
