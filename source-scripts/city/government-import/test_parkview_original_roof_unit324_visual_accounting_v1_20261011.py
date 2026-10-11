"""Actual complete provider/literal 72-face fixture plus rejection cases."""
import copy,unittest
import numpy as np
from run import ROOT,HERE,read
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from parkview_original_roof_unit324_visual_accounting_v1_20261011 import verify,canonical,sha,FACES,SOURCE
BASE=ROOT/'docs/astra-city/government-import'
class ActualSource(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  probe=BASE/'government-xl-terrain-recovery-parkview-block11-complete-original-current-probe-v1-20261010'
  rows=read(probe/'selection.json.gz')['rows'];original=np.concatenate([decode_original_world_triangles((ROOT/r['candidate']['path']).read_bytes())for r in rows])
  rt=read(HERE/'local'/probe.name/'runtime-geometry.json.gz');literal=np.concatenate([np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)]for r in rt['rows']])
  graph=read(BASE/'xl-terrain-recovery-20261010-parkview-block11-complete-original-support-v1/diagnostic.json.gz');host=graph['components'][285]['globalOriginalFaces']
  finite=next(r for r in read(BASE/'xl-terrain-recovery-20261010-parkview-authentic-two-TIN-complete-conservative-v3/diagnostic.json.gz')['rows']if r['uid']=='landsd/255647:0')
  diag=read(BASE/'xl-terrain-recovery-20261011-parkview-original-roof-unit324-interface-v1/diagnostic.json.gz')
  cls.fixtures=[]
  for t,key,r in zip([original,literal],['completeOriginal','actualRendered'],diag['rows']):
   contexts=[dict(sourceFace=i)for i in range(len(t))]
   for i,c in enumerate(finite['allFaces']):contexts[63133+i]={**c[key],'sourceFace':63133+i}
   role=dict(component=324,hostComponent=285,kind='parkview-original-mounted-roof-appendage-324',completeEveryOriginalBoundary=[e['originalBoundaryEdge']for e in r['completeEveryOriginalBoundaryEdge']],completeOriginalTripleIncidences=r['originalMoreThanTwoFaceIncidences'])
   support=dict(hostComponent=285,hostGroundedIndependentlyOfUnit324=True,creditedRootOrBridgeComponents=[285],qualification='Synthetic host-positive witness for source-role unit testing only; actual current adapter must independently ground host')
   data=[t,FACES,contexts,host,support,role];cls.fixtures.append((data,cls.binding(data)))
 @staticmethod
 def binding(d):
  t,f,c,h,s,r=d;return dict(ownedSourceSHA256=SOURCE,completeWorldSHA256=sha(t),completeComponentFacesSHA256=canonical(f),completeFacetContextsSHA256=canonical(c),completeHostFacesSHA256=canonical(h),independentHostSupportSHA256=canonical(s),sourceRoleTemplateSHA256=canonical(r))
 def replay(self,d,b):return verify(*d,expected_binding=b,current_binding=b)
 def changed(self,index,fn,rebind=False):
  d,b=copy.deepcopy(self.fixtures[0]);fn(d[index]);pin=self.binding(d)if rebind else b
  with self.assertRaises(AssertionError):self.replay(d,pin)
 def test_actual_provider72_all_edges_preserved(self):
  d,b=self.fixtures[0];r=self.replay(d,b);self.assertEqual(r['upperOpeningsOutsideBandPreserved'],2);self.assertFalse(r['addedRootOrBridgeCredit']);self.assertFalse(r['closedSolidCertified'])
 def test_actual_literal72_all_edges_preserved(self):
  d,b=self.fixtures[1];r=self.replay(d,b);self.assertEqual(len(r['completeEveryOriginalBoundaryProof']),8)
 def test_omitted_original_face(self):self.changed(1,lambda f:f.pop(),True)
 def test_changed_pose_stale_binding(self):self.changed(0,lambda t:t.__setitem__((FACES[0],0,0),t[FACES[0],0,0]+.01))
 def test_tampered_current_ground_keeps_old_pin(self):self.changed(2,lambda c:c[FACES[0]].update(exactCertifiedLowerClearanceM=-100))
 def test_true_whole_facet_failure(self):self.changed(2,lambda c:c[FACES[0]].update(exactCertifiedLowerClearanceM=-.501,existingOrdinaryClearanceBoundProved=False),True)
 def test_missing_coverage(self):self.changed(2,lambda c:c[FACES[0]].update(groundProjectionCovered=False),True)
 def test_ungrounded_host(self):self.changed(4,lambda s:s.update(hostGroundedIndependentlyOfUnit324=False),True)
 def test_visual_unit_used_as_bridge(self):self.changed(4,lambda s:s['creditedRootOrBridgeComponents'].append(324),True)
 def test_unrelated_host_component(self):self.changed(4,lambda s:s.update(hostComponent=286),True)
 def test_missing_mount_edge(self):self.changed(5,lambda r:r['completeEveryOriginalBoundary'].pop(),True)
 def test_triple_incidence_erased(self):self.changed(5,lambda r:r['completeOriginalTripleIncidences'].clear(),True)
 def test_invented_equipment_role(self):self.changed(5,lambda r:r.update(kind='generic-equipment'),True)
 def test_context_face_hash_changed(self):self.changed(2,lambda c:c[FACES[0]].update(sourceFaceSHA256='0'*64),True)
 def test_source_sha_change(self):
  d,b=self.fixtures[0];b={**b,'ownedSourceSHA256':'0'*64}
  with self.assertRaises(AssertionError):self.replay(d,b)
 def test_mount_detached_even_with_rebound_numeric_shape(self):
  d,b=copy.deepcopy(self.fixtures[0]);d[0][FACES,:,1]+=.2
  with self.assertRaises(AssertionError):self.replay(d,self.binding(d))
if __name__=='__main__':unittest.main()
