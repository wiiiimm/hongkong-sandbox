"""Measure Block 1 footprint differences against the two unchanged original components."""
from pathlib import Path
import numpy as np,shapely
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ronsdale-tower1-assembly-coverage-v1-20261022';DOC=BASE/BATCH
UID='landsd/256898:0';POD='landsd/233771:0'
def main():
 assert not DOC.exists();refs=[Path(__file__)];cache={}
 def take(n,p):
  if n not in cache:cache[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
  assert digest(p.read_bytes())==cache[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 n='government-xl-scripted-source-inventory-20261022';inventory=take(n,BASE/n/'inventory.json');row=next(r for r in inventory['rows']if r['uid']==UID);asset=ROOT/row['assetPath'];assert digest(asset.read_bytes())==row['indexedSourceSHA256'];refs.append(asset);tower=decode_original_world_triangles(asset.read_bytes())
 n='government-xl-ronsdale-inset-runtime-v2-20261022';r=take(n,HERE/'local'/n/'runtime-geometry.json.gz')['rows'][0];assert r['uid']==POD;podium=np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)]
 n='government-xl-ronsdale-regional-scope-v1-20261022';forms=take(n,BASE/n/'form-obligations.json.gz');b=next(x for x in forms if x['uid']==UID);target=shapely.Polygon(b['rings'][0],b['rings'][1:])
 identity=take('government-xl-remaining-forty-original-identity-v2-20261021',BASE/'government-xl-remaining-forty-original-identity-v2-20261021/256898:0/identity.json');assert identity['sourceSHA256']==row['indexedSourceSHA256'];assert identity['reasons']==['fresh-current-spatial-bound:targetCoveredBySourceProjection','full-source-target-coverage']
 def projection(tri):return shapely.union_all([shapely.MultiPoint(f[:,[0,2]]).convex_hull for f in tri])
 tp=projection(tower);pp=projection(podium);missing=target.difference(tp);residual=missing.difference(pp)
 result=dict(uids=[UID,POD],uid=UID,towerSourceSHA256=row['indexedSourceSHA256'],podiumSourceSHA256=r['sourceSHA256'],targetAreaM2=target.area,towerCoveredFraction=target.intersection(tp).area/target.area,missingTowerProjectionAreaM2=missing.area,missingCoveredByOriginalPodiumM2=missing.intersection(pp).area,remainingMissingAreaM2=residual.area,compoundCoveredFraction=target.intersection(tp.union(pp)).area/target.area,sourceGeometryChanges=0,identityReviewApproved=False,installationApproved=False,qualification='Two original component projection accounting only; does not prove the missing part belongs to the podium or transfer identity approval.')
 save(DOC/'coverage.json',dict(**result,targetWKT=target.wkt,towerProjectionWKT=tp.wkt,podiumProjectionWKT=pp.wkt,missingWKT=missing.wkt,residualWKT=residual.wkt))
 fig,ax=plt.subplots(figsize=(9,9))
 for geom,color,label in [(target,'black','Recorded Block 1 footprint'),(tp,'royalblue','Original Block 1 source projection'),(pp,'grey','Original podium source projection'),(missing,'darkorange','Missing from tower projection')]:
  labelled=False
  for part in shapely.get_parts(geom):
   if part.geom_type=='Polygon':
    xy=np.asarray(part.exterior.coords);ax.plot(xy[:,0],xy[:,1],color=color,label=label if not labelled else None);labelled=True
 ax.set_aspect('equal');ax.invert_yaxis();ax.legend();ax.set_title('Unchanged original Ronsdale components and recorded Block 1 footprint');fig.tight_layout();fig.savefig(DOC/'coverage.png',dpi=150);plt.close(fig)
 refs.extend([HERE/'exact_packed_world_geometry_20261009.py']);module('ronsdale_coverage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-two-component-footprint-coverage-context',refs,result);print(result,flush=True)
if __name__=='__main__':main()
