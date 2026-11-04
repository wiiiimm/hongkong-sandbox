"""UNEXECUTED acquisition draft: exact thirteen-domain retention distance envelope.
A declared 5m L-infinity collar is a NEW changed surface, not prior geometry.
No terrain/source building generation or acceptance. Full saved-piece compatibility
of the complete changed closed projection must precede any constructor.
"""
from fractions import Fraction as F
from southside_saved_local_core_parent_adapter_v3_20261012 import affine_value,min_branch_partition,split,bb,old
WIDTH=F(5)
def _cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def _hull(points):
 p=sorted(set(points));assert p
 if len(p)==1:return p
 lo=[];hi=[]
 for q in p:
  while len(lo)>1 and _cross(lo[-2],lo[-1],q)<=0:lo.pop()
  lo.append(q)
 for q in reversed(p):
  while len(hi)>1 and _cross(hi[-2],hi[-1],q)<=0:hi.pop()
  hi.append(q)
 return lo[:-1]+hi[:-1]
def _support_planes(points):
 p=_hull(points);x0=min(v[0]for v in p);x1=max(v[0]for v in p);z0=min(v[1]for v in p);z1=max(v[1]for v in p)
 planes=[(F(1),F(0),-x0),(-F(1),F(0),x1),(F(0),F(1),-z0),(F(0),-F(1),z1)]
 if len(p)==2:
  a,b=p;line=(-(b[1]-a[1]),b[0]-a[0],(b[1]-a[1])*a[0]-(b[0]-a[0])*a[1]);planes.extend([line,tuple(-v for v in line)])
 elif len(p)>2:
  for a,b in zip(p,p[1:]+p[:1]):planes.append((-(b[1]-a[1]),b[0]-a[0],(b[1]-a[1])*a[0]-(b[0]-a[0])*a[1]))
 return sorted(set(planes))
def prepare_branches(proved_union):
 """Only mask primitives reused. No building/terrain facets combined."""
 branches={}
 for record in proved_union['completeRawDomainRecords']:
  p=[tuple(F(v)for v in q)for q in record['completeXZPoints']];assert p and all(len(q)==2 for q in p)
  key=tuple(_hull(p));row=branches.setdefault(key,dict(coreHull=key,completeOriginalDomainLineage=[]));row['completeOriginalDomainLineage'].append(record)
 for row in branches.values():
  planes=_support_planes(row['coreHull']);row['alphaTerms']=[(F(0),F(0),F(1))]+[(a/(WIDTH*(abs(a)+abs(b))),b/(WIDTH*(abs(a)+abs(b))),F(1)+c/(WIDTH*(abs(a)+abs(b))))for a,b,c in planes]
  row['closedOuterHull']=_hull([(x+dx,z+dz)for x,z in row['coreHull']for dx in [-WIDTH,WIDTH]for dz in [-WIDTH,WIDTH]])
  row['closedOuterBounds']=[min(q[0]for q in row['closedOuterHull']),min(q[1]for q in row['closedOuterHull']),max(q[0]for q in row['closedOuterHull']),max(q[1]for q in row['closedOuterHull'])]
  assert all(min(affine_value(t,(x,F(0),z))for t in row['alphaTerms'])==1 for x,z in row['coreHull'])
 return list(branches.values())
def alpha_at(x,z,branches):return max([F(0)]+[min(affine_value(t,(F(x),F(0),F(z)))for t in r['alphaTerms'])for r in branches])
def complete_changed_projection_domains(branches):
 """Full closed outer projection, including alpha=0 boundary. Not a safe mask."""
 out=[]
 for i,r in enumerate(branches):
  h=r['closedOuterHull'];assert len(h)>=4
  for j in range(1,len(h)-1):out.append(dict(domainID=f'retention-outer-{i}-triangle-{j}',domainKind='UNQUALIFIED-complete-new-five-metre-retention-closed-projection',completeXZPoints=[[str(v)for v in p]for p in [h[0],h[j],h[j+1]]],completeOriginalDomainLineage=r['completeOriginalDomainLineage']))
 return out
def partition_retention_alpha(poly,branches,axis):
 """Existing exact min/max scheduling; emits regions only, never terrain."""
 regions=[(poly,(F(0),F(0),F(0)),None)]
 for i,r in enumerate(branches):
  following=[]
  for region,current,owner in regions:
   if not old.closed_xz_touch(bb(region),r['closedOuterBounds']):following.append((region,current,owner));continue
   replacements=[];improved=False
   for p,candidate,term in min_branch_partition(region,r['alphaTerms'],axis):
    difference=tuple(candidate[k]-current[k]for k in range(3))
    if not any(affine_value(difference,v)>0 for v in p):replacements.append((p,current,owner));continue
    positive,negative=split(p,[difference],axis);replacements.extend((q,current,owner)for q in negative)
    if old.intrinsic_area(positive,axis):replacements.append((positive,candidate,[i,term]));improved=True
   following.extend(replacements if improved else [(region,current,owner)])
  assert sum((old.intrinsic_area(p,axis)for p,_,_ in following),F(0))==old.intrinsic_area(poly,axis)
  regions=following
 for p,a,owner in regions:
  assert all(0<=affine_value(a,v)<=1 and affine_value(a,v)==alpha_at(v[0],v[2],branches)for v in p)
 return regions
