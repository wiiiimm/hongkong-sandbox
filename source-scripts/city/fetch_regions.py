"""Fetch bounded, sequential Overpass snapshots once; normal rebuilds use these files."""
import argparse,gzip,json,pathlib,urllib.parse,urllib.request
HERE=pathlib.Path(__file__).resolve().parent
REGIONS=json.loads((HERE/'regions.json').read_text())
def query(bbox):
 clauses=['way["building"]','way["building:part"]','relation["building"]["type"="multipolygon"]','relation["building:part"]["type"="multipolygon"]','way["highway"]','way["leisure"="park"]','way["aeroway"="runway"]','way["aeroway"="taxiway"]']
 return '[out:json][timeout:150];('+''.join(f'{c}({",".join(map(str,bbox))});' for c in clauses)+');out geom;'
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--region',choices=[r['id'] for r in REGIONS]);ap.add_argument('--refresh',action='store_true');a=ap.parse_args();(HERE/'snapshots').mkdir(exist_ok=True)
 for r in REGIONS:
  if a.region and r['id']!=a.region:continue
  target=HERE/'snapshots'/f'{r["id"]}.json.gz'
  if target.exists() and not a.refresh:print('Using cached',r['id'],flush=True);continue
  q=query(r['bbox']);print('Fetching',r['id'],flush=True)
  request=urllib.request.Request('https://overpass-api.de/api/interpreter',data=urllib.parse.urlencode({'data':q}).encode(),headers={'User-Agent':'HongKongSandbox-Astra/2.0 (bounded OSM district import; https://github.com/wiiiimm/hongkong-sandbox)'})
  with urllib.request.urlopen(request,timeout=180) as response:raw=response.read()
  parsed=json.loads(raw)
  if parsed.get('remark') or not parsed.get('elements'):raise RuntimeError('Incomplete Overpass response: '+str(parsed.get('remark')))
  tmp=target.with_suffix('.tmp');tmp.write_bytes(gzip.compress(raw,mtime=0));tmp.replace(target)
  target.with_suffix('.query.txt').write_text(q+'\n')
  print(r['id'],len(parsed['elements']),'elements;',parsed['osm3s']['timestamp_osm_base'],flush=True)
