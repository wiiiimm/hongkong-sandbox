import unittest
from copy import deepcopy
from hierarchical_original_terrain_binding_v2_20261026 import verify_successor
from expand_rendered_terrain_group_v1_20261026 import extend_right
from test_expand_rendered_terrain_group_v1_20261026 import fixtures

def pair():
 old,root=fixtures();old['patches'][0]['meta']=dict(targetUids=['landsd/1:0'])
 old['patches'][0]['nativeMesh']=dict(index=[0,1,2],position=[0.,8.,0.,5.,8.,0.,0.,8.,5.])
 new,_=extend_right(old,root,root_cells=[0,0,2,1])
 new['patches'].append(dict(coarseCells=[2,0,4,2],meta=dict(targetUids=['landsd/2:0']),nativeMesh=dict(index=[0,1,2])))
 new['meta']['targetUids']=['landsd/1:0','landsd/2:0']
 return old,new

class BindingTests(unittest.TestCase):
 def test_exact_retention(self):
  old,new=pair();proof=verify_successor(old,new,['landsd/2:0']);self.assertEqual(proof['retainedUids'],['landsd/1:0']);self.assertFalse(proof['installationApproved'])
 def test_changed_original_geometry_refused(self):
  old,new=pair();new['patches'][0]['nativeMesh']['position'][0]+=.01
  with self.assertRaises(AssertionError):verify_successor(old,new,['landsd/2:0'])
 def test_changed_old_grid_refused(self):
  old,new=pair();new['renderedElev'][1]+=.01
  with self.assertRaises(AssertionError):verify_successor(old,new,['landsd/2:0'])
 def test_overlapping_child_refused(self):
  old,new=pair();new['patches'][-1]['coarseCells']=[0,0,4,2]
  with self.assertRaises(AssertionError):verify_successor(old,new,['landsd/2:0'])
 def test_removed_child_refused(self):
  old,new=pair();new['patches'].pop(0)
  with self.assertRaises(AssertionError):verify_successor(old,new,['landsd/2:0'])
 def test_invented_target_refused(self):
  old,new=pair();new['meta']['targetUids'].append('landsd/3:0')
  with self.assertRaises(AssertionError):verify_successor(old,new,['landsd/2:0'])
 def test_exclusion_of_old_surface_refused(self):
  old,new=pair();new['patchExclusions']=[[0,0,1,1]]
  with self.assertRaises(AssertionError):verify_successor(old,new,['landsd/2:0'])
class RepeatedExtensionTests(unittest.TestCase):
 def repeated(self):
  old,new=pair();prior=dict(existingGroupURL='old-group.json',existingGroupSHA256='original-provenance')
  old['meta']['scriptedOriginalChildExtension']=deepcopy(prior)
  new['meta']['scriptedOriginalChildExtension']=dict(previousExtension=deepcopy(prior),existingGroupURL='current-group.json')
  return old,new
 def test_previous_extension_retained(self):
  old,new=self.repeated();self.assertTrue(verify_successor(old,new,['landsd/2:0'])['allOriginalChildrenUnchanged'])
 def test_missing_previous_extension_refused(self):
  old,new=self.repeated();new['meta']['scriptedOriginalChildExtension'].pop('previousExtension')
  with self.assertRaises(AssertionError):verify_successor(old,new,['landsd/2:0'])
 def test_changed_previous_extension_refused(self):
  old,new=self.repeated();new['meta']['scriptedOriginalChildExtension']['previousExtension']['existingGroupSHA256']='changed'
  with self.assertRaises(AssertionError):verify_successor(old,new,['landsd/2:0'])
if __name__=='__main__':unittest.main()
