import copy,unittest
from original_installed_support_model_only_contract_v1_20261027 import verify_metadata,verify_native_scope,verify_browser_native_scope

class Contract(unittest.TestCase):
 def setUp(self):
  self.sources={'tower':'tower-sha'};self.supports={'tower':'podium'}
  self.parent=dict(uid='podium',buildingCSUID='parent-csuid',sha256='parent-sha',triangles=100,rootTranslation=[-834500,0,816500],publicationApproved=True,sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True)
  self.current={'podium':self.parent}
  self.original={'tower':dict(uid='tower',sha256='tower-sha',rootTranslation=[-834500,0,816500],worldBounds=[[0,0,0],[1,1,1]],asset='assets/tower-sha.glb.gz')}
  self.models=[dict(self.original['tower'],priority='landmark',proceduralWindows=False,supportDependencies=[dict(uid='podium',state='installed',buildingCSUID='parent-csuid',sha256='parent-sha')])]
  self.scope=dict(uids=['tower'],currentManifestSHA256='manifest',rows=[dict(uid='tower',sourceSHA256='tower-sha',currentNativeActorsChecked=1,nearbyNativeActors=[dict(uid='podium',sourceSHA256='parent-sha')])])
  self.pair=dict(uid='tower',nativeUid='podium',sourceSHA256='tower-sha',nativeSHA256='parent-sha',rawCurrentNativeEntry=copy.deepcopy(self.parent),modes=[dict(mode=m,finiteContactPairs=2,positiveSurfaceContactPairs=1,areaContactPairs=0)for m in ['original','literal','leftF32','balancedF32']])
  self.contacts=dict(rows=[self.pair]);self.review=dict(sourceSpecificPhysicalInterpretationAccepted=True,rawCanonicalFailuresPreserved=True,sourceGeometryChanges=0,sourcePoseChanges=0,currentManifestSHA256='manifest',retainedNativeEntries=copy.deepcopy(self.current),unresolvedExternalBasicContacts=[],acceptedInstalledSupportContacts=[dict(uid='tower',nativeUid='podium',physicalInterpretationAccepted=True,rawContactSummary=copy.deepcopy(self.pair))])
 def metadata(self):return verify_metadata(self.models,self.sources,self.supports,self.original,self.current)
 def native(self):return verify_native_scope(self.scope,self.contacts,self.current,self.sources,self.supports,{'podium'},1,self.review)
 def browser_fixture(self):
  cfg=dict(terrain=[],additionalRetainedUids=['podium'],nativeSupportUidsByModel={'tower':['podium']})
  reports=[dict(passed=True,errors=[],retainedNativeOwnViews=[dict(uid='podium',time=t,width=w,active=True,visible=True,fullyFramed=True,fallbackFaces=0,sourceSHA256='parent-sha',originalTriangles=100,meshVisibility=[True],wireframeFlags=[False])for t in ['15:00','22:00']])for w in [1280,390]]
  return cfg,reports
 def test_complete_native_desktop_mobile_views(self):
  cfg,reports=self.browser_fixture();self.assertTrue(verify_browser_native_scope(cfg,self.sources,self.supports,{'podium'},self.current,reports))
 def test_mixed_viewport_report_rejects(self):
  cfg,reports=self.browser_fixture();reports[0]['retainedNativeOwnViews'][0]['width']=390
  with self.assertRaises(AssertionError):verify_browser_native_scope(cfg,self.sources,self.supports,{'podium'},self.current,reports)
 def test_retained_basic_fallback_rejects(self):
  cfg,reports=self.browser_fixture();reports[1]['retainedNativeOwnViews'][0]['fallbackFaces']=1
  with self.assertRaises(AssertionError):verify_browser_native_scope(cfg,self.sources,self.supports,{'podium'},self.current,reports)
 def test_exact_installed_parent_path(self):self.assertTrue(self.metadata());self.assertTrue(self.native())
 def test_dependency_omitted(self):
  self.models[0].pop('supportDependencies')
  with self.assertRaises(AssertionError):self.metadata()
 def test_parent_revision_changed(self):
  self.current['podium']['sha256']='new'
  with self.assertRaises(AssertionError):self.metadata()
  with self.assertRaises(AssertionError):self.native()
 def test_parent_on_hold(self):
  self.parent['publicationApproved']=False
  with self.assertRaises(AssertionError):self.metadata()
 def test_source_pose_changed(self):
  self.models[0]['verticalPlacementOffsetHKPD']=.1
  with self.assertRaises(AssertionError):self.metadata()
 def test_geometry_render_group_added(self):
  self.models[0]['renderGroups']=['partial']
  with self.assertRaises(AssertionError):self.metadata()
 def test_changed_native_contact_cannot_borrow_approval(self):
  self.pair['modes'][0]['finiteContactPairs']=3
  with self.assertRaises(AssertionError):self.native()
 def test_missing_coordinate_world(self):
  self.pair['modes'].pop()
  with self.assertRaises(AssertionError):self.native()
 def test_unreviewed_pair_rejects(self):
  self.review['acceptedInstalledSupportContacts']=[]
  with self.assertRaises(AssertionError):self.native()
 def test_external_basic_conflict_rejects(self):
  self.review['unresolvedExternalBasicContacts']=['foreign']
  with self.assertRaises(AssertionError):self.native()
 def test_stale_scene_rejects(self):
  self.review['currentManifestSHA256']='old'
  with self.assertRaises(AssertionError):self.native()
 def test_extra_native_pair_rejects(self):
  self.contacts['rows'].append(copy.deepcopy(self.pair))
  with self.assertRaises(AssertionError):self.native()
if __name__=='__main__':unittest.main()
