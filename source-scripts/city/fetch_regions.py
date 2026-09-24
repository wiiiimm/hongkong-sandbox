"""Fetch bounded, sequential Overpass snapshots once; rebuilds use committed caches.
Queries use Hong Kong's mapped administrative area to avoid importing Shenzhen.
A separate cached boundary supports local clipping and reproducible provenance.
"""
import argparse,gzip,json,pathlib,time,urllib.error,urllib.parse,urllib.request
HERE=pathlib.Path(__file__).resolve().parent
REGIONS=json.loads((HERE/'regions.json').read_text())
BOUNDARY_QUERY='[out:json][timeout:150];relation(913110);out geom;'
ENDPOINT='https://overpass-api.de/api/interpreter'
def query(bbox):
 clauses=['way["building"]','way["building:part"]','relation["building"]["type"="multipolygon"]','relation["building:part"]["type"="multipolygon"]','way["highway"]','way["leisure"="park"]','way["aeroway"="runway"]','way["aeroway"="taxiway"]','way["landuse"~"^(residential|commercial|retail|industrial)$"]','relation["type"="multipolygon"]["landuse"~"^(residential|commercial|retail|industrial)$"]']
 return '[out:json][timeout:150];area(3600913110)->.hk;('+''.join(f'{c}({",".join(map(str,bbox))})(area.hk);' for c in clauses)+');out geom;'
def fetch(target,q,refresh=False):
 if target.exists() and not refresh:print('Using cached',target.name,flush=True);return
 print('Fetching',target.name,flush=True)
 for attempt in range(3):
  request=urllib.request.Request(ENDPOINT,data=urllib.parse.urlencode({'data':q}).encode(),headers={'User-Agent':'HongKongSandbox-Astra/4.0 (bounded cached HK import; https://github.com/wiiiimm/hongkong-sandbox)'})
  try:
   with urllib.request.urlopen(request,timeout=180) as response:raw=response.read()
   parsed=json.loads(raw)
   if parsed.get('remark') or not parsed.get('elements'):raise RuntimeError('Incomplete Overpass response: '+str(parsed.get('remark')))
   break
  except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,RuntimeError) as error:
   if attempt==2:raise
   print('Temporary source error:',error,'; retrying once the endpoint has cooled down',flush=True);time.sleep(10*(attempt+1))
 tmp=target.with_suffix('.tmp');tmp.write_bytes(gzip.compress(raw,mtime=0));tmp.replace(target)
 target.with_suffix('.query.txt').write_text(q+'\n')
 print(target.name,len(parsed['elements']),'elements;',parsed['osm3s']['timestamp_osm_base'],flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--region',choices=[r['id'] for r in REGIONS]);ap.add_argument('--refresh',action='store_true');a=ap.parse_args();(HERE/'snapshots').mkdir(exist_ok=True)
 fetch(HERE/'snapshots/hong-kong-boundary.json.gz',BOUNDARY_QUERY,a.refresh and not a.region)
 for r in REGIONS:
  if a.region and r['id']!=a.region:continue
  fetch(HERE/'snapshots'/f'{r["id"]}.json.gz',query(r['bbox']),a.refresh)
