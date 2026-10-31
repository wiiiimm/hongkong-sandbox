"""Construct a private global original-TIN inset and partition by parent lineage.

This is not a validated terrain patch, installation or publication adapter.
"""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_tin_inset_construction_v1_20261029 import construct
from inherited_parent_coverage_v1 import qualify
from unchanged_low_parent_faces_v1_20261024 import bind, verify
from coordinated_native_boundary_v1_20261023 import seam_segments, compatible_seam

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-depot120104-land-inset-construction-v2-20261029'
PLAN = 'government-xl-depot120104-exact-land-domains-v1-20261029'
FAILED = 'government-xl-depot120104-terrain-sequence-v1-20261029-120104-0-inset'
CURRENT = 'government-xl-oceanwalk-depot-current-v1-20261029'
TERRAIN = 'government-xl-depot120104-cached-terrain-v1-20261029'
UID = 'landsd/120104:0'


def main():
    out, local = BASE / BATCH, HERE / 'local' / BATCH
    assert not out.exists() and not local.exists()
    refs, batch_pins, all_pins = [Path(__file__)], {}, {}

    def take_batch(batch, path):
        if batch not in batch_pins:
            batch_pins[batch] = authenticate(BASE / batch)[1]
            refs.append(BASE / batch / 'result.json')
        assert digest(path.read_bytes()) == batch_pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    plan = take_batch(PLAN, BASE / PLAN / 'summary.json')
    assert plan['readyForPrivateThreeMemberInset'] and plan['exactLandUnionRetained']
    parent = take_batch(FAILED, HERE / 'local' / FAILED / 'parent.json')
    for name, sha in parent['inputHashes'].items():
        path = ROOT / name
        assert digest(path.read_bytes()) == sha
        refs.append(path)
    baseline = np.asarray(parent['triangles'], dtype='<f8')
    selection = take_batch(CURRENT + '-runtime', BASE / (CURRENT + '-runtime') / 'selection.json.gz')
    row = next(r for r in selection['rows'] if r['uid'] == UID)
    attr = next(r for r in take_batch(CURRENT + '-attributes', BASE / (CURRENT + '-attributes') / 'attributes.json.gz')['rows'] if r['uid'] == UID)
    asset = ROOT / row['candidate']['path']
    assert digest(asset.read_bytes()) == row['sourceSHA256'] == attr['sourceSHA256'] == plan['sourceSHA256']
    refs.append(asset)
    ix = np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)
    literal = np.asarray(attr['completeLiteralWorldPosition']).reshape(-1, 3)
    original = literal.copy()
    original[ix.ravel()] = decode_original_world_triangles(asset.read_bytes()).reshape(-1, 3)
    worlds = [original, literal, np.asarray(attr['completeExplicitLeftAssociatedFloat32WorldPosition']).reshape(-1, 3), np.asarray(attr['completeExplicitBalancedFloat32WorldPosition']).reshape(-1, 3)]
    projection = shapely.union_all([shapely.union_all(shapely.polygons(p[ix][:, :, [0, 2]])) for p in worlds])
    core = projection.buffer(1, join_style='mitre')
    outer = core.buffer(3, join_style='mitre')
    land = shapely.union_all(shapely.polygons(baseline[:, :, [0, 2]]))
    assert land.covers(outer) and outer.distance(land.boundary) > 0
    checked = next(r for r in take_batch(TERRAIN, BASE / TERRAIN / 'summary.json')['rows'] if r['uid'] == UID)
    assert checked['sourceSHA256'] == row['sourceSHA256'] and checked['uncoveredSourceProjectionAreaM2'] == 0
    all_pins.update(batch_pins[TERRAIN])

    def take(path):
        assert digest(path.read_bytes()) == all_pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    out.mkdir()
    local.mkdir(parents=True)
    # Diagnostic construction continues after retaining the unchanged production
    # guard failure. No resulting surface is eligible for patch validation.
    try:
        low = bind(baseline, outer)
        low_guard = dict(passed=True)
    except AssertionError as error:
        low = None
        low_guard = dict(passed=False, reason=str(error), productionGuardChanged=False)
    output, lineage = construct(baseline, projection, core, outer, checked, take, all_pins, refs, out, local)
    low_proof = verify(output, low) if low is not None else dict(verified=False, guardFailure=low_guard)
    assert np.isfinite(output).all() and len(output) <= 25000
    save(out / 'global-lineage.json.gz', lineage)
    save(local / 'global-triangles.json.gz', dict(triangles=output.tolist()))
    assert len(output) == len(lineage['outputLineage'])
    assigned, pieces, arrays = set(), [], {}
    for member in plan['members']:
        parent_ids = set(member['parentFaceIds'])
        ids = [i for i, item in enumerate(lineage['outputLineage']) if item['parentFace'] in parent_ids]
        assert ids and not assigned.intersection(ids)
        assigned.update(ids)
        faces = output[ids]
        coverage = qualify(faces, member['bounds'])
        assert all(shapely.box(*member['bounds']).covers(shapely.Polygon(f[:, [0, 2]])) for f in faces)
        path = local / ('member-' + str(member['member']) + '.json.gz')
        save(path, dict(triangles=faces.tolist(), outputFaceIds=ids, coarseCells=member['coarseCells']))
        refs.append(path)
        arrays[member['member']] = faces
        pieces.append(dict(member=member['member'], triangles=len(faces), parentCoverage=coverage, path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())))
    assert assigned == set(range(len(output)))
    seams = []
    for edge in plan['sharedEdges']:
        line = shapely.from_wkt(edge['sharedEdgeWKT'])
        coordinates = list(line.coords)
        vertical = coordinates[0][0] == coordinates[-1][0]
        axis, coordinate = (0, coordinates[0][0]) if vertical else (2, coordinates[0][1])
        lo, hi = sorted(p[1 if vertical else 0] for p in coordinates)
        curves = [seam_segments(arrays[edge[k]], axis, coordinate, lo, hi) for k in ['left', 'right']]
        seams.append(dict(left=edge['left'], right=edge['right'], proof=compatible_seam(*curves, lo, hi)))
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256'] == plan['currentManifestSHA256']
    refs.append(manifest)
    result = dict(uids=[UID], sourceSHA256=row['sourceSHA256'], globalTerrainFaces=len(output),
                  members=pieces, sharedSeams=seams, unchangedLowParent=low_proof,
                  omittedWaterAreaM2=plan['omittedWaterAreaM2'], everyOutputFaceAssignedOnce=True,
                  terrainPatchValidationPassed=False, rendererChecksPassed=False, existingLowParentGuard=low_guard,
                  sourceGeometryChanges=0, installationApproved=False, publication=False,
                  qualification='One unchanged V14 construction algorithm over exact existing land facets, then partition by original parent-face lineage without refitting or clipping. Ordinary per-member coverage and complete finite rendered shared-edge envelopes checked. Existing low-parent guard failures are retained and make this ineligible for patch approval. Final native-patch boundary/overlap validation, renderer, neighbours, browser and installation remain required.')
    save(out / 'summary.json', result)
    refs.extend([HERE / n for n in ['original_tin_inset_construction_v1_20261029.py', 'selected_original_local_inset_v14_20261029.py', 'ronsdale_local_inset_v2_20261022.py', 'exact_affine_halfplane_clip_v1_20261024.py', 'affine_terrain_blend_v1.py', 'provider_projection_seam_cover_v1_20261029.py', 'coordinated_native_boundary_v1_20261023.py', 'inherited_parent_coverage_v1.py', 'unchanged_low_parent_faces_v1_20261024.py']])
    refs.extend(p for p in local.rglob('*') if p.is_file())
    module('depot_land_inset_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'private-coast-preserving-global-original-tin-construction', list(dict.fromkeys(refs)), result)
    print({k: result[k] for k in ['globalTerrainFaces', 'omittedWaterAreaM2', 'installationApproved']}, flush=True)


if __name__ == '__main__':
    main()
