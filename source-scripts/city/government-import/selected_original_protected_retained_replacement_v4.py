"""Bounded original-TIN replacement retaining one complete current native terrain patch.

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
    parser.add_argument('--retain-patch', action='append', required=True)
    parser.add_argument('--protection-scope', required=True)
    parser.add_argument('--protect-form', action='append', required=True)
    parser.add_argument('--core-margin', type=float, default=.1)
    args = parser.parse_args()
    assert .01 <= args.core_margin <= 1 and len(set(args.protect_form)) == len(args.protect_form)
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc, local = base / args.batch, HERE / 'local' / args.batch
    assert not doc.exists() and not local.exists()
    refs = [Path(__file__)]
    _, pins = authenticate(base / args.capture)
    _, terrain_pins = authenticate(base / args.terrain_check)
    refs.extend([base / args.capture / 'result.json', base / args.terrain_check / 'result.json'])
    # Historical terrain provenance and current-scene evidence are separate
    # namespaces. Only the exact source terrain bytes transfer; no historical
    # manifest, runtime, terrain-placement or approval state transfers.
    def bound_take(path, bound):
        assert digest(path.read_bytes()) == bound[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    def take(path):
        return bound_take(path, pins)
    def terrain_take(path):
        return bound_take(path, terrain_pins)
    selected = take(base / args.capture / 'selection.json.gz')['rows']
    row = next(r for r in selected if r['uid'] == args.uid)
    g = next(r for r in take(HERE / 'local' / args.capture / 'runtime-geometry.json.gz')['rows'] if r['uid'] == args.uid)
    checked = next(r for r in terrain_take(base / args.terrain_check / 'summary.json')['rows'] if r['uid'] == args.uid)
    assert row['sourceSHA256'] == g['sourceSHA256'] == checked['sourceSHA256']
    asset = ROOT / row['candidate']['path']
    assert digest(asset.read_bytes()) == row['sourceSHA256']
    refs.append(asset)
    tri = np.asarray(g['position']).reshape(-1, 3)[np.asarray(g['index']).reshape(-1, 3)]
    projection = shapely.union_all([shapely.MultiPoint(f[:, [0, 2]]).convex_hull for f in tri])
    # Narrow only the terrain blend; every original building vertex/pose and
    # the complete original terrain under its actual projection remain fixed.
    core = projection.buffer(args.core_margin, join_style='mitre')
    outer = projection.buffer(1, join_style='mitre').buffer(3, join_style='mitre')
    protection_receipt, protection_pins = authenticate(base / args.protection_scope)
    assert protection_receipt['uids'] == [args.uid]
    protection_path = base / args.protection_scope / 'form-obligations.json.gz'
    assert digest(protection_path.read_bytes()) == protection_pins[str(protection_path.relative_to(ROOT))]
    assert digest((ROOT / '3d-viewer/city/data/manifest.json').read_bytes()) == pins['3d-viewer/city/data/manifest.json'] == protection_pins['3d-viewer/city/data/manifest.json']
    refs.extend([base / args.protection_scope / 'result.json', protection_path])
    forms = {r['uid']: r for r in read(protection_path)}
    protected = []
    for uid in args.protect_form:
        assert uid != args.uid and uid in forms
        f = forms[uid]
        polygon = shapely.Polygon(f['rings'][0], f['rings'][1:])
        assert polygon.is_valid and polygon.area > 0
        assert projection.distance(polygon) > 0, 'A source-overlapping form requires separate source/assembly resolution'
        region = polygon.buffer(.01, join_style='mitre')
        assert not core.intersects(region), 'Narrower core still touches protected current form'
        protected.append(dict(uid=uid, sourceDistanceM=projection.distance(polygon), bufferedBounds=list(region.bounds), formSHA256=digest(__import__('json').dumps(f,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())))
        outer = outer.difference(region)
    assert outer.is_valid and outer.covers(core) and core.distance(outer.boundary) > 0
    save(doc / 'protected-return.json', dict(sourceUid=args.uid, coreMarginM=args.core_margin, protected=protected, coreWKT=core.wkt, outerWKT=outer.wkt, qualification='Original source projection remains inside exact original TIN core. Return joins unchanged current parent at every protected-form boundary. No source geometry edits or neighbour acceptance transfer.'))
    rootpath = ROOT / '3d-viewer/city/data/terrain.json'
    parent = read(rootpath)
    refs.append(rootpath)
    georef, size = parent['meta']['georef'], parent['cell']
    a, b, c, d = outer.bounds
    cells = [math.floor((a-.001+834500-georef['bE'])/size), math.floor((b-.001-816500+georef['bN'])/size), math.ceil((c+.001+834500-georef['bE'])/size), math.ceil((d+.001-816500+georef['bN'])/size)]
    builder = module('selected_inset_builder', HERE / 'validated_parent_roundoff_template_v2.py')
    manifest = take(ROOT / '3d-viewer/city/data/manifest.json')
    expected = set(args.retain_patch)
    assert len(expected) == len(args.retain_patch) and 0 < len(expected) <= 4
    assert expected <= {r['url'] for r in manifest['terrainPatches']}
    retained = []
    retained_face_count = 0
    for url in args.retain_patch:
        path = ROOT / '3d-viewer' / url
        node = take(path)
        assert node.get('nativeMesh') and not node.get('patches') and not node.get('hydro')
        retained_face_count += len(node['nativeMesh']['index']) // 3
        current = node['coarseCells']
        cells = [min(cells[0], current[0]), min(cells[1], current[1]), max(cells[2], current[2]), max(cells[3], current[3])]
        retained.append(dict(url=url, sha256=digest(path.read_bytes()), retainedUids=node['meta']['targetUids']))
    assert len(retained) == 1, 'This initial bounded adapter requires exactly one retained native patch'
    bounds = builder.extent(cells, parent)
    domain = shapely.box(*bounds)
    contacts = set()
    for entry in manifest['terrainPatches']:
        node = take(ROOT / '3d-viewer' / entry['url'])
        coarse_contact = domain.intersection(shapely.box(*builder.extent(node['coarseCells'], parent))).area > 0
        packed_contact = False
        def visit(value):
            nonlocal packed_contact
            if value.get('nativeMesh'):
                vertices = np.asarray(value['nativeMesh']['position']).reshape(-1, 3)
                vertices = np.concatenate([vertices, vertices.astype('float32').astype('float64')])
                low, high = vertices.min(0), vertices.max(0)
                packed_contact |= domain.intersection(shapely.box(low[0], low[2], high[0], high[2])).area > 0
            for child in value.get('patches', []):
                visit(child)
        visit(node)
        if coarse_contact or packed_contact:
            contacts.add(entry['url'])
    assert contacts == expected, 'Expanded region requires further explicit terrain retention'
    assert domain.covers(outer) and outer.distance(domain.boundary) > 0
    save(doc / 'scope.json', dict(uids=[args.uid], cells=cells, bounds=bounds, coreBounds=list(core.bounds), outerBounds=list(outer.bounds)))
    result = dict(uids=[args.uid], retainedPatches=retained, installationApproved=False, publication=False, newlyInstalled=0, sourceGeometryChanges=0, scriptExternalAICalls=0)
    try:
        capturetool = HERE / 'selected_original_parent_capture_v1.mjs'
        subprocess.run(['node', str(capturetool), str((doc / 'scope.json').relative_to(ROOT)), str((local / 'parent.json').relative_to(ROOT))], cwd=ROOT, check=True)
        captured = read(local / 'parent.json')
        refs.extend([capturetool, local / 'parent.json'])
        for name, sha in captured['inputHashes'].items():
            assert digest((ROOT / name).read_bytes()) == sha
            refs.append(ROOT / name)
        baseline = np.asarray(captured['triangles'])
        assert len(baseline), 'No current parent terrain faces'
        current_union = shapely.union_all(shapely.polygons(baseline[:, :, [0, 2]]))
        save(doc / 'current-parent-coverage.json', dict(missingAreaM2=float(domain.difference(current_union).area), outsideAreaM2=float(current_union.difference(domain).area), qualification='Measure the actual existing surface. The unchanged builder.make_patch/validate_native_mesh coverage, overlap and boundary guards below determine admissibility; no exact-zero surrogate gate or new waiver.'))
        # Metadata template uses exact existing ground, without any clamp exception.
        template = builder.make_patch(dict(cells=cells, uids=[args.uid]), parent, baseline, [], parent_sha256=digest(rootpath.read_bytes()), terrain_triangle_budget=retained_face_count+25000, declare_float32_roundoff=True, overlap_evidence_dir=doc / 'parent-template-overlap', overlap_sources=[local / 'parent.json', Path(__file__)])
        save(local / 'parent-template.json', template)
        if template['nativeMesh']['source'].get('numericalCoverageGap'):
            save(doc / 'parent-template-roundoff.json', template['nativeMesh']['source']['numericalCoverageGap'])
        decoder = module('selected_inset_source', HERE / 'xl-second-pass.py')
        decoder.LOCAL = local
        source, source_refs = [], []
        for name in checked['sourceTerrainPaths']:
            path = ROOT / name
            metadata = terrain_take(path)
            for buffer in metadata.get('buffers', []):
                member = path.parent / buffer['uri']
                assert digest(member.read_bytes()) == terrain_pins[str(member.relative_to(ROOT))]
                refs.append(member)
            source_refs.append(dict(path=name, sha256=terrain_pins[name]))
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
        sectors = []
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
        # The existing parent has tiny genuine uncovered regions. Replacing
        # only parent/source intersections reproduces those holes. Put the
        # complete authentic source-TIN core in once, independent of parent
        # triangle coverage; blend only the surrounding existing-parent return.
        core_faces = 0
        for j, face in enumerate(source):
            for part in lift(shapely.Polygon(face[:, [0, 2]]).intersection(core), planes[j]):
                assert part[:, 1].min() >= 1.2, 'new-inset-surface-below-existing-clamp'
                output.append(part)
                lineage.append(dict(kind='complete-authentic-original-tin-core', sourceFace=j))
                inserted += shapely.Polygon(part[:, [0, 2]]).area
                core_faces += 1
        parent_union = shapely.union_all(shapely.polygons(baseline[:, :, [0, 2]]))
        original_union = shapely.union_all(polygons)
        filled = core.intersection(original_union).difference(parent_union)
        # Removed face areas count each existing overlapping source layer;
        # the new authentic core is a single upper envelope. Account exactly
        # for the already proved parent overlap instead of assuming it is zero.
        core_domain = core.intersection(original_union)
        old_core_area = sum(shapely.Polygon(face[:, [0, 2]]).intersection(core_domain).area for face in baseline)
        old_core_union_area = parent_union.intersection(core_domain).area
        old_core_excess = old_core_area-old_core_union_area
        conservation = dict(insertedAreaM2=inserted, removedAreaM2=removed, filledParentHoleAreaM2=float(filled.area), removedExistingCoreProjectedExcessM2=old_core_excess, residualM2=inserted-removed-filled.area+old_core_excess)
        save(doc / 'core-area-accounting.json', conservation)
        assert abs(conservation['residualM2']) < 1e-6, 'Complete original core area accounting disagrees: '+str(conservation)
        save(doc / 'authentic-core-coverage.json', dict(coreFaces=core_faces, originalTinAddedForMissingCurrentParentM2=float(filled.area), removedAreaM2=removed, insertedAreaM2=inserted, coreWKT=core.wkt, qualification='Complete source-derived affine TIN core, without clipping it to pre-existing parent holes. No invented source/model heights or coverage waiver. Current-neighbour, exact drawn coverage, strict foundations and parent boundary gates remain required.'))
        output = np.asarray(output)
        template['nativeMesh']['position'] = output.reshape(-1).tolist()
        template['nativeMesh']['index'] = list(range(output.size//3))
        template['meta']['source']['nativeSources'] = source_refs
        template['meta']['targetUids'] = sorted(set([args.uid] + [u for r in retained for u in r['retainedUids']]))
        template['meta']['source']['retainedNativeSources'] = retained
        template['nativeMesh']['source']['retainedNativeSources'] = retained
        policy = 'Original highest source terrain replacement within explicit source core and a piecewise-affine return carved around authenticated nonintersecting current forms. Exact existing ground elsewhere; original model bytes/pose unchanged.'
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
        save(doc / 'proposal-with-overlap-evidence.json', template)
        builder.validate_patch(template, parent)
        assert len(output) <= retained_face_count+25000, 'Incremental terrain runtime budget exceeded'
        save(doc / 'incremental-runtime-budget.json', dict(retainedOriginalTerrainFaces=retained_face_count, candidateTerrainFaces=len(output), addedTerrainFaces=len(output)-retained_face_count, maximumAdditionalFaces=25000, policySource='source-scripts/city/government-import/selected_retained_native_candidate_v2.py', qualification='Established retained-parent incremental limit, matching retained replacementV7. Existing source/geometry/placement/runtime/device guards remain. No geometry consolidation or source edits.'))
        path = local / 'candidate-terrain.json'
        save(path, template)
        save(doc / 'lineage.json.gz', dict(changedParentFaces=changed, sourceFaces=source.tolist(), outputLineage=lineage, coreWKT=core.wkt, outerWKT=outer.wkt, removedAreaM2=removed, insertedAreaM2=inserted))
        result.update(status='private-terrain-validator-passed', candidate=dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()), replaces=retained[0]), terrainTriangles=len(output), changedParentFaces=len(changed))
        refs.append(path)
    except Exception as error:
        result.update(status='bounded-inset-investigation', reason=str(error), errorType=type(error).__name__, permanentRejection=False)
        save(doc / 'failure.json', dict(errorType=type(error).__name__, message=str(error), traceback=traceback.format_exc()))
    save(doc / 'summary.json', result)
    refs.extend(path for path in local.rglob('*') if path.is_file())
    refs.extend(path for path in doc.rglob('*') if path.is_file())
    refs.extend([HERE / 'ronsdale_local_inset_v2_20261022.py', HERE / 'china_merchants_finite_inset_v4_20261021.py', HERE / 'xl-second-pass.py', HERE / 'validated_parent_roundoff_template_v2.py', HERE / 'sham_shui_po_pool_shared_terrain_v2_20261016.py', HERE / 'float32_coverage.py', HERE / 'native_patch_resolution.py'])
    module('selected_inset_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'bounded-selected-original-terrain-replacement', list(dict.fromkeys(refs)), result)
    print(result, flush=True)


if __name__ == '__main__':
    main()
