"""Causal missing-area and exact third-form OP research, no identity credit."""
import sys,json,importlib.util,numpy as np,shapely
from shapely.geometry import Polygon,mapping
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from run import ROOT,HERE,read,save,digest
sys.path.insert(0,str(HERE.parent/'landsd-territory'));from source import request,BASE
BATCH='government-xl-miami-op-complete-pair-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH
s=importlib.util.spec_from_file_location('miami_pair_decode',HERE/'xl-second-pass.py');d=importlib.util.module_from_spec(s);s.loader.exec_module(d);d.LOCAL=LOCAL
selection=read(DOC/'selection.json.gz');rows=selection['rows'];tri=[]
for r in rows:r['triangles']=r['native']['model']['triangles'];tri.append(d.glb_triangles(r))
tri=np.concatenate(tri);fp=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));target=shapely.union_all([Polygon(r['source']['building']['rings'][0],r['source']['building']['rings'][1:]) for r in rows]);missing=target.difference(fp)
holes=[Polygon(ring) for p in ([fp] if fp.geom_type=='Polygon' else fp.geoms) if p.geom_type=='Polygon' for ring in p.interiors];inside=shapely.union_all(holes);interior=missing.intersection(inside);outside=missing.difference(inside)
fig,ax=plt.subplots(figsize=(12,8))
def draw(g,color,alpha):
 for p in ([g] if g.geom_type=='Polygon' else getattr(g,'geoms',[])):
  if p.geom_type!='Polygon':continue
  x,z=p.exterior.xy;ax.fill(x,z,color=color,alpha=alpha)
  for ring in p.interiors:x,z=ring.xy;ax.fill(x,z,color='white')
draw(fp,'#2a9d8f',.45);draw(interior,'#f4a261',.8);draw(outside,'#e63946',.8)
for r in rows:
 for ring in r['source']['building']['rings']:x,z=np.array(ring).T;ax.plot(x,z,color='black',linewidth=.7)
ax.set_aspect('equal');ax.invert_yaxis();ax.set_title('Every original Miami podium + Club II face · amber inner voids, red external missing area');fig.tight_layout();fig.savefig(DOC/'complete-original-missing-roles.png',dpi=180);plt.close(fig)
normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normals,axis=1);vertical=(length>0)&(abs(normals[:,1])<1e-6*length);proof=[]
for hole in sorted(holes,key=lambda p:-p.area):
 if hole.area<.01:continue
 faces=[];lines=[]
 for fi in np.flatnonzero(vertical):
  line=hole.exterior.intersection(shapely.convex_hull(shapely.multipoints(tri[fi,:,[0,2]].T)))
  if line.length>0:faces.append(int(fi));lines.append(line)
 proof.append({'areaM2':hole.area,'geometry':mapping(hole),'missingTargetWithinHoleM2':hole.intersection(missing).area,'innerOriginalVerticalFaceIds':faces,'innerWallPerimeterFraction':shapely.union_all(lines).length/hole.length,'qualification':'Exact original inward boundaries are geometrical evidence only; open sky/pool/source completeness needs primary role evidence.'})
out={'missingTargetAreaM2':missing.area,'sourceBoundedInteriorMissingM2':interior.area,'outerBoundaryMissingM2':outside.area,'sourceHoleCount':len(holes),'originalOpenings':proof,'identityAccepted':False,'installationApproved':False,'geometryChanges':0};save(DOC/'complete-original-missing-role-cause.json.gz',out);print({k:v for k,v in out.items() if k!='originalOpenings'},flush=True)
# Fresh exact stable source identity + relation for the overlap form, with geometry.
ids=['1484725876P20060311','1496725917P20061130']
foreign=[]
for tile in read(ROOT/'3d-viewer/city/data/manifest.json')['tiles']:
 for b in read(ROOT/'3d-viewer'/tile['url'])['buildings']:
  if b['uid']=='landsd/231147:0':foreign.append(b)
assert len(foreign)==1;ids.append(foreign[0]['buildingCSUID']);save(DOC/'current-foreign-overlap-form.json',foreign[0])
for csuid in ids:
 params={'f':'json','where':"BuildingCSUID='"+csuid+"'",'outFields':'*','returnGeometry':'false','resultRecordCount':'1000'}
 raw,rec=request(BASE+'/1002/query',params);(DOC/('current-op-relations-'+csuid+'.json')).write_bytes(raw);save(DOC/('current-op-relations-'+csuid+'.request.json'),rec)
print({'exactCurrentOPRelationCSUIDs':ids},flush=True)
