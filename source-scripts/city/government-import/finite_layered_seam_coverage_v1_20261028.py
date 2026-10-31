"""Exact coverage of every finite seam height layer; no production validator changes."""
from fractions import Fraction as F
from coordinated_native_boundary_v1_20261023 import value

def uncovered(segment,mates,tolerance=F(999,100000)):
 assert 0<tolerance<=F(999,100000)
 start,end=segment[:2];assert start<=end
 intervals=[]
 for mate in mates:
  lo,hi=max(start,mate[0]),min(end,mate[1])
  if lo>hi:continue
  left=value(segment,lo)-value(mate,lo)
  if lo==hi:
   if abs(left)<=tolerance:intervals.append((lo,hi))
   continue
  right=value(segment,hi)-value(mate,hi);slope=(right-left)/(hi-lo)
  if slope==0:
   if abs(left)<=tolerance:intervals.append((lo,hi))
  else:
   a=lo+(-tolerance-left)/slope;b=lo+(tolerance-left)/slope;a,b=max(lo,min(a,b)),min(hi,max(a,b))
   if a<=b:intervals.append((a,b))
 if start==end:return []if intervals else [(start,end)]
 cursor=start;gaps=[]
 for lo,hi in sorted(intervals):
  if lo>cursor:gaps.append((cursor,lo))
  cursor=max(cursor,hi)
 if cursor<end:gaps.append((cursor,end))
 return gaps

def bidirectional_layer_coverage(left,right,tolerance=F(999,100000)):
 assert left and right and 0<tolerance<=F(999,100000)
 results=[]
 for own,mates in [(left,right),(right,left)]:
  failures=[]
  for i,segment in enumerate(own):
   gaps=uncovered(segment,mates,tolerance)
   if gaps:failures.append(dict(segment=i,face=segment[4],uncoveredIntervals=[[str(a),str(b)]for a,b in gaps]))
  results.append(dict(segments=len(own),uncoveredSegments=len(failures),failures=failures))
 return dict(passed=all(not r['uncoveredSegments']for r in results),toleranceMetres=str(tolerance),directions=results,method='Exact rational union of parameter intervals where each original finite affine height segment has at least one finite opposite-side layer within the 9.99mm bound, strictly below the unchanged1cm limit. Both directions and isolated points included; no sampling or upper-layer-only substitution.')
