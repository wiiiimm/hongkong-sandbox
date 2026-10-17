"""Exact authored panel topology and certified continuous body-distance upper witnesses.
Never interprets a small distance as structural support or changes source geometry.
"""
import json,gzip,struct,numpy as np,shapely
from fractions import Fraction as F
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from original_shell_diagnostic_20261009 import shell_context
from exact_shell_context_accelerated_20261009 import shell_self_intersections
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from xl_source_stream_binding_20261009 import source_stream_binding
BATCH='xl-terrain-recovery-20261009-hsbc-original-panel-context-v1';DOC=ROOT/'docs/astra-city/government-import'/BATCH
GRAPH=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-265848-current-ordinary-support-v1/diagnostic.json.gz'
PHYSICAL=ROOT/'docs/astra-city/government-import/government-xl-terrain-recovery-265848-retained-physical-v5-20261009';GEO=HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def exact_point_triangle_sq(p,t):
 p=tuple(F.from_float(float(x)) for x in p);a,b,c=rational_face(t);u=sub(b,a);v=sub(c,a);w=sub(p,a);uu=dot(u,u);uv=dot(u,v);vv=dot(v,v);du=dot(w,u);dv=dot(w,v);den=uu*vv-uv*uv;candidates=[]
 if den:
  s=(du*vv-dv*uv)/den;q=(dv*uu-du*uv)/den
  if s>=0 and q>=0 and s+q<=1:candidates.append(tuple(a[k]+s*u[k]+q*v[k] for k in range(3)))
 for x,y in [(a,b),(b,c),(c,a)]:
  e=sub(y,x);l=dot(e,e);k=min(F(1),max(F(0),dot(sub(p,x),e)/l)) if l else F(0);candidates.append(tuple(x[j]+k*e[j] for j in range(3)))
 distances=[dot(sub(p,q),sub(p,q)) for q in candidates];i=min(range(len(distances)),key=distances.__getitem__);return distances[i],candidates[i]
def float_distances(p,t):
 a,b,c=t[:,0],t[:,1],t[:,2];u=b-a;v=c-a;w=p-a;uu=np.einsum('ij,ij->i',u,u);uv=np.einsum('ij,ij->i',u,v);vv=np.einsum('ij,ij->i',v,v);du=np.einsum('ij,ij->i',w,u);dv=np.einsum('ij,ij->i',w,v);den=uu*vv-uv*uv;s=np.divide(du*vv-dv*uv,den,out=np.zeros(len(t)),where=den!=0);q=np.divide(dv*uu-du*uv,den,out=np.zeros(len(t)),where=den!=0);closest=a+s[:,None]*u+q[:,None]*v;d=np.einsum('ij,ij->i',p-closest,p-closest);d[(den==0)|(s<0)|(q<0)|(s+q>1)]=np.inf
 for x,y in [(a,b),(b,c),(c,a)]:
  e=y-x;l=np.einsum('ij,ij->i',e,e);k=np.divide(np.einsum('ij,ij->i',p-x,e),l,out=np.zeros(len(t)),where=l!=0);closest=x+np.clip(k,0,1)[:,None]*e;d=np.minimum(d,np.einsum('ij,ij->i',p-closest,p-closest))
 return d

def main():
 assert not DOC.exists();graph=read(GRAPH);g=read(GEO)['rows'][0];row=read(PHYSICAL/'selection.json.gz')['rows'][0];p=np.asarray(g['position']).reshape(-1,3);ids=np.asarray(g['index']).reshape(-1,3);tri=p[ids];asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==g['sourceSHA256']==graph['actors'][0]['sourceSHA256'];assert digest(tri.tobytes())==graph['binding']['completeOriginalWorldTrianglesSHA256']
 component=29;faces=graph['components'][component]['globalOriginalFaces'];assert len(faces)==5;rooted=set(graph['resolvedOriginalComponents']);bodyids=np.array([i for k,c in enumerate(graph['components']) if k in rooted for i in c['globalOriginalFaces']],int);body=tri[bodyids];bounds=tri[faces].min(axis=(0,1)),tri[faces].max(axis=(0,1));nearest=[];continuous=[];interfaces=[]
 for i in faces:
  ds=np.array([float_distances(v,body) for v in tri[i]]);chosen=int(bodyids[np.argmin(ds.max(axis=0))]);exact=[exact_point_triangle_sq(v,tri[chosen]) for v in tri[i]];upper=max(r[0] for r in exact)
  continuous.append({'sourceFace':i,'rootedOriginalBodyFace':chosen,'exactVertexSquaredDistancesM2':[str(r[0]) for r in exact],'exactClosestBodyPoints':[[str(x) for x in r[1]] for r in exact],'exactContinuousSquaredUpperBoundM2':str(upper),'displayContinuousUpperBoundM':float(upper)**.5,'proof':'Distance to a convex finite triangle is convex; maximum over a complete source triangle lies at an original vertex. Every point of this source face is within this exact bound of an already rooted original body face. No tolerance acceptance or load-bearing claim.'})
  for k,v in enumerate(tri[i]):
   j=int(bodyids[np.argmin(ds[k])]);d,q=exact_point_triangle_sq(v,tri[j]);nearest.append({'sourceFace':i,'sourceVertex':k,'rootedOriginalBodyFace':j,'exactSquaredDistanceToSelectedNearestBodyTriangleM2':str(d),'closestOriginalBodyPoint':list(map(str,q)),'completeRootedBodyTriangleFloatSearch':len(body),'nearestSearchNotExactGlobalCertification':True})
  t=tri[i];candidates=np.flatnonzero(np.all(tri.max(axis=1)>=t.min(axis=0),axis=1)&np.all(tri.min(axis=1)<=t.max(axis=0),axis=1));
  for j in candidates:
   if j in faces or not np.any(np.cross(tri[j,1]-tri[j,0],tri[j,2]-tri[j,0])):continue
   points=intersection_points(rational_face(t),rational_face(tri[j]))
   if points:interfaces.append({'originalFaces':[i,int(j)],'exactIntersectionPoints':[[str(x) for x in q] for q in sorted(points)],'positiveDimension':len(points)>=2,'sharedRuntimeVertexIndices':sorted(map(int,set(ids[i])&set(ids[j])))})
 data=gzip.decompress(raw);size,kind=struct.unpack_from('<II',data,12);packed=json.loads(data[20:20+size]);refs=[ref(p) for p in [Path(__file__),GRAPH,GEO,PHYSICAL/'result.json',asset,HERE/'original_shell_diagnostic_20261009.py',HERE/'exact_shell_context_accelerated_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'xl_source_stream_binding_20261009.py']]
 result={'uid':g['uid'],'sourceSHA256':g['sourceSHA256'],'component':component,'all5OriginalFaces':faces,'completeOriginalVertices':tri[faces].tolist(),'completeRuntimeVertexIndices':ids[faces].tolist(),'sourceStreamBinding':source_stream_binding(raw),'originalNodePrimitiveMembership':{'nodes':packed['nodes'],'meshes':packed['meshes'],'materials':packed.get('materials',[])},'originalShell':shell_context(tri,faces),'originalSelfIntersections':shell_self_intersections(tri[faces]),'everyOtherOriginalFaceExactInterface':interfaces,'nearestOriginalBodyVertexWitnesses':nearest,'certifiedContinuousBodyDistanceUpperWitnesses':continuous,'rawComponentGroundFailure':graph['ordinaryRootProofs'][component],'evidenceRefs':refs,'structuralSupportAccepted':False,'authorisedVisualDetailRole':False,'installationApproved':False,'modelGeometryChanges':0,'scriptExternalAICalls':0}
 result=json.loads(json.dumps(result));save(DOC/'diagnostic.json.gz',result);print(json.dumps({'faces':faces,'interfaces':len(interfaces),'continuumUpperM':[r['displayContinuousUpperBoundM'] for r in continuous],'sourceVisualRoleNotYetAuthorised':True}),flush=True)
if __name__=='__main__':main()
