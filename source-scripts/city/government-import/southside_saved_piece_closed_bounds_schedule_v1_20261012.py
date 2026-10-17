"""Scheduling only: exact closed AABB exclusions before unchanged saved-piece clipping."""
from fractions import Fraction as F

def closed_bounds(points):
 assert points and all(len(p)==2 for p in points)
 return tuple((min(F(p[k])for p in points),max(F(p[k])for p in points))for k in range(2))

def strictly_disjoint_bounds(a,b):
 return any(a[k][1]<b[k][0]or b[k][1]<a[k][0]for k in range(2))

def prepare_domains(domains):
 assert domains and len({d['domainID']for d in domains})==len(domains)
 records=[(d,closed_bounds(d['completeXZPoints']))for d in domains]
 union=tuple((min(b[k][0]for _,b in records),max(b[k][1]for _,b in records))for k in range(2))
 return union,records

def saved_piece_bounds(piece):
 if 'allExactSourcePrismIntersectionVertices'not in piece:
  assert piece.get('closedProjectionDisjoint')or piece.get('collapsedProjectionConservative')
  return None
 return closed_bounds([[v['exactOriginalSourcePoint'][k]for k in (0,2)]for v in piece['allExactSourcePrismIntersectionVertices']])

def nominate_domains(piece_bounds,prepared):
 union,records=prepared
 if piece_bounds is None:return [d for d,_ in records],dict(nonFiniteRecordNotPruned=True,totalDomains=len(records),nominatedDomains=len(records),actorStrictDisjoint=False,primitiveStrictDisjoint=0)
 if strictly_disjoint_bounds(piece_bounds,union):return [],dict(nonFiniteRecordNotPruned=False,totalDomains=len(records),nominatedDomains=0,actorStrictDisjoint=True,primitiveStrictDisjoint=len(records))
 nominated=[d for d,b in records if not strictly_disjoint_bounds(piece_bounds,b)]
 return nominated,dict(nonFiniteRecordNotPruned=False,totalDomains=len(records),nominatedDomains=len(nominated),actorStrictDisjoint=False,primitiveStrictDisjoint=len(records)-len(nominated))
