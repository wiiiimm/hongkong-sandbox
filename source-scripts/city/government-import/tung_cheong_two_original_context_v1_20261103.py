"""Compare two exact originals and their different GIS outlines, with no reassignment."""
import sys,uuid
from pathlib import Path
import numpy as np
import shapely
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from original_assembly_context_plot_v3_20261023 import clipped_faces
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tung-cheong-two-original-context-v1-20261103'
HIGH='government-xl-tung-cheong53799-post-inset-v1-20261103-runtime'
LOW='government-xl-tung-cheong-low223636-exact-original-recovery-v2-20261103'
PRIMARY='government-xl-tung-cheong-high-low-primary-records-v1-20261103'

def main():
    out=BASE/BATCH;lp=HERE/'local'/BATCH/'reservation.json';assert not out.exists()
    if '--owned'not in sys.argv:
        assert not lp.parent.exists();c=reservations.claim('tung-cheong-two-original-context-'+str(uuid.uuid4()),['building:landsd/53799:0','building:landsd/223636:0','native-source:a04c53795d53db1d54dd224b5d4b2b9091855f5b8525f82753a981f88bc08438/B339081144201063C0','immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease);refs=[Path(__file__)];pins={}
    def take(batch,name):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        p=BASE/batch/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    high=take(HIGH,'selection.json.gz')['rows'][0];low=take(LOW,'summary.json');assert low['viewerIdentityAssigned']is False and low['identityAccepted']is False
    paths=[ROOT/high['candidate']['path'],ROOT/low['sourceAsset']['path']];shas=[high['sourceSHA256'],low['sourceSHA256']]
    for p,h in zip(paths,shas):assert digest(p.read_bytes())==h;refs.append(p)
    a,b=[decode_original_world_triangles(p.read_bytes())for p in paths];assert len(a)==12158 and len(b)==44
    primary=take(PRIMARY,'footprints.json')['features'];assert {r['attributes']['BuildingCSUID']for r in primary}=={'3391111439T20050430','3390811442T20050430'}
    proof=exact_finite_contacts(a,list(range(len(a))),b,list(range(len(b))));assert proof['allPairsExamined']and proof['sourceFacesOmitted']==0
    save(out/'original-pair-contacts.json.gz',proof)
    polys=[shapely.union_all(shapely.polygons(t[:,:,[0,2]]))for t in [a,b]]
    tile=ROOT/'3d-viewer/city/data/tiles/-1_2.json';forms={f['uid']:f for f in read(tile)['buildings']};refs.append(tile)
    before=forms['landsd/223636:0'];foot=shapely.Polygon(before['rings'][0],before['rings'][1:]);fresh=next(r for r in primary if r['attributes']['BuildingCSUID']==before['buildingCSUID']);current=shapely.Polygon([(x-834500,816500-y)for x,y in fresh['geometry']['rings'][0]])
    lo=b.min((0,1))-[4,1,4];hi=b.max((0,1))+[4,5,4];planes=[(i,float(lo[i]),True)for i in range(3)]+[(i,float(hi[i]),False)for i in range(3)]
    fig=plt.figure(figsize=(16,12),layout='constrained')
    ax=fig.add_subplot(2,2,1)
    for tri,color in [(a,'#83a9be'),(b,'#dd7a23')]:ax.add_collection(PolyCollection(tri[:,:,[0,2]],facecolors=color,alpha=.35,linewidth=0))
    for uid,color in [('landsd/53799:0','#445568'),('landsd/223636:0','#a40c2a')]:
        xy=np.asarray(forms[uid]['rings'][0]);ax.plot(xy[:,0],xy[:,1],color=color,label='cached '+uid)
    xy=np.asarray(current.exterior.coords);ax.plot(xy[:,0],xy[:,1],'k--',label='fresh low footprint');ax.autoscale();ax.set_aspect('equal');ax.legend(fontsize=8);ax.set_title('Complete high original blue / low original orange / GIS outlines')
    ax=fig.add_subplot(2,2,2)
    for tri,color in [(a,'#83a9be'),(b,'#dd7a23')]:ax.add_collection(PolyCollection(tri[:,:,[0,2]],facecolors=color,alpha=.35,linewidth=0))
    for shape,color in [(foot,'#a40c2a'),(current,'#111111')]:xy=np.asarray(shape.exterior.coords);ax.plot(xy[:,0],xy[:,1],color=color)
    ax.set(xlim=(lo[0],hi[0]),ylim=(lo[2],hi[2]),title='Low-component plan close-up; display limits only');ax.set_aspect('equal')
    for n,azimuth in enumerate([30,210]):
        ax=fig.add_subplot(2,2,3+n,projection='3d')
        for tri,color in [(a,'#83a9be'),(b,'#dd7a23')]:
            shown=clipped_faces(tri,planes)
            if len(shown):ax.add_collection3d(Poly3DCollection((shown-lo)[:,:,[0,2,1]],facecolors=color,edgecolors='#35424c',linewidth=.15,alpha=.8))
        size=(hi-lo)[[0,2,1]];ax.set(xlim=(0,size[0]),ylim=(0,size[1]),zlim=(0,size[2]),title='Exact two originals: base crop, no source edits');ax.set_box_aspect(size.copy());ax.view_init(24,azimuth)
    image=out/'two-originals-and-gis-context.png';fig.savefig(image,dpi=130);plt.close(fig);refs.append(image)
    result=dict(uids=['landsd/53799:0'],unmatchedSourceKey=low['nativeCacheKey']+'/'+low['model']['modelId'],unmatchedViewerUid=None,proposedLowViewerUid='landsd/223636:0',viewerIdentityAssigned=False,sourceSHA256s=shas,completeOriginalFaces=[len(a),len(b)],originalWorldSHA256s=[digest(t.astype('<f8').tobytes())for t in [a,b]],pairFiniteContacts=len(proof['contacts']),pairPositiveSurfaceContacts=sum(c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2 for c in proof['contacts']),pairAreaContacts=sum(c['dimension']==2 for c in proof['contacts']),lowOriginalProjectionM2=polys[1].area,lowProjectionInsideHighProjectionM2=polys[1].intersection(polys[0]).area,lowProjectionInsideCachedLowFootprintM2=polys[1].intersection(foot).area,lowProjectionInsideFreshLowFootprintM2=polys[1].intersection(current).area,freshProviderObjectIds={r['attributes']['BuildingCSUID']:r['attributes']['OBJECTID']for r in primary},cachedLowViewerUid=before['uid'],image=dict(path=str(image.relative_to(ROOT)),sha256=digest(image.read_bytes())),sourceGeometryChanges=0,sourcePoseChanges=0,identityAccepted=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Original coordinate stream only: exact complete pair geometry and raw contacts, not all-world acceptance. The low source remains unmatched; different current provider OBJECTIDs remain explicit and never replace viewer keys. Complete indexed originals supply all plots; clipping affects display only. No source ownership, common-structure relationship or collision acceptance is inferred.')
    save(out/'summary.json',result);assert reservations.owns(lease)
    refs.extend([HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_finite_triangle_contacts_20261010.py',HERE/'original_assembly_context_plot_v3_20261023.py'])
    module('tung_cheong_two_original_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-two-original-current-gis-context-only',refs,result)
    print({k:result[k]for k in ['pairFiniteContacts','pairPositiveSurfaceContacts','pairAreaContacts','lowOriginalProjectionM2','lowProjectionInsideHighProjectionM2','lowProjectionInsideFreshLowFootprintM2']},flush=True)
if __name__=='__main__':main()
