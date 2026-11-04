"""Actual complete source/ground fixtures, hermetic role counterexamples."""
import copy,unittest
import numpy as np
from run import ROOT,read
import evangel_college_named_lower_source_skin_20261011 as lower
import evangel_college_named_two_upper_strips_20261011 as strips
B=ROOT/'docs/astra-city/government-import'
class RemainingRoles(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.data=read(B/'government-xl-evangel-college-91306-current-actual-ground-capture-v1-20261011/complete-four-stream-ground-inputs.json.gz')
  cls.finite=read(B/'government-xl-evangel-college-91306-complete13960-preserved-candidate-finite-diagnostic-v2-20261011/diagnostic.json.gz')
  cls.grade=read(B/'government-xl-evangel-college-91306-current-four-body-grade-paths-v3-20261011/diagnostic.json.gz')
  cls.graph=read(B/'government-xl-evangel-college-91306-complete226-source-component-interfaces-v1-20261011/diagnostic.json.gz')
  cls.q=read(B/'government-xl-evangel-college-91306-complete226-current-component-qualification-diagnostic-v1-20261011/diagnostic.json.gz')
  cls.g=np.asarray(read(ROOT/'source-scripts/city/government-import/local/government-xl-evangel-college-91306-disjoint-current-neighbour-parent-retention-v5-20261011/runtime-geometry.json.gz')['rows'][0]['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)
 @staticmethod
 def row(d,m):return next(r for r in d['rows']if r['arithmetic']==m)
 def args(self,mode='providerOriginal'):
  return dict(world=np.asarray(self.data['completeWorldStreams'][mode]['completeWorldTriangles'],dtype='<f8'),ground=self.g,finite_row=self.row(self.finite,mode),grade_row=self.row(self.grade,mode),parts=self.row(self.graph,mode)['completeOriginalTopology']['sharedEdgeConnectedComponents'])
 def stripargs(self,mode='providerOriginal'):
  q=self.row(self.q,mode);return dict(world=self.args(mode)['world'],qualification_row=q,parts=self.args(mode)['parts'],qualified_host_face_ids=q['completeConditionalHostFaceIds'])
 def reject_lower(self,change):
  a=copy.deepcopy(self.args());change(a)
  with self.assertRaises((AssertionError,KeyError,ValueError)):lower.verify(**a)
 def reject_strip(self,change):
  a=copy.deepcopy(self.stripargs());change(a)
  with self.assertRaises((AssertionError,KeyError,ValueError)):strips.verify(**a)
 def test_actual_four_world_lower_roles(self):
  for m in self.data['completeWorldStreams']:
   p=lower.verify(**self.args(m));self.assertFalse(p['slopingFacesTreatedAsSteepWalls']);self.assertFalse(p['currentAcceptance']);self.assertEqual(len(p['completeColumnBaseClosureProposals']),2)
 def test_actual_four_world_three_backed_edges(self):
  for m in self.data['completeWorldStreams']:
   p=strips.verify(**self.stripargs(m));self.assertTrue(p['rawWholeBoundaryFailureRetained']);self.assertEqual(len(p['completeTwoStrips']),2)
 def test_changed_world(self):self.reject_lower(lambda a:a['world'].__setitem__((3854,0,1),8.4))
 def test_changed_ground(self):self.reject_lower(lambda a:a['ground'].__setitem__((0,0,1),100))
 def test_nonfinite_world(self):self.reject_lower(lambda a:a['world'].__setitem__((3854,0,1),np.nan))
 def test_missing_raw_underside(self):self.reject_lower(lambda a:a['grade_row']['rawDownwardFacesRetainedAsUncredited'].remove(3854))
 def test_wrong_failure_scope(self):self.reject_lower(lambda a:a['grade_row']['rawDownwardFacesRetainedAsUncredited'].append(3846))
 def test_unproved_grade_inventory(self):self.reject_lower(lambda a:a['grade_row']['complete5297CurrentGradeContactInventory'].__setitem__('allPairsExamined',False))
 def test_missing_whole_column_face(self):self.reject_lower(lambda a:a['parts'][68].pop())
 def test_wrong_ordinary_record_identity(self):self.reject_lower(lambda a:a['finite_row']['complete13960FaceComparisons'][5137].__setitem__('sourceFace',5147))
 def test_base_negative_not_erased(self):self.reject_lower(lambda a:a['finite_row']['complete13960FaceComparisons'][5137]['groundComparisons']['currentDrawn'].__setitem__('completeFiniteOrdinaryBoundProved',True))
 def test_missing_base_ground_coverage(self):self.reject_lower(lambda a:a['finite_row']['complete13960FaceComparisons'][5137]['groundComparisons']['currentDrawn']['coarse'].__setitem__('groundProjectionCovered',False))
 def test_hidden_original_upper_host(self):self.reject_lower(lambda a:a['finite_row']['complete13960FaceComparisons'][3846]['groundComparisons']['currentDrawn']['coarse'].__setitem__('exactCertifiedLowerClearanceM','0'))
 def test_stale_host_source(self):self.reject_lower(lambda a:a['finite_row']['complete13960FaceComparisons'][3846]['groundComparisons']['currentDrawn']['coarse'].__setitem__('sourceFaceSHA256','0'*64))
 def test_missing_underside_grade(self):self.reject_lower(lambda a:a['grade_row']['complete5297CurrentGradeContactInventory'].__setitem__('contacts',[c for c in a['grade_row']['complete5297CurrentGradeContactInventory']['contacts']if c['sourceFaceA']!=3855]))
 def test_point_contacts_never_grade(self):self.reject_lower(lambda a:next(c for c in a['grade_row']['complete5297CurrentGradeContactInventory']['contacts']if c['sourceFaceA']==3854).__setitem__('dimension',0))
 def test_missing_strip_whole_face(self):self.reject_strip(lambda a:a['parts'][221].pop())
 def test_changed_strip_pose(self):self.reject_strip(lambda a:a['world'].__setitem__((13826,0,1),30))
 def test_no_visual_structural_root(self):self.reject_strip(lambda a:next(v for v in a['qualification_row']['completeFiveVisualDispositions']if v['originalComponent']==221).__setitem__('structuralRootCredit',True))
 def test_missing_original_boundary_edge(self):self.reject_strip(lambda a:next(v for v in a['qualification_row']['completeFiveVisualDispositions']if v['originalComponent']==221)['completeBoundaryEdgeFiniteHostBandProofs'].pop())
 def test_host_not_qualified(self):self.reject_strip(lambda a:a['qualified_host_face_ids'].clear())
 def test_host_census_omission(self):self.reject_strip(lambda a:next(v for v in a['qualification_row']['completeFiveVisualDispositions']if v['originalComponent']==221)['strictlyOutsideUnchangedBandHostFaces'].pop())
 def test_free_edge_failure_not_erased(self):
  def change(a):
   v=next(v for v in a['qualification_row']['completeFiveVisualDispositions']if v['originalComponent']==221);next(r for r in v['completeBoundaryEdgeFiniteHostBandProofs']if not r['fullEdgeAssociated'])['fullEdgeAssociated']=True
  self.reject_strip(change)
 def test_mounted_end_not_unqualified(self):
  def change(a):
   v=next(v for v in a['qualification_row']['completeFiveVisualDispositions']if v['originalComponent']==221);next(r for r in v['completeBoundaryEdgeFiniteHostBandProofs']if r['fullEdgeAssociated'])['fullEdgeAssociated']=False
  self.reject_strip(change)
 def test_axis_trials_not_omitted(self):
  def change(a):
   v=next(v for v in a['qualification_row']['completeFiveVisualDispositions']if v['originalComponent']==221);next(r for r in v['completeBoundaryEdgeFiniteHostBandProofs']if r['fullEdgeAssociated'])['completeCoordinatePermutationTrials'].pop()
  self.reject_strip(change)
if __name__=='__main__':unittest.main()
