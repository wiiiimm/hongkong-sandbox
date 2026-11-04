"""Fetch exact Hoi Shing appendage HK80 primary topographic context; no acceptance."""
import math,sys,json,gzip,mapbox_vector_tile
from shapely.geometry import shape,mapping
from shapely.ops import transform
from run import ROOT,HERE,read,save,digest
sys.path.insert(0,str(HERE.parent/'landsd-territory'));from source import request
BATCH='government-xl-hoi-shing-exact-72-face-primary-vectors-v1-20261011';DOC=ROOT/'docs/astra-city/government-import'/BATCH
BASE='https://mapapi.geodata.gov.hk/gs/api/v1.0.0/vt/basemap/HK80'
def fetch(path,url,parameters=None,json_expected=False):
 if path.exists():
  raw=path.read_bytes();assert digest(raw)==read(path.with_name(path.name+'.request.json'))['sha256'];return json.loads(raw) if json_expected else raw
 raw,receipt=request(url,parameters,json_expected=json_expected);path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw);save(path.with_name(path.name+'.request.json'),receipt);return json.loads(raw) if json_expected else raw
meta=fetch(DOC/'service.json',BASE,{'f':'pjson'},True);style=fetch(DOC/'style.json',BASE+'/resources/styles/root.json',None,True)
info=meta['tileInfo'];level=15;lod=next(l for l in info['lods'] if l['level']==level);res=lod['resolution'];tile_size=info['cols'];width=res*tile_size;ox=info['origin']['x'];oy=info['origin']['y'];assert info['spatialReference'].get('latestWkid',info['spatialReference']['wkid'])==2326
part=read(ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261011-hoi-shing-72-face-upward-part-context-v1/diagnostic.json.gz')
assert len(part['complete72FacePartIds'])==72
lo,hi=part['completePartBounds'];x0,z0,x1,z1=lo[0]-20,lo[2]-20,hi[0]+20,hi[2]+20
from shapely.geometry import box
context=box(x0,z0,x1,z1);emin,emax=x0+834500,x1+834500;nmin,nmax=816500-z1,816500-z0;tiles=set()
for x in range(math.floor((emin-ox)/width),math.floor((emax-ox)/width)+1):
 for y in range(math.floor((oy-nmax)/width),math.floor((oy-nmin)/width)+1):tiles.add((x,y))
rows=[]
for x,y in sorted(tiles):
 raw=fetch(DOC/f'vector-tiles/{level}-{x}-{y}.pbf',f'{BASE}/tile/{level}/{y}/{x}.pbf');decoded=mapbox_vector_tile.decode(gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw,default_options={'y_coord_down':True});save(DOC/f'vector-tiles/{level}-{x}-{y}-layers.json',{k:{'extent':v['extent'],'features':len(v['features'])} for k,v in decoded.items()})
 for name,layer in decoded.items():
  extent=layer['extent']
  for f in layer['features']:
   geom=transform(lambda xx,yy,zz=None:(ox+x*width+xx/extent*width-834500,816500-(oy-y*width-yy/extent*width)),shape(f['geometry']))
   if not geom.intersects(context):continue
   rows.append({'tile':[level,x,y],'layer':name,'id':f.get('id'),'properties':f.get('properties'),'geometry':mapping(geom),'quantizationStepM':width/extent})
selected=[l for l in style['layers'] if l.get('source-layer') in {r['layer'] for r in rows}]
save(DOC/'original-provider-stair-style-contract.json',{'layers':selected,'tileInfo':info,'qualification':'Original provider cartographic feature symbols and exact HK80 tile coordinate convention. Only exact cartographic context: no appendage function, surveyed height, support or burial acceptance from a symbol alone.'});save(DOC/'decoded-original-feature-geometries.json.gz',{'rows':rows,'tileCount':len(tiles),'worldOrigin':[834500,816500],'sourceUntouched':True,'exactSourcePartContext':{'path':'docs/astra-city/government-import/xl-terrain-recovery-20261011-hoi-shing-72-face-upward-part-context-v1/diagnostic.json.gz','sha256':digest((ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261011-hoi-shing-72-face-upward-part-context-v1/diagnostic.json.gz').read_bytes())},'contextBoundsXZ':[x0,z0,x1,z1],'completeOriginalIntersectingFeaturesPreserved':True,'physicalAccepted':False,'identityAccepted':False})
print({'tiles':len(tiles),'features':len(rows),'layers':[(r['layer'],r['properties']) for r in rows[:30]],'style':[(l['id'],l.get('filter')) for l in selected]},flush=True)
