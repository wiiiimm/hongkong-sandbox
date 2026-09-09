"""HKS-222 isolated geometry-only repair. Never edits original sources or viewer assets."""
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
import numpy as np

MATERIAL_EXTENSIONS={'KHR_materials_specular','KHR_materials_ior'}
DTYPES={5120:'i1',5121:'u1',5122:'<i2',5123:'<u2',5125:'<u4',5126:'<f4'}
WIDTHS={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}
ROOT_TRANSLATION=np.array([-834500.,0.,816500.])
sha=lambda b:hashlib.sha256(b).hexdigest()


def safe_uri(uri):
    p=PurePosixPath(uri)
    if not uri or p.is_absolute() or '..'in p.parts or '\\'in uri or ':'in uri:
        raise ValueError('Unsafe/external source URI')
    return p


def accessor(data,buffers,index):
    a=data['accessors'][index]
    if a.get('sparse') or a.get('normalized') or a.get('extensions'):
        raise ValueError('Unsupported sparse/normalised/extended geometry accessor')
    dtype=np.dtype(DTYPES[a['componentType']]);width=WIDTHS[a['type']]
    v=data['bufferViews'][a['bufferView']];raw=buffers[v['buffer']]
    count=a['count'];offset=a.get('byteOffset',0);stride=v.get('byteStride',width*dtype.itemsize);start=v.get('byteOffset',0)
    if type(count)is not int or count<1 or offset<0 or start<0 or stride<width*dtype.itemsize or start+v['byteLength']>len(raw) or offset+(count-1)*stride+width*dtype.itemsize>v['byteLength']:
        raise ValueError('Geometry accessor outside source buffer')
    return np.ndarray((count,width),dtype=dtype,buffer=raw,offset=start+offset,strides=(stride,dtype.itemsize))


def repair_model(original,read_buffer):
    """Return derived glTF/buffers plus proof. POSITION/index source bytes never change."""
    source=json.loads(original);data=copy.deepcopy(source);actions=[];raw_buffers=[];original_buffers={}
    for b in source.get('buffers',[]):
        uri=str(safe_uri(b['uri']));raw=read_buffer(uri)
        if len(raw)<b['byteLength']:raise ValueError('Truncated original buffer')
        raw_buffers.append(raw);original_buffers[uri]=raw
    source_hashes={'source.gltf':sha(original),**{uri:sha(raw)for uri,raw in original_buffers.items()}}
    if source.get('animations') or source.get('skins') or source.get('extensions'):
        raise ValueError('Animated/skinned/top-level extended source unsupported')
    declared=set(source.get('extensionsUsed',[]))|set(source.get('extensionsRequired',[]))
    if declared-MATERIAL_EXTENSIONS:raise ValueError('Non-material source extension unsupported')
    for material in source.get('materials',[]):
        if set(material.get('extensions',{}))-MATERIAL_EXTENSIONS:raise ValueError('Unknown material extension')
    for collection in ('meshes','nodes','bufferViews','buffers','accessors','scenes'):
        if any(v.get('extensions')for v in source.get(collection,[])):raise ValueError('Non-material extended geometry object')
    matrices=[]
    for index,node in enumerate(data.get('nodes',[])):
        if any(k in node for k in ('skin','weights')):raise ValueError('Skinned/morph nodes unsupported')
        if any(k in node for k in ('translation','rotation','scale')):
            if 'matrix'in node:raise ValueError('Node declares both matrix and TRS')
            t=np.asarray(node.pop('translation',[0,0,0]),dtype=np.float64)
            q=np.asarray(node.pop('rotation',[0,0,0,1]),dtype=np.float64)
            scale=np.asarray(node.pop('scale',[1,1,1]),dtype=np.float64)
            if t.shape!=(3,)or q.shape!=(4,)or scale.shape!=(3,)or not all(np.isfinite(v).all()for v in(t,q,scale))or np.any(scale==0):raise ValueError('Invalid finite source TRS')
            if abs(float(q@q)-1)>1e-6:raise ValueError('Source quaternion must be unit length')
            x,y,z,w=q;xx=2*x*x;yy=2*y*y;zz=2*z*z;xy=2*x*y;xz=2*x*z;yz=2*y*z;wx=2*w*x;wy=2*w*y;wz=2*w*z
            rotation=np.array([[1-yy-zz,xy-wz,xz+wy],[xy+wz,1-xx-zz,yz-wx],[xz-wy,yz+wx,1-xx-yy]])
            m=np.eye(4);m[:3,:3]=rotation*scale[None,:];m[:3,3]=t
            node['matrix']=m.T.reshape(-1).tolist()
            actions.append({'action':'source-trs-to-equivalent-matrix','node':index,'translation':t.tolist(),'quaternion':q.tolist(),'sourceScale':scale.tolist(),'order':'T * R * S','addedScale':1})
        m=np.asarray(node.get('matrix',np.eye(4).T.reshape(-1)),dtype=np.float64).reshape(4,4).T
        if not np.isfinite(m).all()or not np.array_equal(m[3],[0,0,0,1])or abs(np.linalg.det(m[:3,:3]))<1e-15:raise ValueError('Invalid source affine transform')
        matrices.append(m)
    meshes=data.get('meshes',[]);reachable=[];active=set()
    def visit(i,parent):
        if type(i)is not int or not 0<=i<len(matrices)or i in active:raise ValueError('Invalid/cyclic source scene')
        active.add(i);node=data['nodes'][i];world=parent@matrices[i]
        if not np.isfinite(world).all():raise ValueError('Non-finite accumulated transform')
        if 'mesh'in node:
            if not 0<=node['mesh']<len(meshes):raise ValueError('Invalid source mesh reference')
            reachable.append((node['mesh'],world))
        for child in node.get('children',[]):visit(child,world)
        active.remove(i)
    for i in data.get('scenes',[{'nodes':[]}])[data.get('scene',0)].get('nodes',[]):visit(i,np.eye(4))
    primitive_count=sum(len(m.get('primitives',[]))for m in meshes)
    if not primitive_count:
        return {'state':'source-empty','sourceHashes':source_hashes,'repairActions':[],
                'geometryProof':{'sourceMeshes':len(meshes),'sourcePrimitives':0,'reachablePrimitives':0,'verticalScale':1},'files':original_buffers}
    if not reachable:raise ValueError('Source mesh geometry exists but is unreachable')
    extra={};proof=[];positions={};total_triangles=0
    for mi,mesh in enumerate(meshes):
        if mesh.get('weights'):raise ValueError('Morph weights unsupported')
        for pi,p in enumerate(mesh.get('primitives',[])):
            if p.get('mode',4)!=4 or p.get('targets')or p.get('extensions'):raise ValueError('Non-triangle/morph/extended primitive unsupported')
            attrs=p['attributes'];pa=data['accessors'][attrs['POSITION']]
            if pa['componentType']!=5126 or pa['type']!='VEC3':raise ValueError('POSITION must be native float32 VEC3')
            position=accessor(data,raw_buffers,attrs['POSITION'])
            if not np.isfinite(position).all():raise ValueError('Invalid POSITION cannot be repaired mechanically')
            if 'indices'in p:
                ia=data['accessors'][p['indices']]
                if ia['type']!='SCALAR'or ia['componentType']not in(5121,5123,5125):raise ValueError('Invalid source index type')
                indices=accessor(data,raw_buffers,p['indices']).reshape(-1)
            else:indices=np.arange(len(position),dtype=np.uint32)
            if not len(indices)or len(indices)%3 or int(indices.max())>=len(position):raise ValueError('Invalid source triangle indices')
            positions[(mi,pi)]=position;total_triangles+=len(indices)//3
            original_attrs=copy.deepcopy(attrs)
            for key in list(attrs):
                if key.startswith('TEXCOORD_'):
                    del attrs[key];actions.append({'action':'omit-photograph-uv','mesh':mi,'primitive':pi,'attribute':key})
                elif key not in('POSITION','NORMAL','COLOR_0'):raise ValueError('Unknown primitive attribute')
            if 'COLOR_0'in attrs:
                colour=accessor(data,raw_buffers,attrs['COLOR_0'])
                if len(colour)!=len(position)or not np.isfinite(colour).all():raise ValueError('Invalid source vertex colours')
            normal=None
            if 'NORMAL'in attrs:
                normal=accessor(data,raw_buffers,attrs['NORMAL'])
            if normal is None or normal.shape!=position.shape or not np.isfinite(normal).all():
                # Shading-only replacement; degenerate triangles remain in the mesh.
                tri=indices.reshape(-1,3);v=position.astype(np.float64);n=np.zeros_like(v)
                face=np.cross(v[tri[:,1]]-v[tri[:,0]],v[tri[:,2]]-v[tri[:,0]])
                for corner in range(3):np.add.at(n,tri[:,corner],face)
                lengths=np.linalg.norm(n,axis=1);zero=lengths==0;n[~zero]/=lengths[~zero,None];n[zero]=[0,1,0]
                normal=n.astype('<f4');name=f'repair-normal-{mi}-{pi}.bin'
                if name in original_buffers:raise ValueError('Derived normal filename conflicts with source')
                raw=normal.tobytes();bi=len(data['buffers']);data['buffers'].append({'uri':name,'byteLength':len(raw)});raw_buffers.append(raw);extra[name]=raw
                vi=len(data['bufferViews']);data['bufferViews'].append({'buffer':bi,'byteOffset':0,'byteLength':len(raw),'target':34962})
                ai=len(data['accessors']);data['accessors'].append({'bufferView':vi,'byteOffset':0,'componentType':5126,'count':len(normal),'type':'VEC3'});attrs['NORMAL']=ai
                actions.append({'action':'regenerate-shading-normals','mesh':mi,'primitive':pi,'zeroNormalVertices':int(zero.sum()),'zeroNormalPolicy':'Finite up-vector for shading only; source triangles unchanged'})
            proof.append({'mesh':mi,'primitive':pi,'vertices':len(position),'triangles':len(indices)//3,'positionAccessor':original_attrs['POSITION'],'positionBytesSHA256':sha(position.tobytes()),'indexAccessor':p.get('indices'),'indexBytesSHA256':sha(indices.tobytes()),'positionAndIndexAccessorsUnchanged':True})
    bounds=[];reachable_primitives=0
    for mi,m in reachable:
        for pi,_ in enumerate(meshes[mi].get('primitives',[])):
            v=positions[(mi,pi)].astype(np.float64);world=v@m[:3,:3].T+m[:3,3]+ROOT_TRANSLATION
            if not np.isfinite(world).all():raise ValueError('Non-finite native world coordinates')
            bounds.append([world.min(axis=0),world.max(axis=0)]);reachable_primitives+=1
    if not bounds:raise ValueError('No reachable geometry')
    for key in ('images','textures','samplers','extensionsUsed','extensionsRequired'):data.pop(key,None)
    for material in data.get('materials',[]):
        material.pop('extensions',None)
        for key in ('normalTexture','occlusionTexture','emissiveTexture'):material.pop(key,None)
        for key in ('baseColorTexture','metallicRoughnessTexture'):material.get('pbrMetallicRoughness',{}).pop(key,None)
    if declared:actions.append({'action':'omit-material-only-extensions','extensions':sorted(declared)})
    actions.append({'action':'omit-photographs-and-texture-references'})
    # Re-decode the derived references to prove they still read the original geometry.
    for entry in proof:
        p=data['meshes'][entry['mesh']]['primitives'][entry['primitive']]
        if sha(accessor(data,raw_buffers,p['attributes']['POSITION']).tobytes())!=entry['positionBytesSHA256']:raise AssertionError('Position bytes changed')
        if 'indices'in p and sha(accessor(data,raw_buffers,p['indices']).reshape(-1).tobytes())!=entry['indexBytesSHA256']:raise AssertionError('Index bytes changed')
    derived=json.dumps(data,separators=(',',':'),allow_nan=False).encode()
    world_bounds=[np.min(np.array(bounds)[:,0],axis=0).tolist(),np.max(np.array(bounds)[:,1],axis=0).tolist()]
    return {'state':'prepared-geometry-only','sourceHashes':source_hashes,'repairActions':actions,
            'geometryProof':{'sourceMeshes':len(meshes),'sourcePrimitives':primitive_count,'reachablePrimitives':reachable_primitives,'triangles':total_triangles,'sourcePositionsAndIndicesPreserved':True,'primitives':proof,'worldBounds':world_bounds,'rootTranslation':ROOT_TRANSLATION.tolist(),'verticalScale':1},
            'files':{**original_buffers,**extra,'geometry.gltf':derived}}
