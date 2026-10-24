"""Two display-only orthographic sheets from saved indexed source/TIN arrays."""
from fractions import Fraction
GROUPS=[('A: 12130/31/32',[12130,12131,12132]),('B: 12150/12249',[12150,12249]),('C: 12191–95/12288/90/92/93',[12191,12192,12193,12194,12195,12288,12290,12292,12293]),('D: 12199/12201/02/03',[12199,12201,12202,12203])]

def bind_groups(packet):
    ids=[i for _,g in GROUPS for i in g]
    assert len(ids)==len(set(ids))==18 and sorted(ids)==packet['sourceFaceIDs']
    assert len(packet['all22SavedBelowMinus05WitnessesVerbatim'])==22 and packet['sourceRoleAssigned'] is False and packet['warningResolved'] is False
    return GROUPS

def emit_projection(ax,source,ground,selected,witnesses,axes):
    """Projection only: every supplied triangle retained; no sections/height sampling."""
    import numpy as np
    from matplotlib.collections import PolyCollection
    a,b=axes
    for tri,color,alpha,width in [(source,'#667085',.13,.25),(ground,'#238751',.18,.3),(selected,'#c93535',.9,1.1)]:
        if len(tri):ax.add_collection(PolyCollection(np.asarray(tri)[:,:,[a,b]],facecolors='none',edgecolors=color,linewidths=width,alpha=alpha))
    if len(witnesses):
        w=np.asarray(witnesses);ax.scatter(w[:,a],w[:,b],s=13,c='#bc2020',edgecolors='white',linewidths=.2,zorder=4)
    ax.autoscale_view();ax.grid(alpha=.17);ax.ticklabel_format(useOffset=False,style='plain');ax.set_xlabel(['X east, city metres','Y elevation, metres','Z = −north, city metres'][a]);ax.set_ylabel(['X east, city metres','Y elevation, metres','Z = −north, city metres'][b])

def render_saved(packet,geometry,out):
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    bind_groups(packet);pos=np.asarray(geometry['position'],dtype='<f8').reshape(-1,3);index=np.asarray(geometry['index'],dtype=np.int64).reshape(-1,3);tri=pos[index];ground=np.asarray(geometry['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)
    assert tri.shape==(15140,3,3) and pos.shape==(43248,3) and np.isfinite(tri).all() and np.isfinite(ground).all()
    for d in packet['fourWorldDescriptors']['literal']:
        exact=np.asarray([[float(Fraction(v))for v in xyz]for xyz in d['exactXYZ']],dtype='<f8');assert exact.tobytes()==tri[d['originalFaceID']].tobytes()
    ids=packet['sourceFaceIDs'];w=packet['all22SavedBelowMinus05WitnessesVerbatim'];points=[q['xyz']for q in w]
    fig,ax=plt.subplots(figsize=(16,11),dpi=200);emit_projection(ax,tri,ground,tri[ids],points,(0,2));ax.set_aspect('equal');ax.set_title('Complete indexed Museum source plan / saved authentic drawn TIN / exact18 faces and all22 samples')
    for name,g in GROUPS:
        p=tri[g].reshape(-1,3).mean(axis=0);ax.annotate(name,(p[0],p[2]),xytext=(5,5),textcoords='offset points',fontsize=8,bbox=dict(facecolor='white',alpha=.8,edgecolor='none'))
    fig.text(.02,.02,'Grey: complete15140 literal source triangles. Green: complete saved drawn TIN. Red: exact18 +22 raw below−.5 points.\nOrthographic projection, not live occlusion or a support/collision certificate. Source roles unassigned; raw warning remains.',fontsize=10);fig.tight_layout(rect=(0,.07,1,1));p=out/'full-indexed-literal-source-and-authentic-ground-plan-3200x2200.png';fig.savefig(p);plt.close(fig)
    fig,axs=plt.subplots(4,3,figsize=(18,15),dpi=200);panels=[]
    for row,(name,g)in enumerate(GROUPS):
        sel=tri[g];lo=sel.min(axis=(0,1));hi=sel.max(axis=(0,1));margin=max(float(hi[0]-lo[0]),float(hi[2]-lo[2]),1)*.15+1
        xzlo=lo[[0,2]]-margin;xzhi=hi[[0,2]]+margin
        def keep(t):return ((t[:,:,[0,2]].max(axis=1)>=xzlo)&(t[:,:,[0,2]].min(axis=1)<=xzhi)).all(axis=1)
        src=tri[keep(tri)];terrain=ground[keep(ground)];wp=[q['xyz']for q in w if set(q['sourceLineage']['originalFaceIDs']).intersection(g)]
        for col,axes in enumerate([(0,2),(0,1),(2,1)]):
            ax=axs[row,col];emit_projection(ax,src,terrain,sel,wp,axes)
            if col==0:ax.set_xlim(xzlo[0],xzhi[0]);ax.set_ylim(xzlo[1],xzhi[1]);ax.set_aspect('equal')
            else:
                dim=axes[0];k=0 if dim==0 else 1;ax.set_xlim(xzlo[k],xzhi[k]);ax.set_ylim(lo[1]-.4,hi[1]+1.5)
            ax.set_title(name+' — '+['plan','X/Y projection','Z/Y projection'][col],fontsize=9)
        context=sorted({i for q in packet['exactSharedSourceEdgeContext']['literal'] if set(q['selectedFaceIDs']).intersection(g) for i in q['allExactSourceFaceIDs']})
        panels.append(dict(name=name,selectedSourceFaceIDs=g,allExactSharedEdgeContinuationIDsContextOnly=context,sourceTriangleIDsInDisplayWindow=np.flatnonzero(keep(tri)).tolist(),savedGroundTriangleIDsInDisplayWindow=np.flatnonzero(keep(ground)).tolist(),displayMarginM=margin,sourceAboveYDisplayCropRetainedInFullPlan=True))
    fig.suptitle('Exact18 lower-source context: saved literal geometry and authentic TIN projections',fontsize=16);fig.text(.01,.015,'Grey source / green TIN outlines / red selected faces and below−.5 samples. Side panels are projections, not cuts or sampled ground profiles.\nLocal display windows and Y crops are framing only; full source/ground retained in plan. No role, burial, support, collision or installation approval.',fontsize=11);fig.tight_layout(rect=(0,.06,1,.975));q=out/'exact18-literal-source-and-authentic-ground-projections-3600x3000.png';fig.savefig(q);plt.close(fig)
    return [p,q],panels
