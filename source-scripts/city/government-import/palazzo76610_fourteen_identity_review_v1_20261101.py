"""Bounded identity review of fourteen exact original provider units, never placement."""
import argparse
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations, connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

P = 'government-xl-palazzo76610-after-prosperous-'
BATCH = P + 'fourteen-identity-review-v1-20261101'
EXPECTED = {76610,252774,71042,71045,71688,71703,71709,71886,72626,88303,88899,89150,304541,340334}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--owned', action='store_true')
    a = ap.parse_args()
    base = ROOT / 'docs/astra-city/government-import'
    out = base / BATCH
    assert not out.exists()
    refs, pins = [Path(__file__)], {}

    def take(batch, filename):
        if batch not in pins:
            pins[batch] = authenticate(base / batch)[1]
            refs.append(base / batch / 'result.json')
        path = base / batch / filename
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selected = take(P+'fourteen-authentic-tin-runtime-v1-20261101', 'selection.json.gz')
    rows = selected['rows']
    assert {r['source']['building']['objectId'] for r in rows} == EXPECTED and len(rows) == 14
    resources = sorted('building:'+r['uid'] for r in rows)
    lp = HERE / 'local' / BATCH / 'reservation.json'
    if not a.owned:
        assert not lp.parent.exists()
        claim = reservations.claim('palazzo-identity-'+str(uuid.uuid4()), resources, batch=BATCH, ttl=3600)
        assert claim['ok'], claim
        return execute_reserved(claim['reservation'], lp, [sys.executable, __file__, '--owned'])
    lease = read(lp)
    assert reservations.owns(lease) and sorted(lease['resources']) == resources
    primary = take(P+'fourteen-primary-records-v1-20261101', 'footprints.json')['features']
    assert len(primary) == 14
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selected['manifestSHA256']
    refs.append(manifest)
    views = {}
    for name in ['twelve-source-views-v1-20261031','two-boundary-source-views-v1-20261031']:
        batch = P+name
        take(batch, 'summary.json')
        for path in sorted((base/batch).glob('*-plan.png')):
            uid = 'landsd/'+path.name.split('-')[0]+':0'
            images = []
            for suffix in ['plan','oblique-35','oblique-215']:
                image = path.with_name(path.name.split('-')[0]+'-0-'+suffix+'.png')
                sha = digest(image.read_bytes())
                assert sha == pins[batch][str(image.relative_to(ROOT))]
                refs.append(image)
                images.append(dict(path=str(image.relative_to(ROOT)), sha256=sha))
            views[uid] = images
    assert set(views) == {r['uid'] for r in rows}
    reviewed = []
    for row in rows:
        uid, form = row['uid'], row['source']['building']
        proof = take(P+'fourteen-identity-v1-20261031', uid.split('/')[1]+'/identity.json')
        matches = [f['attributes'] for f in primary if f['attributes']['BuildingCSUID'] == form['buildingCSUID']]
        assert len(matches) == 1
        record = matches[0]
        assert record['Status'] == 'Active'
        assert record['BuildingID'] == form['buildingId']
        assert record['BuildingBlockType'] == form['structureType']
        assert record['BaseHeight'] == form['baseHeightHKPD'] and record['TopHeight'] == form['topHeightHKPD']
        assert record['GeoRefNo'] == form['buildingCSUID'][:10] == row['modelId'][1:11]
        assert proof['originalOwnership']['sourceGraphVerified']
        assert proof['originalOwnership']['originalRootName'] == row['modelId']
        assert proof['exactCurrentComponentRoute']['qualified'] and proof['freshCurrentIdentity']['exactObjectAndCSUID']
        tile = ROOT/'3d-viewer'/row['source']['tile']
        assert digest(tile.read_bytes()) == row['source']['tileSHA256']
        assert next(f for f in read(tile)['buildings'] if f['uid'] == uid) == form
        refs.append(tile)
        asset = ROOT/row['candidate']['path']
        assert digest(asset.read_bytes()) == row['sourceSHA256'] == proof['sourceSHA256']
        refs.append(asset)
        triangles = decode_original_world_triangles(asset.read_bytes())
        assert len(triangles) == row['triangles']
        assert digest(triangles.astype('<f8').tobytes()) == proof['worldTrianglesSHA256']
        native = row['native']
        with connect() as db:
            db.execute('SET TRANSACTION READ ONLY')
            sha, data = db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s', (native['cacheKey'],)).fetchone()
            assert sha == native['resultSha']
            assert next(m for m in data['models'] if m['modelId'] == row['modelId']) == native['model']
        matches = [c for c in native['model']['matching']['officialCandidates'] if c['buildingCSUID'] == form['buildingCSUID'] and c['objectId'] == form['objectId']]
        assert len(matches) == 1
        observation = ('Stepped high-rise source shell, inset upper roof structures and open upper strips align with its own outline and orientation; no adjacent tower substituted.')
        if form['objectId'] == 72626:
            observation = ('Individually inspected all three full-size source views. The upright stepped shell aligns with the surveyed outline; upper horizontal surfaces leave repeated open strips. Raw76.4328% projected target coverage remains. This identifies the exact supplied unit, not a complete closed building or a claim that every footprint point has a roof.')
        elif form['objectId'] == 76610:
            observation = ('Long low strip with broad stepped central podium and source-authored projection voids follows the surveyed form. Raw88.5927% coverage and11.567881m2 unrelated projected excess onto304541/340334 remain. Both boundary originals are separately identified; their junction/physical acceptance remains unresolved.')
        elif form['objectId'] == 252774:
            observation = 'Low curved unit follows its own curved outline; the complete original unit is not relabelled as a residential tower.'
        elif form['objectId'] == 304541:
            observation = 'Stepped rectangular source with repeated facade/roof changes follows its own outline. Its installed304700 neighbour has a separate CSUID/source and is not substituted or merged; actual crossing review remains pending.'
        elif form['objectId'] == 340334:
            observation = 'Low L-shaped original roof/wall unit follows its own outline. No invented landmark name, source cap or geometry completion.'
        reviewed.append(dict(uid=uid, sourceSHA256=row['sourceSHA256'], modelId=row['modelId'], buildingCSUID=form['buildingCSUID'], stableBuildingID=form['buildingId'], freshPrimaryRecord=record, sourceWorldSHA256=proof['worldTrianglesSHA256'], rawIdentityVerbatim=proof, identityAccepted=True, identityOnlyApproved=True, identityReviewApproved=True, observation=observation, sourceImagesActuallyInspected=views[uid], physicalAcceptance=False, installationApproved=False, publication=False))
    assert reservations.owns(lease) and digest(manifest.read_bytes()) == selected['manifestSHA256']
    result = dict(uids=sorted(r['uid'] for r in rows), sourceSHA256ByUid={r['uid']:r['sourceSHA256'] for r in rows}, rows=reviewed, identityAccepted=True, identityOnlyApproved=True, rawIdentityWarningsPreserved=True, sourceGeometryChanges=0, sourcePoseChanges=0, aiGeometryModelling=False, sourceEvidenceInterpretationUsedAI=True, modelAndEffort='Unknown from tool-visible metadata; not inferred', physicalAcceptance=False, installationApproved=False, publication=False, qualification='Bounded identity interpretation of exactly fourteen complete provider-owned units at unchanged source pose. Fresh unique Active BuildingID/CSUID/GeoRef/type/heights, current exact forms, original source graphs, full source bytes and42source views are bound. Views were inspected in four contact sheets, with Tower7 all three images individually inspected. Roof-projection coverage is not architectural completeness; all raw coverage/extent/foreign overlap warnings remain verbatim. No global acceptance rule changes and no identity approval for any other revision, physical/placement/support/collision/runtime/browser/publication or optimisation approval.')
    for row in reviewed:
        save(out/row['uid'].split('/')[1]/'ROOT-IDENTITY-REVIEW.json', row)
    save(out/'summary.json', result)
    refs.append(HERE/'exact_packed_world_geometry_20261009.py')
    module('palazzo14_identity_review_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'bounded-fourteen-original-provider-unit-identity-review-only', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
