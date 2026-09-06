"""Fetch Hong Kong bridge/elevated-walkway geometry.
One cached geometry query; connected access ways use the complete retained highway snapshots. source snapshots in source-scripts/city/snapshots remain unchanged.
"""
import gzip,json,pathlib,urllib.parse,urllib.request
HERE=pathlib.Path(__file__).resolve().parent
QUERY='''[out:json][timeout:160];area(3600913110)->.hk;(
way["highway"]["bridge"]["bridge"!="no"](area.hk);
way["highway"~"^(footway|path|pedestrian|steps|cycleway|corridor)$"]["level"](area.hk);
way["highway"~"^(footway|path|pedestrian|steps|cycleway|corridor)$"]["layer"~"^[1-9]"](area.hk);
way["highway"~"^(footway|path|pedestrian|steps|cycleway|corridor)$"]["min_height"](area.hk);
way["highway"~"^(footway|path|pedestrian|steps|cycleway|corridor)$"]["height"](area.hk);
way["man_made"="bridge"](area.hk);
relation["man_made"="bridge"]["type"="multipolygon"](area.hk);
);out geom;'''
def main():
 target=HERE/'hong-kong-bridges-osm.json.gz'
 if target.exists():print('Using retained',target);return
 request=urllib.request.Request('https://overpass-api.de/api/interpreter',data=urllib.parse.urlencode({'data':QUERY}).encode(),headers={'User-Agent':'HongKongSandbox-Astra/bridge-geometry (cached HK ODbL import)'})
 with urllib.request.urlopen(request,timeout=185) as response:raw=response.read()
 data=json.loads(raw)
 if data.get('remark') or not data.get('elements'):raise ValueError('Incomplete Overpass response')
 target.write_bytes(gzip.compress(raw,mtime=0));(HERE/'hong-kong-bridges-osm.query.txt').write_text(QUERY+'\n');print(len(data['elements']),'elements;',data['osm3s']['timestamp_osm_base'])
def fetch_districts():
 target=HERE/'hong-kong-districts-osm.json.gz'
 if target.exists():return
 query='[out:json][timeout:120];area(3600913110)->.hk;relation["boundary"="administrative"]["admin_level"="6"](area.hk);out geom;'
 request=urllib.request.Request('https://overpass-api.de/api/interpreter',data=urllib.parse.urlencode({'data':query}).encode(),headers={'User-Agent':'HongKongSandbox-Astra/bridge-district-audit'})
 with urllib.request.urlopen(request,timeout=145) as response:raw=response.read()
 parsed=json.loads(raw)
 if parsed.get('remark') or not parsed.get('elements'):raise ValueError('Incomplete district boundary response')
 target.write_bytes(gzip.compress(raw,mtime=0));(HERE/'hong-kong-districts-osm.query.txt').write_text(query+'\n');print('District audit:',len(parsed['elements']),'boundaries')
if __name__=='__main__':main();fetch_districts()
