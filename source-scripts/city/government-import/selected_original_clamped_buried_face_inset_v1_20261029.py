"""Bounded original-TIN inset local to all authenticated wholly buried faces.

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
from affine_terrain_blend_v1 import sector as blend_sector, evaluate as blend_evaluate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'capture', 'terrain-check', 'context', 'uid']:
        parser.add_argument('--' + key, required=True)
    parser.add_argument('--parent-capture', help='Completed prior diagnostic with identical current renderer inputs/domain')
    args = parser.parse_args()
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc, local = base / args.batch, HERE / 'local' / args.batch
    assert not doc.exists() and not local.exists()
    refs, pins = [Path(__file__), HERE / 'affine_terrain_blend_v1.py', HERE / 'inherited_parent_coverage_v1.py', HERE / 'clamped_original_terrain_v4_20261026.py'], {}
    historical_ground_manifest = None
    for name in [args.capture, args.terrain_check, args.context]:
        _, bound = authenticate(base / name)
        refs.append(base / name / 'result.json')
        for key, sha in bound.items():
            if name == args.terrain_check and key == '3d-viewer/city/data/manifest.json':
                historical_ground_manifest = sha
                continue
            assert key not in pins or pins[key] == sha
            pins[key] = sha
    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    selection = take(base / args.capture / 'selection.json.gz')
    manifestpath = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifestpath.read_bytes()) == selection['manifestSHA256'] == pins[str(manifestpath.relative_to(ROOT))]
    refs.append(manifestpath)
    save(doc / 'terrain-source-context.json', dict(historicalSourceTerrainManifestSHA256=historical_ground_manifest, currentRendererManifestSHA256=selection['manifestSHA256'], qualification='Historical original-terrain diagnostics supply only exact source-bound terrain paths. Actual model coordinates and parent ground are freshly captured against current map. No old terrain/current-scene acceptance transferred.'))
    selected = selection['rows']
    row = next(r for r in selected if r['uid'] == args.uid)
    g = next(r for r in take(HERE / 'local' / args.capture / 'runtime-geometry.json.gz')['rows'] if r['uid'] == args.uid)
    checked = next(r for r in take(base / args.terrain_check / 'summary.json')['rows'] if r['uid'] == args.uid)
    assert row['sourceSHA256'] == g['sourceSHA256'] == checked['sourceSHA256']
    asset = ROOT / row['candidate']['path']
    assert digest(asset.read_bytes()) == row['sourceSHA256']
    refs.append(asset)
    tri = np.asarray(g['position']).reshape(-1, 3)[np.asarray(g['index']).reshape(-1, 3)]
    context = take(base / args.context / (args.uid.split('/')[1]+'.json'))
    assert context['uid']==args.uid and context['sourceSHA256']==row['sourceSHA256']
    faces=list(context['buriedFaces'])
    ids=[f['faceIndex']for f in faces];assert ids and len(ids)==len(set(ids))
    assert all(type(i)is int and 0<=i<len(tri)for i in ids)
    for f in faces:
        assert np.array_equal(np.asarray(f['vertices']),tri[f['faceIndex']])
        t=tri[f['faceIndex']];normal=np.cross(t[1]-t[0],t[2]-t[0]);assert bool(f['upward'])==bool(normal[1]>.25*np.linalg.norm(normal))
    save(doc / 'original-face-scope.json',dict(uid=args.uid,sourceSHA256=row['sourceSHA256'],completeSourceFaces=len(tri),selectedWhollyBuriedFaceIds=ids,qualification='All authenticated wholly buried source faces nominate diagnostic locality only, including lower walls and undersides. This does not qualify any source role or burial. Source-TIN floor remains1.2m; every original face remains in final physical checks.'))
    projection = shapely.union_all([shapely.MultiPoint(f[:, [0, 2]]).convex_hull for f in tri[ids]])
    assert projection.area>0

    core = projection.buffer(1, join_style='mitre')
    outer = core.buffer(3, join_style='mitre')
    rootpath = ROOT / '3d-viewer/city/data/terrain.json'
    parent = read(rootpath)
    refs.append(rootpath)
    georef, size = parent['meta']['georef'], parent['cell']
    a, b, c, d = outer.bounds
    cells = [math.floor((a-.001+834500-georef['bE'])/size), math.floor((b-.001-816500+georef['bN'])/size), math.ceil((c+.001+834500-georef['bE'])/size), math.ceil((d+.001-816500+georef['bN'])/size)]
    builder = module('selected_inset_builder', HERE / 'resolve_pass_indexed_parent_clipping_v2.py')
    bounds = builder.extent(cells, parent)
    domain = shapely.box(*bounds)
    assert domain.covers(outer) and outer.distance(domain.boundary) > 0
    save(doc / 'scope.json', dict(uids=[args.uid], cells=cells, bounds=bounds, coreBounds=list(core.bounds), outerBounds=list(outer.bounds)))
    result = dict(uids=[args.uid], installationApproved=False, publication=False, newlyInstalled=0, sourceGeometryChanges=0, scriptExternalAICalls=0)
    try:
        capturetool = HERE / 'selected_original_parent_capture_v2.mjs'
        if args.parent_capture:
            prior = base / args.parent_capture
            _, previous_pins = authenticate(prior)
            previous_parent = HERE / 'local' / args.parent_capture / 'parent.json'
            assert digest(previous_parent.read_bytes()) == previous_pins[str(previous_parent.relative_to(ROOT))]
            assert digest(capturetool.read_bytes()) == previous_pins[str(capturetool.relative_to(ROOT))]
            assert read(previous_parent)['domain'] == bounds
            local.mkdir(parents=True, exist_ok=True)
            (local / 'parent.json').write_bytes(previous_parent.read_bytes())
            refs.extend([prior / 'result.json', previous_parent])
        else:
            subprocess.run(['node', str(capturetool), str((doc / 'scope.json').relative_to(ROOT)), str((local / 'parent.json').relative_to(ROOT))], cwd=ROOT, check=True)
        captured = read(local / 'parent.json')
        refs.extend([capturetool, local / 'parent.json'])
        for name, sha in captured['inputHashes'].items():
            assert digest((ROOT / name).read_bytes()) == sha
            refs.append(ROOT / name)
        baseline = np.asarray(captured['triangles'])
        from inherited_parent_coverage_v1 import qualify as qualify_parent_coverage
        save(doc / 'parent-coverage-context.json', qualify_parent_coverage(baseline, bounds))
        # Metadata template uses exact existing ground, without any clamp exception.
        template_proof = module('selected_parent_template_proof', HERE / 'sham_shui_po_pool_shared_terrain_v2_20261016.py')
        template_proof.DOC = doc / 'parent-template-validation'
        def qualify_template(patch):
            from float32_coverage import approve_roundoff
            from native_patch_resolution import projected_context
            _, polygons, _, _ = projected_context(patch, bounds)
            if shapely.union_all(polygons).symmetric_difference(domain).area:
                save(doc / 'parent-template-coverage.json', approve_roundoff(patch, bounds))
            template_proof.overlap_proof(patch, [local / 'parent.json', capturetool, Path(__file__)])
        template = builder.make_patch(dict(cells=cells, uids=[args.uid]), parent, baseline, [], parent_sha256=digest(rootpath.read_bytes()), prepare_validation=qualify_template)
        save(local / 'parent-template.json', template)
        from terrain_parent_template_basis_v1 import validated_template_faces
        captured_baseline_faces = len(baseline)
        baseline = validated_template_faces(template, parent)
        basis_path = local / 'parent-template.json'
        save(doc / 'parent-template-basis.json', dict(
            path=str(basis_path.relative_to(ROOT)), sha256=digest(basis_path.read_bytes()),
            capturedParentFaces=captured_baseline_faces, validatedTemplateFaces=len(baseline),
            policy='Use the full validated coarse-parent edge return as the inset basis. Changes outside the source inset include that return; all affected-actor and final terrain checks remain required.',
            installationApproved=False))
        refs.append(HERE / 'terrain_parent_template_basis_v1.py')
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
        original_upper = np.asarray(upper)
        save(local / 'original-upper.json.gz', original_upper.tolist())
        refs.append(local / 'original-upper.json.gz')
        from clamped_original_terrain_v4_20261026 import clamp_surface
        save(local / 'original-upper-planes.json.gz', [planes[i].tolist() for i in upperlineage])
        refs.append(local / 'original-upper-planes.json.gz')
        source, clamp_proof = clamp_surface(original_upper, floor=1.2, source_planes=[planes[i] for i in upperlineage])
        save(doc / 'existing-height-floor.json', clamp_proof)
        # Recompute every affine piece after exact level-set partitioning.
        planes = [np.asarray(p) for p in clamp_proof['outputAffinePlanes']]
        polygons = shapely.polygons(source[:, :, [0, 2]])
        assert abs(float(shapely.area(polygons).sum()-shapely.union_all(polygons).area)) < 1e-6
        assert shapely.union_all(polygons).symmetric_difference(union).area < 1e-6
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
            sectors.append((polygon, blend_sector(xz, weights)))
        output, lineage, changed = [], [], []
        floor_roundoff = []
        removed = inserted = 0.
        for i, face in enumerate(baseline):
            polygon = shapely.Polygon(face[:, [0, 2]])
            if polygon.area <= 1e-10 or not polygon.intersects(outer):
                output.append(face)
                lineage.append(dict(kind='unchanged', validatedTemplateFace=i))
                continue
            parentplane, cuts, added = plane(face), [], []
            for j in tree.query(polygon, predicate='intersects'):
                intersection = polygon.intersection(polygons[j])
                if intersection.area <= 1e-10:
                    continue
                lower = lower_region(intersection, parentplane-planes[j])
                if lower.area <= 1e-10:
                    continue
                cuts.append(lower)
                for region, weightplane in sectors:
                    for part in lift(lower.intersection(region), planes[j]):
                        if weightplane is not None:
                            weights = blend_evaluate(part[:, [0, 2]], weightplane)
                            oldheight = part[:, [0, 2]] @ parentplane[:2]+parentplane[2]
                            part[:, 1] = part[:, 1]*(1-weights)+oldheight*weights
                        minimum_before = float(part[:, 1].min())
                        assert minimum_before >= 1.2-1e-10, ('real-floor-violation', minimum_before, part.tolist())
                        if minimum_before < 1.2:
                            floor_roundoff.append(dict(validatedTemplateFace=i, sourceFace=int(j), maximumCorrectionM=1.2-minimum_before))
                        # Explicit max field also applies at shared return vertices;
                        # retain the exact existing final floor assertion.
                        part[:, 1] = np.maximum(part[:, 1], 1.2)
                        assert part[:, 1].min() >= 1.2, 'new-inset-surface-below-existing-clamp'
                        added.append((part, int(j)))
            if not cuts:
                output.append(face)
                lineage.append(dict(kind='unchanged', validatedTemplateFace=i))
                continue
            cut = shapely.union_all(cuts)
            removed += cut.area
            changed.append(i)
            for part in parent_fragment_lift(polygon.difference(cut), parentplane):
                output.append(part)
                lineage.append(dict(kind='parent-fragment', validatedTemplateFace=i))
            for part, j in added:
                output.append(part)
                lineage.append(dict(kind='original-inset-or-return', validatedTemplateFace=i, sourceFace=j))
                inserted += shapely.Polygon(part[:, [0, 2]]).area
        save(doc / 'return-floor-roundoff.json', dict(policy='explicit-existing-floor-at-return-vertices', corrections=floor_roundoff, maximumPermittedCorrectionM=1e-10, finalHeightFloorM=1.2, globalValidatorChanged=False))
        assert abs(removed-inserted) < 1e-6
        output = np.asarray(output)
        template['nativeMesh']['source'].pop('numericalCoverageGap', None)
        template['nativeMesh']['position'] = output.reshape(-1).tolist()
        template['nativeMesh']['index'] = list(range(output.size//3))
        template['meta']['source']['nativeSources'] = source_refs
        policy = 'Original highest source terrain with existing1.2m sea-level floor, lower inset within model projection+1m and a shared piecewise-affine3m return. Validated coarse-parent edge return retained outside the original inset; original model bytes/pose unchanged.'
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
    assert digest(manifestpath.read_bytes()) == selection['manifestSHA256']
    save(doc / 'summary.json', result)
    refs.extend(path for path in local.rglob('*') if path.is_file())
    refs.extend([HERE / 'ronsdale_local_inset_v2_20261022.py', HERE / 'china_merchants_finite_inset_v4_20261021.py', HERE / 'xl-second-pass.py', HERE / 'resolve_pass_indexed_parent_clipping_v2.py', HERE / 'sham_shui_po_pool_shared_terrain_v2_20261016.py', HERE / 'float32_coverage.py', HERE / 'native_patch_resolution.py'])
    module('selected_inset_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'bounded-selected-original-terrain-inset', list(dict.fromkeys(refs)), result)
    print(result, flush=True)


if __name__ == '__main__':
    main()
