"""Fetch OSM land-use polygons for the current city footprint, once and sequentially."""
import gzip,json,pathlib,urllib.parse,urllib.request
HERE=pathlib.Path(__file__).resolve().parent
QUERY='[out:json][timeout:150];(way["landuse"~"^(residential|commercial|retail|industrial)$"](22.19,113.82,22.37,114.27);relation["type"="multipolygon"]["landuse"~"^(residential|commercial|retail|industrial)$"](22.19,113.82,22.37,114.27););out geom;'
if __name__=='__main__':
 target=HERE/'snapshots/activity-landuse.json.gz'
 if target.exists():print('Using cached activity land-use snapshot')
 else:
  req=urllib.request.Request('https://overpass-api.de/api/interpreter',data=urllib.parse.urlencode({'data':QUERY}).encode(),headers={'User-Agent':'HongKongSandbox-Astra/3.0 (bounded land-use import)'})
  with urllib.request.urlopen(req,timeout=180) as response:raw=response.read()
  data=json.loads(raw)
  if data.get('remark') or not data.get('elements'):raise RuntimeError('Incomplete land-use source')
  target.write_bytes(gzip.compress(raw,mtime=0));target.with_suffix('.query.txt').write_text(QUERY+'\n')
  print(len(data['elements']),'land-use records;',data['osm3s']['timestamp_osm_base'])
