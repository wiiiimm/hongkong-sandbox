"""Validate exact private terrain lineage, highest surface and parent boundary."""
from pathlib import Path
import copy
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from source_surface_inset import plane
from native_patch_resolution import _faces

BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-mount-sterling-terrain-validation-v2-20261020'
DOC=BASE/BATCH
LOCAL=HERE/'local'/BATCH
CONFORM=BASE/'government-xl-mount-sterling-conforming-terrain-v1-20261020'
PRIVATE=BASE/'government-xl-mount-sterling-private-surface-v1-20261020'
GROUND=BASE/'government-xl-mount-sterling-adjoining-ground-v1-20261020'

def main():
    assert not DOC.exists() and not LOCAL.exists()
    refs=[Path(__file__),HERE/'source_surface_inset.py',HERE/'native_patch_resolution.py']
    pins={}
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for folder in [CONFORM,PRIVATE,GROUND]:
            receipt=read(folder/'result.json')
            assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
            refs.append(folder/'result.json')
            pins[folder]={e['path']:e['sha256'] for e in receipt['evidenceRefs']}
    def take(folder,path):
        assert digest(path.read_bytes())==pins[folder][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    rows=take(CONFORM,CONFORM/'terrain-candidates.json')
    candidatepath=ROOT/rows[0]['path']
    candidate=take(CONFORM,candidatepath)
    changes=take(CONFORM,CONFORM/'face-changes.json.gz')['rows']
    parentpath=ROOT/'3d-viewer'/rows[0]['replaces']['url']
    assert digest(parentpath.read_bytes())==rows[0]['replaces']['sha256']
    refs.append(parentpath)
    parent=_faces(read(parentpath))
    originalpath=HERE/'local'/PRIVATE.name/'candidate-terrain.json'
    original=take(PRIVATE,originalpath)
    lineage=take(PRIVATE,PRIVATE/'lineage.json.gz')['rows']
    groundpath=HERE/'local'/GROUND.name/'289787:0-ground.json.gz'
    source=np.asarray(take(GROUND,groundpath)['completeAdjoiningTerrain'])
    def faces(p):
        return np.asarray(p['nativeMesh']['position']).reshape(-1,3)[np.asarray(p['nativeMesh']['index']).reshape(-1,3)]
    prior=faces(original);output=faces(candidate)
    counts={r['face']:r['outputFaces'] for r in changes}
    offset=0;max_plane=0.;max_area=0.;kinds={};records=[]
    assert len(prior)==len(lineage)
    for i,(face,origin) in enumerate(zip(prior,lineage)):
        count=counts.get(i,1);part=output[offset:offset+count]
        assert len(part)==count
        reference=source[origin['face']] if origin['kind']=='original-government-terrain-plane-fragment' else parent[origin['face']]
        if i not in counts:
            assert np.array_equal(part[0],face)
        p=shapely.Polygon(reference[:,[0,2]])
        if p.area>1e-10:
            normal=np.cross(reference[1]-reference[0],reference[2]-reference[0])
            normal/=np.linalg.norm(normal)
            error=float(np.abs((part-reference[0])@normal).max())
            assert error<1e-7,(i,error)
            max_plane=max(max_plane,error)
        else:
            assert count==1 and np.array_equal(part[0],reference)
        a=shapely.Polygon(face[:,[0,2]])
        b=shapely.union_all(shapely.polygons(part[:,:,[0,2]]))
        area=float(a.symmetric_difference(b).area)
        assert area<1e-6,(i,area)
        max_area=max(max_area,area)
        kinds[origin['kind']]=kinds.get(origin['kind'],0)+count
        records.append(dict(outputStart=offset,outputCount=count,previousFace=i,**origin))
        offset+=count
    assert offset==len(output)
    save(DOC/'source-lineage.json.gz',dict(rows=records,completeOutputFaces=offset))
    patch=copy.deepcopy(candidate)
    overlap=module('mount_sterling_overlap',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py')
    overlap.DOC=DOC
    overlap.overlap_proof(patch,[candidatepath,parentpath,groundpath,DOC/'source-lineage.json.gz',Path(__file__)])
    refs.append(HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py')
    check=copy.deepcopy(patch);check['nativeMesh'].pop('sourceOverlap',None)
    assert check==candidate,'Only overlap evidence metadata may change'
    rootpath=ROOT/'3d-viewer/city/data/terrain.json'
    validator=module('mount_sterling_terrain_validator',HERE.parent/'island-detail-integration/publish.py')
    validator.validate_patch(patch,read(rootpath))
    path=LOCAL/'candidate-terrain.json';save(path,patch)
    rows[0].update(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()))
    save(DOC/'terrain-candidates.json',rows)
    summary=dict(uids=['landsd/289787:0'],terrainValidationPassed=True,
                 outputFaces=len(output),faceOrigins=kinds,
                 maximumSourcePlaneNormalDistanceM=max_plane,maximumSplitCoverageDifferenceM2=max_area,
                 fullRenderedGeometryUnchangedFromConformingCandidate=True,
                 sourceGeometryChanges=0,productionTerrainChanges=0,installationApproved=False)
    save(DOC/'summary.json',summary)
    refs.extend([path,rootpath,HERE.parent/'island-detail-integration/publish.py',
                 HERE.parent/'island-detail-integration/native_terrain_validation.py'])
    module('mount_sterling_terrain_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH,'source-plane-lineage-full-overlap-and-boundary-validation',list(dict.fromkeys(refs)),summary)
    print(summary,flush=True)

if __name__=='__main__':main()
