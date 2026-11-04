"""Plot exact named original faces and current ground in two opposite views.
Read-only diagnostic; display cropping never changes production geometry.
"""
import argparse
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from original_assembly_context_plot_v3_20261023 import clipped_faces


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','runtime','uid']:p.add_argument('--'+key,required=True)
    p.add_argument('--faces',type=int,nargs='+',required=True);a=p.parse_args()
    assert a.batch.startswith('government-xl-')and'/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists()
    receipt,pins=authenticate(base/a.runtime);path=HERE/'local'/a.runtime/'runtime-geometry.json.gz'
    assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))]
    g=next(r for r in read(path)['rows']if r['uid']==a.uid)
    t=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3)
    ids=sorted(set(a.faces));assert len(ids)==len(a.faces)and ids[0]>=0 and ids[-1]<len(t)
    lo,hi=t[ids].min((0,1)),t[ids].max((0,1));center=(lo+hi)/2
    lo-=np.array([2,1,2]);hi+=np.array([2,1,2]);planes=[(i,v,side)for i in range(3)for v,side in [(lo[i],True),(hi[i],False)]]
    def shown(tri):
        broad=tri[np.all(tri.max(1)>=lo,axis=1)&np.all(tri.min(1)<=hi,axis=1)]
        v=clipped_faces(broad,planes);v[:,:,[0,2]]-=center[[0,2]];return v[:,:,[0,2,1]]
    fig=plt.figure(figsize=(14,7),layout='constrained')
    for i,angle in enumerate([35,215]):
        ax=fig.add_subplot(1,2,i+1,projection='3d')
        for tri,color,alpha in [(ground,'#9d9685',.6),(t,'#9ab6c6',.2),(t[ids],'#db472e',1)]:
            ax.add_collection3d(Poly3DCollection(shown(tri),facecolor=color,edgecolor='none',alpha=alpha))
        ax.set(xlim=(lo[0]-center[0],hi[0]-center[0]),ylim=(lo[2]-center[2],hi[2]-center[2]),zlim=(lo[1],hi[1]),xlabel='Local east (m)',ylabel='Local viewer Z (m)',zlabel='HKPD height (m)')
        ax.set_box_aspect((hi-lo)[[0,2,1]]);ax.view_init(elev=20,azim=angle)
    fig.suptitle('Named original faces red; current ground grey; other source context translucent. Display crop only.')
    out.mkdir();image=out/'named-faces-current-ground.png';fig.savefig(image,dpi=150);plt.close(fig)
    summary=dict(uids=[a.uid],sourceSHA256=g['sourceSHA256'],sourceFaces=ids,sourceWorldSHA256=digest(t.tobytes()),drawnGroundSHA256=digest(ground.tobytes()),image=dict(path=str(image.relative_to(ROOT)),sha256=digest(image.read_bytes())),sourceGeometryChanges=0,architecturalRoleAccepted=False,installationApproved=False)
    save(out/'summary.json',summary)
    module('named_face_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'named-complete-original-faces-current-grade-two-angle-diagnostic', [Path(__file__),base/a.runtime/'result.json',path,HERE/'original_assembly_context_plot_v3_20261023.py'],summary)


if __name__=='__main__':main()
