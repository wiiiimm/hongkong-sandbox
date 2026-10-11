"""Hermetic exact actual captured catalogue refs, including renderer URL origins."""
import unittest,copy
from run import ROOT,read
from exact_current_delta_catalogue_reference_binding_20261011 import verify_delta_catalogue_refs
BASE=ROOT/'docs/astra-city/government-import'
class CatalogueReferenceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.delta=read(BASE/'government-xl-complete-native-actual-position-post-block6-delta-v1-20261011/input.json.gz')['currentCatalogueRefs']
  cls.regional=read(BASE/'government-xl-lippo-tower-only-current-complete-inputs-v4-20261011/input.json.gz')['currentCatalogueRefs']
  cls.manifest=dict(officialModelCatalogues=[r['path'].removeprefix('3d-viewer/') for r in cls.regional])
 def reject(self,fn):
  a=copy.deepcopy([self.delta,self.regional,self.manifest]);fn(a)
  with self.assertRaises((AssertionError,KeyError,ValueError,TypeError)):verify_delta_catalogue_refs(*a)
 def test_complete_actual_two_schemas_with_exact_url_origins(self):self.assertTrue(verify_delta_catalogue_refs(self.delta,self.regional,self.manifest))
 def test_tampered_original_path(self):self.reject(lambda a:a[0][0].update(originalPath='3d-viewer/other.json'))
 def test_reordered_delta(self):self.reject(lambda a:a[0].reverse())
 def test_reordered_regional(self):self.reject(lambda a:a[1].reverse())
 def test_reordered_both_not_manifest(self):self.reject(lambda a:(a[0].reverse(),a[1].reverse()))
 def test_omitted_delta(self):self.reject(lambda a:a[0].pop())
 def test_omitted_regional(self):self.reject(lambda a:a[1].pop())
 def test_duplicate_current_path(self):self.reject(lambda a:a[0].__setitem__(-1,copy.deepcopy(a[0][0])))
 def test_tampered_delta_sha(self):self.reject(lambda a:a[0][0].update(sha256='0'*64))
 def test_tampered_regional_sha(self):self.reject(lambda a:a[1][0].update(sha256='0'*64))
 def test_non_sha_both(self):self.reject(lambda a:(a[0][0].update(sha256='invalid'),a[1][0].update(sha256='invalid')))
 def test_extra_unbound_delta_role(self):self.reject(lambda a:a[0][0].update(role='something'))
 def test_missing_renderer_original_path(self):self.reject(lambda a:a[0][0].pop('originalPath'))
 def test_manifest_missing_catalogue(self):self.reject(lambda a:a[2]['officialModelCatalogues'].pop())
if __name__=='__main__':unittest.main()
