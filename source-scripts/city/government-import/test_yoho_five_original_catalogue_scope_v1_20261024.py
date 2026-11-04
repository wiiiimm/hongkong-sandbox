"""Adversarial checks for the exact-source/native Yoho staging boundary."""
import copy,unittest
from yoho_five_original_catalogue_scope_v1_20261024 import SOURCES,SUPPORTS,PARENT,RETAINED,PAIRS,verify_metadata,verify_native_scope,verify_terrain

class YohoScopeTests(unittest.TestCase):
    def setUp(self):
        self.models=[dict(uid=u,sha256=h,buildingCSUID=u,proceduralWindows=False,rootTranslation=[-834500,0,816500])for u,h in SOURCES.items()]
        for m in self.models:
            if m['uid']in SUPPORTS:m['supportDependencies']=[dict(uid=PARENT,state='installed',buildingCSUID=PARENT,sha256=SOURCES[PARENT])]
        self.current={u:dict(uid=u,sha256=u)for u in RETAINED}
        self.current.update({str(n):dict(uid=str(n))for n in range(6876-len(RETAINED))})
        self.scope=dict(uids=list(SOURCES),rows=[dict(uid=u,sourceSHA256=h,currentNativeActorsChecked=6876,nearbyNativeActors=[dict(uid=n,sourceSHA256=self.current[n]['sha256'])for n in RETAINED]if u==PARENT else[])for u,h in SOURCES.items()])
        self.native=dict(rows=[dict(uid=u,nativeUid=v,sourceSHA256=SOURCES[u],nativeSHA256=self.current[v]['sha256'],rawCurrentNativeEntry=copy.deepcopy(self.current[v]),modes=[dict(mode=m)for m in ['original','literal','leftF32','balancedF32']])for u,v in PAIRS])
    def test_exact_inputs_unchanged(self):
        before=copy.deepcopy((self.models,self.scope,self.native,self.current));self.assertTrue(verify_metadata(self.models));self.assertTrue(verify_native_scope(self.scope,self.native,self.current));self.assertEqual(before,(self.models,self.scope,self.native,self.current))
    def test_changed_source_rejected(self):
        self.models[0]['sha256']='wrong'
        with self.assertRaises(AssertionError):verify_metadata(self.models)
    def test_source_move_rejected(self):
        self.models[0]['verticalPlacementOffsetHKPD']=.01
        with self.assertRaises(AssertionError):verify_metadata(self.models)
    def test_missing_dependency_rejected(self):
        next(m for m in self.models if m['uid']in SUPPORTS).pop('supportDependencies')
        with self.assertRaises(AssertionError):verify_metadata(self.models)
    def test_suppression_rejected(self):
        self.models[0]['suppressesBuildingUids']=['x']
        with self.assertRaises(AssertionError):verify_metadata(self.models)
    def test_retained_basic_binding_injection_rejected(self):
        self.models[0]['retainedBasicSupportDependencies']=[dict(uid='x')]
        with self.assertRaises(AssertionError):verify_metadata(self.models)
    def test_missing_native_pair_rejected(self):
        self.native['rows'].pop()
        with self.assertRaises(AssertionError):verify_native_scope(self.scope,self.native,self.current)
    def test_changed_native_entry_rejected(self):
        self.current[next(iter(RETAINED))]['label']='changed'
        with self.assertRaises(AssertionError):verify_native_scope(self.scope,self.native,self.current)
    def test_new_native_dependency_rejected(self):
        uid=self.native['rows'][0]['nativeUid'];self.current[uid]['supportDependencies']=[dict(uid=PARENT)];self.native['rows'][0]['rawCurrentNativeEntry']=copy.deepcopy(self.current[uid])
        with self.assertRaises(AssertionError):verify_native_scope(self.scope,self.native,self.current)
    def test_missing_coordinate_world_rejected(self):
        self.native['rows'][0]['modes'].pop()
        with self.assertRaises(AssertionError):verify_native_scope(self.scope,self.native,self.current)
    def test_wider_terrain_routing_rejected(self):
        with self.assertRaises(AssertionError):verify_terrain(dict(meta=dict(targetUids=list(SOURCES)),nativeMesh=dict(index=[0]*1236)),'h','h')
    def test_changed_terrain_bytes_rejected(self):
        with self.assertRaises(AssertionError):verify_terrain(dict(meta=dict(targetUids=[PARENT]),nativeMesh=dict(index=[0]*1236)),'h','x')
    def test_exact_terrain_accepted(self):self.assertTrue(verify_terrain(dict(meta=dict(targetUids=[PARENT]),nativeMesh=dict(index=[0]*1236)),'h','h'))

if __name__=='__main__':unittest.main()
