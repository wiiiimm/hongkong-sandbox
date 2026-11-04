"""Fetch a single bounded, cached supplementary OSM surface/landmark snapshot.
Existing project snapshots remain untouched. Rebuilds do not require a network.
"""
import gzip,json,pathlib,urllib.parse,urllib.request
HERE=pathlib.Path(__file__).resolve().parent
QUERY='''[out:json][timeout:150];area(3600913110)->.hk;(
way["natural"="beach"](area.hk);relation["natural"="beach"]["type"="multipolygon"](area.hk);
way["leisure"="pitch"](area.hk);way["man_made"="pier"](area.hk);
way["highway"="pedestrian"]["area"="yes"](area.hk);
node["place"~"^(island|village|hamlet)$"](area.hk);
node["tourism"="viewpoint"](area.hk);
);out geom;'''
def main():
 target=HERE/'surfaces-osm.json.gz'
 if target.exists():print('Using retained',target);return
 request=urllib.request.Request('https://overpass-api.de/api/interpreter',data=urllib.parse.urlencode({'data':QUERY}).encode(),headers={'User-Agent':'HongKongSandbox-Astra/NT-regional-pass (cached ODbL geometry)'})
 with urllib.request.urlopen(request,timeout=175) as response:raw=response.read()
 parsed=json.loads(raw)
 if parsed.get('remark') or not parsed.get('elements'):raise ValueError('Incomplete Overpass response')
 target.write_bytes(gzip.compress(raw,mtime=0));(HERE/'surfaces-osm.query.txt').write_text(QUERY+'\n')
 print(len(parsed['elements']),'elements;',parsed['osm3s']['timestamp_osm_base'])
if __name__=='__main__':main()
