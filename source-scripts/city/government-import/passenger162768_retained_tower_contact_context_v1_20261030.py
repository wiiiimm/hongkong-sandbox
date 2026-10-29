"""Exact retained auxiliary contacts and local scientific views; no geometry edits."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module
P='government-xl-passenger162768-after-civic-five-'
BATCH=P+'retained-tower-contact-context-v1-20261030'

def main():
    base=ROOT/'docs/astra-city/government-import';doc=base/BATCH;assert not doc.exists()
    refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:
            pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    runtime=P+'current-ground-v1-20261030';foreign=P+'foreign-contacts-v1-20261030'
    selection=take(runtime,base/runtime/'selection.json.gz');row=next(r for r in selection['rows'] if r['uid']=='landsd/162768:0')
    asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset)
    tri=decode_original_world_triangles(asset.read_bytes());assert len(tri)==32238
    basics=take(foreign,base/foreign/'basic.json')['rows'];rows=[]
    for object_id in [153422,332872]:
        uid=f'landsd/{object_id}:0';b=next(r for r in basics if r['uid']==uid)
        mesh=np.asarray(b['position']).reshape(-1,3)[np.asarray(b['index']).reshape(-1,3)]
        low,high=mesh.reshape(-1,3).min(0),mesh.reshape(-1,3).max(0)
        modes=[]
        for mode in ['original','literal','leftF32','balancedF32']:
            proof=take(foreign,base/foreign/f'162768:0--{object_id}:0--{mode}.json.gz')
            contacts=[c for c in proof['contacts'] if c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2 and c['dimension']>0]
            ids=sorted({c['sourceFaceA'] for c in contacts})
            modes.append(dict(mode=mode,positiveContacts=len(contacts),sourceFaceIds=ids,contactHeightRangeM=[min(c['bounds'][0][1] for c in contacts),max(c['bounds'][1][1] for c in contacts)]))
        ids=modes[0]['sourceFaceIds'];detail=[]
        for index in ids:
            t=tri[index];normal=np.cross(t[1]-t[0],t[2]-t[0]);length=np.linalg.norm(normal)
            detail.append(dict(faceIndex=index,vertices=t.tolist(),unitNormal=(normal/length).tolist(),heightRangeM=[float(t[:,1].min()),float(t[:,1].max())]))
        context=np.all(tri.max(1)>=low-2,axis=1)&np.all(tri.min(1)<=high+2,axis=1)
        fig=plt.figure(figsize=(12,6));fig.suptitle(f'{uid}: unchanged retained BASIC (orange), original (blue), contacting original facets (red)')
        for col,azimuth in enumerate([30,120],1):
            ax=fig.add_subplot(1,2,col,projection='3d')
            for triangles,color,alpha in [(tri[context],'#2c7fb8',.12),(mesh,'#ffa600',.35),(tri[ids],'#d73027',.45)]:
                # Plot axes X,Z,Y so up remains HKPD. Camera clipping is visual only.
                ax.add_collection3d(Poly3DCollection(triangles[:,:,[0,2,1]],facecolor=color,edgecolor=color,linewidth=.2,alpha=alpha))
            ax.set_xlim(low[0]-2,high[0]+2);ax.set_ylim(low[2]-2,high[2]+2);ax.set_zlim(low[1]-2,high[1]+2)
            ax.set_xlabel('X (m)');ax.set_ylabel('Z (m)');ax.set_zlabel('HKPD (m)');ax.view_init(elev=24,azim=azimuth)
            ax.ticklabel_format(useOffset=False);ax.set_box_aspect((high[0]-low[0]+4,high[2]-low[2]+4,high[1]-low[1]+4))
        path=doc/f'{object_id}-local-contact-context.png';path.parent.mkdir(parents=True,exist_ok=True);fig.savefig(path,dpi=160,bbox_inches='tight');plt.close(fig)
        rows.append(dict(uid=uid,exactBasicForm=b['currentBuilding'],basicBounds=[low.tolist(),high.tolist()],modes=modes,originalContactFacets=detail,diagram=str(path.relative_to(ROOT))))
    result=dict(uids=[row['uid']],sourceSHA256=row['sourceSHA256'],rows=rows,completeOriginalFaces=32238,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,identityAccepted=False,installationApproved=False,qualification='All finite contacts preserved in four worlds. Local plots use original coordinates and fixed camera limits, not modified source geometry. Both auxiliary BASIC actors remain retained. Support/ownership/architectural interpretation is separate.')
    save(doc/'summary.json',result)
    module('passenger_retained_tower_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'retained-two-tower-exact-original-contact-context',refs,result)

if __name__=='__main__':main()
