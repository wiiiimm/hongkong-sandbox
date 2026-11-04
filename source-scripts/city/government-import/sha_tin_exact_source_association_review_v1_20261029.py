"""Review four exact original source associations; retain every placement hold.

This identifies native provider units, not ownership of their projections or
permission to install, suppress another actor, or certify as-built dimensions.
"""
import argparse
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from original_source_assembly_diagnostic import COVERAGE_REASONS

BASE = ROOT / 'docs/astra-city/government-import'
CASES = {
    'landsd/231013:0': 'government-xl-civic-seven-identity-v1-20261029',
    'landsd/271344:0': 'government-xl-civic-two-neighbours-identity-v1-20261029',
    'landsd/92881:0': 'government-xl-sha-tin-citylink-movie-identity-v1-20261029',
    'landsd/238142:0': 'government-xl-sha-tin-citylink-movie-identity-v1-20261029',
}
CAPTURE = 'government-xl-sha-tin-civic-seven-complete-runtime-v1-20261029'
PRIMARY = 'government-xl-sha-tin-civic-seven-official-records-v1-20261029'
PERMITS = 'government-xl-sha-tin-civic-seven-complete-permit-families-v1-20261029'
CONTACTS = 'government-xl-sha-tin-civic-seven-foreign-contacts-v1-20261029'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch', required=True)
    p.add_argument('--owned', action='store_true')
    a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    out, local = BASE / a.batch, HERE / 'local' / a.batch
    assert not out.exists()
    leasepath = local / 'reservation.json'
    if not a.owned:
        assert not local.exists()
        claim = reservations.claim('sha-tin-source-association-' + str(uuid.uuid4()),
            ['building:' + uid for uid in sorted(CASES)], batch=a.batch, ttl=1800)
        assert claim['ok']
        return execute_reserved(claim['reservation'], leasepath,
            [sys.executable, __file__, '--batch', a.batch, '--owned'])
    lease = read(leasepath)
    assert reservations.owns(lease)
    refs, pins = [Path(__file__), HERE / 'original_source_assembly_diagnostic.py'], {}

    def take(batch, filename):
        if batch not in pins:
            _, pins[batch] = authenticate(BASE / batch)
            refs.append(BASE / batch / 'result.json')
        path = BASE / batch / filename
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selection = take(CAPTURE, 'selection.json.gz')
    selected = {r['uid']: r for r in selection['rows']}
    primary = take(PRIMARY, 'summary.json')
    assert not primary['missingRequestedCSUIDs'] and primary['footprints'] == len(selected) == 7
    official = take(PRIMARY, 'footprints.json')['features']
    permits = take(PERMITS, 'summary.json')
    assert permits['allRequestedPermitRecordsReturned']
    assert set(permits['completePermitCSUIDs']) == {'3744326967T20050430', '3743126836T20180612'}
    assert set(permits['permits']) == {'NT134/84', 'NT33/2018(OP)'}
    contacts = take(CONTACTS, 'summary.json')
    assert set(contacts['uids']) == set(selected)
    manifestpath = ROOT / '3d-viewer/city/data/manifest.json'
    manifestsha = digest(manifestpath.read_bytes())
    assert manifestsha == selection['manifestSHA256'] == primary['currentManifestSHA256'] == permits['currentManifestSHA256']
    refs.append(manifestpath)
    reviews = []
    for uid, batch in CASES.items():
        row = selected[uid]
        b = row['source']['building']
        raw = take(batch, uid.split('/')[1] + '/identity.json')
        assert raw['reasons'] and not set(raw['reasons']) - COVERAGE_REASONS
        assert raw['originalOwnership']['sourceGraphVerified']
        assert raw['originalOwnership']['originalRootName'] == row['modelId']
        assert raw['exactCurrentComponentRoute']['qualified']
        assert raw['exactWholeCellCoverage']['covered'] and raw['geographicCell']['targetCoversWholeCell']
        assert raw['freshCurrentIdentity']['exactObjectAndCSUID']
        assert raw['freshCurrentIdentity']['targetCoveredBySourceProjection'] >= .95
        assert raw['exactCurrentComponentRoute']['source']['building'] == b
        tile = ROOT / '3d-viewer' / row['source']['tile']
        assert digest(tile.read_bytes()) == row['source']['tileSHA256'] == raw['exactCurrentComponentRoute']['source']['tileSHA256']
        assert [v for v in read(tile)['buildings'] if v['uid'] == uid] == [b]
        asset = ROOT / row['candidate']['path']
        assert digest(asset.read_bytes()) == row['sourceSHA256'] == raw['sourceSHA256']
        refs.extend([tile, asset])
        matches = [f['attributes'] for f in official if f['attributes']['BuildingCSUID'] == b['buildingCSUID']]
        assert len(matches) == 1
        record = matches[0]
        assert record['Status'] == 'Active' and record['BuildingBlockType'] == b['structureType']
        assert record['BaseHeight'] == b['baseHeightHKPD'] and record['TopHeight'] == b['topHeightHKPD']
        boundaries = [r for r in contacts['rows'] if r.get('uid', r.get('sourceUid')) == uid]
        review = dict(uid=uid, modelId=row['modelId'], sourceSHA256=row['sourceSHA256'],
            sourceFormSHA256=raw['sourceFormSHA256'], worldTrianglesSHA256=raw['worldTrianglesSHA256'],
            reviewType='exact-current-native-root-and-CSUID-source-association-only', reviewer='Codex ROOT',
            identityOnlyApproved=True, identityReviewApproved=True, sourceIdentityReviewed=True,
            identityProof=dict(exactObjectId=True, exactBuildingCSUID=True, uniqueViewerMatch=True, identityAccepted=True),
            rawIdentityVerbatim=raw, rawReasonsRetained=raw['reasons'],
            sourceOfficialRecord=record, completePermitPacket=PERMITS,
            permitMembershipUnavailableForThisCSUID=b['buildingCSUID'] not in permits['completePermitCSUIDs'],
            independentPhysicalBoundaryObligations=boundaries,
            requiresIndependentBoundaryPlacementReview=True, boundaryOwnershipApproved=False,
            outsideAssemblySuppressionApproved=False, requiresNativeHeightApplicabilityReview=True,
            nativeRecordedBounds=row['native']['model']['worldBounds'],
            recordedBaseHeight=b['base'], recordedTopHeight=b['base'] + b['height'],
            placementReviewed=False, physicalAccepted=False, publicationApproved=False, installationApproved=False,
            sourceIdentityReviewUsedAI=True, aiGeometryModelling=False, sourceGeometryChanges=0, sourcePoseChanges=0,
            basis=[
                'The complete provider graph, exact typed current component route, current object/CSUID, and exact full encoded metre-cell coverage agree for these immutable bytes. Fresh official active CSUID/type/base/top records agree with the unchanged map form. No name/proximity substitution or coordinate edit is used.',
                'This accepts only association of the exact provider unit to this map actor. Town-hall public-campus and Citylink records have no linked permit in this packet; no permit or legal ownership is invented. The bus and cinema have separately enumerated complete permit families, which remain distinct.',
                'All raw extent/unrelated-overlap failures and every complete measured original/BASIC interface remain mandatory placement obligations. This review grants no roof suppression, interpenetration, support, collision, source-height/as-built applicability, visual or publication approval.',
                'The original native vertical ranges differ from the footprint height fields. They are retained explicitly for separate functional/source applicability review, never scaled, rebased, hidden or treated as corrected measurements.'
            ])
        save(out / (uid.split('/')[1] + '-review.json'), review)
        reviews.append(dict(uid=uid, sourceSHA256=row['sourceSHA256'], identityOnlyApproved=True,
                            requiresIndependentBoundaryPlacementReview=True, requiresNativeHeightApplicabilityReview=True))
    result = dict(uids=sorted(CASES), rows=reviews, identityOnlyApproved=True,
        sourceGeometryChanges=0, sourcePoseChanges=0, aiGeometryModelling=False,
        placementReviewed=False, physicalAccepted=False, publicationApproved=False, installationApproved=False,
        qualification='Bounded exact original source association only. All failed spatial proxies, boundary roles, current source-height applicability, support, collision, browser and publication gates remain unapproved.')
    save(out / 'summary.json', result)
    assert reservations.owns(lease)
    module('sha_tin_exact_association_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        a.batch, 'exact-four-original-source-association-only-review', list(dict.fromkeys(refs)), result)
    print(dict(sourceAssociationsReviewed=len(reviews), placementApproved=False, newlyInstalled=0), flush=True)


if __name__ == '__main__':
    main()
