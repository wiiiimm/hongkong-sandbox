import copy,types,unittest
from unittest.mock import patch
from fuying_five_member_terrain_stage_v1_20261029 import verify_review,publication_adapter,complete_boundary_validators,three,NEIGHBOURS,OLD_URL,boundary
class GroupContract(unittest.TestCase):
    def setUp(self):
        self.manifest={'path':'manifest','sha256':'m'};self.proof={'path':'proof','sha256':'p'}
        self.entries=[dict(source=str(i),sha256=str(i),destination='dest'+str(i))for i in range(5)]
        self.review=dict(status='approved-for-five-member-terrain-staging',currentManifest=self.manifest,wholeParentContract=self.proof,supersededURL=OLD_URL,supersededSHA256=boundary.OLD_SHA,sourceGeometryChanges=0,sourcePoseChanges=0,derivedTerrainConnectorFacetsAdded=39,allPriorTerrainPositionsAndIndicesPreserved=True,allSixFourWorldFoundationsPassed=True,all40FormsAnd9NativeRegressionsPassed=True,retainedNativeRows=[dict(uid=u,passed=True,terrain=dict(newlyWhollyBuried=0,newlyUpwardWhollyBuried=0))for u in sorted(NEIGHBOURS)],all40PrivateExportsActuallyViewed=True,replacementSources={e['source']:e['sha256']for e in self.entries},modelInstallationApproved=False)
    def verify(self):verify_review(self.review,self.manifest,self.proof,self.entries)
    def test_complete(self):self.verify()
    def test_missing_member(self):
        self.entries.pop()
        with self.assertRaises(AssertionError):self.verify()
    def test_changed_source(self):
        self.entries[0]['sha256']='changed'
        with self.assertRaises(AssertionError):self.verify()
    def test_duplicate_destination(self):
        self.entries[0]['destination']=self.entries[1]['destination']
        with self.assertRaises(AssertionError):self.verify()
    def test_retained_native_failure(self):
        self.review['retainedNativeRows'][0]['terrain']['newlyWhollyBuried']=1
        with self.assertRaises(AssertionError):self.verify()
    def test_unseen_images(self):
        self.review['all40PrivateExportsActuallyViewed']=False
        with self.assertRaises(AssertionError):self.verify()
    def test_cannot_turn_terrain_review_into_model_approval(self):
        self.review['modelInstallationApproved']=True
        with self.assertRaises(AssertionError):self.verify()
    def test_stale_manifest(self):
        self.review['currentManifest']={'sha256':'stale'}
        with self.assertRaises(AssertionError):self.verify()
    def test_original_retained_and_context_restored_on_exception(self):
        calls=[]
        def ordinary(*args):calls.append(args);raise ValueError('ordinary guard')
        pub=types.SimpleNamespace(stage_top_level_terrain=ordinary)
        with self.assertRaises(ValueError):
            with publication_adapter(pub):pub.stage_top_level_terrain({},1,2,3,4)
        self.assertIs(pub.stage_top_level_terrain,ordinary)
        self.assertFalse(hasattr(pub,'_fu_ying_group_adapter_active'))
        self.assertEqual(calls,[({},1,2,3,4)])
class ExistingPolicyDispatch(unittest.TestCase):
    def nodes(self):
        return [{'nativeMesh':{'source':{}}}, {'nativeMesh':{'source':{'coordinatedBoundary':{'policy':three.POLICY}}}}, {'nativeMesh':{'source':{'coordinatedBoundary':{'policy':boundary.POLICY}}}}]
    def test_both_groups_checked_with_ordinary_nodes(self):
        ordinary,chain,five=self.nodes()
        with patch.object(three,'validate_effective_coordinated_members')as a,patch.object(boundary,'validate_effective_coordinated_members')as b:
            with complete_boundary_validators():boundary.legacy.validate_effective_coordinated_members([ordinary,chain,five])
            a.assert_called_once_with([ordinary,chain]);b.assert_called_once_with([ordinary,five])
    def test_prior_group_failure_propagates(self):
        old=boundary.legacy.validate_effective_coordinated_members
        with patch.object(three,'validate_effective_coordinated_members',side_effect=AssertionError('missing prior chain')):
            with self.assertRaisesRegex(AssertionError,'missing prior chain'):
                with complete_boundary_validators():boundary.legacy.validate_effective_coordinated_members(self.nodes())
        self.assertIs(boundary.legacy.validate_effective_coordinated_members,old)
    def test_unknown_policy_rejected(self):
        node={'coarseCells':[0,0,1,1],'nativeMesh':{'source':{'coordinatedBoundary':{'policy':'unknown'}}}}
        with self.assertRaises(AssertionError):
            with complete_boundary_validators():boundary.legacy.validate_effective_coordinated_members([node])
if __name__=='__main__':unittest.main()
