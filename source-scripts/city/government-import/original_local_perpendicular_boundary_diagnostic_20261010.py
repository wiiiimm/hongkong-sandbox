"""Enumerate finite ORIGINAL host planes for every authored boundary loop.

Diagnosis only. An opposite facade is a separate original plane, not the upper
envelope of the local mounting surface. Every candidate plane is enumerated;
every original loop edge must be covered continuously in the unchanged .1m
coordinate band. No geometry, solid, visual-role or support certification.
"""
from collections import defaultdict
from fractions import Fraction as F
import hashlib
import numpy as np
from exact_original_segment_surface_contact_band_20261009 import verify_contact_segment
from exact_original_perpendicular_edge_facet_band_20261010 import verify as perpendicular

def _plane(face):
 a,b,c=[tuple(F(float(v)) for v in p) for p in face]
 u=tuple(b[i]-a[i] for i in range(3));v=tuple(c[i]-a[i] for i in range(3))
 n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
 if not any(n):return None
 coeff=(*n,-sum(n[i]*a[i] for i in range(3)));scale=next(x for x in n if x)
 return tuple(x/scale for x in coeff)

def prepare_hosts(triangles,rooted_faces):
 tri=np.asarray(triangles,float);assert tri.ndim==3 and tri.shape[1:]==(3,3) and np.isfinite(tri).all()
 ids=list(rooted_faces);assert ids and len(ids)==len(set(ids)) and all(type(i)is int and 0<=i<len(tri) for i in ids)
 groups=defaultdict(list)
 for i in ids:
  plane=_plane(tri[i])
  if plane is not None:groups[plane].append(i)
 return dict(triangles=tri,rootedFaces=ids,planes=groups,worldSHA256=hashlib.sha256(tri.tobytes()).hexdigest())

def diagnose(prepared,component_faces):
 tri=prepared['triangles'];ids=list(component_faces);assert ids and len(ids)==len(set(ids)) and all(type(i)is int and 0<=i<len(tri) for i in ids) and not set(ids)&set(prepared['rootedFaces'])
 edges=defaultdict(list);reasons=[]
 for i in ids:
  if _plane(tri[i]) is None:reasons.append('degenerate-original-detail')
  vs=list(map(tuple,tri[i]))
  for a,b in zip(vs,vs[1:]+vs[:1]):edges[tuple(sorted((a,b)))].append((i,a,b))
 boundary=[]
 for inc in edges.values():
  if len(inc)==1:boundary.append(inc[0])
  elif len(inc)!=2 or inc[0][1:]!=inc[1][1:][::-1]:reasons.append('nonmanifold-or-inconsistent-original-winding')
 outgoing=defaultdict(list);incoming=defaultdict(list)
 for i,a,b in boundary:outgoing[a].append((i,a,b));incoming[b].append(a)
 if not boundary:reasons.append('no-authored-opening')
 if set(outgoing)!=set(incoming) or any(len(outgoing[v])!=1 or len(incoming[v])!=1 for v in set(outgoing)|set(incoming)):reasons.append('original-boundary-is-not-directed-closed-loops')
 loops=[]
 if not reasons:
  unseen=set(outgoing)
  while unseen:
   start=min(unseen);v=start;loop=[]
   while True:
    assert v in unseen,'Original loop repeats a vertex';unseen.remove(v)
    edge=outgoing[v][0];loop.append(edge);v=edge[2]
    if v==start:break
   loops.append(loop)
 results=[];limit=F(.1)
 for loop in loops:
  normal=np.sum([np.cross(a,b) for _,a,b in loop],axis=0);ln=float(np.linalg.norm(normal));axis=int(np.argmax(np.abs(normal))) if ln else 0
  row=dict(completeOriginalBoundaryEdges=[dict(sourceFace=i,vertices=[list(a),list(b)]) for i,a,b in loop],enumeratedLocalHostPlanes=[],passed=False)
  if not ln or axis==1 or abs(normal[1])>.25*ln:
   row['reason']='opening-is-not-vertical-facade';results.append(row);continue
  surfaces=tri[prepared["rootedFaces"]];bands=[]
  for i,a,b in loop:
   band=perpendicular([a,b],surfaces);band["allFiniteOriginalFacetIntervals"]=[{**r,"originalSourceFace":prepared["rootedFaces"][r["originalSurfaceFace"]]} for r in band["allFiniteOriginalFacetIntervals"]];bands.append(dict(originalBoundaryFace=i,originalBoundaryEdge=[list(a),list(b)],band=band))
  row["everyOriginalBoundaryEdgePerpendicularBand"]=bands;row["passed"]=all(x["band"]["verifiedCompleteOriginalEdgePerpendicularBand"] for x in bands);results.append(row)
 if not all(x['passed'] for x in results) or not results:reasons.append('complete-original-loops-have-no-finite-local-host-plane')
 return dict(contract='complete-original-local-finite-host-perpendicular-boundary-diagnostic-v1',completeOriginalWorldTrianglesSHA256=prepared['worldSHA256'],completeOriginalFaces=ids,completeRootedOriginalScopeFaces=prepared['rootedFaces'],completeOriginalDirectedBoundaryEdges=[dict(sourceFace=i,vertices=[list(a),list(b)]) for i,a,b in boundary],completeOriginalLoops=results,sourceOnlyBoundaryBandPassed=not reasons,reasons=sorted(set(reasons)),strictBandM=.1,sourceGeometryChanges=0,visualRoleAccepted=False,structuralRootCredit=False,installationApproved=False)
