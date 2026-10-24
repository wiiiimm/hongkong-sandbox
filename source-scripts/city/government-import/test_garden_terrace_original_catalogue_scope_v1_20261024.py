"""Adversarial tests for immutable Garden Terrace sources and retained neighbour."""
import copy
import unittest
from garden_terrace_original_catalogue_scope_v1_20261024 import (
    SOURCES, SUPPORTS, PARENT, RETAINED, RETAINED_SHA, PAIRS, MODES,
    verify_metadata, verify_native_scope,
)


class GardenScopeTests(unittest.TestCase):
    def setUp(self):
        self.models = [dict(uid=u, sha256=h, buildingCSUID=u, proceduralWindows=False,
                            rootTranslation=[-834500, 0, 816500]) for u, h in SOURCES.items()]
        for m in self.models:
            if m['uid'] in SUPPORTS:
                m['supportDependencies'] = [dict(uid=PARENT, state='installed', buildingCSUID=PARENT, sha256=SOURCES[PARENT])]
        self.current = {u: dict(uid=u, sha256=RETAINED_SHA) for u in RETAINED}
        self.current.update({str(i): dict(uid=str(i)) for i in range(6881-len(RETAINED))})
        self.scope = dict(uids=list(SOURCES), rows=[dict(uid=u, sourceSHA256=h,
            currentNativeActorsChecked=6881, nearbyNativeActors=[dict(uid=n, sourceSHA256=RETAINED_SHA)
            for n in RETAINED] if u == PARENT else []) for u, h in SOURCES.items()])
        self.native = dict(rows=[dict(uid=u, nativeUid=v, sourceSHA256=SOURCES[u],
            nativeSHA256=RETAINED_SHA, rawCurrentNativeEntry=copy.deepcopy(self.current[v]),
            modes=[dict(mode=m, areaContactPairs=0, positiveSurfaceContactPairs=62 if u==PARENT else 0)
            for m in MODES]) for u, v in PAIRS])

    def test_exact_inputs_preserved(self):
        before=copy.deepcopy((self.models,self.scope,self.native,self.current))
        self.assertTrue(verify_metadata(self.models))
        self.assertTrue(verify_native_scope(self.scope,self.native,self.current))
        self.assertEqual(before,(self.models,self.scope,self.native,self.current))

    def test_changed_source_rejected(self):
        self.models[0]['sha256']='changed'
        with self.assertRaises(AssertionError): verify_metadata(self.models)

    def test_changed_pose_rejected(self):
        self.models[0]['verticalPlacementOffsetHKPD']=.01
        with self.assertRaises(AssertionError): verify_metadata(self.models)

    def test_missing_support_rejected(self):
        self.models[0].pop('supportDependencies')
        with self.assertRaises(AssertionError): verify_metadata(self.models)

    def test_podium_dependency_rejected(self):
        next(m for m in self.models if m['uid']==PARENT)['supportDependencies']=[dict(uid=self.models[0]['uid'])]
        with self.assertRaises(AssertionError): verify_metadata(self.models)

    def test_suppression_rejected(self):
        self.models[0]['suppressesBuildingUids']=['external']
        with self.assertRaises(AssertionError): verify_metadata(self.models)

    def test_retained_basic_injection_rejected(self):
        self.models[0]['retainedBasicSupportDependencies']=[dict(uid='external')]
        with self.assertRaises(AssertionError): verify_metadata(self.models)

    def test_missing_native_pair_rejected(self):
        self.native['rows'].pop()
        with self.assertRaises(AssertionError): verify_native_scope(self.scope,self.native,self.current)

    def test_changed_retained_entry_rejected(self):
        self.current[next(iter(RETAINED))]['label']='changed'
        with self.assertRaises(AssertionError): verify_native_scope(self.scope,self.native,self.current)

    def test_manufactured_retained_dependency_rejected(self):
        uid=next(iter(RETAINED));self.current[uid]['supportDependencies']=[dict(uid=PARENT)]
        for r in self.native['rows']: r['rawCurrentNativeEntry']=copy.deepcopy(self.current[uid])
        with self.assertRaises(AssertionError): verify_native_scope(self.scope,self.native,self.current)

    def test_missing_coordinate_world_rejected(self):
        self.native['rows'][0]['modes'].pop()
        with self.assertRaises(AssertionError): verify_native_scope(self.scope,self.native,self.current)

    def test_new_area_intersection_rejected(self):
        self.native['rows'][0]['modes'][0]['areaContactPairs']=1
        with self.assertRaises(AssertionError): verify_native_scope(self.scope,self.native,self.current)

    def test_changed_line_relationship_rejected(self):
        self.native['rows'][0]['modes'][0]['positiveSurfaceContactPairs']+=1
        with self.assertRaises(AssertionError): verify_native_scope(self.scope,self.native,self.current)

    def test_stale_inventory_rejected(self):
        self.current.pop('0')
        with self.assertRaises(AssertionError): verify_native_scope(self.scope,self.native,self.current)


if __name__=='__main__': unittest.main()
