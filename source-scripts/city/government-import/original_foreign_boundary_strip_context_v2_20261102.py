"""Describe full source/BASIC projection slivers including empty before contacts; no approval."""
import argparse,sys,uuid
from pathlib import Path
from fractions import Fraction
import numpy as np
import shapely
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import'
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','attributes','foreign','uid']:p.add_argument('--'+k,required=True)
    p.add_argument('--other',action='append',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args()
    assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.runtime,a.attributes,a.foreign])
    assert a.uid not in a.other and len(a.other)==len(set(a.other))
    out=BASE/a.batch;lp=HERE/'local'/(a.batch+'-lease')/'reservation.json';assert not out.exists()
    if not a.owned:
        assert not lp.parent.exists();c=reservations.claim('original-boundary-context-'+str(uuid.uuid4()),['building:'+u for u in [a.uid,*a.other]],batch=a.batch,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
    lease=read(lp);assert reservations.owns(lease);refs=[Path(__file__)];pins={}
    def take(batch,name):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=take(a.runtime,'selection.json.gz');source=next(r for r in selection['rows']if r['uid']==a.uid)
    attr=next(r for r in take(a.attributes,'attributes.json.gz')['rows']if r['uid']==a.uid);asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256']==attr['sourceSHA256'];refs.append(asset)
    ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3);basic=take(a.foreign,'basic.json');meshes={r['uid']:np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)]for r in basic['rows']}
    modes={'before-basic':meshes[a.uid],'original':decode_original_world_triangles(asset.read_bytes())}
    for mode,key in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:modes[mode]=np.asarray(attr[key]).reshape(-1,3)[ix]
    rawsummary=take(a.foreign,'summary.json');rows=[];images=[]
    for other in a.other:
        target=meshes[other];tp=shapely.union_all(shapely.polygons(target[:,:,[0,2]]));assert tp.geom_type=='Polygon'
        boundary=np.asarray(tp.exterior.coords);rawrow=next(r for r in rawsummary['rows']if r['uid']==a.uid and r['foreignUid']==other)
        for mode,tri in modes.items():
            proof=take(a.foreign,a.uid.split('/')[1]+'--'+other.split('/')[1]+'--'+mode+'.json.gz');assert proof['allPairsExamined']and proof['sourceFacesOmitted']==0
            summary=next(r for r in rawrow['modes']if r['mode']==mode);assert len(proof['contacts'])==summary['allFiniteContactPairs']and len(tri)==summary['completeSourceFaces']
            sp=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));overlap=sp.intersection(tp);coords=shapely.get_coordinates(overlap)
            strips=[]
            for left,right in zip(boundary[:-1],boundary[1:]):
                v=right-left;length=np.linalg.norm(v)
                if length==0:continue
                if not len(coords):continue
                signed=(v[0]*(coords-left)[:,1]-v[1]*(coords-left)[:,0])/length
                strips.append(dict(segment=[left.tolist(),right.tolist()],maximumAbsoluteDistanceFromSupportingLineM=float(np.abs(signed).max()),signedDistanceRangeM=[float(signed.min()),float(signed.max())]))
            strip=min(strips,key=lambda r:r['maximumAbsoluteDistanceFromSupportingLineM']) if strips else None
            points=np.asarray([[float(Fraction(z))for z in point]for c in proof['contacts']for point in c['exactPoints']],dtype=float).reshape(-1,3);assert bool(len(points))==bool(proof['contacts'])
            row=dict(uid=a.uid,foreignUid=other,mode=mode,completeSourceFaces=len(tri),completeForeignFaces=len(target),sourceWorldSHA256=digest(tri.astype('<f8').tobytes()),foreignWorldSHA256=digest(target.astype('<f8').tobytes()),projectionOverlapAreaM2=float(overlap.area),boundaryStrip=strip,overlapBounds=list(overlap.bounds) if not overlap.is_empty else [],finiteContactPairs=len(proof['contacts']),areaContactPairs=sum(c['dimension']==2 for c in proof['contacts']),contactYRangeM=[float(points[:,1].min()),float(points[:,1].max())] if len(points) else None,sourceContactFaceIds=sorted({c['sourceFaceA']for c in proof['contacts']}),collisionApproved=False)
            rows.append(row)
            if mode=='original'and len(coords):
                assert strip is not None
                fig,axes=plt.subplots(1,2,figsize=(14,6),layout='constrained')
                for ax in axes:
                    for geom,color,label in [(sp,'#347ca0','Complete original'),(tp,'#a54536','Complete BASIC')]:
                        for g in shapely.get_parts(geom):
                            xy=np.asarray(g.exterior.coords);ax.plot(xy[:,0],xy[:,1],color=color,label=label)
                    ax.scatter(coords[:,0],coords[:,1],s=8,c='#9b18ac');ax.set_aspect('equal');ax.grid(alpha=.2)
                lo,hi=coords.min(0),coords.max(0);axes[1].set_xlim(lo[0]-1,hi[0]+1);axes[1].set_ylim(lo[1]-1,hi[1]+1)
                axes[0].set_title(a.uid+' / '+other+' whole projections');axes[1].set_title('All overlap pieces / boundary strip '+format(strip['maximumAbsoluteDistanceFromSupportingLineM'],'.6f')+' m')
                fig.suptitle('Double-precision full-projection context; exact finite contacts retained separately. No placement/collision approval.')
                image=out/(other.split('/')[1].replace(':','-')+'-projection-boundary.png');image.parent.mkdir(parents=True,exist_ok=True);fig.savefig(image,dpi=140);plt.close(fig);refs.append(image);images.append(dict(path=str(image.relative_to(ROOT)),sha256=digest(image.read_bytes())))
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    for key,sha in basic['inputHashes'].items():assert digest((ROOT/key).read_bytes())==sha;refs.append(ROOT/key)
    assert reservations.owns(lease)
    result=dict(uids=[a.uid,*a.other],rows=rows,images=images,sourceSHA256=source['sourceSHA256'],currentManifestSHA256=selection['manifestSHA256'],projectionMethod='GEOS double-precision complete face union; numerical context, not rational clearance certification',rawExactContactsPreserved=True,sourceGeometryChanges=0,sourcePoseChanges=0,collisionApproved=False,identityApproved=False,installationApproved=False,publication=False)
    save(out/'summary.json',result)
    module('original_foreign_boundary_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-original-and-basic-boundary-projection-context-no-acceptance',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
