"""Plot every immutable original source face, coloured by provider-authored root.

Source coordinates are only permuted for chart axes. No source/terrain edits,
root filtering, fitted transforms, architectural reconstruction or acceptance.
"""
import argparse,sys,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from observed_reserved_runner_v2_20261103 import execute_reserved
from exact_packed_world_geometry_v2_20261103 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-source43101-complete-root-views-v1-20261103'
SELECT='government-xl-source43101-current-selection-v1-20261029'
PROVIDER='government-xl-after-sha-tin-43101-provider-roots-v1-20261029'
FBX='government-xl-source43101-raw-fbx-hierarchy-v2-20261103'

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--owned',action='store_true');a=ap.parse_args()
    out=BASE/BATCH;local=HERE/'local'/BATCH;lp=local/'reservation.json'
    if not a.owned:
        assert not out.exists() and not local.exists()
        c=reservations.claim('source43101-complete-source-views-'+str(uuid.uuid4()),['building:landsd/43101:0','immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    from pathlib import Path
    lease=read(lp);assert reservations.owns(lease);refs=[Path(__file__),HERE/'exact_packed_world_geometry_v2_20261103.py']
    values={}
    for batch,name in [(SELECT,'selection.json.gz'),(PROVIDER,'summary.json'),(FBX,'summary.json')]:
        _,pins=authenticate(BASE/batch);p=BASE/batch/name;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];values[batch]=read(p);refs.extend([BASE/batch/'result.json',p])
    row=values[SELECT]['rows'][0];proof=values[PROVIDER];assert row['uid']=='landsd/43101:0' and row['sourceSHA256']==proof['sourceSHA256'] and proof['allProviderAndPackedWorldArraysEqual']
    asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset)
    tri=decode_original_world_triangles(asset.read_bytes());counts=[r['completeFaces']for r in proof['roots']];assert sum(counts)==len(tri)==24308 and len(counts)==2
    pieces=np.split(tri,[counts[0]])
    for a,b in zip(pieces,proof['roots']):assert digest(a.astype('<f8').tobytes())==b['providerWorldSHA256']
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    colors=[np.array([.25,.52,.82]),np.array([.93,.51,.21])]
    plotted=tri[:,:,[0,2,1]];lo,hi=plotted.min((0,1)),plotted.max((0,1));center=(lo+hi)/2;radius=(hi-lo).max()/2
    outputs=[]
    for angle in [30,120,210,300]:
        fig=plt.figure(figsize=(10,9),dpi=160);ax=fig.add_subplot(projection='3d')
        for number,part in enumerate(pieces):
            faces=part[:,:,[0,2,1]];normals=np.cross(faces[:,1]-faces[:,0],faces[:,2]-faces[:,0]);length=np.linalg.norm(normals,axis=1);lighting=np.full(len(faces),.65);valid=length>0;lighting[valid]=.45+.55*np.abs(normals[valid]@np.array([.4,.3,.866]))/length[valid];shade=np.clip(lighting[:,None]*colors[number],0,1)
            ax.add_collection3d(Poly3DCollection(faces,facecolors=shade,edgecolors='none',linewidth=0))
        ax.set(xlim=(center[0]-radius,center[0]+radius),ylim=(center[1]-radius,center[1]+radius),zlim=(center[2]-radius,center[2]+radius),xlabel='Viewer X (m)',ylabel='Viewer Z (m)',zlabel='Elevation HKPD (m)');ax.set_box_aspect([1,1,1]);ax.view_init(elev=24,azim=angle)
        ax.set_title('43101: complete original, both authored roots\nBlue: B4561111 | Orange: B456572683001063C0')
        out.mkdir(exist_ok=True);p=out/('complete-two-roots-azimuth-'+str(angle)+'.png');fig.savefig(p);plt.close(fig);refs.append(p);outputs.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()),width=1600,height=1440,azimuth=angle))
    assert digest(asset.read_bytes())==row['sourceSHA256'] and reservations.owns(lease)
    result=dict(uids=[row['uid']],sourceSHA256=row['sourceSHA256'],sourceWorldArraySHA256=digest(tri.astype('<f8').tobytes()),allOriginalFacesRendered=len(tri),providerRoots=proof['roots'],images=outputs,allRootsRetained=True,chartAxesPermutation=[0,2,1],currentMapOrTerrainRendered=False,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,identityAccepted=False,physicalAcceptance=False,publication=False,qualification=__doc__)
    save(out/'summary.json',result)
    module('source43101_complete_root_view_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-original-two-provider-root-geometry-views',refs,result)

if __name__=='__main__':main()
