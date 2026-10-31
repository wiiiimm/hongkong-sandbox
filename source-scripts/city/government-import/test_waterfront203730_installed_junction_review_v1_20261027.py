import unittest,copy
from waterfront203730_installed_junction_review_v1_20261027 import verify_scope,SHA,PSHA,NONWALL,MODES
class Scope(unittest.TestCase):
 def setUp(self):
  r=dict(recordedTowerBaseHKPD='32.1',exactHighestNativeContactHKPD='31',canonicalAnchors=412,remainingRimTargets=5,finiteCanonicalPaths=5,rawStrictSupportPassed=False,rawCompoundCapsPassed=False,allCrossingsHaveOriginalFacetPairContact=True,originalCrossingSourceFaces=[4092,9500,9501,9502,9522],rawCompoundNonWallFaces=NONWALL[:],negativeWallCount=27,all27WallCapPathsPassed=True,compoundBuriedTriangles=6,compoundBuriedUpwardTriangles=0,allBuriedFacesWallLike=True,buriedFacesHaveCapPaths=True,wholeActualGroundBurial=0,rawTransverseCrossings=26)
  self.f=dict(sourceSHA256=SHA,nativeSHA256=PSHA,sourceFaces=10667,worlds={m:copy.deepcopy(r)for m in MODES});self.f['worlds']['literal']['rawTransverseCrossings']=1010
 def bad(self,**fields):
  self.f['worlds']['literal'].update(fields)
  with self.assertRaises(AssertionError):verify_scope(self.f)
 def test_exact_scope(self):self.assertTrue(verify_scope(self.f))
 def test_different_source_rejects(self):
  self.f['sourceSHA256']='different'
  with self.assertRaises(AssertionError):verify_scope(self.f)
 def test_contact_above_recorded_tower_base_rejects(self):self.bad(exactHighestNativeContactHKPD='32.1')
 def test_new_facet_pair_rejects(self):self.bad(allCrossingsHaveOriginalFacetPairContact=False)
 def test_raw_support_failure_cannot_be_laundered(self):self.bad(rawStrictSupportPassed=True)
 def test_missing_nonwall_face_rejects(self):self.bad(rawCompoundNonWallFaces=NONWALL[:-1])
 def test_whole_buried_upward_floor_rejects(self):self.bad(compoundBuriedUpwardTriangles=1)
 def test_missing_cap_path_rejects(self):self.bad(buriedFacesHaveCapPaths=False)
 def test_incomplete_support_paths_rejects(self):self.bad(finiteCanonicalPaths=4)
 def test_missing_world_rejects(self):
  del self.f['worlds']['original']
  with self.assertRaises(AssertionError):verify_scope(self.f)
if __name__=='__main__':unittest.main()
