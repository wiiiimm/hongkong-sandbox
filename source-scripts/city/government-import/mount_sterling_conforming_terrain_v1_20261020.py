"""Split shared terrain edges before Float32 packing; keep original face planes."""
from pathlib import Path
import copy
import numpy as np,shapely
from shapely.geometry import Polygon,LineString
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from source_surface_inset import plane
from native_patch_resolution import _faces
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-mount-sterling-conforming-terrain-v1-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;CONTRACT=BASE/'government-xl-mount-sterling-replacement-contract-v1-20261020'
def main():
    assert not DOC.exists() and not LOCAL.exists();r=read(CONTRACT/'result.json');refs=[Path(__file__),CONTRACT/'result.json',HERE/'source_surface_inset.py',HERE/'native_patch_resolution.py'];pins={e['path']:e['sha256'] for e in r['evidenceRefs']}
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
    def take(p):
        assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
    rows=take(CONTRACT/'terrain-candidates.json');parent=take(ROOT/rows[0]['path']);candidate=copy.deepcopy(parent);vertices=np.asarray(parent['nativeMesh']['position']).reshape(-1,3);faces=vertices[np.asarray(parent['nativeMesh']['index']).reshape(-1,3)];points=np.unique(vertices[:,[0,2]],axis=0);tree=shapely.STRtree(shapely.points(points));region=shapely.from_wkt(parent['nativeMesh']['source']['mountSterlingPrivateInset']['regionWKT']).buffer(.002);output=[];changes=[]
    for i,face in enumerate(faces):
        poly=Polygon(face[:,[0,2]])
        if poly.area<=1e-10 or not poly.intersects(region):output.append(face);continue
        boundary=[];added=0
        for a,b in zip(face[:,[0,2]],np.roll(face[:,[0,2]],-1,axis=0)):
            d=b-a;dd=d@d
            if dd==0:continue
            ids=tree.query(LineString([a,b]).buffer(1e-7),predicate='intersects');part=points[ids];t=(part-a)@d/dd;distance=np.abs((part[:,0]-a[0])*d[1]-(part[:,1]-a[1])*d[0])/np.sqrt(dd);valid=(t>1e-9)&(t<1-1e-9)&(distance<1e-7);part=part[valid];t=t[valid];boundary.append(a)
            for p in part[np.argsort(t)]:boundary.append(p);added+=1
        if not added:output.append(face);continue
        constrained=Polygon(boundary);assert constrained.is_valid and abs(constrained.area-poly.area)<1e-6
        coefficient=plane(face);new=[]
        for triangle in shapely.get_parts(shapely.constrained_delaunay_triangles(constrained)):
            if triangle.area<=1e-12:continue
            xz=np.asarray(triangle.exterior.coords[:3]);new.append(np.column_stack([xz[:,0],xz@coefficient[:2]+coefficient[2],xz[:,1]]))
        assert abs(sum(Polygon(t[:,[0,2]]).area for t in new)-poly.area)<1e-6
        output.extend(new);changes.append(dict(face=i,addedBoundaryPoints=added,outputFaces=len(new),projectedAreaErrorM2=float(constrained.area-poly.area)))
    candidate['nativeMesh']['position']=np.asarray(output).reshape(-1).tolist();candidate['nativeMesh']['index']=list(range(len(output)*3));candidate['nativeMesh']['source']['mountSterlingConformingEdges']=dict(policy='Split shared exact source/parent plane edges before Float32 packing. No building geometry changes.',changedFaces=len(changes))
    packed=_faces(candidate);ps=shapely.polygons(packed[:,:,[0,2]]);point=shapely.Point(-2238.51123046875,-5589.798828125);covered=np.flatnonzero(shapely.covers(ps,point)).tolist();out=LOCAL/'candidate-terrain.json';save(out,candidate);refs.append(out);rows[0].update(path=str(out.relative_to(ROOT)),sha256=digest(out.read_bytes()));save(DOC/'terrain-candidates.json',rows);save(DOC/'face-changes.json.gz',dict(rows=changes));summary=dict(uids=['landsd/289787:0'],originalCandidateFaces=len(faces),candidateFaces=len(output),splitFaces=len(changes),missingSampleCovered=bool(covered),coveringFaces=covered,maximumProjectedAreaErrorM2=max(abs(r['projectedAreaErrorM2']) for r in changes),sourceGeometryChanges=0,installationApproved=False);save(DOC/'summary.json',summary);module('mount_sterling_conforming_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-exact-plane-shared-edge-conformity',refs,summary);print(summary,flush=True)
if __name__=='__main__':main()
