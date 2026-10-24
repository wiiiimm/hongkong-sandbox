import copy
import unittest
from original_source_ownership import graph_reasons

def fixture():
    return {'asset':{'version':'2.0'},'buffers':[{'byteLength':256}],
        'bufferViews':[{'buffer':0,'byteLength':256}],
        'accessors':[{'bufferView':0,'count':3},{'bufferView':0,'count':3}],
        'scenes':[{'nodes':[0]}],'nodes':[{'name':'B123','matrix':[1,0,0,0,0,0,-1,0,0,1,0,0,834500,5,-816500,1],'children':[1]},{'mesh':0}],
        'meshes':[{'primitives':[{'attributes':{'POSITION':0},'indices':1}]}]}

class OriginalSourceGraph(unittest.TestCase):
    def test_one_exact_root_accounts_for_all_geometry(self):
        self.assertEqual(graph_reasons(fixture(),'B123',1),[])
    def test_wrong_root_and_scaled_pose_are_rejected(self):
        g=fixture();g['nodes'][0]['name']='B999';g['nodes'][0]['matrix'][0]=2
        self.assertIn('source-root-name',graph_reasons(g,'B123',1));self.assertIn('original-unit-hkpd-root-pose',graph_reasons(g,'B123',1))
    def test_foreign_root_even_if_same_scene_is_rejected(self):
        g=fixture();g['nodes'].append({'name':'B999','mesh':0});g['scenes'][0]['nodes'].append(2)
        self.assertIn('single-exact-source-root-required',graph_reasons(g,'B123',1))
    def test_unreachable_mesh_is_not_owned(self):
        g=fixture();g['meshes'].append(copy.deepcopy(g['meshes'][0]))
        self.assertIn('unowned-or-repeated-source-meshes',graph_reasons(g,'B123',1))
    def test_cycles_and_shared_nodes_are_rejected(self):
        g=fixture();g['nodes'][1]['children']=[0]
        self.assertIn('cycle-or-repeated-node',graph_reasons(g,'B123',1))
        g=fixture();g['nodes'][0]['children']=[1,1]
        self.assertIn('cycle-or-repeated-node',graph_reasons(g,'B123',1))
    def test_foreign_actor_pose_and_external_data_are_rejected(self):
        g=fixture();g['nodes'][1].update(name='another-building',scale=[1,1,1],camera=0);g['buffers'][0]['uri']='foreign.bin'
        reasons=graph_reasons(g,'B123',1)
        for expected in ['foreign-named-child','additional-child-pose','additional-source-actor','external-or-multiple-source-buffers']:self.assertIn(expected,reasons)
    def test_full_face_accounting_and_sparse_inputs(self):
        g=fixture();g['accessors'][0]['sparse']={}
        reasons=graph_reasons(g,'B123',2)
        self.assertIn('unhandled-accessor',reasons);self.assertIn('original-face-accounting',reasons)

if __name__=='__main__':unittest.main()
