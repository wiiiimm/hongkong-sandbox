"""Exact nonzero shared-edge topology census; no point-only component glue.

Partial collinear edges may still be real interfaces, but need independent
positive-dimensional intersection proofs. Winding conflicts/nonmanifold edges
are preserved; this is connectivity diagnosis, never closed-solid/root credit.
"""
import hashlib,json,collections,numpy as np

def exact_nonrendering(face):
 ratios=[float(v).as_integer_ratio()for p in face for v in p];power=max(d.bit_length()-1 for _,d in ratios);values=[n<<(power-(d.bit_length()-1))for n,d in ratios];p,q,r=[values[i:i+3]for i in [0,3,6]];u=[q[i]-p[i]for i in range(3)];v=[r[i]-p[i]for i in range(3)];return u[1]*v[2]-u[2]*v[1]==u[2]*v[0]-u[0]*v[2]==u[0]*v[1]-u[1]*v[0]==0

def census(triangles,face_ids):
 t=np.asarray(triangles,float);assert t.ndim==3 and t.shape[1:]==(3,3)and np.isfinite(t).all();ids=list(face_ids);assert ids==sorted(set(ids))and all(type(i)is int and 0<=i<len(t)for i in ids)
 nonrender=[i for i in ids if exact_nonrendering(t[i])];blocked=set(nonrender);render=[i for i in ids if i not in blocked];parent={i:i for i in render};edgefaces=collections.defaultdict(list);zero=[]
 def root(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 def join(a,b):
  x,y=root(a),root(b)
  if x!=y:parent[max(x,y)]=min(x,y)
 for i in render:
  verts=[tuple(p)for p in t[i]]
  for a,b in zip(verts,verts[1:]+verts[:1]):
   if a==b:zero.append(dict(face=i,vertex=a));continue
   key=tuple(sorted([a,b]));edgefaces[key].append((i,1 if a==key[0]else-1))
 for rows in edgefaces.values():
  for i,_ in rows[1:]:join(rows[0][0],i)
 groups=collections.defaultdict(list)
 for i in render:groups[root(i)].append(i)
 inventory=[dict(edge=key,originalFaceIncidences=rows)for key,rows in sorted(edgefaces.items())];canonical=json.dumps(inventory,sort_keys=True,separators=(',',':')).encode();components=sorted(groups.values(),key=lambda g:g[0])
 return dict(contract='exact-original-nonzero-shared-edge-component-census-v2',completeWorldTrianglesSHA256=hashlib.sha256(t.tobytes()).hexdigest(),completeOriginalFaceIds=ids,exactNonrenderingOriginalFaces=nonrender,nonrenderingFacesProvideNoBridge=True,completeRenderableFaceIds=render,sharedEdgeConnectedComponents=components,exactNonzeroEdgeInventorySHA256=hashlib.sha256(canonical).hexdigest(),completeNonzeroEdges=len(edgefaces),boundaryEdges=sum(len(r)==1 for r in edgefaces.values()),nonmanifoldEdges=sum(len(r)>2 for r in edgefaces.values()),twoFaceOrientationConflicts=sum(len(r)==2 and r[0][1]==r[1][1]for r in edgefaces.values()),originalCollapsedEdgeIncidences=zero,pointOnlyComponentGlue=False,closedSolidCertification=False,rootOrContactCredit=False,sourceGeometryChanges=0)
