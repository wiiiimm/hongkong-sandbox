"""Behavioural regressions: roofs with identical bounds, winding, holes and cache safety."""
import copy
import unittest
import numpy as np
from shape_metrics import compare, mesh, frame, raster
from shape_screen import route, cache_key, valid_cached, digest, encode


def box(x=0,y=0,z=0,w=20,h=10,d=16):
    p=np.array([[x,y,z],[x+w,y,z],[x+w,y,z+d],[x,y,z+d],
                [x,y+h,z],[x+w,y+h,z],[x+w,y+h,z+d],[x,y+h,z+d]],dtype=float)
    faces=[[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]]
    return p[faces]


def pitched():
    a=box(h=8).tolist();a=[t for i,t in enumerate(a) if i not in (2,3)]
    # Roof ridge reaches the same height as the flat comparison box.
    a += [[[0,8,0],[20,8,0],[20,10,8]],[[0,8,0],[20,10,8],[0,10,8]],
          [[0,10,8],[20,10,8],[20,8,16]],[[0,10,8],[20,8,16],[0,8,16]],
          [[0,8,0],[0,10,8],[0,8,16]],[[20,8,0],[20,8,16],[20,10,8]]]
    return np.array(a)


class GeometryTests(unittest.TestCase):
    def test_same_shape_different_winding_and_order(self):
        a=box();r=compare(a,a[::-1,::-1]);self.assertEqual(r['comparison'],'negligible-difference')
        self.assertEqual(max(v['silhouetteDifference'] for v in r['views']),0)
    def test_same_bounds_different_roof_is_detected(self):
        r=compare(box(),pitched());self.assertEqual(r['boundsDifferenceMetres'],0)
        self.assertEqual(r['comparison'],'material-difference');self.assertGreater(r['roof']['depthP95Metres'],1)
    def test_world_translation_is_not_normalized_away(self):
        r=compare(box(),box()+[2,0,0]);self.assertEqual(r['comparison'],'placement-only-difference')
        self.assertGreater(max(v['silhouetteDifference'] for v in r['views']),.1)
    def test_open_courtyard_detected_from_roof(self):
        ring=np.concatenate([box(w=3),box(x=17,w=3),box(x=3,z=0,w=14,d=3),box(x=3,z=13,w=14,d=3)])
        r=compare(box(),ring);self.assertEqual(r['comparison'],'material-difference');self.assertGreater(r['roof']['silhouetteDifference'],.3)
    def test_extra_mesh_does_not_mutate_input(self):
        a=box();before=a.copy();b=np.concatenate([a,box(x=20,w=5,h=7)])
        self.assertEqual(compare(a,b)['comparison'],'material-difference');np.testing.assert_array_equal(a,before)
    def test_disjoint_meshes_are_serializable(self):
        r=compare(box(),box()+[100,0,0]);encode(r);self.assertNotEqual(r['comparison'],'negligible-difference')
    def test_bad_geometry_rejected(self):
        for a in [[],[0]*8,[float('nan')]*9]:
            with self.assertRaises(ValueError):mesh(a)
    def test_repeat_metrics_identical(self):self.assertEqual(compare(box(),pitched()),compare(box(),pitched()))


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.n={'matches':1,'identityMatches':True,'recordedHeightsMatch':True,'state':'packed-needs-placement-review','cachedOverlap':1,'cachedCentroidDistanceMetres':0,'nativeTerrainDiagnostic':{'status':'diagnostic-complete','lowRimGapRange':[0,.1]}}
        self.audit={'flags':[],'terrain':{'state':'sampled-source-footprint-envelope'}}
        self.budget={'triangles':100,'geometryBytes':200,'residentBytes':400}
        self.profiles={'mobile':dict.fromkeys(self.budget,1000)}
    def decide(self,state='unassessed',kind='negligible-difference',landmark=False):
        return route(state,self.n,self.audit,{'comparison':kind},self.budget,self.profiles,landmark)[0]
    def test_verified_does_not_require_geometry(self):
        self.assertEqual(route('enhanced',{}, {},None,None,{},False)[0],'skip')
    def test_negligible_is_candidate_not_accepted(self):self.assertEqual(self.decide(),'keep-current-candidate')
    def test_existing_rework_never_skips(self):self.assertEqual(self.decide('enhancement-required'),'retain-pending')
    def test_material_difference_routes_only_after_gates(self):
        self.assertEqual(self.decide(kind='material-difference'),'import-candidate')
        self.n['identityMatches']=False;self.assertEqual(self.decide(kind='material-difference'),'retain-pending')
    def test_terrain_and_runtime_hold(self):
        self.n['nativeTerrainDiagnostic']['lowRimGapRange']=[8,9];self.assertEqual(self.decide(kind='material-difference'),'retain-pending')
        self.n['nativeTerrainDiagnostic']['lowRimGapRange']=[0,.1];self.budget['residentBytes']=2000
        self.assertEqual(self.decide(kind='material-difference'),'retain-pending')
    def test_landmark_not_accepted_by_geometry_alone(self):self.assertEqual(self.decide(landmark=True),'retain-pending')
    def test_unknown_or_missing_stays_pending(self):
        self.assertEqual(self.decide(kind='uncertain-difference'),'retain-pending')
        self.assertEqual(route('unassessed',{}, {},None,None,{},False)[0],'retain-pending')


class CacheTests(unittest.TestCase):
    def test_context_and_geometry_and_engine_invalidate(self):
        baseline=cache_key({'inputHash':'a'},{'geometrySHA256':'b'},'c')
        self.assertNotEqual(baseline,cache_key({'inputHash':'x'},{'geometrySHA256':'b'},'c'))
        self.assertNotEqual(baseline,cache_key({'inputHash':'a'},{'geometrySHA256':'x'},'c'))
        self.assertNotEqual(baseline,cache_key({'inputHash':'a'},{'geometrySHA256':'b'},'x'))
    def test_cache_tampering_rejected(self):
        from shape_metrics import VERSION
        d={'kind':VERSION,'cacheKey':'k','result':{'value':1},'resultSHA256':digest(encode({'value':1}))}
        self.assertEqual(valid_cached(d,'k'),{'value':1});d['result']['value']=2
        with self.assertRaises(ValueError):valid_cached(d,'k')

if __name__=='__main__':unittest.main()
