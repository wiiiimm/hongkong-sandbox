"""DRAFT exact source/native finite-union selection and complete coverage.
Uses actual polygons, never equality of the old native union to a rectangle.
"""
from collections import defaultdict
from fractions import Fraction as F
from exact_resumable_projected_inventory_v1_20261011 import integer_coordinates,boxes,cells,positive_aabb,interiors_separated
from exact_source_core_ten_metre_transition_domain_v1_20261011 import polygon,intersection,separated
from exact_original_projection_coverage_v2_20261010 import signed_area,subtract

def cross_pairs(source,native):
 allints,den=integer_coordinates(source+native);a,b=allints[:len(source)],allints[len(source):];ab,bb=boxes(a),boxes(b);width=5*den;buckets=defaultdict(set)
 for j,box in enumerate(bb):
  for key in cells(box,width):buckets[key].add(j)
 pairs=[]
 for i,box in enumerate(ab):
  found=set()
  for key in cells(box,width):found.update(buckets[key])
  pairs.extend((i,j)for j in sorted(found))
 return pairs,a,b,ab,bb,den
def contacts(source,native,checkpoints):
 source=[polygon(p)for p in source];native=[polygon(p)for p in native];pairs,a,b,ab,bb,den=cross_pairs(source,native)
 def compute(part):
  out=[]
  for i,j in part:
   if not positive_aabb(ab[i],bb[j]):kind='exact-AABB-zero-positive-area';area=F(0)
   elif interiors_separated(a[i],b[j]):kind='exact-integer-SAT-zero-positive-area';area=F(0)
   else:kind='exact-positive-overlap';area=signed_area(intersection(source[i],native[j]));assert area>0
   out.append(dict(sourcePiece=i,nativePiece=j,disposition=kind,exactPositiveAreaM2=area))
  return out
 rows=checkpoints.map('cross-source-native-pairs',pairs,compute);assert [(r['sourcePiece'],r['nativePiece'])for r in rows]==pairs
 positive=[r for r in rows if r['exactPositiveAreaM2']>0]
 return positive,dict(completeSourcePieces=len(source),completeNativePieces=len(native),completeCrossPairs=len(source)*len(native),completeBucketCandidatePairs=len(pairs),exactBucketDisjointPairs=len(source)*len(native)-len(pairs),exactAABBZeroPositivePairs=sum(r['disposition']=='exact-AABB-zero-positive-area'for r in rows),exactSATZeroPositivePairs=sum(r['disposition']=='exact-integer-SAT-zero-positive-area'for r in rows),exactClippedPositivePairs=len(positive),integerCoordinateDenominator=den,bucketWidthM=5)
def coverage(source,native,checkpoints):
 source=[polygon(p)for p in source];native=[polygon(p)for p in native];pairs,_,_,_,_,_=cross_pairs(source,native);by_native=defaultdict(list)
 for i,j in pairs:by_native[j].append(i)
 items=[dict(nativePiece=j,completeClosedBucketCandidateSourcePieces=sorted(by_native[j]))for j in range(len(native))]
 def compute(part):
  rows=[]
  for item in part:
   remaining=[native[item['nativePiece']]]
   for i in item['completeClosedBucketCandidateSourcePieces']:
    remaining=[p for q in remaining for p in ([q]if separated(q,source[i])else subtract(q,source[i]))]
    if not remaining:break
   rows.append(dict(**item,allUncoveredPositivePolygons=remaining,exactUncoveredPositiveAreaM2=sum(signed_area(p)for p in remaining)))
  return rows
 rows=checkpoints.map('complete-native-finite-union-coverage',items,compute)
 assert len(rows)==len(native)and all(r['nativePiece']==j and r['completeClosedBucketCandidateSourcePieces']==items[j]['completeClosedBucketCandidateSourcePieces']for j,r in enumerate(rows))
 return rows
