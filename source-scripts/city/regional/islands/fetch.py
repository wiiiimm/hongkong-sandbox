"""Retain bounded OSM island-detail queries; never modify earlier source snapshots."""
import gzip,json,pathlib,time,urllib.error,urllib.parse,urllib.request
HERE=pathlib.Path(__file__).resolve().parent
REGIONS=[('western-and-southern-islands',[22.13,113.82,22.375,114.34]),('northeastern-islands',[22.425,114.285,22.565,114.445])]
CLAUSES=['way["man_made"="pier"]','relation["man_made"="pier"]["type"="multipolygon"]','way["natural"="beach"]','relation["natural"="beach"]["type"="multipolygon"]','way["highway"="pedestrian"]["area"="yes"]','relation["highway"="pedestrian"]["area"="yes"]["type"="multipolygon"]','way["leisure"="pitch"]','relation["leisure"="pitch"]["type"="multipolygon"]','way["aeroway"="apron"]','relation["aeroway"="apron"]["type"="multipolygon"]','node["place"="island"]','way["place"="island"]','relation["place"="island"]']
def fetch(name,bbox):
 target=HERE/'snapshots'/f'{name}.json.gz'
 if target.exists():print('Using cached',name,flush=True);return
 q='[out:json][timeout:150];area(3600913110)->.hk;('+''.join(f'{c}({",".join(map(str,bbox))})(area.hk);' for c in CLAUSES)+');out geom;'
 for attempt in range(3):
  try:
   req=urllib.request.Request('https://overpass-api.de/api/interpreter',data=urllib.parse.urlencode({'data':q}).encode(),headers={'User-Agent':'HongKongSandbox-Astra/5.0 (bounded cached island surfaces; https://github.com/wiiiimm/hongkong-sandbox)'})
   with urllib.request.urlopen(req,timeout=180) as response:raw=response.read()
   data=json.loads(raw)
   if data.get('remark') or not data.get('elements'):raise RuntimeError('Partial or empty source response')
   break
  except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,RuntimeError) as error:
   if attempt==2:raise
   print(name,error,'backing off',flush=True);time.sleep(20*(attempt+1))
 target.write_bytes(gzip.compress(raw,mtime=0));target.with_suffix('.query.txt').write_text(q+'\n')
 print(name,len(data['elements']),'records',data['osm3s']['timestamp_osm_base'],flush=True)
if __name__=='__main__':
 for name,bbox in REGIONS:fetch(name,bbox)
