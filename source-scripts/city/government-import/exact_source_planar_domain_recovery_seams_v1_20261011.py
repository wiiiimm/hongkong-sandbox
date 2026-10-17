"""Exact source-planar clipping and 3D retained-edge seam rejection.
No adjustment, tolerance, fabricated walls or acceptance credit.
"""
from fractions import Fraction as F
import numpy as np
from exact_original_projection_coverage_v2_20261010 import point,clip,clean,signed_area,cross,subtract

def projected(face):return [point(p)for p in np.asarray(face)[:,[0,2]]]
def oriented(poly):return list(reversed(poly))if signed_area(poly)<0 else poly

def source_height(face,p):
 x=[point(v)for v in np.asarray(face)[:,[0,2]]];y=[F(float(v))for v in np.asarray(face)[:,1]];den=cross(x[0],x[1],x[2]);assert den!=0,'Projected source is degenerate'
 return (cross(x[1],x[2],p)*y[0]+cross(x[2],x[0],p)*y[1]+cross(x[0],x[1],p)*y[2])/den

def overlap_interval(a,b,c,d):
 assert a!=b,'Collapsed boundary edge'
 if cross(a,b,c)!=0 or cross(a,b,d)!=0:return None
 k=0 if b[0]!=a[0]else 1;tc=(c[k]-a[k])/(b[k]-a[k]);td=(d[k]-a[k])/(b[k]-a[k]);lo=max(F(0),min(tc,td));hi=min(F(1),max(tc,td))
 return (lo,hi)if lo<hi else None

def interval_covered(parts):
 cursor=F(0)
 for lo,hi in sorted(parts):
  if lo>cursor:return False
  cursor=max(cursor,hi)
 return cursor>=1

def recover(domains,source,retained):
 domains=np.asarray(domains,dtype='<f8');source=np.asarray(source,dtype='<f8');retained=np.asarray(retained,dtype='<f8')
 for a in [domains,source,retained]:assert a.ndim==3 and a.shape[1:]==(3,3)and np.isfinite(a).all()
 polys=[oriented(projected(f))for f in domains];assert all(signed_area(p)>0 for p in polys),'Degenerate domain'
 # Only genuine identical full projected shared edges become internal; unmatched
 # subdivisions stay external and cannot receive invented neighbour/seam credit.
 edges={}
 for di,p in enumerate(polys):
  for a,b in zip(p,p[1:]+p[:1]):edges.setdefault(tuple(sorted((a,b))),[]).append((di,a,b))
 assert all(len(v)<=2 for v in edges.values()),'Nonmanifold domain edge'
 for v in edges.values():
  if len(v)==2:
   assert v[0][1:]==tuple(reversed(v[1][1:])),'Domain shared winding conflict'
   assert all(source_height(domains[v[0][0]],p)==source_height(domains[v[1][0]],p)for p in v[0][1:]),'Domain shared3D height conflict'
 boundary=[v[0]for v in edges.values()if len(v)==1];pieces=[];coverage=[]
 for di,domain in enumerate(polys):
  remaining=[domain]
  for si,face in enumerate(source):
   src=projected(face)
   if signed_area(src)==0:continue
   src=oriented(src)
   if any(max(p[k]for p in src)<min(p[k]for p in domain)or max(p[k]for p in domain)<min(p[k]for p in src)for k in [0,1]):continue
   poly=src
   for a,b in zip(domain,domain[1:]+domain[:1]):poly=clip(poly,a,b,True)
   if signed_area(poly)==0:continue
   pieces.append(dict(domain=di,source=si,polygon=poly,exactPoints=[(p[0],source_height(face,p),p[1])for p in poly]))
   remaining=[q for old in remaining for q in subtract(old,src)]
  uncovered=sum(abs(signed_area(p))for p in remaining);coverage.append(dict(domain=di,exactUncoveredAreaM2=str(uncovered),covered=uncovered==0))
 seams=[];boundary_coverage=[]
 for bi,(di,a,b)in enumerate(boundary):
  parts=[];neighbours=0
  for ri,rf in enumerate(retained):
   rp=projected(rf)
   if signed_area(rp)==0:continue
   for c,d in zip(rp,rp[1:]+rp[:1]):
    iv=overlap_interval(a,b,c,d)
    if iv is None:continue
    neighbours+=1
    for piece in pieces:
     if piece['domain']!=di:continue
     pp=piece['polygon']
     for e,g in zip(pp,pp[1:]+pp[:1]):
      jv=overlap_interval(a,b,e,g)
      if jv is None:continue
      lo,hi=max(iv[0],jv[0]),min(iv[1],jv[1])
      if lo>=hi:continue
      pts=[tuple(a[k]+t*(b[k]-a[k])for k in [0,1])for t in [lo,hi]];gaps=[source_height(source[piece['source']],p)-source_height(rf,p)for p in pts];parts.append((lo,hi));seams.append(dict(boundary=bi,domain=di,source=piece['source'],retained=ri,exactInterval=[str(lo),str(hi)],exactEndpointHeightGapsM=[str(v)for v in gaps],heightCompatible=all(v==0 for v in gaps)))
  boundary_coverage.append(dict(boundary=bi,domain=di,retainedPositiveEdgeIncidences=neighbours,completePositiveDimensionalSharedSeam=interval_covered(parts)))
 passed=bool(pieces and all(p['covered']for p in coverage)and all(p['completePositiveDimensionalSharedSeam']for p in boundary_coverage)and all(p['heightCompatible']for p in seams))
 return dict(exactSourcePlanarPieces=pieces,domainCoverage=coverage,completeExternalDomainEdges=len(boundary),internalDomainEdges=sum(len(v)==2 for v in edges.values()),boundaryCoverage=boundary_coverage,allExact3DSeamProofs=seams,seamCompatible=passed,terrainProposalApproved=False)
