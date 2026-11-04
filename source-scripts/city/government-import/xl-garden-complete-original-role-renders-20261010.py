"""Complete original source-role renders; visible source context, no source edits."""
import numpy as np
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
DOC=ROOT/'docs/astra-city/government-import/government-xl-garden-complete-original-role-renders-20261010';BASE=DOC.parent

def render(own,foreign,ids,forms,path):
 fig=plt.figure(figsize=(16,10),dpi=150);ax=fig.add_subplot(121);ax.add_collection(PolyCollection(own[:,:,[0,2]],facecolors='#506d9e30',edgecolors='none'));ax.add_collection(PolyCollection(foreign[:,:,[0,2]],facecolors='#2196ba55',edgecolors='none'));ax.add_collection(PolyCollection(own[ids][:,:,[0,2]],facecolors='#f02f3599',edgecolors='#e22222',linewidths=.4))
 for b,color in forms:
  for ring in b['rings']:
   v=np.asarray(ring);ax.plot(v[:,0],v[:,1],color=color,linewidth=.9)
 ax.autoscale();ax.set_aspect('equal');ax.invert_yaxis();ax.set_xlabel('Viewer east metres');ax.set_ylabel('Viewer south metres');ax.set_title('Complete source projection; exact role faces red')
 az=fig.add_subplot(122,projection='3d')
 for a,col in [(own,'#506d9e28'),(foreign,'#2196ba70'),(own[ids],'#f02f35cc')]:az.add_collection3d(Poly3DCollection(a[:,:,[0,2,1]],facecolors=col,edgecolors='none'))
 a=np.concatenate([own,foreign]).reshape(-1,3);az.set_xlim(a[:,0].min(),a[:,0].max());az.set_ylim(a[:,2].min(),a[:,2].max());az.set_zlim(a[:,1].min(),a[:,1].max());az.set_box_aspect(np.ptp(a[:,[0,2,1]],axis=0));az.view_init(elev=23,azim=135);az.set_xlabel('East m');az.set_ylabel('South m');az.set_zlabel('HKPD m');az.set_title('All original faces; independent foreign source cyan')
 fig.tight_layout();fig.savefig(path);plt.close(fig)

def main():
 assert not DOC.exists();DOC.mkdir(parents=True);t=read(BASE/'government-xl-garden-common-op-original-terrace-context-20261010/diagnostic.json.gz');s=read(BASE/'xl-terrain-recovery-20261010-garden-two-foreign-current-inputs-v1/check-selection.json.gz');p=read(BASE/'xl-terrain-recovery-20261010-garden-terrace-podium-current-inputs-v1/check-selection.json.gz');o=read(BASE/'government-xl-source-neighbour-recovery-leads-20261010/selection.json.gz');rows={r['uid']:r for r in s['rows']+p['rows']+o['rows']};arrays={};inputs=[Path(__file__)]
 for u in ['landsd/109491:0','landsd/162285:0','landsd/304714:0','landsd/213929:0']:
  r=rows[u];path=ROOT/r['candidate']['path'];raw=path.read_bytes();assert digest(raw)==r['sourceSHA256'];arrays[u]=decode_original_world_triangles(raw);inputs.append(path)
 render(arrays['landsd/109491:0'],arrays['landsd/162285:0'],t['completeTerraceFaceIds'],[(rows['landsd/109491:0']['source']['building'],'black'),(t['completeCurrentPodiumForm'],'green')],DOC/'tower-terrace-and-distinct-podium-2400x1500.png')
 render(arrays['landsd/304714:0'],arrays['landsd/213929:0'],[642,643,644],[(rows['landsd/304714:0']['source']['building'],'black'),(rows['landsd/213929:0']['source']['building'],'green')],DOC/'no1-roof-edges-and-whole-hollywood-source-2400x1500.png')
 save(DOC/'render-provenance.json',{'inputHashes':{str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in inputs},'sourceFaces':[10726,1418,821,546],'size':[2400,1500],'worldCoordinateConvention':['east','south','HKPD'],'sourceGeometryChanges':0,'physicalAccepted':False,'qualification':'Complete independently acquired original source geometry, no source simplification/edit, no appearance-only installation or physical claim.'})
 print(DOC,flush=True)
if __name__=='__main__':main()
