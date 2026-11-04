"""Source-bound views of residual Tower 3A facets; no mesh or acceptance changes."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from tko_buried_source_view_v2_20261021 import clipped_faces
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tko-tower3a-attachment-view-v1-20261021';DOC=BASE/BATCH
FOUND=BASE/'government-xl-tko-complete-foundations-v2-20261021';JOIN=BASE/'government-xl-tko-residual-component-joins-v1-20261021'
def main():
 assert not DOC.exists();refs=[Path(__file__),HERE/'tko_buried_source_view_v2_20261021.py',HERE/'china_ferry_current_foundations_v1_20261020.py'];used={}
 def take(d,p):
  _,pins=authenticate(d);k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[k];used[k]=pins[k];refs.extend([d/'result.json',p]);return read(p)
 inp=take(FOUND,FOUND/'original/32024:0/input.json.gz');r=inp['rows'][0];t=np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)]
 joins=take(JOIN,JOIN/'original/32024:0-joins.json.gz');assert digest(t.tobytes())==joins['sourceWorldSHA256'];ids=sorted({f for c in joins['components']for f in c['componentFaces']});red=t[ids];origin=red.mean((0,1));origin[1]=0;DOC.mkdir()
 for name,ylo,yhi in [('lower',24,32),('upper',159,166),('full',23,166)]:
  lo=red.min((0,1))-[3,0,3];hi=red.max((0,1))+[3,0,3];lo[1]=ylo;hi[1]=yhi
  fig=plt.figure(figsize=(14,10),dpi=140)
  for i,az in enumerate([-55,35,125,215]):
   ax=fig.add_subplot(2,2,i+1,projection='3d')
   for tr,col,alpha in [(t,'#4088aa',.23),(red,'#db4828',.9)]:
    faces=(clipped_faces(tr,lo,hi)-origin)[:,:,[0,2,1]];ax.add_collection3d(Poly3DCollection(faces,facecolor=col,edgecolor=col,alpha=alpha,linewidth=.2))
   ax.set_xlim(lo[0]-origin[0],hi[0]-origin[0]);ax.set_ylim(lo[2]-origin[2],hi[2]-origin[2]);ax.set_zlim(ylo,yhi);ax.set_box_aspect([hi[0]-lo[0],hi[2]-lo[2],min(yhi-ylo,20)]);ax.view_init(elev=20,azim=az);ax.set_xlabel('Local x');ax.set_ylabel('Local z');ax.set_zlabel('HKPD height')
  fig.suptitle('Tower 3A: two original residual components (red), original tower (blue)\nDiagnostic transparency and cropping only; full-height view has compressed vertical aspect');fig.tight_layout();fig.savefig(DOC/(name+'.png'));plt.close(fig)
 for p,h in used.items():assert digest((ROOT/p).read_bytes())==h
 save(DOC/'context.json',dict(uids=['landsd/32024:0'],sourceWorldSHA256=digest(t.tobytes()),faceIds=ids,sourceGeometryChanges=0,installationApproved=False))
 module('tko_attachment_view_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-residual-component-context-views',list(dict.fromkeys(refs)),dict(uids=['landsd/32024:0'],installationApproved=False))
if __name__=='__main__':main()
