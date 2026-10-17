import copy,unittest
from run import ROOT,read
from actual_native_bounds_baseline_rebind_20261011 import validate_unchanged_actor,exact_post_block6_census
DOC=ROOT/'docs/astra-city/government-import/government-xl-complete-current-native-actual-position-matrix-bounds-v2-20261011'
class ActualBaselineTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  inp=read(DOC/'input.json.gz');out=read(DOC/'inventory.json.gz');cls.uid=inp['rows'][0]['uid'];cls.i=inp['rows'][0];cls.o=next(r for r in out['rows'] if r['uid']==cls.uid);cls.uids=[r['uid'] for r in inp['rows']]
 def sample(self):return [copy.deepcopy(v) for v in [self.i,self.o,self.i['rawCurrentEntry'],self.i['currentBuilding'],self.i['source'],self.i['source']['sha256']]]
 def reject(self,fn):
  a=self.sample();fn(a)
  with self.assertRaises((AssertionError,KeyError,ValueError,TypeError)):validate_unchanged_actor(*a)
 def test_actual_whole_baseline_actor(self):self.assertEqual(validate_unchanged_actor(*self.sample()),self.o)
 def test_changed_entry_metadata(self):self.reject(lambda a:a[2].update(role='changed'))
 def test_changed_source_sha(self):self.reject(lambda a:a.__setitem__(5,'0'*64))
 def test_changed_source_path(self):self.reject(lambda a:a[4].update(path='other'))
 def test_changed_current_viewer_form(self):self.reject(lambda a:a[3].update(baseHeightHKPD=999))
 def test_missing_unused_vertex(self):self.reject(lambda a:a[1].update(completePositionVertices=a[1]['completePositionVertices']-1))
 def test_missing_mesh(self):self.reject(lambda a:a[1]['actualRenderMeshes'].pop())
 def test_missing_original_facet(self):self.reject(lambda a:a[1].update(sourceFacesOmitted=1))
 def test_false_full_position_flag(self):self.reject(lambda a:a[1].update(wholeUnusedPositionVerticesIncluded=False))
 def test_false_mesh_position_flag(self):self.reject(lambda a:a[1]['actualRenderMeshes'][0].update(wholePositionVerticesIncludingUnused=False))
 def test_actual_exact_delta_census(self):self.assertTrue(exact_post_block6_census(self.uids,self.uids+['landsd/255438:0']))
 def test_wrong_delta_census(self):
  with self.assertRaises(AssertionError):exact_post_block6_census(self.uids,self.uids+['landsd/1:0'])
 def test_duplicate_current_uid(self):
  with self.assertRaises(AssertionError):exact_post_block6_census(self.uids,self.uids+[self.uid])
if __name__=='__main__':unittest.main()
