"""Private exact-plane source-terrain inset; no production writes or acceptance."""
from pathlib import Path
import copy
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from native_patch_resolution import _faces
from source_surface_inset import plane,lift
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-mount-sterling-private-surface-v1-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
REC=BASE/'government-xl-mount-sterling-nine-original-recovery-v1-20261020';GROUND=BASE/'government-xl-mount-sterling-adjoining-ground-v1-20261020';SCOPE=BASE/'government-xl-mount-sterling-current-scope-v2-20261020';PARENT='city/data/government-native-lai-chi-kok-original-v1-20261019.json'
def main():
    assert not DOC.exists() and not LOCAL.exists();refs=[Path(__file__),HERE/'native_patch_resolution.py',HERE/'source_surface_inset.py',HERE/'exact_packed_world_geometry_20261009.py'];pins={}
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for folder in (REC,GROUND,SCOPE):
            receipt=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt);refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256'] for e in receipt['evidenceRefs']}
    def take(folder,path):
        assert digest(path.read_bytes())==pins[folder][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    row=next(r for r in take(REC,REC/'recovery.json')['rows'] if r['modelId']=='B323332207602063C0');asset=ROOT/row['assetPath'];assert digest(asset.read_bytes())==row['sourceSHA256']==pins[REC][row['assetPath']];refs.append(asset);model=decode_original_world_triangles(asset.read_bytes())
    original=np.asarray(take(GROUND,HERE/'local'/GROUND.name/'289787:0-ground.json.gz')['completeAdjoiningTerrain']);parentpath=ROOT/'3d-viewer'/PARENT;parent=take(SCOPE,parentpath);old=_faces(parent)
    projection=shapely.union_all(shapely.polygons(model[:,:,[0,2]]));region=projection.buffer(.1,join_style='mitre');sourcepolys=shapely.polygons(original[:,:,[0,2]]);valid=shapely.area(sourcepolys)>1e-10;tree=shapely.STRtree(sourcepolys);sourceids=tree.query(region,predicate='intersects');sourceids=[int(i) for i in sourceids if valid[i]]
    missing=region.difference(shapely.union_all(sourcepolys[sourceids]));assert missing.area<1e-6,('original-source-coverage',missing.area)
    oldpolys=shapely.polygons(old[:,:,[0,2]]);overlaps=shapely.intersects(oldpolys,region);areas=shapely.area(oldpolys);assert not np.any(overlaps&(areas<=1e-10)), 'vertical-terrain-in-repair-region-needs-explicit-clipping'
    output=[];lineage=[];changed=[];removed=0.;inserted=0.
    for i,face in enumerate(old):
        if not overlaps[i] or oldpolys[i].intersection(region).area<=1e-10:output.append(face);lineage.append(dict(kind='unchanged-parent',face=i));continue
        changed.append(i);removed+=oldpolys[i].intersection(region).area
        for f in lift(oldpolys[i].difference(region),plane(face)):output.append(f);lineage.append(dict(kind='parent-plane-fragment',face=i))
    for i in sourceids:
        part=sourcepolys[i].intersection(region)
        if part.area<=1e-10:continue
        inserted+=part.area
        for f in lift(part,plane(original[i])):output.append(f);lineage.append(dict(kind='original-government-terrain-plane-fragment',face=i))
    faces=np.asarray(output);candidate=copy.deepcopy(parent);candidate['nativeMesh']['position']=faces.reshape(-1).tolist();candidate['nativeMesh']['index']=list(range(len(faces)*3));candidate['nativeMesh']['source']['mountSterlingPrivateInset']=dict(policy='Original source planes inside mall projection plus 0.1m; existing parent planes retained outside. Private, not approved.',sourceSHA256=row['sourceSHA256'],regionWKT=region.wkt)
    # Old overlap evidence is historical and cannot approve the changed mesh.
    candidate['nativeMesh'].pop('sourceOverlap',None)
    path=LOCAL/'candidate-terrain.json';save(path,candidate);refs.append(path)
    save(DOC/'lineage.json.gz',dict(rows=lineage,changedParentFaces=changed,oldFaceCount=len(old),sourceFaceCount=len(original),installationApproved=False))
    save(DOC/'terrain-candidates.json',[dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),replaces=dict(url=PARENT,sha256=digest(parentpath.read_bytes())))])
    summary=dict(uids=[row['uid']],oldFaces=len(old),candidateFaces=len(faces),changedParentFaces=len(changed),unchangedParentFaces=len(old)-len(changed),repairAreaM2=float(region.area),removedProjectedAreaM2=removed,insertedProjectedAreaM2=inserted,sourceCoverageGapM2=float(missing.area),sourceGeometryChanges=0,installationApproved=False,terrainValidated=False,nextStep='Actual renderer, boundary and complete parent-neighbour checks; authenticate new source overlap evidence if required.')
    save(DOC/'summary.json',summary);module('mount_sterling_private_surface_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-original-terrain-plane-composition',refs,summary);print(summary,flush=True)
if __name__=='__main__':main()
