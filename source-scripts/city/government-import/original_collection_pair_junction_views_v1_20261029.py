"""Plot the complete exact original pair junction; display only, no acceptance."""
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

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','runtime','contacts','roles','uid','peer']:p.add_argument('--'+key,required=True)
    a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch
    assert a.batch.startswith('government-xl-') and '/'not in a.batch and not out.exists()
    pins={};refs=[Path(__file__)]
    def take(name,path):
        if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
        assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    contacts=take(a.contacts,base/a.contacts/'summary.json');roles=take(a.roles,base/a.roles/'summary.json');uids=sorted([a.uid,a.peer])
    assert len(set(uids))==2 and set(uids)<=set(contacts['uids']) and roles['uids']==contacts['uids'] and roles['sourceSHA256ByUid']==contacts['sourceSHA256ByUid']
    selected={r['uid']:r for r in take(a.runtime,base/a.runtime/'selection.json.gz')['rows']}
    geometry={r['uid']:r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']}
    mode=next(r for r in contacts['rows']if r['mode']=='original'and r['uid']==uids[0]and r['peerUid']==uids[1]);assert not mode['strictBoundsSeparated']
    rawpath=ROOT/mode['rawPath'];classified=take(a.roles,base/a.roles/rawpath.name);raw=take(a.contacts,rawpath)
    assert len(raw['contacts'])==len(classified) and raw['allPairsExamined'] and raw['sourceFacesOmitted']==0
    assert all({k:v for k,v in c.items()if k!='contactRole'}==r for c,r in zip(classified,raw['contacts']))
    triangles=[]
    for uid in uids:
        row=selected[uid];path=ROOT/row['candidate']['path'];assert digest(path.read_bytes())==row['sourceSHA256']==contacts['sourceSHA256ByUid'][uid];refs.append(path)
        tri=decode_original_world_triangles(path.read_bytes());triangles.append(tri)
    points=np.asarray([[float(Fraction(x))for x in point]for c in classified for point in c['exactPoints']]);assert len(points)
    lo,hi=points.min(0)-[2,1,2],points.max(0)+[2,3,2];size=np.maximum((hi-lo)[[0,2,1]],.1)
    planes=[(axis,float(lo[axis]),True)for axis in range(3)]+[(axis,float(hi[axis]),False)for axis in range(3)]
    ground=np.asarray(geometry[uids[0]]['drawnGroundGeometry'],float).reshape(-1,3,3)
    fig=plt.figure(figsize=(18,7),layout='constrained')
    for i,angle in enumerate([35,125,215]):
        ax=fig.add_subplot(1,3,i+1,projection='3d')
        for tri,color in zip(triangles,['#d04729','#2368b6']):
            ix=np.all(tri.max(1)>=lo,axis=1)&np.all(tri.min(1)<=hi,axis=1);polys=clipped_faces(tri[ix],planes)
            if len(polys):ax.add_collection3d(Poly3DCollection((polys-lo)[:,:,[0,2,1]],facecolors=color,edgecolors=color,alpha=.28,linewidth=.35))
        ix=np.all(ground.max(1)>=lo,axis=1)&np.all(ground.min(1)<=hi,axis=1);polys=clipped_faces(ground[ix],planes)
        if len(polys):ax.add_collection3d(Line3DCollection([np.vstack([v,v[:1]])for v in(polys-lo)[:,:,[0,2,1]]],colors='#16834a',linewidth=.5))
        for contact in classified:
            v=np.asarray([[float(Fraction(x))for x in point]for point in contact['exactPoints']])-lo
            if len(v)>1:ax.plot(v[:,0],v[:,2],v[:,1],color='#171717',linewidth=1)
            else:ax.scatter(v[:,0],v[:,2],v[:,1],color='#171717',s=4)
        ax.set(xlim=(0,size[0]),ylim=(0,size[1]),zlim=(0,size[2]),xlabel='X offset m',ylabel='Z offset m',zlabel='HKPD offset m');ax.set_box_aspect(size.copy());ax.view_init(24,angle)
    fig.suptitle('Original source pair: '+', '.join(uids)+'\nRed first source; blue second source; green drawn ground; black all exact contact loci. Display crop only.',fontsize=10)
    path=out/'complete-original-pair-junction.png';path.parent.mkdir();fig.savefig(path,dpi=140);plt.close(fig);refs.append(path)
    for path in refs:
        key=str(path.relative_to(ROOT))
        for bound in pins.values():
            if key in bound:assert digest(path.read_bytes())==bound[key]
    result=dict(uids=uids,sourceSHA256ByUid={u:contacts['sourceSHA256ByUid'][u]for u in uids},completeOriginalContactCount=len(classified),completeOriginalContactRoles=next(r['roles']for r in roles['rows']if r['mode']=='original'and r['uid']==uids[0]and r['peerUid']==uids[1]),image=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())),sourceGeometryChanges=0,physicalAcceptance=False,visualAcceptance=False,installationApproved=False,publication=False,qualification='Three views of both exact original surfaces, current drawn-ground context and every original finite contact locus. Only display context is clipped; no source geometry change or semantic/collision approval.')
    save(out/'summary.json',result);refs.extend([HERE/'exact_packed_world_geometry_20261009.py',HERE/'original_assembly_context_plot_v3_20261023.py'])
    module('original_pair_junction_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-exact-original-pair-junction-three-angle-display',refs,result)

if __name__=='__main__':main()
