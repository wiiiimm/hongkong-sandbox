"""Render exact source extents for two identity reviews; no model edits or acceptance."""
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
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-three-podium-extent-context-v1-20261022';DOC=BASE/BATCH
UIDS=['landsd/277890:0','landsd/23296:0','landsd/290878:0']

def main():
    assert not DOC.exists();source=BASE/'government-xl-remaining-forty-podium-identity-v1-20261021';_,pins=authenticate(source);refs=[Path(__file__),source/'result.json']
    p=source/'selection.json.gz';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);selected=[r for r in read(p)['rows']if r['uid']in UIDS];assert len(selected)==3;results=[]
    DOC.mkdir(parents=True)
    for row in selected:
        asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']==pins[str(asset.relative_to(ROOT))];refs.append(asset)
        identity=source/row['uid'].split('/')[1]/'identity.json';assert digest(identity.read_bytes())==pins[str(identity.relative_to(ROOT))];refs.append(identity)
        tile=ROOT/'3d-viewer'/row['source']['tile'];assert digest(tile.read_bytes())==row['source']['tileSHA256'];refs.append(tile)
        tri=decode_original_world_triangles(asset.read_bytes());assert len(tri)==row['triangles'];b=row['source']['building'];foot=shapely.Polygon(b['rings'][0],b['rings'][1:]);polys=shapely.polygons(tri[:,:,[0,2]]);areas=shapely.area(polys);outside=np.zeros(len(tri),dtype=bool)
        for i,f in enumerate(tri):outside[i]=not foot.covers(shapely.MultiPoint(f[:,[0,2]]).convex_hull)
        lo,hi=tri.min((0,1)),tri.max((0,1));centre=(lo+hi)/2
        fig=plt.figure(figsize=(16,7));ax=fig.add_subplot(121,projection='3d')
        for mask,color,alpha in [(~outside,'slategray',.6),(outside,'darkorange',.8)]:
            ax.add_collection3d(Poly3DCollection((tri[mask]-centre)[:,:,[0,2,1]],facecolor=color,edgecolor='none',alpha=alpha))
        dims=np.maximum(hi-lo,1);ax.set_xlim(-dims[0]/2,dims[0]/2);ax.set_ylim(-dims[2]/2,dims[2]/2);ax.set_zlim(-dims[1]/2,dims[1]/2);ax.set_box_aspect(dims[[0,2,1]]);ax.view_init(22,-60);ax.set_title('Whole original source; orange = faces extending outside footprint')
        ax=fig.add_subplot(122)
        for geom,color in [(shapely.union_all(polys[areas>1e-10]),'darkorange'),(foot,'navy')]:
            for p in shapely.get_parts(geom):
                if p.geom_type=='Polygon':
                    x,z=p.exterior.xy;ax.plot(np.asarray(x)-centre[0],np.asarray(z)-centre[2],color=color,linewidth=1)
        ax.set_aspect('equal');ax.invert_yaxis();ax.set_title('Source projection (orange), recorded footprint (blue)');ax.set_xlabel('Local X metres');ax.set_ylabel('Local Z metres')
        fig.suptitle(b.get('name')or row['uid']);fig.tight_layout();png=DOC/(row['uid'].split('/')[1].replace(':','-')+'.png');fig.savefig(png,dpi=140);plt.close(fig)
        results.append(dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],triangles=len(tri),facesExtendingOutsideFootprint=int(outside.sum()),rawIdentityReasons=read(identity)['reasons'],image=str(png.relative_to(ROOT))))
    summary=dict(uids=UIDS,rows=results,installationApproved=False,identityReviewApproved=False,sourceGeometryChanges=0)
    save(DOC/'summary.json',summary);refs.append(HERE/'exact_packed_world_geometry_20261009.py');module('extent_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-extent-visual-context',list(dict.fromkeys(refs)),summary)
    print(summary,flush=True)

if __name__=='__main__':main()
