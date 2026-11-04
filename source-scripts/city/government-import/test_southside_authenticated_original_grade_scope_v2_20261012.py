"""Unexecuted26 actual saved-source and adverse scope/path cases; no new predicates."""
import unittest,json,gzip,hashlib,copy
from pathlib import Path
import numpy as np
from southside_authenticated_original_grade_scope_v1_20261012 import prepare,account_path
R=Path(__file__).resolve().parents[3];B=R/'docs/astra-city/government-import';D=B/'government-xl-southside-authenticated-original-ground-grade-draft-v1-20261012'
MODES=['providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix'];UIDS=['landsd/315025:0','landsd/300867:0']
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
_FIXTURE=None
def fixture():
 global _FIXTURE
 if _FIXTURE is None:
  p=D/'actual-saved-mode-bindings.json';assert hashlib.sha256(p.read_bytes()).hexdigest()=='ae459858b2e99f68046745b174cc2600b9b680864d5c9a75d138c07383d4b78d';bind=read(p)
  a=B/'government-xl-southside-315025-300867-current-grade-source-context-v1-20261012/diagnostic.json.gz';b=B/'government-xl-southside-315025-300867-unfiltered-original-sheets-comparison-v2-20261012/diagnostic.json.gz'
  assert hashlib.sha256(a.read_bytes()).hexdigest()==bind['currentGradeDiagnosticSHA256']and hashlib.sha256(b.read_bytes()).hexdigest()==bind['authenticatedComparisonDiagnosticSHA256']
  old={(q['uid'],q['arithmetic']):q for q in read(a)['rows']};auth={(q['uid'],q['arithmetic']):q for q in read(b)['rows']}
  data=read(B/'government-xl-southside-315025-300867-current-actual-ground-capture-v1-20261012/complete-two-actor-four-stream-ground-inputs.json.gz')['rows'];ground={q['uid']:np.asarray(q['completeSelectedFacets'],dtype='<f8')for q in read(b.parent/'complete-unfiltered-authenticated-source-ground.json.gz')['actorConservativeGrounds']}
  _FIXTURE=(bind,old,auth,data,ground)
 return _FIXTURE
def args(uid=UIDS[0],mode=MODES[0]):
 bind,old,auth,data,ground=fixture();return dict(world=np.asarray(data[uid]['completeWorldStreams'][mode]['completeWorldTriangles'],dtype='<f8'),ground=ground[uid],current=old[uid,mode],authenticated=auth[uid,mode],binding=bind['boundModes'][uid+'|'+mode])
class ActualBaseline(unittest.TestCase):pass
for u in UIDS:
 for m in MODES:
  def case(self,uid=u,mode=m):
   q=prepare(**args(uid,mode));self.assertEqual(len(q['failed']),300 if uid==UIDS[0]else 163);self.assertEqual(len(q['nonsteep']),12 if uid==UIDS[0]else 0);self.assertEqual(len(q['records']),11699 if uid==UIDS[0]else 1191);self.assertFalse(q['zeros']&set(q['eligible']));self.assertFalse(q['nonsteep']&set(q['eligible']))
  setattr(ActualBaseline,'test_'+u.split('/')[1].replace(':','_')+'_'+m,case)
class ActualAdverse(unittest.TestCase):
 def run_bad(self,change):
  q=args();q['authenticated']=copy.copy(q['authenticated']);q['current']=copy.copy(q['current']);change(q)
  with self.assertRaises(AssertionError):prepare(**q)
 def test_missing_saved_face(self):self.run_bad(lambda q:q['authenticated'].update(completeOriginalFaceComparisons=q['authenticated']['completeOriginalFaceComparisons'][:-1]))
 def test_duplicate_saved_face(self):self.run_bad(lambda q:q['authenticated'].update(completeOriginalFaceComparisons=[q['authenticated']['completeOriginalFaceComparisons'][0]]*11699))
 def test_changed_world(self):
  def change(q):q['world']=q['world'].copy();q['world'][0,0,0]=np.nextafter(q['world'][0,0,0],np.inf)
  self.run_bad(change)
 def test_drawn_ground_cannot_replace_original(self):self.run_bad(lambda q:q.update(ground=np.zeros((25388,3,3),dtype='<f8')))
 def test_changed_source(self):self.run_bad(lambda q:q['authenticated'].update(sourceSHA256='0'*64))
 def test_changed_mode(self):self.run_bad(lambda q:q['authenticated'].update(arithmetic=MODES[1]))
 def test_changed_current_failure_scope(self):self.run_bad(lambda q:q['current'].update(allRawFailedFaces=[]))
 def test_changed_current_orientation(self):
  def change(q):rows=list(q['current']['allCompleteOriginalFiniteRecords']);replacement='steep-wall';assert rows[0]['exactOrientationDiagnostic']!=replacement;rows[0]=dict(rows[0],exactOrientationDiagnostic=replacement);q['current']['allCompleteOriginalFiniteRecords']=rows
  self.run_bad(change)
 def test_changed_topology(self):self.run_bad(lambda q:q['current'].update(completeOriginalTopology={}))
 def test_self_supplied_binding(self):self.run_bad(lambda q:q.update(binding=dict(currentRowCanonicalSHA256='0'*64,authenticatedRowCanonicalSHA256='0'*64)))
class PathAccounting(unittest.TestCase):
 def values(self):return dict(ids=[1,2],eligible=[1,2],component_map={1:0,2:0},positive_grade_ids={1},terminal_cap_strict=True,interfaces=[dict(hasWholeStrictlyExposedOriginalEdge=True)],raw_helper_path=dict(hasExactOriginalStrictClearCapRoofPath=True))
 def test_positive_remains_nonaccepting(self):
  q=account_path(**self.values());self.assertTrue(q['diagnosticGradeToWholeClearCapAndExposedEdges']);self.assertFalse(q['rootCredit']);self.assertFalse(q['fullBodyRootProved'])
 def test_vacuous_single_face(self):
  q=self.values();q.update(ids=[1],interfaces=[]);self.assertFalse(account_path(**q)['diagnosticGradeToWholeClearCapAndExposedEdges'])
 def test_point_only_grade(self):
  q=self.values();q['positive_grade_ids']=set();self.assertFalse(account_path(**q)['diagnosticGradeToWholeClearCapAndExposedEdges'])
 def test_hidden_terminal(self):
  q=self.values();q['terminal_cap_strict']=False;self.assertFalse(account_path(**q)['diagnosticGradeToWholeClearCapAndExposedEdges'])
 def test_unexposed_whole_edge(self):
  q=self.values();q['interfaces']=[dict(hasWholeStrictlyExposedOriginalEdge=False)];self.assertFalse(account_path(**q)['diagnosticGradeToWholeClearCapAndExposedEdges'])
 def test_zero_or_nonwall_excluded(self):
  q=self.values();q['eligible']=[1]
  with self.assertRaises(AssertionError):account_path(**q)
 def test_cross_component_bridge(self):
  q=self.values();q['component_map'][2]=1
  with self.assertRaises(AssertionError):account_path(**q)
 def test_repeated_source_face(self):
  q=self.values();q['ids']=[1,1]
  with self.assertRaises(AssertionError):account_path(**q)
if __name__=='__main__':unittest.main()
