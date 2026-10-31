"""Complete original orthographic context; display crops only, no model edits."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import'
INPUT=BASE/'government-xl-heya-aqua-184286-installed-podium-complete-source-census-v1-20261011'
SOURCES=BASE/'government-xl-georef-sparkle-heya-original-supports-20261008/support-inputs.json'
DOC=BASE/'government-xl-heya-aqua-terminal-parts-orthographic-context-v2-20261011'
T,P='landsd/184286:0','landsd/184285:0'
def main():
    assert not DOC.exists();data=read(INPUT/'diagnostic.json.gz');rows=read(SOURCES)['sources'];worlds={}
    for uid in [T,P]:
        selected=[r for r in rows if r['uid']==uid];assert len(selected)==1
        raw=(ROOT/selected[0]['candidate']['path']).read_bytes();assert digest(raw)==data['actors'][uid]['sourceTuple']['sourceSHA256']
        worlds[uid]=decode_original_world_triangles(raw);assert digest(worlds[uid].astype('<f8').tobytes())==data['actors'][uid]['sourceTuple']['worldSHA256']
    parts=data['actors'][T]['completeOriginalTopology']['sharedEdgeConnectedComponents']
    families=[f for f in data['completePositiveRealFacetInterfaceFamilies']if any(n[0]==T for n in f)and not any(n[0]==P for n in f)]
    ids=sorted(i for f in families for u,k in f if u==T for i in parts[k]);assert len(ids)==1312
    items=[('complete-58-terminal-source-facade-orthographic-3000x1800.png',ids,None),
        ('complete-repeat-A-122-facet-source-context-3000x1800.png',sorted(i for k in [93,94,279,280,281]for i in parts[k]),None),
        ('complete-repeat-B-16-facet-source-context-3000x1800.png',parts[140],None)]
    DOC.mkdir(parents=True)
    for filename,chosen,_ in items:
        fig,axes=plt.subplots(1,3,figsize=(15,9),dpi=200)
        lo=worlds[T][chosen].min((0,1));hi=worlds[T][chosen].max((0,1));span=np.maximum(hi-lo,.5);lo=lo-span*.25;hi=hi+span*.25
        for ax,(a,b),names in zip(axes,[(0,1),(2,1),(0,2)],[('City X','HKPD'),('City Z','HKPD'),('City X','City Z')]):
            for uid,color in [(P,'#638096'),(T,'#b7bdc5')]:
                ax.add_collection(PolyCollection(worlds[uid][:,:,[a,b]],facecolors=color,edgecolors='#999fa8',linewidths=.1,alpha=.3))
            ax.add_collection(PolyCollection(worlds[T][chosen][:,:,[a,b]],facecolors='#ed8b2c',edgecolors='#9f400a',linewidths=.5,alpha=.85))
            ax.set_xlim(lo[a],hi[a]);ax.set_ylim(lo[b],hi[b]);ax.set_xlabel(names[0]+' / m');ax.set_ylabel(names[1]+' / m');ax.grid(alpha=.2)
        fig.suptitle('Heya Aqua exact original source projections\nOrange: complete chosen source facets; grey/blue: full unchanged tower/podium context. Display crops only. No mount/root/function credit.',fontsize=11)
        fig.tight_layout(rect=(0,0,1,.94));fig.savefig(DOC/filename);plt.close(fig)
    save(DOC/'context.json',dict(uids=[T,P],complete58TerminalFaceIds=ids,sourceDiagnosticSHA256=digest((INPUT/'diagnostic.json.gz').read_bytes()),
        sourceGeometryChanges=0,currentAcceptance=False,visualRolesAccepted=False,groundRootsAccepted=False,
        images=[dict(filename=n,completeHighlightedOriginalFaceIds=c,width=3000,height=1800,sha256=digest((DOC/n).read_bytes()))for n,c,_ in items],
        producer=dict(path=str(Path(__file__).relative_to(ROOT)),sha256=digest(Path(__file__).read_bytes()))))
    print(DOC)
if __name__=='__main__':main()
