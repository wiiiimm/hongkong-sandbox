import sys
from pathlib import Path
sys.path.insert(0,'source-scripts/city/government-import')
from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from shapely.geometry import Polygon,box
import shapely
B=ROOT/'docs/astra-city/government-import'; prior=B/'government-xl-orchards-podium-current-checks-v1-20261017'
r=read(prior/'selection.json.gz')['rows'][0]; raw=(ROOT/r['candidate']['path']).read_bytes();assert digest(raw)==r['sourceSHA256']
t=decode_original_world_triangles(raw);p=shapely.union_all(shapely.polygons(t[:,:,[0,2]]));b=r['source']['building'];target=Polygon(b['rings'][0],b['rings'][1:]);missing=target.difference(p)
forms=[]
for f in read(ROOT/'3d-viewer'/r['source']['tile'])['buildings']:
 try:g=Polygon(f['rings'][0],f['rings'][1:]);a=g.intersection(missing).area
 except Exception:continue
 if a>1:forms.append(dict(uid=f['uid'],name=f.get('name'),csuid=f.get('buildingCSUID'),parent=f.get('parent'),base=f.get('base'),top=f.get('topHeightHKPD'),missingIntersectionM2=a))
models=[]
with connect() as c:
 c.execute('SET TRANSACTION READ ONLY')
 rows=c.execute('SELECT DISTINCT r.cache_key,r.result_sha,r.result FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,r['native']['cacheKey'])).fetchall()
 for key,sha,data in rows:
  for m in data['models']:
   bounds=m.get('worldBounds')
   if not bounds:continue
   lo,hi=bounds; a=box(lo[0],lo[2],hi[0],hi[2]).intersection(missing).area
   if a>1:models.append(dict(modelId=m['modelId'],sourceEntry=m.get('sourceEntry'),worldBounds=bounds,triangles=m.get('triangles'),matching=m.get('matching'),asset=m.get('asset'),missingBoundingBoxIntersectionM2=a,cacheKey=key,resultSha=sha))
out=dict(uid=b['uid'],sourceSHA256=r['sourceSHA256'],missingAreaM2=missing.area,missingBounds=list(missing.bounds),forms=sorted(forms,key=lambda f:-f['missingIntersectionM2']),models=sorted(models,key=lambda m:-m['missingBoundingBoxIntersectionM2']),note='Bounding-box intersections nominate sources only, not source identity or geometric coverage acceptance.')
save(Path('/tmp/orchards-missing-source-survey.json'),out)
print('missing',missing.area);print('forms',out['forms']);print('models',[(m['modelId'],m['triangles'],round(m['missingBoundingBoxIntersectionM2'],2),m['matching'])for m in out['models']])
