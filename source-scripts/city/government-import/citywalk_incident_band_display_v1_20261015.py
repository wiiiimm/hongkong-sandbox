"""Inspect complete attributed original lower facade bands and source podium."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/'government-xl-citywalk-incident-band-display-v1-20261015'
DESC=BASE/'government-xl-citywalk-current294-face-descriptors-v1-20261015/descriptors.json.gz';POD=BASE/'government-xl-citywalk-saved294-source-layer-attribution-v1-20261014/input.json.gz';CAP=BASE/'government-xl-citywalk-horizontal-caps-context-v1-20261015/caps.json'
assert not DOC.exists();DOC.mkdir();packet=read(DESC);pod=np.asarray(next(w['position']for w in read(POD)['sourceWorlds']if w['label']=='actualLiteral')).reshape(-1,3,3)
fig=plt.figure(figsize=(16,20));bindings=[]
for i,row in enumerate(packet['rows']):
    tris=np.asarray([f['sourceVertices']for f in row['faces']]);lo=tris.min((0,1));hi=tris.max((0,1));origin=np.array([lo[0],0,lo[2]])
    mask=(pod[:,:,0].max(1)>=lo[0]-1)&(pod[:,:,0].min(1)<=hi[0]+1)&(pod[:,:,2].max(1)>=lo[2]-1)&(pod[:,:,2].min(1)<=hi[2]+1)&(pod[:,:,1].max(1)>=lo[1]-1)&(pod[:,:,1].min(1)<=hi[1]+1)
    colors=['#e32929'if f['heightSpan']==0 else '#286fd0'if f['exactNormalYIsZero']else '#993dc2'for f in row['faces']]
    for j,(elev,az)in enumerate([(24,-55),(24,125)]):
        ax=fig.add_subplot(5,2,i*2+j+1,projection='3d')
        conv=lambda a:(a-origin)[:,:,[0,2,1]]
        ax.add_collection3d(Poly3DCollection(conv(pod[mask]),facecolors='#e3b76d',edgecolors='#705124',linewidths=.15,alpha=.22))
        ax.add_collection3d(Poly3DCollection(conv(tris),facecolors=colors,edgecolors='#183c5c',linewidths=.35,alpha=.9))
        ax.set_xlim(-1,hi[0]-lo[0]+1);ax.set_ylim(-1,hi[2]-lo[2]+1);ax.set_zlim(lo[1]-1,hi[1]+1);ax.view_init(elev=elev,azim=az);ax.set_box_aspect((hi[0]-lo[0]+2,hi[2]-lo[2]+2,hi[1]-lo[1]+2));ax.set_title(f"{row['uid']} — all {len(tris)} incident facets");ax.set_zlabel('HKPD m')
    bindings.append(dict(uid=row['uid'],faceIDs=[f['originalFaceID']for f in row['faces']],contextPodiumFaceIDs=np.flatnonzero(mask).tolist()))
fig.suptitle('Citywalk: unchanged lower tower bands entering original podium\nBlue: exact vertical; purple: other; red: horizontal caps; amber: contextual podium. Opposing views.',fontsize=14);fig.tight_layout(rect=[0,0,1,.96]);fig.savefig(DOC/'all-461-facets-opposing-views.png',dpi=130);plt.close(fig)
fig=plt.figure(figsize=(15,5))
for i,c in enumerate(read(CAP)['rows']):
    v=np.asarray(c['vertices']);origin=v[0,[0,2]];ax=fig.add_subplot(1,3,i+1);q=v[:,[0,2]]-origin;ax.fill(q[:,0],q[:,1],color='#e32929',alpha=.7);ax.plot(*np.vstack([q,q[0]]).T,color='black');ax.axis('equal');ax.grid(alpha=.2);ax.set_title(f"{c['uid']} face {c['originalFaceID']}\n{c['areaM2']:.8f} m², normalY={c['normalY']}");ax.set_xlabel('Local x (m)');ax.set_ylabel('Local z (m)')
fig.suptitle('Three complete source caps, plan view — no area-based acceptance');fig.tight_layout();fig.savefig(DOC/'three-complete-caps.png',dpi=130);plt.close(fig)
save(DOC/'display.json',dict(inputRefs=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in [Path(__file__),DESC,POD,CAP]],bindings=bindings,wholeIncidentFacets=461,geometryChanges=0,acceptance=False,qualification='Actual source vertices; all incident facets retained. Podium selected by closed XYZ context bounds for display only. Not full assembly visibility/collision acceptance.'))
print(DOC)
