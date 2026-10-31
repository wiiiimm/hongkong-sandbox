"""Source terrain core with exact finite clips onto actual current parent planes.

This constructs terrain candidates only. It cannot grant surface, support,
actor, runtime or publication approval. It never accepts a building mesh.
"""
from fractions import Fraction
import numpy as np,shapely
from rendered_patch_sampler import RenderedPatchSampler
from native_parent_child_flat_composition_20261010 import faces
def rational(p):return tuple(Fraction.from_float(float(v)) for v in p)
def clip(poly,value):
 if not poly:return []
 out=[]
 for p,q in zip(poly,poly[1:]+poly[:1]):
  a,b=value(p),value(q)
  if a>=0:out.append(p)
  if (a>=0)!=(b>=0):
   t=a/(a-b);out.append(tuple(p[k]+t*(q[k]-p[k]) for k in range(3)))
 clean=[]
 for p in out:
  if not clean or clean[-1]!=p:clean.append(p)
 if len(clean)>1 and clean[0]==clean[-1]:clean.pop()
 return clean
def rectangle(poly,bb):
 for axis,v,sign in [(0,bb[0],1),(2,bb[1],1),(0,bb[2],-1),(2,bb[3],-1)]:
  v=Fraction.from_float(float(v));poly=clip(poly,lambda p,axis=axis,v=v,sign=sign:sign*(p[axis]-v))
 return poly
def cross(a,b,c):return (b[0]-a[0])*(c[2]-a[2])-(b[2]-a[2])*(c[0]-a[0])
def triangle_clip(poly,triangle):
 t=[rational(p) for p in triangle]
 if cross(*t)<0:t.reverse()
 if cross(*t)==0:return []
 for a,b in zip(t,t[1:]+t[:1]):poly=clip(poly,lambda p,a=a,b=b:cross(a,b,p))
 return poly
def parent_plane_height(point,triangle):
 t=[rational(p) for p in triangle];den=cross(*t)
 assert den!=0,"Verticalfacetcannotbeheightplane"
 weights=[cross(point,t[1],t[2])/den,cross(t[0],point,t[2])/den,cross(t[0],t[1],point)/den]
 return sum(w*p[1] for w,p in zip(weights,t))
def nondegenerate(t):
 a,b,c=t;u=[b[k]-a[k] for k in range(3)];v=[c[k]-a[k] for k in range(3)]
 return any([u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]])
def height_facet_indices(triangles):
 triangles=np.asarray(triangles,float)
 if not np.isfinite(triangles).all():raise ValueError("Nonfinite parent surface")
 return np.asarray([i for i,t in enumerate(triangles) if cross(*[rational(p) for p in t])!=0],dtype=int)
def transition(native,parent,bb,grid_sampler):
 native=np.asarray(native,float)
 if not np.isfinite(native).all() or not np.isfinite(bb).all():raise ValueError("Nonfinite source terrain or bounds")
 parent_faces=faces(parent);normal=np.cross(parent_faces[:,1]-parent_faces[:,0],parent_faces[:,2]-parent_faces[:,0]);parent_surface=parent_faces[height_facet_indices(parent_faces)];polys=shapely.polygons(parent_surface[:,:,[0,2]]);tree=shapely.STRtree(polys);sampler=RenderedPatchSampler(parent,grid_sampler,grid_sampler);core=[bb[0]+10,bb[1]+10,bb[2]-10,bb[3]-10];assert core[0]<core[2] and core[1]<core[3]
 regions=[(core,False),([bb[0],bb[1],bb[2],core[1]],True),([bb[0],core[3],bb[2],bb[3]],True),([bb[0],core[1],core[0],core[3]],True),([core[2],core[1],bb[2],core[3]],True)];output=[];records=[];degenerate=[];clip_pairs=0
 for source_index,face in enumerate(native):
  original=[rational(p) for p in face]
  if not nondegenerate(original):degenerate.append(source_index)
  start=len(output)
  for region,is_transition in regions:
   poly=rectangle(original,region)
   if len(poly)<3:continue
   if is_transition:
    v=np.asarray(poly,float)[:,[0,2]];lo=np.nextafter(v.min(0),-np.inf);hi=np.nextafter(v.max(0),np.inf);candidates=sorted(map(int,tree.query(shapely.box(*lo,*hi))));groups=[]
    for i in candidates:
     clipped=triangle_clip(poly,parent_surface[i]);clip_pairs+=1
     if len(clipped)>=3:groups.append((clipped,parent_surface[i]))
   else:groups=[(poly,None)]
   for group,parent_plane in groups:
    vertices=[]
    for p in group:
     v=np.asarray(p,float)
     if is_transition:
      alpha=max(0,min(1,min(v[0]-bb[0],bb[2]-v[0],v[2]-bb[1],bb[3]-v[2])/10));v[1]=v[1]*alpha+float(parent_plane_height(p,parent_plane))*(1-alpha)
     vertices.append(v)
    for j in range(1,len(vertices)-1):
     exact_face=[group[0],group[j],group[j+1]]
     if nondegenerate(exact_face):output.append([vertices[0],vertices[j],vertices[j+1]])
  records.append({'originalSourceTerrainFace':source_index,'outputFaceRange':[start,len(output)],'originalExactlyDegenerate':source_index in degenerate})
 out=np.asarray(output,float).astype(np.float32).astype(float);assert np.isfinite(out).all();return out,{'completeSourceTerrainFaces':len(native),'actualParentFacets':len(parent_faces),'actualParentHeightFacets':len(parent_surface),'heightFacetClassification':'exact-dyadic-nonzero-projected-area; no tolerance','completeOriginalSourceFaceDispositions':records,'originalDegenerateSourceTerrainFaceIds':degenerate,'childFacets':len(out),'finiteParentClipPairs':clip_pairs,'core':core,'bounds':bb,'sourceClipArithmetic':'exact-Fraction finite plane/rectangle intersections; no area/edge epsilon omission','transitionHeightSource':'each exact actual current native Float32 parent affine facet separately; runtime upper-envelope retains all overlapping branches; no vertex-highest branch splicing','governmentBuildingGeometryChanges':0,'physicalAccepted':False,'qualification':'New source-terrain candidate. Core source planes remain original; transition clips use actual parent finite facets rather than coarse grid triangles. Float32 child surface/seam/full coverage/current actor checks remain independently mandatory.'}
