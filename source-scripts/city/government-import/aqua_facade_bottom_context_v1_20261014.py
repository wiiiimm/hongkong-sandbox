"""Exact saved-triangle descriptors and 2D context; no acceptance thresholds."""
from fractions import Fraction
import numpy as np

def descriptor(face,tri):
    a=np.asarray(tri);assert a.shape==(3,3)and np.isfinite(a).all()
    p=[[Fraction(float(v))for v in row]for row in a];u=[p[1][k]-p[0][k]for k in range(3)];v=[p[2][k]-p[0][k]for k in range(3)];n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
    return dict(originalFaceID=int(face),exactXYZ=[[str(v)for v in row]for row in p],exactCrossNormal=[str(v)for v in n],nondegenerate=any(n),exactYRange=[str(min(row[1]for row in p)),str(max(row[1]for row in p))],exactTwiceProjectedArea=str(abs(n[1])),sourceRoleAssigned=None)

def shared_edges(a,b):
    def edges(t):
        keys=[tuple(float(v)for v in row)for row in t];return {tuple(sorted((keys[i],keys[(i+1)%3])))for i in range(3)}
    return [[list(p)for p in e]for e in sorted(edges(a)&edges(b))]

def draw_2d(tri,failed,partial,continuation):
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    fig,axes=plt.subplots(2,2,figsize=(18,12),dpi=100)
    for ax,(coords,title)in zip(axes.ravel(),[((0,2),'Full source plan: X/Z'),((0,1),'Full source side: X/HKPD Y'),((2,1),'Full source side: Z/HKPD Y'),((0,1),'Exact failed patch and full-height continuation: X/HKPD Y')]):
        detail=ax is axes[1,1];shown=sorted(set(failed+continuation))if detail else list(range(len(tri)))
        ax.add_collection(PolyCollection(tri[shown][:,:,coords],facecolors='#aaaaaa',edgecolors='#777777',linewidths=.15,alpha=.12))
        if not detail:ax.add_collection(PolyCollection(tri[partial][:,:,coords],facecolors='#e79a32',edgecolors='#c27512',linewidths=.3,alpha=.7))
        else:ax.add_collection(PolyCollection(tri[continuation][:,:,coords],facecolors='#44a4bc',edgecolors='#276a80',linewidths=.7,alpha=.3))
        ax.add_collection(PolyCollection(tri[failed][:,:,coords],facecolors='#c5266b',edgecolors='#950747',linewidths=1.3,alpha=1.))
        if detail:
            for i in failed+continuation:
                c=tri[i].mean(axis=0);ax.annotate(str(i),(c[coords[0]],c[coords[1]]),fontsize=8)
            ax.axhline(6.,color='#988766',linestyle='--',linewidth=1,label='Saved failed-face ground samples: Y=6 m (local only)');ax.legend(fontsize=8)
        ax.autoscale_view();ax.margins(.08);ax.set_aspect('equal',adjustable='datalim');ax.set_title(title);ax.set_xlabel(['world X / m','HKPD Y / m','world Z / m'][coords[0]]);ax.set_ylabel(['world X / m','HKPD Y / m','world Z / m'][coords[1]]);ax.grid(alpha=.15)
    fig.text(.025,.02,'2D exact saved literal triangulation projections, not rendered material or depth/occlusion proof. Grey: full source; orange: ALL 278 partial-below faces; magenta: 3 strict failures; cyan: 8 exact continuation faces.\nAll geometry remains unchanged. Original face IDs retain source attribution. Roles are proposed for ROOT review only; strict foundation FALSE, minimum gap and ordinary warning remain. No ground polygon fill / 3D painter occlusion.',fontsize=9);fig.subplots_adjust(left=.07,right=.98,top=.94,bottom=.1,hspace=.24,wspace=.2);return fig
