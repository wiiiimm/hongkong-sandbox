"""Synthetic audit point-order lineage, no production source or model calculations."""
import unittest
from unittest.mock import patch
import numpy as np
import heritage165054_two_tin_clamp_lowrim_context_v1_20261014 as a
class SavedPointLineage(unittest.TestCase):
    def geometry(self):return dict(position=[0,0,0,2,0,0,0,0,2,9,4,9],index=[0,1,2])
    def test_lineage_matches_unchanged_existing_sample_order(self):
        r=a.module(a.HERE/'resolve-pass.py','synthetic_only_standard_sampler');g=self.geometry();points,bottom=r.sample_points(g);tags=a.tag_points(g,np)
        self.assertEqual(len(tags),len(points));self.assertEqual(len(tags),9);self.assertEqual([v['kind'] for v in tags[:5]],['source-POSITION']*4+['source-face-centre']);self.assertEqual(tags[4]['originalFaceIDs'],[0]);self.assertEqual(tags[5]['edge'],0);self.assertEqual(tags[5]['edgeNumerator'],1);self.assertEqual(tags[5]['edgeDenominator'],2)
    def test_unused_vertices_remain_context_not_omitted_or_named_support(self):
        tags=a.tag_points(self.geometry(),np);self.assertEqual(tags[3],dict(kind='source-POSITION',vertexID=3,originalFaceIDs=[]));self.assertNotIn('sourceRole',tags[3])
    def test_upper_edges_do_not_create_new_lowrim_point_obligations(self):
        g=dict(position=[0,0,0,3,2,0,0,2,3],index=[0,1,2]);tags=a.tag_points(g,np);self.assertEqual(len(tags),4)
    def test_actual_45_context_retained_with_four_source_only_keys(self):
        scope=a.read(a.north.DOC/'proposal-input.json')['scope']['allActorsForNominationLease']
        from run import reservations
        with patch.object(reservations,'connect',side_effect=AssertionError('DB forbidden')):r=a.resources(scope)
        self.assertEqual(len(r),4);self.assertIn('immutable-source-sheet:7-SW-15D',r);self.assertIn('immutable-source-sheet:7-SW-20B',r);self.assertEqual(len(scope),45)
class MissingSamplesAndClipTypes(unittest.TestCase):
    def test_matching_missing_nan_and_sampler_minus_infinity(self):
        x=np.array([5.,np.nan,-np.inf]);self.assertTrue(a.same_source_height_samples(x,x.copy(),np))
        y=x.copy();y[2]=np.inf;self.assertFalse(a.same_source_height_samples(x,y,np))
        y=x.copy();y[1]=5.;self.assertFalse(a.same_source_height_samples(x,y,np))
    def test_finite_comparison_remains_exact_without_tolerance(self):
        self.assertFalse(a.same_source_height_samples(np.array([5.]),np.array([np.nextafter(5.,np.inf)]),np))
    def test_actual_legacy_rect_keeps_array_vertices_and_tolist_serialization(self):
        r=a.module(a.HERE/'resolve-pass.py','synthetic_clip_type_only');tri=np.array([[0.,1.,0.],[2.,2.,0.],[0.,3.,2.]])
        poly=r.exact.rect(list(tri),[.5,0.,1.5,1.5]);self.assertGreaterEqual(len(poly),3)
        self.assertTrue(all(isinstance(v,np.ndarray) and v.shape==(3,) for v in poly));self.assertTrue(all(isinstance(v.tolist(),list) for v in poly))
        self.assertEqual(r.exact.rect(list(tri),[4.,4.,5.,5.]),[])
if __name__=='__main__':unittest.main()
