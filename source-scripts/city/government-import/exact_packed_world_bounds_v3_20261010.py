"""Readonly complete original packed geometry bounds, no catalogue bound trust."""
import gzip,json,struct,numpy as np,hashlib

def packed_world_bounds(raw):
 data=gzip.decompress(raw);magic,version,total=struct.unpack_from('<III',data)
 assert magic==0x46546c67 and version==2 and total==len(data)
 size,kind=struct.unpack_from('<II',data,12);assert kind==0x4e4f534a
 doc=json.loads(data[20:20+size]);size2,kind2=struct.unpack_from('<II',data,20+size)
 assert kind2==0x004e4942 and 28+size+size2==len(data)
 binary=data[28+size:];assert len(doc['buffers'])==1 and not doc['buffers'][0].get('uri')
 def access(index):
  a=doc['accessors'][index];v=doc['bufferViews'][a['bufferView']]
  assert not a.get('normalized') and not a.get('sparse') and v['buffer']==0
  width={'VEC3':3,'SCALAR':1}[a['type']];dtype=np.dtype({5126:'<f4',5123:'<u2',5125:'<u4'}[a['componentType']]);stride=v.get('byteStride',width*dtype.itemsize)
  assert stride>=width*dtype.itemsize
  return np.ndarray((a['count'],width),dtype=dtype,buffer=binary,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(stride,dtype.itemsize))
 parts=[];position_parts=[];visited=[];unused=0
 def visit(index,parent,ancestors):
  nonlocal unused
  assert index not in ancestors,'Cyclic hierarchy';node=doc['nodes'][index]
  assert not any(k in node for k in ['translation','rotation','scale']),'Unreviewed TRS'
  matrix=np.asarray(node.get('matrix',np.eye(4).reshape(-1,order='F').tolist()),float).reshape(4,4,order='F');assert np.isfinite(matrix).all()
  assert np.array_equal(matrix[3],np.array([0.,0.,0.,1.])), 'Non-affine provider node matrix'
  transform=parent@matrix;visited.append(index)
  if 'mesh' in node:
   for primitive in doc['meshes'][node['mesh']]['primitives']:
    assert primitive.get('mode',4)==4 and 'indices' in primitive
    v=access(primitive['attributes']['POSITION']).astype(float);ids=access(primitive['indices']).reshape(-1)
    assert len(ids)%3==0 and (ids>=0).all() and (ids<len(v)).all()
    v=(np.c_[v,np.ones(len(v))]@transform.T)[:,:3]+np.array([-834500,0,816500])
    position_parts.append(v);unused+=len(v)-len(np.unique(ids));parts.append(v[ids].reshape(-1,3,3))
  for child in node.get('children',[]):visit(child,transform,ancestors|{index})
 for root in doc['scenes'][doc.get('scene',0)]['nodes']:visit(root,np.eye(4),set())
 tri=np.concatenate(parts);assert np.isfinite(tri).all()
 positions=np.concatenate(position_parts);assert np.isfinite(positions).all()
 return {'sourceSHA256':hashlib.sha256(raw).hexdigest(),'originalWholeSourceBounds':[positions.min(axis=0).tolist(),positions.max(axis=0).tolist()],'originalIndexedFaceBounds':[tri.min(axis=(0,1)).tolist(),tri.max(axis=(0,1)).tolist()],'completeOriginalPositionVertices':len(positions),'originalUnreferencedPositionVertices':unused,'allOriginalPositionVerticesAccounted':True,'completeOriginalTriangles':len(tri),'worldTrianglesSHA256':hashlib.sha256(tri.tobytes()).hexdigest(),'sceneNodesTraversed':visited}
