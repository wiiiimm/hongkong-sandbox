import unittest
import numpy as np
import shapely
from vertical_original_terrain_transition_v2_20261026 import Transition
from retained_inset_work_budget_v2_20261026 import verify

class VerticalTests(unittest.TestCase):
    def setUp(self):
        self.face=np.asarray([[0,10,0],[2,10,0],[0,14,0]],float);self.box=shapely.box(-1,-1,3,1);self.transition=Transition([self.box],[[0,0,5]],[(self.box,None)])
    def test_core_collapse_replays_and_accounts_parent(self):
        faces,p=self.transition.transform(self.face);self.assertFalse(faces);self.assertTrue(p['fullyCollapsed']);self.assertTrue(p['exactPartitionTYAreaPreserved'])
        result=verify(np.asarray([self.face]),np.empty((0,3,3)),[],[0],self.transition);self.assertTrue(result['allParentFacesAccounted']);self.assertEqual(result['replacedFaces'],1)
    def test_unaccounted_omission_rejected(self):
        with self.assertRaises(AssertionError):verify(np.asarray([self.face]),np.empty((0,3,3)),[],[],self.transition)
    def test_outside_parent_not_accepted_as_collapse(self):
        outside=Transition([shapely.box(10,10,11,11)],[[0,0,5]],[(self.box,None)])
        with self.assertRaises(AssertionError):verify(np.asarray([self.face]),np.empty((0,3,3)),[],[0],outside)
    def test_duplicate_collapse_rejected(self):
        with self.assertRaises(AssertionError):verify(np.asarray([self.face]),np.empty((0,3,3)),[],[0,0],self.transition)
    def test_nonvertical_parent_rejected(self):
        with self.assertRaises(AssertionError):self.transition.transform([[0,10,0],[2,10,0],[0,14,1]])
    def test_constant_return_preserves_a_nonzero_wall(self):
        weight=dict(origin=[0,0],scale=[1,1],coefficients=[0,0],intercept=.5)
        t=Transition([self.box],[[0,0,5]],[(self.box,weight)]);faces,proof=t.transform(self.face);self.assertTrue(faces);self.assertFalse(proof['fullyCollapsed']);self.assertTrue(proof['exactPartitionTYAreaPreserved'])
        before=np.linalg.norm(np.cross(self.face[1]-self.face[0],self.face[2]-self.face[0]))/2
        after=sum(np.linalg.norm(np.cross(f[1]-f[0],f[2]-f[0]))/2 for f in faces);self.assertAlmostEqual(after,before/2)
    def test_nonzero_return_cannot_be_declared_collapsed(self):
        weight=dict(origin=[0,0],scale=[1,1],coefficients=[0,0],intercept=.5);t=Transition([self.box],[[0,0,5]],[(self.box,weight)])
        with self.assertRaises(AssertionError):verify(np.asarray([self.face]),np.empty((0,3,3)),[],[0],t)
    def test_source_outside_return_preserves_unowned_parent(self):
        small=shapely.box(-1,-1,.5,1);t=Transition([self.box],[[0,0,5]],[(small,None)]);faces,p=t.transform(self.face);self.assertTrue(faces);self.assertTrue(p['exactPartitionTYAreaPreserved']);self.assertTrue(any(np.max(f[:,1])>5 for f in faces))
    def test_three_projected_vertices_are_partition_events(self):
        face=np.asarray([[0,10,0],[1,14,0],[2,10,0]],float);t=Transition([self.box],[[0,0,5]],[(self.box,dict(origin=[0,0],scale=[1,1],coefficients=[0,0],intercept=.5))]);faces,p=t.transform(face);self.assertTrue(faces);self.assertTrue(p['exactPartitionTYAreaPreserved']);self.assertTrue(all(len(np.unique(f[:,[0,2]],axis=0))<=2 for f in faces))
    def test_no_source_keeps_exact_face(self):
        t=Transition([shapely.box(10,10,11,11)],[[0,0,5]],[(self.box,None)]);faces,p=t.transform(self.face);self.assertTrue(np.array_equal(faces[0],self.face));self.assertFalse(p['changed'])

if __name__=='__main__':unittest.main()
