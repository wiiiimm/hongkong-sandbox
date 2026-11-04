import copy,unittest
from heritage_parent_capture_scope_binding_v1_20261014 import bind_scope,bind_current_forms
class ScopeBinding(unittest.TestCase):
 def setUp(self):
  self.uid='landsd/165054:0';self.forms=[dict(building=dict(uid=self.uid if i==0 else 'landsd/'+str(i)+':0',base=0.0),existingNative=False,tile='city/data/tiles/test.json')for i in range(23)]
  self.scope=dict(region=[0,0,1,1],scope=dict(currentProjectedFormsTouching=self.forms));unknown=['landsd/'+str(i+9000)+':0'for i in range(22)]
  self.cert=dict(fullParentClosedDomain=[0,0,1,1],completeCurrentNativeActors=6653,wholeCurrentNativeTouchingUIDs=[],touchingNativeOutsideNominationScope=[],all22PriorUnknownUIDsRetained=unknown,priorUnknownUIDsProvedOutside=unknown,rows=[dict(uid=str(i),strictAllFourClosedDomainDisjoint=True,nativeInstallationApprovalTransferred=False)for i in range(6653)])
 def test_complete23_includes_owned_and22_others(self):
  forms,actors=bind_scope(self.scope,self.cert,self.uid);self.assertEqual(len(actors),23);self.assertIn(self.uid,actors);self.assertEqual(len(set(actors)-{self.uid}),22)
 def test_duplicate_actor_fail_closed(self):
  self.forms[-1]['building']['uid']=self.uid
  with self.assertRaises(AssertionError):bind_scope(self.scope,self.cert,self.uid)
 def test_one_touching_native_fail_closed(self):
  self.cert['rows'][20]['strictAllFourClosedDomainDisjoint']=False
  with self.assertRaises(AssertionError):bind_scope(self.scope,self.cert,self.uid)
 def test_native_flag_cannot_enter_basic_scope(self):
  self.forms[2]['existingNative']=True
  with self.assertRaises(AssertionError):bind_scope(self.scope,self.cert,self.uid)
 def test_full_current_form_numeric_bytes_not_python_equality(self):
  tiles={'city/data/tiles/test.json':dict(buildings=copy.deepcopy([r['building']for r in self.forms]))};bind_current_forms(self.forms,tiles);tiles['city/data/tiles/test.json']['buildings'][0]['base']=-0.0
  with self.assertRaises(AssertionError):bind_current_forms(self.forms,tiles)
if __name__=='__main__':unittest.main()
