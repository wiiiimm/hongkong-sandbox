"""Counterexamples for exact nested-cycle binding and unchanged finite limits."""
import copy,unittest
from unittest.mock import patch
import one_peking_nested_cycle_boundary_v1_20261101 as b
class CycleTests(unittest.TestCase):
 def setUp(self):
  self.parent=dict(w=7,h=7,cell=1,elev=[5.]*49,vegetation=[0]*49,meta=dict(georef=dict(bE=834499,bN=816501,aE=1,aN=-1),targetUids=['landsd/10:0','landsd/11:0']),patches=[dict(id=str(i),coarseCells=[0,0,1,1],meta=dict(targetUids=[]))for i in range(17)])
  self.parent['patches'][12]=self.node((0,1,4,4),['landsd/10:0'],False);self.parent['patches'][15]=self.node((0,0,2,1),['landsd/11:0'],False)
  self.sources={'retained-12':self.node((0,1,4,4),sorted(b.OWNERS|{'landsd/10:0'}),True),'retained-15':self.node((0,0,2,1),sorted(b.OWNERS|{'landsd/11:0'}),True),'new-root':self.node((2,0,4,1),sorted(b.OWNERS),True)}
  self.candidates={n:b.refined_new_metadata(v,self.parent)if n=='new-root'else copy.deepcopy(v)for n,v in self.sources.items()}
  self.composition=dict(jobId=b.COMPOSITION_JOB,parentSHA256=b.PARENT_SHA,allFiniteSeamsPassed=True,uids=sorted(b.OWNERS),members={n:dict(candidate=dict(path='source-'+n,sha256='s'*64),beforeFaces=len(b.nested.triangles(v)),afterFaces=len(b.nested.triangles(v)),changedParentFaces=1)for n,v in self.sources.items()})
  self.proof=dict(policy=b.POLICY,parent=dict(path='parent',sha256=b.PARENT_SHA),composition=dict(path='composition',sha256=b.COMPOSITION_SHA),members={n:dict(candidate=dict(path=n,sha256='n'*64),canonicalSHA256=b.nested.canonical_sha(v))for n,v in self.candidates.items()});self.ref=dict(path='proof',sha256='p'*64)
  self.data={'parent':self.parent,'composition':self.composition,'proof':self.proof,**{'source-'+n:v for n,v in self.sources.items()},**self.candidates}
  for p in [patch.object(b.nested,'reference',side_effect=lambda ref:self.data[ref['path']]),patch.object(b,'NEW_BOUNDS',(2.,0.,4.,1.))]:p.start();self.addCleanup(p.stop)
 def node(self,bb,targets,changed):
  x,z,X,Z=bb;w=round((X-x)*2)+1;h=round((Z-z)*2)+1;pos=[];idx=[]
  for r in range(h):
   for c in range(w):
    a,d=x+c*.5,z+r*.5;y=5-max(0,1-abs(a-2))*max(0,1-abs(d-1))if changed else 5;pos.extend([a,y,d])
  for r in range(h-1):
   for c in range(w-1):k=r*w+c;idx.extend([k,k+1,k+w,k+1,k+w+1,k+w])
  return dict(id='test',w=w,h=h,cell=.5,coarseCells=[x+1,z+1,X+1,Z+1],elev=[5.]*(w*h),vegetation=[0]*(w*h),meta=dict(georef=dict(aE=.5,aN=-.5,bE=834500+x,bN=816500-z,W=w,H=h),parentTerrain='city/data/test-parent.json',parentSha256=b.PARENT_SHA,targetUids=targets),nativeMesh=dict(position=pos,index=idx,source=dict(policy='test')))
 def load(self):return b.load(self.ref)
 def marked(self):
  nodes={n:copy.deepcopy(v)for n,v in self.candidates.items()}
  for n,v in nodes.items():v['nativeMesh']['source']['coordinatedBoundary']=dict(policy=b.POLICY,proof=self.ref,member=n)
  return nodes
 def successor(self):
  n=self.marked();s=copy.deepcopy(self.parent);s['patches'][12]=n['retained-12'];s['patches'][15]=n['retained-15'];s['patches'].append(n['new-root']);s['meta']['targetUids']=sorted(set(self.parent['meta']['targetUids'])|b.OWNERS);return s
 def test_complete_cycle_has_three_edges(self):self.assertEqual(len(self.load()[3]),3)
 def test_exact_successor(self):b.load(self.ref,self.successor())
 def test_refinement_keeps_geometry(self):self.assertEqual(self.candidates['new-root']['nativeMesh'],self.sources['new-root']['nativeMesh'])
 def test_wrong_parent(self):self.proof['parent']['sha256']='x'*64;self.assertRaises(AssertionError,self.load)
 def test_wrong_composition(self):self.proof['composition']['sha256']='x'*64;self.assertRaises(AssertionError,self.load)
 def test_missing_member(self):self.proof['members'].pop('new-root');self.assertRaises(AssertionError,self.load)
 def test_rehashed_changed_candidate(self):
  self.candidates['retained-12']['nativeMesh']['position'][1]-=.01;self.proof['members']['retained-12']['canonicalSHA256']=b.nested.canonical_sha(self.candidates['retained-12']);self.assertRaises(AssertionError,self.load)
 def test_rehashed_changed_grid(self):
  self.candidates['new-root']['elev'][0]=4;self.proof['members']['new-root']['canonicalSHA256']=b.nested.canonical_sha(self.candidates['new-root']);self.assertRaises(AssertionError,self.load)
 def test_lost_target(self):
  self.candidates['retained-12']['meta']['targetUids'].remove('landsd/10:0');self.proof['members']['retained-12']['canonicalSHA256']=b.nested.canonical_sha(self.candidates['retained-12']);self.assertRaises(AssertionError,self.load)
 def test_effective_set(self):b.validate_effective(list(self.marked().values()))
 def test_missing_effective(self):self.assertRaises(AssertionError,b.validate_effective,list(self.marked().values())[:2])
 def test_duplicate_effective(self):
  ns=list(self.marked().values());self.assertRaises(AssertionError,b.validate_effective,ns+[copy.deepcopy(ns[0])])
 def test_unmarked_mate(self):
  ns=self.marked();ns['new-root']=self.candidates['new-root'];self.assertRaises(AssertionError,b.validate_effective,list(ns.values()))
 def test_unrelated_child(self):
  s=self.successor();s['patches'][3]['id']='changed';self.assertRaises(AssertionError,b.load,self.ref,s)
 def test_changed_root_grid(self):
  s=self.successor();s['elev'][0]=4;self.assertRaises(AssertionError,b.load,self.ref,s)
 def test_third_edge(self):
  ns={n:self.candidates[n]for n in ['retained-15','new-root']};f=b.finite_callback(ns,'retained-15');self.assertTrue(f(2,4,1));self.assertFalse(f(1,5,0))
 def test_one_centimetre_limit(self):
  ns=copy.deepcopy({n:self.candidates[n]for n in ['retained-15','new-root']})
  for i in range(1,len(ns['new-root']['nativeMesh']['position']),3):ns['new-root']['nativeMesh']['position'][i]+=.02
  self.assertRaises(AssertionError,b.finite_callback,ns,'retained-15')
 def test_dispatch_restored(self):
  try:
   with b.private_validator():self.assertIs(b.nested.coordinated_boundary,b.coordinated_boundary);raise RuntimeError('test')
  except RuntimeError:pass
  self.assertIs(b.nested.coordinated_boundary,b.ORIGINAL_BOUNDARY);self.assertIs(b.validator.validate_effective_coordinated_members,b.ORIGINAL_EFFECTIVE)
if __name__=='__main__':unittest.main()
