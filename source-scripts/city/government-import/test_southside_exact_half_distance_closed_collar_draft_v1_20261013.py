"""UNEXECUTED pure boundary/packing/scope fixtures for the source-bound mask."""
import unittest,math,struct
from fractions import Fraction as F
from southside_exact_half_distance_closed_collar_draft_v1_20261013 import derived_width,pack_coordinate,closed_masks,region_certificate

def core(points):return [dict(completeCoreHull=points,completeOriginalCoreDomainLineage=[{'uid':'fixture','completeXZPoints':points}])]
def proof(d='1'):
 return dict(exactMinimumDistanceM=d,completeCorePrimitiveCount=2,exactExaminedCorePrimitives=1,completeExaminedCoreProofs=[dict(corePrimitive=0,completeExactDistanceProof=dict(exactDistanceM=d))],completeStrictDistanceExclusions=[dict(corePrimitive=1,exactClosedBoundsLowerDistanceM='2')],completeNearestCoreTies=[dict(corePrimitive=0,proof=dict(exactDistanceM=d))])
class Tests(unittest.TestCase):
 def test_width_is_exact_half_not_decimal_rounding(self):
  d=F(236023373611996694358247725523355,1244133349520838023872690224365568);self.assertEqual(derived_width(d)*2,d);self.assertNotEqual(derived_width(d),F(1,10))
 def test_zero_and_negative_separation_rejected(self):
  for d in [0,-1]:
   with self.assertRaises(AssertionError):derived_width(d)
 def test_closed_point_minkowski_square(self):
  masks,e=closed_masks(core([(F(3),F(4))]),F(1,2));self.assertEqual(set(masks[0]['completeExactClosedMinkowskiOuterHull']),{(F(5,2),F(7,2)),(F(7,2),F(7,2)),(F(7,2),F(9,2)),(F(5,2),F(9,2))});self.assertEqual(e,0)
 def test_vertical_segment_endpoints_retained(self):
  masks,_=closed_masks(core([(F(0),F(0)),(F(0),F(2))]),F(1));self.assertEqual(set(masks[0]['completeExactClosedMinkowskiOuterHull']),{(F(-1),F(-1)),(F(1),F(-1)),(F(1),F(3)),(F(-1),F(3))})
 def test_original_area_lineage_not_dropped(self):
  c=core([(F(0),F(0)),(F(2),F(0)),(F(0),F(1))]);c[0]['completeOriginalCoreDomainLineage']*=13;masks,_=closed_masks(c,F(1,8));self.assertEqual(len(masks[0]['completeOriginalCoreDomainLineage']),13)
 def test_actual_float32_bytes_and_error(self):
  value=F(1)+F(1,2**24);r=pack_coordinate(value);self.assertEqual(r['literalFloat32BytesLE'],struct.pack('<f',float(value)).hex());self.assertEqual(r['exactPackedCoordinate'],1);self.assertEqual(r['exactAbsolutePackingErrorM'],F(1,2**24))
 def test_next_double_error_is_not_tolerance_rounded(self):
  value=F(math.nextafter(1.,2.));r=pack_coordinate(value);self.assertEqual(r['exactAbsolutePackingErrorM'],F(1,2**52))
 def test_strict_packed_enclosure(self):
  r=region_certificate(proof(),F(1,2),F(1,8),2);self.assertTrue(r['completeClosedPackedMaskStrictlySeparated']);self.assertEqual(r['exactClosedSeparationLowerBoundM'],F(3,8))
 def test_touching_packed_enclosure_remains_false(self):
  self.assertFalse(region_certificate(proof(),F(1,2),F(1,2),2)['completeClosedPackedMaskStrictlySeparated'])
 def test_missing_core_exclusion_rejected(self):
  p=proof();p['completeStrictDistanceExclusions']=[]
  with self.assertRaises(AssertionError):region_certificate(p,F(1,2),0,2)
 def test_duplicate_core_schedule_rejected(self):
  p=proof();p['completeStrictDistanceExclusions'][0]['corePrimitive']=0
  with self.assertRaises(AssertionError):region_certificate(p,F(1,2),0,2)
 def test_changed_nearest_distance_rejected(self):
  p=proof();p['completeNearestCoreTies'][0]['proof']['exactDistanceM']='3/2'
  with self.assertRaises(AssertionError):region_certificate(p,F(1,2),0,2)
 def test_equal_exclusion_not_strict_rejected(self):
  p=proof();p['completeStrictDistanceExclusions'][0]['exactClosedBoundsLowerDistanceM']='1'
  with self.assertRaises(AssertionError):region_certificate(p,F(1,2),0,2)
 def test_empty_lineage_rejected(self):
  c=core([(F(0),F(0))]);c[0]['completeOriginalCoreDomainLineage']=[]
  with self.assertRaises(AssertionError):closed_masks(c,F(1))
if __name__=='__main__':unittest.main(verbosity=2)
