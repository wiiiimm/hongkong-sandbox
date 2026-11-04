import unittest
import numpy as np
import shapely
from bounded_original_inset_faces_v1_20261023 import inset_faces
from coordinated_native_boundary_v1_20261023 import seam_segments,compatible_seam


def square(x0,z0,x1,z1,y):return np.array([[[x0,y,z0],[x1,y,z0],[x0,y,z1]],[[x1,y,z0],[x1,y,z1],[x0,y,z1]]],float)


class BoundedInset(unittest.TestCase):
    def setUp(self):self.base=square(-10,-10,10,10,5);self.projection=shapely.box(-1,-1,1,1)
    def center_height(self,faces):
        values=[]
        for face in faces:
            if shapely.Polygon(face[:,[0,2]]).covers(shapely.Point(0,0)):
                a,b,c=face;normal=np.cross(b-a,c-a)
                if abs(normal[1])>1e-10:values.append(a[1]+(normal[0]*a[0]+normal[2]*a[2])/normal[1])
        return max(values)
    def test_core_uses_original_height_and_preserves_domain(self):
        r=inset_faces(self.base,square(-10,-10,10,10,3),self.projection)
        self.assertAlmostEqual(self.center_height(r['output']),3)
        self.assertLess(shapely.union_all(shapely.polygons(r['output'][:,:,[0,2]])).symmetric_difference(shapely.box(-10,-10,10,10)).area,1e-8)
        self.assertAlmostEqual(r['removedAreaM2'],r['insertedAreaM2'])
        for face,record in zip(r['output'],r['lineage']):
            if record['kind']=='unchanged':self.assertTrue(np.array_equal(face,self.base[record['parentFace']]))
    def test_highest_original_layer_is_selected(self):
        terrain=np.concatenate([square(-10,-10,10,10,3),square(-10,-10,10,10,4)])
        self.assertAlmostEqual(self.center_height(inset_faces(self.base,terrain,self.projection)['output']),4)
    def test_new_below_clamp_is_rejected(self):
        with self.assertRaises(AssertionError):inset_faces(self.base,square(-10,-10,10,10,.5),self.projection)
    def test_source_does_not_cover_projection(self):
        with self.assertRaises(AssertionError):inset_faces(self.base,square(2,2,10,10,3),self.projection)
    def test_adjacent_partitions_have_same_full_finite_seam(self):
        left=square(-10,-10,0,10,5);right=square(0,-10,10,10,5)
        r=inset_faces(np.concatenate([left,right]),square(-10,-10,10,10,3),self.projection)
        parts=[np.array([face for face,line in zip(r['output'],r['lineage'])if(line['parentFace']<2)==flag])for flag in [True,False]]
        proof=compatible_seam(*[seam_segments(p,0,0,-10,10)for p in parts],-10,10)
        self.assertTrue(proof['passed'])


if __name__=='__main__':unittest.main()
