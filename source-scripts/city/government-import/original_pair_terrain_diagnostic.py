"""Build a diagnostic original TIN candidate for exact independently grounded parts.

No identity approval. Reuses established terrain construction, coverage, seam,
parent-boundary and overlap guards without modifying any government model.
"""
import importlib.util
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import box
from run import ROOT, HERE, read, save, digest


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def build(rows, doc, local):
    second = module('independent_pair_terrain_decoder', 'xl-second-pass.py')
    second.LOCAL = local
    acquisition = module('independent_pair_terrain_cache', 'xl-indexed-terrain-continuation.py')
    patches = module('independent_pair_terrain_patches', 'native_patch_resolution.py')
    parent_path = ROOT / '3d-viewer/city/data/terrain.json'
    parent = read(parent_path)
    world = [r['native']['model']['worldBounds'] for r in rows]
    rectangles = [second.resolution.rectangle_for(b, parent) for b in world]
    cells = [min(r[0] for r in rectangles), min(r[1] for r in rectangles),
        max(r[2] for r in rectangles), max(r[3] for r in rectangles)]
    bounds = second.resolution.extent(cells, parent)
    for entry in read(ROOT / '3d-viewer/city/data/manifest.json')['terrainPatches']:
        other = read(ROOT / '3d-viewer' / entry['url'])
        assert box(*bounds).intersection(box(*patches._patch_bounds(other))).area <= 1e-8, 'Retained terrain needs a separate route'
    from terrain_source_preflight import SourceSheetIndex
    index = SourceSheetIndex(read(ROOT / 'source-scripts/city/landmark-acquisition/index.json'))
    sheets = sorted({s['sheet'] for b in world for s in index.covering_sheets(b)})
    fragments, files, used, recoveries = [], [], [], []
    for sheet in sheets:
        folder, recovery = acquisition.terrain_sheet(sheet, local)
        recoveries.append(recovery)
        receipt, entries = acquisition.verified_terrain(folder)
        source_files = [{'path': str((folder / 'terrain' / e['name']).relative_to(ROOT)),
            'sha256': e['sha256']} for e in entries]
        files.extend(source_files)
        fragments.extend(second.terrain_triangles(p) for p in sorted((folder / 'terrain').rglob('*.gltf')))
        used.append({'sheet': sheet, 'revision': receipt['revisionDate'], 'sourceETag': receipt['sourceETag'],
            'directorySHA256': receipt['directorySHA256'], 'sourceFiles': source_files})
    save(doc / 'source-recovery.json', {'rows': recoveries, 'modelGeometryChanges': 0})
    native = np.concatenate(fragments)
    native = native[(native[:, :, 0].max(axis=1) >= bounds[0]) & (native[:, :, 0].min(axis=1) <= bounds[2]) &
        (native[:, :, 2].max(axis=1) >= bounds[1]) & (native[:, :, 2].min(axis=1) <= bounds[3])]
    assert len(native)
    models = [second.glb_triangles(r) for r in rows]
    projection = shapely.union_all([shapely.union_all(shapely.polygons(t[:, :, [0, 2]])) for t in models])
    low = native[:, :, 1].min(axis=1) < 1.2
    low_area = float(shapely.union_all(shapely.polygons(native[low][:, :, [0, 2]])).intersection(projection).area) if low.any() else 0
    if low.any() and low_area < 1e-6:
        native = native[~low]
    core = [min(b[0][0] for b in world)-1, min(b[0][2] for b in world)-1,
        max(b[1][0] for b in world)+1, max(b[1][2] for b in world)+1]
    validator = second.resolution.validate_patch
    second.resolution.validate_patch = lambda *_: None
    try:
        patch = second.resolution.make_patch({'uids': [r['uid'] for r in rows], 'cells': cells}, parent, native, used,
            native_core=core, terrain_triangle_budget=100000, allow_native_below_clamp=low_area >= 1e-6,
            parent_url='city/data/terrain.json', parent_sha256=digest(parent_path.read_bytes()))
    finally:
        second.resolution.validate_patch = validator
    sampler = second.resolution.terrain.fine.DemSampler(parent, rendered=True)
    gap = patches.projected_context(patch, bounds)[2].intersection(projection)
    fill = patches.fill_narrow_source_seam(patch, bounds, projection, sampler, tolerance=.02) if gap.area > 1e-6 else patches.fill_parent_only_holes(patch, parent, bounds, projection, sampler)
    remaining = float(patches.projected_context(patch, bounds)[2].area)
    maximum = max(.25, (bounds[2]-bounds[0])*(bounds[3]-bounds[1])*1e-3)
    assert remaining <= maximum
    if remaining > 1e-8:
        patch['nativeMesh']['source']['numericalCoverageGap'] = {'policy': 'parent-grid-fallback',
            'measuredAreaM2': remaining, 'maximumAreaM2': maximum, 'maximumFraction': 1e-3}
    patch['nativeMesh']['source']['finalBoundarySnap'] = patches.snap_boundary_to_parent(patch, bounds, sampler)
    target = local / (patch['id'] + '.json')
    save(target, patch)
    if patches.projected_context(patch, bounds)[3] > 1e-8:
        patches.approve_original_overlap(patch, target, doc / 'native-overlap.json', files)
        patches.finalize_overlap_evidence(patch, doc / 'native-overlap.json')
    validator(patch, parent)
    save(target, patch)
    candidate = {'path': str(target.relative_to(ROOT)), 'sha256': digest(target.read_bytes()),
        'uids': [r['uid'] for r in rows], 'bounds': bounds, 'triangles': len(patch['nativeMesh']['index'])//3}
    save(doc / 'terrain-candidates.json', [candidate])
    save(doc / 'terrain.json', {'patch': candidate, 'sourceFiles': files, 'parentHoleFill': fill,
        'publication': False, 'modelGeometryChanges': 0, 'qualification': 'Original source TIN diagnostic only; identity and all physical/neighbour/publication checks remain required.'})
