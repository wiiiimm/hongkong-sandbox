"""Inside Blender: preserve and census every raw FBX model/geometry/connection.

No scene import, transform fitting, polygon triangulation or geometry edits.
A multipart hierarchy is reported as authored, without assuming a coordinate
contract or accepting it for installation.
"""
import bpy, sys, json, hashlib
from pathlib import Path
import numpy as np
for path in bpy.utils.script_paths():sys.path.insert(0,str(Path(path)/'addons_core'))
from io_scene_fbx import parse_fbx
ROOT=Path(__file__).resolve().parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=sha(p))
def literal(value):
    if isinstance(value,bytes):return dict(rawBytesHex=value.hex(),decodedUTF8=value.decode('utf8',errors='replace'))
    if isinstance(value,dict):return {str(k):literal(v)for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [literal(v)for v in value]
    return value

def properties(element):
    ps=next((e for e in element.elems if e.id==b'Properties70'),None)
    return {e.props[0].decode():e.props[4:]for e in ps.elems if e.id==b'P'}if ps else {}

args=sys.argv[sys.argv.index('--')+1:];assert len(args)==3
source_list,out,local=[(ROOT/a).resolve()for a in args]
assert all(p.is_relative_to(ROOT)for p in [source_list,out,local]) and not out.exists() and not local.exists()
rows=json.loads(source_list.read_text())['rows'];assert rows and len({r['sourcePath']for r in rows})==len(rows)
parser=Path(parse_fbx.__file__).resolve();binary=Path(bpy.app.binary_path).resolve();parser_sha,binary_sha=sha(parser),sha(binary)
out.mkdir(parents=True);local.mkdir(parents=True);toolchain=out/'toolchain';toolchain.mkdir();archived=toolchain/'parse_fbx.py';archived.write_bytes(parser.read_bytes());results=[]
for number,row in enumerate(rows):
    path=(ROOT/row['sourcePath']).resolve();assert path.is_relative_to(ROOT) and sha(path)==row['sourceSHA256']
    tree,version=parse_fbx.parse(str(path));objects=next(e for e in tree.elems if e.id==b'Objects');models=[e for e in objects.elems if e.id==b'Model'];geometries=[e for e in objects.elems if e.id==b'Geometry'];connections=next(e for e in tree.elems if e.id==b'Connections');links=[e.props for e in connections.elems if e.id==b'C'];settings=properties(next(e for e in tree.elems if e.id==b'GlobalSettings'))
    geometry_rows=[];arrays={}
    for index,geom in enumerate(geometries):
        v=next((e for e in geom.elems if e.id==b'Vertices'),None);i=next((e for e in geom.elems if e.id==b'PolygonVertexIndex'),None)
        item=dict(sourceObjectID=geom.props[0],sourceName=literal(geom.props[1]),sourceType=literal(geom.props[2:]),rawProperties=literal(properties(geom)))
        if v is not None and i is not None:
            vertices=np.asarray(v.props[0],dtype='<f8').reshape(-1,3);encoded=np.asarray(i.props[0],dtype='<i8');assert np.isfinite(vertices).all() and len(encoded)>0
            ends=np.flatnonzero(encoded<0);assert len(ends)>0 and ends[-1]==len(encoded)-1
            sizes=np.diff(np.r_[-1,ends]);indices=np.where(encoded<0,-encoded-1,encoded);assert indices.min()>=0 and indices.max()<len(vertices)
            arrays['geometry'+str(index)+'ControlPoints']=vertices;arrays['geometry'+str(index)+'EncodedPolygonIndices']=encoded
            item.update(sourceVertexArrayType=str(v.props[0].typecode),completeControlPoints=len(vertices),completeOriginalPolygons=len(sizes),originalPolygonSizeCensus={str(int(n)):int((sizes==n).sum())for n in np.unique(sizes)},unusedControlPointIndices=sorted(set(range(len(vertices)))-set(map(int,indices))),controlPointBounds=[vertices.min(0).tolist(),vertices.max(0).tolist()],controlPointSHA256=hashlib.sha256(vertices.tobytes()).hexdigest(),encodedPolygonIndicesSHA256=hashlib.sha256(encoded.tobytes()).hexdigest())
        geometry_rows.append(item)
    target=local/(str(number)+'-complete-original-arrays.npz');np.savez_compressed(target,**arrays)
    results.append(dict(source=row,rawFBXVersion=version,completeModelCount=len(models),completeGeometryCount=len(geometries),completeObjectTypeCensus={key.decode('utf8',errors='replace'):sum(e.id==key for e in objects.elems)for key in sorted({e.id for e in objects.elems})},rawGlobalSettings=literal(settings),completeModels=[dict(sourceObjectID=e.props[0],sourceName=literal(e.props[1]),sourceType=literal(e.props[2:]),rawProperties=literal(properties(e)))for e in models],completeGeometries=geometry_rows,completeConnections=literal(links),completeOriginalArrays=ref(target),sourceBytesUnchanged=sha(path)==row['sourceSHA256'],sourceGeometryChanges=0,sourcePoseChanges=0,coordinateContractInterpreted=False,identityAccepted=False,installationApproved=False))
assert sha(parser)==parser_sha and sha(binary)==binary_sha
result=dict(rows=results,inspectionToolchain=dict(blenderVersion=bpy.app.version_string,executablePath=str(binary),executableSHA256=binary_sha,installedParserModulePath=str(parser),installedParserModuleSHA256=parser_sha,archivedParserSource=ref(archived)),sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sceneImportUsed=False,sourceFormatAcceptanceInherited=False,installationApproved=False)
(out/'inspection.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(rows=[dict(modelId=r['source']['modelId'],models=r['completeModelCount'],geometries=r['completeGeometryCount'],modelNames=[m['sourceName']['decodedUTF8']for m in r['completeModels']])for r in results])),flush=True)
