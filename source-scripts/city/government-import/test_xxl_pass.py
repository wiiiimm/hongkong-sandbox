"""First-pass routing must preserve exact installed work and reject stale/ambiguous IDs."""
import importlib.util
from pathlib import Path
import unittest
s=importlib.util.spec_from_file_location('xxl',Path(__file__).with_name('xxl-pass.py'))
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

class XXLRouteTests(unittest.TestCase):
    def setUp(self):
        self.e={'uid':'landsd/1:0','buildingCSUID':'one','objectId':1,'recordedBaseHeight':2,'recordedTopHeight':22,'sha256':'hash','overlapOfSmallerFootprint':1,'footprintCentroidDistanceMetres':.5}
        self.n={'model':{'candidate':self.e,'state':'packed-needs-placement-review'}}
        self.source={'building':{'uid':'landsd/1:0','buildingCSUID':'one','objectId':1,'baseHeightHKPD':2,'topHeightHKPD':22}}
    def test_existing_verified_exact_source_is_reused_under_original_acceptance(self):
        self.e['footprintCentroidDistanceMetres']=3
        self.assertEqual(m.initial_reason(self.n,self.source,{'state':'installed-verified','sha':'hash'},{'sha256':'hash'}),('installed',[]))
    def test_changed_identity_cannot_inherit_installation(self):
        self.source['building']['buildingCSUID']='changed'
        status,reasons=m.initial_reason(self.n,self.source,{'state':'installed-verified','sha':'hash'},{'sha256':'hash'})
        self.assertEqual(status,'held-unknown');self.assertIn('current-source-identity-changed',reasons)
    def test_missing_unique_candidate_has_no_invented_uid(self):
        self.n['model'].pop('candidate')
        self.assertEqual(m.initial_reason(self.n,None,None,None),('held-unknown',['no-unique-current-viewer-match']))
    def test_new_original_mesh_requires_strict_fit_but_no_ai(self):
        self.assertEqual(m.initial_reason(self.n,self.source,None,None),('in-process',[]))
        self.e['footprintCentroidDistanceMetres']=1.01
        self.assertEqual(m.initial_reason(self.n,self.source,None,None),('held-unknown',['strict-identity-fit']))
    def test_previous_hold_is_not_erased_by_new_batch(self):
        status,reasons=m.initial_reason(self.n,self.source,{'state':'held','sha':'hash'},None)
        self.assertEqual(status,'held-unknown');self.assertIn('existing-review-requires-resolution',reasons)
