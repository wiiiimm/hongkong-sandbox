"""Construct a private full-domain terrain candidate; original assets immutable."""
from pathlib import Path
import traceback
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from native_patch_resolution import grid_surface_faces
from china_merchants_finite_inset_v4_20261021 import plane, lift
from float32_coverage import approve_roundoff, geometry_sha

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-stonecutters-private-terrain-v3-20261021'
DOC = BASE / BATCH
LOCAL = HERE / 'local' / BATCH
UID = 'landsd/127037:0'

def main():
    assert not DOC.exists() and not LOCAL.exists()
    refs, consumed = [Path(__file__)], {}
    def take(batch, path):
        _, pins = authenticate(BASE / batch)
        key = str(path.relative_to(ROOT))
        assert digest(path.read_bytes()) == pins[key], key
        consumed[key] = pins[key]
        refs.extend([BASE / batch / 'result.json', path])
        return read(path)
    sb = 'government-xl-stonecutters-regional-scope-v2-20261021'
    scope = take(sb, BASE / sb / 'scope.json')
    assert scope['simpleRootReplacementEligible'], 'Existing terrain needs explicit retention'
    rootpath = ROOT / '3d-viewer/city/data/terrain.json'
    parent = take(sb, rootpath)
    take(sb, ROOT / '3d-viewer/city/data/manifest.json')
    tb = 'government-xl-stonecutters-ground-trial-v1-20261021'
    line = take(tb, BASE / tb / 'lineage.json.gz')
    summary = take(tb, BASE / tb / 'summary.json')
    core, outer = shapely.from_wkt(line['coreWKT']), shapely.from_wkt(line['outerWKT'])
    domain = scope['regionalParentExtent']
    rectangle = shapely.box(*domain)
    assert rectangle.covers(outer) and outer.distance(rectangle.boundary) > 0
    builder = module('stone_private_builder', HERE / 'resolve-pass-indexed-parent-clipping.py')
    sampler = builder.terrain.fine.DemSampler(parent, rendered=True)
    baseline = np.asarray(grid_surface_faces(sampler, rectangle))
    floor = summary['sourceMinimumY']
    forms = take(sb, BASE / sb / 'form-obligations.json.gz')
    neighbour = next(f for f in forms if f['uid'] == 'landsd/128950:0')
    protected = shapely.Polygon(neighbour['rings'][0], neighbour['rings'][1:]).buffer(.25, join_style='mitre')
    guard = protected.buffer(1, join_style='mitre')
    save(DOC / 'protected-neighbour.json', dict(uid=neighbour['uid'], protectedWKT=protected.wkt, guardWKT=guard.wkt))
    output, lineage = [], []
    for i, face in enumerate(baseline):
        polygon = shapely.Polygon(face[:, [0, 2]])
        if polygon.area <= 1e-10 or polygon.disjoint(outer):
            output.append(face.copy()); lineage.append(i); continue
        coefficients = plane(face)
        regions = (polygon.intersection(core), polygon.intersection(outer).difference(core), polygon.difference(outer))
        regions = [part for region in regions for part in (region.intersection(protected), region.intersection(guard).difference(protected), region.difference(guard)) if part.area > 1e-10]
        for region in regions:
            for fragment in lift(region, coefficients):
                for vertex in fragment:
                    point = shapely.Point(vertex[[0, 2]])
                    weight = min(max(0., 1. - point.distance(core) / 8.), min(1., point.distance(protected)))
                    vertex[1] = min(vertex[1], vertex[1] + weight * (floor - vertex[1]))
                output.append(fragment); lineage.append(i)
    faces = np.asarray(output)
    candidate = builder.make_patch(dict(uids=[UID], cells=scope['regionalCoarseCells']), parent,
                                   baseline, [], allow_native_below_clamp=True)
    candidate['nativeMesh']['position'] = faces.reshape(-1).tolist()
    candidate['nativeMesh']['index'] = list(range(len(faces) * 3))
    policy = 'Private source-minimum terrain core with 1m collar and 8m return to unchanged current root terrain; preserve neighbour128950 footprint plus0.25m and a1m transition; no building geometry or pose edits.'
    candidate['nativeMesh']['source']['policy'] = policy
    candidate['meta']['source']['policy'] = policy
    before = geometry_sha(candidate)
    error = None
    try:
        from native_patch_resolution import projected_context
        _, polygons, missing, _ = projected_context(candidate, domain)
        residue = shapely.union_all(polygons).symmetric_difference(rectangle).area
        save(DOC / 'coverage-measurement.json', dict(symmetricDifferenceAreaM2=residue, missingAreaM2=missing.area))
        if residue > 0:
            save(DOC / 'numerical-coverage.json', approve_roundoff(candidate, domain))
        overlap = module('stone_private_overlap', HERE / 'sham_shui_po_pool_shared_terrain_v2_20261016.py')
        overlap.DOC = DOC
        overlap.overlap_proof(candidate, [Path(__file__), BASE / sb / 'result.json'])
        builder.validate_patch(candidate, parent)
        assert len(faces) <= 25000 and geometry_sha(candidate) == before
    except Exception as exc:
        error = dict(type=type(exc).__name__, message=str(exc), traceback=traceback.format_exc())
        save(DOC / 'validation-failure.json', error)
    out = LOCAL / 'candidate-terrain.json'
    save(out, candidate)
    save(DOC / 'lineage.json.gz', dict(parentFaceIds=lineage, baselineFaces=len(baseline)))
    save(DOC / 'terrain-candidates.json', [dict(path=str(out.relative_to(ROOT)), sha256=digest(out.read_bytes()),
                                               uids=[UID], bounds=domain, triangles=len(faces))])
    result = dict(uids=[UID], terrainValidationPassed=error is None, error=error, triangles=len(faces),
                  sourceGeometryChanges=0, installationApproved=False, productionChanges=0,
                  nextStep='Complete current runtime, full source foundation/support, all neighbour regression, identity and browser acceptance.')
    save(DOC / 'summary.json', result)
    for key, expected in consumed.items():
        assert digest((ROOT / key).read_bytes()) == expected, key
    refs += [out, HERE / 'resolve-pass-indexed-parent-clipping.py', HERE / 'native_patch_resolution.py',
             HERE / 'china_merchants_finite_inset_v4_20261021.py', HERE / 'float32_coverage.py',
             HERE / 'sham_shui_po_pool_shared_terrain_v2_20261016.py']
    module('stone_private_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'private-original-terrain-candidate-validation', list(dict.fromkeys(refs)), result)
    print(result, flush=True)

if __name__ == '__main__':
    main()
