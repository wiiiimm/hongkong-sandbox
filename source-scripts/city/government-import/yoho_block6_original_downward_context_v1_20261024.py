"""Exact original downward-facade context; diagnostic only, no acceptance."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from source_closed_components import components
from primrose_compound_foundation_v2_20261015 import module

BASE=ROOT/'docs/astra-city/government-import'
P='government-xl-next-repairs-yoho-'
BATCH=P+'56771-downward-context-v1-20261024'
BAD={13247,13630,13631}

def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    runtime=P+'five-inset-runtime-v1-20261024';selection=take(runtime,BASE/runtime/'selection.json.gz')['rows']
    meshes={}
    for uid in ['landsd/56771:0','landsd/231756:0']:
        row=next(r for r in selection if r['uid']==uid);asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset);meshes[uid]=decode_original_world_triangles(asset.read_bytes())
    tri=meshes['landsd/56771:0'];podium=meshes['landsd/231756:0'];topology=components(tri)
    groups=[g for g in topology['components']if BAD.intersection(g['faceIndices'])];assert len(groups)==1
    group=groups[0];values=tri[group['faceIndices']];group=dict(group,bounds=[values.min((0,1)).tolist(),values.max((0,1)).tolist()])
    modes=[]
    for mode in ['original','literal','left','balanced']:
        batch=P+'56771-compound-clearance-v1-20261024';raw=take(batch,BASE/batch/(mode+'.json.gz'));cap=take(batch,BASE/batch/(mode+'-cap-paths.json.gz'))['proof']
        assert set(cap['negativeNonWallFaces'])==BAD and all(p['hasExactSharedEdgeClearCapPath']for p in cap['paths'])
        badrows=[r for r in raw['rows']if r['sourceFace']in BAD];assert len(badrows)==3
        for r in badrows:
            t=np.asarray(r['vertices']);n=np.cross(t[1]-t[0],t[2]-t[0]);assert n[1]/np.linalg.norm(n)==-1
        modes.append(dict(mode=mode,downwardFaces=badrows,allWallCapPathsVerified=True,wallCapPaths=len(cap['paths']),rawAggregatePassed=cap['allAffectedHavePaths']))
    context=[]
    for f in sorted(BAD):
        ids=np.flatnonzero(np.any(np.all(tri[:,:,None,:]==tri[f][None,None,:,:],axis=3),axis=(1,2)))
        context.append(dict(sourceFace=f,vertices=tri[f].tolist(),exactSharedVertexNeighbours=[dict(sourceFace=int(i),vertices=tri[i].tolist())for i in ids]))
    save(out/'exact-context.json',dict(sourceComponent=group,faceContexts=context,modes=modes,installationApproved=False,architectureReview=False,qualification='Normals, exact source topology and neighbouring vertices only. No architectural role or ground/support acceptance follows from this diagnostic. Raw compound non-wall negatives remain false.'))
    selected=tri[sorted(BAD)];low=selected.min((0,1))-np.array([1.5,3,1.5]);high=selected.max((0,1))+np.array([1.5,4,1.5])
    def nearby(t):return t[np.all(t.max(1)>=low,axis=1)&np.all(t.min(1)<=high,axis=1)]
    origin=(low+high)/2
    fig=plt.figure(figsize=(16,7))
    for k,(azim,elev)in enumerate([(35,25),(-130,15)]):
        ax=fig.add_subplot(1,2,k+1,projection='3d')
        for t,color,alpha in [(nearby(podium),'teal',.25),(nearby(tri),'grey',.3),(selected,'red',1)]:
            ax.add_collection3d(Poly3DCollection((t-origin)[:,:,[0,2,1]],facecolors=color,edgecolors=color,linewidths=.25,alpha=alpha))
        a=low-origin;b=high-origin;ax.set_xlim(a[0],b[0]);ax.set_ylim(a[2],b[2]);ax.set_zlim(a[1],b[1]);ax.set_box_aspect((high-low)[[0,2,1]].copy());ax.view_init(elev=elev,azim=azim);ax.set_xlabel('X relative (m)');ax.set_ylabel('Z relative (m)');ax.set_zlabel('Y relative (m)');ax.set_title('Original tower grey / original podium teal / three downward faces red')
    fig.tight_layout();fig.savefig(out/'original-local-context.png',dpi=150);plt.close(fig)
    refs.extend(HERE/n for n in ['exact_packed_world_geometry_20261009.py','source_closed_components.py'])
    module('yoho_downward_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-downward-facade-context',refs,dict(uids=['landsd/56771:0','landsd/231756:0'],sourceGeometryChanges=0,installationApproved=False,architectureReview=False,negativeNonWallFaces=sorted(BAD),allWallCapPathsVerified=True))

if __name__=='__main__':main()
