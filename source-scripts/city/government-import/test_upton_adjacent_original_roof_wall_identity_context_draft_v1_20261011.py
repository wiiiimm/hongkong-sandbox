"""DRAFT tests. Historical offline fixtures only; no DB/current worker/acceptance.

Do not run before ROOT review. Every evaluator case keeps full original source
triangles; mock only the immutable loader after independently reading its real
hash-bound fixture, then test the decision gates with temporary current files.
"""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
import upton_adjacent_original_roof_wall_identity_context_draft_v1_20261011 as P

ROOT=Path(__file__).resolve().parents[3]
IDENTITY=P.BASE+'government-xl-upton338946-podium12728-current-unchanged-owned-identity-v1-20261011/'
class DraftTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.context,cls.triangles=P.frozen_context(ROOT)
  cls.old=next(x for x in P.read(ROOT,IDENTITY+'identities.json')['rows'] if x['uid']==P.UID)['rawFullCellIdentity']
  cls.old_forms=P.read(ROOT,IDENTITY+'complete-current-forms.json.gz')['rows']
 def setUp(self):
  self.temp=TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
  self.proof=deepcopy(self.old);self.forms=deepcopy(self.old_forms);self.context_case=deepcopy(self.context)
  refs={}
  for label,path in [('manifest','3d-viewer/city/data/manifest.json'),('runtimeClosure','fixtures/runtime-closure.json'),('nativeCatalogue','fixtures/native.json'),('buildingSourceCatalogue','fixtures/source.json')]:
   p=self.root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(P.canonical({'fixture':label,'historicalOnly':True}));refs[label]=dict(path=path,sha256=P.digest(p.read_bytes()))
  for path,h in self.proof['exactRouteTileHashes'].items():
   p=self.root/'3d-viewer'/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/'3d-viewer'/path).read_bytes());self.assertEqual(P.digest(p.read_bytes()),h)
  self.proof['exactRouteManifestSHA256']=refs['manifest']['sha256']
  self.current=dict(manifestSHA256=refs['manifest']['sha256'],requiredFileRefs=refs)
 def assess(self):
  self.current['ordinaryProofCanonicalSHA256']=P.digest(P.canonical(self.proof));self.current['completeFormsCanonicalSHA256']=P.digest(P.canonical(self.forms))
  with patch.object(P,'frozen_context',return_value=(self.context,self.triangles)):
   return P.assess_draft(self.root,self.proof,self.forms,self.current,self.context_case,self.triangles)
 def reject(self):
  with self.assertRaises((AssertionError,StopIteration,KeyError,ValueError)):self.assess()
 def test_complete_named_fixture_retains_all_negatives_and_no_credit(self):
  r=self.assess();self.assertTrue(r['draftContextQualified']);self.assertEqual(r['rawOrdinaryIdentity'],self.proof);self.assertEqual(len(r['complete23ProperInteriorCrossingsRetained']),23)
  self.assertGreater(r['rawNamedGISExcessM2'],1);self.assertEqual(len(r['completeCurrentFormsRetained']),len(self.forms))
  for k in ['identityAccepted','physicalAccepted','installationApproved','sharedEdgeCredit','rootCredit','solidClearanceCredit','relatedForeignPhysicalExemption','authoredExactJointEstablished']:self.assertFalse(r[k])
 def test_other_ordinary_reason_is_never_removed(self):
  self.proof['reasons'].append('full-source-extent');r=self.assess();self.assertFalse(r['draftContextQualified']);self.assertEqual(r['proposedIdentityReasons'],['full-source-extent'])
 def test_wrong_source_revision(self):self.proof['sourceSHA256']='0'*64;self.reject()
 def test_wrong_complete_world(self):self.proof['worldTrianglesSHA256']='0'*64;self.reject()
 def test_wrong_owned_uid(self):self.proof['uid']=P.ADJACENT;self.reject()
 def test_provider_root_substitution(self):self.context_case['context']['providerRootContext'][0]['originalRoot']['matrix'][13]+=1;self.reject()
 def test_missing_original_crossing(self):self.context_case['roles']['complete23ContactsRetained'].pop();self.reject()
 def test_point_only_substitution(self):self.context_case['roles']['complete23ContactsRetained'][0]['originalContact']['dimension']=0;self.reject()
 def test_partial_contact_substitution(self):self.context_case['roles']['complete23ContactsRetained'][0]['originalContact']['exactPoints'].pop();self.reject()
 def test_fake_shared_edge_credit(self):self.context_case['roles']['complete23ContactsRetained'][0]['authoredBoundarySeamQualified']=True;self.reject()
 def test_missing_primary_plan(self):self.context_case['roles']['primaryContexts']=[];self.reject()
 def test_wrong_foreign_stable_csuid(self):next(x for x in self.forms if x['uid']==P.ADJACENT)['buildingCSUID']='wrong';self.reject()
 def test_new_unrelated_foreign_overlap_not_exempted(self):
  self.forms.append(dict(uid='landsd/999999:0',parent='different',rings=[[[-2400,-100],[-2200,-100],[-2200,100],[-2400,100],[-2400,-100]]],buildingCSUID='unknown'));self.reject()
 def test_whole_cell_failure(self):self.proof['exactWholeCellCoverage']['halves'][0]['exactProjectionCovered']=False;self.reject()
 def test_incomplete_source_count(self):self.proof['exactWholeCellCoverage']['wholeOriginalFacesAccounted']=1640;self.reject()
 def test_failed_original_graph(self):self.proof['originalOwnership']['sourceGraphVerified']=False;self.reject()
 def test_changed_current_manifest(self):(self.root/'3d-viewer/city/data/manifest.json').write_bytes(b'changed');self.reject()
 def test_changed_runtime(self):(self.root/self.current['requiredFileRefs']['runtimeClosure']['path']).write_bytes(b'changed');self.reject()
 def test_missing_current_catalogue_binding(self):del self.current['requiredFileRefs']['buildingSourceCatalogue'];self.reject()
 def test_stale_ordinary_form(self):next(x for x in self.forms if x['uid']==P.UID)['base']+=1;self.reject()
 def test_low_target_coverage(self):
  own=next(x for x in self.forms if x['uid']==P.UID);own['rings']=[[[-2400,-100],[-2200,-100],[-2200,100],[-2400,100],[-2400,-100]]];self.proof['exactCurrentComponentRoute']['source']['building']=deepcopy(own);self.reject()
 def test_excess_extent(self):
  own=next(x for x in self.forms if x['uid']==P.UID);own['rings']=[[[-2322,6],[-2321,6],[-2321,7],[-2322,7],[-2322,6]]];self.proof['exactCurrentComponentRoute']['source']['building']=deepcopy(own);self.reject()
 def test_projection_source_mutation(self):
  t={u:v.copy() for u,v in self.triangles.items()};t[P.UID][0,0,1]+=1
  self.current['ordinaryProofCanonicalSHA256']=P.digest(P.canonical(self.proof));self.current['completeFormsCanonicalSHA256']=P.digest(P.canonical(self.forms))
  with patch.object(P,'frozen_context',return_value=(self.context,self.triangles)),self.assertRaises(AssertionError):P.assess_draft(self.root,self.proof,self.forms,self.current,self.context_case,t)
if __name__=='__main__':unittest.main()
