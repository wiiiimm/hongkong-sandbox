import copy,unittest
from run import ROOT,read,digest
from original_exact_replacement_routing_metadata_scope_20261010 import boundaries,verify_boundaries
BASE=ROOT/'docs/astra-city/government-import/government-xl-terrain-recovery-ching-hin-original-terrain-current-v3-20261010'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
class Routing(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.p=read(BASE/'current-source-terrain-preflight.json');cls.m=read(ROOT/'3d-viewer/city/data/manifest.json');cls.c=read(BASE/'terrain-candidates.json');cls.s=read(BASE/'exact-unchanged-adjacent-terrain-seams.json');cls.kw=dict(candidate_ref=ref(BASE/'terrain-candidates.json'),seam_ref=ref(BASE/'exact-unchanged-adjacent-terrain-seams.json'),manifest_ref=cls.p['currentManifest'],actual_assets={r['entry']['url']:dict(ref=r['asset'],data=read(ROOT/r['asset']['path'])) for r in cls.p['completeCurrentTerrainRouting']},proposal=read(ROOT/cls.c[0]['path']))
 def fixture(self):return copy.deepcopy((self.p,self.m,self.c,self.s,self.kw))
 def test_actual_complete_routing_and_seam(self):
  p,m,c,s,k=self.fixture();d=boundaries(p,m,c,s,**k);self.assertTrue(d);self.assertEqual(verify_boundaries(p,m,c,s,d,**k),{r['pointer'] for r in d})
 def test_numeric_asset_cannot_be_metadata(self):
  p,m,c,s,k=self.fixture();d=boundaries(p,m,c,s,**k);d[0]['pointer']=d[0]['pointer'].replace('/entry/source','/asset')
  with self.assertRaises(AssertionError):verify_boundaries(p,m,c,s,d,**k)
 def test_manifest_origin_changed(self):
  p,m,c,s,k=self.fixture();p['currentManifest']['sha256']='0'*64
  with self.assertRaises(AssertionError):boundaries(p,m,c,s,**k)
 def test_seam_missing(self):
  p,m,c,s,k=self.fixture();s['rows']=[]
  with self.assertRaises(AssertionError):boundaries(p,m,c,s,**k)
 def test_seam_mesh_changed(self):
  p,m,c,s,k=self.fixture();s['rows'][0]['proof']['binding']['completeProposalTrianglesSHA256']='0'*64
  with self.assertRaises(AssertionError):boundaries(p,m,c,s,**k)
 def test_parent_hash_changed(self):
  p,m,c,s,k=self.fixture();k['actual_assets'][c[0]['replaces']['url']]['ref']['sha256']='0'*64
  with self.assertRaises(AssertionError):boundaries(p,m,c,s,**k)
 def test_actor_or_routing_omitted(self):
  p,m,c,s,k=self.fixture();p['completeCurrentTerrainRouting'].pop()
  with self.assertRaises(AssertionError):boundaries(p,m,c,s,**k)
 def test_core_boundary_fabricated(self):
  p,m,c,s,k=self.fixture();d=boundaries(p,m,c,s,**k);d.append(dict(pointer='/immutableTerrainProposal',canonicalSHA256='0'*64))
  with self.assertRaises(AssertionError):verify_boundaries(p,m,c,s,d,**k)
 def test_candidate_identity_changed(self):
  p,m,c,s,k=self.fixture();c[0]['uids']=['landsd/1:0']
  with self.assertRaises(AssertionError):boundaries(p,m,c,s,**k)
 def test_positive_area_overlap_not_seam(self):
  p,m,c,s,k=self.fixture();url=s['rows'][0]['adjacentURL'];r=next(r for r in p['completeCurrentTerrainRouting'] if r['entry']['url']==url);r['testedBounds']=[c[0]['bounds']]
  with self.assertRaises(AssertionError):boundaries(p,m,c,s,**k)
if __name__=='__main__':unittest.main()
