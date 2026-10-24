import unittest
from fractions import Fraction as F
import numpy as np
from exact_original_paired_finite_clearance_20261010 import verify
from exact_original_face_conservative_clearance_v4_20261010 import verify as coarse

def ground(y=0):
    return np.array([[[-2,y,-2],[3,y,-2],[3,y,3]],[[-2,y,-2],[3,y,3],[-2,y,3]]],float)

class PairedFinite(unittest.TestCase):
    def test_sloped_source_and_ground_same_position(self):
        f=np.array([[0,0,0],[1,10,0],[0,0,1]],float)
        g=ground();g[:,:,1]=10*g[:,:,0]
        self.assertFalse(coarse(f,g)['existingOrdinaryClearanceBoundProved'])
        p=verify(f,g);self.assertEqual(p['exactCertifiedLowerClearanceM'],'0');self.assertTrue(p['existingOrdinaryClearanceBoundProved'])
    def test_vertical_sloped_bottom_source_edge(self):
        f=np.array([[0,10,0],[1,10,1],[1,0,1]],float)
        g=ground();g[:,:,1]=10-10*g[:,:,0]
        p=verify(f,g);self.assertEqual(p['exactCertifiedLowerClearanceM'],'0');self.assertTrue(p['existingOrdinaryClearanceBoundProved'])
    def test_nearly_vertical_exact_source(self):
        f=np.array([[0,0,0],[1,10,1],[.5,5,.500000000000001]])
        g=ground();g[:,:,1]=10*g[:,:,0]
        self.assertEqual(verify(f,g)['exactCertifiedLowerClearanceM'],'0')
    def test_genuine_burial_remains_failed(self):
        f=np.array([[0,-.501,0],[1,10,0],[0,0,1]])
        self.assertFalse(verify(f,ground())['existingOrdinaryClearanceBoundProved'])
    def test_fixed_limit_equality_and_next_float(self):
        f=np.array([[0,-.5,0],[1,-.5,0],[0,-.5,1]])
        self.assertTrue(verify(f,ground())['existingOrdinaryClearanceBoundProved'])
        f[0,1]=np.nextafter(-.5,-np.inf)
        self.assertFalse(verify(f,ground())['existingOrdinaryClearanceBoundProved'])
    def test_opposing_overlapping_ground_is_upper_envelope(self):
        f=np.array([[0,0,0],[1,0,0],[0,0,1]])
        a=ground();a[:,:,1]=a[:,:,0];b=ground();b[:,:,1]=1-b[:,:,0]
        p=verify(f,np.concatenate([a,b]));self.assertEqual(p['exactCertifiedLowerClearanceM'],'-1');self.assertFalse(p['existingOrdinaryClearanceBoundProved'])
    def test_real_interior_ground_island(self):
        f=np.array([[0,0,0],[1,0,0],[0,0,1]])
        island=np.array([[[.2,1,.2],[.3,1,.2],[.2,1,.3]]])
        self.assertFalse(verify(f,np.concatenate([ground(),island]))['existingOrdinaryClearanceBoundProved'])
    def test_missing_ground_coverage(self):
        f=np.array([[0,1,0],[1,1,0],[0,1,1]])
        g=np.array([[[0,0,0],[.1,0,0],[0,0,.1]]])
        p=verify(f,g);self.assertFalse(p['groundProjectionCovered']);self.assertFalse(p['existingOrdinaryClearanceBoundProved'])
    def test_point_projection_retains_lowest_actual_height(self):
        f=np.array([[0,2,0],[0,3,0],[0,4,0]])
        self.assertEqual(verify(f,ground())['exactCertifiedLowerClearanceM'],'2')
    def test_touching_collapsed_ground_remains_conservative(self):
        f=np.array([[0,1,0],[1,1,1],[1,2,1]])
        g=np.concatenate([ground(),np.array([[[0,10,0],[1,10,1],[.5,10,.5]]])])
        p=verify(f,g);self.assertFalse(p['existingOrdinaryClearanceBoundProved']);self.assertTrue(any(r.get('collapsedProjectionConservative') for r in p['allExactFiniteSourceGroundPieces']))
    def test_disjoint_collapsed_ground_has_no_credit(self):
        f=np.array([[0,1,0],[1,1,0],[0,1,1]])
        g=np.concatenate([ground(),np.array([[[.9,10,.9],[1,10,1],[.95,10,.95]]])])
        self.assertTrue(verify(f,g)['existingOrdinaryClearanceBoundProved'])
    def test_nonfinite_input_rejected(self):
        f=np.array([[0,1,0],[1,1,0],[0,np.nan,1]])
        with self.assertRaises(AssertionError):verify(f,ground())

class ActualGlorious(unittest.TestCase):
    def test_actual_original_and_rendered_faces84_and145(self):
        from run import HERE,ROOT,read,digest
        from exact_packed_world_geometry_20261009 import decode_original_world_triangles
        name='government-xl-terrain-recovery-glorious-peak-original-pair-current-physical-v2-20261010'
        selection=read(ROOT/'docs/astra-city/government-import'/name/'selection.json.gz')
        row=next(r for r in selection['rows'] if r['uid']=='landsd/233193:0');raw=(ROOT/row['candidate']['path']).read_bytes()
        self.assertEqual(digest(raw),'c39add0a40833c7ae87ba659d952608f176f0a0e9230b800fe4a397a862c9fb2')
        original=decode_original_world_triangles(raw)
        r=next(r for r in read(HERE/'local'/name/'runtime-geometry.json.gz')['rows'] if r['uid']==row['uid'])
        rendered=np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)];g=np.asarray(r['drawnGroundGeometry']).reshape(-1,3,3)
        for faces in [original,rendered]:
            for i in [84,145]:
                with self.subTest(face=i,geometry='original' if faces is original else 'rendered'):
                    self.assertFalse(coarse(faces[i],g)['existingOrdinaryClearanceBoundProved'])
                    p=verify(faces[i],g);self.assertTrue(p['existingOrdinaryClearanceBoundProved']);self.assertFalse(p['sourcePlaneInversionUsed']);self.assertGreaterEqual(F(p['exactCertifiedLowerClearanceM']),F(-1,2))
    def test_actual_source_wall_burial_is_not_hidden(self):
        from run import HERE,read
        name='government-xl-terrain-recovery-glorious-peak-original-pair-current-physical-v2-20261010'
        r=next(r for r in read(HERE/'local'/name/'runtime-geometry.json.gz')['rows'] if r['uid']=='landsd/233193:0')
        tri=np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)];g=np.asarray(r['drawnGroundGeometry']).reshape(-1,3,3)
        self.assertFalse(verify(tri[56],g)['existingOrdinaryClearanceBoundProved'])

if __name__=='__main__':unittest.main()
