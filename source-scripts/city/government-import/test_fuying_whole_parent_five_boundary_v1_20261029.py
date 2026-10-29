"""Whole-parent/availability counterexamples and unchanged finite seam limits."""
import copy,unittest
from unittest.mock import patch
import fuying_whole_parent_five_boundary_v1_20261029 as b
class ContractTests(unittest.TestCase):
 def setUp(self):
  self.root=dict(w=4,h=3,meta=dict(georef=dict(bE=834500,bN=816500,aE=1,aN=-1)))
  targets=['landsd/'+str(i)+':0'for i in range(5)]
  self.old=self.node([0,0,3,2],targets);self.old['meta']['parentSha256']='r'*64
  cells={'west-west-low-z':[0,0,1,1],'west-east-low-z':[1,0,2,1],'west-high-z':[0,1,2,2],'east-low-z':[2,0,3,1],'east-high-z':[2,1,3,2]}
  self.nodes={n:self.node(c,targets+['landsd/181489:0'])for n,c in cells.items()}
  self.proof=dict(policy=b.POLICY,parent=dict(path='root',sha256='r'*64),oldNative=dict(path='old',sha256=b.OLD_SHA),targetUids=targets+['landsd/181489:0'],members={n:dict(candidate=dict(path=n,sha256=n),canonicalSHA256=b.legacy.canonical_sha(v))for n,v in self.nodes.items()})
  self.data={'root':self.root,'old':self.old,'proof':self.proof,**self.nodes};self.ref=dict(path='proof',sha256='p'*64)
  self.mock=patch.object(b.legacy,'reference',side_effect=lambda ref:self.data[ref['path']]);self.mock.start();self.addCleanup(self.mock.stop)
 def node(self,c,targets):
  x,z,X,Z=c;w=X-x+1;h=Z-z+1
  return dict(w=w,h=h,coarseCells=c,meta=dict(parentTerrain='city/data/terrain.json',parentSha256='r'*64,targetUids=targets,georef=dict(bE=834500+x,bN=816500-z,aE=1,aN=-1)),elev=[0]*(w*h),renderedElev=[0]*(w*h),vegetation=[0]*(w*h),nativeMesh=dict(position=[x,0,z,X,0,z,X,0,Z,x,0,Z],index=[0,1,2,0,2,3],source={}))
 def load(self):return b.load(self.ref,self.root)
 def test_complete_partition(self):self.assertEqual(len(self.load()[1]),5)
 def test_missing_member(self):self.proof['members'].pop('west-high-z');self.assertRaises(AssertionError,self.load)
 def test_changed_body(self):self.nodes['west-high-z']['nativeMesh']['position'][1]=1;self.assertRaises(AssertionError,self.load)
 def test_wrong_old_revision(self):self.proof['oldNative']['sha256']='x'*64;self.assertRaises(AssertionError,self.load)
 def test_lost_legacy_target(self):self.proof['targetUids'].pop(0);self.assertRaises(AssertionError,self.load)
 def test_changed_grid_even_rehashed(self):
  n='west-high-z';self.nodes[n]['elev'][0]=1;self.proof['members'][n]['canonicalSHA256']=b.legacy.canonical_sha(self.nodes[n]);self.assertRaises(AssertionError,self.load)
 def marked(self):
  out=copy.deepcopy(list(self.nodes.values()))
  for n,v in zip(self.nodes,out):v['nativeMesh']['source']['coordinatedBoundary']=dict(policy=b.POLICY,proof=self.ref,member=n)
  return out
 def test_full_effective_set(self):b.validate_effective_coordinated_members(self.marked())
 def test_missing_effective_member(self):self.assertRaises(AssertionError,b.validate_effective_coordinated_members,self.marked()[:-1])
 def test_duplicate_effective_member(self):
  ns=self.marked();self.assertRaises(AssertionError,b.validate_effective_coordinated_members,ns+[copy.deepcopy(ns[0])])
 def test_old_parent_cannot_remain(self):self.assertRaises(AssertionError,b.validate_effective_coordinated_members,self.marked()+[self.old])
 def test_finite_same_triangle_boundary(self):
  pair={n:self.nodes[n]for n in ['west-west-low-z','west-east-low-z']};f=b.finite_callback(pair,'west-west-low-z');self.assertTrue(f(1,0,.0));self.assertFalse(f(.5,0,.0))
 def test_existing_one_centimetre_limit(self):
  pair=copy.deepcopy({n:self.nodes[n]for n in ['west-west-low-z','west-east-low-z']})
  for i in range(1,len(pair['west-east-low-z']['nativeMesh']['position']),3):pair['west-east-low-z']['nativeMesh']['position'][i]=.02
  self.assertRaises(AssertionError,b.finite_callback,pair,'west-west-low-z')
if __name__=='__main__':unittest.main()
