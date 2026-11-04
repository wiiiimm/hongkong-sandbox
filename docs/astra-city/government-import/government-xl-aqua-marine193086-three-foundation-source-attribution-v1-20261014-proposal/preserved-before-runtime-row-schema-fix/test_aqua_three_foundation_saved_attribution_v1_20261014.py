import unittest,hashlib,numpy as np
from types import SimpleNamespace
from aqua_three_foundation_saved_attribution_v1_20261014 import trace_foundation,source_index_binding
class Tests(unittest.TestCase):
    def fake(self):
        calls=[]
        def samples(*args,**kwargs):calls.append('samples');return np.array([6.,6.,6.,6.])
        def components(t,m):calls.append('components');return [np.array([0])]
        f=SimpleNamespace(connected_components=components,s=SimpleNamespace(context=SimpleNamespace(shared=SimpleNamespace(samples=samples))))
        def foundation(t,g,p):f.s.context.shared.samples(None);f.connected_components(t,np.array([True]));return dict(triangles=1,fullyBuriedUpwardTriangles=1)
        f.foundation_context=foundation;return f,calls,samples,components
    def test_observer_preserves_function_result_and_restores_dependencies(self):
        f,c,s,p=self.fake();original=f.foundation_context;r,m,h=trace_foundation(f,np.zeros((1,3,3)),None,None,dict(triangles=1,fullyBuriedUpwardTriangles=1));self.assertEqual(c,['samples','components']);self.assertIs(f.foundation_context,original);self.assertIs(f.connected_components,p);self.assertIs(f.s.context.shared.samples,s);self.assertEqual(m.tolist(),[True]);self.assertEqual(h.tolist(),[[6.]*4])
    def test_changed_saved_aggregate_fails_and_restores(self):
        f,c,s,p=self.fake()
        with self.assertRaises(AssertionError):trace_foundation(f,np.zeros((1,3,3)),None,None,dict(triangles=1,fullyBuriedUpwardTriangles=0))
        self.assertIs(f.connected_components,p);self.assertIs(f.s.context.shared.samples,s)
    def test_kernel_exception_restores(self):
        f,c,s,p=self.fake();f.foundation_context=lambda *args:(_ for _ in ()).throw(ValueError('failure'))
        with self.assertRaises(ValueError):trace_foundation(f,np.zeros((1,3,3)),None,None,{})
        self.assertIs(f.connected_components,p);self.assertIs(f.s.context.shared.samples,s)
    def pins(self):
        return dict(graph=dict(meshes=[dict(primitives=[dict(indices=1,attributes=dict(POSITION=0),material=0)])],accessors=[dict(type='VEC3',count=3),dict(type='SCALAR',count=3,componentType=5123,bufferView=0)],bufferViews=[dict(byteLength=6)],nodes=[dict(name='original')],materials=[{}]),allBufferViews=[dict(index=0,sha256=hashlib.sha256(np.array([0,1,2],dtype='<u2').tobytes()).hexdigest())])
    def test_complete_index_bytes_bind_original_face_ordinal(self):
        r=source_index_binding([0,1,2],3,self.pins());self.assertTrue(r['exactOriginalFaceOrdinals']);self.assertTrue(r['notSourceTopologyOrEngineeringCertificate'])
    def test_changed_order_index_or_unused_vertex_count_rejected(self):
        for ix,n in [([0,2,1],3),([0,1,65536],3),([0,.5,2],3),([0,1,2],4)]:
            with self.assertRaises(AssertionError):source_index_binding(ix,n,self.pins())
    def test_unproved_multi_primitive_or_accessor_offset_rejected(self):
        for case in ['multi','offset']:
            p=self.pins()
            if case=='multi':p['graph']['meshes'][0]['primitives']*=2
            else:p['graph']['accessors'][1]['byteOffset']=1
            with self.assertRaises(AssertionError):source_index_binding([0,1,2],3,p)
if __name__=='__main__':unittest.main()
