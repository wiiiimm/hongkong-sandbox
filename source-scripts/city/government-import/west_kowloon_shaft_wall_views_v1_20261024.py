"""Inspect representative exact current wall/grade relationships and all source context."""
import argparse
from pathlib import Path
from fractions import Fraction
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection,Line3DCollection
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--shaft',choices=['261098','267327'],required=True);a=parser.parse_args()
    base=ROOT/'docs/astra-city/government-import';prefix='government-xl-next-repairs-west-kowloon-bus-';batch=prefix+'shaft'+a.shaft+'-wall-views-v1-20261024';out=base/batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(n,p):
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    runtime=prefix+'five-original-runtime-v1-20261024';g=next(r for r in take(runtime,HERE/'local'/runtime/'runtime-geometry.json.gz')['rows']if r['uid']=='landsd/'+a.shaft+':0');tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3)
    low_name=prefix+'shaft'+a.shaft+'-low-faces-v1-20261024';low=take(low_name,base/low_name/'literal.json.gz');assert low['sourceWorldSHA256']==digest(tri.tobytes()) and low['groundSHA256']==digest(ground.tobytes())
    cap_name=prefix+'shaft'+a.shaft+'-cap-paths-v1-20261024';caps=next(r for r in take(cap_name,base/cap_name/'summary.json')['rows']if r['mode']=='literal');assert caps['sourceWorldSHA256']==digest(tri.tobytes()) and caps['completeDrawnGroundSHA256']==digest(ground.tobytes());paths={r['sourceFace']:r['originalPath']for r in caps['completeGroundClearancePartition']['paths']};assert caps['completeGroundClearancePartition']['allAffectedHavePaths']
    targets=[r['sourceFace']for r in low['rows']];assert targets
    clipping=module('west_wall_display_clip',HERE/'sung_fung_original_podium_low_surface_views_v1_20261024.py').clipped;refs.append(HERE/'sung_fung_original_podium_low_surface_views_v1_20261024.py');out.mkdir();views=[]
    for face in [targets[0]]:
        path=sorted({i for f in targets for i in paths[f]});selected=tri[path];lo=selected.min((0,1))-[2,1,2];hi=selected.max((0,1))+[2,2,2];size=(hi-lo)[[0,2,1]]
        fig=plt.figure(figsize=(14,6))
        for k,angle in enumerate([35,215]):
            ax=fig.add_subplot(1,2,k+1,projection='3d')
            for values,color,alpha in [(ground,'wire',1),(tri,'#64748b',.12),(selected,'#dd9b29',.6),(tri[targets],'#bc2430',1)]:
                polys=clipping(values,lo,hi)
                if not polys:continue
                if color=='wire':ax.add_collection3d(Line3DCollection([np.asarray([poly[j],poly[(j+1)%len(poly)]])for poly in polys for j in range(len(poly))],colors='#2a864b',linewidths=.5))
                else:ax.add_collection3d(Poly3DCollection(polys,facecolors=color,edgecolors=color,alpha=alpha,linewidth=.2))
            ax.set_xlim(0,size[0]);ax.set_ylim(0,size[1]);ax.set_zlim(0,size[2]);ax.set_box_aspect(size.copy());ax.view_init(24,angle);ax.set(xlabel='X offset m',ylabel='Z offset m',zlabel='Y offset m')
        fig.suptitle(f'West Kowloon shaft {a.shaft}: all affected walls red; exact original clear-cap path orange; unchanged source grey; actual ground green wire\nSource assets unchanged. Display clipping only; no role/placement approval from colour or topology.');fig.tight_layout();p=out/f'wall-{face}.png';fig.savefig(p,dpi=130);plt.close(fig);views.append(dict(sourceFace=face,originalPath=path,completeAffectedFaceIds=targets,image=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
    result=dict(uids=[g['uid']],sourceSHA256=g['sourceSHA256'],completeSourceWorldSHA256=digest(tri.tobytes()),completeDrawnGroundSHA256=digest(ground.tobytes()),completeAffectedWallFaces=[r['sourceFace']for r in low['rows']],views=views,allAffectedShownInCloseup=True,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Both angles show all affected lower shaft faces in red and their authenticated original cap paths in orange. Complete actual ground shown as green wire; source untouched. Numeric complete four-world finite proofs remain independent; no physical acceptance from image colours.')
    save(out/'summary.json',result);module('west_shaft_wall_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'source-bound-worst-and-exposure-failing-wall-current-ground-context-exports',refs,result);print(dict(closeups=len(views),allAffectedWalls=len(low['rows'])),flush=True)

if __name__=='__main__':main()
