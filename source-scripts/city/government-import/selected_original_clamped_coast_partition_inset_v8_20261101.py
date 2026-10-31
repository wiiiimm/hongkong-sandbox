"""V8: exact source inset on an authenticated corrected private terrain parent.

Uses the established Ronsdale plane/upper-envelope method. All existing final
validators and the 1.2m source-height gate remain. Exact old low parent facets
outside the edit use the existing v14 preservation proof; no model geometry edits.
"""
import argparse
from collections import Counter
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
    for key in ['batch', 'capture', 'terrain-check', 'context']:
        parser.add_argument('--' + key, required=True)
    parser.add_argument('--uid', action='append', required=True)
    parser.add_argument('--preserve-context', help='Authenticated current model-only scope for retained BASIC ground')
    parser.add_argument('--preserve-uid', action='append', default=[])
    parser.add_argument('--preserve-fallback-uid', action='append', default=[], help='Selected original own unchanged BASIC fallback; preserves its current ground')
    parser.add_argument('--private-parent', required=True, help='Authenticated corrected private terrain to retain outside the new source edit')
    args = parser.parse_args()
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc, local = base / args.batch, HERE / 'local' / args.batch
    assert not doc.exists() and not local.exists()
    refs, pins = [Path(__file__), HERE / 'affine_terrain_blend_v1.py', HERE / 'inherited_parent_coverage_v1.py', HERE / 'clamped_original_terrain_v4_20261026.py'], {}
    historical_ground_manifest = None
    protected_uids=args.preserve_uid+args.preserve_fallback_uid
    assert bool(args.preserve_context)==bool(protected_uids)
    assert len(protected_uids)==len(set(protected_uids))<=8
    for name in [args.capture, args.terrain_check, args.context, args.private_parent]+([args.preserve_context] if args.preserve_context else []):
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
    wanted=set(args.uid)
    assert 0<len(wanted)==len(args.uid)<=8
    selected=[r for r in selection['rows'] if r['uid'] in wanted]
    assert {r['uid'] for r in selected}==wanted
    runtime={r['uid']:r for r in take(HERE/'local'/args.capture/'runtime-geometry.json.gz')['rows']}
    checked_rows={r['uid']:r for r in take(base/args.terrain_check/'summary.json')['rows']}
    projections=[];face_scopes=[];source_paths=None
    for row in selected:
        uid=row['uid'];g=runtime[uid];checked=checked_rows[uid]
        assert row['sourceSHA256']==g['sourceSHA256']==checked['sourceSHA256']
        assert checked['nativeResultSHA256']==row['native']['resultSha']
        paths=sorted(checked['sourceTerrainPaths'])
        if source_paths is None:source_paths=paths
        else:assert source_paths==paths, 'Paired inset requires identical authenticated source terrain members'
        asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset)
        tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
        assert len(tri)==row['triangles']
        context=take(base/args.context/(uid.split('/')[1]+'.json'))
        assert context['uid']==uid and context['sourceSHA256']==row['sourceSHA256']
        faces=list(context['buriedFaces']);ids=[f['faceIndex']for f in faces]
        assert ids and len(ids)==len(set(ids))and all(type(i)is int and 0<=i<len(tri)for i in ids)
        for f in faces:
            assert np.array_equal(np.asarray(f['vertices']),tri[f['faceIndex']])
            t=tri[f['faceIndex']];normal=np.cross(t[1]-t[0],t[2]-t[0]);assert bool(f['upward'])==bool(normal[1]>.25*np.linalg.norm(normal))
        projections.extend(shapely.MultiPoint(f[:,[0,2]]).convex_hull for f in tri[ids])
        face_scopes.append(dict(uid=uid,sourceSHA256=row['sourceSHA256'],completeSourceFaces=len(tri),selectedWhollyBuriedFaceIds=ids))
    save(doc/'original-face-scope.json',dict(rows=face_scopes,qualification='All exact buried facets nominate locality only. Complete source validation remains required for every member; source floor and parent/water guards unchanged.'))
    projection=shapely.union_all(projections)
    assert projection.area>0

    core = projection.buffer(1, join_style='mitre')
    outer = core.buffer(3, join_style='mitre')
    rootpath = ROOT / '3d-viewer/city/data/terrain.json'
    parent = read(rootpath)
    refs.append(rootpath)
    georef, size = parent['meta']['georef'], parent['cell']
    a, b, c, d = outer.bounds
    cells = [math.floor((a-.001+834500-georef['bE'])/size), math.floor((b-.001-816500+georef['bN'])/size), math.ceil((c+.001+834500-georef['bE'])/size), math.ceil((d+.001-816500+georef['bN'])/size)]
    private_receipt, private_pins = authenticate(base/args.private_parent)
    assert private_receipt['status']=='private-terrain-validator-passed' and not private_receipt.get('replacedNativeTerrain')
    private_path=ROOT/private_receipt['candidate']['path'];private_node=take(private_path)
    assert digest(private_path.read_bytes())==private_receipt['candidate']['sha256']
    assert private_node.get('nativeMesh') and not private_node.get('patches') and not private_node.get('hydro')
    assert private_node['meta']['parentTerrain']=='city/data/terrain.json' and private_node['meta']['parentSha256']==digest(rootpath.read_bytes())
    retained=set(private_node['meta']['targetUids']);assert retained==set(private_receipt['uids']) and retained and not wanted.intersection(retained)
    by_uid={r['uid']:r for r in selection['rows']};assert retained<=by_uid.keys()
    for u in retained:
        r=by_uid[u];assert r['sourceSHA256']==private_receipt['sourceSHA256ByUid'][u]
        asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];refs.append(asset)
    targets=sorted(wanted|retained)
    oldcells=private_node['coarseCells'];cells=[min(cells[0],oldcells[0]),min(cells[1],oldcells[1]),max(cells[2],oldcells[2]),max(cells[3],oldcells[3])]
    assert 0<=cells[0]<cells[2]<parent['w'] and 0<=cells[1]<cells[3]<parent['h']
    builder = module('selected_inset_builder', HERE / 'resolve_pass_indexed_parent_clipping_v2.py')
    bounds = builder.extent(cells, parent)
    domain = shapely.box(*bounds)
    assert domain.covers(outer) and outer.distance(domain.boundary) > 0
    save(doc / 'scope.json', dict(uids=targets, cells=cells, bounds=bounds, coreBounds=list(core.bounds), outerBounds=list(outer.bounds)))
    result = dict(uids=targets, editedSourceUids=sorted(wanted), retainedPrivateParentUids=sorted(retained), sourceSHA256ByUid={u:by_uid[u]['sourceSHA256']for u in targets}, retainedPrivateParent=private_receipt['candidate'], installationApproved=False, publication=False, newlyInstalled=0, sourceGeometryChanges=0, scriptExternalAICalls=0)
    try:
        capturetool=HERE/'selected_original_parent_capture_v3.mjs'
        save(doc/'private-parent-candidates.json',[private_receipt['candidate']])
        subprocess.run(['node',str(capturetool),str((doc/'scope.json').relative_to(ROOT)),str((local/'parent.json').relative_to(ROOT)),str((doc/'private-parent-candidates.json').relative_to(ROOT))],cwd=ROOT,check=True)
        captured = read(local / 'parent.json')
        refs.extend([capturetool, local / 'parent.json'])
        for name, sha in captured['inputHashes'].items():
            assert digest((ROOT / name).read_bytes()) == sha
            refs.append(ROOT / name)
        assert captured['domain']==bounds and captured['inputHashes'][str(private_path.relative_to(ROOT))]==private_receipt['candidate']['sha256']
        baseline = np.asarray(captured['triangles'])
        # Exactly repartition mixed old coast triangles before selecting an
        # inland-only edit. No parent height, plane, winding or surface changes.
        from exact_private_parent_partition_v1_20261101 import partition_bound_parent
        baseline, partition_proof = partition_bound_parent(baseline,private_node)
        save(doc / 'exact-parent-surface-partition.json', partition_proof)
        refs.extend(HERE/n for n in ['exact_private_parent_partition_v1_20261101.py','test_exact_private_parent_partition_v1_20261101.py','exact_float32_parent_level_partition_v3_20261101.py','test_exact_float32_parent_level_partition_v3_20261101.py','exact_float32_parent_level_partition_v2_20261031.py'])
        private_output=set(partition_proof['retainedPrivateOutputFaceIds'])
        finite=[i for i,face in enumerate(baseline)if np.cross(face[1]-face[0],face[2]-face[0])[1]!=0]
        production=[i for i in finite if i not in private_output]
        private_finite=[i for i in finite if i in private_output]
        assert private_finite and all(baseline[i,:,1].min()>=float(np.float32(1.2))for i in private_output)
        # Production coast uses the unchanged old level/3m-gradient bound.
        # Inherited private faces have a stronger full affine lower bound:
        # every represented vertex is already >=Float32(1.2). New edits are
        # lower-only and source-clamped >=1.2; zero-XZ faces remain untouched.
        gradients = [float(np.linalg.norm(plane(baseline[i])[:2])) for i in production] or [0.]
        threshold = partition_proof['levelM'] + 3 * max(gradients) + .001
        from exact_affine_halfplane_clip_v1_20261024 import lower_region as exact_positive_region
        allowed = shapely.union_all([exact_positive_region(shapely.Polygon(baseline[i][:,[0,2]]),plane(baseline[i])-np.array([0.,0.,threshold]))for i in production]+[shapely.Polygon(baseline[i][:,[0,2]])for i in private_finite])
        save(doc/'private-parent-height-domain.json',dict(privateMinimumRenderedY=partition_proof['privateMinimumRenderedY'],privateAffineFloorProvedByAllVertices=True,privateFiniteFacets=len(private_finite),productionFiniteFacets=len(production),productionMaximumGradient=max(gradients),productionThresholdM=threshold,zeroProjectionFacesRetainedNotHeightIndexed=True,newSourceHeightFloorM=1.2,lowFaceEditProtectionStillRequired=True,installationApproved=False))
        old_core, old_projection = core, projection
        core = core.intersection(allowed)
        assert core.area > 0 and old_core.covers(core)
        if protected_uids:
            assert not wanted.intersection(args.preserve_uid)
            assert set(args.preserve_fallback_uid).issubset(wanted)
            scope=take(base/args.preserve_context/'summary.json')
            assert scope['currentManifestSHA256']==selection['manifestSHA256']
            source_forms={}
            for uid in scope['uids']:
                for form in take(base/args.preserve_context/(uid.split('/')[1]+'-forms.json.gz')):
                    source_forms[form['building']['uid']]=form
            protected=[];protected_rows=[];requested=set(protected_uids)
            for uid in protected_uids:
                form=source_forms[uid];building=form['building'];tile=ROOT/'3d-viewer'/form['tile']
                assert digest(tile.read_bytes())==form['tileSHA256']
                assert next(b for b in read(tile)['buildings']if b['uid']==uid)==building
                assert not building.get('modelGeometry');refs.append(tile)
                polygon=shapely.Polygon(building['rings'][0],building['rings'][1:])
                assert polygon.is_valid and polygon.area>0
                protected.append(polygon);protected_rows.append(dict(uid=uid,sourceForm=building,tileSHA256=form['tileSHA256'],footprintWKT=polygon.wkt,selectedOwnFallback=uid in args.preserve_fallback_uid))
            for url in read(manifestpath)['officialModelCatalogues']:
                path=ROOT/'3d-viewer'/url;refs.append(path)
                for model in read(path)['models']:
                    assert model['uid']not in requested and not requested.intersection(model.get('suppressesBuildingUids',[]))
            protected=shapely.union_all(protected)
            # Locality margin only: no validator tolerance is changed. Retained
            # BASIC ground remains outside the existing three-metre return.
            core=core.difference(protected.buffer(3.05,join_style='mitre'))
            # Shrink the proposed edit domain by 1mm before strict containment;
            # this changes locality, never a validator tolerance or source vertex.
            core=core.buffer(-.001,join_style='mitre')
            assert core.area>0 and old_core.covers(core)
            protected_outer=core.buffer(3,join_style='bevel')
            assert not protected_outer.intersects(protected)
            save(doc/'retained-basic-ground-domain.json',dict(rows=protected_rows,minimumDistanceFromEditM=protected.distance(protected_outer),strictlyOutsideEdit=True,completeSourceValidationStillRequired=True,installationApproved=False))
        outer = core.buffer(3, join_style='bevel')
        assert domain.covers(outer) and outer.distance(domain.boundary) > 0
        projection = old_projection.intersection(core)
        assert projection.area > 0
        save(doc / 'refined-edit-scope.json', dict(originalCoreWKT=old_core.wkt, actualCoreWKT=core.wkt, actualOuterWKT=outer.wkt, selectedProjectionOutsideEditAreaM2=old_projection.difference(core).area, parentPartitionLevelM=partition_proof['levelM'], maximumParentGradient=max(gradients), inlandCoreMinimumParentM=threshold, completeSourceValidationStillRequired=True, installationApproved=False))
        refs.append(HERE / 'exact_affine_halfplane_clip_v1_20261024.py')
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
        template = builder.make_patch(dict(cells=cells, uids=targets), parent, baseline, [], parent_sha256=digest(rootpath.read_bytes()), allow_native_below_clamp=bool(low_binding['faceIds']), prepare_validation=qualify_template)
        save(local / 'parent-template.json', template)
        from terrain_parent_template_basis_v1 import validated_template_faces
        captured_baseline_faces = len(baseline)
        assert partition_proof['parentSurfaceExactlyUnchanged']
        # Retain the actual corrected parent rather than applying a second
        # coarse-edge blend. Final actual output still passes builder validation.
        baseline = captured_baseline
        basis_path = local / 'parent-template.json'
        save(doc / 'parent-template-basis.json', dict(
            path=str(basis_path.relative_to(ROOT)), sha256=digest(basis_path.read_bytes()),
            capturedParentFaces=captured_baseline_faces, validatedTemplateFaces=len(baseline),
            policy='Actual complete corrected private parent, with exact represented facet retention. Metadata template is ordinarily validated; its second edge blend is not used as the baseline. Final actual output must pass the same complete validator.',templateGeometryUsedAsBaseline=False,
            installationApproved=False))
        refs.append(HERE / 'terrain_parent_template_basis_v1.py')
        decoder = module('selected_inset_source', HERE / 'xl-second-pass.py')
        decoder.LOCAL = local
        source, source_refs = [], []
        for name in source_paths:
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
        outside=[i for i,f in enumerate(baseline) if shapely.Polygon(f[:,[0,2]]).area<=1e-10 or not shapely.Polygon(f[:,[0,2]]).intersects(outer)]
        expected=Counter(np.asarray(baseline[i],dtype='<f4').tobytes()for i in outside)
        outside_ids=set(outside)
        observed=Counter(np.asarray(output[k],dtype='<f4').tobytes()for k,r in enumerate(lineage)if r['kind']=='unchanged' and r['validatedTemplateFace']in outside_ids)
        assert expected==observed, 'Corrected private parent changed outside the actual source edit'
        save(doc/'private-parent-retention.json',dict(retainedPrivateParent=private_receipt['candidate'],retainedUids=sorted(retained),editedUids=sorted(wanted),outsideParentFacets=len(outside),exactFloat32OutsideFaceMultiplicityPreserved=True,allParentFacetsAccounted=len(baseline),outputFaces=len(output),installationApproved=False,qualification='Complete captured private parent is the baseline. Existing exact coast partition preserves surfaces; all post-partition facets outside the actual edit are retained byte-identically at rendered Float32 precision. Full later source/ground/seam/current-scene checks remain required.'))
        template['meta']['source']['retainedPrivateParent']=dict(candidate=private_receipt['candidate'],sourceSHA256ByUid={u:by_uid[u]['sourceSHA256']for u in retained},sourceMetadata=private_node['meta']['source'],parentCaptureTool='selected_original_parent_capture_v3.mjs')
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
        save(doc / 'unchanged-low-parent-proof.json', verify_low(output, low_binding))
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
