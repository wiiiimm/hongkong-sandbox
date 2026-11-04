"""Bind literal loader streams; independently measure all four full mesh pairs."""
import hashlib,importlib.util,json
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from one_peking_installed_hullett_finite_silhouette_identity_20261010 import OWN,FOREIGN,polygon,provider_polygon
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-one-peking-hullett-complete-literal-silhouette-check-v1-20261010';DOC=BASE/BATCH
CONTEXT=BASE/'government-xl-one-peking-hullett-complete-original-boundary-context-v1-20261010'
LITERAL=BASE/'government-xl-one-peking-hullett-literal-production-geometry-v1-20261010'
PRIMARY=BASE/'government-xl-one-peking-hullett-three-exact-original-primary-context-v2-20261010'
def sha(b):return hashlib.sha256(b).hexdigest()
def projection(a):return shapely.union_all(shapely.polygons(a[:,:,[0,2]]))
def main():
 assert not DOC.exists()
 c=read(CONTEXT/'diagnostic.json.gz');literal=read(LITERAL/'diagnostic.json.gz');primary=read(PRIMARY/'diagnostic.json.gz')
 for p,h in literal['inputHashes'].items():assert sha((ROOT/p).read_bytes())==h,p
 rows={r['uid']:r for r in c['sources']};actual={r['uid']:r for r in literal['rows']}
 assert set(rows)==set(actual) and len(rows)==3
 streams={};refs=[Path(__file__),HERE/'xl-one-peking-hullett-literal-production-geometry-v1-20261010.mjs',LITERAL/'diagnostic.json.gz',CONTEXT/'diagnostic.json.gz',CONTEXT/'result.json',PRIMARY/'result.json',PRIMARY/'diagnostic.json.gz',HERE/'one_peking_installed_hullett_finite_silhouette_identity_20261010.py']
 for uid,r in rows.items():
  path=ROOT/r['source']['path'];assert sha(path.read_bytes())==r['source']['sha256'];refs.append(path)
  a=actual[uid];assert a['loaderPassed'] and a['sourceSHA256']==r['source']['sha256']
  pos=np.asarray(a['position'],dtype='<f8').reshape((-1,3));index=np.asarray(a['index'],dtype=np.int64).reshape((-1,3));assert np.isfinite(pos).all() and index.min()>=0 and index.max()<len(pos)
  rendered=pos[index];original=decode_original_world_triangles(path.read_bytes());assert rendered.shape==original.shape==(r['completeFaces'],3,3)
  assert sha(original.tobytes())==r['worldTrianglesSHA256']
  streams[uid]={'original':original,'literal':rendered}
 forms=[r['building'] for r in c['completeCurrentForms']];by={b['uid']:b for b in forms};assert len(by)==5
 own_primary=next(r['freshPrimary'] for r in primary['rows'] if r['uid']==OWN)
 targets={'current':polygon(by[OWN]['rings']),'provider':provider_polygon(own_primary)}
 measurements=[]
 for own_kind,own in streams[OWN].items():
  own_projection=projection(own)
  for foreign_kind,foreign in streams[FOREIGN].items():
   foreign_projection=projection(foreign)
   for target_kind,target in targets.items():
    excess=own_projection.difference(target)
    every_other=[excess.intersection(polygon(b['rings'])) for b in forms if b['uid'] not in [OWN,FOREIGN]]
    effective=excess.intersection(foreign_projection)
    total=shapely.union_all([effective,*every_other])
    assert total.area<=1,(own_kind,foreign_kind,target_kind,total.area)
    measurements.append(dict(ownGeometry=own_kind,foreignGeometry=foreign_kind,target=target_kind,rawBasicForeignProxyExcessM2=excess.intersection(polygon(by[FOREIGN]['rings'])).area,completeActualForeignExcessM2=effective.area,allForeignEffectiveExcessM2=total.area,unchangedForeignLimitM2=1))
 bindings={uid:{kind:dict(completeFaces=len(a),worldTrianglesSHA256=sha(np.asarray(a,dtype='<f8').tobytes())) for kind,a in pair.items()} for uid,pair in streams.items()}
 save(DOC/'diagnostic.json.gz',dict(uids=list(rows),completeGeometryBindings=bindings,measurements=measurements,allEightSourceLiteralTargetCombinationsPassed=True,historicalManifestSHA256=c['capturedManifestSHA256'],currentManifestAcceptanceClaimed=False,identityAccepted=False,physicalAccepted=False,collisionExemption=False,sourceGeometryChanges=0))
 s=importlib.util.spec_from_file_location('literal_peking_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 refs.extend(ROOT/p for p in literal['inputHashes'])
 m.freeze(BATCH,'complete-original-and-literal-installed-foreign-silhouette-independent-source-only-check-v1',refs,dict(uids=list(rows),completeFaces=sum(r['completeFaces'] for r in rows.values()),allEightCombinationsPassed=True,maxAllForeignEffectiveExcessM2=max(r['allForeignEffectiveExcessM2'] for r in measurements),ordinaryForeignLimitM2=1,currentManifestAcceptanceClaimed=False,identityAccepted=False,physicalAccepted=False,collisionExemption=False,qualification='Independent complete literal production-loader foreign geometry, not source-to-runtime tolerance credit. Every other form remains foreign. Current binding and all physical gates still required.'))
 print(json.dumps({'bindings':bindings,'measurements':measurements}),flush=True)
if __name__=='__main__':main()
