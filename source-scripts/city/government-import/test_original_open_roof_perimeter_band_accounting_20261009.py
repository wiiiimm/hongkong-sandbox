import copy,hashlib,unittest,collections
import numpy as np
from original_open_roof_perimeter_band_accounting_20261009 import verify,canonical
def lower_edges(tri,ids):
 e=collections.Counter(tuple(sorted((tuple(a),tuple(b)))) for i in ids for a,b in zip(tri[i],np.roll(tri[i],-1,axis=0)));minimum=float(tri[ids,:,1].min())
 return [[list(v) for v in edge] for edge,count in sorted(e.items()) if count==1 and edge[0][1]==edge[1][1]==minimum]
class RoofBand(unittest.TestCase):
 def fixture(self):
  roof=[[[0,0,0],[0,0,4],[4,0,0]],[[4,0,0],[0,0,4],[4,0,4]]];ring=np.asarray([[1,.025,1],[1.1,.025,1],[1.1,.025,1.1],[1,.025,1.1]]);faces=[]
  for p,q in zip(ring,np.roll(ring,-1,axis=0)):
   P=p.copy();Q=q.copy();P[1]=Q[1]=2;faces.extend([[p,q,Q],[p,Q,P]])
  tri=np.asarray(roof+faces,float);components=[dict(globalOriginalFaces=[0,1]),dict(globalOriginalFaces=list(range(2,10)))];ctx=[dict(sourceFace=i,groundProjectionCovered=True,minimum=dict(minimumGapM=0)) for i in range(10)];roles=[dict(component=1,kind='open-vertical-roof-post',completeOriginalFaces=list(range(2,10)),completeOriginalLowerBoundary=lower_edges(tri,list(range(2,10))))]
  return [tri,components,ctx,[0],[],roles]
 def binding(self,d):return dict(completeOriginalWorldTrianglesSHA256=hashlib.sha256(d[0].tobytes()).hexdigest(),completeComponentsSHA256=canonical(d[1]),completeCurrentFacetContextsSHA256=canonical(d[2]),independentRootedComponentsSHA256=canonical(d[3]),visualOnlyComponentsSHA256=canonical(d[4]),sourceRolesSHA256=canonical(d[5]))
 def call(self,d):
  b=self.binding(d);return verify(*d,expected_binding=b,current_binding=b)
 def test_complete_perimeter_existing_band_not_exact_contact(self):
  r=self.call(self.fixture());self.assertEqual(r['sourceRoofFootingComponents'],[1]);self.assertTrue(r['exactOriginalNoncontactPreserved']);self.assertFalse(r['groundRootCredit']);self.assertFalse(r['fullAcceptance'])
 def rejects(self,fn):
  d=self.fixture();fn(d)
  with self.assertRaises(AssertionError):self.call(d)
 def test_gap_exceeds_existing_band(self):self.rejects(lambda d:d[0][2:,:,1].__iadd__(.1))
 def test_burial_exceeds_existing_band(self):self.rejects(lambda d:d[0][2:,:,1].__isub__(.2))
 def test_omitted_lower_edge(self):self.rejects(lambda d:d[5][0]['completeOriginalLowerBoundary'].pop())
 def test_unrooted_body(self):self.rejects(lambda d:d[3].clear())
 def test_visual_curb_cannot_root_or_bridge(self):self.rejects(lambda d:d[4].append(0))
 def test_reversed_face(self):self.rejects(lambda d:d[0].__setitem__(2,d[0][2,::-1]))
 def test_detached_side(self):self.rejects(lambda d:d[0][2].__iadd__([1,0,0]))
 def test_zero_area_face(self):self.rejects(lambda d:d[0].__setitem__(2,[d[0][2,0]]*3))
 def test_missing_current_ground(self):self.rejects(lambda d:d[2][3].update(groundProjectionCovered=False))
 def test_ordinary_burial(self):self.rejects(lambda d:d[2][3]['minimum'].update(minimumGapM=-.50001))
 def test_real_roof_hole(self):self.rejects(lambda d:d[0][:2,:,0].__iadd__(20))
 def test_nonvertical_body_not_post(self):self.rejects(lambda d:d[0][2:,:,0].__imul__(50))
 def test_claiming_rooted_component_rejects(self):self.rejects(lambda d:d[3].append(1))
 def test_context_mutation_with_same_binding(self):
  d=self.fixture();b=self.binding(d);d[2][2]['minimum']['minimumGapM']=.2
  with self.assertRaises(AssertionError):verify(*d,expected_binding=b,current_binding=b)
 def test_source_mutation_with_same_binding(self):
  d=self.fixture();b=self.binding(d);d[0][2,0,0]+=.001
  with self.assertRaises(AssertionError):verify(*d,expected_binding=b,current_binding=b)
 def test_partition_mutation_with_same_binding(self):
  d=self.fixture();b=self.binding(d);d[1][1]['globalOriginalFaces'].pop()
  with self.assertRaises(AssertionError):verify(*d,expected_binding=b,current_binding=b)
 def test_role_mutation_with_same_binding(self):
  d=self.fixture();b=self.binding(d);d[5][0]['completeOriginalLowerBoundary'].pop()
  with self.assertRaises(AssertionError):verify(*d,expected_binding=b,current_binding=b)
 def test_actual_complete_source_posts_and_equipment(self):
  from run import ROOT,read,digest
  from exact_packed_world_geometry_20261009 import decode_original_world_triangles
  base=ROOT/'docs/astra-city/government-import'
  g=read(base/'xl-terrain-recovery-20261009-118230-original-world-current-support-v1/diagnostic.json.gz');t=read(base/'xl-terrain-recovery-20261009-118230-current-original-grade-support-v1/typed-support.json.gz');ctx=read(base/'xl-terrain-recovery-20261009-118230-boundary-current-complete-context-v3/diagnostic.json.gz')['faces'];row=read(base/'government-xl-terrain-recovery-harbourfront-boundary-nested-physical-v3-20261009/selection.json.gz')['rows'][0]
  raw=(ROOT/row['candidate']['path']).read_bytes();self.assertEqual(digest(raw),'0e9740f9b9b3061aa4f4bbe26b397db58f870476aa0716745339e505a79c51ff');tri=decode_original_world_triangles(raw);self.assertEqual(len(tri),19438);self.assertEqual(digest(tri.tobytes()),'b276304c2b94878d7c47665b7536a1dca385cf0bd52dd8264dff92d7dc9c5863')
  roles=[]
  for k in [0,85,333]:
   ids=g['components'][k]['globalOriginalFaces'];boundary=collections.Counter(tuple(sorted((tuple(a),tuple(b)))) for i in ids for a,b in zip(tri[i],np.roll(tri[i],-1,axis=0)))
   lower=lower_edges(tri,ids) if k!=333 else [[list(v) for v in e] for e,n in sorted(boundary.items()) if n==1]
   roles.append(dict(component=k,kind='open-vertical-roof-post' if k!=333 else 'open-bottom-upright-roof-equipment',completeOriginalFaces=ids,completeOriginalLowerBoundary=lower))
  d=[tri,g['components'],ctx,t['resolvedOriginalComponents'],[422],roles];r=self.call(d);self.assertEqual(r['sourceRoofFootingComponents'],[0,85,333]);self.assertEqual([len(x['completeOriginalLowerBoundaryBandProof']) for x in r['originalPerimeterRoles']],[10,12,24]);self.assertFalse(r['groundRootCredit'])
if __name__=='__main__':unittest.main()
