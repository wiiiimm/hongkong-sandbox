import unittest
from fractions import Fraction as F
import math
import numpy as np
from exact_closed_ground_aabb_pruning_v1_20261011 import CompleteGround,enclosing_float
from exact_original_rational_interface_segment_clearance_20261011 import verify
from exact_original_upper_ground_interfaces_20261009 import exact_upper_ground_interfaces

class Tests(unittest.TestCase):
    def setUp(self):
        self.g=np.array([[[-1,0,-1],[2,0,-1],[-1,0,2]],[[2,0,2],[-1,0,2],[2,0,-1]],[[20,100,20],[21,100,20],[20,100,21]]],float)
        self.s=[['0','1','0'],['1','1','0']]
    def compare(self,s,g):
        prepared=CompleteGround(g); a=verify(s,g);b=prepared.segment(s)
        for key in ['closedWholeSegmentProjectionCovered','strictlyExposedWholePositiveInterface','exactMinimumGapM']:
            self.assertEqual(a[key],b[key])
        nested=b['selectedGroundKernelProof'];mapped=[]
        for row in nested['allFinitePieces'] if nested else []:
            mapped.append(dict(row,groundFace=b['originalGroundFaceBySelectedKernelFace'][row['groundFace']]))
        self.assertEqual(a['allFinitePieces'],mapped);prepared.verify_binding()
        return b
    def test_far_high_facet_does_not_bury_segment(self):
        p=self.compare(self.s,self.g);self.assertEqual(p['selection']['selectedOriginalGroundFaces'],[0,1])
        self.assertEqual(p['selectedGroundKernelProof']['completeFiniteGroundFacesAccounted'],2)
        self.assertEqual(p['selection']['completeGroundFacetCount'],3)
        self.assertNotEqual(p['selection']['completeGroundSHA256'],p['selectedGroundKernelProof']['completeGroundSHA256'])
    def test_touched_high_island_retained(self):
        island=np.array([[[1,2,0],[1.1,2,0],[1,2,.1]]]);p=self.compare(self.s,np.concatenate([self.g,island]))
        self.assertFalse(p['strictlyExposedWholePositiveInterface']);self.assertIn(3,p['selection']['selectedOriginalGroundFaces'])
    def test_collapsed_line_and_point_retained(self):
        extra=np.array([[[.5,2,0],[1,2,0],[.7,2,0]],[[0,3,0],[0,3,0],[0,3,0]]])
        p=self.compare(self.s,np.concatenate([self.g,extra]));self.assertEqual(p['exactMinimumGapM'],'-2')
        self.assertEqual(p['selection']['selectedOriginalGroundFaces'],[0,1,3,4])
    def test_vertical_segment(self):self.compare([['0','1','0'],['0','2','0']],self.g)
    def test_missing_ground_and_empty_selection(self):
        p=self.compare([['30','1','30'],['31','1','30']],self.g)
        self.assertFalse(p['closedWholeSegmentProjectionCovered']);self.assertIsNone(p['selectedGroundKernelProof'])
    def test_exact_boundary(self):self.compare([['-1','1','-1'],['2','1','-1']],self.g)
    def test_outside_grazing(self):
        p=self.compare([['-1','1','-100000001/100000000'],['2','1','-100000001/100000000']],self.g)
        self.assertFalse(p['closedWholeSegmentProjectionCovered'])
    def test_fraction_enclosure_in_both_rounding_directions(self):
        for x in [F(1,3),F(-1,3),F(1)+F(1,2**54),F(1)-F(1,2**55)]:
            self.assertLessEqual(F(enclosing_float(x,True)),x)
            self.assertGreaterEqual(F(enclosing_float(x,False)),x)
        # The exact query is just below binary64 1; a touching x=1 point
        # remains nominated, preventing an inward rounding omission.
        x=F(1)-F(1,2**55);p=CompleteGround(np.array([[[1,2,0]]*3]))
        ids,_=p.select([[str(x),'1','0'],[str(x),'2','0']]);self.assertEqual(ids.tolist(),[0])
    def test_grade_full_equivalence_and_global_id_remap(self):
        ground=np.concatenate([self.g[2:],self.g[:2]])
        face=np.array([[[0,-1,0],[1,1,0],[0,1,0]]],float)
        full=exact_upper_ground_interfaces(face,[0],ground);p=CompleteGround(ground);r=p.grade(face,0)
        self.assertTrue(full);self.assertEqual(full,r['exactUpperGroundIntervals'])
        self.assertEqual(r['selection']['selectedOriginalGroundFaces'],[1,2]);p.verify_binding()
    def test_higher_ground_island_preserves_upper_interval_splits(self):
        g=np.concatenate([self.g,np.array([[[.2,.1,-.2],[.8,.1,-.2],[.5,.1,.2]]])])
        t=np.array([[[0,-1,0],[1,1,0],[0,1,0]]],float)
        p=CompleteGround(g);self.assertEqual(exact_upper_ground_interfaces(t,[0],g),p.grade(t,0)['exactUpperGroundIntervals'])
    def test_input_copy_and_changed_ground_rejected(self):
        g=self.g.copy();p=CompleteGround(g);g[0,0,1]=100;p.verify_binding()
        p.ground.flags.writeable=True;p.ground[0,0,1]=100
        with self.assertRaises(AssertionError):p.verify_binding()
    def test_changed_bounds_cannot_hide_near_facet(self):
        p=CompleteGround(self.g);p.lower.flags.writeable=True;p.lower[0]=100
        with self.assertRaises(AssertionError):p.verify_binding()
    def test_nonfinite_or_rounded_coordinates_or_zero_segment_rejected(self):
        g=self.g.copy();g[0,0,0]=math.inf
        with self.assertRaises(AssertionError):CompleteGround(g)
        p=CompleteGround(self.g)
        for s in [[[0.,1.,0.],[1.,1.,0.]],[self.s[0],self.s[0]]]:
            with self.assertRaises(AssertionError):p.segment(s)

class ActualElementsFixture(unittest.TestCase):
    def test_complete_365886_ground_matches_unpruned_original_interface(self):
        from run import ROOT,read
        base=ROOT/'docs/astra-city/government-import'
        graph=read(base/'xl-terrain-recovery-20261011-elements-complete-owned-original-contact-graph-v1/diagnostic.json.gz')
        contact=next(r for r in graph['oneExactPositiveWitnessPerOwnedInvolvingBodyPair'] if r['components']==[4,998])
        self.assertEqual(contact['globalOriginalFaces'],[5309,148635])
        row=read(base/'xl-terrain-recovery-20261011-elements-two-native-current-render-ground-capture-v1/native-render-ground.json.gz')['rows'][0]
        self.assertEqual(row['uid'],'landsd/273061:0')
        p=CompleteGround(np.asarray(row['drawnGroundGeometry']).reshape(-1,3,3))
        self.assertEqual(len(p.ground),365886)
        self.assertEqual(p.ground_sha,'52a1f0baf2da9d2489a86e8d6925ad1f4da9aaf166e648cf061efedb7d385a0d')
        points=contact['exactContact']['exactPoints'];s=[points[0],points[-1]]
        pruned=p.segment(s);full=verify(s,p.ground)
        self.assertEqual(pruned['selection']['selectedOriginalGroundFaces'],[350928,350929,350930,350931])
        self.assertEqual(pruned['selection']['strictlyDisjointNoncandidateCount'],365882)
        for key in ['closedWholeSegmentProjectionCovered','strictlyExposedWholePositiveInterface','exactMinimumGapM']:
            self.assertEqual(full[key],pruned[key])
        nested=pruned['selectedGroundKernelProof']
        mapped=[dict(r,groundFace=pruned['originalGroundFaceBySelectedKernelFace'][r['groundFace']]) for r in nested['allFinitePieces']]
        self.assertEqual(full['allFinitePieces'],mapped)
        self.assertTrue(pruned['strictlyExposedWholePositiveInterface']);p.verify_binding()

if __name__=='__main__':unittest.main()
