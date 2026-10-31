import copy,unittest
from pathlib import Path
from run import ROOT,read
import north_pair_guarded_publish_v1_20261027 as guard
class ExactPlan(unittest.TestCase):
 def setUp(self):
  self.plan=read(guard.stage.STAGE/'plan.json')
  self.surface=read(guard.BASE/(guard.P+'three-member-surface-v2-20261027')/'summary.json')
 def test_exact_plan(self):self.assertTrue(guard.exact_plan(self.plan,self.surface))
 def reject(self):
  with self.assertRaises((AssertionError,StopIteration)):guard.exact_plan(self.plan,self.surface)
 def test_additional_support_review_rejected(self):self.plan['dependencyReviews']=[{}];self.reject()
 def test_missing_surface_rejected(self):self.plan['topLevelTerrainPatches'].pop();self.reject()
 def test_changed_source_rejected(self):self.plan['topLevelTerrainPatches'][0]['sha256']='changed';self.reject()
 def test_changed_placement_rejected(self):self.plan['areas'][0]['estimates']=['changed'];self.reject()
 def test_duplicate_destination_rejected(self):self.plan['topLevelTerrainPatches'][1]['destination']=self.plan['topLevelTerrainPatches'][0]['destination'];self.reject()
 def test_dropped_retained_target_rejected(self):self.plan['topLevelTerrainPatches'][0]['replaces']['retainedUids'].pop();self.reject()
 def test_unrelated_catalogue_rejected(self):self.plan['areas'][0]['destination']='city/data/unrelated.json';self.reject()
if __name__=='__main__':unittest.main()
