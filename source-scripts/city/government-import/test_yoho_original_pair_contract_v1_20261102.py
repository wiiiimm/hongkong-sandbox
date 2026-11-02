import copy,unittest
from yoho_original_pair_contract_v1_20261102 import SOURCES,SUPPORTS,FACES,verify_models,verify_targets,verify_atomic
class YohoContractTests(unittest.TestCase):
 def setUp(self):
  self.models=[dict(uid=u,sha256=s,triangles=FACES[u],buildingCSUID=u,proceduralWindows=False,rootTranslation=[-834500,0,816500],activationGroup=sorted(SOURCES))for u,s in SOURCES.items()]
  self.models[1]['supportDependencies']=[dict(uid=self.models[0]['uid'],state='installed',buildingCSUID=self.models[0]['buildingCSUID'],sha256=self.models[0]['sha256'])]
  self.prior=dict(meta=dict(targetUids=['landsd/189427:0'],parentTerrain='root',parentSha256='x'),coarseCells=[306,197,316,201]);self.candidate=copy.deepcopy(self.prior);self.candidate['meta']['targetUids']+=['landsd/273672:0']
 def test_exact_lower_ground_owner_and_original_support_graph(self):self.assertTrue(verify_models(self.models));self.assertTrue(verify_targets(self.prior,self.candidate))
 def test_reject_unavailable_peer(self):
  self.models[1]['activationGroup']=[self.models[1]['uid']]
  with self.assertRaises(AssertionError):verify_models(self.models)
 def test_reject_changed_original(self):
  self.models[0]['sha256']='f'*64
  with self.assertRaises(AssertionError):verify_models(self.models)
 def test_reject_missing_physical_support(self):
  self.models[1].pop('supportDependencies')
  with self.assertRaises(AssertionError):verify_models(self.models)
 def test_reject_upper_actor_as_terrain_owner(self):
  self.candidate['meta']['targetUids']+=['landsd/3007:0']
  with self.assertRaises(AssertionError):verify_targets(self.prior,self.candidate)
 def test_reject_lost_retained_target(self):
  self.candidate['meta']['targetUids']=['landsd/273672:0']
  with self.assertRaises(AssertionError):verify_targets(self.prior,self.candidate)
 def test_reject_partial_atomic_frame(self):
  ids=sorted(SOURCES);base=dict(baseOnlyRestoredCompleteGroup=True,completeGroupEvicted=True,failureKeptAllBasics=True,sources=[dict(uid=m['uid'],sha256=m['sha256'],triangles=m['triangles'],active=True)for m in self.models],audit=dict(frames=4,violations=[],transitions=[dict(active=[]),dict(active=ids),dict(active=[])]))
  cases=[dict(copy.deepcopy(base),width=w,failedUid=u)for w,u in [(1280,None),(390,ids[0]),(390,ids[1])]];r=dict(passed=True,pageErrors=[],cases=cases);self.assertTrue(verify_atomic(r,self.models));r['cases'][1]['audit']['transitions'][1]['active']=[ids[0]]
  with self.assertRaises(AssertionError):verify_atomic(r,self.models)
if __name__=='__main__':unittest.main()

class AuthoredJunctionTests(unittest.TestCase):
 def setUp(self):
  import json
  from pathlib import Path
  from yoho_original_pair_contract_v1_20261102 import verify_authored_junction
  self.verify=verify_authored_junction
  base=Path(__file__).resolve().parents[3]/'docs/astra-city/government-import'
  prefix='government-xl-yoho-mall-ii273672-'
  names=['two-originals-v2-20261102-support','original-rooftop-roots-v1-20261102-paths','rooftop-compound-face-census-v1-20261102-faces','original-rooftop-pair-context-v1-20261102']
  self.e=[json.loads((base/(prefix+n)/'summary.json').read_text())for n in names]
 def test_actual_frozen_original_case(self):self.assertTrue(self.verify(*self.e))
 def test_reject_buried_floor(self):
  self.e[2]['rows'][0]['fullyBuriedUpwardFaceIds']=[10]
  with self.assertRaises(AssertionError):self.verify(*self.e)
 def test_reject_unknown_buried_face(self):
  self.e[2]['rows'][0]['fullyBuriedFaceIds']=[11]
  with self.assertRaises(AssertionError):self.verify(*self.e)
 def test_reject_raised_support_path(self):
  self.e[1]['rows'][0]['aboveExistingEndpointCeiling']=1
  with self.assertRaises(AssertionError):self.verify(*self.e)
 def test_reject_changed_world_arrays(self):
  self.e[2]['rows'][0]['sourceWorldSHA256ByUid']['landsd/3007:0']='f'*64
  with self.assertRaises(AssertionError):self.verify(*self.e)
 def test_reject_unreviewed_area_contact(self):
  self.e[3]['rows'][0]['contactDimensions']['2']=1
  with self.assertRaises(AssertionError):self.verify(*self.e)
