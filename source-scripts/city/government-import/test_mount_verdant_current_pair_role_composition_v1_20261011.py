"""Actual complete15579-source composition and independent adversarial inputs."""
import copy,json,unittest
import numpy as np
from run import ROOT,HERE,read,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from mount_verdant_current_pair_role_composition_v1_20261011 import verify,canonical,sha,SOURCE_T,SOURCE_P
BASE=ROOT/'docs/astra-city/government-import'

def fixture(mode='providerOriginal'):
 physical=BASE/'government-xl-terrain-recovery-mount-verdant-pair-authentic-current-v1-20261011';capture=BASE/'xl-terrain-recovery-20261011-mount-verdant-two-current-render-attribute-capture-v2'
 selection=read(physical/'selection.json.gz')['rows'];actual=read(capture/'actual-render-attributes.json.gz')['rows'];parts=[]
 for row,a in zip(selection,actual):
  asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']==a['sourceSHA256']
  if mode=='providerOriginal':parts.append(decode_original_world_triangles(asset.read_bytes()))
  else:
   key={'capturedLiteral':'completeLiteralWorldPosition','explicitLeftAssociatedF32ModelMatrix':'completeExplicitLeftAssociatedFloat32WorldPosition','explicitBalancedF32ModelMatrix':'completeExplicitBalancedFloat32WorldPosition'}[mode]
   parts.append(np.asarray(a[key],float).reshape(-1,3)[np.asarray(a['completeOriginalIndex'],int).reshape(-1,3)])
 tri=np.concatenate(parts);graph=read(BASE/'xl-terrain-recovery-20261011-mount-verdant-complete-original-edge-contact-graph-v1/diagnostic.json.gz')
 finite=read(BASE/'xl-terrain-recovery-20261011-mount-verdant-pair-current-four-stream-finite-grade-v1/diagnostic.json.gz')
 f=[next(r for r in finite['rows'] if r['uid']==u and r['mode']==mode) for u in ['landsd/261717:0','landsd/75782:0']]
 restricted=next(r for r in read(BASE/'xl-terrain-recovery-20261011-mount-verdant-four-stream-restricted-source-contacts-v1/diagnostic.json.gz')['rows'] if r['mode']==mode)
 roofmode={'providerOriginal':'untouched-provider-original','capturedLiteral':'captured-literal','explicitLeftAssociatedF32ModelMatrix':'explicit-left-associated-Float32','explicitBalancedF32ModelMatrix':'explicit-balanced-Float32'}[mode]
 roof=[r for r in read(BASE/'xl-terrain-recovery-20261011-mount-verdant-three-open-bottom-four-stream-roof-perimeters-v1/diagnostic.json.gz')['allThreeCompleteOpenBottomsEveryFourStreams'] if r['mode']==roofmode]
 ground=np.asarray(read(HERE/'local'/physical.name/'runtime-geometry.json.gz')['rows'][1]['drawnGroundGeometry'],float).reshape(-1,3,3)
 return [tri,mode,graph['components'],graph['exactNonrenderingGlobalFacesRetained'],f,restricted,roof,ground]

def binding(a):
 tri,mode,components,zero,finite,restricted,roof,ground=a
 return dict(sourceSHA256ByUID={'landsd/261717:0':SOURCE_T,'landsd/75782:0':SOURCE_P},complete15579WorldSHA256=sha(tri),complete973ComponentsSHA256=canonical(components),completeZeroFaceIDsSHA256=canonical(zero),completeCurrentFiniteRowsSHA256=canonical(finite),restrictedNonvisualSourceGraphSHA256=canonical(restricted),completeRoofPerimeterTemplatesSHA256=canonical(roof),completeActualPodiumGroundSHA256=sha(ground))

class ActualCompleteSourceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.a=fixture();cls.b=binding(cls.a)
 def rejects(self,a,b=None):
  b=b or binding(a)
  with self.assertRaises(AssertionError):verify(*a,expected_binding=b,current_binding=b)
 def test_actual_complete_original_composition(self):
  r=verify(*self.a,expected_binding=self.b,current_binding=self.b)
  self.assertTrue(r['nonrenderingFacetsReceiveNoSupportCredit']);self.assertTrue(r['all973NonzeroBodiesAccounted']);self.assertEqual(len(r['completeIndependentNonvisualBodies']),764);self.assertEqual(len(r['all204VisualBackingRoles']['rows']),204);self.assertEqual(len(r['allTwoPodiumVisualBackingRoles']['rows']),2);self.assertEqual(r['threeActualOriginalOpenBottomRoofPerimeters']['sourceRoofFootingComponents'],[311,312,313]);self.assertFalse(r['visualRootOrBridgeCredit']);self.assertFalse(r['installationApproved'])
 def test_tampered_context_with_stale_binding(self):
  a=copy.deepcopy(self.a);a[4][1]['completeAllOriginalFacetContexts'][0]['maximumObservedGapM']+=1;self.rejects(a,self.b)
 def test_removed_component_face_even_rebound(self):
  a=copy.deepcopy(self.a);a[2][0]['globalOriginalFaces'].pop();self.rejects(a)
 def test_wrong_actor_uid_even_rebound(self):
  a=copy.deepcopy(self.a);a[4][0]['uid']='landsd/75782:0';self.rejects(a)
 def test_tower_ordinary_failure_even_rebound(self):
  a=copy.deepcopy(self.a);a[4][0]['allFaces'][0]['completeOriginalBoundProved']=False;self.rejects(a)
 def test_missing_finite_ground_even_rebound(self):
  a=copy.deepcopy(self.a);a[4][0]['allFaces'][0]['priorCoarseBoundProofVerbatim']['completeOriginal']['groundProjectionCovered']=False;self.rejects(a)
 def test_no_podium_grade_even_rebound(self):
  a=copy.deepcopy(self.a);a[4][1]['complete576MainPodiumGradeInterfaces']=[];self.rejects(a)
 def test_changed_actual_ground_even_rebound(self):
  a=copy.deepcopy(self.a);a[7][0,0,1]+=1;self.rejects(a)
 def test_visual_bridge_forbidden_even_rebound(self):
  a=copy.deepcopy(self.a);a[5]['completeRestrictedOriginalInterfaceReplays'][0]['components'][0]=967;self.rejects(a)
 def test_missing_nonvisual_body_even_rebound(self):
  a=copy.deepcopy(self.a);a[5]['nonvisualAllowedComponents'].pop();self.rejects(a)
 def test_invented_positive_contact_even_rebound(self):
  a=copy.deepcopy(self.a);a[5]['completeRestrictedOriginalInterfaceReplays'][0]['selectedCurrentRepresentationExactContact']['dimension']=2;self.rejects(a)
 def test_zero_cannot_be_contact_endpoint_even_rebound(self):
  a=copy.deepcopy(self.a);a[5]['completeRestrictedOriginalInterfaceReplays'][0]['selectedCurrentRepresentationWitnessGlobalFaces'][0]=a[3][0];self.rejects(a)
 def test_changed_source_pose_even_rebound(self):
  a=copy.deepcopy(self.a);a[0][0,0,1]+=1;self.rejects(a)
 def test_nonfinite_source_rejects(self):
  a=copy.deepcopy(self.a);a[0][0,0,1]=float('nan')
  with self.assertRaises(AssertionError):verify(*a,expected_binding=self.b,current_binding=self.b)

if __name__=='__main__':unittest.main()
