import copy,unittest
from original_retained_own_views_contract_v1_20261025 import verify
class Contract(unittest.TestCase):
 def setUp(self):
  self.entries={'a':dict(sha256='exact',triangles=31,publicationApproved=False)}
  self.views=[dict(uid='a',width=w,time=t,sourceSHA256='exact',originalTriangles=31,active=True,visible=True,fullyFramed=True,fallbackFaces=0,meshVisibility=[True],wireframeFlags=[False])for w in [390,1280]for t in ['15:00','22:00']]
 def test_exact_views_preserve_existing_hold(self):
  before=copy.deepcopy(self.entries);self.assertTrue(verify(self.views,self.entries));self.assertEqual(before,self.entries)
 def test_missing_and_duplicate_rejected(self):
  for views in [self.views[:-1],self.views[:-1]+[self.views[0]]]:
   with self.assertRaises(AssertionError):verify(views,self.entries)
 def test_geometry_visibility_and_framing_rejected(self):
  for key,value in [('sourceSHA256','different'),('originalTriangles',30),('active',False),('visible',False),('fullyFramed',False),('fallbackFaces',1),('meshVisibility',[]),('meshVisibility',[True,False]),('wireframeFlags',[True]),('wireframeFlags',[])]:
   with self.subTest(key=key,value=value):
    views=copy.deepcopy(self.views);views[0][key]=value
    with self.assertRaises(AssertionError):verify(views,self.entries)
 def test_empty_retained_not_accepted(self):
  with self.assertRaises(AssertionError):verify([], {})
if __name__=='__main__':unittest.main()
