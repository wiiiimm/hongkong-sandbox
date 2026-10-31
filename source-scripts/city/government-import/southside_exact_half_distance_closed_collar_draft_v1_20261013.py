"""UNEXECUTED source-bound mask certificate; no terrain or support approval."""
import struct
from fractions import Fraction as F
from southside_saved_negative_region_exact_core_distance_draft_v1_20261013 import hull

def derived_width(distance):
 d=F(distance);assert d>0
 return d/2

def pack_coordinate(value):
 """Literal binary64-to-binary32 packing; retain bytes and exact represented value."""
 v=F(value);raw=struct.pack('<f',float(v));packed=F(struct.unpack('<f',raw)[0])
 return dict(exactOriginalCoordinate=v,literalFloat32BytesLE=raw.hex(),exactPackedCoordinate=packed,exactAbsolutePackingErrorM=abs(packed-v))

def closed_masks(core,width):
 width=F(width);assert width>0
 result=[];error=F(0)
 for i,r in enumerate(core):
  p=hull(r['completeCoreHull']);assert r['completeOriginalCoreDomainLineage']
  outer=hull([(x+dx,z+dz)for x,z in p for dx in [-width,width]for dz in [-width,width]])
  assert len(outer)>=4
  packed=[]
  for point in outer:
   values=[pack_coordinate(v)for v in point];error=max(error,*[v['exactAbsolutePackingErrorM']for v in values]);packed.append(values)
  triangles=[]
  for j in range(1,len(outer)-1):
   ids=[0,j,j+1];exact=[outer[k]for k in ids];literal=[tuple(v['exactPackedCoordinate']for v in packed[k])for k in ids]
   triangles.append(dict(vertexIndices=ids,completeExactClosedXZTriangle=exact,completeLiteralFloat32ClosedXZTriangle=literal,packedProjectionMayCollapse=len(hull(literal))<3))
  result.append(dict(corePrimitive=i,completeCoreHull=p,completeOriginalCoreDomainLineage=r['completeOriginalCoreDomainLineage'],completeExactClosedMinkowskiOuterHull=outer,completePackedOuterVertices=packed,completeClosedProjectionTriangles=triangles))
 return result,error

def region_certificate(proof,width,packing_error,core_count):
 """Consume the pinned previous distance proof; no new distance calculation."""
 distance=F(proof['exactMinimumDistanceM']);width=F(width);packing_error=F(packing_error)
 assert proof['completeCorePrimitiveCount']==core_count
 examined=proof['completeExaminedCoreProofs'];excluded=proof['completeStrictDistanceExclusions'];ties=proof['completeNearestCoreTies']
 assert len(examined)+len(excluded)==core_count and len(examined)==proof['exactExaminedCorePrimitives'] and ties
 seen=[r['corePrimitive']for r in examined+excluded];assert sorted(seen)==list(range(core_count))
 assert all(F(r['completeExactDistanceProof']['exactDistanceM'])>=distance for r in examined)
 assert all(F(r['exactClosedBoundsLowerDistanceM'])>distance for r in excluded)
 assert all(F(r['proof']['exactDistanceM'])==distance for r in ties)
 clearance=distance-width-packing_error
 return dict(exactSavedNegativeRegionToWholeCoreDistanceM=distance,exactDerivedUniformWidthM=width,exactMaxMaskVertexPackingErrorM=packing_error,exactPackedMaskEnclosureRadiusM=width+packing_error,exactClosedSeparationLowerBoundM=clearance,completeClosedPackedMaskStrictlySeparated=clearance>0,completeNearestCoreTieIDs=[r['corePrimitive']for r in ties],exactPreviousProofRetained=True,noSupportOrCurrentAcceptance=True)

def make_certificate(q):
 assert len(q['all8WorldRows'])==8 and len(q['all3653OriginalCoreDomainRecords'])==3653
 assert len(q['all3484PriorCollarNegativesVerbatim'])==3484 and q['completeUnresolvedRecords']==[] and q['positiveUniformGeometricSeparationExists']
 assert q['currentAcceptance']is False and q['noTerrainConstruction'] and q['noWholeFiniteReplay']
 core=q['completePreparedOriginal13Core'];lineage=[r for p in core for r in p['completeOriginalCoreDomainLineage']]
 assert len(lineage)==3653 and sorted(map(repr,lineage))==sorted(map(repr,q['all3653OriginalCoreDomainRecords']))
 minimum=F(q['exactGlobalDistanceInfimumM']);width=derived_width(minimum);masks,error=closed_masks(core,width);rows=[];count=0;observed_min=None
 for row in q['all8WorldRows']:
  records=[]
  for i,r in enumerate(row['completeNegativeRegionSeparationRecords']):
   assert r['completeClosedStrictNegativeRegion']['hasStrictNegativePoint'] and r['completeClosedStrictNegativeRegion']['completeClosedNegativeSourcePoints']
   proof=r['completeExactCoreSeparation'];d=F(proof['exactMinimumDistanceM']);observed_min=d if observed_min is None else min(observed_min,d)
   cert=region_certificate(proof,width,error,len(core));records.append(dict(savedRegionRecordIndex=i,sourceFace=r['sourceFace'],savedPieceID=r['savedPieceID'],completeOriginalFacetSHA256=r['completeOriginalFacetSHA256'],certificate=cert));count+=1
  rows.append(dict(uid=row['uid'],arithmetic=row['arithmetic'],completeWorldSHA256=row['completeWorldSHA256'],completeCurrentGroundSHA256=row['completeCurrentGroundSHA256'],completeRegionCertificates=records))
 assert count==4784 and observed_min==minimum
 return dict(exactGlobalDistanceInfimumM=minimum,exactDerivedUniformWidthM=width,completeClosedCoreMinkowskiMaskPrimitives=masks,exactMaxMaskVertexPackingErrorM=error,all8SourceWorldRows=rows,completeRegionCertificateCount=count,all4784ClosedRegionsSeparatedFromPackedMask=all(r['certificate']['completeClosedPackedMaskStrictlySeparated']for row in rows for r in row['completeRegionCertificates']),maskPackingIsNotCandidateTerrainPacking=True,futureTerrainVerticesAndSeamsRemainUnproved=True,noDistanceReplay=True,noTerrainConstruction=True,currentAcceptance=False)
