import contextlib,io,tempfile,unittest,random
from pathlib import Path
from fractions import Fraction as F
from exact_resumable_projected_inventory_v1_20261011 import Checkpoints,atomic,overlaps,candidate_pairs,integer_coordinates,positive_aabb,interiors_separated,raw,read,atomic_write
from exact_source_core_ten_metre_transition_domain_v1_20261011 import atomic as reference_atomic,intersection
from exact_original_projection_coverage_v2_20261010 import signed_area

class ExactInventoryTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.folder=Path(self.tmp.name)
 def checkpoint(self,ps,name='test',check=lambda:None,size=2):return Checkpoints(self.folder/name,ps,[dict(path='fixed-source',sha256='a'*64)],check,size)
 def run_atomic(self,ps,name='atomic'):
  with contextlib.redirect_stdout(io.StringIO()):return atomic(ps,self.checkpoint(ps,name))
 def assert_reference(self,ps):self.assertEqual(raw(self.run_atomic(ps)[0]),raw(reference_atomic(ps)))
 def test_partition_complete_pair_nomination(self):
  ps=[[(F(x),F(0)),(F(x+2),F(0)),(F(x),F(2))]for x in [-12,-5,0,1,10,31]];ints,den=integer_coordinates(ps);pairs,_=candidate_pairs(ints,den)
  for i,p in enumerate(ps):
   for j in range(i):
    if signed_area(intersection(p,ps[j]))>0:self.assertIn((j,i),pairs)
  with contextlib.redirect_stdout(io.StringIO()):bad,c=overlaps(ps,self.checkpoint(ps))
  self.assertEqual(c['completeUnorderedPairs'],15);self.assertEqual(c['completeClosedBucketCandidatePairs']+c['excludedExactBucketDisjointPairs'],15);self.assertEqual([r['pieces']for r in bad],[[2,3]])
 def test_touch_only_not_positive(self):self.assert_reference([[(0,0),(5,0),(0,5)],[(5,0),(5,5),(0,5)]])
 def test_contained_and_duplicate_positive_preserved(self):self.assert_reference([[(0,0),(8,0),(0,8)],[(0,0),(8,0),(0,8)],[(1,1),(2,1),(1,2)]])
 def test_narrow_exact_overlap(self):
  eps=F(1,2**80);self.assert_reference([[(0,0),(1,0),(0,1)],[(1-eps,0),(2,0),(1-eps,1)]])
 def test_non_dyadic_coordinates(self):self.assert_reference([[(F(-1,3),0),(F(2,3),0),(F(-1,3),1)],[(0,0),(1,0),(0,1)]])
 def test_t_junction_complete_source_edge_split(self):self.assert_reference([[(0,0),(10,0),(0,10)],[(10,0),(10,5),(5,5)],[(5,5),(10,5),(0,10)]])
 def test_disjoint_islands_no_point_bridge(self):self.assert_reference([[(0,0),(1,0),(0,1)],[(10,10),(11,10),(10,11)]])
 def test_point_touch_branch_retained(self):
  ps=[[(0,0),(1,0),(0,1)],[(0,0),(-1,0),(0,-1)]];r,_=self.run_atomic(ps);self.assertFalse(r['projectedTopologyQualified']);self.assertTrue(r['allBranchPoints']);self.assert_reference(ps)
 def test_reversed_winding_rejected(self):
  with self.assertRaises(AssertionError):self.run_atomic([[(0,0),(0,1),(1,0)]])
 def test_resume_exact_identical_outputs(self):
  ps=[[(0,0),(5,0),(0,5)],[(5,0),(5,5),(0,5)]];first=self.run_atomic(ps);second=self.run_atomic(ps);self.assertEqual(raw(first),raw(second));self.assertGreater(len(list((self.folder/'atomic').rglob('*.json.gz'))),2)
 def test_changed_source_contract_rejected(self):
  self.checkpoint([[(0,0),(1,0),(0,1)]])
  with self.assertRaises(AssertionError):self.checkpoint([[(0,0),(2,0),(0,1)]])
 def test_changed_chunk_payload_rejected(self):
  ps=[[(0,0),(1,0),(0,1)]];self.run_atomic(ps);p=next((self.folder/'atomic/whole-source-edge-cuts').glob('*.json.gz'));v=read(p);v['payload'][0]['cuts']=[F(0),F(1,2),F(1)];atomic_write(p,v)
  with self.assertRaises(AssertionError):self.run_atomic(ps)
 def test_changed_chunk_partition_rejected(self):
  ps=[[(0,0),(1,0),(0,1)]];self.run_atomic(ps);p=next((self.folder/'atomic/whole-source-edge-cuts').glob('*.json.gz'));v=read(p);v['binding']['start']=1;atomic_write(p,v)
  with self.assertRaises(AssertionError):self.run_atomic(ps)
 def test_live_input_fence_fails_before_reuse(self):
  ps=[[(0,0),(1,0),(0,1)]];self.run_atomic(ps)
  def changed():raise AssertionError('Changed authoritative input')
  with self.assertRaises(AssertionError):self.checkpoint(ps,'atomic',changed)
 def test_exact_sat_against_complete_clip(self):
  rng=random.Random(71);ps=[]
  for _ in range(25):
   x,z=rng.randrange(-20,20),rng.randrange(-20,20);w,h=rng.randrange(1,10),rng.randrange(1,10);ps.append([(F(x),F(z)),(F(x+w),F(z)),(F(x),F(z+h))])
  ints,den=integer_coordinates(ps)
  for i,p in enumerate(ps):
   for j in range(i):self.assertEqual(not interiors_separated(ints[i],ints[j]),signed_area(intersection(p,ps[j]))>0)
 def test_integer_aabb_touch_or_gap_is_zero(self):
  self.assertFalse(positive_aabb((0,1,0,1),(1,2,0,1)));self.assertFalse(positive_aabb((0,1,0,1),(2,3,0,1)));self.assertTrue(positive_aabb((0,2,0,2),(1,3,1,3)))

if __name__=='__main__':unittest.main()
