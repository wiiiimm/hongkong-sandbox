import copy,hashlib,unittest
import test_exact_frozen_finite_chunk_hydration_draft_v1_20261012 as base
from exact_frozen_finite_chunk_prefix_draft_v1_20261012 import verify_prefixes,hydrate
class Tests(base.Tests):
 def test_final_output_mutation_rejected_without_proof_stripping(self):
  a,_=self.write();old,_=hydrate(self.root,[a],{0:0,1:0});key=hashlib.sha256(b'wg').hexdigest();final={key:dict(allWholeFacetProofs=copy.deepcopy(old[('w','g')]))};self.assertEqual(verify_prefixes(old,final),{'w':2});final[key]['allWholeFacetProofs'][0]['exactLowerM']='0'
  with self.assertRaises(AssertionError):verify_prefixes(old,final)
if __name__=='__main__':unittest.main()
