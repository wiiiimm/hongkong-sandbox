"""Inspect exact original neighbour interfaces and the remaining footprint strip."""
from pathlib import Path
from fractions import Fraction
from collections import Counter
import numpy as np,shapely
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_primitive_contacts_v1 import exact_component_contacts_with_primitives
from exact_original_shell_intersections_20261009 import rational_face
from exact_contact_role_context_v1_20261023 import contact_role


def band_bound(shape,boundary):
    if shape.is_empty:return dict(lowerM=0,upperM=0)
    lo,hi=0.,1.
    while not shape.difference(boundary.buffer(hi,quad_segs=32)).is_empty:hi*=2;assert hi<100
    for _ in range(30):
        mid=(lo+hi)/2
        if shape.difference(boundary.buffer(mid,quad_segs=32)).is_empty:hi=mid
        else:lo=mid
    return dict(lowerM=lo,upperM=hi,method='Whole finite overlap polygon covered by an inscribed Euclidean boundary-band polygon; no sampling or source geometry buffer credit.')


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-island-cheong-shing-full-boundary-context-v1-20261023';out=base/batch;assert not out.exists();refs=[Path(__file__)];cache={}
    def take(batch,name):
        if batch not in cache:cache[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        p=base/batch/name;assert digest(p.read_bytes())==cache[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    runtime='government-xl-island-cheong-shing-four-original-runtime-v2-20261023';selected=take(runtime,'selection.json.gz');family=take('government-xl-island-industrial-complete-family-coverage-v1-20261023','summary.json');assert family['familyProjectionQualified']
    current=take('government-xl-island-industrial-paired-current-neighbours-v1-20261023','neighbour-inputs.json.gz');forms={r['building']['uid']:r['building']for r in current['rows']};assert len(forms)==774
    triangles={};polygons={};rows={r['uid']:r for r in selected['rows']};uids=['landsd/20270:0','landsd/159422:0','landsd/274231:0','landsd/269430:0']
    for uid in uids:
        r=rows[uid];assert forms[uid]==r['source']['building'];p=ROOT/r['candidate']['path'];raw=p.read_bytes();assert digest(raw)==r['sourceSHA256'];refs.append(p);triangles[uid]=decode_original_world_triangles(raw);f=forms[uid];polygons[uid]=shapely.Polygon(f['rings'][0],f['rings'][1:])
    pairs=[]
    for uid in uids[:2]:
        a,b=triangles[uid],triangles['landsd/269430:0'];proof=exact_component_contacts_with_primitives(a,range(len(a)),b,range(len(b)),maximum_pairs=1000000);assert proof['allPairsExamined'];classified=[]
        for c in proof['contacts']:
            pts=[tuple(Fraction(v)for v in p)for p in c['exactPoints']];faces=[rational_face(a[c['sourceFaceA']]),rational_face(b[c['sourceFaceB']])];classified.append(dict(c,role=contact_role(*faces,pts,c['dimension'],c['primitiveDimensions'])))
        save(out/(uid.replace('/','-').replace(':','-')+'-complete-contacts.json.gz'),dict(**proof,classified=classified));ys=[float(Fraction(p[1]))for c in classified for p in c['exactPoints']];pairs.append(dict(uid=uid,otherUid='landsd/269430:0',allExactPairsExamined=True,trianglePairsTested=proof['trianglePairsTested'],contacts=len(classified),roles=dict(Counter(c['role']for c in classified)),contactYRangeM=[min(ys),max(ys)]if ys else None))
    projection=shapely.union_all([shapely.MultiPoint(f[:,[0,2]]).convex_hull for uid in uids[:2]for f in triangles[uid]]);target=shapely.union_all([polygons[u]for u in uids[:2]]);other=polygons['landsd/269430:0'];overlap=projection.difference(target).intersection(other);assert overlap.area>0;foreign_band=band_bound(overlap,other.boundary);family_band=band_bound(overlap,target.boundary)
    out.mkdir(exist_ok=True);colors=['#3576a8','#df8a36','#4b9365','#9c688f'];complete=np.concatenate(list(triangles.values()));low,high=complete.min((0,1)),complete.max((0,1));center=(low+high)/2
    fig=plt.figure(figsize=(15,9),layout='constrained')
    for k,angle in enumerate([35,215]):
        ax=fig.add_subplot(1,2,k+1,projection='3d')
        for uid,color in zip(uids,colors):
            t=triangles[uid];ax.add_collection3d(Poly3DCollection(t[:,:,[0,2,1]]-[center[0],center[2],0],facecolors=color,edgecolor='none',alpha=1))
        ax.set(xlim=(low[0]-center[0]-2,high[0]-center[0]+2),ylim=(low[2]-center[2]-2,high[2]-center[2]+2),zlim=(0,high[1]+2),xlabel='Local east (m)',ylabel='Viewer Z (m)',zlabel='HKPD height (m)');ax.set_box_aspect((high[0]-low[0]+4,high[2]-low[2]+4,high[1]+2));ax.view_init(elev=22,azim=angle)
    fig.suptitle('All 13,848 unchanged original faces: K28/80 tower blue / podium orange; K42/90 tower green / podium purple\nSource-only diagnostic, no terrain, placement or architectural acceptance');fig.savefig(out/'four-complete-originals.png',dpi=150);plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,9),layout='constrained')
    for uid,color in zip(uids,colors):
        q=np.asarray(polygons[uid].exterior.coords);ax.plot(q[:,0],q[:,1],color=color,label=uid)
    for p in shapely.get_parts(overlap):
        if p.geom_type=='Polygon':
            q=np.asarray(p.exterior.coords);ax.fill(q[:,0],q[:,1],color='#d5264e',alpha=.9)
    x0,z0,x1,z1=overlap.bounds;ax.set(xlim=(x0-3,x1+3),ylim=(z0-3,z1+3),xlabel='Viewer X (m)',ylabel='Viewer Z (m)',title=f'Remaining foreign footprint overlap: {overlap.area:.6f} m²\nWhole-strip foreign-boundary distance <= {foreign_band["upperM"]:.6f} m; diagnostic only');ax.set_aspect('equal');ax.legend();fig.savefig(out/'remaining-foreign-footprint-strip.png',dpi=150);plt.close(fig)
    result=dict(uids=uids,sourceSHA256ByUid={u:rows[u]['sourceSHA256']for u in uids},rows=pairs,foreignOverlapWKT=overlap.wkt,foreignOverlapM2=float(overlap.area),foreignFootprintBoundaryDistance=foreign_band,familyFootprintBoundaryDistance=family_band,all774CurrentFormsRetained=True,completeOriginalFaces=len(complete),sourceGeometryChanges=0,identityAccepted=False,installationApproved=False,qualification='All source-original pair candidates rechecked exactly; geometric contact roles, source-only complete-face renders and entire finite footprint-overlap strip measured. Boundary bands are measurement constructs only, not acceptance/coverage tolerance. No common ownership, permitted collision, structural support, terrain or publication inference.')
    save(out/'summary.json',result);refs.extend(HERE/n for n in ['exact_packed_world_geometry_20261009.py','exact_original_primitive_contacts_v1.py','exact_original_shell_intersections_20261009.py','exact_contact_role_context_v1_20261023.py']);module('boundary_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'fresh-whole-original-neighbour-boundary-contact-visual-context',refs,result);print({k:result[k]for k in ['rows','foreignOverlapM2','foreignFootprintBoundaryDistance','familyFootprintBoundaryDistance']},flush=True)

if __name__=='__main__':main()
