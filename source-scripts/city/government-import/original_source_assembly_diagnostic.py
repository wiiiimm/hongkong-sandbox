"""Bounded identity diagnostic for two explicitly pinned unchanged source parts.

Individual hard identity/pose/GeoRef checks remain mandatory. Individual spatial
failures stay in the evidence; this diagnostic tests the unchanged limits on the
complete same-building assembly and grants no identity or publication approval. Measure footprint
coverage over the verified same-building assembly, anchored by its original
strict tower/podium interface. This module does not publish or approve models.
"""
import hashlib
import numpy as np
import shapely
from shapely.geometry import Polygon

POLICY = 'exact-original-two-part-assembly-diagnostic-v1'
COVERAGE_REASONS = frozenset({
    'fresh-current-spatial-bound:targetCoveredBySourceProjection',
    'full-source-target-coverage',
    'full-source-maximum-extent',
    'full-source-unrelated-overlap',
    'fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM',
    'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2',
})


def evaluate(rows, individual, triangles, interface, forms, *, tower, podium):
    UIDS = frozenset({tower, podium})
    TOWER, PODIUM = tower, podium
    assert len(UIDS)==2 and all(u.startswith("landsd/") and u.endswith(":0") for u in UIDS)
    reasons = []
    by_uid = {r['uid']: r for r in rows}
    if len(rows) != 2 or set(by_uid) != UIDS:
        return {'policy': POLICY, 'passed': False, 'reasons': ['unscoped-source-group'],
                'installationApproved': False, 'modelGeometryChanges': 0}
    buildings = {u: r['source']['building'] for u, r in by_uid.items()}
    parents = {b.get('parent') for b in buildings.values()}
    references = [set(b.get('osmRefs', [])) for b in buildings.values()]
    if len(parents) != 1 or not next(iter(parents)) or not set.intersection(*references):
        reasons.append('different-or-missing-building-parent')
    if buildings[TOWER].get('structureType') != 'Tower' or buildings[PODIUM].get('structureType') != 'Podium':
        reasons.append('wrong-tower-podium-types')
    for key in ['objectId', 'buildingCSUID']:
        if len({b.get(key) for b in buildings.values()}) != 2 or any(b.get(key) is None for b in buildings.values()):
            reasons.append('nonunique-government-' + key)
    projections = []
    targets = []
    vertices = []
    for uid, row in by_uid.items():
        proof = individual[uid]
        if proof.get('sourceSHA256') != row['sourceSHA256']:
            reasons.append(uid + ':individual-source-hash')
        remaining = set(proof['reasons']) - COVERAGE_REASONS
        reasons.extend(uid + ':' + r for r in remaining)
        cell = proof.get('geographicCell', {})
        if not cell.get('targetCoversWholeCell') or not cell.get('originalProjectionCoversWholeCell'):
            reasons.append(uid + ':whole-georef-cell')
        tri = np.asarray(triangles[uid], dtype=float)
        if tri.shape != (row['triangles'], 3, 3) or not np.isfinite(tri).all():
            reasons.append(uid + ':invalid-full-source-geometry')
            continue
        sha = hashlib.sha256(tri.astype('<f8').tobytes()).hexdigest()
        if sha != proof.get('worldTrianglesSHA256'):
            reasons.append(uid + ':individual-world-geometry-hash')
        projections.append(shapely.union_all(shapely.polygons(tri[:, :, [0, 2]])))
        b = buildings[uid]
        targets.append(Polygon(b['rings'][0], b['rings'][1:]))
        vertices.append(tri[:, :, [0, 2]].reshape(-1, 2))
    contact = interface.get('interface', {})
    if (interface.get('uid') != TOWER or interface.get('supportUid') != PODIUM
            or interface.get('sourceSHA256') != by_uid[TOWER]['sourceSHA256']
            or interface.get('supportSHA256') != by_uid[PODIUM]['sourceSHA256']
            or not contact.get('passed') or not contact.get('samples')
            or contact.get('strictContacts') != contact.get('samples')
            or contact.get('wallIntersections') or contact.get('unresolved')):
        reasons.append('exact-original-support-interface')
    measures = {}
    if len(projections) == 2:
        source = shapely.union_all(projections)
        target = shapely.union_all(targets)
        if not source.is_valid or not target.is_valid or source.area <= 0 or target.area <= 0:
            reasons.append('invalid-full-compound-projection')
        else:
            coverage = source.intersection(target).area / target.area
            extent = float(shapely.distance(shapely.points(np.concatenate(vertices)), target).max())
            excess = source.difference(target)
            unrelated = []
            for b in forms:
                if b['uid'] not in UIDS and b.get('parent') not in parents:
                    unrelated.append(Polygon(b['rings'][0], b['rings'][1:]))
            unrelated_area = excess.intersection(shapely.union_all(unrelated)).area if unrelated else 0
            measures = {'targetCoveredBySourceProjection': coverage,
                        'sourceExcessMaximumDistanceFromTargetM': extent,
                        'sourceExcessCoveredByUnrelatedFormsM2': unrelated_area,
                        'sourceProjectionAreaM2': source.area, 'targetAreaM2': target.area}
            for key, lower, upper in [('targetCoveredBySourceProjection', .95, 1.000000001),
                                      ('sourceExcessMaximumDistanceFromTargetM', 0, 10),
                                      ('sourceExcessCoveredByUnrelatedFormsM2', 0, 1)]:
                if not lower <= measures[key] <= upper:
                    reasons.append('compound-spatial-bound:' + key)
    passed = not reasons
    return {'policy': POLICY, 'uids': sorted(UIDS), 'passed': passed,
            'reasons': sorted(set(reasons)), 'measures': measures,
            'rawIndividualIdentity': individual, 'strictOriginalInterface': interface,
            'sourceSHA256s': {u: r['sourceSHA256'] for u, r in by_uid.items()},
            'buildingParent': next(iter(parents)) if len(parents) == 1 else None,
            'installationApproved': False, 'diagnosticOnly': True, 'publication': False, 'modelGeometryChanges': 0,
            'qualification': 'Identity of this exact original same-building assembly only. '
            'All individual non-spatial identity, unique ID, byte, pose and whole GeoRef '
            'checks remain. Original strict support is mandatory. Existing 95% coverage, '
            '10m extent and 1m2 unrelated overlap bounds are measured over the complete '
            'assembly; preserve raw individual failures. Every physical, neighbour, '
            'runtime and browser/publication gate remains separate.'}


def verify_files(rows, contexts, local, interface):
    """Decode and verify current immutable originals and map forms afresh."""
    import importlib.util
    from pathlib import Path
    from run import HERE, ROOT, digest
    from government_georef_cell_identity import verify_files as individual_verify
    local = Path(local)
    individual = {r['uid']: individual_verify(r, contexts[r['uid']], local / r['uid'].split('/')[1])
                  for r in rows}
    for row in rows:
        raw = (ROOT / row['candidate']['path']).read_bytes()
        assert digest(raw) == row['sourceSHA256']
        asset = local / 'assets' / (row['sourceSHA256'] + '.glb.gz')
        asset.parent.mkdir(parents=True, exist_ok=True)
        asset.write_bytes(raw)
    spec = importlib.util.spec_from_file_location('pak_compound_decoder', HERE / 'xl-second-pass.py')
    decoder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(decoder)
    decoder.LOCAL = local
    triangles = {r['uid']: decoder.glb_triangles(r) for r in rows}
    spec = importlib.util.spec_from_file_location('pak_compound_current_forms', HERE / 'xl-final-script-pass.py')
    final = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(final)
    all_tri = np.concatenate(list(triangles.values()))
    lo, hi = all_tri.min(axis=(0, 1)), all_tri.max(axis=(0, 1))
    forms = []
    for b, _, tile in final.load_forms([lo[0]-2, lo[2]-2, hi[0]+2, hi[2]+2]):
        pinned = {sha for ctx in contexts.values()
                  for path, sha in ctx['neighbourTileHashes'].items() if path == tile}
        assert pinned == {digest((ROOT / '3d-viewer' / tile).read_bytes())}
        forms.append(b)
    return evaluate(rows, individual, triangles, interface, forms, tower=interface["uid"], podium=interface["supportUid"])

