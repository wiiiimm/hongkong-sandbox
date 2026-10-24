"""Read-only original FBX hierarchy/double-array evidence inside Blender.

No importer transform, fitting, triangulation, source edits or publication.
Only the explicit authored translation/metre East-North-Up contract can
produce a viewer-coordinate diagnostic; unknown contracts remain recorded.
"""
import bpy,sys,json,hashlib
from pathlib import Path
import numpy as np
for p in bpy.utils.script_paths():sys.path.insert(0,str(Path(p)/'addons_core'))
from io_scene_fbx import parse_fbx
ROOT=Path(__file__).resolve().parents[3]
ACQUIRE=ROOT/'docs/astra-city/government-import/government-xl-lee-kong-145527-original-fbx-acquisition-v1-20261011'
DOC=ROOT/'docs/astra-city/government-import/government-xl-lee-kong-145527-original-raw-fbx-inspection-v2-20261011'
LOCAL=ROOT/'source-scripts/city/government-import/local'/DOC.name
def prop(e):
 p=next((c for c in e.elems if c.id==b'Properties70'),None)
 return {c.props[0].decode():c.props[4:]for c in p.elems if c.id==b'P'}if p else {}
def literal(v):
 if isinstance(v,dict):return {str(k):literal(x)for k,x in v.items()}
 if isinstance(v,bytes):return dict(rawBytesHex=v.hex(),decodedUTF8=v.decode('utf8',errors='replace'))
 if isinstance(v,(list,tuple)):return [literal(x)for x in v]
 return v
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
assert not DOC.exists()and not LOCAL.exists()
parser_path=Path(parse_fbx.__file__).resolve();parser_bytes=parser_path.read_bytes();parser_sha=hashlib.sha256(parser_bytes).hexdigest();binary_path=Path(bpy.app.binary_path).resolve();binary_sha=hashlib.sha256(binary_path.read_bytes()).hexdigest()
rows=json.loads((ACQUIRE/'untouched-current-fbx-sources.json').read_text())['rows'];assert len(rows)==1;row=rows[0]
assert row['uid']=='landsd/145527:0'and row['modelId']=='B355721853801063C0'
path=ROOT/row['sourcePath'];before=ref(path);assert before['sha256']==row['sourceSHA256']
tree,version=parse_fbx.parse(str(path));objects=next(c for c in tree.elems if c.id==b'Objects');models=[c for c in objects.elems if c.id==b'Model'];geometries=[c for c in objects.elems if c.id==b'Geometry'];connections=next(c for c in tree.elems if c.id==b'Connections');links=[c.props for c in connections.elems if c.id==b'C'];settings=prop(next(c for c in tree.elems if c.id==b'GlobalSettings'))
reasons=[]
if len(models)!=1 or len(geometries)!=1:reasons.append('requires-independent-complete-multipart-hierarchy-transform-interpretation')
expected={'UnitScaleFactor':[100.0],'UpAxis':[2],'CoordAxis':[0],'FrontAxis':[1],'UpAxisSign':[1],'CoordAxisSign':[1],'FrontAxisSign':[-1]}
if any(settings.get(k)!=v for k,v in expected.items()):reasons.append('unknown-authored-unit-or-axis-contract')
out=dict(source=row,untouchedFBX=before,rawFBXVersion=version,completeModelCount=len(models),completeGeometryCount=len(geometries),completeConnections=literal(links),rawGlobalSettings=literal(settings),completeModelProperties=[dict(sourceObjectID=m.props[0],sourceName=literal(m.props[1]),rawProperties=literal(prop(m)))for m in models],supportedTranslationOnlyMetreEastNorthUpContract=False,sourceGeometryChanges=0,sourceFormatAcceptanceInherited=False,currentAcceptance=False,installationApproved=False)
if len(models)==len(geometries)==1:
 model,geom=models[0],geometries[0];properties=prop(model)
 if properties.get('Lcl Rotation',[0,0,0])!=[0,0,0]or properties.get('Lcl Scaling',[1,1,1])!=[1,1,1]:reasons.append('nontranslation-authored-transform-needs-independent-interpretation')
 if any('Geometric'in k or 'Pivot'in k or 'PreRotation'in k or 'PostRotation'in k for k in properties):reasons.append('additional-authored-pivot-or-geometric-transform-not-interpreted')
 if [b'OO',geom.props[0],model.props[0]]not in links or [b'OO',model.props[0],0]not in links:reasons.append('root-geometry-world-link-not-explicit')
 verts_node=next(c for c in geom.elems if c.id==b'Vertices');indices_node=next(c for c in geom.elems if c.id==b'PolygonVertexIndex');vertices=np.asarray(verts_node.props[0],dtype='<f8').reshape(-1,3);encoded=np.asarray(indices_node.props[0],dtype=np.int64);ends=np.flatnonzero(encoded<0);sizes=np.diff(np.r_[-1,ends]);indices=np.where(encoded<0,-encoded-1,encoded)
 assert np.isfinite(vertices).all()and len(encoded)>0 and ends[-1]==len(encoded)-1 and indices.min()>=0 and indices.max()<len(vertices)
 out.update(sourceGeometryObjectID=geom.props[0],sourceGeometryRootName=literal(geom.props[1]),sourceVertexArrayType=str(verts_node.props[0].typecode),completeSourceControlPointCount=len(vertices),completeOriginalPolygonCount=len(sizes),completeOriginalPolygonSizeCensus={str(int(n)):int((sizes==n).sum())for n in np.unique(sizes)},completeUnusedSourceControlPoints=sorted(set(range(len(vertices)))-set(map(int,indices))),completeControlPointSHA256=hashlib.sha256(vertices.tobytes()).hexdigest(),completeEncodedPolygonIndexSHA256=hashlib.sha256(encoded.astype('<i8').tobytes()).hexdigest())
 if not np.all(sizes==3):reasons.append('nontriangular-source-polygons-retained-without-triangulation')
 translation=properties.get('Lcl Translation')
 if translation is None or len(translation)!=3 or not np.isfinite(translation).all():reasons.append('missing-or-nonfinite-authored-translation')
 LOCAL.mkdir(parents=True);np.savez_compressed(LOCAL/'complete-original-control-points-and-polygons.npz',vertices=vertices,encodedPolygonIndices=encoded,polygonSizes=sizes)
 if not reasons:
  absolute=vertices+np.asarray(translation,dtype='<f8');viewer=np.column_stack([absolute[:,0]-834500,absolute[:,2],816500-absolute[:,1]]);tri=viewer[indices.reshape(-1,3)];np.savez_compressed(LOCAL/'complete-original-viewer-world.npz',originalControlPoints=vertices,absoluteWorldControlPoints=absolute,viewerWorldControlPoints=viewer,indices=indices.reshape(-1,3),triangles=tri)
  out.update(supportedTranslationOnlyMetreEastNorthUpContract=True,authoredTranslation=list(translation),coordinateDerivation='Unchanged original double control points plus authored translation; 100 source centimetres represent one metre. East/North/Up maps to viewer (East-834500, Up, 816500-North); no fitted alignment or rotation.',completeViewerWorldTriangleCount=len(tri),completeViewerWholeControlPointBounds=[viewer.min(0).tolist(),viewer.max(0).tolist()],completeViewerWorldTriangleSHA256=hashlib.sha256(tri.astype('<f8').tobytes()).hexdigest())
out['unresolvedConventionReasons']=reasons;assert ref(path)==before and hashlib.sha256(parser_path.read_bytes()).hexdigest()==parser_sha and hashlib.sha256(binary_path.read_bytes()).hexdigest()==binary_sha;DOC.mkdir(parents=True);toolchain=DOC/'toolchain';toolchain.mkdir();archived_parser=toolchain/'parse_fbx.py';archived_parser.write_bytes(parser_bytes);out['inspectionToolchain']=dict(blenderVersion=bpy.app.version_string,blenderVersionTuple=list(bpy.app.version),executablePath=str(binary_path),executableSHA256=binary_sha,installedParserModulePath=str(parser_path),installedParserModuleSHA256=parser_sha,archivedParserSource=ref(archived_parser),startAndEndToolSourceHashesVerified=True);(DOC/'inspection.json').write_text(json.dumps(out,indent=2));print(json.dumps(dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],supportedCoordinateContract=not reasons,reasons=reasons,triangles=out.get('completeViewerWorldTriangleCount'))),flush=True)
