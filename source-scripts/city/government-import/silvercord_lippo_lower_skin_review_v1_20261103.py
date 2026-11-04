"""Bounded original lower-skin interpretation, without whole physical approval.

Keep the failed Silvercord foundation policy and every raw warning unchanged.
"""
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-silvercord-lippo-lower-skin-role-review-v1-20261103'
LOCAL = HERE / 'local' / BATCH
UIDS = ['landsd/233997:0', 'landsd/231645:0']
PACKETS = {'landsd/233997:0': [([1347, 1348, 1349], None), ([6240, 6241, 6242], 11663)],
           'landsd/231645:0': [([8231, 8232, 8233], 11518)]}


def owned():
    lease = read(LOCAL / 'reservation.json')
    assert reservations.owns(lease) and not (BASE / BATCH).exists()
    refs, pins = [Path(__file__)], {}

    def take(batch, name):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]
            refs.append(BASE / batch / 'result.json')
        path = BASE / batch / name
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    inspection = take('government-xl-silvercord-lippo-complete-lower-root-inspection-v1-20261103', 'ROOT-EXPORT-INSPECTION.json')
    assert inspection['allListedExportsActuallyInspected'] and inspection['imageCount'] == 4
    local_views = BASE / 'government-xl-silvercord-lippo-lower-patch-root-inspection-v1-20261103/ROOT-PLOT-INSPECTION.json'
    previous = read(local_views)
    assert previous['allListedExportsActuallyInspected'] and len(previous['images']) == 3
    refs.append(local_views)
    images = inspection['imagesActuallyInspected'] + previous['images']
    for row in images:
        path = ROOT / row['path']
        assert digest(path.read_bytes()) == row['sha256']
        refs.append(path)
    selection = take('government-xl-silvercord-lippo-complete-floor-runtime-v2-20261103', 'selection.json.gz')
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256']
    refs.append(manifest)
    contacts_batch = 'government-xl-silvercord-lippo-lower-patch-source-contacts-v1-20261103'
    results, sources, policies = [], {}, {}
    for uid in UIDS:
        key = uid.split('/')[1].replace(':', '-')
        source = next(r for r in selection['rows'] if r['uid'] == uid)
        asset = ROOT / source['candidate']['path']
        assert digest(asset.read_bytes()) == source['sourceSHA256']
        refs.append(asset)
        sources[uid] = source['sourceSHA256']
        components = take('government-xl-silvercord-lippo-lower-component-context-v1-20261103-' + key, 'summary.json')
        foundation = take('government-xl-silvercord-lippo-complete-floor-foundations-v1-20261103-' + key, 'summary.json')
        policies[uid] = foundation
        assert components['sourceSHA256'] == sources[uid] and len(foundation['rows']) == 4
        assert all(r['fullyBuriedUpwardTriangles'] == 0 for r in foundation['rows'])
        assert foundation['establishedFoundationPolicyPassed'] is (uid == 'landsd/231645:0')
        for mode in ['original', 'literal', 'leftF32', 'balancedF32']:
            assert reservations.owns(lease)
            low = take('government-xl-silvercord-lippo-complete-floor-roles-v1-20261103-below-' + key, mode + '.json.gz')
            component_mode = {'leftF32': 'left', 'balancedF32': 'balanced'}.get(mode, mode)
            context = next(r for r in components['rows'] if r['mode'] == component_mode)
            contacts = take(contacts_batch, key + '-' + mode + '.json.gz')
            assert context['sourceWorldSHA256'] == contacts['sourceWorldSHA256'] == low['sourceWorldSHA256']
            assert contacts['completeFiniteProof']['allPairsExamined'] and contacts['completeFiniteProof']['sourceFacesOmitted'] == 0
            walls, lower = set(low['negativeWallFaces']), set(low['negativeNonWallFaces'])
            expected = {f for packet, _ in PACKETS[uid] for f in packet}
            assert lower == expected and set(low['completeNegativeFaces']) == walls | lower
            assert len(walls) == (410 if uid == UIDS[0] else 234)
            paths = {r['sourceFace']: r for r in low['allWallCapPaths']}
            assert set(paths) == walls and all(r['hasExactSharedEdgeClearCapPath'] for r in paths.values())
            faces = {r['sourceFace']: r for r in context['faces']}
            assert set(faces) == lower and all(r['downward'] and not r['exactlyHorizontal'] for r in faces.values())
            packets = []
            for packet, wall in PACKETS[uid]:
                group = set(packet)
                assert all(group - {f} <= {q['sourceFace'] for q in faces[f]['adjacentFaces']} for f in packet)
                details = [faces[f] for f in packet]
                if wall is None:
                    assert all(r['wholeSharedEdgeComponentFaces'] == 3 for r in details)
                    assert not [r for r in contacts['positiveExternalSourceContacts'] if r['sourceFaceA'] in group]
                    area = sum(r['areaM2'] for r in details)
                    assert 0 < area < .06
                else:
                    assert wall in paths
                    assert any(c['sourceFaceA'] in group and c['sourceFaceB'] == wall and c['dimension'] > 0
                               for c in contacts['positiveExternalSourceContacts'])
                    assert any(c['sourceFaceA'] == wall and c['dimension'] > 0
                               and c['sourcePrimitiveDimensionA'] == c['sourcePrimitiveDimensionB'] == 2
                               for c in low['completePositiveGradeContacts'])
                packets.append(dict(sourceFaceIds=packet, exactOriginalFacetDetails=details,
                                    originalGradeContactingWall=wall, groundRootCredit=False, bridgeCredit=False))
            results.append(dict(uid=uid, mode=mode, sourceWorldSHA256=low['sourceWorldSHA256'],
                completeGroundSHA256=low['completeGroundSHA256'], qualifiedNegativeSourceFaceIds=sorted(walls | lower),
                originalWallCapPaths=list(paths.values()), originalLowerPackets=packets))
    review = dict(uids=UIDS, reviewer='Codex ROOT', sourceSHA256ByUid=sources, rows=results,
        imagesActuallyInspected=images, sourceRoleAccepted=True,
        qualifiedRole='exact-unchanged-original-lower-wall-and-downward-skins',
        basis=[
            'All 644 affected wall facets are original source skins with exact shared-edge routes to clear upper source faces in each of the four bound coordinate streams. The actual source/ground plots show grade crossing the lower wall context; entire partially negative triangles are preserved.',
            'Silvercord6240/6241/6242 and Lippo8231/8232/8233 are original tilted three-facet lower skins, each connected by an original finite edge to a wall with actual positive finite grade contact and its own clear-cap path. Their exact slopes and every contact are retained; they are not rounded into a horizontal floor or assigned a structural purpose.',
            'Silvercord1347/1348/1349 remain the exact isolated downward three-facet skin, total original area below0.06m2, with the saved point contacts and no positive external source contact. It receives no structural attachment, ground root, bridge, floor or walking-route credit. Its unchanged presence is recorded as source detail; disconnectedness does not create a new per-component engineering admission requirement.',
            'This accepts the represented lower-skin role only. Silvercord still FAILS the unchanged0.001 buried-area policy in all four streams, all18 disconnected rim warnings remain raw, and no whole-source foundation, collision, placement, neighbour, native-owner migration, stage, browser or publication approval is granted. A separate complete physical interpretation is mandatory.'
        ], rawFoundationEvidenceByUid=policies, rawFoundationFlagsRewritten=False,
        groundRootCredit=False, interComponentBridgeCredit=False, sourceGeometryChanges=0,
        sourcePoseChanges=0, physicalAcceptance=False, placementReviewed=False,
        publicationApproved=False, installationApproved=False, publication=False,
        sourceEvidenceInterpretationUsedAI=True, aiGeometryModelling=False,
        modelAndEffort='Not verified from available runtime metadata')
    assert reservations.owns(lease) and digest(manifest.read_bytes()) == selection['manifestSHA256']
    save(BASE / BATCH / 'ROOT-LOWER-SOURCE-REVIEW.json', review)
    module('silvercord_lippo_lower_skin_review', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'bounded-exact-original-lower-skin-source-role-review', list(dict.fromkeys(refs)), review)


if __name__ == '__main__':
    if '--owned' in sys.argv:
        owned()
    else:
        assert not LOCAL.exists() and not (BASE / BATCH).exists()
        claim = reservations.claim('silvercord-lippo-lower-skin-review-' + str(uuid.uuid4()),
            ['building:' + uid for uid in UIDS] + ['immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
        assert claim['ok'], claim
        execute_reserved(claim['reservation'], LOCAL / 'reservation.json', [sys.executable, __file__, '--owned'])
