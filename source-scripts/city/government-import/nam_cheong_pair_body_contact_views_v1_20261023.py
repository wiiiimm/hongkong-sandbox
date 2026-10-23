"""Current-bound views and exact plane-side extents for original pair crossings."""
from fractions import Fraction as F
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BATCH='government-xl-nam-cheong-pair-body-contact-views-v1-20261023'
CAP='government-xl-nam-cheong-fu-yun-after-island-current-v1-20261023-runtime'
ROLES='government-xl-nam-cheong-fu-yun-contact-roles-v1-20261023'
ATTRIBUTION='government-xl-nam-cheong-fu-yun-compound-envelope-attribution-v1-20261023'


def minor_plane_extent_squared(source,plane):
    a=[[F(float(x)) for x in p] for p in source];b=[[F(float(x)) for x in p] for p in plane]
    u=[b[1][i]-b[0][i] for i in range(3)];v=[b[2][i]-b[0][i] for i in range(3)]
    normal=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
    norm2=sum(x*x for x in normal);assert norm2>0
    values=[sum(normal[i]*(p[i]-b[0][i]) for i in range(3)) for p in a]
    low,high=min(values),max(values)
    reach=min(-low,high) if low<0<high else F(0)
    return dict(exactSignedPlaneNumerators=list(map(str,values)),exactPlaneNormalSquared=str(norm2),exactMinorPlaneSideExtentSquaredM2=str(reach*reach/norm2),strictPlaneCrossing=low<0<high)


def main():
    base=ROOT/'docs/astra-city/government-import';doc=base/BATCH
    assert not doc.exists()
    refs,pins=[Path(__file__)],{}
    for name in [CAP,ROLES,ATTRIBUTION]:
        _,pins[name]=authenticate(base/name);refs.append(base/name/'result.json')
    def take(name,path):
        assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    selection=take(CAP,base/CAP/'selection.json.gz');selected={r['uid']:r for r in selection['rows']}
    triangles={};sources={}
    for uid in ['landsd/268867:0','landsd/270874:0']:
        row=selected[uid];path=ROOT/row['candidate']['path'];raw=path.read_bytes();assert digest(raw)==row['sourceSHA256'];refs.append(path);sources[uid]=row['sourceSHA256'];triangles[uid]=decode_original_world_triangles(raw)
    nam,fu=triangles['landsd/268867:0'],triangles['landsd/270874:0']
    contacts=[r for r in take(ROLES,base/ROLES/'classified-contacts.json.gz') if r['contactRole']=='transverse-surface-crossing']
    assert len(contacts)==22
    attribution=take(ATTRIBUTION,base/ATTRIBUTION/'summary.json')
    assert attribution['sourceSHA256ByUid']==sources
    proofs=[]
    for c in contacts:
        a,b=nam[c['sourceFaceA']],fu[c['sourceFaceB']]
        ab,ba=minor_plane_extent_squared(a,b),minor_plane_extent_squared(b,a)
        proofs.append(dict(sourceFaceA=c['sourceFaceA'],sourceFaceB=c['sourceFaceB'],namAgainstFuPlane=ab,fuAgainstNamPlane=ba,minimumBidirectionalMinorPlaneExtentSquaredM2=str(min(F(ab['exactMinorPlaneSideExtentSquaredM2']),F(ba['exactMinorPlaneSideExtentSquaredM2']))),rawExactContact=c,acceptableContact=False))
    save(doc/'original-crossing-plane-extents.json.gz',proofs)
    views=[]
    for label,ids in [('base-cap-contacts',[8440,8538]),('lower-detail-interface',[10131])]:
        records=[c for c in contacts if c['sourceFaceA'] in ids]
        points=np.asarray([[float(F(x)) for x in p] for c in records for p in c['exactPoints']])
        lo,hi=points.min(0)-[2,1,2],points.max(0)+[2,5 if label=='lower-detail-interface' else 2,2]
        center=(lo+hi)/2
        aa=np.flatnonzero(np.all(nam.max(1)>=lo,axis=1)&np.all(nam.min(1)<=hi,axis=1))
        bb=np.flatnonzero(np.all(fu.max(1)>=lo,axis=1)&np.all(fu.min(1)<=hi,axis=1))
        for direction,az in [('southwest',-125),('northeast',55)]:
            fig=plt.figure(figsize=(10,8));ax=fig.add_subplot(projection='3d')
            for mesh,faceids,color,alpha in [(nam,aa,'#aab6c0',.14),(fu,bb,'#7398c4',.16),(nam,sorted({c['sourceFaceA'] for c in records}),'#e8a12c',.75),(fu,sorted({c['sourceFaceB'] for c in records}),'#3274a3',.65)]:
                local=(mesh[faceids]-center)[:,:,[0,2,1]];ax.add_collection3d(Poly3DCollection(local,facecolor=color,edgecolor='none',alpha=alpha))
            local=(points-center)[:,[0,2,1]];ax.scatter(local[:,0],local[:,1],local[:,2],s=8,c='#b61522',depthshade=False)
            ax.set_xlim(lo[0]-center[0],hi[0]-center[0]);ax.set_ylim(lo[2]-center[2],hi[2]-center[2]);ax.set_zlim(lo[1]-center[1],hi[1]-center[1]);ax.set_box_aspect((hi-lo)[[0,2,1]]);ax.view_init(elev=25,azim=az)
            ax.set(xlabel='Local east(m)',ylabel='LocalZ(m)',zlabel='Localheight(m)',title=label+'; orange=Nam,blue=FuYun,red=exact intersections')
            fig.tight_layout();path=doc/(label+'-'+direction+'.png');path.parent.mkdir(parents=True,exist_ok=True);fig.savefig(path,dpi=135);plt.close(fig)
            views.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),label=label,contextNamFaceIds=list(map(int,aa)),contextFuFaceIds=list(map(int,bb))))
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    summary=dict(uids=sorted(sources),sourceSHA256ByUid=sources,rows=proofs,views=views,currentManifestSHA256=selection['manifestSHA256'],sourceGeometryChanges=0,physicalAccepted=False,installationApproved=False,qualification='All22originaltransversecontacts retained. Exact plane-side extents are geometric descriptors, not a collision tolerance or support approval. Images retain source faces and explicitly clip context; no architectural role or acceptance inferred from appearance alone. Compoundminimumprovider attribution remains unchanged.')
    save(doc/'summary.json',summary)
    refs.append(HERE/'exact_packed_world_geometry_20261009.py')
    module('nam_pair_body_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-pair-crossing-extents-and-body-context-views',refs,summary)


if __name__=='__main__':
    main()
