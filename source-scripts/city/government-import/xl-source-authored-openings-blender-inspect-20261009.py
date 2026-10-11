"""Run inside factory-startup Blender: read-only FBX import and full geometry inspection.
No vertices, transforms, modifiers, hierarchy or source files edited; no .blend/export.
"""
import bpy,sys,json,gzip,hashlib
from pathlib import Path
import numpy as np
for p in bpy.utils.script_paths():sys.path.insert(0,str(Path(p)/'addons_core'))
from io_scene_fbx import parse_fbx as parse
root=Path(__file__).resolve().parents[3];doc=root/'docs/astra-city/government-import/government-xl-source-authored-openings-20261009';local=root/'source-scripts/city/government-import/local/government-xl-source-authored-openings-20261009'
mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'legacy'
def encode(v):
 if isinstance(v,bytes):return v.decode('utf8',errors='backslashreplace')
 if isinstance(v,np.ndarray):return v.tolist()
 if isinstance(v,(tuple,list)):return [encode(x) for x in v]
 return v
def props70(e):
 p=next((c for c in e.elems if c.id==b'Properties70'),None)
 return {encode(c.props[0]):encode(c.props[4:]) for c in p.elems if c.id==b'P'} if p else {}
for row in json.loads((doc/'untouched-current-fbx-sources.json').read_text())['rows']:
 p=root/row['sourcePath'];raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==row['sourceSHA256'];fbx,version=parse.parse(str(p));global_node=next(c for c in fbx.elems if c.id==b'GlobalSettings');objs=next(c for c in fbx.elems if c.id==b'Objects');conn=next(c for c in fbx.elems if c.id==b'Connections');original_models=[{'id':encode(c.props[0]),'name':encode(c.props[1]),'kind':encode(c.props[2]),'properties':props70(c)} for c in objs.elems if c.id==b'Model'];original_geometry=[{'id':encode(c.props[0]),'name':encode(c.props[1]),'kind':encode(c.props[2]),'vertices':next((len(k.props[0])//3 for k in c.elems if k.id==b'Vertices'),0),'polygonIndexEntries':next((len(k.props[0]) for k in c.elems if k.id==b'PolygonVertexIndex'),0)} for c in objs.elems if c.id==b'Geometry']
 bpy.ops.wm.read_factory_settings(use_empty=True)
 if mode=='legacy':result=bpy.ops.import_scene.fbx(filepath=str(p),global_scale=1.0,use_manual_orientation=False,bake_space_transform=False,use_anim=False,use_custom_props=True,use_image_search=False)
 else:result=bpy.ops.wm.fbx_import(filepath=str(p),global_scale=1.0,import_subdivision=False,use_anim=False,validate_meshes=False,use_custom_props=True)
 assert result=={'FINISHED'};objects=[];triangles=[];objectIds=[]
 for oid,o in enumerate(bpy.context.scene.objects):
  item={'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'matrixWorld':[[float(x) for x in r] for r in o.matrix_world],'matrixLocal':[[float(x) for x in r] for r in o.matrix_local],'modifiers':[{'name':m.name,'type':m.type} for m in o.modifiers]}
  if o.type=='MESH':
   mesh=o.data;mesh.calc_loop_triangles();mat=np.array(o.matrix_world,dtype=np.float64);verts=np.array([list(v.co) for v in mesh.vertices],dtype=np.float64);world=verts@mat[:3,:3].T+mat[:3,3];idx=np.array([t.vertices[:] for t in mesh.loop_triangles],dtype=np.int64);t=world[idx];triangles.append(t);objectIds += [oid]*len(t);item.update(vertices=len(verts),polygons=len(mesh.polygons),triangles=len(t),worldBounds=[world.min(axis=0).tolist(),world.max(axis=0).tolist()],meshDataName=mesh.name)
  objects.append(item)
 tri=np.concatenate(triangles);out=local/'blender-inspection'/mode/row['modelId'];out.mkdir(parents=True,exist_ok=True);np.savez_compressed(out/'full-world-triangles.npz',triangles=tri,objectIds=np.array(objectIds,dtype=np.int64));info={'source':row,'importMode':mode,'blenderVersion':bpy.app.version_string,'blenderBuildHash':bpy.app.build_hash.decode(),'blenderExecutable':bpy.app.binary_path,'fbxVersion':version,'rawGlobalSettings':props70(global_node),'rawSourceModels':original_models,'rawSourceGeometry':original_geometry,'rawConnections':encode([c.props for c in conn.elems]),'sceneUnitScale':bpy.context.scene.unit_settings.scale_length,'objects':objects,'fullWorldBounds':[tri.min(axis=(0,1)).tolist(),tri.max(axis=(0,1)).tolist()],'fullTriangleCount':len(tri),'fullWorldTrianglesSHA256':hashlib.sha256(tri.astype('<f8').tobytes()).hexdigest(),'geometryChanges':0,'sourceFileSHA256After':hashlib.sha256(p.read_bytes()).hexdigest(),'qualification':'Factory-startup read-only import, original polygon loop triangulation for inspection only, all objects retained. No evaluated modifier geometry, mesh edits, pose edits, manual axes or scale overrides; independent FBX coordinate/frame proof still required.'};(out/'inspection.json').write_text(json.dumps(info,indent=2));print(json.dumps({'modelId':row['modelId'],'mode':mode,'units':info['rawGlobalSettings'],'bounds':info['fullWorldBounds'],'triangles':len(tri),'objects':[(o['name'],o['type']) for o in objects]}),flush=True)
