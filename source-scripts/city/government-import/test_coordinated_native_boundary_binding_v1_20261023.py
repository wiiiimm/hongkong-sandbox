"""Adversarial binding tests for the opt-in finite native boundary contract."""
import copy,hashlib,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
INTEGRATION=Path(__file__).resolve().parents[1]/'island-detail-integration'
if str(INTEGRATION)not in sys.path:sys.path.insert(0,str(INTEGRATION))
import coordinated_native_boundary as boundary
from native_terrain_validation import validate_native_mesh


class Boundaries(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.patch=patch.object(boundary,'ROOT',self.root);self.patch.start()
        self.parent=dict(w=3,h=3,cell=1,elev=[5]*9,vegetation=[0]*9,meta=dict(georef=dict(aE=1,aN=-1,bE=834499,bN=816500,W=3,H=3)))
        self.parentref=self.write('3d-viewer/city/data/terrain.json',self.parent)
        self.old={name:self.member(name,False)for name in ['left','right']};self.candidate={name:self.member(name,True)for name in ['left','right']}
        self.proof=dict(policy=boundary.POLICY,parent=self.parentref,editRegionWKT='POLYGON ((-0.25 0.25, 0.25 0.25, 0.25 1.75, -0.25 1.75, -0.25 0.25))',members={})
        for name in ['left','right']:self.rebind(name)
        self.own=copy.deepcopy(self.candidate['left']);self.bind()
    def tearDown(self):self.patch.stop();self.temp.cleanup()
    def write(self,name,data):
        path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);raw=(json.dumps(data,sort_keys=True,separators=(',',':'))+'\n').encode();path.write_bytes(raw)
        return dict(path=name,sha256=hashlib.sha256(raw).hexdigest())
    def member(self,name,changed):
        x0=-1 if name=='left'else 0;positions=[]
        for r in range(5):
            z=r*.5
            for c in range(3):
                x=x0+c*.5;y=5
                if changed and x==0:y=5-2*max(0,1-abs(z-1))
                positions.extend([x,y,z])
        indices=[]
        for r in range(4):
            for c in range(2):
                i=r*3+c;indices.extend([i,i+1,i+3,i+1,i+4,i+3])
        return dict(w=3,h=5,cell=.5,elev=[5]*15,vegetation=[0]*15,coarseCells=[0 if name=='left'else 1,0,1 if name=='left'else 2,2],meta=dict(georef=dict(aE=.5,aN=-.5,bE=834500+x0,bN=816500,W=3,H=5),parentTerrain='city/data/terrain.json',parentSha256=self.parentref['sha256'],targetUids=[name]),nativeMesh=dict(position=positions,index=indices,source=dict(policy='test source')))
    def rebind(self,name):
        self.proof['members'][name]=dict(before=self.write(name+'-old.json',self.old[name]),candidate=self.write(name+'-candidate.json',self.candidate[name]),canonicalSHA256=boundary.canonical_sha(self.candidate[name]))
    def bind(self):self.own['nativeMesh']['source']['coordinatedBoundary']=dict(policy=boundary.POLICY,proof=self.write('proof.json',self.proof),member='left')
    def validate(self):return boundary.coordinated_boundary(self.own,self.parent)
    def test_matching_finite_boundaries(self):self.assertTrue(self.validate()(0,3,1))
    def test_absent_marker_keeps_legacy_path(self):self.assertIsNone(boundary.coordinated_boundary(self.candidate['left'],self.parent))
    def test_external_edge_gets_no_coordinated_credit(self):self.assertFalse(self.validate()(-1,5,1))
    def test_shared_edge_outside_edit_gets_no_credit(self):self.assertFalse(self.validate()(0,5,0))
    def test_nearby_edge_cannot_claim_exact_shared_boundary(self):self.assertFalse(self.validate()(-.001,3,1))
    def test_lower_hidden_edge_vertex_is_rejected(self):
        self.assertFalse(self.validate()(0,2,1))
    def test_own_geometry_change_is_rejected(self):
        self.own['nativeMesh']['position'][0]+=.1
        with self.assertRaises(AssertionError):self.validate()
    def test_mate_file_changed_after_binding_is_rejected(self):
        self.write('right-candidate.json',self.old['right'])
        with self.assertRaises(AssertionError):self.validate()
    def test_original_before_bytes_changed_is_rejected(self):
        self.write('left-old.json',self.candidate['left'])
        with self.assertRaises(AssertionError):self.validate()
    def test_hash_bound_but_incompatible_mate_is_rejected(self):
        for i in range(0,len(self.candidate['right']['nativeMesh']['position']),3):
            p=self.candidate['right']['nativeMesh']['position']
            if p[i]==0 and p[i+2]==1:p[i+1]+=.1
        self.rebind('right');self.bind()
        with self.assertRaises(AssertionError):self.validate()
    def test_edit_region_cannot_reach_external_boundary(self):
        self.proof['editRegionWKT']='POLYGON ((-1 0, 1 0, 1 2, -1 2, -1 0))';self.bind()
        with self.assertRaises(AssertionError):self.validate()
    def test_different_parent_is_rejected(self):
        altered=copy.deepcopy(self.parent);altered['elev'][0]=4
        with self.assertRaises(AssertionError):boundary.coordinated_boundary(self.own,altered)
    def test_wrong_member_identity_is_rejected(self):
        self.own['nativeMesh']['source']['coordinatedBoundary']['member']='right'
        with self.assertRaises(AssertionError):self.validate()
    def test_incomplete_mate_surface_is_rejected(self):
        self.candidate['right']['nativeMesh']['index']=[];self.rebind('right');self.bind()
        with self.assertRaises(AssertionError):self.validate()
    def test_ordinary_validator_still_rejects_unbound_shared_edge(self):
        with self.assertRaisesRegex(AssertionError,'boundary does not join parent'):validate_native_mesh(self.candidate['left'],self.parent)
    def test_ordinary_validator_accepts_bound_continuous_shared_edge(self):
        validate_native_mesh(self.own,self.parent)
    def test_ordinary_validator_keeps_external_root_height_guard(self):
        for i in range(0,len(self.candidate['left']['nativeMesh']['position']),3):
            p=self.candidate['left']['nativeMesh']['position']
            if p[i]==-1 and p[i+2]==1:p[i+1]=4
        self.rebind('left');self.own=copy.deepcopy(self.candidate['left']);self.bind()
        with self.assertRaisesRegex(AssertionError,'boundary does not join parent'):validate_native_mesh(self.own,self.parent)
    def test_unindexed_lower_edge_position_cannot_hide_beneath_upper_surface(self):
        self.candidate['left']['nativeMesh']['position'].extend([0,2,1]);self.rebind('left');self.own=copy.deepcopy(self.candidate['left']);self.bind()
        with self.assertRaises(AssertionError):validate_native_mesh(self.own,self.parent)
    def final_pair(self):
        mate=copy.deepcopy(self.candidate['right'])
        mate['nativeMesh']['source']['coordinatedBoundary']=dict(policy=boundary.POLICY,proof=self.own['nativeMesh']['source']['coordinatedBoundary']['proof'],member='right')
        return [self.own,mate]
    def test_complete_pair_can_be_published_atomically(self):
        boundary.validate_effective_coordinated_members(self.final_pair())
    def test_private_mate_file_does_not_allow_half_publication(self):
        with self.assertRaisesRegex(AssertionError,'present exactly once'):boundary.validate_effective_coordinated_members([self.own])
    def test_final_mate_old_geometry_is_not_new_candidate(self):
        with self.assertRaises(AssertionError):boundary.validate_effective_coordinated_members([self.own,self.old['right']])
    def test_duplicate_final_mate_is_rejected(self):
        pair=self.final_pair()
        with self.assertRaises(AssertionError):boundary.validate_effective_coordinated_members(pair+[pair[1]])
    def test_final_mate_proof_identity_must_match(self):
        pair=self.final_pair();pair[1]['nativeMesh']['source']['coordinatedBoundary']['member']='left'
        with self.assertRaises(AssertionError):boundary.validate_effective_coordinated_members(pair)
    def test_preexisting_exact_mate_can_be_retained(self):
        boundary.validate_effective_coordinated_members([self.own,self.candidate['right']])
    def test_valid_uncoordinated_native_still_joins_root(self):
        validate_native_mesh(self.old['left'],self.parent)
    def add_inside_boundary_vertex(self,y=3.004):
        p=self.candidate['left']['nativeMesh'];i=len(p['position'])//3;p['position'].extend([-.001,y,1])
        idx=p['index'];start=next(k for k in range(0,len(idx),3)if idx[k:k+3]==[5,8,7]);idx[start:start+3]=[5,8,i,5,i,7]
        self.rebind('left');self.own=copy.deepcopy(self.candidate['left']);self.bind()
        return tuple(np.array([-.001,y,1],dtype='float32').astype('float64'))
    def test_actual_inside_vertex_has_finite_same_triangle_edge_path(self):
        point=self.add_inside_boundary_vertex()
        self.assertTrue(self.validate()(*point));validate_native_mesh(self.own,self.parent)
    def test_near_vertex_height_limit_is_not_relaxed(self):
        point=self.add_inside_boundary_vertex(3.02)
        with self.assertRaises(AssertionError):self.validate()(*point)
    def test_near_vertex_without_incident_finite_edge_path_gets_no_credit(self):
        mesh=self.candidate['left']['nativeMesh'];i=len(mesh['position'])//3
        mesh['position'].extend([-.001,3.004,1,-.1,3.4,.9,-.2,3.8,1.1]);mesh['index'].extend([i,i+1,i+2])
        self.rebind('left');self.own=copy.deepcopy(self.candidate['left']);self.bind()
        point=tuple(np.array([-.001,3.004,1],dtype='float32').astype('float64'))
        self.assertFalse(self.validate()(*point))
    def test_exact_matching_rendered_strip_is_checked_without_height_credit(self):
        mesh=self.candidate['left']['nativeMesh'];i=len(mesh['position'])//3
        mesh['position'].extend([0,3,1,0,4,.5,0,4.000001,.5]);mesh['index'].extend([i,i+1,i+2])
        self.rebind('left');self.own=copy.deepcopy(self.candidate['left']);self.bind()
        self.assertTrue(self.validate()(0,4.000000953674316,.5))
    def test_vertical_strip_below_mate_cannot_claim_height_credit(self):
        mesh=self.candidate['left']['nativeMesh'];i=len(mesh['position'])//3
        mesh['position'].extend([0,2,1,0,3,.5,0,3.000001,.5]);mesh['index'].extend([i,i+1,i+2])
        self.rebind('left');self.own=copy.deepcopy(self.candidate['left']);self.bind()
        self.assertFalse(self.validate()(0,2,1))
    def test_proof_change_is_rejected(self):
        path=self.root/'proof.json';path.write_text('{}')
        with self.assertRaises(AssertionError):self.validate()


if __name__=='__main__':unittest.main()
