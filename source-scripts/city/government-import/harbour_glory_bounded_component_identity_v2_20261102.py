"""Named unchanged original components; preserve both raw component-shape failures.

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
BATCH = 'government-xl-harbour-glory-eleven-exact-component-identity-review-v2-20261102'
CAPTURE = 'government-xl-harbour-glory-eleven-after-shangrila-v2-20261102-runtime'
IDENTITY = 'government-xl-harbour-glory-eleven-after-shangrila-v2-20261102-identity'
EXACT = {'landsd/35148:0': ('8e70c6bcec6eaa6462a1fd27a6dc2bef7a2c82711cdfd59b3857550e3056d6b9', '3791616746T20190201', 'B379161674601063C0'), 'landsd/247461:0': ('6f7f1e34e35487b314ea73457bbdd930ab9d53a8c1e9a7a7db175cf1f3678c85', '3790316766P20190204', 'B379031676602063C0'), 'landsd/108870:0': ('6c263cf331e9c478c2d33882db68c5d96f21159d6692fa2889923af2c84a356d', '3788816762T20190201', 'B378881676201063C0'), 'landsd/258158:0': ('4b05058c2fe2a19a1907f71302db2c14710adba358395df0a24cd7b0b05cc132', '3788616698T20190201', 'B378861669801063C0'), 'landsd/260014:0': ('11c55026bd34b29802e02355c298b0f4c3a97f6944ad0f944a088ca40e90185f', '3789916775T20190201', 'B378991677501063C0'), 'landsd/271909:0': ('d3701b6581e00494db9df4aaf16810017a09d13bfe04bf1f33f2e30a156594d1', '3784816713T20190201', 'B378481671301063C0'), 'landsd/273684:0': ('348f3eb99497e96e0e1011136aa44950a281d11b47f5ffb4dabfeb2e1fdaf2a1', '3786816695T20190201', 'B378681669501063C0'), 'landsd/28391:0': ('db29ceae389c65517aea12a1dee4ffd734b3e9b1db1c15c9f24c2e51bbbdac53', '3787116683P20190204', 'B378711668302063C0'), 'landsd/67682:0': ('706c91a53f3d39956ff597608bed731df21d2a7fc412f71711111d78e8634aa9', '3789516710T20190201', 'B378951671001063C0'), 'landsd/92999:0': ('9e3fd83bf47930059f31d95fba2e05bac684e65cc402271cf9833f16de60e3e3', '3793016731T20190201', 'B379301673101063C0'), 'landsd/232659:0': ('60e13d7f6ed4cdc7243d4c98a666f4c39c35f56eb9199b2dfbcaf4d3142ed295', '3787616769T20190201', 'B378761676901063C0')}

def main():
    out = BASE / BATCH
    lp = HERE / 'local' / BATCH / 'reservation.json'
    if '--owned' not in sys.argv:
        assert not out.exists() and not lp.parent.exists()
        c = reservations.claim('harbour-glory-component-identity-' + str(uuid.uuid4()),
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
    observation = BASE / 'government-xl-harbour-glory-eleven-identity-observations-v1-20261102.json'
    seen = read(observation)
    assert set(seen['observations'])=={'landsd/247461:0','landsd/92999:0'}
    refs.append(observation)
    rows = []
    for uid, (source_sha, csuid, model_id) in EXACT.items():
        row = selected[uid]
        identity_batch=IDENTITY
        raw = take(identity_batch, uid.split('/')[1] + '/identity.json')
        context = take(identity_batch, uid.split('/')[1] + '/context.json')['identity']
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
        if uid in seen['observations']:
            observed=seen['observations'][uid]
            assert observed['reviewer']=='Codex ROOT'and observed['diagramActuallyViewed']and not raw['passed']and raw['reasons']==observed['rawReasons']
            plot=take(observed['plotBatch'],'summary.json');image=plot['image']
            assert image==observed['image']and image['sha256']==digest((ROOT/image['path']).read_bytes())
            assert plot['sourceSHA256']==source_sha and plot['originalWorldSHA256']==raw['worldTrianglesSHA256'] and plot['completeSourceFaces']==row['triangles']
            refs.append(ROOT/image['path']);images=[image];basis=observed['basis']
        else:
            assert raw['passed']and not raw['reasons']
            basis=['Independently passed existing exact original component identity checks; no shape exception or whole-landmark claim.']
        proof = {k: True for k in ['exactObjectId', 'exactBuildingCSUID', 'uniqueViewerMatch', 'identityAccepted']}
        review = dict(uid=uid, sourceSHA256=source_sha, sourceFormSHA256=raw['sourceFormSHA256'],
            worldTrianglesSHA256=raw['worldTrianglesSHA256'], identityAccepted=True, identityProof=proof,
            rawProof=raw, rawReasonsPreserved=raw['reasons'], componentIdentityOnly=True,
            wholeLandmarkCompletenessClaimed=False, imagesActuallyViewed=images,
            sourceGeometryChanges=0, sourcePoseChanges=0, genericThresholdChanges=0,
            physicalAcceptance=False, collisionApproved=False, installationApproved=False, publication=False,
            sourceIdentityReviewUsedAI=bool(images), aiGeometryModelling=False, basis=basis)
        save(out / (uid.split('/')[1] + '-identity-review.json'), review)
        rows.append(dict(uid=uid, sourceSHA256=source_sha, identityAccepted=True, identityProof=proof,
                         rawReasonsPreserved=raw['reasons'], review=review))
    assert reservations.owns(lease) and digest(manifest.read_bytes()) == sha
    result = dict(uids=list(EXACT), rows=rows, identityAccepted=True, currentManifestSHA256=sha,
        sourceSHA256ByUid={u: v[0] for u, v in EXACT.items()}, physicalAcceptance=False,
        installationApproved=False, publication=False, sourceGeometryChanges=0, sourcePoseChanges=0,
        sourceIdentityReviewUsedAI=True, aiGeometryModelling=False)
    save(out / 'summary.json', result)
    module('harbour_glory_bounded_identity_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'named-exact-harbour-glory-component-identity-raw-outline-failure-preserved', list(dict.fromkeys(refs)), result)

if __name__ == '__main__':
    main()
