"""Plot complete unchanged Island Industrial originals and recorded footprints."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from shapely.geometry import Polygon, MultiPoint
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    base=ROOT/'docs/astra-city/government-import'
    batch='government-xl-island-industrial-source-views-v1-20261023'
    out=base/batch
    assert not out.exists()
    names=['government-xl-all-200-original-terrain-batch-v2-20261022','government-xl-island-industrial-podium-acquire-v1-20261023','government-xl-island-industrial-contact-roles-v1-20261023']
    refs=[Path(__file__)];pins={}
    for name in names:
        _,q=authenticate(base/name);pins.update(q);refs.append(base/name/'result.json')
    def take(path):
        assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    owner=next(r for r in take(base/names[0]/'selection.json.gz')['rows']if r['uid']=='landsd/20270:0')
    podium=take(base/names[1]/'summary.json')['rows'][0]
    roles=take(base/names[2]/'summary.json')
    tri=[]
    for path,sha in [(owner['candidate']['path'],owner['sourceSHA256']),(podium['asset']['path'],podium['sourceSHA256'])]:
        p=ROOT/path;raw=p.read_bytes();assert digest(raw)==sha;refs.append(p);tri.append(decode_original_world_triangles(raw))
    assert [len(t)for t in tri]==[11166,537]
    forms=[owner['source']['building'],podium['currentForm']]
    alltri=np.concatenate(tri);lo=alltri.min((0,1));hi=alltri.max((0,1));center=(lo+hi)/2
    colors=['#6d9eb8','#d38251'];out.mkdir()
    fig=plt.figure(figsize=(15,8),layout='constrained')
    for i,angle in enumerate([35,215]):
        ax=fig.add_subplot(1,2,i+1,projection='3d')
        faces=np.concatenate([t[:,:,[0,2,1]]-[center[0],center[2],0]for t in tri])
        ax.add_collection3d(Poly3DCollection(faces,facecolors=[colors[0]]*len(tri[0])+[colors[1]]*len(tri[1]),edgecolor='none'))
        ax.set(xlim=(lo[0]-center[0]-1,hi[0]-center[0]+1),ylim=(lo[2]-center[2]-1,hi[2]-center[2]+1),zlim=(lo[1]-1,hi[1]+1),xlabel='Local east (m)',ylabel='Viewer Z (m)',zlabel='HKPD height (m)')
        ax.set_box_aspect((hi[0]-lo[0]+2,hi[2]-lo[2]+2,hi[1]-lo[1]+2));ax.view_init(elev=24,azim=angle)
    fig.suptitle('Complete unchanged originals: tower blue (11,166 faces), podium candidate orange (537 faces)')
    fig.savefig(out/'complete-originals.png',dpi=150);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(13,7),layout='constrained')
    for i,ax in enumerate(axes):
        projection=shapely.union_all([MultiPoint(f[:,[0,2]]).convex_hull for f in tri[i]])
        shapes=list(projection.geoms)if hasattr(projection,'geoms')else[projection]
        for shape in shapes:
            if shape.geom_type=='Polygon':
                q=np.asarray(shape.exterior.coords);ax.fill(q[:,0]-center[0],q[:,1]-center[2],color=colors[i],alpha=.6)
                for ring in shape.interiors:
                    q=np.asarray(ring.coords);ax.fill(q[:,0]-center[0],q[:,1]-center[2],color='white')
        for j,form in enumerate(forms):
            q=np.asarray(form['rings'][0]);ax.plot(q[:,0]-center[0],q[:,1]-center[2],color=['navy','darkred'][j],label=form['uid'])
        ax.set_title(['Tower source projection','Podium candidate projection'][i]);ax.set_aspect('equal');ax.legend();ax.set_xlabel('Local east (m)');ax.set_ylabel('Viewer Z (m)')
    fig.suptitle('Recorded footprint outlines and exact source projections; no identity/support approval')
    fig.savefig(out/'footprint-projections.png',dpi=150);plt.close(fig)
    result=dict(uids=roles['uids'],sourceSHA256ByUid=roles['sourceSHA256ByUid'],completeOriginalFaces=len(alltri),sourceGeometryChanges=0,installationApproved=False,qualification='Source-only full unchanged face render and footprint diagnostic. No runtime scene, terrain, collision or support approval; transverse crossings remain unresolved.')
    save(out/'summary.json',result);refs.append(HERE/'exact_packed_world_geometry_20261009.py')
    module('island_source_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'complete-original-source-visual-diagnostic',refs,result)


if __name__=='__main__':main()
