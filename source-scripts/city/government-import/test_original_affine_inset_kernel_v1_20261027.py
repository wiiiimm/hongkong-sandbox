import unittest
import numpy as np
import shapely
from original_affine_inset_kernel_v1_20261027 import source_upper_surface, inset_parent


def surface(height):
    return np.asarray([[[0,height,0],[10,height,0],[0,height,10]],
                       [[10,height,0],[10,height,10],[0,height,10]]],float)


class InsetContracts(unittest.TestCase):
    def setUp(self):
        self.projection=shapely.box(4,4,6,6)
        self.core=self.projection.buffer(1,join_style='mitre')
        self.outer=self.core.buffer(1,join_style='mitre')

    def test_highest_authored_surface_and_input_immutability(self):
        source=np.concatenate([surface(2),surface(3)])
        original=source.copy()
        faces,planes=source_upper_surface(source,self.projection,self.core,self.outer)
        self.assertTrue(np.array_equal(source,original))
        self.assertTrue(np.all(faces[:,:,1]==3))
        self.assertEqual(len(planes),len(faces))

    def test_lower_inset_conserves_area_and_never_edits_inputs(self):
        parent=surface(5);before=parent.copy()
        source,planes=source_upper_surface(surface(3),self.projection,self.core,self.outer)
        output,proof=inset_parent(parent,source,planes,self.core,self.outer)
        self.assertTrue(np.array_equal(parent,before))
        self.assertAlmostEqual(proof['removedAreaM2'],proof['insertedAreaM2'],places=6)
        self.assertAlmostEqual(shapely.union_all(shapely.polygons(output[:,:,[0,2]])).area,100)
        self.assertTrue(np.all(output[:,:,1]>=3))
        self.assertTrue(np.all(output[:,:,1]<=5))

    def test_higher_source_does_not_raise_parent(self):
        parent=surface(3)
        source,planes=source_upper_surface(surface(5),self.projection,self.core,self.outer)
        output,proof=inset_parent(parent,source,planes,self.core,self.outer)
        self.assertTrue(np.array_equal(output,parent))
        self.assertEqual(proof['changedParentFaces'],[])

    def test_incomplete_source_is_rejected(self):
        with self.assertRaisesRegex(AssertionError,'complete source model'):
            source_upper_surface(surface(3)[:1],shapely.box(7,7,8,8),
                                 shapely.box(6,6,9,9),shapely.box(5,5,10,10))

    def test_surface_outside_edit_retains_exact_coordinates(self):
        untouched=surface(7)+np.array([20,0,0])
        parent=np.concatenate([surface(5),untouched])
        source,planes=source_upper_surface(surface(3),self.projection,self.core,self.outer)
        output,proof=inset_parent(parent,source,planes,self.core,self.outer)
        for original_index in [2,3]:
            ids=[i for i,row in enumerate(proof['outputLineage'])
                 if row==dict(kind='unchanged',parentFace=original_index)]
            self.assertEqual(len(ids),1)
            self.assertTrue(np.array_equal(output[ids[0]],parent[original_index]))

    def test_existing_new_surface_clamp_still_rejects(self):
        source,planes=source_upper_surface(surface(1),self.projection,self.core,self.outer)
        with self.assertRaisesRegex(AssertionError,'existing-clamp'):
            inset_parent(surface(5),source,planes,self.core,self.outer)


if __name__=='__main__':
    unittest.main()
