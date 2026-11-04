"""Unmodified primary government aerial context at exact original extra components."""
import math,urllib.request,time
from pyproj import Transformer
from run import ROOT,HERE,read,save,digest
DOC=ROOT/'docs/astra-city/government-import/government-xl-spatial-surface-roles-20261009';rows=[]
for uid in ['173512-0','263423-0','157125-0']:
 r=read(DOC/(uid+'.json.gz'));b=r['variants']['direct-shared-OSM']['stats']['farSourceBounds']
 if b is None:
  v=r['variants']['direct-shared-OSM'];ring=v['groupForms'][0]['rings'][0];xs=[p[0] for p in ring];zs=[p[1] for p in ring];b=[[min(xs),0,min(zs)],[max(xs),0,max(zs)]]
 x=(b[0][0]+b[1][0])/2;z=(b[0][2]+b[1][2])/2;lon,lat=Transformer.from_crs(2326,4326,always_xy=True).transform(x+834500,816500-z);n=2**20;tx=int((lon+180)/360*n);ty=int((1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*n)
 for dx,dy in [(0,0),(1,0),(0,1),(-1,0),(0,-1)]:
  url=f'https://mapapi.geodata.gov.hk/gs/api/v1.0.0/xyz/imagery/WGS84/20/{tx+dx}/{ty+dy}.png';p=DOC/uid/f'raw-official-imagery-20-{tx+dx}-{ty+dy}.png'
  p.parent.mkdir(parents=True,exist_ok=True)
  if p.exists():rows.append(read(p.with_suffix('.request.json')));continue
  with urllib.request.urlopen(url,timeout=30) as res:raw=res.read();headers=dict(res.headers);assert res.status==200 and raw.startswith(b'\x89PNG')
  p.write_bytes(raw);receipt={'url':url,'headers':headers,'sha256':digest(raw),'latitude':lat,'longitude':lon,'tileXY':[tx+dx,ty+dy],'sourceExtraCentrePixelXY':[((lon+180)/360*n-(tx+dx))*256,((1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*n-(ty+dy))*256],'qualification':'Unmodified official imagery for source-authored component role visual context; no metre-level property ownership inferred, no tracing, source edits or fitted placement.'};save(p.with_suffix('.request.json'),receipt);rows.append(receipt)
 print(uid,lat,lon,tx,ty,flush=True)
save(DOC/'primary-imagery-context.json',{'rows':rows,'qualification':'Original government imagery, no image edits or geoalignment fitting.'})
