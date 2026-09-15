"""Bake verified official glTF models into the existing city building geometry contract.
Retains node transforms, triangle order, source normals/colours and HKPD elevation.
No elevation correction, simplification, or inferred geometry is introduced.
"""
import gzip, hashlib, json, pathlib
import numpy as np
from prepare_model_sample import matrix
HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[3]
ASSETS=HERE/'model-sample'
DTYPES={5120:'i1',5121:'u1',5122:'<i2',5123:'<u2',5125:'<u4',5126:'<f4'}
SIZES={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}


def decode(data,index,folder):
    a=data['accessors'][index];v=data['bufferViews'][a['bufferView']]
    assert 'sparse' not in a and not a.get('normalized',False),'Source format requires explicit additional validation'
    dtype=np.dtype(DTYPES[a['componentType']]);size=SIZES[a['type']]
    buffer=(folder/data['buffers'][v['buffer']]['uri']).read_bytes()
    return np.ndarray((a['count'],size),dtype=dtype,buffer=buffer,
        offset=v.get('byteOffset',0)+a.get('byteOffset',0),
        strides=(v.get('byteStride',dtype.itemsize*size),dtype.itemsize)).copy()


def bake(spec, assets=ASSETS):
    path=assets/spec['url'];data=json.loads(path.read_text());parts=[]
    def visit(index,parent):
        node=data['nodes'][index];transform=parent@matrix(node)
        if 'mesh' in node:
            for primitive in data['meshes'][node['mesh']]['primitives']:
                assert primitive.get('mode',4)==4
                attributes=primitive['attributes'];positions=decode(data,attributes['POSITION'],path.parent).astype(float)
                positions=(np.c_[positions,np.ones(len(positions))]@transform.T)[:,:3]
                positions[:,0]-=834500;positions[:,2]+=816500
                normals=decode(data,attributes['NORMAL'],path.parent).astype(float)
                normals=normals@np.linalg.inv(transform[:3,:3]);lengths=np.linalg.norm(normals,axis=1)[:,None]
                # Some adjacent official models contain zero source normals. Preserve
                # them as finite zero vectors instead of turning them into NaN.
                normals=np.divide(normals,lengths,out=np.zeros_like(normals),where=lengths>1e-12)
                indices=decode(data,primitive['indices'],path.parent).reshape(-1) if 'indices' in primitive else np.arange(len(positions))
                assert len(indices)%3==0 and indices.max()<len(positions)
                part={'position':positions[indices],'normal':normals[indices],'material':primitive.get('material',0)}
                if 'COLOR_0' in attributes:part['colour']=decode(data,attributes['COLOR_0'],path.parent)[indices]
                parts.append(part)
        for child in node.get('children',[]):visit(child,transform)
    for index in data['scenes'][data.get('scene',0)]['nodes']:visit(index,np.eye(4))
    # Current tile has one source material per building. Never discard a new split silently.
    assert len(set(p['material'] for p in parts))==1
    position=np.concatenate([p['position'] for p in parts]);normal=np.concatenate([p['normal'] for p in parts])
    bounds=[position.min(axis=0).tolist(),position.max(axis=0).tolist()]
    assert np.max(np.abs(np.array(bounds)-spec['worldBounds']))<1e-8
    assert np.isfinite(position).all() and np.isfinite(normal).all()
    record={'modelId':spec['id'],'position':position.reshape(-1).tolist(),'normal':normal.reshape(-1).tolist(),
        'zeroSourceNormalVertices':int((np.linalg.norm(normal,axis=1)<=1e-12).sum()),'worldBounds':bounds,'vertices':len(position),'triangles':len(position)//3,'source':spec['sourceEntry'],
        'sourceHashes':spec['sourceHashes'],'sourceMaterials':data.get('materials',[]),
        'sourceMaterialIndex':parts[0]['material'],'officialMatches':spec['officialMatches']}
    if all('colour' in p for p in parts):
        colours=np.concatenate([p['colour'] for p in parts]);record['colour']=colours.reshape(-1).tolist();record['colourItemSize']=colours.shape[1]
    return record


def main():
    manifest_path=ASSETS/'manifest.json';manifest=json.loads(manifest_path.read_text())
    fallback_path=ROOT/'3d-viewer/city/data/mui-wo-buildings.json';fallback=json.loads(fallback_path.read_text())
    by_csuid={}
    for b in fallback['buildings']:by_csuid.setdefault(b['buildingCSUID'],[]).append(b['uid'])
    result={};duplicate=[]
    for spec in manifest['models']:
        if not spec['replacementVerified']:continue
        # The sample has exact one-to-one matches. Multipart ambiguity is deliberately rejected.
        assert len(spec['officialBuildingCSUIDs'])==1
        csuid=spec['officialBuildingCSUIDs'][0];uids=by_csuid[csuid];assert len(uids)==1
        uid=uids[0];assert uid not in result
        result[uid]={'buildingCSUID':csuid,**bake(spec)}
    output={'schemaVersion':1,'kind':'official-building-model-geometries','datasetId':manifest['datasetId'],
        'tile':manifest['tile'],'tileRevision':manifest['tileRevision'],'crs':'EPSG:2326',
        'origin':[834500,816500],'verticalDatum':'Hong Kong Principal Datum',
        'coordinatePolicy':'Unindexed source triangles transformed through the exact glTF node hierarchy, then x=E-834500,y=HKPD height,z=816500-N. No source height change or geometric simplification. JSON retains double precision; the existing renderer may upload Float32 attributes.',
        'normalPolicy':'Source normals transformed with inverse transpose, normalised; triangle order unchanged.',
        'materialPolicy':'Source vertex colours and material factors are retained here for evidence. The city may intentionally use its existing facade palette and window shader as a presentation choice.',
        'manifestSource':'manifest.json','manifestSha256':hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        'officialFootprintSourceSha256':manifest['officialFootprintSnapshotSha256'],
        'counts':{'matchedBuildingGeometries':len(result),'triangles':sum(r['triangles'] for r in result.values()),'vertices':sum(r['vertices'] for r in result.values()),'unmatchedModelsExcluded':sum(not m['replacementVerified'] for m in manifest['models'])},
        'byBuildingUid':result}
    raw=json.dumps(output,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode();dest=ASSETS/'model-geometries.json';dest.write_bytes(raw)
    check={'file':dest.name,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'gzipBytes':len(gzip.compress(raw,mtime=0)),**output['counts']}
    (HERE/'model-geometry-bake.json').write_text(json.dumps(check,indent=2)+'\n');print(json.dumps(check,indent=2))
if __name__=='__main__':main()
