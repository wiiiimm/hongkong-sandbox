"""Named unchanged government components; retain the tower's raw outline failure.

Identity interpretation only, without physical or publication approval.
"""
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-shangrila-exact-component-identity-review-v1-20261101'
CAPTURE = 'government-xl-shangrila-original-pair-after-harbour-one-current-v1-20261101-runtime'
IDENTITY = 'government-xl-shangrila-original-pair-after-harbour-one-current-v1-20261101-identity'
EXACT = {
    'landsd/240962:0': ('2b2c545fe714424d9b0af9af5acd62256f64a011a1d0c5e455ccc2e04644a6a4', '3628517563T20050430', 'B362851756301063C0'),
    'landsd/233824:0': ('e7406277e84cd879c2e4ffcd9e5e19b25b52ffc740072e429ca32a0ebd79d613', '3628017573P20060311', 'B362801757302063C0'),
}

def main():
    out = BASE / BATCH
    lp = HERE / 'local' / BATCH / 'reservation.json'
    if '--owned' not in sys.argv:
        assert not out.exists() and not lp.parent.exists()
        c = reservations.claim('shangrila-component-identity-' + str(uuid.uuid4()),
            ['building:' + u for u in EXACT], batch=BATCH, ttl=3600)
        assert c['ok'], c
        return execute_reserved(c['reservation'], lp, [sys.executable, __file__, '--owned'])
    lease = read(lp)
    assert reservations.owns(lease)
    refs, pins = [Path(__file__)], {}
    def take(batch, name):
        if batch not in pins:
            _, pins[batch] = authenticate(BASE / batch)
            refs.append(BASE / batch / 'result.json')
        p = BASE / batch / name
        assert digest(p.read_bytes()) == pins[batch][str(p.relative_to(ROOT))]
        refs.append(p)
        return read(p)
    selected = {r['uid']: r for r in take(CAPTURE, 'selection.json.gz')['rows']}
    assert set(selected) == set(EXACT)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    sha = digest(manifest.read_bytes())
    refs.append(manifest)
    observation = BASE / 'government-xl-shangrila-identity-observation-v1-20261101.json'
    seen = read(observation)
    assert seen['reviewer'] == 'Codex ROOT' and seen['diagramActuallyViewed']
    refs.append(observation)
    rows = []
    for uid, (source_sha, csuid, model_id) in EXACT.items():
        row = selected[uid]
        raw = take(IDENTITY, uid.split('/')[1] + '/identity.json')
        context = take(IDENTITY, uid.split('/')[1] + '/context.json')['identity']
        asset = ROOT / row['candidate']['path']
        assert digest(asset.read_bytes()) == raw['sourceSHA256'] == row['sourceSHA256'] == source_sha
        assert row['modelId'] == model_id and row['source']['building']['buildingCSUID'] == csuid
        assert raw['exactRouteManifestSHA256'] == sha
        assert raw['originalOwnership']['sourceGraphVerified'] and raw['originalOwnership']['originalRootName'] == model_id
        route = raw['exactCurrentComponentRoute']
        assert route['qualified'] and route['official']['objectId'] == int(uid.split('/')[1].split(':')[0])
        assert route['official']['buildingCSUID'] == csuid and context['exactObjectAndCSUID']
        assert raw['exactWholeCellCoverage']['covered'] and raw['geographicCell']['targetCoversWholeCell']
        assert raw['exactWholeCellCoverage']['wholeOriginalFacesAccounted'] == row['triangles']
        refs.append(asset)
        for tile, expected in raw['exactRouteTileHashes'].items():
            path = ROOT / '3d-viewer' / tile
            assert digest(path.read_bytes()) == expected
            refs.append(path)
        images = []
        if uid == 'landsd/240962:0':
            assert not raw['passed'] and raw['reasons'] == ['fresh-current-spatial-bound:targetCoveredBySourceProjection', 'full-source-target-coverage']
            assert context['targetCoveredBySourceProjection'] == 0.9499798430122594
            assert context['sourceProjectionInsideTarget'] == 0.9423051631115877
            assert context['sourceExcessMaximumDistanceFromTargetM'] == 2.6456779690687706
            assert context['unrelatedIntersectingForms'] == 0 and context['sourceExcessCoveredByUnrelatedFormsM2'] == 0
            plot = take('government-xl-shangrila240962-current-projection-v1-20261101', 'summary.json')
            image = plot['image']
            assert image == seen['image'] and image['sha256'] == digest((ROOT / image['path']).read_bytes())
            assert plot['sourceSHA256'] == source_sha and plot['originalWorldSHA256'] == raw['worldTrianglesSHA256']
            assert plot['completeSourceFaces'] == row['triangles']
            refs.append(ROOT / image['path'])
            images = [image]
        else:
            assert raw['passed'] and not raw['reasons']
        proof = {k: True for k in ['exactObjectId', 'exactBuildingCSUID', 'uniqueViewerMatch', 'identityAccepted']}
        review = dict(uid=uid, sourceSHA256=source_sha, sourceFormSHA256=raw['sourceFormSHA256'],
            worldTrianglesSHA256=raw['worldTrianglesSHA256'], identityAccepted=True, identityProof=proof,
            rawProof=raw, rawReasonsPreserved=raw['reasons'], componentIdentityOnly=True,
            wholeLandmarkCompletenessClaimed=False, imagesActuallyViewed=images,
            sourceGeometryChanges=0, sourcePoseChanges=0, genericThresholdChanges=0,
            physicalAcceptance=False, collisionApproved=False, installationApproved=False, publication=False,
            sourceIdentityReviewUsedAI=bool(images), aiGeometryModelling=False, basis=seen['basis'])
        save(out / (uid.split('/')[1] + '-identity-review.json'), review)
        rows.append(dict(uid=uid, sourceSHA256=source_sha, identityAccepted=True, identityProof=proof,
                         rawReasonsPreserved=raw['reasons'], review=review))
    assert reservations.owns(lease) and digest(manifest.read_bytes()) == sha
    result = dict(uids=list(EXACT), rows=rows, identityAccepted=True, currentManifestSHA256=sha,
        sourceSHA256ByUid={u: v[0] for u, v in EXACT.items()}, physicalAcceptance=False,
        installationApproved=False, publication=False, sourceGeometryChanges=0, sourcePoseChanges=0,
        sourceIdentityReviewUsedAI=True, aiGeometryModelling=False)
    save(out / 'summary.json', result)
    module('shangrila_bounded_identity_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'named-exact-shangrila-component-identity-raw-outline-failure-preserved', list(dict.fromkeys(refs)), result)

if __name__ == '__main__':
    main()
