"""Exact native availability and BASIC lifetime metadata; no publication or DB writes."""
import copy,unittest
import selected_original_finite_basic_native_stage_v2_20261026 as stage
UID='landsd/255539:0';PARENT='landsd/256136:0'
REVIEW=stage.read(stage.BASE/stage.CONFIG['review']/'ROOT-PHYSICAL-REVIEW.json')
class Metadata(unittest.TestCase):
 def test_native_edge_preserved_and_basic_appended(self):
  result=stage.expected_dependencies(UID,copy.deepcopy(REVIEW));self.assertEqual([r['uid']for r in result],[PARENT,'landsd/233218:0']);self.assertEqual(result[0]['sha256'],REVIEW['retainedNativeEntries'][PARENT]['sha256']);self.assertEqual(result[1]['state'],'surveyed-footprint-fallback')
 def test_preview_requires_only_tested_native_edge(self):self.assertEqual(stage.expected_dependencies(UID,copy.deepcopy(REVIEW),include_basic=False),stage.expected_dependencies(UID,copy.deepcopy(REVIEW))[:1])
 def test_missing_lifetime_refused(self):
  r=copy.deepcopy(REVIEW);r['retainedBasicSupportDependencies'][0]['mustRemainBasicAndUnsuppressed']=False
  with self.assertRaises(AssertionError):stage.expected_dependencies(UID,r)
 def test_unknown_parent_refused(self):
  r=copy.deepcopy(REVIEW);r['retainedNativeEntries'].pop(PARENT)
  with self.assertRaises(AssertionError):stage.expected_dependencies(UID,r)
 def test_changed_runtime_graph_refused(self):
  r=copy.deepcopy(REVIEW);r['runtimeAvailabilityDependenciesByUid']={UID:'landsd/255543:0'}
  with self.assertRaises(AssertionError):stage.expected_dependencies(UID,r)
 def test_basic_cannot_alias_original_parent(self):
  r=copy.deepcopy(REVIEW);r['retainedBasicSupportDependencies'][0]['supportUid']=PARENT
  with self.assertRaises(AssertionError):stage.expected_dependencies(UID,r)
 def test_source_sha_cannot_change(self):
  r=copy.deepcopy(REVIEW);r['sourceSHA256ByUid']={UID:'0'*64}
  with self.assertRaises(AssertionError):stage.expected_dependencies(UID,r)
if __name__=='__main__':unittest.main()
