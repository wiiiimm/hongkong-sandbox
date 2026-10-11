import unittest,hashlib,numpy as np
from hsbc_mounted_visual_panel_accounting_20261009 import verify,canonical_sha,UID,SOURCE

def fixture():
 a,b,c,d,e,f,h=[(0,10,0),(0,10,1),(0,8,0),(0,8,1),(0,10,2),(0,8,2),(0,9,2)]
 t=np.array([[a,b,c],[b,d,c],[b,e,d],[e,h,d],[h,f,d],[a,(1,10,-1),(1,10,1)],[e,(1,10,1),(1,10,3)]],float)
 g={'components':[{'globalOriginalFaces':[5,6],'actorUID':UID},{'globalOriginalFaces':list(range(5)),'actorUID':UID}],'resolvedOriginalComponents':[0],'supportInterfaceAccepted':False,'reasons':['unresolved-original-component:1'],'ordinaryGroundRootComponents':[0],'contactWitnesses':[],'groundRootedComponentParents':{'0':None}}
 c=[{'sourceFace':i,'groundProjectionCovered':True,'minimum':{'minimumGapM':3}} for i in range(5)]
 r={'uid':UID,'sourceSHA256':SOURCE,'component':1,'originalFaces':list(range(5)),'rootedBodyComponent':0,'rootedBodyContactFaces':[5,6],'independentlyVerifiedPackedWorldRoundoffM':0}
 return t,c,g,r

def binding(t,c,g,r):return {'completeOriginalWorldTrianglesSHA256':hashlib.sha256(t.tobytes()).hexdigest(),'strictGraphSHA256':canonical_sha(g),'continuousContextsSHA256':canonical_sha(c),'frozenRoleSHA256':canonical_sha(r),'providerRootStreamsSHA256':'provider-source-receipt','fullCurrentPhysicalSHA256':'physical-receipt','fullCurrentForeignScopeSHA256':'foreign-receipt'}
def check(t,c,g,r):
 b=binding(t,c,g,r);return verify(t,c,g,expected_role=r,expected_binding=b,current_binding=b)
class Tests(unittest.TestCase):
 def test_two_exact_points_visual_accounting_only(self):
  r=check(*fixture());self.assertTrue(r['visualPanelAccounted']);self.assertEqual(r['addedGroundRoots'],[]);self.assertEqual(r['addedLoadBearingEdges'],[]);self.assertFalse(r['panelCanSupportOtherComponents'])
 def rejects(self,mutation):
  data=fixture();mutation(*data)
  with self.assertRaises((AssertionError,ValueError,KeyError)):check(*data)
 def test_detached_corner(self):self.rejects(lambda t,c,g,r:t[6].__iadd__([1,0,0]))
 def test_one_point_only(self):self.rejects(lambda t,c,g,r:r.update(rootedBodyContactFaces=[5]))
 def test_unrooted_body(self):self.rejects(lambda t,c,g,r:g.update(resolvedOriginalComponents=[]))
 def test_panel_cannot_support_other_component(self):self.rejects(lambda t,c,g,r:g.update(contactWitnesses=[{'components':[1,0]}]))
 def test_panel_not_ground_root(self):self.rejects(lambda t,c,g,r:g['ordinaryGroundRootComponents'].append(1))
 def test_buried_face(self):self.rejects(lambda t,c,g,r:c[3]['minimum'].update(minimumGapM=-.5001))
 def test_missing_ground(self):self.rejects(lambda t,c,g,r:c[2].update(groundProjectionCovered=False))
 def test_omitted_context(self):self.rejects(lambda t,c,g,r:c.pop())
 def test_reversed_face(self):self.rejects(lambda t,c,g,r:t.__setitem__(2,t[2,::-1]))
 def test_detached_face(self):self.rejects(lambda t,c,g,r:t[2].__iadd__([5,0,0]))
 def test_unrelated_source(self):self.rejects(lambda t,c,g,r:r.update(uid='landsd/123:0'))
 def test_contact_below_top(self):self.rejects(lambda t,c,g,r:t[5,:,1].__isub__(.01))
 def test_widened_locator(self):self.rejects(lambda t,c,g,r:r.update(independentlyVerifiedPackedWorldRoundoffM=.01))
 def test_changed_context_binding(self):
  t,c,g,r=fixture();b=binding(t,c,g,r);c[2]['minimum']['minimumGapM']=2
  with self.assertRaises(AssertionError):verify(t,c,g,expected_role=r,expected_binding=b,current_binding=b)
 def test_missing_foreign_scope_binding(self):
  t,c,g,r=fixture();b=binding(t,c,g,r);b.pop('fullCurrentForeignScopeSHA256')
  with self.assertRaises(KeyError):verify(t,c,g,expected_role=r,expected_binding=b,current_binding=b)
if __name__=='__main__':unittest.main()
