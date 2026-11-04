"""Inspect representative exact current wall/grade relationships and all source context."""
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
    base=ROOT/'docs/astra-city/government-import';prefix='government-xl-next-repairs-west-kowloon-bus-';batch=prefix+'wall-source-views-v1-20261024';out=base/batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(n,p):
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    runtime=prefix+'protected-return-runtime-v1-20261024';g=take(runtime,HERE/'local'/runtime/'runtime-geometry.json.gz')['rows'][0];tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3)
    low_name=prefix+'protected-return-low-faces-v1-20261024';low=take(low_name,base/low_name/'literal.json.gz');assert low['sourceWorldSHA256']==digest(tri.tobytes()) and low['groundSHA256']==digest(ground.tobytes())
    cap_name=prefix+'complete-ground-cap-paths-v2-20261024';caps=next(r for r in take(cap_name,base/cap_name/'summary.json')['rows']if r['mode']=='literal');assert caps['sourceWorldSHA256']==digest(tri.tobytes()) and caps['completeDrawnGroundSHA256']==digest(ground.tobytes());paths={r['sourceFace']:r['originalPath']for r in caps['completeGroundClearancePartition']['paths']};assert caps['completeGroundClearancePartition']['allAffectedHavePaths']
    cont_name=prefix+'protected-return-prephysical-v1-20261024-continuous';ctx=take(cont_name,base/cont_name/'255415:0.json.gz');assert ctx['sourceBinding']['decodedWorldTrianglesSHA256']==digest(tri.tobytes());hidden=[i for i in ctx['continuousAffectedFaces']if ctx['faces'][i].get('maximumObservedGapM',0)<=0]
    worst=min(low['rows'],key=lambda r:Fraction(r['minimumFiniteGapM']))['sourceFace'];partial=caps['initialSharedEdgeUnresolvedFaces'][0];targets=sorted(set([worst,partial,*hidden]));assert len(targets)<=6 and len(hidden)==4
    clipping=module('west_wall_display_clip',HERE/'sung_fung_original_podium_low_surface_views_v1_20261024.py').clipped;refs.append(HERE/'sung_fung_original_podium_low_surface_views_v1_20261024.py');out.mkdir();views=[]
    for face in targets:
        path=paths[face];selected=tri[path];lo=selected.min((0,1))-[2,1,2];hi=selected.max((0,1))+[2,2,2];size=(hi-lo)[[0,2,1]]
        fig=plt.figure(figsize=(14,6))
        for k,angle in enumerate([35,215]):
            ax=fig.add_subplot(1,2,k+1,projection='3d')
            for values,color,alpha in [(ground,'wire',1),(tri,'#64748b',.12),(selected,'#dd9b29',.6),(tri[[face]],'#bc2430',1)]:
                polys=clipping(values,lo,hi)
                if not polys:continue
                if color=='wire':ax.add_collection3d(Line3DCollection([np.vstack([poly,poly[:1]])for poly in polys],colors='#2a864b',linewidths=.5))
                else:ax.add_collection3d(Poly3DCollection(polys,facecolors=color,edgecolors=color,alpha=alpha,linewidth=.2))
            ax.set_xlim(0,size[0]);ax.set_ylim(0,size[1]);ax.set_zlim(0,size[2]);ax.set_box_aspect(size.copy());ax.view_init(24,angle);ax.set(xlabel='X offset m',ylabel='Z offset m',zlabel='Y offset m')
        fig.suptitle(f'West Kowloon wall {face} red; exact original clear-cap path orange; unchanged source grey; actual ground green wire\nSource assets unchanged. Display clipping only; no role/placement approval from colour or topology.');fig.tight_layout();p=out/f'wall-{face}.png';fig.savefig(p,dpi=130);plt.close(fig);views.append(dict(sourceFace=face,originalPath=path,rawExposureDiagnostic=ctx['faces'][face].get('maximumObservedGapM'),image=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
    result=dict(uids=[g['uid']],sourceSHA256=g['sourceSHA256'],completeSourceWorldSHA256=digest(tri.tobytes()),completeDrawnGroundSHA256=digest(ground.tobytes()),completeAffectedWallFaces=[r['sourceFace']for r in low['rows']],representativeWallFaces=targets,worstFiniteGapFace=worst,rawExposureFailingFaces=hidden,firstSharedEdgeUnresolvedFace=partial,views=views,allAffectedShownInCloseup=False,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Two angles for every raw exposure-failing wall, the worst finite-depth wall and a partial-contact case. Whole-source numeric proof covers all527walls; these close-ups are representative context, not a claim everywall was separately rendered. Full original source plots and browser exports remain independently inspectable.')
    save(out/'summary.json',result);module('west_wall_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'source-bound-worst-and-exposure-failing-wall-current-ground-context-exports',refs,result);print(dict(closeups=len(views),allAffectedWalls=len(low['rows'])),flush=True)

if __name__=='__main__':main()
