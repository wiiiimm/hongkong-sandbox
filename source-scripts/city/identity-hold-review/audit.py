"""Read-only exception evidence using retained exact source geometry and footprints."""
import json,pathlib,sys,sqlite3,hashlib
import numpy as np
from shapely.geometry import Polygon,MultiPoint
from shapely import make_valid,union_all
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/identity-hold-review'
sys.path.insert(0,str(ROOT/'docs/astra-city/mui-wo-buildings/review'))
from bake_model_geometry import bake
read=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report_path=ROOT/'docs/astra-city/landmark-preflight/report.json';pre=read(report_path)
c=sqlite3.connect(f'file:{ROOT}/source-scripts/city/building-batch/local/buildings.sqlite?mode=ro',uri=True);c.row_factory=sqlite3.Row;c.execute('PRAGMA query_only=ON')
bs={r['uid']:dict(r) for r in c.execute('select uid,name,csuid,source_base,source_top,structure_type,rings_json,x,z,input_path from buildings where active=1')};c.close()
def shape(b):
 r=json.loads(b['rings_json']);return make_valid(Polygon(r[0],r[1:]))
def intersect(a,b):
 i=a.intersection(b).area;return {'footprintCovered':i/max(b.area,.001),'modelProjectionInsideFootprint':i/max(a.area,.001),'overlapOfSmaller':i/max(min(a.area,b.area),.001),'centroidDistance':a.centroid.distance(b.centroid),'hausdorff':a.hausdorff_distance(b)}
rows=[];hashes={str(report_path.relative_to(ROOT)):sha(report_path)}
for p in pre['parts']:
 if 'exact-reference-identity-or-footprint-mismatch' not in p['classification']:continue
 b=bs[p['uid']];a=p['acquisitionEvidence'];m=a['models'][0];mp=ROOT/m['manifest'];manifest=read(mp);s=next(s for s in manifest['models'] if s['id']==m['modelId']);hashes[str(mp.relative_to(ROOT))]=sha(mp)
 for path,digest in s['sourceHashes'].items():assert sha(mp.parent/path)==digest
 baked=bake(s,mp.parent);positions=np.array(baked['position']).reshape(-1,3);tri=positions.reshape(-1,3,3);hull=MultiPoint(positions[:,[0,2]]).convex_hull
 faces=[Polygon(t[:,[0,2]]) for t in tri];projection=union_all([t for t in faces if t.area>1e-8]);foot=shape(b)
 related=[v for v in bs.values() if v['csuid'] and v['csuid'][:10]==b['csuid'][:10]]
 near=[v for v in bs.values() if v['csuid'] and abs(v['x']-b['x'])<300 and abs(v['z']-b['z'])<300 and projection.intersects(shape(v))]
 levels={}
 for level in [b['source_base']+.5,(b['source_base']+b['source_top'])/2,b['source_top']-1]:
  fs=[Polygon(t[:,[0,2]]) for t in tri if t[:,1].max()>=level];pr=union_all([t for t in fs if t.area>1e-8]);levels[str(round(level,3))]=intersect(pr,foot)
 row={'uid':p['uid'],'name':b['name'],'csuid':b['csuid'],'landmarks':p['landmarkIds'],'modelId':s['id'],'sourceManifest':str(mp.relative_to(ROOT)),'sourceHashes':s['sourceHashes'],'nativeBounds':s['worldBounds'],'nativeTriangles':s['triangles'],'footprintBaseTop':[b['source_base'],b['source_top']],'standardHullMatch':intersect(hull,foot),'actualTriangleProjection':intersect(projection,foot),'projectionArea':projection.area,'footprintArea':foot.area,'aboveElevationProjection':levels,'sameGeoRefRecords':[{k:v[k] for k in ['uid','name','csuid','source_base','source_top','structure_type']}|{'projectionOverlap':intersect(projection,shape(v))} for v in related],'nearbyIntersectedFootprints':[{k:v[k] for k in ['uid','name','csuid','source_base','source_top','structure_type']}|{'projectionOverlap':intersect(projection,shape(v))} for v in near]}
 rows.append(row)
 # SVG inspection is generated from native projected triangles and actual footprint holes.
 lo=np.minimum(np.array(projection.bounds[:2]),np.array(foot.bounds[:2]))-5;hi=np.maximum(np.array(projection.bounds[2:]),np.array(foot.bounds[2:]))+5;size=hi-lo
 def rings_svg(g,colour,opacity):
  result=[]
  for poly in (g.geoms if hasattr(g,'geoms') else [g]):
   if not hasattr(poly,'exterior'):continue
   paths=[]
   for ring in [poly.exterior,*poly.interiors]:paths.append('M '+' L '.join(f'{x:.3f},{z:.3f}' for x,z in ring.coords)+' Z')
   result.append(f'<path d="{" ".join(paths)}" fill="{colour}" fill-opacity="{opacity}" stroke="{colour}" stroke-width=".25" fill-rule="evenodd"/>')
  return ''.join(result)
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{lo[0]} {lo[1]} {size[0]} {size[1]}" width="700" height="700"><rect x="{lo[0]}" y="{lo[1]}" width="{size[0]}" height="{size[1]}" fill="white"/>'+rings_svg(projection,'#246fcb',.4)+rings_svg(foot,'#de3737',.3)+'</svg>'
 (DOC/(p['uid'].replace('/','-').replace(':','-')+'.svg')).write_text(svg)
 print(json.dumps({k:row[k] for k in ['uid','name','standardHullMatch','actualTriangleProjection','footprintBaseTop','nativeBounds']}) )
# The eight non-government entries are OSM components, not eight missing government buildings.
osm=[]
for p in pre['parts']:
 if 'no-government-identity' not in p['classification']:continue
 b=bs[p['uid']];f=shape(b);matches=[]
 for uid in next(l['members'] for l in pre['landmarks'] if l['id']=='tall-the-center'):
  if uid.startswith('landsd/') and uid in bs:
   v=bs[uid];matches.append({'uid':uid,'name':v['name'],'csuid':v['csuid'],'baseTop':[v['source_base'],v['source_top']],'footprintOverlap':intersect(shape(v),f)})
 osm.append({'uid':b['uid'],'name':b['name'],'baseTop':[b['source_base'],b['source_top']],'area':f.area,'sourceInput':b['input_path'],'govComponents':matches})
live=read(DOC/'live-footprints.json');liveChecks=[]
for f in live['features']:
 attrs=f['attributes'];uid='landsd/'+str(attrs['OBJECTID'])+':0';b=bs[uid];rings=[[[x-834500,816500-n]for x,n in ring]for ring in f['geometry']['rings']];actual=make_valid(Polygon(rings[0],rings[1:]));old=shape(b)
 liveChecks.append({'uid':uid,'csuidUnchanged':attrs['BuildingCSUID']==b['csuid'],'baseTopUnchanged':[attrs['BaseHeight'],attrs['TopHeight']]==[b['source_base'],b['source_top']],'footprintHausdorffMetres':old.hausdorff_distance(actual),'intersectionOverLargerArea':old.intersection(actual).area/max(old.area,actual.area)})
output={'issue':'HKS-214','sourcePreflightSHA256':sha(report_path),'inputHashes':hashes,'verticalScale':1,'rows':rows,'nonGovernmentEntries':osm,'currentGovernmentFootprints':liveChecks,'dbWrites':0,'limits':['Projected actual triangle union is identity geometry evidence, not terrain/support proof.','Model GeoRefNo identifies a source reference; full BuildingCSUID/component correspondence must still be judged.','No global conservative matching threshold was relaxed; original caches untouched.']}
(DOC/'audit.json').write_text(json.dumps(output,indent=2,ensure_ascii=False)+'\n')
