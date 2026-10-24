"""Independently read back complete four-world finite-path evidence; no approval."""
from pathlib import Path
from fractions import Fraction
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from pool_incident_wall_contacts_v1_20261017 import closest
BASE=ROOT/'docs/astra-city/government-import'
def main():
 batch='government-xl-fu-tor-loy-four-world-path-readback-v1-20261023';out=BASE/batch;assert not out.exists()
 refs=[Path(__file__)];cache={}
 def take(name,path):
  if name not in cache:cache[name]=authenticate(BASE/name)[1];refs.append(BASE/name/'result.json')
  assert digest(path.read_bytes())==cache[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 cap='government-xl-fu-tor-loy-five-originals-current-v1-20261023-runtime'
 sources={r['uid']:r for r in take(cap,BASE/cap/'selection.json.gz')['rows']}
 attrs='government-xl-fu-tor-loy-five-originals-attributes-v1-20261023'
 attributes={r['uid']:r for r in take(attrs,BASE/attrs/'attributes.json.gz')['rows']}
 worlds={}
 for uid,r in sources.items():
  asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];refs.append(asset)
  g=attributes[uid];index=np.asarray(g['completeOriginalIndex']).reshape(-1,3)
  worlds[uid]={'original':decode_original_world_triangles(asset.read_bytes())}
  for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[uid][mode]=np.asarray(g[field],dtype='<f8').reshape(-1,3)[index]
 rows=[]
 for number in ['231442','232818','233770','233775']:
  uid='landsd/'+number+':0';support='landsd/228219:0'
  name=f'government-xl-fu-tor-loy-{number}-four-world-contact-paths-v1-20261023'
  checks=f'government-xl-fu-tor-loy-{number}-four-world-support-v1-20261023'
  strict=take(checks,BASE/checks/'summary.json')
  for mode in ['original','literal','leftF32','balancedF32']:
   p=take(name,BASE/name/(mode+'.json.gz'));t=worlds[uid][mode];podium=worlds[support][mode]
   assert digest(t.tobytes())==p['sourceWorldSHA256'] and digest(podium.tobytes())==p['supportWorldSHA256']
   check=next(r for r in strict['rows']if r['mode']==mode)['support']
   assert [r['witness']for r in p['rows']]==check['unresolved']
   assert p['targets']==p['verifiedPaths']==len(p['rows']) and p['remaining']==0
   worst=0.;faces=set()
   for row in p['rows']:
    v=row['verifiedPath'];assert v;ids=v['faces'];points=np.asarray(v['continuousPath'])
    assert len(points)==len(ids)+1 and ids[0]in row['incidentFaces']
    assert np.array_equal(points[0],row['witness']['position'])
    c=v['contact'];assert c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2 and c['dimension']>0 and ids[-1]==c['sourceFaceA']
    end=np.array([[float(Fraction(q))for q in point]for point in c['exactPoints']]).mean(0)
    assert np.array_equal(end,points[-1]);ceiling=max(points[0,1],points[-1,1]);assert points[:,1].max()<=ceiling+1e-9
    for i,f in enumerate(ids):
     assert np.linalg.norm(np.cross(t[f,1]-t[f,0],t[f,2]-t[f,0]))>0;faces.add(f)
     for q in points[i:i+2]:worst=max(worst,float(np.linalg.norm(closest(q,t[f])-q)))
    worst=max(worst,float(np.linalg.norm(closest(end,podium[c['sourceFaceB']])-end)))
    for i,(f,g)in enumerate(zip(ids,ids[1:])):
     shared=set(map(tuple,t[f]))&set(map(tuple,t[g]));assert len(shared)>=2
     q=points[i+1];assert any(np.linalg.norm(closest(q,np.array([a,b,b]))-q)<=.001 for a in shared for b in shared if a!=b)
   assert worst<=.001
   rows.append(dict(uid=uid,mode=mode,paths=len(p['rows']),pathFaces=len(faces),maximumResidualM=worst,degeneratePathFaces=0));print(rows[-1],flush=True)
 result=dict(uids=sorted(sources),rows=rows,verifiedWitnessPaths=sum(r['paths']for r in rows),sourceGeometryChanges=0,installationApproved=False,qualification='Independent input-hash and path readback. Every saved unresolved witness covered once; nondegenerate original faces, finite positive-dimensional original contact endpoints and exact shared-edge transitions. Physical architecture, component roles and installation remain unapproved.')
 save(out/'summary.json',result);refs += [HERE/'pool_incident_wall_contacts_v1_20261017.py',HERE/'exact_packed_world_geometry_20261009.py']
 module('fu_tor_path_readback_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'independent-four-world-original-path-readback',refs,result)
if __name__=='__main__':main()
