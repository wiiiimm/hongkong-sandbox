import sys,json,pathlib,sqlite3,zipfile,numpy as np
from shapely.geometry import Polygon,MultiPoint
from shapely.ops import unary_union
H=pathlib.Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(R/'docs/astra-city/mui-wo-buildings/review'));from prepare_model_sample import model_geometry
c=sqlite3.connect('file:'+str(R/'source-scripts/city/building-batch/local/buildings.sqlite')+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
report=json.loads((H/'report.json').read_text());held={r['uid']:dict(c.execute('select * from buildings where uid=?',(r['uid'],)).fetchone()) for r in report['held']};out=[]
with zipfile.ZipFile(R/report['sourceCache']) as z:
 for n in z.namelist():
  if not n.endswith('.gltf') or not n.startswith(('BUILDING/','INFRASTRUCTURE/')):continue
  folder=pathlib.PurePosixPath(n).parent;g=json.loads(z.read(n));v,tri=model_geometry(g,lambda u:z.read(str(folder/u)));hull=MultiPoint(v[:,[0,2]]).convex_hull
  relevant=[]
  for uid,b in held.items():
   rings=json.loads(b['rings_json']);p=Polygon(rings[0],rings[1:])
   if hull.intersects(p):relevant.append((uid,p))
  if not relevant:continue
  orders=[];offset=0
  for node in g['nodes']:
   if 'mesh' not in node:continue
   for primitive in g['meshes'][node['mesh']]['primitives']:
    count=g['accessors'][primitive['attributes']['POSITION']]['count']
    if 'indices' in primitive:
     ac=g['accessors'][primitive['indices']];view=g['bufferViews'][ac['bufferView']];raw=z.read(str(folder/g['buffers'][view['buffer']]['uri']));ind=np.frombuffer(raw,dtype={5121:'<u1',5123:'<u2',5125:'<u4'}[ac['componentType']],count=ac['count'],offset=view.get('byteOffset',0)+ac.get('byteOffset',0))
    else:ind=np.arange(count)
    orders.append(ind+offset);offset+=count
  assert offset==len(v)
  tris=v[np.concatenate(orders)].reshape(-1,3,3);faces=[Polygon(t[:,[0,2]]) for t in tris if abs(np.cross(t[1]-t[0],t[2]-t[0])[1])>.01 and t[:,1].min()>2.5]
  projected=unary_union(faces)
  for uid,p in relevant:out.append({'uid':uid,'sourceEntry':n,'projectedRoofCoverage':projected.intersection(p).area/p.area,'sourceBounds':[v.min(axis=0).tolist(),v.max(axis=0).tolist()],'qualification':'Projected roof coverage is geometric evidence only, not proof of source identity or permission to suppress this building part.'})
(H/'canopy-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
