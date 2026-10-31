"""Classify every source facet under a peer-building envelope, separate from earth.

Read-only diagnostic, not permission to edit faces or override compound checks.
"""
import argparse
from pathlib import Path
import numpy as np
import shapely
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','runtime','attributes','uid']:ap.add_argument('--'+key,required=True)
    ap.add_argument('--peer',action='append',required=True);a=ap.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch
    assert a.batch.startswith('government-xl-')and '/'not in a.batch and not out.exists()
    assert len(a.peer)==len(set(a.peer))and a.uid not in a.peer
    refs=[Path(__file__)];pins={}
    def take(n,p):
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    selected=take(a.runtime,base/a.runtime/'selection.json.gz');rows={r['uid']:r for r in selected['rows']}
    runtime=take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz');captured={r['uid']:r for r in runtime['rows']}
    attributes=take(a.attributes,base/a.attributes/'attributes.json.gz');attrs={r['uid']:r for r in attributes['rows']};assert attributes['startEndAllInputsVerified']
    worlds={}
    for uid in [a.uid,*a.peer]:
        r=rows[uid];p=ROOT/r['candidate']['path'];raw=p.read_bytes();assert digest(raw)==r['sourceSHA256']==attrs[uid]['sourceSHA256'];refs.append(p)
        ix=np.asarray(attrs[uid]['completeOriginalIndex']).reshape(-1,3)
        worlds[uid]=dict(original=decode_original_world_triangles(raw),**{m:np.asarray(attrs[uid][k]).reshape(-1,3)[ix]for m,k in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]})
    kernel=module('peer_envelope_kernel',HERE/'xl-final-script-pass.py');ground=np.asarray(captured[a.uid]['drawnGroundGeometry']).reshape(-1,3,3)
    b=rows[a.uid]['source']['building'];footprint=shapely.Polygon(b['rings'][0],b['rings'][1:]);results=[]
    for mode,tri in worlds[a.uid].items():
        peers=np.concatenate([worlds[u][mode]for u in a.peer]);all_ground=np.concatenate([ground,peers]);lo=tri.min((0,1));hi=tri.max((0,1))
        def heights(values):
            mask=(values[:,:,0].max(1)>=lo[0]-1)&(values[:,:,0].min(1)<=hi[0]+1)&(values[:,:,2].max(1)>=lo[2]-1)&(values[:,:,2].min(1)<=hi[2]+1)
            values=values[mask];polys=shapely.polygons(values[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;values=values[valid];polys=polys[valid]
            points=np.concatenate([tri,tri.mean(1)[:,None,:]],axis=1)
            ys=kernel.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),values,shapely.STRtree(polys)).reshape(-1,4)
            return points[:,:,1]-ys
        earthgap=heights(ground);compoundgap=heights(all_ground);buried=np.isfinite(compoundgap).all(1)&(compoundgap<-.5).all(1)
        cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);area=np.linalg.norm(cross,axis=1)/2;up=cross[:,1]>.25*np.linalg.norm(cross,axis=1)
        foundation=kernel.foundation_context(tri,all_ground,footprint);assert int(buried.sum())==foundation['fullyBuriedTriangles']and int((buried&up).sum())==foundation['fullyBuriedUpwardTriangles']
        details=[]
        for i in np.flatnonzero(buried):
            details.append(dict(sourceFace=int(i),vertices=tri[i].tolist(),areaM2=float(area[i]),upward=bool(up[i]),earthGapsM=earthgap[i].tolist(),peerEnvelopeGapsM=compoundgap[i].tolist(),heightRangeM=[float(tri[i,:,1].min()),float(tri[i,:,1].max())],distanceBelowHighestOriginalSourceVertexM=float(tri[:,:,1].max()-tri[i,:,1].max())))
        save(out/(mode+'-facets.json.gz'),dict(rows=details,completeSourceFaces=len(tri),sourceWorldSHA256=digest(tri.tobytes()),currentDrawnEarthSHA256=digest(ground.tobytes()),completeCompoundFoundation=foundation))
        results.append(dict(mode=mode,completeSourceFaces=len(tri),peerEnvelopeBuriedFaces=np.flatnonzero(buried).tolist(),peerEnvelopeUpwardFaces=np.flatnonzero(buried&up).tolist(),allPeerEnvelopeBuriedFacesClearOfEarth=bool(np.all(earthgap[buried]>=-.5)),compoundFoundation=foundation))
        if mode=='original':
            centre=tri.reshape(-1,3).mean(0);t=tri-centre;q=peers-centre;fig=plt.figure(figsize=(17,8),dpi=140)
            for panel,azimuth in enumerate([-60,120],1):
                ax=fig.add_subplot(1,2,panel,projection='3d');ax.add_collection3d(Poly3DCollection(t,facecolor='#c7ccd1',edgecolor='#7d8790',linewidth=.08,alpha=.5))
                selected_ids=np.flatnonzero(buried);ax.add_collection3d(Poly3DCollection(t[selected_ids],facecolor=['#d52e2e'if up[i]else'#e5a544'for i in selected_ids],edgecolor='#5a2020',linewidth=.3,alpha=.95))
                selected=(q[:,:,0].max(1)>=t[:,:,0].min()-2)&(q[:,:,0].min(1)<=t[:,:,0].max()+2)&(q[:,:,2].max(1)>=t[:,:,2].min()-2)&(q[:,:,2].min(1)<=t[:,:,2].max()+2)
                ax.add_collection3d(Poly3DCollection(q[selected],facecolor='#6790b1',edgecolor='#367198',linewidth=.08,alpha=.055))
                lower=t.min((0,1));upper=t.max((0,1));ax.set_xlim(lower[0]-2,upper[0]+2);ax.set_ylim(lower[1]-2,upper[1]+2);ax.set_zlim(lower[2]-2,upper[2]+2);ax.set_box_aspect(np.maximum(upper-lower,1));ax.view_init(elev=20,azim=azimuth);ax.set_xlabel('X east');ax.set_ylabel('Y height');ax.set_zlabel('Z south')
            fig.suptitle(a.uid+' complete original: orange = under peer envelope; red = upward subset. Blue peer context cropped; NOT earth burial or approval.');fig.tight_layout();fig.savefig(out/'complete-source-peer-envelope-context.png');plt.close(fig)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256'];refs.append(manifest)
    result=dict(uids=[a.uid,*a.peer],sourceSHA256ByUid={u:rows[u]['sourceSHA256']for u in [a.uid,*a.peer]},rows=results,sourceGeometryChanges=0,physicalAcceptance=False,architectureReview=False,installationApproved=False,publication=False,qualification='Full canonical compound envelope and every classified original face preserved in each world. Overhead peer-building height is distinguished from actual current earth height. Diagnostic face orientation, small area or source overlap does not by itself grant architectural/support/compound/publication approval. No model or terrain edited.')
    save(out/'summary.json',result);refs.extend([HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py'])
    module('original_peer_envelope_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-source-peer-envelope-versus-actual-earth-facet-context',list(dict.fromkeys(refs)),result)


if __name__=='__main__':main()
