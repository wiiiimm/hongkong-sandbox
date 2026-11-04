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
BATCH = 'government-xl-thei-private-terrain-v3-20261021'
DOC = BASE / BATCH
LOCAL = HERE / 'local' / BATCH
UIDS = ['landsd/259613:0','landsd/259803:0']

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
    sb = 'government-xl-thei-regional-scope-v1-20261021'
    scope = take(sb, BASE / sb / 'scope.json')
    assert scope['simpleRootReplacementEligible'], 'Existing terrain needs explicit retention'
    rootpath = ROOT / '3d-viewer/city/data/terrain.json'
    parent = take(sb, rootpath)
    take(sb, ROOT / '3d-viewer/city/data/manifest.json')
    tb = 'government-xl-thei-original-ground-stem-trial-v1-20261021'
    line = take(tb, BASE / tb / 'lineage.json.gz')
    summary = take(tb, BASE / tb / 'summary.json')
    core, outer = shapely.from_wkt(line['coreWKT']), shapely.from_wkt(line['outerWKT'])
    domain = scope['regionalParentExtent']
    rectangle = shapely.box(*domain)
    assert rectangle.covers(outer) and outer.distance(rectangle.boundary) > 0
    builder = module('stone_private_builder', HERE / 'resolve-pass-indexed-parent-clipping.py')
    sampler = builder.terrain.fine.DemSampler(parent, rendered=True)
    baseline = np.asarray(grid_surface_faces(sampler, rectangle))
    old = 'government-xl-259803-independent-original-ground-20261008'
    meta = take(old, BASE / old / 'terrain.json')
    oldpath = ROOT / meta['patch']['path']
    assert digest(oldpath.read_bytes()) == meta['patch']['sha256']
    refs.append(oldpath)
    old_domain = shapely.box(*meta['patch']['bounds'])
    assert rectangle.covers(old_domain)
    private = take(tb, HERE / 'local' / tb / 'private-ground.json.gz')
    faces = np.asarray(private['triangles'])
    assert old_domain.covers(shapely.box(float(faces[:,:,0].min()),float(faces[:,:,2].min()),float(faces[:,:,0].max()),float(faces[:,:,2].max())))
    output = list(faces)
    lineage = [-1] * len(faces)
    for i, face in enumerate(baseline):
        polygon = shapely.Polygon(face[:, [0, 2]])
        region = polygon.difference(old_domain)
        for fragment in lift(region, plane(face)):
            output.append(fragment); lineage.append(i)
    faces = np.asarray(output)
    # Restore the whole affected depot footprint, not just its sampled points.
    nb = 'government-xl-thei-form-regression-v1-20261021'
    neighbours = take(nb, BASE / nb / 'neighbour-inputs.json.gz')
    form = next(r['building'] for r in neighbours['rows'] if r['building']['uid'] == 'landsd/70208:0')
    guard = shapely.Polygon(form['rings'][0],form['rings'][1:]).buffer(.25,join_style='mitre')
    transition = guard.buffer(2,join_style='mitre')
    current = 'government-xl-thei-current-runtime-v1-20261021'
    rows = take(current, BASE / current / 'selection.json.gz')['rows']
    from exact_packed_world_geometry_20261009 import decode_original_world_triangles
    for row in rows:
        asset = ROOT / row['candidate']['path']
        assert digest(asset.read_bytes()) == row['sourceSHA256']; refs.append(asset)
        tri = decode_original_world_triangles(asset.read_bytes())
        projection = shapely.union_all(shapely.polygons(tri[:,:,[0,2]]))
        assert projection.disjoint(transition), 'Neighbour restoration overlaps owned model'
    repaired = []
    root_polys = [shapely.Polygon(t[:,[0,2]]) for t in baseline]
    for face in faces:
        poly = shapely.Polygon(face[:,[0,2]])
        if poly.area <= 1e-10 or poly.disjoint(transition):
            repaired.append(face); continue
        coefficients = plane(face)
        repaired.extend(lift(poly.difference(transition),coefficients))
        for rootface, rootpoly in zip(baseline,root_polys):
            region = poly.intersection(transition).intersection(rootpoly)
            if region.area <= 1e-10: continue
            root_coeff = plane(rootface)
            repaired.extend(lift(region.intersection(guard),root_coeff))
            for fragment in lift(region.difference(guard),coefficients):
                for vertex in fragment:
                    parent_y = root_coeff[0]*vertex[0]+root_coeff[1]*vertex[2]+root_coeff[2]
                    weight = max(0.,1-shapely.Point(vertex[[0,2]]).distance(guard)/2)
                    vertex[1] += weight*(parent_y-vertex[1])
                repaired.append(fragment)
    faces = np.asarray(repaired)
    lineage = []  # Full input/guard geometry is retained below; no obsolete face map.
    save(DOC/'depot-preservation.json',dict(uid=form['uid'],guardWKT=guard.wkt,transitionWKT=transition.wkt,wholeFootprint=True,sourceModelsDisjoint=True))
    candidate = builder.make_patch(dict(uids=UIDS, cells=scope['regionalCoarseCells']), parent,
                                   baseline, [], allow_native_below_clamp=True)
    candidate['nativeMesh']['position'] = faces.reshape(-1).tolist()
    candidate['nativeMesh']['index'] = list(range(len(faces) * 3))
    policy = 'Private exact prior original-TIN candidate with local source-stem ground adjustment; expanded exterior remains current parent terrain. No building geometry or pose edits.'
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
                                               uids=UIDS, bounds=domain, triangles=len(faces))])
    result = dict(uids=UIDS, terrainValidationPassed=error is None, error=error, triangles=len(faces),
                  sourceGeometryChanges=0, installationApproved=False, productionChanges=0,
                  nextStep='Complete current runtime, full source foundation/support, all neighbour regression, identity and browser acceptance.')
    save(DOC / 'summary.json', result)
    for key, expected in consumed.items():
        assert digest((ROOT / key).read_bytes()) == expected, key
    refs += [HERE/'exact_packed_world_geometry_20261009.py', out, HERE / 'resolve-pass-indexed-parent-clipping.py', HERE / 'native_patch_resolution.py',
             HERE / 'china_merchants_finite_inset_v4_20261021.py', HERE / 'float32_coverage.py',
             HERE / 'sham_shui_po_pool_shared_terrain_v2_20261016.py']
    module('stone_private_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'private-original-terrain-candidate-validation', list(dict.fromkeys(refs)), result)
    print(result, flush=True)

if __name__ == '__main__':
    main()
