"""Adversarial binding and root-edge checks for a finite terrain chain."""
import copy,hashlib,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import three_member_native_boundary_v1_20261027 as chain
from native_terrain_validation import validate_native_mesh

class ChainChecks(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.patch=patch.object(chain.legacy,'ROOT',self.root);self.patch.start()
        self.parent=dict(w=4,h=3,cell=1,elev=[5]*12,vegetation=[0]*12,meta=dict(georef=dict(aE=1,aN=-1,bE=834499,bN=816500,W=4,H=3)))
        self.parentref=self.write('root.json',self.parent);self.names=['left','middle','right']
        self.before={n:self.member(i,False)for i,n in enumerate(self.names)}
        self.candidate={n:self.member(i,True)for i,n in enumerate(self.names)};self.bind()
    def tearDown(self):self.patch.stop();self.temp.cleanup()
    def write(self,name,value):
        raw=(json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode();(self.root/name).write_bytes(raw)
        return dict(path=name,sha256=hashlib.sha256(raw).hexdigest())
    def member(self,i,changed):
        x0=i-1;positions=[]
        for r in range(5):
            z=r*.5
            for c in range(3):
                x=x0+c*.5;y=5-2*max(0,1-abs(z-1))if changed and x in [0,1]else 5
                positions.extend([x,y,z])
        indices=[]
        for r in range(4):
            for c in range(2):
                k=r*3+c;indices.extend([k,k+1,k+3,k+1,k+4,k+3])
        return dict(w=3,h=5,cell=.5,elev=[5]*15,vegetation=[0]*15,coarseCells=[i,0,i+1,2],meta=dict(georef=dict(aE=.5,aN=-.5,bE=834500+x0,bN=816500,W=3,H=5),parentTerrain='city/data/terrain.json',parentSha256=self.parentref['sha256'],targetUids=[str(i)]),nativeMesh=dict(position=positions,index=indices,source=dict(policy='test')))
    def bind(self):
        self.members={n:dict(before=self.write(n+'-before.json',self.before[n]),candidate=self.write(n+'-candidate.json',self.candidate[n]),canonicalSHA256=chain.legacy.canonical_sha(self.candidate[n]))for n in self.names};self.pairs=[]
        for i,names in enumerate([['left','middle'],['middle','right']]):
            x=i;wkt=f'POLYGON (({x-.25} 0.25, {x+.25} 0.25, {x+.25} 1.75, {x-.25} 1.75, {x-.25} 0.25))'
            self.pairs.append(self.write('pair-'+str(i)+'.json',dict(policy=chain.legacy.POLICY,parent=self.parentref,members={n:self.members[n]for n in names},editRegionWKT=wkt)))
        self.proof=dict(policy=chain.POLICY,parent=self.parentref,members=self.members,pairs=self.pairs);self.rewrite_master()
    def rewrite_master(self):
        ref=self.write('master.json',self.proof);self.nodes=[]
        for n in self.names:
            node=copy.deepcopy(self.candidate[n]);node['nativeMesh']['source']['coordinatedBoundary']=dict(policy=chain.POLICY,proof=ref,member=n);self.nodes.append(node)
    def validate(self):
        with chain.private_validator():
            for node in self.nodes:validate_native_mesh(node,self.parent)
            chain.legacy.validate_effective_coordinated_members(self.nodes)
    def test_complete_chain_passes_existing_surface_rules(self):self.validate()
    def test_middle_member_checks_both_seams(self):
        callback=chain.coordinated_boundary(self.nodes[1],self.parent)
        self.assertTrue(callback(0,3,1));self.assertTrue(callback(1,3,1));self.assertFalse(callback(.5,5,0))
    def test_missing_end_member_is_rejected(self):
        with self.assertRaisesRegex(AssertionError,'All three'):chain.validate_effective_coordinated_members(self.nodes[:2])
    def test_duplicate_member_is_rejected(self):
        with self.assertRaises(AssertionError):chain.validate_effective_coordinated_members(self.nodes+[self.nodes[2]])
    def test_old_body_is_not_new_mate(self):
        with self.assertRaises(AssertionError):chain.validate_effective_coordinated_members(self.nodes[:2]+[self.before['right']])
    def test_unmarked_private_candidate_is_not_effective_mate(self):
        with self.assertRaises(AssertionError):chain.validate_effective_coordinated_members(self.nodes[:2]+[self.candidate['right']])
    def test_modified_bound_body_is_rejected(self):
        self.nodes[1]['nativeMesh']['position'][1]-=.1
        with self.assertRaises(AssertionError):self.validate()
    def test_rebound_incompatible_seam_still_fails_finite_pair_check(self):
        self.candidate['right']['nativeMesh']['position'][6*3+1]+=.1;self.bind()
        with self.assertRaises(AssertionError):self.validate()
    def test_root_boundary_guard_is_unchanged(self):
        self.candidate['left']['nativeMesh']['position'][6*3+1]=4;self.bind()
        with self.assertRaisesRegex(AssertionError,'boundary does not join parent'):self.validate()
    def test_omitted_shared_edge_is_rejected(self):
        self.proof['pairs']=self.proof['pairs'][:1];self.rewrite_master()
        with self.assertRaises(AssertionError):self.validate()
    def test_pair_body_must_equal_master_member(self):
        pair=json.loads((self.root/'pair-0.json').read_text());pair['members']['left']['canonicalSHA256']='0'*64
        self.proof['pairs'][0]=self.write('pair-0.json',pair);self.rewrite_master()
        with self.assertRaisesRegex(AssertionError,'Pair body differs'):self.validate()
    def test_parent_change_is_rejected(self):
        parent=copy.deepcopy(self.parent);parent['elev'][0]=4
        with self.assertRaisesRegex(AssertionError,'parent differs'):chain.coordinated_boundary(self.nodes[1],parent)
    def test_dispatch_restores_legacy_functions(self):
        old=chain.legacy.coordinated_boundary
        with chain.private_validator():self.assertIs(chain.legacy.coordinated_boundary,chain.coordinated_boundary)
        self.assertIs(chain.legacy.coordinated_boundary,old)

if __name__=='__main__':unittest.main()
