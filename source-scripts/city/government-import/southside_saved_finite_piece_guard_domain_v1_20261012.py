"""DRAFT: restrict existing exact source/ground pieces to complete guard domains.
No full finite/coverage recomputation, new bound or role/acceptance credit.
"""
from fractions import Fraction as F
from exact_original_paired_finite_clearance_20261010 import clip_source
from exact_original_projection_coverage_v2_20261010 import signed_area

def rational_point(p):return tuple(F(v)for v in p)
def bounds(poly):return tuple((min(p[k]for p in poly),max(p[k]for p in poly))for k in (0,2))
def strictly_disjoint(poly,xz):
 b=bounds(poly);return any(b[k][1]<min(p[k]for p in xz)or max(p[k]for p in xz)<b[k][0]for k in range(2))
def closed_clip(poly,domain):
 """Domain is a complete triangle/segment/point; boundaries never pruned."""
 assert poly and domain and all(len(p)==3 for p in poly)and all(len(p)==2 for p in domain)
 if strictly_disjoint(poly,domain):return []
 area=signed_area(domain)
 if area:
  if area<0:domain=list(reversed(domain))
  lines=list(zip(domain,domain[1:]+domain[:1]))
 else:
  a,b=max(((a,b)for a in domain for b in domain),key=lambda ab:sum((ab[0][k]-ab[1][k])**2 for k in range(2)))
  if a==b:
   x,z=a;lines=[((x,z),(x,z-1)),((x,z),(x,z+1)),((x,z),(x+1,z)),((x,z),(x-1,z))]
  else:
   dx,dz=b[0]-a[0],b[1]-a[1];lines=[(a,b),(b,a),(a,(a[0]+dz,a[1]-dx)),(b,(b[0]-dz,b[1]+dx))]
 result=list(poly)
 for a,b in lines:
  if not result:break
  result=clip_source(result,a,b)
 return result

def ground_height(p,ground):
 a,b,c=ground;u=tuple(b[k]-a[k]for k in range(3));v=tuple(c[k]-a[k]for k in range(3));n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]);assert n[1]!=0
 return a[1]-(n[0]*(p[0]-a[0])+n[2]*(p[2]-a[2]))/n[1]

def restrict_saved_piece(piece,ground,domains):
 assert len(ground)==3 and all(len(p)==3 for p in ground)
 if 'allExactSourcePrismIntersectionVertices'not in piece:
  assert piece.get('closedProjectionDisjoint')or piece.get('collapsedProjectionConservative')
  return dict(savedPieceVerbatim=piece,collapsedOrDisjointNotGivenPlaneCredit=True,unresolved=bool(piece.get('collapsedProjectionConservative')),restrictions=[],noAcceptanceCredit=True)
 vertices=piece['allExactSourcePrismIntersectionVertices'];assert vertices
 poly=[rational_point(v['exactOriginalSourcePoint'])for v in vertices]
 for p,v in zip(poly,vertices):
  gy=ground_height(p,ground);assert str(gy)==v['exactFiniteGroundHeightM']and str(p[1]-gy)==v['exactGapM']
 assert min(F(v['exactGapM'])for v in vertices)==F(piece['exactMinimumGapM'])
 rows=[]
 for domain in domains:
  xz=[rational_point(p)for p in domain['completeXZPoints']];cut=closed_clip(poly,xz)
  if not cut:continue
  gaps=[p[1]-ground_height(p,ground)for p in cut];minimum=min(gaps)
  rows.append(dict(domainID=domain['domainID'],domainKind=domain['domainKind'],completeClippedOriginalSourcePoints=[[str(v)for v in p]for p in cut],exactGapAtEveryClippedVertexM=[str(v)for v in gaps],exactMinimumGapM=str(minimum),unchangedOrdinaryBoundProvedOnRestriction=minimum>=F(-1,2),pointOrSegmentRestrictionsRetained=True))
 return dict(savedPieceVerbatim=piece,completeSavedVertexAndPlaneEqualityVerified=True,restrictions=rows,unresolved=False,noAcceptanceCredit=True)
