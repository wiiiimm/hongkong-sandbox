"""Actual original source context, not support or current approval."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BASE=ROOT/'docs/astra-city/government-import'
INPUT=BASE/'government-xl-heya-aqua-184286-installed-podium-complete-source-census-v1-20261011'
SOURCES=BASE/'government-xl-georef-sparkle-heya-original-supports-20261008/support-inputs.json'
DOC=BASE/'government-xl-heya-aqua-completed-original-terminal-parts-context-v1-20261011'
T,P='landsd/184286:0','landsd/184285:0'

def main():
    assert not DOC.exists()
    data=read(INPUT/'diagnostic.json.gz');sources=read(SOURCES)['sources'];worlds={}
    for uid in [T,P]:
        rows=[r for r in sources if r['uid']==uid];assert len(rows)==1
        raw=(ROOT/rows[0]['candidate']['path']).read_bytes()
        assert digest(raw)==data['actors'][uid]['sourceTuple']['sourceSHA256']
        worlds[uid]=decode_original_world_triangles(raw)
        assert digest(worlds[uid].astype('<f8').tobytes())==data['actors'][uid]['sourceTuple']['worldSHA256']
    families=data['completePositiveRealFacetInterfaceFamilies']
    unrelated=[f for f in families if any(n[0]==T for n in f)and not any(n[0]==P for n in f)]
    terminal=sorted(n[1]for f in unrelated for n in f if n[0]==T)
    assert len(terminal)==58
    parts=data['actors'][T]['completeOriginalTopology']['sharedEdgeConnectedComponents']
    ids=sorted(i for k in terminal for i in parts[k]);assert len(ids)==1312
    views=[('whole-original-pair-terminal-facade-parts-3000x1800.png',None,[(93,'A: repeated group'),(140,'B: repeated part')]),
        ('repeat-group-A-original-context-3000x1800.png',[-534,-530,-5688,-5683,89,120],[(93,'93–94 /279–281'),(190,'190–191 /273–275')]),
        ('repeat-group-B-original-context-3000x1800.png',[-529,-523,-5699,-5693,80,120],[(140,'140–150 /194')])]
    DOC.mkdir(parents=True)
    for filename,bounds,labels in views:
        fig=plt.figure(figsize=(15,9),dpi=200);ax=fig.add_subplot(projection='3d')
        for uid,color,alpha in [(P,'#526f80',.75),(T,'#adb6bd',.65)]:
            tri=worlds[uid];keep=np.ones(len(tri),bool)
            if bounds is not None:
                low=np.array([bounds[0],bounds[4],bounds[2]]);high=np.array([bounds[1],bounds[5],bounds[3]])
                keep=np.all(tri.max(1)>=low,axis=1)&np.all(tri.min(1)<=high,axis=1)
            ax.add_collection3d(Poly3DCollection(tri[keep][:,:,[0,2,1]],facecolors=color,edgecolors='none',alpha=alpha))
        highlights=worlds[T][ids];ax.add_collection3d(Poly3DCollection(highlights[:,:,[0,2,1]],facecolors='#e87516',edgecolors='#9b3d0d',linewidths=.15,alpha=1))
        if bounds is None:
            allpoints=np.concatenate([worlds[u].reshape(-1,3)for u in [T,P]]);lo=allpoints.min(0);hi=allpoints.max(0);bounds=[lo[0]-2,hi[0]+2,lo[2]-2,hi[2]+2,lo[1]-2,hi[1]+2]
        ax.set_xlim(bounds[:2]);ax.set_ylim(bounds[2:4]);ax.set_zlim(bounds[4:6]);ax.set_box_aspect([bounds[1]-bounds[0],bounds[3]-bounds[2],bounds[5]-bounds[4]])
        for part,label in labels:
            c=worlds[T][parts[part]].mean((0,1));ax.text(c[0],c[2],c[1],label,color='#702800',fontsize=8)
        ax.view_init(elev=16,azim=-42);ax.set_xlabel('City X / m');ax.set_ylabel('City Z / m');ax.set_zlabel('HKPD / m')
        ax.set_title('Heya Aqua unchanged original source\nOrange: complete58 components /1312facets with no positive interface path to podium; no role/root credit',fontsize=11)
        fig.tight_layout();fig.savefig(DOC/filename);plt.close(fig)
    save(DOC/'context.json',dict(uids=[T,P],completeTerminalComponentIds=terminal,completeTerminalFaceIds=ids,
        sourceDiagnosticSHA256=digest((INPUT/'diagnostic.json.gz').read_bytes()),
        actualSourceWorldSHA256s={u:data['actors'][u]['sourceTuple']['worldSHA256']for u in [T,P]},
        sourceGeometryChanges=0,visualRolesAccepted=False,groundRootsAccepted=False,currentAcceptance=False,
        images=[dict(filename=name,sha256=digest((DOC/name).read_bytes()),width=3000,height=1800)for name,_,_ in views],
        producer=dict(path=str(Path(__file__).relative_to(ROOT)),sha256=digest(Path(__file__).read_bytes()))))
    print(DOC)

if __name__=='__main__':main()
