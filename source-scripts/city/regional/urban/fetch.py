#!/usr/bin/env python3
"""Retain ODbL public-space polygons and district boundaries for urban pass."""
import gzip,json,pathlib,time,urllib.request,urllib.parse
HERE=pathlib.Path(__file__).resolve().parent
BBOX='22.19,114.105,22.37,114.267'
QUERIES={
 'named-public-places':f'[out:json][timeout:90];(nwr["leisure"="park"]({BBOX});nwr["place"="square"]({BBOX});nwr["leisure"="garden"]["name"]({BBOX}););out geom;',
 'public-surfaces':'[out:json][timeout:120];('+''.join(f'{kind}{tag}({BBOX});' for kind in ['way','relation'] for tag in ['["man_made"="pier"]','["natural"="beach"]','["leisure"="pitch"]','["highway"="pedestrian"]["area"="yes"]'])+');out geom;',
 'urban-boundaries':f'[out:json][timeout:120];relation["boundary"="administrative"]["admin_level"~"6|8"]({BBOX});out geom;',
}
for name,query in QUERIES.items():
 target=HERE/'snapshots'/f'{name}.json.gz'
 if target.exists():print(name,'retained',flush=True);continue
 (HERE/'snapshots'/f'{name}.query.txt').write_text(query+'\n')
 for endpoint in ['https://overpass.private.coffee/api/interpreter','https://overpass.kumi.systems/api/interpreter','https://overpass-api.de/api/interpreter']:
  try:
   req=urllib.request.Request(endpoint,data=urllib.parse.urlencode({'data':query}).encode(),headers={'User-Agent':'HongKongSandbox/1.0 OSM regional geometry import'})
   with urllib.request.urlopen(req,timeout=150) as response:raw=response.read()
   data=json.loads(raw)
   if 'remark' in data:raise ValueError(data['remark'])
   target.write_bytes(gzip.compress(raw,mtime=0));print(name,len(data['elements']),data['osm3s']['timestamp_osm_base'],flush=True);break
  except Exception as error:
   print(endpoint,error,flush=True)
 else:raise RuntimeError('No complete source response for '+name)
