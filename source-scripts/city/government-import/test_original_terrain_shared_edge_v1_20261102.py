"""Shared-edge routing must preserve the strict seam and full obligation guards."""
import copy
import unittest
from unittest.mock import patch
from original_terrain_shared_edge_v1_20261102 import verify
from original_terrain_obligation_union_v3_20261102 import merge
from qualified_original_shared_edge_stage_v1_20261102 import dispatch
import original_terrain_point_contact_v2_20261025 as point
import original_terrain_obligation_union_v2_20261025 as union


def fixture(height=5.):
    root = dict(cell=1, w=4, h=4, meta=dict(georef=dict(aE=1, aN=-1, bE=834500, bN=816500)))
    def node(a, c, y):
        return dict(coarseCells=[a, 0, c, 2], meta=dict(parentTerrain='root', parentSha256='same'),
            nativeMesh=dict(position=[a,y,0,c,y,0,c,y,2,a,y,2], index=[0,1,2,0,2,3]))
    current, old = node(1, 2, 5.), node(0, 1, height)
    scope = dict(currentNativeActors=7, uids=['new'], touchingNativeUids=[], positiveAreaTerrainOverlaps=0,
        regionalParentExtent=[1,0,2,2], intersectingForms=1,
        terrainContacts=[dict(url='old', extent=[0,0,1,2], coarseOverlapAreaM2=0,
            packedContacts=[dict(hierarchy=[], overlapAreaM2=0, packedBounds=[0,0,1,2])])])
    return scope, current, root, {'old': old}


class Edge(unittest.TestCase):
    def test_valid_profile_and_obligation_census(self):
        args = fixture(5.005); before = copy.deepcopy(args); result = verify(*args)
        self.assertLess(result['rows'][0]['comparison']['maximumErrorM'], .01)
        self.assertEqual(args, before)
        self.assertEqual(merge({}, [{'uid':'new'}], args[0], native_count=7,
            target_uids=['new'], expected_count=1, point_context=result,
            replayed_point_contacts=result), {'new':{'uid':'new'}})

    def test_excess_height_is_rejected(self):
        with self.assertRaises(AssertionError): verify(*fixture(5.011))

    def test_missing_finite_interval_is_rejected(self):
        args = fixture(); args[3]['old']['nativeMesh']['index'] = [0,2,3]
        with self.assertRaises(AssertionError): verify(*args)

    def test_isolated_spike_cannot_hide_between_interval_checks(self):
        args=fixture(); m=args[1]['nativeMesh']
        m['position'] += [1,5.02,1,1.5,5,0.5,1.5,5,1.5];m['index'] += [4,5,6]
        with self.assertRaises(AssertionError): verify(*args)

    def test_unused_outside_position_is_rejected(self):
        args=fixture(); args[1]['nativeMesh']['position'] += [3,5,1]
        with self.assertRaises(AssertionError): verify(*args)

    def test_changed_parent_is_rejected(self):
        args=fixture();args[3]['old']['meta']['parentSha256']='different'
        with self.assertRaises(AssertionError): verify(*args)

    def test_positive_overlap_is_rejected(self):
        args=fixture();args[0]['positiveAreaTerrainOverlaps']=1
        with self.assertRaises(AssertionError): verify(*args)

    def test_unknown_old_member_is_rejected(self):
        args=list(fixture());args[3]={}
        with self.assertRaises(AssertionError): verify(*args)

    def test_nested_geometry_is_rejected(self):
        args=fixture();args[3]['old']['patches']=[{}]
        with self.assertRaises(AssertionError): verify(*args)

    def test_missing_form_is_rejected(self):
        args=fixture();result=verify(*args)
        with self.assertRaises(AssertionError):
            merge({}, [], args[0], native_count=7, target_uids=['new'], expected_count=1,
                point_context=result,replayed_point_contacts=result)

    def test_changed_context_is_rejected(self):
        args=fixture();result=verify(*args);changed=copy.deepcopy(result);changed['rows'][0]['interval']=[0,1]
        with self.assertRaises(AssertionError):
            merge({}, [{'uid':'new'}], args[0], native_count=7,target_uids=['new'],expected_count=1,
                point_context=changed,replayed_point_contacts=result)

    def test_point_path_remains_the_existing_path(self):
        scope=fixture()[0];result=dict(contract='exact-original-terrain-single-point-contact-v1',
            rows=[dict(url='old',noPositiveAreaOrSharedEdge=True,exactParentVertexAgreement=True)])
        self.assertEqual(merge({},[{'uid':'new'}],scope,native_count=7,target_uids=['new'],expected_count=1,
            point_context=result,replayed_point_contacts=result),{'new':{'uid':'new'}})
        result['rows'][0]['noPositiveAreaOrSharedEdge']=False
        with self.assertRaises(AssertionError):
            merge({},[{'uid':'new'}],scope,native_count=7,target_uids=['new'],expected_count=1,
                point_context=result,replayed_point_contacts=result)

    def test_dispatch_preserves_other_point_calls_and_restores_on_error(self):
        args=fixture();original_merge=union.merge
        with patch.object(point,'verify',return_value='ordinary-point') as ordinary:
            with self.assertRaises(RuntimeError):
                with dispatch(*args):
                    self.assertEqual(point.verify({'different':True},None,None,None),'ordinary-point')
                    self.assertEqual(point.verify(*args)['contract'],'existing-finite-native-shared-edge-context-v1')
                    raise RuntimeError('test cleanup')
            self.assertIs(point.verify,ordinary)
        self.assertIs(union.merge,original_merge)


if __name__ == '__main__':
    unittest.main()
