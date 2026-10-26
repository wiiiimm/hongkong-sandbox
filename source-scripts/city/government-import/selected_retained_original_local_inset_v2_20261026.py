"""Original-TIN inset inside an exact complete installed terrain envelope.

Uses the established Ronsdale plane/upper-envelope method, retaining each
original source plane through clipping instead of refitting tiny derived faces. All existing final
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
from ronsdale_local_inset_v2_20261022 import plane, lift, parent_fragment_lift
from exact_affine_halfplane_clip_v2_20261024 import lower_region
from affine_terrain_blend_v1 import sector as blend_sector, evaluate as blend_evaluate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'capture', 'terrain-check', 'uid']:
        parser.add_argument('--' + key, required=True)
    parser.add_argument('--companion',action='append',default=[],help='Explicit complete original whose footprint needs the same terrain inset')
    parser.add_argument('--cover-native',action='append',default=[],help='Current native terrain URL whose complete coarse extent and target obligations must be retained')
    parser.add_argument('--parent-capture', help='Completed prior diagnostic with identical current renderer inputs/domain')
    args = parser.parse_args()
    assert len(args.cover_native)==1, "Retained-envelope route requires exactly one complete installed terrain"
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc, local = base / args.batch, HERE / 'local' / args.batch
    assert not doc.exists() and not local.exists()
    refs, pins = [Path(__file__), HERE / 'affine_terrain_blend_v1.py', HERE / 'inherited_parent_coverage_v1.py', HERE / 'exact_affine_halfplane_clip_v2_20261024.py'], {}
    historical_ground_manifest = None
    for name in [args.capture, args.terrain_check]:
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
    wanted=[args.uid,*args.companion]
    assert len(wanted)==len(set(wanted)) and len(wanted)<=8
    geometries=take(HERE / 'local' / args.capture / 'runtime-geometry.json.gz')['rows']
    complete=[];source_hashes={}
    for uid in wanted:
        source=next(r for r in selected if r['uid']==uid)
        geometry=next(r for r in geometries if r['uid']==uid)
        path=ROOT/source['candidate']['path']
        assert digest(path.read_bytes())==source['sourceSHA256']==geometry['sourceSHA256']
        refs.append(path);source_hashes[uid]=source['sourceSHA256']
        faces=np.asarray(geometry['position']).reshape(-1,3)[np.asarray(geometry['index']).reshape(-1,3)]
        assert len(faces)==source['triangles']
        complete.append(faces)
    tri=np.concatenate(complete)
    projection = shapely.union_all([shapely.MultiPoint(f[:, [0, 2]]).convex_hull for f in tri])
    core = projection.buffer(1, join_style='mitre')
    outer = core.buffer(3, join_style='mitre')
    rootpath = ROOT / '3d-viewer/city/data/terrain.json'
    parent = read(rootpath)
    refs.append(rootpath)
    georef, size = parent['meta']['georef'], parent['cell']
    a, b, c, d = outer.bounds
    cells = [math.floor((a-.001+834500-georef['bE'])/size), math.floor((b-.001-816500+georef['bN'])/size), math.ceil((c+.001+834500-georef['bE'])/size), math.ceil((d+.001-816500+georef['bN'])/size)]
    retained_targets=set();replacement_records=[]
    current=read(manifestpath);urls={r['url']if isinstance(r,dict)else r for r in current.get('terrainPatches',[])}
    assert len(args.cover_native)==len(set(args.cover_native))
    for url in args.cover_native:
        assert url in urls
        path=(ROOT/'3d-viewer'/url).resolve();assert path.is_relative_to((ROOT/'3d-viewer/city/data').resolve())
        previous=read(path);assert previous.get('nativeMesh')and previous['meta']['parentTerrain']=='city/data/terrain.json'
        assert previous['meta']['parentSha256']==digest(rootpath.read_bytes())
        assert not previous['nativeMesh'].get('source',{}).get('coordinatedBoundary'),'A coordinated mate requires its own complete paired proof'
        old=previous['coarseCells'];assert len(old)==4 and all(type(n)is int for n in old)
        cells=[min(cells[0],old[0]),min(cells[1],old[1]),max(cells[2],old[2]),max(cells[3],old[3])]
        retained_targets.update(previous['meta']['targetUids']);refs.append(path)
        replacement_records.append(dict(url=url,path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),coarseCells=old,targetUids=previous['meta']['targetUids']))
    if args.cover_native:
        # Any further cut native would recreate the same unbound outer seam.
        for url in urls:
            path=ROOT/'3d-viewer'/url;other=read(path)
            if not other.get('nativeMesh')or other['meta'].get('parentTerrain')!='city/data/terrain.json':continue
            old=other['coarseCells']
            intersects=min(cells[2],old[2])>max(cells[0],old[0])and min(cells[3],old[3])>max(cells[1],old[1])
            if intersects:
                assert cells[0]<=old[0]<old[2]<=cells[2]and cells[1]<=old[1]<old[3]<=cells[3],'Expanded domain cuts another native boundary'
                assert url in args.cover_native,'Every replaced native terrain needs explicit full obligations'
        save(doc/'retained-native-terrain-obligations.json',dict(records=replacement_records,allPreviousTargetsRetained=True,sourceGeometryChanges=0,publication=False))
    builder = module('selected_inset_builder', HERE / 'resolve_pass_indexed_parent_clipping_v2.py')
    bounds = builder.extent(cells, parent)
    domain = shapely.box(*bounds)
    assert domain.covers(outer) and outer.distance(domain.boundary) > 0
    save(doc / 'scope.json', dict(uids=wanted, cells=cells, bounds=bounds, coreBounds=list(core.bounds), outerBounds=list(outer.bounds)))
    result = dict(uids=wanted,sourceSHA256ByUid=source_hashes,completeSourceFaces=len(tri), installationApproved=False, publication=False, newlyInstalled=0, sourceGeometryChanges=0, scriptExternalAICalls=0)
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
        from unchanged_low_parent_faces_v1_20261024 import bind as bind_low, verify as verify_low
        low_binding = bind_low(baseline, outer)
        captured_baseline = baseline.copy()
        refs.append(HERE / 'unchanged_low_parent_faces_v1_20261024.py')
        from retained_native_template_v3_20261023 import reuse_template
        template = reuse_template(cells, parent, baseline, replacement_records, outer, doc, local, builder)
        template['meta']['targetUids']=sorted(set(template['meta']['targetUids'])|set(wanted))
        save(local / 'parent-template.json', template)
        retained_baseline_faces=len(baseline)
        save(doc / 'parent-template-basis.json', dict(
            capturedParentFaces=len(baseline), validatedTemplateFaces=len(baseline),
            exactExistingEnvelopeReused=True,
            policy='Exact complete existing Float32 face multiset reused, including multiplicity. No rebuilding or new whole-template triangle credit. All ordinary surface validators and low-face preservation remain required.',
            installationApproved=False))
        refs.append(HERE / 'retained_native_template_v3_20261023.py')
        decoder = module('selected_inset_source', HERE / 'xl-second-pass.py')
        decoder.LOCAL = local
        source, source_refs, source_planes = [], [], []
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
                    # Keep the authored source plane through clipping. Tiny derived
                    # triangles can be ill-conditioned for a second plane fit;
                    # no clipped primitive or source facet is discarded here.
                    coefficients = plane(face)
                    parts = lift(polygon.intersection(outer), coefficients)
                    source.extend(parts)
                    source_planes.extend(coefficients.copy() for _ in parts)
        source = np.asarray(source)
        polygons = shapely.polygons(source[:, :, [0, 2]])
        union = shapely.union_all(polygons)
        assert projection.difference(union).area < 1e-6, 'Original terrain does not cover the complete model projection'
        assert len(source_planes) == len(source)
        planes = source_planes
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
            sectors.append((polygon, blend_sector(xz, weights)))
        output, lineage, changed = [], [], []
        removed = inserted = 0.
        area_cases = []
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
                        assert part[:, 1].min() >= 1.2, 'new-inset-surface-below-existing-clamp'
                        added.append((part, int(j)))
            if not cuts:
                output.append(face)
                lineage.append(dict(kind='unchanged', parentFace=i))
                continue
            cut = shapely.union_all(cuts)
            local_inserted = sum(shapely.Polygon(part[:, [0, 2]]).area for part, _ in added)
            if abs(cut.area-local_inserted) > 1e-9:
                area_cases.append(dict(parentFace=i, removedAreaM2=cut.area, insertedAreaM2=local_inserted, signedDifferenceM2=cut.area-local_inserted, parentTriangle=face.tolist(), cutWKT=cut.wkt, insertedTriangles=[part.tolist() for part, _ in added], sourceFaceIds=[j for _, j in added]))
            removed += cut.area
            changed.append(i)
            for part in parent_fragment_lift(polygon.difference(cut), parentplane):
                output.append(part)
                lineage.append(dict(kind='parent-fragment', parentFace=i))
            for part, j in added:
                output.append(part)
                lineage.append(dict(kind='original-inset-or-return', parentFace=i, sourceFace=j))
                inserted += shapely.Polygon(part[:, [0, 2]]).area
        save(doc / 'area-conservation-diagnostic.json.gz', dict(removedAreaM2=removed, insertedAreaM2=inserted, signedDifferenceM2=removed-inserted, existingLimitM2=1e-6, allLocalDiscrepanciesAboveOneBillionthM2=area_cases, toleranceChanged=False, installationApproved=False))
        assert abs(removed-inserted) < 1e-6
        output = np.asarray(output)
        template['nativeMesh']['source'].pop('numericalCoverageGap', None)
        template['nativeMesh']['position'] = output.reshape(-1).tolist()
        template['nativeMesh']['index'] = list(range(output.size//3))
        template['meta']['source']['nativeSources'] = source_refs
        policy = 'Original highest source terrain, lower inset within model projection+1m and a shared piecewise-affine3m return. Exact existing low parent facets outside the edit remain unchanged; all original source, water-mask, coverage, boundary and runtime checks apply.'
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
        save(doc / 'unchanged-low-parent-proof.json', verify_low(output, low_binding))
        builder.validate_patch(template, parent)
        from retained_inset_work_budget_v1_20261026 import verify as verify_work
        budget=verify_work(baseline, output, lineage)
        save(doc/'retained-inset-work-budget.json',budget)
        refs.append(HERE/'retained_inset_work_budget_v1_20261026.py')
        path = local / 'candidate-terrain.json'
        save(path, template)
        save(doc / 'lineage.json.gz', dict(changedParentFaces=changed, sourceFaces=source.tolist(), outputLineage=lineage, coreWKT=core.wkt, outerWKT=outer.wkt, removedAreaM2=removed, insertedAreaM2=inserted))
        result.update(replacedNativeTerrain=replacement_records,retainedNativeTerrainTargets=sorted(retained_targets),status='private-terrain-validator-passed', candidate=dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())), terrainTriangles=len(output), changedParentFaces=len(changed))
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
