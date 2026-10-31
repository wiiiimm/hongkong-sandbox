"""Adversarial checks for the closed PolyU source proposal, using frozen inputs."""
import copy
import unittest
from run import ROOT,read
import polyu_lee_shau_kee_original_catalogue_scope_v1_20261025 as c
B=ROOT/'docs/astra-city/government-import'


class ScopeTests(unittest.TestCase):
 def setUp(self):
  selection=read(B/'government-xl-polyu-lee-shau-kee-current-ground-v2-20261025/selection.json.gz')
  self.entries={r['uid']:r['candidate']['entry']for r in selection['rows']}
  self.models=read(ROOT/'source-scripts/city/government-import/local/government-xl-polyu-two-original-retained-native-unapproved-browser-v3-20261025/catalogue.json')['models']
  self.scope=read(B/'government-xl-polyu-lee-shau-kee-current-scope-v2-20261025/summary.json')
  self.native=read(B/'government-xl-after-tvb-next-three-with-companions-native-contacts-v1-20261025/summary.json')
  self.current={r['uid']:r['entry']for r in read(B/'government-xl-after-tvb-next-three-with-companions-native-contacts-v1-20261025/native-input.json.gz')['rows']}
  for i in range(6929-len(self.current)):self.current['fixture-unrelated/'+str(i)]={}
 def test_exact_originals_and_held_native_are_preserved(self):
  self.assertTrue(c.verify_metadata(self.models,self.entries));self.assertTrue(c.verify_native_scope(self.scope,self.native,self.current))
 def test_pose_geometry_skin_and_invented_support_reject(self):
  for field,value in [('rootTranslation',[-834499,0,816500]),('verticalPlacementOffsetHKPD',1),('proceduralWindows',True),('supportDependencies',[dict(uid=c.LIB,state='installed',sha256=c.RETAINED[c.LIB],buildingCSUID='3655618355P20060311')]),('sha256','a'*64),('partialSource',True)]:
   bad=copy.deepcopy(self.models);next(m for m in bad if m['uid']==c.MAIN)[field]=value
   with self.subTest(field=field),self.assertRaises(AssertionError):c.verify_metadata(bad,self.entries)
 def test_missing_contacts_or_cleared_native_hold_reject(self):
  for action in ['missing-pair','changed-contact','cleared-hold','changed-current-source']:
   n=copy.deepcopy(self.native);cur=copy.deepcopy(self.current)
   if action=='missing-pair':n['rows']=n['rows'][1:]
   elif action=='changed-contact':next(r for r in n['rows']if r['uid']==c.MAIN and r['nativeUid']==c.LIB)['modes'][0]['finiteContactPairs']-=1
   elif action=='cleared-hold':cur[c.LIB]['publicationApproved']=True
   else:cur[c.LIB]['sha256']='a'*64
   with self.subTest(action=action),self.assertRaises(AssertionError):c.verify_native_scope(self.scope,n,cur)


if __name__=='__main__':unittest.main()
