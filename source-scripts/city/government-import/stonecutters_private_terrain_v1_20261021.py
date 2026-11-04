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
BATCH = 'government-xl-stonecutters-private-terrain-v1-20261021'
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
    output, lineage = [], []
    for i, face in enumerate(baseline):
        polygon = shapely.Polygon(face[:, [0, 2]])
        if polygon.area <= 1e-10 or polygon.disjoint(outer):
            output.append(face.copy()); lineage.append(i); continue
        coefficients = plane(face)
        for region in (polygon.intersection(core), polygon.intersection(outer).difference(core), polygon.difference(outer)):
            for fragment in lift(region, coefficients):
                for vertex in fragment:
                    weight = max(0., 1. - shapely.Point(vertex[[0, 2]]).distance(core) / 8.)
                    vertex[1] = min(vertex[1], vertex[1] + weight * (floor - vertex[1]))
                output.append(fragment); lineage.append(i)
    faces = np.asarray(output)
    candidate = builder.make_patch(dict(uids=[UID], cells=scope['regionalCoarseCells']), parent,
                                   baseline, [], allow_native_below_clamp=True)
    candidate['nativeMesh']['position'] = faces.reshape(-1).tolist()
    candidate['nativeMesh']['index'] = list(range(len(faces) * 3))
    policy = 'Private source-minimum terrain core with 1m collar and 8m return to unchanged current root terrain; no building geometry or pose edits.'
    candidate['nativeMesh']['source']['policy'] = policy
    candidate['meta']['source']['policy'] = policy
    before = geometry_sha(candidate)
    error = None
    try:
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
