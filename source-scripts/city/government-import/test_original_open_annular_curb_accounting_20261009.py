import copy,hashlib,unittest
from fractions import Fraction
import numpy as np
from original_open_annular_curb_accounting_20261009 import verify,canonical

class AnnularCurb(unittest.TestCase):
 def fixture(self):
  outer=[(-2,-2),(2,-2),(2,2),(-2,2)];inner=[(-1.8,-1.8),(1.8,-1.8),(1.8,1.8),(-1.8,1.8)]
  def point(p,y):return [p[0],y,p[1]]
  ts=[]
  for i in range(4):
   j=(i+1)%4;a,b=point(outer[i],.1),point(outer[j],.1);c,d=point(inner[i],.1),point(inner[j],.1)
   ts.extend([[a,c,b],[b,c,d]])
   aa,bb=point(outer[i],-.6),point(outer[j],-.6)
   ts.extend([[a,b,aa],[b,bb,aa]])
   cc,dd=point(inner[i],-.6),point(inner[j],-.6)
   ts.extend([[c,cc,d],[d,cc,dd]])
  t=np.asarray(ts,float);g=np.asarray([[[-5,0,-5],[5,0,-5],[5,0,5]],[[-5,0,-5],[5,0,5],[-5,0,5]]],float)
  c=[dict(sourceFace=i,groundProjectionCovered=True,minimum=dict(minimumGapM=float(face[:,1].min())),maximumObservedGapM=float(face[:,1].max())) for i,face in enumerate(t)]
  return t,c,list(range(len(t))),g
 def binding(self,t,c,ids,g):return dict(completeOriginalWorldTrianglesSHA256=hashlib.sha256(t.tobytes()).hexdigest(),currentDrawnGroundSHA256=hashlib.sha256(g.tobytes()).hexdigest(),completeCurrentFacetContextsSHA256=canonical(c),completeOriginalPartFacesSHA256=canonical(ids))
 def call(self,t,c,ids,g):
  b=self.binding(t,c,ids,g);return verify(t,c,ids,g,expected_binding=b,current_binding=b)
 def test_annular_grade_crossing_visual_only(self):
  r=self.call(*self.fixture());self.assertTrue(r['originalLowExteriorRoleVerified']);self.assertEqual(r['openLowerPerimeterLoops'],2);self.assertEqual(len(r['affectedOriginalWallFaces']),16);self.assertTrue(r['exactActualGradeInterfaces']);self.assertFalse(r['structuralRootCredit']);self.assertFalse(r['maySupportOtherComponents']);self.assertFalse(r['closedSolidCertified']);self.assertFalse(r['installationApproved'])
 def test_stale_world(self):
  t,c,ids,g=self.fixture();b=self.binding(t,c,ids,g);t[0,0,0]+=.01
  with self.assertRaises(AssertionError):verify(t,c,ids,g,expected_binding=b,current_binding=b)
 def test_stale_context(self):
  t,c,ids,g=self.fixture();b=self.binding(t,c,ids,g);c[0]['minimum']['minimumGapM']+=.01
  with self.assertRaises(AssertionError):verify(t,c,ids,g,expected_binding=b,current_binding=b)
 def test_stale_ground(self):
  t,c,ids,g=self.fixture();b=self.binding(t,c,ids,g);g[:,:,1]+=.01
  with self.assertRaises(AssertionError):verify(t,c,ids,g,expected_binding=b,current_binding=b)
 def test_stale_membership(self):
  t,c,ids,g=self.fixture();b=self.binding(t,c,ids,g)
  with self.assertRaises(AssertionError):verify(t,c,ids[:-1],g,expected_binding=b,current_binding=b)
 def test_tall_building_rejected(self):
  t,c,ids,g=self.fixture();t[:,:,1]*=10
  with self.assertRaisesRegex(AssertionError,'bounded low'):self.call(t,c,ids,g)
 def test_broad_slab_rejected(self):
  t,c,ids,g=self.fixture();t[:,:,[0,2]]*=3
  with self.assertRaisesRegex(AssertionError,'Broad solid'):self.call(t,c,ids,g)
 def test_reversed_face(self):
  t,c,ids,g=self.fixture();t[2]=t[2,::-1]
  with self.assertRaisesRegex(AssertionError,'winding'):self.call(t,c,ids,g)
 def test_missing_cap(self):
  t,c,ids,g=self.fixture();ids.remove(0)
  with self.assertRaises(AssertionError):self.call(t,c,ids,g)
 def test_duplicate_original_face(self):
  t,c,ids,g=self.fixture();ids.append(ids[-1])
  with self.assertRaises(AssertionError):self.call(t,c,ids,g)
 def test_buried_upward_cap(self):
  t,c,ids,g=self.fixture();c[0]['minimum']['minimumGapM']=-.5001
  with self.assertRaisesRegex(AssertionError,'upward'):self.call(t,c,ids,g)
 def test_no_exposure(self):
  t,c,ids,g=self.fixture()
  for row in c:row['maximumObservedGapM']=-.1
  with self.assertRaisesRegex(AssertionError,'exposed'):self.call(t,c,ids,g)
 def test_no_ground_coverage(self):
  t,c,ids,g=self.fixture();c[0]['groundProjectionCovered']=False
  with self.assertRaises(AssertionError):self.call(t,c,ids,g)
 def test_true_boolean_ground_required(self):
  t,c,ids,g=self.fixture();c[0]['groundProjectionCovered']=1
  with self.assertRaises(AssertionError):self.call(t,c,ids,g)
 def test_no_exact_grade_contact(self):
  t,c,ids,g=self.fixture();g[:,:,1]+=10
  with self.assertRaisesRegex(AssertionError,'upper-ground contact'):self.call(t,c,ids,g)
 def test_higher_upper_ground_disallows_lower_plane_contacts(self):
  t,c,ids,g=self.fixture();high=g.copy();high[:,:,1]=1;g=np.concatenate([g,high])
  with self.assertRaisesRegex(AssertionError,'upper-ground contact'):self.call(t,c,ids,g)
 def test_higher_island_splits_actual_upper_ground_intervals(self):
  t,c,ids,g=self.fixture();island=np.asarray([[[-1,1,-3],[1,1,-3],[1,1,3]],[[-1,1,-3],[1,1,3],[-1,1,3]]],float);g=np.concatenate([g,island]);r=self.call(t,c,ids,g)
  # Outer front/back original wall contacts survive only outside the high
  # finite island; endpoints on the lower plane cannot certify its interior.
  for row in r['exactActualGradeInterfaces']:
   for witness in row['exactActiveUpperGroundIntervals']:
    a,b=[[float(Fraction(v)) for v in p] for p in witness['exactSegmentEndpoints']];m=(np.asarray(a)+b)/2
    self.assertFalse(-1<m[0]<1 and -3<m[2]<3)
  self.assertTrue(any(len(w['allGroundCoverageAndHeightBreakpoints'])>2 for row in r['exactActualGradeInterfaces'] for w in row['exactActiveUpperGroundIntervals']))
 def test_actual_harbourfront_all_original_54_faces(self):
  from run import ROOT,HERE,read
  from exact_packed_world_geometry_20261009 import decode_original_world_triangles
  base=ROOT/'docs/astra-city/government-import';p=base/'government-xl-terrain-recovery-harbourfront-boundary-nested-physical-v3-20261009';row=read(p/'selection.json.gz')['rows'][0];t=decode_original_world_triangles((ROOT/row['candidate']['path']).read_bytes());c=read(base/'xl-terrain-recovery-20261009-118230-boundary-current-complete-context-v3/diagnostic.json.gz')['faces'];geom=read(HERE/'local'/p.name/'runtime-geometry.json.gz')['rows'][0];g=np.asarray(geom['drawnGroundGeometry'],float).reshape(-1,3,3);ids=read(base/'xl-terrain-recovery-20261009-118230-low-ancillary-context-v1/diagnostic.json.gz')['component432OriginalFaces']
  r=self.call(t,c,ids,g);self.assertEqual(len(ids),54);self.assertEqual(r['affectedOriginalWallFaces'],[17716,17717,17718,17719,17736,17738,17739,17846,17849,17850,17851,17852]);self.assertEqual(len(r['originalCapFaces']),20);self.assertEqual(r['openLowerPerimeterLoops'],2);self.assertAlmostEqual(r['annularCapAreaM2'],7.319915771484375);self.assertTrue(r['exactActualGradeInterfaces'])

if __name__=='__main__':unittest.main()
