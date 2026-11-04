"""Diagnostic views of unchanged source faces around residual contact witnesses."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-sol-city-tower5-facade-view-v1-20261021';DOC=BASE/BATCH;ROUTE=BASE/'government-xl-sol-city-tower5-route-heights-v1-20261021';OLD=BASE/'government-xl-sol-city-complete-capture-v1-20261021'
assert not DOC.exists();refs=[Path(__file__)];pins={}
with connect()as db:
 db.execute('SET TRANSACTION READ ONLY')
 for d in [ROUTE,OLD]:
  r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json');pins[d]={e['path']:e['sha256']for e in r['evidenceRefs']}
def take(d,p):
 assert digest(p.read_bytes())==pins[d][str(p.relative_to(ROOT))];refs.append(p);return read(p)
route=take(ROUTE,ROUTE/'268424:0.json.gz');sources={r['uid']:r for r in take(OLD,OLD/'selection.json.gz')['rows']};arrays=[]
for uid in ['landsd/268424:0','landsd/273271:0']:
 r=sources[uid];p=ROOT/r['candidate']['path'];assert digest(p.read_bytes())==r['candidate']['entry']['sha256'];refs.append(p);arrays.append(decode_original_world_triangles(p.read_bytes()))
t,p=arrays;points=np.asarray([r['witness']['position']for r in route['rows']]);origin=np.mean(points,axis=0);origin[1]=0
def clipped_faces(tri,lower,upper):
 out=[]
 for face in tri:
  polygon=[v.copy() for v in face]
  for axis in range(3):
   for boundary,sign in [(lower[axis],1),(upper[axis],-1)]:
    if not polygon:break
    result=[]
    for a,b in zip(polygon,polygon[1:]+polygon[:1]):
     va=sign*(a[axis]-boundary);vb=sign*(b[axis]-boundary)
     if va>=0:result.append(a)
     if (va>=0)!=(vb>=0):result.append(a+(b-a)*(va/(va-vb)))
    polygon=result
  for j in range(1,len(polygon)-1):out.append([polygon[0],polygon[j],polygon[j+1]])
 return np.asarray(out).reshape(-1,3,3)
fig=plt.figure(figsize=(16,12),dpi=160)
for i,az in enumerate([-55,35,125,215]):
 ax=fig.add_subplot(2,2,i+1,projection='3d')
 for tri,color,label in [(p,'#d8a04e','Original podium'),(t,'#3576a5','Original tower')]:
  low,high=tri.min(1),tri.max(1);lo=points.min(0)-[3,6,3];hi=points.max(0)+[3,12,3];mask=np.all(high>=lo,axis=1)&np.all(low<=hi,axis=1);faces=(clipped_faces(tri[mask],np.array([points[:,0].min()-1,float(points[:,1].min()-1),points[:,2].min()-1]),np.array([points[:,0].max()+1,float(points[:,1].max()+5),points[:,2].max()+1]))-origin)[:,:,[0,2,1]];ax.add_collection3d(Poly3DCollection(faces,facecolor=color,edgecolor=color,linewidth=.2,alpha=(.08 if label=='Original podium' else .35),label=label))
 ids=sorted({f for r in route['rows']for f in r['incidentFaces']});ax.add_collection3d(Poly3DCollection((t[ids]-origin)[:,:,[0,2,1]],facecolor='#d62728',edgecolor='#670000',linewidth=.4,alpha=1))
 q=(points-origin)[:,[0,2,1]];ax.scatter(*q.T,c='red',s=12);ax.set_xlim(points[:,0].min()-origin[0]-1,points[:,0].max()-origin[0]+1);ax.set_ylim(points[:,2].min()-origin[2]-1,points[:,2].max()-origin[2]+1);ax.set_zlim(float(points[:,1].min()-1),float(points[:,1].max()+5));ax.view_init(elev=18,azim=az);ax.set_xlabel('Local x (m)');ax.set_ylabel('Local z (m)');ax.set_zlabel('HKPD height (m)');ax.set_title('Original source geometry — local low-rim view');ax.set_box_aspect([1,2,2])
fig.suptitle('Sol City Tower 5: red = 17 unresolved witnesses; blue = tower; amber = podium\nDiagnostic facade crop (visual-only plane clipping), transparency for inspection only; source geometry unchanged')
DOC.mkdir();fig.tight_layout();fig.savefig(DOC/'original-rim-context.png');plt.close(fig)
save(DOC/'context.json',dict(uids=['landsd/268424:0','landsd/273271:0'],witnessCount=len(points),incidentFaceIds=ids,incidentFaces=t[ids].tolist(),witnesses=route['rows'],sourceGeometryChanges=0,installationApproved=False,qualification='Local cropped translucent diagnostic, not full-source clearance or publication evidence.'))
refs.append(HERE/'exact_packed_world_geometry_20261009.py');module('sol_view_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-rim-source-context-views',refs,dict(uids=['landsd/268424:0','landsd/273271:0'],installationApproved=False))
