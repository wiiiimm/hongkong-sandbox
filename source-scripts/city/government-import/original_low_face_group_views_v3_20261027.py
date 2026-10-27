"""Plot every exact low-face group and optional original-pair junction, without approval."""
import argparse
from pathlib import Path
from fractions import Fraction
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection,Line3DCollection
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_assembly_context_plot_v3_20261023 import clipped_faces


def groups(tri,ids):
    remaining=set(ids);out=[]
    while remaining:
        seen={min(remaining)};remaining-=seen;vertices=set(map(tuple,tri[min(seen)]))
        while True:
            found={i for i in remaining if any(tuple(v) in vertices for v in tri[i])}
            if not found:break
            remaining-=found;seen|=found
            for i in found:vertices.update(map(tuple,tri[i]))
        out.append(sorted(seen))
    assert sorted(i for group in out for i in group)==sorted(ids)
    return out


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','low-faces','uid']:p.add_argument('--'+k,required=True)
    p.add_argument('--pair-contacts');p.add_argument('--peer');a=p.parse_args()
    assert bool(a.pair_contacts)==bool(a.peer)
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert a.batch.startswith('government-xl-')and '/'not in a.batch and not out.exists()
    refs=[Path(__file__)];pins={}
    def take(name,path):
        if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
        assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=take(a.runtime,base/a.runtime/'selection.json.gz');source=next(r for r in selection['rows']if r['uid']==a.uid)
    def original(row):
        path=ROOT/row['candidate']['path'];assert digest(path.read_bytes())==row['sourceSHA256'];refs.append(path);return decode_original_world_triangles(path.read_bytes())
    tri=original(source);low=take(a.low_faces,base/a.low_faces/'original.json.gz');assert digest(tri.astype('<f8').tobytes())==low['sourceWorldSHA256']
    geometry=next(r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']if r['uid']==a.uid);ground=np.asarray(geometry['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);assert digest(ground.tobytes())==low['groundSHA256']
    ids=[r['sourceFace']for r in low['rows']];clusters=groups(tri,ids);exports=[];records=[];out.mkdir()
    def draw(label,selected,other=None,contact_points=None):
        points=tri[selected].reshape(-1,3)if contact_points is None else contact_points
        lo,hi=points.min(0)-[2,1,2],points.max(0)+[2,3,2];size=np.maximum((hi-lo)[[0,2,1]],.1)
        planes=[(axis,float(lo[axis]),True)for axis in range(3)]+[(axis,float(hi[axis]),False)for axis in range(3)]
        fig=plt.figure(figsize=(15,7),layout='constrained')
        for k,angle in enumerate([35,215]):
            ax=fig.add_subplot(1,2,k+1,projection='3d')
            meshes=[(tri,'#64748b',.12),(tri[selected],'#d04729',.95)]
            if other is not None:meshes.append((other,'#2368b6',.4))
            for mesh,color,alpha in meshes:
                ix=np.all(mesh.max(1)>=lo,axis=1)&np.all(mesh.min(1)<=hi,axis=1);polys=clipped_faces(mesh[ix],planes)
                if len(polys):ax.add_collection3d(Poly3DCollection((polys-lo)[:,:,[0,2,1]],facecolors=color,edgecolors=color,alpha=alpha,linewidth=.35))
            ix=np.all(ground.max(1)>=lo,axis=1)&np.all(ground.min(1)<=hi,axis=1);polys=clipped_faces(ground[ix],planes)
            if len(polys):ax.add_collection3d(Line3DCollection([np.vstack([v,v[:1]])for v in (polys-lo)[:,:,[0,2,1]]],colors='#16834a',linewidth=.7))
            for i in selected:
                c=tri[i].mean(0)-lo
                if np.all(c>=0)and np.all(c<hi-lo):ax.text(c[0],c[2],c[1],str(i),fontsize=6)
            ax.set(xlim=(0,size[0]),ylim=(0,size[1]),zlim=(0,size[2]),xlabel='X offset m',ylabel='Z offset m',zlabel='HKPD offset m');ax.set_box_aspect(size.copy());ax.view_init(24,angle)
        fig.suptitle(f'{a.uid}: {label}\nRed: all declared original facets; grey: source context; green: drawn terrain; blue: original peer. Display crops only.',fontsize=11)
        path=out/(label+'.png');fig.savefig(path,dpi=140);plt.close(fig);refs.append(path);exports.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())))
    for i,cluster in enumerate(clusters):
        draw('low-group-'+str(i+1),cluster);t=tri[cluster];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);length=np.linalg.norm(n,axis=1)
        records.append(dict(sourceFaces=cluster,bounds=[t.min((0,1)).tolist(),t.max((0,1)).tolist()],facets=[dict(sourceFace=j,areaM2=float(length[k]/2),signedNormalYRatio=float(n[k,1]/length[k]) if length[k] > 0 else None,degenerate=bool(length[k] == 0))for k,j in enumerate(cluster)]))
    pair=None
    if a.peer:
        peerrow=next(r for r in selection['rows']if r['uid']==a.peer);peer=original(peerrow);summary=take(a.pair_contacts,base/a.pair_contacts/'summary.json');assert summary['uids']==[a.uid,a.peer]
        for record,row in zip(summary['rows'],[source,peerrow]):assert record['sourceSHA256']==row['sourceSHA256']
        contacts=take(a.pair_contacts,base/a.pair_contacts/'complete-classified-contacts.json.gz');special=[r for r in contacts if r['dimension']==2 or r['contactRole']=='transverse-surface-crossing'];assert special
        selected=sorted({r['sourceFaceA']for r in special});points=np.asarray([[float(Fraction(x))for x in v]for r in special for v in r['exactPoints']]);draw('original-peer-area-and-crossing',selected,peer,points);pair=dict(peer=a.peer,allContactDimensions=summary['contactDimensions'],allContactRoles=summary['contactRoles'],displayedAreaAndCrossingContacts=special)
    result=dict(uids=[a.uid],sourceSHA256=source['sourceSHA256'],completeAffectedFaces=ids,groups=records,pair=pair,exports=exports,sourceGeometryChanges=0,architectureReview=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Every declared exact low facet belongs to exactly one displayed exact-shared-vertex group. Local plots clip display context only and label original face IDs; no mesh, placement, terrain or contact changes, and no review approval.')
    save(out/'summary.json',result);refs.extend([HERE/'exact_packed_world_geometry_20261009.py',HERE/'original_assembly_context_plot_v3_20261023.py']);module('low_group_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-original-low-face-group-and-pair-junction-views',list(dict.fromkeys(refs)),result);print(dict(groups=len(clusters),faces=len(ids),exports=len(exports)),flush=True)

if __name__=='__main__':main()
