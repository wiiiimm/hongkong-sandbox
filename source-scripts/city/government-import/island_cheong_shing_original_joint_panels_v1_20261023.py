"""Measure and render unchanged original return panels; grant no physical approval."""
from pathlib import Path
from collections import defaultdict, deque
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-island-cheong-shing-original-joint-panels-v1-20261023';out=base/batch
    assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,name):
        if batch not in pins:
            pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        p=base/batch/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    runtime='government-xl-island-cheong-shing-four-original-runtime-v3-20261023'
    selected={r['uid']:r for r in take(runtime,'selection.json.gz')['rows']}
    attribution='government-xl-island-cheong-shing-source-internal-embedding-v1-20261023'
    summary=take(attribution,'summary.json');assert summary['actualTerrainNegativeHalfMetreSamples']==0
    geometries={}
    for uid,r in selected.items():
        p=ROOT/r['candidate']['path'];raw=p.read_bytes();assert digest(raw)==r['sourceSHA256'];refs.append(p);geometries[uid]=decode_original_world_triangles(raw)
    records=[];fig=plt.figure(figsize=(14,9),layout='constrained')
    for panel,(uid,support) in enumerate([('landsd/20270:0','landsd/159422:0'),('landsd/274231:0','landsd/269430:0')]):
        detail=take(attribution,uid.replace('/','-').replace(':','-')+'/original.json.gz');assert detail['supportUid']==support
        t=geometries[uid];norm=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);renderable=np.linalg.norm(norm,axis=1)>0
        edgefaces=defaultdict(list)
        for i,face in enumerate(t):
            if not renderable[i]:continue
            for a,b in [(0,1),(1,2),(2,0)]:
                va,vb=tuple(face[a]),tuple(face[b])
                if va!=vb:edgefaces[tuple(sorted([va,vb]))].append(i)
        adjacency=defaultdict(set)
        for faces in edgefaces.values():
            for i in faces:adjacency[i].update(j for j in faces if j!=i)
        faceids=[r['sourceFace']for r in detail['rows']];assert len(faceids)==2
        rows=[]
        for f in faceids:
            queue=deque([f]);prev={f:None};target=None
            while queue:
                i=queue.popleft()
                if norm[i,1]>0:target=i;break
                for j in sorted(adjacency[i]):
                    if j not in prev:prev[j]=i;queue.append(j)
            path=[]
            if target is not None:
                i=target
                while i is not None:path.append(i);i=prev[i]
                path.reverse()
            rows.append(dict(sourceFace=f,areaM2=float(np.linalg.norm(norm[f])/2),normalY=float(norm[f,1]),exactSharedEdgeNeighbours=sorted(adjacency[f]),pathToUpwardSourceFace=path,upwardFaceReachable=target is not None,structuralSupportClaimed=False))
        points=t[faceids].reshape(-1,3);low,high=points.min(0)-1.5,points.max(0)+1.5;center=(low+high)/2
        for v,angle in enumerate([35,215]):
            ax=fig.add_subplot(2,2,panel*2+v+1,projection='3d')
            for key,color,alpha in [(uid,'#4381ad',.55),(support,'#db983c',.4)]:
                s=geometries[key];mask=np.all(s.max(1)>=low,axis=1)&np.all(s.min(1)<=high,axis=1)
                ax.add_collection3d(Poly3DCollection(s[mask][:,:,[0,2,1]],facecolor=color,edgecolor='none',alpha=alpha))
            ax.add_collection3d(Poly3DCollection(t[faceids][:,:,[0,2,1]],facecolor='#e52241',edgecolor='black',linewidth=.7))
            ax.set(xlim=(low[0],high[0]),ylim=(low[2],high[2]),zlim=(low[1],high[1]),title=uid+' source faces '+str(faceids),xlabel='X',ylabel='Z',zlabel='HKPD height')
            ax.set_box_aspect((high-low)[[0,2,1]]);ax.view_init(elev=20,azim=angle)
        records.append(dict(uid=uid,supportUid=support,sourceSHA256=selected[uid]['sourceSHA256'],supportSHA256=selected[support]['sourceSHA256'],rows=rows))
    out.mkdir(parents=True);fig.suptitle('Original joint panels in red; unchanged tower blue / original podium orange\nSource-only diagnostic; transparency reveals adjacency, not solid containment or physical approval');fig.savefig(out/'original-joint-panels.png',dpi=150);plt.close(fig)
    result=dict(uids=list(selected),rows=records,sourceGeometryChanges=0,physicalAccepted=False,installationApproved=False,qualification='Exact shared-edge paths and source-only closeups identify topology of each flagged vertical face. An upward source face is not a ground/support root. No internal overlap, structural, foreign collision or publication approval is inferred.')
    save(out/'summary.json',result);refs.append(HERE/'exact_packed_world_geometry_20261009.py');module('joint_panels_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-original-joint-panel-topology-and-visual-context',refs,result);print(result,flush=True)

if __name__=='__main__':main()
