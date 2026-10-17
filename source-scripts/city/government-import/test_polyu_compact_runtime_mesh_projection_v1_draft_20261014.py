"""UNEXECUTED compact mesh/provenance count/hash fixtures, synthetic only."""
from pathlib import Path
import copy,json,subprocess,unittest
import polyu_compact_runtime_mesh_projection_v1_draft_20261014 as h
class ProjectionFixtures(unittest.TestCase):
    def setUp(self):
        self.mesh=dict(position=[-0.0,2,0,1,2,0,0,2,1,9,9,9],index=[0,1,2]);self.source=dict(path='saved/complete-nominee.json.gz',sha256='1'*64)
        self.bound=h.mesh_binding(self.mesh);self.preserved=dict(unchangedPriorFacets=1,unchangedOldMappings=1,unchangedPrefixFacets=1,retainedPriorPositionVertices=4)
        self.projection=h.project(self.mesh,self.source,self.bound,self.preserved)
    def test_complete_projection_preserves_input_unused_and_signed_zero(self):
        before=copy.deepcopy(self.mesh);h.verify(self.projection,self.source,self.bound,self.preserved);self.assertEqual(self.mesh,before)
        changed=copy.deepcopy(self.mesh);changed['position'][0]=0.0;self.assertNotEqual(h.mesh_binding(changed),self.bound)
        changed=copy.deepcopy(self.mesh);changed['position'][-1]=8;self.assertNotEqual(h.mesh_binding(changed),self.bound)
    def test_wrong_source_nomination_reference_rejected(self):
        self.projection['sourceNominationRef']['sha256']='2'*64
        with self.assertRaises(AssertionError):h.verify(self.projection,self.source,self.bound,self.preserved)
    def test_wrong_complete_mesh_hash_rejected(self):
        self.projection['meshBinding']['completeMeshTupleSHA256']='3'*64
        with self.assertRaises(AssertionError):h.verify(self.projection,self.source,self.bound,self.preserved)
    def test_wrong_counts_and_preservation_counts_rejected(self):
        for field in ['completeIndexedFaces','completePositionVertices']:
            q=copy.deepcopy(self.projection);q['meshBinding'][field]+=1
            with self.assertRaises(AssertionError):h.verify(q,self.source,self.bound,self.preserved)
        q=copy.deepcopy(self.projection);q['preservationCounts']['unchangedOldMappings']=0
        with self.assertRaises(AssertionError):h.verify(q,self.source,self.bound,self.preserved)
    def test_changed_index_order_and_wrong_range_rejected(self):
        q=copy.deepcopy(self.projection);q['newNativeMesh']['index']=[0,2,1]
        with self.assertRaises(AssertionError):h.verify(q,self.source,self.bound,self.preserved)
        q['newNativeMesh']['index']=[0,1,4]
        with self.assertRaises(AssertionError):h.verify(q,self.source,self.bound,self.preserved)
    def test_changed_position_and_partial_mesh_rejected(self):
        for values in [[0,2,0,1,2,0,0,2,1],[0,2,0,1,2,0,0,3,1,9,9,9]]:
            q=copy.deepcopy(self.projection);q['newNativeMesh']['position']=values
            with self.assertRaises(AssertionError):h.verify(q,self.source,self.bound,self.preserved)
    def test_extra_provenance_or_approval_cannot_enter_native_mesh(self):
        q=copy.deepcopy(self.mesh);q['sourceOverlap']={}
        with self.assertRaises(AssertionError):h.mesh_binding(q)
        self.projection['physicalAccepted']=True
        with self.assertRaises(AssertionError):h.verify(self.projection,self.source,self.bound,self.preserved)
    def test_python_node_binary_tuple_and_negative_hash_count_contract(self):
        js=Path(__file__).with_name('polyu_compact_runtime_mesh_projection_v1_draft_20261014.mjs')
        for projection,passed in [(self.projection,True),({**self.projection,'meshBinding':{**self.bound,'completeMeshTupleSHA256':'3'*64}},False),({**self.projection,'meshBinding':{**self.bound,'completeIndexedFaces':2}},False)]:
            data=json.dumps(dict(projection=projection,sourceRef=self.source,expected=self.bound,preserved=self.preserved))
            p=subprocess.run(['node',str(js)],input=data,text=True,capture_output=True);self.assertEqual(p.returncode==0,passed,p.stderr)
if __name__=='__main__':unittest.main(verbosity=2)
