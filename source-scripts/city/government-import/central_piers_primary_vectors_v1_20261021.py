"""Original independently georeferenced government vectors around far source wall."""
import sys,math,json,gzip,mapbox_vector_tile,shapely
from shapely.geometry import shape,mapping
from shapely.ops import transform
from pathlib import Path
from run import ROOT,HERE,read,save,digest
sys.path.insert(0,str(HERE.parent/'landsd-territory'));from source import request
DOC=ROOT/'docs/astra-city/government-import/government-xl-central-piers-primary-vectors-v1-20261021'
BASE='https://mapapi.geodata.gov.hk/gs/api/v1.0.0/vt/basemap/HK80'
def fetch(path,url,params=None,json_expected=False):
 if path.exists():raw=path.read_bytes();assert digest(raw)==read(path.with_name(path.name+'.request.json'))['sha256']
 else:
  raw,r=request(url,params,json_expected=False);path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw);save(path.with_name(path.name+'.request.json'),r)
 return json.loads(gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw) if json_expected else raw
meta=fetch(DOC/'provider-vector-service.json',BASE,{'f':'pjson'},True);style=fetch(DOC/'provider-vector-style.json',BASE+'/resources/styles/root.json',None,True);info=meta['tileInfo'];level=15;res=next(l['resolution'] for l in info['lods'] if l['level']==level);width=res*info['cols'];ox=info['origin']['x'];oy=info['origin']['y'];assert info['spatialReference'].get('latestWkid',info['spatialReference']['wkid'])==2326
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
source=ROOT/'docs/astra-city/government-import/government-xl-six-far-faces-v1-20261021'
_,pins=authenticate(source);paths=[source/(uid+'.json.gz')for uid in ['213352:0','285475:0']]
for p in paths:assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
packets=[read(p)for p in paths];pts=[v for packet in packets for face in packet['farFaceVertices']for v in face];x0=min(v[0] for v in pts)-15;x1=max(v[0] for v in pts)+15;z0=min(v[2] for v in pts)-15;z1=max(v[2] for v in pts)+15;region=shapely.box(x0,z0,x1,z1);tiles=set()
for x in range(math.floor((x0+834500-ox)/width),math.floor((x1+834500-ox)/width)+1):
 for y in range(math.floor((oy-(816500-z0))/width),math.floor((oy-(816500-z1))/width)+1):tiles.add((x,y))
rows=[]
for x,y in sorted(tiles):
 raw=fetch(DOC/f'vector-tiles/{level}-{x}-{y}.pbf',f'{BASE}/tile/{level}/{y}/{x}.pbf');layers=mapbox_vector_tile.decode(gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw,default_options={'y_coord_down':True});save(DOC/f'vector-tiles/{level}-{x}-{y}-layers.json',{n:{'extent':l['extent'],'features':len(l['features'])} for n,l in layers.items()})
 for name,l in layers.items():
  extent=l['extent']
  for f in l['features']:
   g=transform(lambda xx,yy,zz=None:(ox+x*width+xx/extent*width-834500,816500-(oy-y*width-yy/extent*width)),shape(f['geometry']))
   if not g.intersects(region):continue
   rows.append({'tile':[level,x,y],'layer':name,'id':f.get('id'),'properties':f.get('properties'),'geometry':mapping(g),'quantizationStepM':width/extent})
save(DOC/'pier-approach-government-vector-context.json.gz',{'sourcePackets':[{'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}for p in paths],'rows':rows,'qualification':'Independent HK80 provider features around both exact source extent sets. No identity or installation approval.'})
result=dict(uids=['landsd/213352:0','landsd/285475:0'],tiles=len(tiles),features=len(rows),installationApproved=False,identityApproved=False)
r=module('pier_vectors_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(DOC.name,'independent-official-pier-approach-vectors',[Path(__file__),source/'result.json',*paths],result)
print(dict(jobId=r['jobId'],**result),flush=True)
