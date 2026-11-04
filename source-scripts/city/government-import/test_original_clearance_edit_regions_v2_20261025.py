import unittest
from copy import deepcopy
import numpy as np
from run import digest
from original_clearance_edit_regions_v2_20261025 import edit_regions,verify_domain_sources


class RequiredEarthTests(unittest.TestCase):
 def setUp(self):
  tri=np.asarray([[[0.,2.,0.],[1.,2.,0.],[0.,2.,1.]],[[10.,2.,0.],[10.,20.,0.],[10.,20.,1.]]],dtype='<f8');self.worlds={m:tri.copy()for m in ['original','literal','left','balanced']};self.ground=np.asarray([[[0.,3.,0.],[20.,3.,0.],[0.,3.,20.]]],dtype='<f8');self.proofs={};self.caps={}
  for mode,t in self.worlds.items():
   source=digest(t.tobytes());ground=digest(self.ground.tobytes());self.proofs[mode]=dict(completeSourceFaces=2,sourceWorldSHA256=source,groundSHA256=ground,rows=[dict(sourceFace=i,vertices=t[i].tolist(),absoluteNormalYRatio=1 if i==0 else 0)for i in [0,1]])
   self.caps[mode]=dict(sourceWorldSHA256=source,actualGroundSHA256=ground,compoundGroundSHA256=ground,proof=dict(completeSourceFaces=2,negativeSourceFaces=[0,1],negativeNonWallFaces=[0],nonrenderingSourceFaces=[],paths=[dict(sourceFace=1,hasExactSharedEdgeClearCapPath=True)]))
 def test_complete_floor_and_wall_classification_is_retained(self):
  region,core,outer,bindings=edit_regions(self.worlds,self.ground,self.proofs,self.caps)
  self.assertTrue(core.covers(region));self.assertTrue(outer.covers(core));self.assertLess(core.bounds[2],5)
  for b in bindings:self.assertEqual(b['requiredEarthFixFaces'],[0]);self.assertEqual(b['retainedNegativeWallsWithExactClearCap'],[1]);self.assertEqual(b['allNegativeFaces'],[0,1])
 def test_global_nonrendering_inventory_does_not_change_negative_face_accounting(self):
  # A whole-source inventory may mention faces outside this negative partition.
  proofs=deepcopy(self.proofs);caps=deepcopy(self.caps);worlds=deepcopy(self.worlds)
  for mode in worlds:
   worlds[mode]=np.concatenate([worlds[mode],np.full((1,3,3),100.)])
   proofs[mode]['completeSourceFaces']=3;proofs[mode]['sourceWorldSHA256']=digest(worlds[mode].tobytes())
   caps[mode]['sourceWorldSHA256']=proofs[mode]['sourceWorldSHA256'];caps[mode]['proof']['completeSourceFaces']=3;caps[mode]['proof']['nonrenderingSourceFaces']=[2]
  _,_,_,bindings=edit_regions(worlds,self.ground,proofs,caps)
  for b in bindings:self.assertEqual(b['allNegativeFaces'],[0,1]);self.assertEqual(b['requiredEarthFixFaces'],[0])
 def test_a_failed_wall_path_requires_an_edit_instead_of_skip(self):
  caps=deepcopy(self.caps);caps['left']['proof']['paths'][0]['hasExactSharedEdgeClearCapPath']=False
  region,core,outer,bindings=edit_regions(self.worlds,self.ground,self.proofs,caps)
  self.assertGreater(core.bounds[2],10);self.assertEqual(next(b for b in bindings if b['mode']=='left')['requiredEarthFixFaces'],[0,1])
 def test_primary_parent_annotation_still_requires_all_exact_source_receipt_members(self):
  rows=[dict(uid='primary',sourceSHA256='a'*64),dict(uid='tower',sourceSHA256='b'*64)];context=dict(uids=['primary']);receipt=dict(uids=['tower','primary'],sourceSHA256ByUid={r['uid']:r['sourceSHA256']for r in rows})
  self.assertTrue(verify_domain_sources(context,receipt,'primary',rows,['primary','tower']))
  for bad in [dict(uids=['primary'],sourceSHA256ByUid={'primary':'a'*64}),dict(uids=['tower','primary'],sourceSHA256ByUid={'primary':'a'*64,'tower':'c'*64})]:
   with self.assertRaises(AssertionError):verify_domain_sources(context,bad,'primary',rows,['primary','tower'])
 def test_missing_faces_or_changed_cap_bindings_reject(self):
  for kind in ['missing-wall','missing-floor','ground','source','count']:
   caps=deepcopy(self.caps)
   if kind=='missing-wall':caps['original']['proof']['paths']=[]
   elif kind=='missing-floor':caps['original']['proof']['negativeNonWallFaces']=[]
   elif kind=='ground':caps['original']['actualGroundSHA256']='a'*64
   elif kind=='source':caps['original']['sourceWorldSHA256']='a'*64
   else:caps['original']['proof']['completeSourceFaces']=1
   with self.subTest(kind=kind),self.assertRaises(AssertionError):edit_regions(self.worlds,self.ground,self.proofs,caps)


if __name__=='__main__':unittest.main()
