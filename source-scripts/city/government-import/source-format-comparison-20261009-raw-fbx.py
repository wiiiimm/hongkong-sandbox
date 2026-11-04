"""Inside Blender: inspect exact FBX binary double arrays and authored transforms.
Only accepts this cohort's explicit single root, triangular polygon, translation-only contract.
No fitted alignment, remeshing, source changes or coordinate rounding.
"""
import bpy,sys,json,hashlib
from pathlib import Path
import numpy as np
for p in bpy.utils.script_paths():sys.path.insert(0,str(Path(p)/'addons_core'))
from io_scene_fbx import parse_fbx
root=Path(__file__).resolve().parents[3];doc=root/'docs/astra-city/government-import/government-xl-source-format-comparison-20261009';local=root/'source-scripts/city/government-import/local/government-xl-source-format-comparison-20261009'
def prop(e):
 p=next((c for c in e.elems if c.id==b'Properties70'),None)
 return {c.props[0].decode():c.props[4:] for c in p.elems if c.id==b'P'} if p else {}
rows=[]
for row in json.loads((doc/'untouched-current-fbx-sources.json').read_text())['rows']:
 p=root/row['sourcePath'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sourceSHA256'];tree,ver=parse_fbx.parse(str(p));objs=next(c for c in tree.elems if c.id==b'Objects');models=[c for c in objs.elems if c.id==b'Model'];geoms=[c for c in objs.elems if c.id==b'Geometry'];cons=next(c for c in tree.elems if c.id==b'Connections');assert len(models)==len(geoms)==1
 model=models[0];geom=geoms[0];props=prop(model);settings=prop(next(c for c in tree.elems if c.id==b'GlobalSettings'))
 assert settings['UnitScaleFactor']==[100.0] and settings['UpAxis']==[2] and settings['CoordAxis']==[0] and settings['FrontAxis']==[1] and settings['UpAxisSign']==[1] and settings['CoordAxisSign']==[1] and settings['FrontAxisSign']==[-1]
 assert props.get('Lcl Rotation',[0,0,0])==[0,0,0] and props.get('Lcl Scaling',[1,1,1])==[1,1,1]
 assert all('Geometric' not in k and 'Pivot' not in k and 'PreRotation' not in k and 'PostRotation' not in k for k in props)
 links=[c.props for c in cons.elems if c.id==b'C'];assert [b'OO',geom.props[0],model.props[0]] in links and [b'OO',model.props[0],0] in links
 verts_node=next(c for c in geom.elems if c.id==b'Vertices');indices_node=next(c for c in geom.elems if c.id==b'PolygonVertexIndex');verts=np.array(verts_node.props[0],dtype=np.float64).reshape(-1,3);indices=np.array(indices_node.props[0],dtype=np.int64);ends=np.flatnonzero(indices<0);sizes=np.diff(np.r_[-1,ends]);assert np.all(sizes==3),(row['modelId'],np.unique(sizes,return_counts=True));indices=np.where(indices<0,-indices-1,indices).reshape(-1,3);world=verts+np.array(props['Lcl Translation'],dtype=np.float64);tri=world[indices];out=local/'raw-fbx'/row['modelId'];out.mkdir(parents=True,exist_ok=True);np.savez_compressed(out/'full-world-triangles.npz',triangles=tri,vertices=verts,indices=indices)
 inspection=json.loads((local/'blender-inspection/legacy'/row['modelId']/'inspection.json').read_text());legacy=np.load(local/'blender-inspection/legacy'/row['modelId']/'full-world-triangles.npz')['triangles'];item={'source':row,'rawFBXVersion':ver,'modelRootName':model.props[1].split(b'\x00')[0].decode(),'geometryRootName':geom.props[1].split(b'\x00')[0].decode(),'sourceVertexArrayType':str(verts_node.props[0].typecode),'worldTransform':'Exact authored Lcl Translation; source axes East/North/Up; UnitScaleFactor100cm=1m; no parent pose','translation':props['Lcl Translation'],'allPolygonsTriangular':True,'vertexCount':len(verts),'triangleCount':len(tri),'fullWorldBounds':[tri.min(axis=(0,1)).tolist(),tri.max(axis=(0,1)).tolist()],'worldTrianglesSHA256':hashlib.sha256(tri.astype('<f8').tobytes()).hexdigest(),'legacyImporterTriangleCount':len(legacy),'geometryChanges':0,'identityAccepted':False};(out/'inspection.json').write_text(json.dumps(item,indent=2));rows.append(item);print(json.dumps(item),flush=True)
(doc/'raw-fbx-coordinate-proof.json').write_text(json.dumps({'rows':rows},indent=2))
