"""Show every current University Hall wall-clearance failure; source geometry unchanged."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection,Line3DCollection
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-next-repairs-university-hall-93417-wall-source-views-v3-20261024';out=base/batch;assert not out.exists();refs=[Path(__file__)];pins={}
    runtime='government-xl-next-repairs-university-hall-93417-runtime-v1-20261023';context='government-xl-next-repairs-university-hall-93417-current-prephysical-v1-20261024-continuous'
    def take(n,p):
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    g=next(r for r in take(runtime,HERE/'local'/runtime/'runtime-geometry.json.gz')['rows']if r['uid']=='landsd/93417:0');ctx=take(context,base/context/'93417:0.json.gz');assert g['sourceSHA256']==ctx['sourceSHA256']
    tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3)
    assert digest(tri.tobytes())==ctx['sourceBinding']['decodedWorldTrianglesSHA256'] and digest(ground.tobytes())==ctx['sourceBinding']['drawnGroundSHA256']
    ids=ctx['continuousAffectedFaces'];assert ids==ctx['affectedWallFaces'] and len(ids)==14
    clipping=module('wall_display_clip',HERE/'sung_fung_original_podium_low_surface_views_v1_20261024.py').clipped;refs.append(HERE/'sung_fung_original_podium_low_surface_views_v1_20261024.py')
    centres=tri.mean(1);remaining=set(ids);groups=[]
    while remaining:
        group={min(remaining)};remaining-=group
        while True:
            more={j for j in remaining if any(np.linalg.norm(centres[j]-centres[i])<2 for i in group)}
            if not more:break
            group|=more;remaining-=more
        groups.append(sorted(group))
    out.mkdir();records=[]
    for n,group in enumerate(groups):
        bad=tri[group];lo=bad.min((0,1))-[2,1,2];hi=bad.max((0,1))+[2,3,2];size=(hi-lo)[[0,2,1]]
        fig=plt.figure(figsize=(14,6))
        for k,angle in enumerate([35,215]):
            ax=fig.add_subplot(1,2,k+1,projection='3d')
            for mesh,color,alpha in [(ground,'none',1),(tri,'#64748b',.16),(bad,'#b91c1c',1)]:
                polys=clipping(mesh,lo,hi)
                if polys:
                    if color=='none':ax.add_collection3d(Line3DCollection([np.vstack([poly,poly[:1]])for poly in polys],colors='#29854a',linewidths=.6))
                    else:ax.add_collection3d(Poly3DCollection(polys,facecolors=color,edgecolors=color,alpha=alpha,linewidth=.25))
            ax.set_xlim(0,size[0]);ax.set_ylim(0,size[1]);ax.set_zlim(0,size[2]);ax.set_box_aspect(size.copy());ax.view_init(24,angle);ax.set_xlabel('X offset m');ax.set_ylabel('Z offset m');ax.set_zlabel('Y offset m')
        fig.suptitle('University Hall original walls '+str(group)+' red; unchanged source grey; actual current ground green wire\nDisplay clipping only, no source changes, no automatic physical acceptance.');fig.tight_layout();path=out/f'region-{n+1}.png';fig.savefig(path,dpi=130);plt.close(fig)
        records.append(dict(sourceFaces=group,bounds=[lo.tolist(),hi.tolist()],image=str(path.relative_to(ROOT)),imageSHA256=digest(path.read_bytes())))
    assert sorted(i for r in records for i in r['sourceFaces'])==ids
    result=dict(uids=[g['uid']],sourceSHA256=g['sourceSHA256'],completeSourceWorldSHA256=digest(tri.tobytes()),completeGroundSHA256=digest(ground.tobytes()),regions=records,allFourteenAffectedFacesShown=True,sourceGeometryChanges=0,sourcePoseChanges=0,sourceRoleAccepted=False,physicalAcceptance=False,installationApproved=False,publication=False)
    save(out/'summary.json',result);module('university_wall_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'complete-current-wall-clearance-source-and-ground-context-exports',refs,result)
    print(dict(regions=len(records),affectedFaces=len(ids)),flush=True)

if __name__=='__main__':main()
