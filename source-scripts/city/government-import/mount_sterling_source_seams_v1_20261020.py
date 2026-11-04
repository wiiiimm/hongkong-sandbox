"""Private bounded Float32 seam fill using original government planes only."""
from pathlib import Path
import copy
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from native_patch_resolution import _faces
from source_surface_inset import plane,lift
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-mount-sterling-source-seams-v1-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;CONTRACT=BASE/'government-xl-mount-sterling-replacement-contract-v1-20261020';GROUND=BASE/'government-xl-mount-sterling-adjoining-ground-v1-20261020'
def main():
    assert not DOC.exists() and not LOCAL.exists();refs=[Path(__file__),HERE/'native_patch_resolution.py',HERE/'source_surface_inset.py'];pins={}
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for folder in (CONTRACT,GROUND):
            r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256'] for e in r['evidenceRefs']}
    def take(folder,p):
        assert digest(p.read_bytes())==pins[folder][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    rows=take(CONTRACT,CONTRACT/'terrain-candidates.json');old=ROOT/rows[0]['path'];p=take(CONTRACT,old);candidate=copy.deepcopy(p);region=shapely.from_wkt(p['nativeMesh']['source']['mountSterlingPrivateInset']['regionWKT']);ground=np.asarray(take(GROUND,HERE/'local'/GROUND.name/'289787:0-ground.json.gz')['completeAdjoiningTerrain']);polys=shapely.polygons(ground[:,:,[0,2]]);tree=shapely.STRtree(polys);passes=[];lineage=[]
    def gaps():
        faces=_faces(candidate);ps=shapely.polygons(faces[:,:,[0,2]]);ids=shapely.STRtree(ps).query(region,predicate='intersects');return region.difference(shapely.union_all(ps[ids]))
    before=gaps();assert 0<before.area<.02
    for step in range(3):
        gap=gaps();additions=[]
        for i in tree.query(gap,predicate='intersects'):
            if polys[i].area<=1e-10:continue
            cut=polys[i].intersection(gap)
            for f in lift(cut,plane(ground[i])):additions.append(f);lineage.append(dict(passIndex=step,originalTerrainFace=int(i),vertices=f.tolist()))
        if not additions:break
        offset=len(candidate['nativeMesh']['position'])//3;candidate['nativeMesh']['position'].extend(np.asarray(additions).reshape(-1).tolist());candidate['nativeMesh']['index'].extend(range(offset,offset+len(additions)*3));after=gaps();passes.append(dict(passIndex=step,beforeAreaM2=float(gap.area),afterAreaM2=float(after.area),addedFaces=len(additions)))
        if after.area>=gap.area-1e-10 or after.area<1e-8:break
    assert candidate['nativeMesh']['position'][:len(p['nativeMesh']['position'])]==p['nativeMesh']['position'];assert candidate['nativeMesh']['index'][:len(p['nativeMesh']['index'])]==p['nativeMesh']['index']
    candidate['nativeMesh']['source']['mountSterlingSourceSeamFill']=dict(policy='Only exact government planes in measured private Float32 gaps; no parent/model height inference.',passes=passes)
    out=LOCAL/'candidate-terrain.json';save(out,candidate);refs.append(out);rows[0].update(path=str(out.relative_to(ROOT)),sha256=digest(out.read_bytes()));save(DOC/'terrain-candidates.json',rows);save(DOC/'lineage.json.gz',dict(rows=lineage));summary=dict(uids=['landsd/289787:0'],passes=passes,remainingGapAreaM2=float(gaps().area),existingFacesUnchanged=True,installationApproved=False,sourceGeometryChanges=0);save(DOC/'summary.json',summary)
    module('mount_sterling_source_seam_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-original-plane-numerical-seams',refs,summary);print(summary,flush=True)
if __name__=='__main__':main()
