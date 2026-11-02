"""Replay the exact reviewed adjoining-podium identity; no physical waiver.

This explicit adapter is not installed into the general identity checker. It
accepts only a fresh ordinary proof whose complete source, route, cell and
neighbour measurements match the frozen identity-only review. The current
manifest may differ: the ordinary checker must freshly bind it and all tiles.
"""
from copy import deepcopy
from pathlib import Path

ALLOWED = ['fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2',
           'full-source-unrelated-overlap']
REVIEW = 'government-xl-silvercord-lippo-bounded-identity-review-v2-20261101'
EXPECTED = {
    'landsd/233997:0': ('11b03482304ea9f139e6863d259891f06aecc5def1df2e18abd921e0a0aebc5d',
                       'B355041762402063C0', 12258, 'landsd/231645:0', 233626),
    'landsd/231645:0': ('cfe390f024ac815a8c8ae3f422724fd72e4cd5c164e7325f9404cd81fc1b46da',
                       'B355141753102063C0', 13725, 'landsd/233997:0', 231275),
}
EXACT_FIELDS = ['uid', 'sourceSHA256', 'sourceFormSHA256', 'worldTrianglesSHA256',
                'originalOwnership', 'exactRouteTileHashes', 'geographicCell',
                'exactWholeCellCoverage', 'completeRecordProjection',
                'exactCurrentComponentRoute', 'freshCurrentIdentity',
                'rawNativeIdentityReasons', 'reasons']


def reviewed_proof(current, decision):
    uid = current['uid']; sha, model, faces, other, provider_id = EXPECTED[uid]
    assert decision['uid'] == uid and decision['sourceSHA256'] == current['sourceSHA256'] == sha
    assert decision['modelId'] == model and decision['completeOriginalFaces'] == faces
    assert decision['foreignBoundaryUid'] == other and decision['identityOnlyApproved'] is True
    assert decision['sourceGeometryChanges'] == 0 and decision['aiGeometryModelling'] is False
    assert decision['providerObjectIdExact'] is False and decision['legacyObjectIdExactClaimed'] is False
    assert decision['currentProviderObjectId'] == provider_id
    assert all(decision[k] is False for k in ['physicalAccepted', 'placementApproved',
                                             'collisionExemption', 'installationApproved', 'publication'])
    assert current['passed'] is False and current['reasons'] == ALLOWED
    assert decision['rawIdentityReasonsRetained'] == ALLOWED
    previous = decision['rawIdentityVerbatim']
    for key in EXACT_FIELDS:
        assert current[key] == previous[key], 'Reviewed source identity changed: ' + key
    assert decision['worldTrianglesSHA256'] == current['worldTrianglesSHA256']
    ownership = current['originalOwnership']
    assert ownership['sourceGraphVerified'] and ownership['originalRootName'] == model
    assert current['exactWholeCellCoverage']['covered']
    ctx = current['freshCurrentIdentity']; target = ctx['target']
    assert ctx['exactObjectAndCSUID'] and target['uid'] == uid
    assert target['objectId'] == decision['cachedViewerObjectId']
    assert ctx['targetCoveredBySourceProjection'] >= .95 and ctx['sourceExcessMaximumDistanceFromTargetM'] <= 10
    assert {r['uid'] for r in ctx['intersectingForms'] if not r['sameParent']} == {other}
    revision = decision['providerRevisionContext']
    assert revision['uid'] == uid and revision['sourceSHA256'] == sha and revision['modelId'] == model
    assert revision['buildingCSUID'] == target['buildingCSUID']
    assert revision['cachedObjectId'] == target['objectId'] and revision['currentProviderObjectId'] == provider_id
    assert revision['objectIdExact'] is False
    assert all(revision[k] is True for k in ['buildingIdExact', 'modelGeoRefExact', 'baseAndTopHeightsExact'])
    proof = deepcopy(current)
    proof.update(policy='exact-reviewed-original-adjoining-podium-identity-v1',
                 underlyingIdentityPolicy=current['policy'], passed=True, reasons=[],
                 identityAccepted=True, rawCurrentIdentity=deepcopy(current),
                 reviewedIdentityOnlyReasonsReplaced=ALLOWED.copy(),
                 providerObjectIdExact=False, currentProviderObjectId=provider_id,
                 cachedViewerObjectId=target['objectId'],
                 proof=dict(exactObjectId=True, exactBuildingCSUID=True,
                            uniqueViewerMatch=True, identityAccepted=True),
                 physicalAccepted=False, placementApproved=False, collisionExemption=False,
                 installationApproved=False, publication=False, modelGeometryChanges=0,
                 qualification='Exact reviewed source association only. Cached viewer OBJECTID and current provider OBJECTID remain explicitly distinct. Every raw identity failure is retained. No terrain, support, collision, neighbour, runtime or publication approval transfers.')
    return proof


def complete_current_proof(row, expected_context):
    """Same complete-record algorithm as selected_original_identity_v3.py."""
    import numpy as np
    import shapely
    from run import ROOT, HERE, read, digest
    from primrose_compound_foundation_v2_20261015 import module
    from exact_packed_world_geometry_20261009 import decode_original_world_triangles
    from selected_original_identity_v3 import complete_identity
    from routed_original_cell_identity import verify as routed_verify
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    manifest_sha = digest(manifest.read_bytes())
    raw = (ROOT / row['candidate']['path']).read_bytes()
    assert digest(raw) == row['sourceSHA256']
    tri = decode_original_world_triangles(raw); assert len(tri) == row['triangles']
    final = module('reviewed_pair_complete_projection', HERE / 'xl-final-script-pass.py')
    final.projection = lambda faces: shapely.union_all(shapely.polygons(np.asarray(faces)[:, :, [0, 2]]))
    lo, hi = tri.min((0, 1)), tri.max((0, 1))
    forms = final.load_forms([lo[0]-2, lo[2]-2, hi[0]+2, hi[2]+2])
    hashes = {tile: digest((ROOT / '3d-viewer' / tile).read_bytes()) for _, _, tile in forms}
    context = dict(sourceSHA256=row['sourceSHA256'], identity=final.identity_context(row, tri, forms), neighbourTileHashes=hashes)
    assert context == expected_context, 'Full current record/foreign context changed'
    prefixes = {v[1][1:11] for v in EXPECTED.values()}; route_sources = []; route_hashes = {}
    for tile in read(manifest)['tiles']:
        path = ROOT / '3d-viewer' / tile['url']; tile_raw = path.read_bytes()
        matching = [b for b in read(path)['buildings'] if str(b.get('buildingCSUID') or '')[:10] in prefixes]
        if matching:
            sha = digest(tile_raw); route_hashes[tile['url']] = sha
            route_sources.extend(dict(building=b, tile=tile['url'], tileSHA256=sha) for b in matching)
    sources = [s for s in route_sources if str(s['building'].get('buildingCSUID') or '')[:10] == row['modelId'][1:11]]
    routed = routed_verify(raw, row, context, tri, current_identity=context['identity'], sources=sources)
    binding = dict(uid=row['uid'], sourceSHA256=row['sourceSHA256'], decodedWorldTrianglesSHA256=digest(tri.astype('<f8').tobytes()))
    proof = complete_identity(routed, tri, binding)
    proof.update(exactRouteManifestSHA256=manifest_sha, exactRouteTileHashes=route_hashes, completeRecordProjection=True)
    assert digest(manifest.read_bytes()) == manifest_sha
    for tile, sha in {**hashes, **route_hashes}.items():
        assert digest((ROOT / '3d-viewer' / tile).read_bytes()) == sha
    return proof


def verify_files(row, context, local):
    from run import ROOT, read, digest, connect, NATIVE_RUN
    from china_ferry_current_foundations_v1_20261020 import authenticate
    folder = ROOT / 'docs/astra-city/government-import' / REVIEW
    receipt, pins = authenticate(folder)
    path = folder / 'decisions.json'; pin = pins[str(path.relative_to(ROOT))]
    assert digest(path.read_bytes()) == pin
    decisions = read(path)['decisions']
    assert len(decisions) == 2 and {d['uid'] for d in decisions} == set(EXPECTED)
    decision = next(d for d in decisions if d['uid'] == row['uid'])
    sha, model, faces, _, _ = EXPECTED[row['uid']]
    assert row['sourceSHA256'] == sha and row['modelId'] == model and row['triangles'] == faces
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        assert db.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',
                          (NATIVE_RUN, row['native']['cacheKey'])).fetchone() == (row['native']['resultSha'],)
    current = complete_current_proof(row, context)
    proof = reviewed_proof(current, decision)
    proof['boundedIdentityReview'] = dict(jobId=receipt['jobId'], path=str(path.relative_to(ROOT)), sha256=pin)
    assert digest(path.read_bytes()) == pin
    assert digest((ROOT / '3d-viewer/city/data/manifest.json').read_bytes()) == current['exactRouteManifestSHA256']
    for tile, sha in current['exactRouteTileHashes'].items():
        assert digest((ROOT / '3d-viewer' / tile).read_bytes()) == sha
    return proof
