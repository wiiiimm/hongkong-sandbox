"""Show complete source geometry responsible for the two footprint extent flags."""
from pathlib import Path
import numpy as np,shapely
from shapely.geometry import Polygon
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-mount-sterling-extent-context-v1-20261020';DOC=BASE/BATCH
SRC=BASE/'government-xl-mount-sterling-eight-identity-v1-20261020';REC=BASE/'government-xl-mount-sterling-nine-original-recovery-v1-20261020'
def main():
    assert not DOC.exists();refs=[Path(__file__),HERE/'exact_packed_world_geometry_20261009.py'];pins={}
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for folder in (SRC,REC):
            r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256'] for e in r['evidenceRefs']}
    def take(folder,path):
        assert digest(path.read_bytes())==pins[folder][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    rows=take(REC,REC/'recovery.json')['rows'];tile=ROOT/'3d-viewer/city/data/tiles/-2_-3.json';forms={b['uid']:b for b in take(SRC,tile)['buildings']};summary=[]
    for uid in ['landsd/103465:0','landsd/289787:0']:
        r=next(r for r in rows if r['uid']==uid and r['modelId']!='B323332207601063C0');p=ROOT/r['assetPath'];assert digest(p.read_bytes())==r['sourceSHA256']==pins[REC][r['assetPath']];refs.append(p)
        t=decode_original_world_triangles(p.read_bytes());b=forms[uid];polygon=Polygon(b['rings'][0],b['rings'][1:]);d=shapely.distance(shapely.points(t[:,:,[0,2]].reshape(-1,2)),polygon).reshape(-1,3);far=np.flatnonzero(d.max(1)>10);outside=np.flatnonzero(d.max(1)>0);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);area=np.linalg.norm(n,axis=1)/2
        rowsout=[dict(face=int(i),maximumDistanceM=float(d[i].max()),areaM2=float(area[i]),vertices=t[i].tolist()) for i in far]
        save(DOC/(uid.split('/')[1]+'-far-faces.json.gz'),dict(uid=uid,sourceSHA256=r['sourceSHA256'],rows=rowsout,installationApproved=False))
        fig,axes=plt.subplots(1,3,figsize=(18,7))
        for ax,dims,title in zip(axes,[(0,2),(0,1),(2,1)],['Plan','X/Y','Z/Y']):
            ax.add_collection(PolyCollection(t[:,:,dims],facecolors='#8ca0b5',edgecolors='none',alpha=.23));ax.add_collection(PolyCollection(t[far][:,:,dims],facecolors='#d94c35',edgecolors='#8c271b',linewidths=.2,alpha=.8));ax.autoscale();ax.set_title(title)
            if dims==(0,2):
                for other in forms.values():
                    if other.get('parent')==b['parent'] or other['uid']=='landsd/111045:0':
                        ring=np.asarray(other['rings'][0]);ax.plot(ring[:,0],ring[:,1],color='#173e37' if other['uid']==uid else '#777777',lw=2 if other['uid']==uid else .6)
                ax.set_aspect('equal')
        fig.suptitle(f'{uid} — unchanged original source grey; faces with a vertex >10m outside own footprint red\nOwn footprint dark green; companion/Mei Foo footprints grey. Diagnostic only.');fig.tight_layout();fig.savefig(DOC/(uid.split('/')[1]+'-extent.png'),dpi=140);plt.close(fig)
        out=dict(uid=uid,completeFaces=len(t),facesWithOutsideVertices=len(outside),facesWithVertexBeyond10m=len(far),maximumDistanceM=float(d.max()),farFaceYRange=[float(t[far,:,1].min()),float(t[far,:,1].max())],farFaceAreaM2=float(area[far].sum()),installationApproved=False);summary.append(out);print(out,flush=True)
    save(DOC/'summary.json',dict(rows=summary,installationApproved=False,sourceGeometryChanges=0));module('mount_sterling_extent_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'two-current-source-extent-contexts',refs,dict(uids=[r['uid'] for r in summary],rows=summary,installationApproved=False))
if __name__=='__main__':main()
