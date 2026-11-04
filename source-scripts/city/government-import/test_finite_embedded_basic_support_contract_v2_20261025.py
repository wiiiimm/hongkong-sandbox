import copy,hashlib,unittest
import numpy as np
from finite_embedded_basic_support_contract_v2_20261025 import verify_mode
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
class Contract(unittest.TestCase):
 def setUp(self):
  self.t=np.array([[[0,0,0],[1,0,0],[0,0,1]],[[0,0,0],[1,0,0],[0,2,0]]],dtype='<f8')
  self.p=np.array([[[-1,.35,-1],[2,.35,-1],[-1,.35,2]]],dtype='<f8')
  contact=exact_finite_contacts(self.t,[1],self.p,[0])['contacts'][0]
  from fractions import Fraction
  end=np.asarray([[float(Fraction(z))for z in q]for q in contact['exactPoints']]).mean(0).tolist()
  witness=dict(position=[.2,0,.2],gap=-.35,reason='support-above-rim')
  self.c=dict(passed=False,maximumEmbeddingM=.5,strictContacts=0,wallIntersections=1,samples=2,unresolved=[witness])
  v=dict(faces=[0,1],continuousPath=[witness['position'],[.5,0,0],end],maximumPathHeightM=.35,endpointHeightCeilingM=.35,maximumResidualM=0,withinEndpointHeight=True,contact=contact)
  self.d=dict(sourceWorldSHA256=hashlib.sha256(self.t.tobytes()).hexdigest(),supportWorldSHA256=hashlib.sha256(self.p.tobytes()).hexdigest(),sourceFaces=2,supportFaces=1,strictInterfacePassed=False,targets=1,verifiedPaths=1,remaining=0,rows=[dict(witness=witness,verifiedPath=v)])
 def test_positive_keeps_canonical_false_and_inputs_unchanged(self):
  before=copy.deepcopy((self.c,self.d));r=verify_mode(self.t,self.p,self.c,self.d);self.assertFalse(r['strictCanonicalPassed']);self.assertEqual(r['verifiedPaths'],1);self.assertEqual(before,(self.c,self.d))
 def test_stale_geometry_or_world_binding_rejected(self):
  for key in ['sourceWorldSHA256','supportWorldSHA256']:
   d=copy.deepcopy(self.d);d[key]='stale'
   with self.assertRaises(AssertionError):verify_mode(self.t,self.p,self.c,d)
 def test_floating_or_nonunderside_target_rejected(self):
  for reason,gap in [('floating',-.35),('support-above-rim',.1),('support-above-rim',-.6)]:
   c=copy.deepcopy(self.c);d=copy.deepcopy(self.d);c['unresolved'][0].update(reason=reason,gap=gap);d['rows'][0]['witness']=copy.deepcopy(c['unresolved'][0])
   with self.assertRaises(AssertionError):verify_mode(self.t,self.p,c,d)
 def test_no_wall_or_changed_limit_rejected(self):
  for key,value in [('wallIntersections',0),('maximumEmbeddingM',.6),('strictContacts',1)]:
   c=copy.deepcopy(self.c);c[key]=value
   with self.assertRaises(AssertionError):verify_mode(self.t,self.p,c,self.d)
 def test_missing_path_or_targets_rejected(self):
  for key,value in [('verifiedPaths',0),('targets',0),('rows',[])]:
   d=copy.deepcopy(self.d);d[key]=value
   with self.assertRaises(AssertionError):verify_mode(self.t,self.p,self.c,d)
 def test_point_contact_or_wrong_endpoint_rejected(self):
  for mutate in [lambda v:v['contact'].update(dimension=0),lambda v:v['continuousPath'][-1].__setitem__(1,.3),lambda v:v.update(withinEndpointHeight=False),lambda v:v.update(maximumResidualM=.002)]:
   d=copy.deepcopy(self.d);mutate(d['rows'][0]['verifiedPath'])
   with self.assertRaises(AssertionError):verify_mode(self.t,self.p,self.c,d)
 def test_fully_buried_geometry_rejected_even_with_rebound_hash(self):
  t=self.t.copy();t[1,2,1]=.2;d=copy.deepcopy(self.d);d['sourceWorldSHA256']=hashlib.sha256(t.tobytes()).hexdigest()
  with self.assertRaises(AssertionError):verify_mode(t,self.p,self.c,d)
 def test_nonfinite_and_excessively_deep_geometry_rejected(self):
  for value in [float('nan'),-.6]:
   t=self.t.copy();t[0,0,1]=value;d=copy.deepcopy(self.d);d['sourceWorldSHA256']=hashlib.sha256(t.tobytes()).hexdigest()
   with self.assertRaises(AssertionError):verify_mode(t,self.p,self.c,d)
 def test_overhang_path_preserves_no_vertical_support(self):
  self.c['unresolved'][0].update(reason='no-vertical-support',gap=None)
  self.d['rows'][0]['witness']=copy.deepcopy(self.c['unresolved'][0]);before=copy.deepcopy((self.c,self.d))
  result=verify_mode(self.t,self.p,self.c,self.d);self.assertEqual(result['verifiedPaths'],1);self.assertFalse(result['strictCanonicalPassed']);self.assertEqual(before,(self.c,self.d))
 def test_overhang_missing_gap_is_preserved(self):
  self.c['unresolved'][0].update(reason='no-vertical-support');self.c['unresolved'][0].pop('gap')
  self.d['rows'][0]['witness']=copy.deepcopy(self.c['unresolved'][0]);before=copy.deepcopy((self.c,self.d))
  self.assertEqual(verify_mode(self.t,self.p,self.c,self.d)['verifiedPaths'],1);self.assertEqual(before,(self.c,self.d))
 def test_overhang_does_not_invent_vertical_gap(self):
  self.c['unresolved'][0].update(reason='no-vertical-support',gap=-.35)
  self.d['rows'][0]['witness']=copy.deepcopy(self.c['unresolved'][0])
  with self.assertRaises(AssertionError):verify_mode(self.t,self.p,self.c,self.d)
if __name__=='__main__':unittest.main()
