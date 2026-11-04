"""Unedited original Aquarium/Ocean Square geometry and exact contact diagnostic views."""
from pathlib import Path
from fractions import Fraction as F
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection,Line3DCollection
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-grand-aquarium-joint-geometry-context-v1-20261022'
def main():
 doc=BASE/BATCH;assert not doc.exists();refs=[Path(__file__)]
 def take(batch,name,local=False):
  folder=BASE/batch;_,pins=authenticate(folder);p=(HERE/'local'/batch if local else folder)/name;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.extend([folder/'result.json',p]);return read(p)
 sourceRow=take('government-xl-grand-aquarium-crack-repaired-runtime-v1-20261022','selection.json.gz')['rows'][0];otherRow=take('government-xl-grand-aquarium-foreign-scope-plan-v1-20261022','selection.json.gz')['rows'][0];models=[]
 for r in [sourceRow,otherRow]:
  p=ROOT/r['candidate']['path'];assert digest(p.read_bytes())==r['sourceSHA256'];refs.append(p);models.append(decode_original_world_triangles(p.read_bytes()))
 g=take('government-xl-grand-aquarium-crack-repaired-runtime-v1-20261022','runtime-geometry.json.gz',True)['rows'][0];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);intersections=take('government-xl-grand-aquarium-full-foreign-intersections-v1-20261022','original-original-295518:0.json.gz')['exactIntersections'];segments=[np.asarray([[float(F(v))for v in p]for p in h['exactIntersectionPoints']])for h in intersections];allpoints=np.concatenate(segments);lo=allpoints.min(0)-[5,2,5];hi=allpoints.max(0)+[5,8,5];source,other=models;fig=plt.figure(figsize=(18,7),dpi=140)
 for k,(azim,terrain)in enumerate([(140,False),(220,False),(140,True)]):
  ax=fig.add_subplot(1,3,k+1,projection='3d')
  for tri,color,alpha in [(other,'#c4a77d',.82),(source,'#6f95b5',.85)]+([(ground,'#899d7a',.75)]if terrain else[]):
   ids=(tri[:,:,0].max(1)>=lo[0])&(tri[:,:,0].min(1)<=hi[0])&(tri[:,:,2].max(1)>=lo[2])&(tri[:,:,2].min(1)<=hi[2]);ax.add_collection3d(Poly3DCollection(tri[ids][:,:,[0,2,1]],facecolors=color,edgecolors='#344054',linewidths=.08,alpha=alpha))
  ax.add_collection3d(Line3DCollection([s[:,[0,2,1]]for s in segments],colors='#e53935',linewidths=.5));ax.set(xlim=(lo[0],hi[0]),ylim=(lo[2],hi[2]),zlim=(lo[1],hi[1]),xlabel='Local X / m',ylabel='Local Z / m',zlabel='HKPD / m');ax.view_init(elev=25,azim=azim);ax.set_box_aspect((hi-lo)[[0,2,1]]);ax.set_title('With actual terrain'if terrain else'Original surfaces; exact joins red');ax.tick_params(labelsize=6)
 fig.suptitle('Grand Aquarium blue; installed Ocean Square tan — unchanged source coordinates, diagnostic only');fig.tight_layout();doc.mkdir(parents=True);image=doc/'original-joint.png';fig.savefig(image);plt.close(fig);save(doc/'provenance.json',dict(sourceSHA256=sourceRow['sourceSHA256'],foreignSHA256=otherRow['sourceSHA256'],exactIntersections=len(intersections),intersectionBounds=[allpoints.min(0).tolist(),allpoints.max(0).tolist()],geometryEdited=False,colorsDiagnosticOnly=True,installationApproved=False));refs.append(HERE/'exact_packed_world_geometry_20261009.py');module('aquarium_joint_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unedited-original-adjoining-geometry-diagnostic-views',refs,dict(uids=['landsd/93424:0'],sourceGeometryChanges=0,installationApproved=False,newlyInstalled=0))
if __name__=='__main__':main()
