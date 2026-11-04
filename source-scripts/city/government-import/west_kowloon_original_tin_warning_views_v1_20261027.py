"""Display the two exact original-TIN warning groups, without modifying any geometry."""
from pathlib import Path
import uuid
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_assembly_context_plot_v3_20261023 import clipped_faces


def main():
    batch='government-xl-west-kowloon-north-original-tin-warning-views-v1-20261027'
    uid='landsd/182397:0'
    base=ROOT/'docs/astra-city/government-import';out=base/batch
    assert not out.exists()
    pins={};refs=[Path(__file__),HERE/'original_assembly_context_plot_v3_20261023.py',HERE/'exact_packed_world_geometry_20261009.py']
    def take(name,path):
        if name not in pins:
            pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
        assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    warnings=take('government-xl-west-kowloon-north-original-tin-failing-facets-v1-20261027',base/'government-xl-west-kowloon-north-original-tin-failing-facets-v1-20261027/summary.json')
    runtime='government-xl-after-dragon-next-five-ground-v1-20261026'
    row=next(r for r in take(runtime,base/runtime/'selection.json.gz')['rows']if r['uid']==uid)
    asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==warnings['sourceSHA256'];refs.append(asset)
    tri=decode_original_world_triangles(asset.read_bytes())
    name='government-xl-after-dragon-next-five-west-kowloon-wide-terrain-v1-20261026'
    ground=np.asarray(take(name,HERE/'local'/name/'original-terrain.json.gz')['triangles'],float)
    assert digest(tri.astype('<f8').tobytes())==warnings['sourceWorldSHA256']
    assert digest(ground.astype('<f8').tobytes())==warnings['originalTerrainSHA256']
    claim=reservations.claim(batch+'-'+str(uuid.uuid4()),['building:'+uid,'original-compute:'+batch],batch=batch,ttl=1800);assert claim['ok'];lease=claim['reservation'];exports=[]
    try:
        out.mkdir()
        ids=[r['sourceFace']for r in warnings['rows']]
        fig,ax=plt.subplots(figsize=(10,10),layout='constrained')
        from matplotlib.collections import PolyCollection
        lo=tri[:,:,[0,2]].min((0,1))
        ax.add_collection(PolyCollection(tri[:,:,[0,2]]-lo,facecolors='#a3aeb8',edgecolors='#72808c',linewidths=.1,alpha=.25))
        ax.add_collection(PolyCollection(tri[ids][:,:,[0,2]]-lo,facecolors='#cf3428',edgecolors='#9d2219',linewidths=.7))
        rings=row['source']['building']['rings']
        for ring in rings:
            points=np.asarray(ring)-lo;ax.plot(points[:,0],points[:,1],color='#202020',linewidth=1)
        ax.autoscale();ax.set_aspect('equal');ax.invert_yaxis();ax.set(xlabel='Viewer east offset m',ylabel='Viewer Z offset m',title='North Tower original source; red = exact35 original-TIN warnings\nBlack = current North Tower footprint. Display only; no acceptance.')
        path=out/'whole-source-warning-plan.png';fig.savefig(path,dpi=140);plt.close(fig);exports.append(path)
        for i,c in enumerate(warnings['components'],1):
            assert reservations.heartbeat(lease)['ok']
            selected=c['sourceFaces'];pts=tri[selected].reshape(-1,3)
            low,high=pts.min(0)-[2,1,2],pts.max(0)+[2,6,2]
            planes=[(k,float(low[k]),True)for k in range(3)]+[(k,float(high[k]),False)for k in range(3)]
            fig=plt.figure(figsize=(15,7),layout='constrained')
            for k,angle in enumerate((35,215),1):
                ax=fig.add_subplot(1,2,k,projection='3d')
                for mesh,color,alpha in ((tri,'#64748b',.12),(tri[selected],'#d04729',.95)):
                    mask=np.all(mesh.max(1)>=low,axis=1)&np.all(mesh.min(1)<=high,axis=1)
                    polys=clipped_faces(mesh[mask],planes)
                    if len(polys):ax.add_collection3d(Poly3DCollection((polys-low)[:,:,[0,2,1]],facecolors=color,edgecolors=color,alpha=alpha,linewidth=.35))
                mask=np.all(ground.max(1)>=low,axis=1)&np.all(ground.min(1)<=high,axis=1)
                polys=clipped_faces(ground[mask],planes)
                if len(polys):ax.add_collection3d(Line3DCollection([np.vstack((v,v[:1]))for v in (polys-low)[:,:,[0,2,1]]],colors='#16834a',linewidth=.7))
                for j in selected:
                    p=tri[j].mean(0)-low;ax.text(p[0],p[2],p[1],str(j),fontsize=6)
                size=(high-low)[[0,2,1]];ax.set(xlim=(0,size[0]),ylim=(0,size[1]),zlim=(0,size[2]),xlabel='East offset m',ylabel='Viewer Z offset m',zlabel='Height offset m');ax.set_box_aspect(size);ax.view_init(24,angle)
            fig.suptitle(f'{uid}: original-TIN warning component{i}; {len(selected)} source facets\nRed=original warning facets; green=unaltered government TIN; grey=original source context. Display crops only.')
            path=out/f'original-tin-group-{i}.png';fig.savefig(path,dpi=140);plt.close(fig);exports.append(path)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
    refs+=exports
    result=dict(uids=[uid],sourceSHA256=warnings['sourceSHA256'],sourceWorldSHA256=warnings['sourceWorldSHA256'],originalTerrainSHA256=warnings['originalTerrainSHA256'],sourceFaces=ids,components=warnings['components'],exports=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in exports],sourceGeometryChanges=0,terrainGeometryChanges=0,actualRendererAcceptance=False,imagesActuallyViewed=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Complete two warning-group display and whole-source locating plan, using authenticated original government TIN, never the historic viewer ground. Context crops affect diagnostic display only. No geometry, terrain, role classification or acceptance changes.')
    save(out/'summary.json',result)
    module('original_tin_warning_plot_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-original-tin-warning-groups-and-location-plan',refs,result)
    print(dict(exports=len(exports),facets=len(ids)),flush=True)

if __name__=='__main__':main()
