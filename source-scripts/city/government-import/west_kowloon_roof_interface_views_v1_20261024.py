"""Show original roof/parapet interfaces, preserving every strict support negative."""
from pathlib import Path
from collections import defaultdict,deque
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection,Line3DCollection
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from pool_incident_wall_contacts_v1_20261017 import closest


def main():
    base=ROOT/'docs/astra-city/government-import';prefix='government-xl-next-repairs-west-kowloon-bus-';batch=prefix+'roof-interface-views-v1-20261024';out=base/batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(s,f):
        n=prefix+s
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        p=base/n/f;assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    selected={r['uid']:r for r in take('five-original-runtime-v1-20261024','selection.json.gz')['rows']};tri={}
    for uid,r in selected.items():
        p=ROOT/r['candidate']['path'];assert digest(p.read_bytes())==r['sourceSHA256'];refs.append(p);tri[uid]=decode_original_world_triangles(p.read_bytes())
    rows=[]
    for number in ['231056','267223']:
        uid='landsd/'+number+':0';t=tri[uid];support=tri['landsd/255415:0'];proof=take('roof'+number+'-support-v1-20261024','summary.json')['rows'][0];assert proof['mode']=='original';unresolved=proof['support']['unresolved'];pts=np.asarray([r['position']for r in unresolved]);norm=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);length=np.linalg.norm(norm,axis=1);incident=set()
        for point in pts:
            broad=np.flatnonzero(np.all(t.min(1)<=point+.001,axis=1)&np.all(t.max(1)>=point-.001,axis=1))
            incident.update(int(i)for i in broad if length[i]>0 and np.linalg.norm(closest(point,t[i])-point)<=.001)
        embedding=take('internal-roof-embedding-v1-20261024',uid.replace('/','-').replace(':','-')+'/original.json.gz');faces=sorted(incident|{r['sourceFace']for r in embedding['rows']});assert faces
        edges=defaultdict(list);adj=defaultdict(set)
        for i,face in enumerate(t):
            if not length[i]:continue
            for a,b in [(0,1),(1,2),(2,0)]:
                edge=tuple(sorted((tuple(face[a]),tuple(face[b]))))
                if edge[0]!=edge[1]:edges[edge].append(i)
        for ids in edges.values():
            for i in ids:adj[i].update(j for j in ids if j!=i)
        paths=[]
        for start in faces:
            queue=deque([start]);prev={start:None};target=None
            while queue:
                i=queue.popleft()
                if norm[i,1]>.5*length[i]:target=i;break
                for j in sorted(adj[i]):
                    if j not in prev:prev[j]=i;queue.append(j)
            path=[];i=target
            while i is not None:path.append(i);i=prev[i]
            paths.append(dict(sourceFace=start,normalYRatio=float(norm[start,1]/length[start]),exactSharedEdgePathToUpwardOriginalFace=path[::-1],upwardFaceReachable=target is not None))
        allpts=t[faces].reshape(-1,3);lo,hi=allpts.min(0)-1.5,allpts.max(0)+1.5;centre=(lo+hi)/2;fig=plt.figure(figsize=(16,8))
        for v,az in enumerate([-125,55]):
            ax=fig.add_subplot(1,2,v+1,projection='3d',computed_zorder=False)
            for geometry,color in [(support,'#d89838'),(t,'#426e91')]:
                mask=np.all(geometry.max(1)>=lo,axis=1)&np.all(geometry.min(1)<=hi,axis=1);q=(geometry[mask]-centre)[:,:,[0,2,1]];segments=q[:,[0,1,1,2,2,0],:].reshape(-1,2,3);ax.add_collection3d(Line3DCollection(segments,colors=color,linewidths=.45,alpha=.7,zorder=1))
            ax.add_collection3d(Poly3DCollection((t[faces]-centre)[:,:,[0,2,1]],facecolor='#e52241',edgecolor='black',linewidth=.25,alpha=.65,zorder=10));q=(pts-centre)[:,[0,2,1]];ax.scatter(*q.T,c='black',s=7,zorder=12)
            ax.set(xlim=(lo[0]-centre[0],hi[0]-centre[0]),ylim=(lo[2]-centre[2],hi[2]-centre[2]),zlim=(lo[1]-centre[1],hi[1]-centre[1]),xlabel='Local X m',ylabel='Local Z m',zlabel='Height m');ax.set_box_aspect((hi-lo)[[0,2,1]].copy());ax.view_init(20,az)
        fig.suptitle(uid+': all unresolved rim points black / incident original faces red\nOriginal roof blue, original podium orange; red drawn above wire for inspection, no acceptance');fig.tight_layout();p=out/(number+'.png');p.parent.mkdir(parents=True,exist_ok=True);fig.savefig(p,dpi=150);plt.close(fig)
        rows.append(dict(uid=uid,rawStrictUnresolved=len(unresolved),paths=paths,embeddingFaces=[r['sourceFace']for r in embedding['rows']],incidentFaces=faces,image=str(p.relative_to(ROOT)),imageSHA256=digest(p.read_bytes()),allIncidentHaveUpwardOriginalPath=all(r['upwardFaceReachable']for r in paths)))
    result=dict(uids=list(selected),sourceSHA256ByUid={u:r['sourceSHA256']for u,r in selected.items()},rows=rows,sourceGeometryChanges=0,physicalAccepted=False,installationApproved=False,qualification='All unresolved original-mode rim points and all below-half-metre original-support embedding faces shown, with exact shared-edge source paths to upward original surfaces. Incident-point matching retains existing1mm diagnostic tolerance; paths and plot colours do not establish canonical support, structural roots, collision or publication approval. Four-world strict negatives remain unchanged.')
    save(out/'summary.json',result);refs.extend(HERE/n for n in ['exact_packed_world_geometry_20261009.py','pool_incident_wall_contacts_v1_20261017.py']);module('west_roof_interface_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'actual-original-roof-parapet-interface-and-rim-context',refs,result)

if __name__=='__main__':main()
