"""Complete unchanged source versus all current forms in its full projection bounds."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ets-combined-identity-context-v1-20261015';DOC=BASE/BATCH
OWN={'landsd/323703:0'}
def main():
 assert not DOC.exists();r=read(BASE/'government-xl-ets-current-placement-metrics-v1-20261015/selection.json.gz')['rows'][0];asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256']
 original=decode_original_world_triangles(asset.read_bytes());a=read(BASE/'government-xl-ets-actual-render-attributes-v2-20261015/attributes.json.gz')['rows'][0];assert a['sourceSHA256']==r['sourceSHA256'];ix=np.asarray(a['completeOriginalIndex']).reshape(-1,3)
 worlds={'original':original}
 for mode,key in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]=np.asarray(a[key]).reshape(-1,3)[ix]
 bounds=np.concatenate(list(worlds.values())).reshape(-1,3);lo=bounds.min(axis=0);hi=bounds.max(axis=0);query=shapely.box(lo[0]-1,lo[2]-1,hi[0]+1,hi[2]+1)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';pins={str(manifest.relative_to(ROOT)):digest(manifest.read_bytes())};forms=[]
 final=module('ets_identity_shapes',HERE/'xl-final-script-pass.py')
 for tile in read(manifest)['tiles']:
  if not shapely.box(*tile['bounds']).intersects(query):continue
  p=ROOT/'3d-viewer'/tile['url'];pins[str(p.relative_to(ROOT))]=digest(p.read_bytes())
  for b in read(p)['buildings']:
   if not b.get('rings'):continue
   poly=final.form_polygon(b)
   if poly.intersects(query):forms.append((b,poly,tile['url']))
 assert {b['uid'] for b,p,t in forms if b['uid'] in OWN}==OWN
 own=shapely.union_all([p for b,p,t in forms if b['uid'] in OWN]);rows=[]
 for mode,tri in worlds.items():
  projection=final.projection(tri);excess=projection.difference(own);coords=shapely.get_coordinates(excess)
  overlaps=[{'uid':b['uid'],'name':b.get('name'),'areaM2':float(projection.intersection(p).area),'targetCoverage':float(projection.intersection(p).area/p.area),'centroidDistanceM':float(projection.centroid.distance(p.centroid))}for b,p,t in forms]
  rows.append({'mode':mode,'completeFaces':len(tri),'sourceAreaM2':projection.area,'ownUnionAreaM2':own.area,'excessAreaM2':excess.area,'maximumExcessDistanceM':float(shapely.distance(shapely.points(coords),own).max()) if len(coords) else 0,'overlaps':overlaps,'unrelatedOverlapM2':sum(x['areaM2']for x in overlaps if x['uid']not in OWN)})
 DOC.mkdir();save(DOC/'context.json',{'sourceSHA256':r['sourceSHA256'],'modelId':r['candidate']['entry']['modelId'],'rows':rows,'currentPins':pins,'forms':[{'building':b,'tile':t}for b,p,t in forms],'identityAccepted':False,'legacyGeoRefEquality':False,'installationApproved':False})
 refs=[Path(__file__),asset,HERE/'xl-final-script-pass.py',BASE/'government-xl-ets-actual-render-attributes-v2-20261015/attributes.json.gz',*[ROOT/p for p in pins]]
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
 module('freeze_ets_identity_context',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-four-world-current-combined-identity-context-v1',refs,{'uids':sorted(OWN),'sourceSHA256':r['sourceSHA256'],'rows':rows,'fullAcceptance':False,'installed':False})
 print([{k:v for k,v in x.items() if k!='overlaps'}for x in rows],flush=True)
if __name__=='__main__':main()
