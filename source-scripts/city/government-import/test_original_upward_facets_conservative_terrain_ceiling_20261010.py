import unittest
import numpy as np
from original_upward_facets_conservative_terrain_ceiling_20261010 import ceiling

class TerrainCeilingTests(unittest.TestCase):
    def setUp(self):
        self.s=np.array([[[0.,2.,0.],[0.,2.,1.],[1.,2.,0.]]])
        self.p=np.array([[0.,4.,0.],[0.,4.,2.],[2.,4.,0.]])
        self.i=np.array([[0,1,2]],np.uint32)
    def test_complete_facet_capped(self):
        p,r=ceiling(self.s,self.s,self.p,self.i)
        self.assertTrue(np.array_equal(p[:,1],np.full(3,2.)))
        self.assertEqual(r['completeRoofCeilingWitnesses'][0]['completeClosedProjectedTerrainFaceIndices'],[0])
        self.assertFalse(r['currentAcceptancePassed'])
    def test_disjoint_facet_unchanged(self):
        s=self.s.copy();s[:,:,[0,2]]+=10
        p,r=ceiling(s,s,self.p,self.i);self.assertTrue(np.array_equal(p,self.p));self.assertEqual(r['changedRawVertexRecords'],[])
    def test_closed_edge_contact_is_included(self):
        s=self.s.copy();s[:,:,0]+=2
        p,r=ceiling(s,s,self.p,self.i);self.assertEqual(len(r['changedRawVertexRecords']),3)
    def test_real_tiny_intersection_not_ignored(self):
        s=self.s.copy();s[:,:,0]+=2-2**-40
        p,r=ceiling(s,s,self.p,self.i);self.assertEqual(len(r['changedRawVertexRecords']),3)
    def test_literal_lower_altitude_controls(self):
        a=self.s.copy();a[:,:,1]-=2**-32
        p,r=ceiling(self.s,a,self.p,self.i);self.assertTrue(np.all(p[:,1]<=a[:,:,1].min()))
    def test_shared_duplicate_records_move_together(self):
        p=np.concatenate([self.p,self.p[:1]])
        q,r=ceiling(self.s,self.s,p,self.i);self.assertEqual(q[0,1],q[3,1])
    def test_original_nonheight_records_are_protected(self):
        p=np.concatenate([self.p,[[0.,0.,0.],[0.,0.,2.]]]);i=np.array([[0,1,2],[0,3,4]],np.uint32)
        with self.assertRaises(AssertionError):ceiling(self.s,self.s,p,i)
    def test_upward_faces_required(self):
        s=self.s[:,[0,2,1]]
        with self.assertRaises(AssertionError):ceiling(s,s,self.p,self.i)
    def test_invalid_source_correspondence_fails(self):
        a=self.s.copy();a[0,0,1]+=.01
        with self.assertRaises(AssertionError):ceiling(self.s,a,self.p,self.i)
    def test_nonfinite_source_fails(self):
        s=self.s.copy();s[0,0,0]=np.nan
        with self.assertRaises(AssertionError):ceiling(s,s,self.p,self.i)
    def test_already_lower_ground_unchanged(self):
        p=self.p.copy();p[:,1]=1
        q,r=ceiling(self.s,self.s,p,self.i);self.assertTrue(np.array_equal(q,p))

if __name__=='__main__':unittest.main()
