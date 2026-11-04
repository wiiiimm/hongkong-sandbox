"""Bounded review of the unchanged Prosperous Garden podium source identity only."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
PREFIX = 'government-xl-prosperous235568'
BATCH = PREFIX + '-podium-identity-review-v1-20261031'
UID = 'landsd/235568:0'
SHA = 'ef354fbb79cbbf576a0e146cf019f2a1ae73c75b031dde2ece59dcdee8f78ac2'


def main():
    out = BASE / BATCH
    assert not out.exists()
    refs, pins = [Path(__file__)], {}

    def take(batch, filename):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]
            refs.append(BASE / batch / 'result.json')
        path = BASE / batch / filename
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    identity = PREFIX + '-six-original-identity-v1-20261031'
    raw = take(identity, '235568:0/identity.json')
    assert raw['uid'] == UID and raw['sourceSHA256'] == SHA
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == raw['exactRouteManifestSHA256']
    refs.append(manifest)
    for tile, sha in raw['exactRouteTileHashes'].items():
        path = ROOT / '3d-viewer' / tile
        assert digest(path.read_bytes()) == sha
        refs.append(path)
    route = raw['exactCurrentComponentRoute']
    assert route['qualified'] and route['official']['objectId'] == 235568
    assert route['official']['buildingCSUID'] == '3538119026P20060311'
    assert raw['originalOwnership']['sourceGraphVerified']
    assert raw['originalOwnership']['originalRootName'] == 'B353811902602063C0'
    assert raw['exactWholeCellCoverage']['covered'] and raw['geographicCell']['targetCoversWholeCell']
    assert set(raw['reasons']) == {'fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM', 'full-source-maximum-extent'}
    spatial = raw['freshCurrentIdentity']
    assert spatial['exactObjectAndCSUID'] and spatial['targetCoveredBySourceProjection'] == 0.9827812419747688
    assert spatial['sourceExcessMaximumDistanceFromTargetM'] == 13.725349893984609
    assert spatial['sourceExcessCoveredByUnrelatedFormsM2'] == 0.0
    towers = {'landsd/' + u + ':0' for u in ['234691', '235119', '235888', '236076', '237129']}
    for uid in towers:
        p = take(identity, uid.split('/')[1] + '/identity.json')
        assert p['passed'] and not p['reasons']
    pairs = take(PREFIX + '-six-original-all-pairs-v1-20261031', 'summary.json')
    assert pairs['sourceSHA256ByUid'][UID] == SHA and pairs['completeUnorderedPairs'] == 15
    links = [r for r in pairs['rows'] if UID in {r['uid'], r['peerUid']}]
    assert len(links) == 20
    for uid in towers:
        assert {r['mode'] for r in links if uid in {r['uid'], r['peerUid']}} == {'original', 'literal', 'leftF32', 'balancedF32'}
    assert all(not r['strictBoundsSeparated'] and r['positiveSurfaceContacts'] > 0 for r in links)
    views = PREFIX + '-podium-source-views-v1-20261031'
    images = take(views, 'summary.json')['rows']
    assert len(images) == 1 and images[0]['uid'] == UID and images[0]['sourceSHA256'] == SHA
    assert images[0]['completeOriginalFaces'] == 17333
    exports = images[0]['images']
    assert {Path(r['path']).name for r in exports} == {'235568-0-plan.png', '235568-0-oblique-35.png', '235568-0-oblique-215.png'}
    for r in exports:
        path = ROOT / r['path']
        assert digest(path.read_bytes()) == r['sha256'] == pins[views][r['path']]
        refs.append(path)
    review = dict(uid=UID, reviewer='Codex ROOT', sourceSHA256=SHA,
                  sourceFormSHA256=raw['sourceFormSHA256'], worldTrianglesSHA256=raw['worldTrianglesSHA256'],
                  identityOnlyApproved=True, sourceIdentityReviewed=True, identityReviewApproved=True,
                  identityProof={k: True for k in ['exactObjectId', 'exactBuildingCSUID', 'uniqueViewerMatch', 'identityAccepted']},
                  rawProof=raw, rawReasonsRetained=raw['reasons'], imagesActuallyInspected=exports,
                  reviewBasis=[
                      'Unique exact government OBJECTID/Podium CSUID, original root graph and full one-metre geographic cell bind this unchanged source. No target, coordinates or source facets changed.',
                      'ROOT inspected the complete 17333-face plan and both oblique exports. The low podium follows the recorded common podium outline and all five separately identified residential tower locations. The courtyard contains an angular low source projection outside the BASIC footprint; this is part of the exact original podium record, not a replacement tower or an unrelated building.',
                      'The source covers 98.27812419747688 percent of the recorded podium footprint. Maximum individual-footprint excess remains 13.725349893984609m; zero excess overlaps unrelated recorded building forms. This exact-source identity review qualifies that preserved extent warning only, with no global limit change or geometry trimming.',
                      'All five exact tower identity checks pass, and all five have finite positive surface contacts with this original podium in all four coordinate representations. These contacts support assembly correspondence only; they do not approve physical attachment or source intersections.',
                      'Keep all five separately identified tower records. No legal ownership, architectural function of the courtyard projection, engineering support, clearance, collision, ground, browser or publication acceptance is inferred.'
                  ], sourceIdentityReviewUsedAI=True, aiGeometryModelling=False,
                  geometryMethod='scripted-original-government-port',
                  placementReviewed=False, physicalAcceptance=False, publicationApproved=False, installationApproved=False)
    save(out / '235568:0-review.json', review)
    for batch, bound in pins.items():
        for path in [r for r in refs if str(r.relative_to(ROOT)) in bound]:
            assert digest(path.read_bytes()) == bound[str(path.relative_to(ROOT))]
    module('prosperous_podium_identity_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'exact-original-podium-identity-review', list(dict.fromkeys(refs)),
        dict(uids=[UID], identityAccepted=True, installationApproved=False,
             sourceGeometryChanges=0, sourceIdentityReviewUsedAI=True, aiGeometryModelling=False))


if __name__ == '__main__':
    main()
