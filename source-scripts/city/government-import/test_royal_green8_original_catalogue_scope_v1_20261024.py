import copy,unittest
from royal_green8_original_catalogue_scope_v1_20261024 import SOURCES,SUPPORTS,verify_metadata,verify_native_scope
class ScopeTests(unittest.TestCase):
 def models(self):
  ms=[dict(uid=u,sha256=h,buildingCSUID=u,proceduralWindows=False,rootTranslation=[-834500,0,816500])for u,h in SOURCES.items()]
  for m in ms:
   if m['uid']in SUPPORTS:
    p=SUPPORTS[m['uid']];m['supportDependencies']=[dict(uid=p,state='installed',buildingCSUID=p,sha256=SOURCES[p])]
  return ms
 def test_exact_original_graph(self):self.assertTrue(verify_metadata(self.models()))
 def test_missing_or_wrong_parent(self):
  for mutate in [lambda m:m.pop('supportDependencies'),lambda m:m['supportDependencies'][0].update(sha256='wrong')]:
   ms=self.models();mutate(ms[0])
   with self.assertRaises(AssertionError):verify_metadata(ms)
 def test_scope_or_pose_changes_rejected(self):
  for k,v in [('sha256','bad'),('verticalPlacementOffsetHKPD',1),('proceduralWindows',True),('suppressesBuildingUids',['other']),('partialSource',True)]:
   ms=self.models();ms[0][k]=v
   with self.assertRaises(AssertionError):verify_metadata(ms)
 def test_sixth_source_rejected(self):
  ms=self.models();ms.append({**ms[0],'uid':'other'})
  with self.assertRaises(AssertionError):verify_metadata(ms)
 def test_empty_nearby_scope_requires_all_current(self):
  scope=dict(uids=list(SOURCES),rows=[dict(uid=u,sourceSHA256=h,currentNativeActorsChecked=6902,nearbyNativeActors=[])for u,h in SOURCES.items()]);native=dict(nativeCompleteFourWorldSeparation=[],independentlyMeasuredOverlappingNativePairs=[]);current={str(i):{}for i in range(6902)}
  self.assertTrue(verify_native_scope(scope,native,current))
  bad=copy.deepcopy(scope);bad['rows'][0]['nearbyNativeActors']=[{'uid':'1'}]
  with self.assertRaises(AssertionError):verify_native_scope(bad,native,current)
  with self.assertRaises(AssertionError):verify_native_scope(scope,native,{})
if __name__=='__main__':unittest.main()
