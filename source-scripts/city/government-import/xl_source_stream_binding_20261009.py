"""Bind original packed provider triangle attributes and complete hierarchy."""
import gzip
import hashlib
import json
import struct
import numpy as np

def sha(data):return hashlib.sha256(data).hexdigest()

def source_stream_binding(raw):
    data=gzip.decompress(raw)
    magic,version,total=struct.unpack_from('<III',data,0)
    assert magic==0x46546c67 and version==2 and total==len(data)
    size,kind=struct.unpack_from('<II',data,12);assert kind==0x4e4f534a
    doc=json.loads(data[20:20+size]);bsize,bkind=struct.unpack_from('<II',data,20+size)
    assert bkind==0x004e4942;binary=data[28+size:28+size+bsize]
    assert len(doc['meshes'])==1 and len(doc['meshes'][0]['primitives'])==1
    primitive=doc['meshes'][0]['primitives'][0];assert primitive.get('mode',4)==4
    def access(index):
        a=doc['accessors'][index];v=doc['bufferViews'][a['bufferView']]
        assert not a.get('normalized') and not a.get('sparse')
        width={'VEC3':3,'SCALAR':1}[a['type']];dtype={5126:'<f4',5123:'<u2',5125:'<u4'}[a['componentType']]
        assert v.get('byteStride',np.dtype(dtype).itemsize*width)==np.dtype(dtype).itemsize*width
        return np.frombuffer(binary,dtype=dtype,count=a['count']*width,
            offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(a['count'],width)
    ids=access(primitive['indices']).ravel();assert len(ids)%3==0
    result={'sourceSHA256':sha(raw)}
    for name,key in [('POSITION','position'),('NORMAL','normal'),('COLOR_0','colour')]:
        values=access(primitive['attributes'][name])[ids];assert np.isfinite(values).all()
        result[key+'TriangleStreamSHA256']=sha(values.tobytes())
    roots=doc['scenes'][doc.get('scene',0)]['nodes'];assert len(roots)==1
    result['rootMatrix']=doc['nodes'][roots[0]]['matrix']
    hierarchy={k:doc[k] for k in ['nodes','scenes','materials']}
    result['sourceHierarchySHA256']=sha(json.dumps(hierarchy,sort_keys=True,separators=(',',':')).encode())
    return result
