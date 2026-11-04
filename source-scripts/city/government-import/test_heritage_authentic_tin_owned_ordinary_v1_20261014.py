"""Candidate setup/binding only; no arrays, native sampler, render or DB."""
import copy,unittest
from unittest.mock import patch
import heritage165054_authentic_tin_owned_ordinary_v1_20261014 as a
class CandidateOwnedBindings(unittest.TestCase):
    def fixture(self):
        c=dict(path='private/patch.json',sha256='pinned',uids=[a.UID],cells=[528,306,532,309],bounds=[2492.5,-10047.5,2772.5,-9837.5],triangles=1)
        p=dict(uid=a.UID,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAccepted=False,installationApproved=False,construction=dict(bareExistingValidatorPassed=True,candidate=c))
        t=dict(coarseCells=c['cells'],w=3,h=3,meta=dict(targetUids=[a.UID],parentTerrain='city/data/terrain.json',georef=dict(W=3,H=3)),nativeMesh=dict(index=[0,1,2],source=dict(verticalScale=1)))
        return p,[c],t
    def test_exact_new_private_candidate_only(self):
        p,c,t=self.fixture();self.assertIs(a.bind_candidate(p,c,t),c[0])
    def test_bare_validator_failure_cannot_enter_owned_capture(self):
        p,c,t=self.fixture();p['construction']['bareExistingValidatorPassed']=False
        with self.assertRaises(AssertionError):a.bind_candidate(p,c,t)
    def test_wrong_owned_uid_cells_or_grid_dimensions_fail_closed(self):
        for k in ['uid','cells','grid']:
            p,c,t=self.fixture()
            if k=='uid':c[0]['uids']=['landsd/57455:0']
            if k=='cells':t['coarseCells']=[528,306,531,309]
            if k=='grid':t['meta']['georef']['W']=43
            with self.subTest(k=k),self.assertRaises(AssertionError):a.bind_candidate(p,c,t)
    def test_existing_scope_failure_fields_do_not_duplicate_or_transfer_acceptance(self):
        scope=dict(physicalAccepted=False,installationApproved=False,currentManifestSHA256=a.CURRENT,scope=dict(allActorsForNominationLease=[a.UID]))
        before=copy.deepcopy(scope)
        with patch.object(a,'ref',lambda p:dict(path='old-diagnostic',sha256='saved')):out=a.pending_scope_record(scope,dict(path='new-private'))
        self.assertEqual(scope,before);self.assertFalse(out['physicalAccepted']);self.assertFalse(out['installationApproved']);self.assertTrue(out['wholeNativeBASICBeforeAfterQualificationNotExecuted'])
    def test_actual_45_scope_resources_keep_osm_and_all_actors_without_DB(self):
        actors=a.read(a.BASE/'government-xl-heritage165054-authentic-tin-nomination-v1-20261014-proposal/draft-pins.json')['canonicalActors']
        from run import reservations
        with patch.object(reservations,'connect',side_effect=AssertionError('DB forbidden')):r=a.resources(actors)
        self.assertEqual(len(r),91);self.assertIn('foreign-form:way/261065256:0',r);self.assertIn('terrain-patch:way/261065256:0',r)
if __name__=='__main__':unittest.main()
