"""Partition immutable physical failures; no actor/terrain edits or acceptance."""
import importlib.util
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon, box
from run import ROOT, HERE, read, save, digest, connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_paired_finite_clearance_20261010 import verify
from native_patch_resolution import _faces, _patch_bounds

BATCH = 'government-xl-man-fuk-current-physical-cause-partition-v1-20261010'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
PHYSICAL = DOC.parent / 'government-xl-man-fuk-complete-retained-original-physical-v2-20261010'


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    result = importlib.util.module_from_spec(spec); spec.loader.exec_module(result)
    return result


def main():
    assert not DOC.exists(), 'Fresh immutable diagnosis required'
    receipt = read(PHYSICAL / 'result.json')
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (receipt['jobId'],)).fetchone() == ('complete', receipt)
    for ref in receipt['evidenceRefs']:
        assert digest((ROOT / ref['path']).read_bytes()) == ref['sha256']
    runtime_path = HERE / 'local' / PHYSICAL.name / 'runtime-geometry.json.gz'
    runtime = read(runtime_path); assert len(runtime['rows']) == 1
    row = read(PHYSICAL / 'selection.json.gz')['rows'][0]
    asset = ROOT / row['candidate']['path']; raw = asset.read_bytes()
    assert digest(raw) == row['sourceSHA256']
    original = decode_original_world_triangles(raw)
    geometry = runtime['rows'][0]
    world = np.asarray(geometry['position']).reshape(-1, 3)[np.asarray(geometry['index']).reshape(-1, 3)]
    assert original.shape == world.shape == (10661, 3, 3)
    assert np.max(np.abs(original - world)) <= 1e-9
    ground = np.asarray(geometry['drawnGroundGeometry']).reshape(-1, 3, 3)
    final = module('man_fuk_immutable_foundation', 'xl-final-script-pass.py')
    points = np.concatenate([world, world.mean(axis=1)[:, None, :]], axis=1)
    polys = shapely.polygons(ground[:, :, [0, 2]])
    valid = shapely.area(polys) > 1e-10
    heights = final.s.context.shared.samples(points[:, :, [0, 2]].reshape(-1, 2), ground[valid], shapely.STRtree(polys[valid])).reshape(-1, 4)
    gaps = points[:, :, 1] - heights
    buried = np.isfinite(heights).all(axis=1) & (gaps < -.5).all(axis=1)
    assert int(buried.sum()) == 27
    parent_path = ROOT / '3d-viewer/city/data/government-native-75697-0.json'
    parent = read(parent_path); parent_box = box(*_patch_bounds(parent))
    native_ground = _faces(parent)
    records = []
    for i in np.flatnonzero(buried):
        native_result = None
        if parent_box.intersects(Polygon(world[i][:, [0, 2]])):
            try: native_result = verify(world[i], native_ground)
            except AssertionError: native_result = {'coverageNotProved': True, 'fullAcceptance': False}
        records.append(dict(originalSourceFace=int(i), completeOriginalFace=original[i].tolist(),
            actualRenderedFace=world[i].tolist(), allFourPriorFoundationPoints=points[i].tolist(),
            priorFoundationGapsM=gaps[i].tolist(),
            completeFiniteCurrentGround=verify(world[i], ground),
            intersectsRetainedParentRectangle=parent_box.intersects(Polygon(world[i][:, [0, 2]])),
            independentlyComparedRetainedOriginalGround=native_result))
    projection = shapely.union_all(shapely.polygons(original[:, :, [0, 2]]))
    inputs = read(PHYSICAL / 'neighbour-inputs.json.gz')
    by_uid = {r['building']['uid']: r['building'] for r in inputs['rows']}
    neighbours = []
    for check in read(PHYSICAL / 'neighbour-checks.json')['rows']:
        if not check['reasons']: continue
        building = by_uid[check['uid']]
        shape = Polygon(building['rings'][0], building['rings'][1:])
        overlap = projection.intersection(shape)
        neighbours.append(dict(uid=building['uid'], name=building.get('name'),
            sourceForm=building, unchangedRawGroundCheck=check,
            completeOriginalSourceProjectionIntersectionM2=float(overlap.area),
            completeOriginalSourceProjectionDistanceM=float(projection.distance(shape)),
            closedProjectionsDisjoint=projection.disjoint(shape),
            intersectsRetainedParentRectangle=parent_box.intersects(shape),
            skipOrInstallationCredit=False))
    save(DOC / 'diagnostic.json.gz', dict(uid=row['uid'],
        sourceSHA256=row['sourceSHA256'], completeOriginalFaces=len(original),
        completeOriginalWorldSHA256=digest(original.tobytes()),
        completeActualRenderedWorldSHA256=digest(world.tobytes()),
        completeCurrentGroundSHA256=digest(ground.tobytes()),
        fullyBuriedOriginalFaces=records, currentNeighbourRegressions=neighbours,
        oldLoaderFailureCause='one-ULP arithmetic-derived recorded top instead of exact authoritative source top',
        newLoaderAccepted=True, unresolvedPhysicalReasons=receipt['reasons'],
        qualification='The previous height sampler omitted one genuine vertical native terrain facet. V2 retains it literally. Complete surface equivalence remains unproved; no terrain, support, source-role or installation exemption.',
        sourceGeometryChanges=0, fullAcceptance=False, installationApproved=False))
    paths = [Path(__file__), PHYSICAL / 'result.json', PHYSICAL / 'selection.json.gz',
        PHYSICAL / 'neighbour-inputs.json.gz', PHYSICAL / 'neighbour-checks.json',
        PHYSICAL / 'foundation.json', runtime_path, asset, parent_path,
        HERE / 'exact_original_paired_finite_clearance_20261010.py',
        HERE / 'test_exact_original_paired_finite_clearance_20261010.py',
        DOC.parent / 'government-xl-man-fuk-complete-retained-original-physical-v1-20261010/result.json']
    freeze = module('man_fuk_cause_checkpoint', 'xl-popcorn-source-investigations-checkpoints-20261009.py')
    freeze.freeze(BATCH, 'immutable-complete-man-fuk-physical-cause-partition-v1', paths,
        dict(uids=[row['uid']], completeOriginalFaces=len(original),
            failedWholeFoundationFaces=27, neighbourRegressions=len(neighbours),
            disjointNeighbourUids=[n['uid'] for n in neighbours if n['closedProjectionsDisjoint']],
            overlappingNeighbourUids=[n['uid'] for n in neighbours if not n['closedProjectionsDisjoint']],
            rawFailuresPreserved=True, fullAcceptance=False,
            nextStep='Use exact complete source/retained-ground intersections to select terrain recovery or original supporting-source recovery; no blind rerun or tolerance change.'))
    print({n['uid']: dict(name=n['name'], overlapM2=n['completeOriginalSourceProjectionIntersectionM2'], disjoint=n['closedProjectionsDisjoint']) for n in neighbours}, flush=True)


if __name__ == '__main__': main()
