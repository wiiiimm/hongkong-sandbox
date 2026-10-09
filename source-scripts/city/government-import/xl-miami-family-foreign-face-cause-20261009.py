"""Account for every original Miami family face touching the distinct foreign podium.

Read-only exact source projection diagnostic. No ownership, geometry, or gate edits.
"""
import importlib.util, numpy as np, shapely
from shapely.geometry import Polygon, mapping
from run import ROOT,HERE,read,save,digest
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
BATCH='government-xl-miami-op-complete-family-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
assert not (DOC/'result.json').exists(),'Completed checkpoint immutable'
selection=read(DOC/'selection.json.gz')
spec=importlib.util.spec_from_file_location('miami_overlap_decode',HERE/'xl-second-pass.py')
decoder=importlib.util.module_from_spec(spec);spec.loader.exec_module(decoder);decoder.LOCAL=HERE/'local'/BATCH
poly=lambda b:Polygon(b['rings'][0],b['rings'][1:])
target=shapely.union_all([poly(r['source']['building']) for r in selection['rows']])
foreign=read(DOC.parent/'government-xl-miami-op-complete-pair-20261009/current-foreign-overlap-form.json')
foreignpoly=poly(foreign);face_records=[];parts=[];alltri=[]
for r in selection['rows']:
 r['triangles']=r['native']['model']['triangles'];tri=decoder.glb_triangles(r);alltri.append(tri)
 projected=shapely.polygons(tri[:,:,[0,2]])
 ids=np.flatnonzero(shapely.intersects(projected,foreignpoly))
 areas=[]
 for fi in ids:
  overlap=projected[fi].difference(target).intersection(foreignpoly)
  if overlap.area<=0:continue
  normal=np.cross(tri[fi,1]-tri[fi,0],tri[fi,2]-tri[fi,0]);norm=np.linalg.norm(normal)
  face_records.append({'uid':r['uid'],'sourceSHA256':r['sourceSHA256'],'modelId':r['modelId'],'faceId':int(fi),'verticesXYZ':tri[fi].tolist(),'unitNormalXYZ':(normal/norm).tolist() if norm else [0,0,0],'overlapAreaM2':overlap.area,'overlap':mapping(overlap),'heightHKPD':[float(tri[fi,:,1].min()),float(tri[fi,:,1].max())]})
  parts.append(overlap);areas.append(overlap)
 if areas:print({'uid':r['uid'],'faces':len(areas),'projectedForeignUnionM2':shapely.union_all(areas).area},flush=True)
union=shapely.union_all(parts);tri=np.concatenate(alltri)
out={'foreignForm':foreign,'foreignFormSHA256':digest((DOC.parent/'government-xl-miami-op-complete-pair-20261009/current-foreign-overlap-form.json').read_bytes()),'completeOriginalTriangles':len(tri),'allOffendingOriginalFaces':face_records,'foreignExcessUnionM2':union.area,'foreignExcessUnion':mapping(union),'identityAccepted':False,'physicalAccepted':False,'geometryChanges':0,'qualification':'Distinct NT161/91 foreign podium retained. Exact projected overlap is evidence of interface only, never shared ownership or physical acceptance.'}
save(DOC/'foreign-podium-every-original-overlap-face.json.gz',out)
fig,ax=plt.subplots(figsize=(10,8))
for r in selection['rows']:
 for ring in r['source']['building']['rings']:x,z=np.array(ring).T;ax.plot(x,z,color='#298a8c',linewidth=.8)
for ring in foreign['rings']:x,z=np.array(ring).T;ax.plot(x,z,color='black',linewidth=1)
for p in ([union] if union.geom_type=='Polygon' else union.geoms):
 if p.geom_type=='Polygon':x,z=p.exterior.xy;ax.fill(x,z,color='#e43d30',alpha=.8)
b=union.bounds;ax.set_xlim(b[0]-20,b[2]+20);ax.set_ylim(b[1]-20,b[3]+20);ax.invert_yaxis();ax.set_aspect('equal');ax.set_title('Original Miami family · exact foreign podium overlap, all current forms retained');fig.tight_layout();fig.savefig(DOC/'foreign-podium-exact-overlap.png',dpi=200);plt.close(fig)
print({'allOffendingOriginalFaces':len(face_records),'foreignExcessUnionM2':union.area,'heightHKPD': [min(f['heightHKPD'][0] for f in face_records),max(f['heightHKPD'][1] for f in face_records)]},flush=True)
