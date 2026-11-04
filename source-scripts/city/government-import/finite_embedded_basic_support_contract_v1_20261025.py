"""Separate evidence contract for a shallow embedded underside with exposed walls.

The canonical strict result stays false. Existing0.5m embedding/1mm finite-path
limits are unchanged. Source identity, current BASIC binding, native contacts,
visual review and publication remain separate requirements.
"""
import hashlib
from fractions import Fraction
import numpy as np
from pool_incident_wall_contacts_v1_20261017 import closest
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts


def verify_mode(source,support,canonical,detail):
 t=np.asarray(source,dtype='<f8').reshape(-1,3,3);p=np.asarray(support,dtype='<f8').reshape(-1,3,3)
 assert len(t)and len(p)and np.isfinite(t).all()and np.isfinite(p).all()
 assert detail['sourceWorldSHA256']==hashlib.sha256(t.tobytes()).hexdigest()
 assert detail['supportWorldSHA256']==hashlib.sha256(p.tobytes()).hexdigest()
 assert detail['sourceFaces']==len(t)and detail['supportFaces']==len(p)
 assert canonical['passed']is False and detail['strictInterfacePassed']is False
 assert canonical['maximumEmbeddingM']==.5 and canonical['strictContacts']==0 and canonical['wallIntersections']>0
 unresolved=canonical['unresolved'];assert unresolved
 assert canonical['samples']==canonical['wallIntersections']+len(unresolved)
 assert detail['targets']==detail['verifiedPaths']==len(unresolved)and detail['remaining']==0
 assert len(detail['rows'])==len(unresolved)
 assert [r['witness']for r in detail['rows']]==unresolved
 floor=float(t[:,:,1].min());roof=float(p[:,:,1].max())
 assert floor<roof<float(t[:,:,1].max())and roof-floor<=.5
 checked=[]
 for raw,row in zip(unresolved,detail['rows']):
  assert raw['reason']=='support-above-rim'and -.5<=raw['gap']<0 and raw['position'][1]==floor
  v=row['verifiedPath'];assert v is not None
  ids=v['faces'];points=np.asarray(v['continuousPath'],dtype='<f8');assert ids and len(points)==len(ids)+1 and np.isfinite(points).all()
  assert np.array_equal(points[0],np.asarray(raw['position']))
  assert all(isinstance(i,int)and 0<=i<len(t)for i in ids)
  for i,face in enumerate(ids):
   assert np.linalg.norm(np.cross(t[face,1]-t[face,0],t[face,2]-t[face,0]))>0
   for q in points[i:i+2]:assert np.linalg.norm(closest(q,t[face])-q)<=.001
  for x,y in zip(ids,ids[1:]):
   shared=set(map(tuple,t[x]))&set(map(tuple,t[y]));assert len(shared)>=2
  contact=v['contact'];assert contact['sourceFaceA']==ids[-1]
  assert contact['sourcePrimitiveDimensionA']==contact['sourcePrimitiveDimensionB']==2 and contact['dimension']>0
  b=contact['sourceFaceB'];assert isinstance(b,int)and 0<=b<len(p)
  terminal=t[ids[-1]];normal=np.cross(terminal[1]-terminal[0],terminal[2]-terminal[0])
  assert normal[1]==0 and terminal[:,1].min()<roof<terminal[:,1].max()
  assert np.all(p[b,:,1]==roof)and points[-1,1]==roof
  replay=exact_finite_contacts(t,[ids[-1]],p,[b]);assert replay['allPairsExamined']and contact in replay['contacts']
  endpoint=np.asarray([[float(Fraction(z))for z in q]for q in contact['exactPoints']]).mean(0)
  assert np.linalg.norm(endpoint-points[-1])<=.001
  maximum=float(points[:,1].max());assert maximum==v['maximumPathHeightM']and maximum<=v['endpointHeightCeilingM']and maximum-floor<=.5
  assert v['maximumResidualM']<=.001 and v['withinEndpointHeight']
  checked.append(dict(sourceWallFace=ids[-1],supportRoofFace=b,pathFaces=len(ids),riseM=maximum-floor))
 return dict(contract='finite-shallow-embedded-underside-to-exposed-source-wall-v1',strictCanonicalPassed=False,targets=len(unresolved),verifiedPaths=len(checked),embeddingM=roof-floor,sourceFaces=len(t),supportFaces=len(p),paths=checked)
