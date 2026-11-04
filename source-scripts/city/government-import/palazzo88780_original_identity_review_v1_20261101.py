"""Bounded identity review of exact original88780, never placement."""
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
BATCH = P + '88780-original-identity-review-v1-20261101'
EXPECTED = {88780}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--owned', action='store_true')
    ap.add_argument('--lease')
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

    selected = take('government-xl-palazzo76610-retained-five-original-recovery-v1-20261101', 'selection.json.gz')
    rows = [r for r in selected['rows'] if r['uid']=='landsd/88780:0']
    assert {r['source']['building']['objectId'] for r in rows} == EXPECTED and len(rows) == 1
    resources = sorted('building:'+r['uid'] for r in rows)
    lp = Path(a.lease) if a.lease else HERE / 'local' / BATCH / 'reservation.json'
    if not a.owned and not a.lease:
        assert not lp.parent.exists()
        claim = reservations.claim('palazzo-identity-'+str(uuid.uuid4()), resources, batch=BATCH, ttl=3600)
        assert claim['ok'], claim
        return execute_reserved(claim['reservation'], lp, [sys.executable, __file__, '--owned'])
    lease = read(lp)
    assert reservations.owns(lease) and set(resources) <= set(lease['resources'])
    primary = take(P+'retained-five-official-records-v1-20261101', 'footprints.json')['features']
    assert len(primary) == 6
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selected['manifestSHA256']
    refs.append(manifest)
    views = {}
    for name in ['retained-five-source-views-v1-20261101']:
        batch = P+name
        take(batch, 'summary.json')
        for path in sorted((base/batch).glob('*-plan.png')):
            uid = 'landsd/'+path.name.split('-')[0]+':0'
            if uid != 'landsd/88780:0': continue
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
        proof = take(P+'retained-five-original-identity-v1-20261101', uid.split('/')[1]+'/identity.json')
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
        observation = 'All three complete source views individually inspected. The long narrow rimmed original unit follows the exact surveyed footprint orientation; the magenta footprint extends along one edge beyond the supplied body. Exact unique GeoRef/type/CSUID/ObjectID, original graph and current primary BuildingID identify this supplied unit. Raw90.6099% target coverage remains. This is not a claim of complete footprint coverage, reconstruction, support or placement.'
        reviewed.append(dict(uid=uid, sourceSHA256=row['sourceSHA256'], modelId=row['modelId'], buildingCSUID=form['buildingCSUID'], stableBuildingID=form['buildingId'], freshPrimaryRecord=record, sourceWorldSHA256=proof['worldTrianglesSHA256'], rawIdentityVerbatim=proof, identityAccepted=True, identityOnlyApproved=True, identityReviewApproved=True, observation=observation, sourceImagesActuallyInspected=views[uid], physicalAcceptance=False, installationApproved=False, publication=False))
    assert reservations.owns(lease) and digest(manifest.read_bytes()) == selected['manifestSHA256']
    result = dict(uids=sorted(r['uid'] for r in rows), sourceSHA256ByUid={r['uid']:r['sourceSHA256'] for r in rows}, rows=reviewed, identityAccepted=True, identityOnlyApproved=True, rawIdentityWarningsPreserved=True, sourceGeometryChanges=0, sourcePoseChanges=0, aiGeometryModelling=False, sourceEvidenceInterpretationUsedAI=True, modelAndEffort='Unknown from tool-visible metadata; not inferred', physicalAcceptance=False, installationApproved=False, publication=False, qualification='Bounded identity interpretation of exactly one complete provider-owned unit88780 at unchanged source pose. Fresh unique Active BuildingID/CSUID/GeoRef/type/heights, current exact forms, original source graphs, full source bytes and three individually inspected source views are bound. Roof-projection coverage is not architectural completeness; all raw coverage/extent/foreign overlap warnings remain verbatim. No global acceptance rule changes and no identity approval for any other revision, physical/placement/support/collision/runtime/browser/publication or optimisation approval.')
    for row in reviewed:
        save(out/row['uid'].split('/')[1]/'ROOT-IDENTITY-REVIEW.json', row)
    save(out/'summary.json', result)
    refs.append(HERE/'exact_packed_world_geometry_20261009.py')
    module('palazzo88780_identity_review_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'bounded-one-original-provider-unit-identity-review-only', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
