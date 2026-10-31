"""Bounded original-TIN replacement, preserving exact current ground outside its return.

Uses the established Ronsdale plane/upper-envelope method. All existing final
validators and the 1.2m source-height gate remain; no model geometry is edited.
"""
import argparse
import copy
import math
import subprocess
import traceback
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from ronsdale_local_inset_v2_20261022 import plane, lift, lower_region, parent_fragment_lift


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'capture', 'terrain-check', 'uid']:
        parser.add_argument('--' + key, required=True)
    args = parser.parse_args()
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc, local = base / args.batch, HERE / 'local' / args.batch
    assert not doc.exists() and not local.exists()
    refs, pins = [Path(__file__)], {}
    for name in [args.capture, args.terrain_check]:
        _, bound = authenticate(base / name)
        refs.append(base / name / 'result.json')
        for key, sha in bound.items():
            assert key not in pins or pins[key] == sha
            pins[key] = sha
    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    selected = take(base / args.capture / 'selection.json.gz')['rows']
    row = next(r for r in selected if r['uid'] == args.uid)
    g = next(r for r in take(HERE / 'local' / args.capture / 'runtime-geometry.json.gz')['rows'] if r['uid'] == args.uid)
    checked = next(r for r in take(base / args.terrain_check / 'summary.json')['rows'] if r['uid'] == args.uid)
    assert row['sourceSHA256'] == g['sourceSHA256'] == checked['sourceSHA256']
    asset = ROOT / row['candidate']['path']
    assert digest(asset.read_bytes()) == row['sourceSHA256']
    refs.append(asset)
    tri = np.asarray(g['position']).reshape(-1, 3)[np.asarray(g['index']).reshape(-1, 3)]
    projection = shapely.union_all([shapely.MultiPoint(f[:, [0, 2]]).convex_hull for f in tri])
    core = projection.buffer(1, join_style='mitre')
    outer = core.buffer(3, join_style='mitre')
    rootpath = ROOT / '3d-viewer/city/data/terrain.json'
    parent = read(rootpath)
    refs.append(rootpath)
    georef, size = parent['meta']['georef'], parent['cell']
    a, b, c, d = outer.bounds
    cells = [math.floor((a-.001+834500-georef['bE'])/size), math.floor((b-.001-816500+georef['bN'])/size), math.ceil((c+.001+834500-georef['bE'])/size), math.ceil((d+.001-816500+georef['bN'])/size)]
    builder = module('selected_inset_builder', HERE / 'resolve-pass-indexed-parent-clipping.py')
    bounds = builder.extent(cells, parent)
    domain = shapely.box(*bounds)
    assert domain.covers(outer) and outer.distance(domain.boundary) > 0
    save(doc / 'scope.json', dict(uids=[args.uid], cells=cells, bounds=bounds, coreBounds=list(core.bounds), outerBounds=list(outer.bounds)))
    result = dict(uids=[args.uid], installationApproved=False, publication=False, newlyInstalled=0, sourceGeometryChanges=0, scriptExternalAICalls=0)
    try:
        capturetool = HERE / 'selected_original_parent_capture_v1.mjs'
        subprocess.run(['node', str(capturetool), str((doc / 'scope.json').relative_to(ROOT)), str((local / 'parent.json').relative_to(ROOT))], cwd=ROOT, check=True)
        captured = read(local / 'parent.json')
        refs.extend([capturetool, local / 'parent.json'])
        for name, sha in captured['inputHashes'].items():
            assert digest((ROOT / name).read_bytes()) == sha
            refs.append(ROOT / name)
        baseline = np.asarray(captured['triangles'])
        assert len(baseline) and shapely.union_all(shapely.polygons(baseline[:, :, [0, 2]])).symmetric_difference(domain).area == 0
        # Metadata template uses exact existing ground, without any clamp exception.
        template = builder.make_patch(dict(cells=cells, uids=[args.uid]), parent, baseline, [], parent_sha256=digest(rootpath.read_bytes()))
        save(local / 'parent-template.json', template)
        decoder = module('selected_inset_source', HERE / 'xl-second-pass.py')
        decoder.LOCAL = local
        source, source_refs = [], []
        for name in checked['sourceTerrainPaths']:
            path = ROOT / name
            metadata = take(path)
            for buffer in metadata.get('buffers', []):
                member = path.parent / buffer['uri']
                assert digest(member.read_bytes()) == pins[str(member.relative_to(ROOT))]
                refs.append(member)
            source_refs.append(dict(path=name, sha256=pins[name]))
            values = decoder.terrain_triangles(path)
            for face in values[(values[:, :, 0].max(1) >= a) & (values[:, :, 0].min(1) <= c) & (values[:, :, 2].max(1) >= b) & (values[:, :, 2].min(1) <= d)]:
                polygon = shapely.Polygon(face[:, [0, 2]])
                if polygon.area > 1e-10:
                    source.extend(lift(polygon.intersection(outer), plane(face)))
        source = np.asarray(source)
        polygons = shapely.polygons(source[:, :, [0, 2]])
        union = shapely.union_all(polygons)
        assert projection.difference(union).area < 1e-6, 'Original terrain does not cover the complete model projection'
        planes = [plane(face) for face in source]
        tree = shapely.STRtree(polygons)
        upper, upperlineage = [], []
        for i, polygon in enumerate(polygons):
            cuts = []
            for j in tree.query(polygon, predicate='intersects'):
                if i == j:
                    continue
                overlap = polygon.intersection(polygons[j])
                if overlap.area <= 1e-10:
                    continue
                if np.array_equal(planes[i], planes[j]):
                    if j < i:
                        cuts.append(overlap)
                else:
                    cuts.append(lower_region(overlap, planes[j]-planes[i]))
            kept = polygon.difference(shapely.union_all(cuts)) if cuts else polygon
            for face in lift(kept, planes[i]):
                upper.append(face)
                upperlineage.append(i)
        source = np.asarray(upper)
        polygons = shapely.polygons(source[:, :, [0, 2]])
        assert abs(float(shapely.area(polygons).sum()-shapely.union_all(polygons).area)) < 1e-6
        assert shapely.union_all(polygons).symmetric_difference(union).area < 1e-6
        planes = [planes[i] for i in upperlineage]
        tree = shapely.STRtree(polygons)
        sectors = [(core, None)]
        for polygon in shapely.get_parts(shapely.constrained_delaunay_triangles(outer.difference(core))):
            if polygon.geom_type != 'Polygon' or polygon.area <= 0:
                continue
            xz = np.asarray(polygon.exterior.coords[:3])
            weights = []
            for x, z in xz:
                point = shapely.Point(x, z)
                inside, outside = point.distance(core.boundary) < 1e-8, point.distance(outer.boundary) < 1e-8
                assert inside != outside
                weights.append(0. if inside else 1.)
            sectors.append((polygon, plane(np.column_stack([xz[:, 0], weights, xz[:, 1]]))))
        output, lineage, changed = [], [], []
        removed = inserted = 0.
        for i, face in enumerate(baseline):
            polygon = shapely.Polygon(face[:, [0, 2]])
            if polygon.area <= 1e-10 or not polygon.intersects(outer):
                output.append(face)
                lineage.append(dict(kind='unchanged', parentFace=i))
                continue
            parentplane, cuts, added = plane(face), [], []
            for j in tree.query(polygon, predicate='intersects'):
                intersection = polygon.intersection(polygons[j])
                if intersection.area <= 1e-10:
                    continue
                # Replace with the exact original terrain in the core whether
                # it is higher or lower than current ground. All unchanged
                # clamp, seam, coverage and whole-neighbour gates still apply.
                lower = intersection
                if lower.area <= 1e-10:
                    continue
                cuts.append(lower)
                for region, weightplane in sectors:
                    for part in lift(lower.intersection(region), planes[j]):
                        if weightplane is not None:
                            weights = np.clip(part[:, [0, 2]] @ weightplane[:2]+weightplane[2], 0, 1)
                            oldheight = part[:, [0, 2]] @ parentplane[:2]+parentplane[2]
                            part[:, 1] = part[:, 1]*(1-weights)+oldheight*weights
                        assert part[:, 1].min() >= 1.2, 'new-inset-surface-below-existing-clamp'
                        added.append((part, int(j)))
            if not cuts:
                output.append(face)
                lineage.append(dict(kind='unchanged', parentFace=i))
                continue
            cut = shapely.union_all(cuts)
            removed += cut.area
            changed.append(i)
            for part in parent_fragment_lift(polygon.difference(cut), parentplane):
                output.append(part)
                lineage.append(dict(kind='parent-fragment', parentFace=i))
            for part, j in added:
                output.append(part)
                lineage.append(dict(kind='original-inset-or-return', parentFace=i, sourceFace=j))
                inserted += shapely.Polygon(part[:, [0, 2]]).area
        assert abs(removed-inserted) < 1e-6
        output = np.asarray(output)
        template['nativeMesh']['position'] = output.reshape(-1).tolist()
        template['nativeMesh']['index'] = list(range(output.size//3))
        template['meta']['source']['nativeSources'] = source_refs
        policy = 'Original highest source terrain replacement within model projection+1m and a shared piecewise-affine3m return. Exact existing ground elsewhere; original model bytes/pose unchanged.'
        for metadata in [template['nativeMesh']['source'], template['meta']['source']]:
            metadata['boundedOriginalInset'] = dict(policy=policy, coreBounds=list(core.bounds), outerBounds=list(outer.bounds))
        from float32_coverage import approve_roundoff
        from native_patch_resolution import projected_context
        _, candidate_polygons, _, _ = projected_context(template, bounds)
        if shapely.union_all(candidate_polygons).symmetric_difference(domain).area:
            save(doc / 'numerical-coverage.json', approve_roundoff(template, bounds))
        overlap = module('selected_inset_overlap', HERE / 'sham_shui_po_pool_shared_terrain_v2_20261016.py')
        overlap.DOC = doc
        overlap.overlap_proof(template, [local / 'parent-template.json', Path(__file__)])
        builder.validate_patch(template, parent)
        assert len(output) <= 25000, 'terrain-runtime-budget'
        path = local / 'candidate-terrain.json'
        save(path, template)
        save(doc / 'lineage.json.gz', dict(changedParentFaces=changed, sourceFaces=source.tolist(), outputLineage=lineage, coreWKT=core.wkt, outerWKT=outer.wkt, removedAreaM2=removed, insertedAreaM2=inserted))
        result.update(status='private-terrain-validator-passed', candidate=dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())), terrainTriangles=len(output), changedParentFaces=len(changed))
        refs.append(path)
    except Exception as error:
        result.update(status='bounded-inset-investigation', reason=str(error), errorType=type(error).__name__, permanentRejection=False)
        save(doc / 'failure.json', dict(errorType=type(error).__name__, message=str(error), traceback=traceback.format_exc()))
    save(doc / 'summary.json', result)
    refs.extend(path for path in local.rglob('*') if path.is_file())
    refs.extend([HERE / 'ronsdale_local_inset_v2_20261022.py', HERE / 'china_merchants_finite_inset_v4_20261021.py', HERE / 'xl-second-pass.py', HERE / 'resolve-pass-indexed-parent-clipping.py', HERE / 'sham_shui_po_pool_shared_terrain_v2_20261016.py', HERE / 'float32_coverage.py', HERE / 'native_patch_resolution.py'])
    module('selected_inset_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'bounded-selected-original-terrain-replacement', list(dict.fromkeys(refs)), result)
    print(result, flush=True)


if __name__ == '__main__':
    main()
