"""Adversarial checks for the exact terrain corner case."""
import copy
import unittest
from original_terrain_point_contact_v1_20261025 import verify


def patch(cells, bounds, height=15.):
    a,b,c,d = bounds
    return dict(coarseCells=cells, nativeMesh=dict(
        position=[a,height,b,c,height,b,c,height,d,a,height,d], index=[0,1,2,0,2,3]))


class PointContactTests(unittest.TestCase):
    def setUp(self):
        self.root = dict(cell=1., w=3,h=3,elev=[15.]*9,
                         meta=dict(georef=dict(aE=1.,aN=-1.,bE=834500.,bN=816500.)))
        self.new = patch([1,1,2,2], [1.,1.,2.,2.])
        self.old = patch([0,0,1,1], [0.,0.,1.,1.])
        self.scope = dict(touchingNativeUids=[],positiveAreaTerrainOverlaps=0,
                          regionalParentExtent=[1.,1.,2.,2.],terrainContacts=[dict(
                              url='old.json',extent=[0.,0.,1.,1.],coarseOverlapAreaM2=0.,
                              packedContacts=[dict(hierarchy=[],overlapAreaM2=0.,packedBounds=[0.,0.,1.,1.])])])

    def run_proof(self):
        return verify(self.scope, self.new, self.root, {'old.json':self.old})

    def test_exact_corner_matches_parent(self):
        result = self.run_proof()
        self.assertEqual(result['rows'][0]['sharedPoint'], [1.,15.,1.])
        self.assertFalse(result['installationApproved'])

    def test_shared_edge_requires_separate_proof(self):
        self.old = patch([0,1,1,2], [0.,1.,1.,2.])
        c=self.scope['terrainContacts'][0];c['extent']=c['packedContacts'][0]['packedBounds']=[0.,1.,1.,2.]
        with self.assertRaises(AssertionError): self.run_proof()

    def test_area_overlap_is_rejected(self):
        self.scope['terrainContacts'][0]['coarseOverlapAreaM2']=1.
        with self.assertRaises(AssertionError): self.run_proof()

    def test_old_corner_height_must_be_unchanged_parent(self):
        self.old['nativeMesh']['position'][7]=15.001
        with self.assertRaises(AssertionError): self.run_proof()

    def test_new_corner_height_must_match_parent(self):
        self.new['nativeMesh']['position'][1]=14.9
        with self.assertRaises(AssertionError): self.run_proof()

    def test_hidden_child_is_not_omitted(self):
        self.old['children']=[copy.deepcopy(self.old)]
        with self.assertRaises(AssertionError): self.run_proof()

    def test_geometry_outside_closed_domain_is_rejected(self):
        self.old['nativeMesh']['position'][0]=1.01
        with self.assertRaises(AssertionError): self.run_proof()

    def test_unindexed_common_vertex_is_not_coverage(self):
        self.old['nativeMesh']['index']=[0,1,3]
        with self.assertRaises(AssertionError): self.run_proof()

    def test_unaccounted_current_contact_is_rejected(self):
        with self.assertRaises(AssertionError): verify(self.scope,self.new,self.root,{})


if __name__ == '__main__': unittest.main()
