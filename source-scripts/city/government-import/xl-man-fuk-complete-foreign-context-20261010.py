"""Read-only original Man Fuk source/foreign-component investigation.

Authoritative floor plan identifies Block A only. It grants no shared-envelope,
physical support, legal ownership or installation exemption for other blocks.
"""
import datetime, importlib.util, json
from pathlib import Path
import numpy as np
from urllib.request import Request, urlopen
import shapely
from shapely.geometry import GeometryCollection, Polygon
from run import ROOT, HERE, read, save, digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from source_closed_components import components

UID = 'landsd/266062:0'
SHA = '22b458321ca483c53324ee152cb27c382e5ac4dfd745974f169b1c551ac8a6c1'
MODEL = 'B364461960802063C0'
DOC = ROOT/'docs/astra-city/government-import/government-xl-man-fuk-complete-foreign-context-20261010'
RANK = DOC.parent/'government-xl-identity-primary-spatial-ranking-20261009/ranking.json.gz'
PLAN_URL = 'https://www.housingauthority.gov.hk/hdw/content/static/file/b5/residential/plans/chunmancourt_bA.pdf'

def parity(rings):
    result = GeometryCollection()
    for ring in rings:
        result = result.symmetric_difference(Polygon(ring))
    assert result.is_valid
    return result

def main():
    assert not DOC.exists(), 'Fresh immutable diagnostic required'
    rank = next(r for r in read(RANK)['rows'] if r['uid'] == UID)
    assert rank['sourceSHA256'] == SHA and rank['modelId'] == MODEL
    asset = ROOT/rank['sourcePath']
    assert digest(asset.read_bytes()) == SHA
    tri = decode_original_world_triangles(asset.read_bytes())
    assert digest(tri.astype('<f8').tobytes()) == rank['sourceTrianglesSHA256']
    assert len(tri) == rank['sourceTriangles']
    manifest = ROOT/'3d-viewer/city/data/manifest.json'
    before = digest(manifest.read_bytes())
    spec = importlib.util.spec_from_file_location('man_fuk_complete_current_forms', HERE/'xl-final-script-pass.py')
    forms_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(forms_module)
    lo, hi = tri.min(axis=(0, 1)), tri.max(axis=(0, 1))
    loaded = forms_module.load_forms([lo[0]-2, lo[2]-2, hi[0]+2, hi[2]+2])
    own = next(b for b, _, _ in loaded if b['uid'] == UID)
    target = parity(own['rings'])
    polygons = shapely.polygons(tri[:, :, [0, 2]])
    projection = shapely.union_all(polygons)
    extras = shapely.difference(polygons, target)
    topology = components(tri)
    face_component = {}
    for ci, c in enumerate(topology['components']):
        for face in c['faceIndices']:
            assert face not in face_component
            face_component[face] = ci
    assert sorted(face_component) == list(range(len(tri)))
    foreign = []
    for building, _, tile in loaded:
        if building['uid'] == UID:
            continue
        form = parity(building['rings'])
        overlap = projection.difference(target).intersection(form)
        if overlap.area <= 0:
            continue
        areas = shapely.area(shapely.intersection(extras, form))
        ids = np.flatnonzero(areas > 0).tolist()
        part_ids = sorted({face_component[i] for i in ids})
        foreign.append(dict(uid=building['uid'], name=building.get('name'),
            sourceForm=building, tile=tile, completeProjectedExcessM2=float(overlap.area),
            allPositiveAreaOriginalFaceIds=ids, perFaceAreaM2={str(i):float(areas[i]) for i in ids},
            originalComponents=[dict(component=ci, topology=topology['components'][ci],
                completeWorldBounds=[tri[topology['components'][ci]['faceIndices']].min(axis=(0,1)).tolist(),
                    tri[topology['components'][ci]['faceIndices']].max(axis=(0,1)).tolist()],
                overlapFaceIds=[i for i in ids if face_component[i] == ci]) for ci in part_ids]))
    with urlopen(Request(PLAN_URL, headers={'User-Agent':'HongKongSandbox-source-research/1.0'}), timeout=120) as response:
        content, final_url, status = response.read(), response.url, response.status
    assert content.startswith(b'%PDF') and len(content) > 1000
    DOC.mkdir(parents=True)
    plan = DOC/'official-man-fuk-block-a-floor-plan.pdf'
    plan.write_bytes(content)
    save(DOC/'official-plan-request.json', dict(url=PLAN_URL, finalURL=final_url,
        status=status, sha256=digest(content), bytes=len(content),
        retrievedAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        qualification='Official Housing Authority typical 1/F–15/F reference plan, not surveyed geographic placement or common ownership/support proof.'))
    hashes = {str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in
        [Path(__file__), RANK, asset, manifest, plan, HERE/'xl-final-script-pass.py',
         HERE/'source_closed_components.py', HERE/'exact_packed_world_geometry_20261009.py',
         *{ROOT/'3d-viewer'/tile for _, _, tile in loaded}]}
    assert digest(manifest.read_bytes()) == before
    save(DOC/'diagnostic.json.gz', dict(uid=UID, modelId=MODEL, sourceSHA256=SHA,
        sourceKey=rank['sourceKey'], allOriginalFaces=len(tri), allOriginalComponents=len(topology['components']),
        completeOriginalWorldSHA256=rank['sourceTrianglesSHA256'], manifestSHA256=before,
        allCurrentLocalForms=[b for b, _, _ in loaded], target=own,
        currentWholeProjectionCoverage=float(target.intersection(projection).area/target.area),
        maximumSourceExtentM=float(shapely.distance(shapely.points(tri[:,:,[0,2]].reshape(-1,2)),target).max()),
        foreignActors=sorted(foreign,key=lambda r:-r['completeProjectedExcessM2']), inputHashes=hashes,
        identityAccepted=False, physicalAccepted=False, installationApproved=False,
        sourceGeometryChanges=0, aiGeometryModelling=False, scriptExternalAICalls=0,
        qualification='Complete unchanged source-face research against every current local actor. Double-precision projection is diagnostic only. Same estate/name or small overlap does not exempt any foreign block. Exact component/source ownership and all ordinary physical/runtime/browser gates remain unresolved.'))
    print(json.dumps(dict(uid=UID, faces=len(tri), components=len(topology['components']),
        foreign=[{k:r[k] for k in ['uid','name','completeProjectedExcessM2','allPositiveAreaOriginalFaceIds']} for r in foreign]),indent=2),flush=True)

if __name__ == '__main__':
    main()
