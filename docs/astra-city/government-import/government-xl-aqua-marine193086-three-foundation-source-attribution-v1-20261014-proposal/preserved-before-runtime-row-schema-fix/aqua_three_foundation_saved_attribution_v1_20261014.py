"""Trace the unchanged foundation selector and authenticate original face indices."""
import hashlib,numpy as np
from copy import deepcopy

def trace_foundation(final,tri,ground,target,saved):
    old_components=final.connected_components;old_samples=final.s.context.shared.samples;trace={}
    def components(t,mask):trace['mask']=np.asarray(mask,dtype=bool).copy();return old_components(t,mask)
    def samples(*args,**kwargs):
        result=old_samples(*args,**kwargs);trace['heights']=np.asarray(result,dtype='<f8').copy();return result
    final.connected_components=components;final.s.context.shared.samples=samples
    try:result=final.foundation_context(tri,ground,target)
    finally:final.connected_components=old_components;final.s.context.shared.samples=old_samples
    import json
    encoded=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
    assert encoded(result)==encoded(saved),'Unchanged selector no longer matches actual saved aggregate'
    assert trace['mask'].shape==(len(tri),)and trace['heights'].size==len(tri)*4
    return result,trace['mask'],trace['heights'].reshape(-1,4)

def source_index_binding(index,vertex_count,pins):
    graph=pins['graph'];assert len(graph['meshes'])==1 and len(graph['meshes'][0]['primitives'])==1
    primitive=graph['meshes'][0]['primitives'][0];accessor=graph['accessors'][primitive['indices']];position=graph['accessors'][primitive['attributes']['POSITION']]
    assert accessor['componentType']==5123 and accessor['type']=='SCALAR'and accessor['count']==len(index)
    assert position['count']==vertex_count and position['type']=='VEC3'
    ids=np.asarray(index);assert np.all(ids>=0)and np.all(ids<vertex_count)and np.all(ids==ids.astype(np.uint16))
    view=graph['bufferViews'][accessor['bufferView']];assert view['byteLength']==len(index)*2 and accessor.get('byteOffset',0)==0
    expected=next(r for r in pins['allBufferViews']if r['index']==accessor['bufferView']);actual=hashlib.sha256(ids.astype('<u2').tobytes()).hexdigest();assert actual==expected['sha256'],'Runtime/source face ordinal correspondence is unresolved'
    return dict(exactOriginalFaceOrdinals=True,sourceIndexAccessor=primitive['indices'],sourcePositionAccessor=primitive['attributes']['POSITION'],completeIndexBufferSHA256=actual,completeVerticesIncludingUnused=vertex_count,primitiveVerbatim=deepcopy(primitive),originalNodesVerbatim=deepcopy(graph['nodes']),materialsVerbatim=deepcopy(graph.get('materials',[])),notSourceTopologyOrEngineeringCertificate=True)
