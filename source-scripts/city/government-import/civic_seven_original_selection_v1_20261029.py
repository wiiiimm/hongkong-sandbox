"""Bind two civic podiums and their five contacted originals to the current map.

No recovery/conversion, identity approval, terrain or model edits. The two sites
remain separate cohorts; contact alone never creates a physical dependency.
"""
import argparse
import copy
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from upton_staged_image_review_binding_v1_20261014 import inventory_delta

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-civic-seven-current-original-selection-v1-20261029'
TARGETS = ['landsd/231013:0', 'landsd/82291:0']
PREVIOUS = BASE / 'government-xl-elegant-garden-original-installed-v1-20261028/full-xl-current-count.json'


def cases():
    result = []
    for uid in TARGETS:
        folder = BASE / ('government-xl-next-nine-two-case-' + uid.split('/')[1].replace(':', '-') + '-contacts-v1-20261028')
        receipt, _ = authenticate(folder)
        assert receipt['targetUid'] == uid and receipt['allNominatedOriginalsTested'] and not receipt['missingCachedSources']
        result.append((folder, receipt))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    out, local = BASE / BATCH, HERE / 'local' / BATCH
    lp = local / 'reservation.json'
    assert not out.exists()
    inputs = cases()
    wanted = set(TARGETS) | {r['peer']['uid'] for _, c in inputs for r in c['rows'] if r['finiteContacts'] > 0}
    assert len(wanted) == 7
    if not args.owned:
        assert not local.exists()
        claim = reservations.claim('civic-original-selection-' + str(uuid.uuid4()),
                                   ['building:' + uid for uid in sorted(wanted)], batch=BATCH, ttl=1800)
        assert claim['ok']
        return execute_reserved(claim['reservation'], lp, [sys.executable, __file__, '--owned'])
    lease = read(lp)
    assert reservations.owns(lease)
    manifestpath = ROOT / '3d-viewer/city/data/manifest.json'
    manifestsha = digest(manifestpath.read_bytes())
    manifest = read(manifestpath)
    refs = [Path(__file__), manifestpath, PREVIOUS]
    installed = {}
    forms = {}
    for url in manifest['officialModelCatalogues']:
        path = ROOT / '3d-viewer' / url
        refs.append(path)
        for model in read(path)['models']:
            assert model['uid'] not in installed
            installed[model['uid']] = model
    assert len(installed) == 7007 and not wanted & set(installed)
    # All relevant source forms are in these observed current manifest tiles.
    for url in ['city/data/tiles/1_-6.json', 'city/data/tiles/1_-2.json']:
        assert url in {t['url'] for t in manifest['tiles']}
        path = ROOT / '3d-viewer' / url
        refs.append(path)
        for b in read(path)['buildings']:
            if b['uid'] in wanted:
                assert not b.get('modelGeometry')
                forms[b['uid']] = dict(building=b, tile=url, tileSHA256=digest(path.read_bytes()))
    assert set(forms) == wanted
    seeds, cohorts = {}, []
    inventorypath = BASE / 'government-xl-unfinished-territorial-neighbour-inventory-v1-20261028/summary.json'
    _, invpins = authenticate(inventorypath.parent)
    assert digest(inventorypath.read_bytes()) == invpins[str(inventorypath.relative_to(ROOT))]
    inventory = read(inventorypath)
    refs.extend([inventorypath, inventorypath.parent / 'result.json'])
    for folder, receipt in inputs:
        refs.append(folder / 'result.json')
        row = next(r for r in inventory['rows'] if r['uid'] == receipt['targetUid'])
        assert row['sourceKey'] == receipt['targetSourceKey'] and row['indexedSourceSHA256'] == receipt['sourceSHA256']
        seeds[row['uid']] = (row, receipt)
        members = [row['uid']]
        for contact in receipt['rows']:
            if contact['finiteContacts'] > 0:
                peer = contact['peer']
                assert peer['uid'] not in seeds
                seeds[peer['uid']] = (peer, receipt)
                members.append(peer['uid'])
        cohorts.append(dict(targetUid=row['uid'], uids=sorted(members), sourceOnlyContactReceipt=str((folder / 'result.json').relative_to(ROOT)),
                            physicalSupportAccepted=False, activationGroupApproved=False))
    rows = []
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for uid in sorted(wanted):
            seed, receipt = seeds[uid]
            cache, modelid = seed['sourceKey'].split('/')
            found = db.execute("SELECT r.result_sha,m.model FROM astra_modelling.native_stage_results r CROSS JOIN LATERAL jsonb_array_elements(r.result->'models') AS m(model) WHERE r.cache_key=%s AND m.model->>'modelId'=%s", (cache, modelid)).fetchall()
            assert len(found) == 1 and found[0][0] == seed['nativeResultSHA256']
            model = found[0][1]
            sha = model['asset']['sha256']
            assert sha == seed['indexedSourceSHA256']
            matches = [ROOT / r['path'] for r in receipt['evidenceRefs'] if r['sha256'] == sha and r['path'].endswith('.glb.gz')]
            assert matches
            asset = next(p for p in matches if p.exists())
            assert digest(asset.read_bytes()) == sha and asset.stat().st_size == model['asset']['bytes']
            refs.append(asset)
            source = forms[uid]
            b = source['building']
            assert b['buildingCSUID'][:10] == modelid[1:11]
            assert b['structureType'] == ('Tower' if modelid[11:13] == '01' else 'Podium')
            entry = dict(**copy.deepcopy(model['asset']), uid=uid, modelId=modelid,
                         label=b.get('name') or b.get('zh') or modelid, objectId=b['objectId'],
                         buildingCSUID=b['buildingCSUID'], recordedBaseHeight=b['baseHeightHKPD'],
                         recordedTopHeight=b['topHeightHKPD'], worldBounds=model['worldBounds'],
                         rootTranslation=[-834500, 0, 816500], sourceTile=seed['sheet'],
                         triangles=model['triangles'], priority='unreviewed', proceduralWindows=False,
                         placementReviewed=False, publicationApproved=False)
            rows.append(dict(uid=uid, source=source, modelId=modelid, sourceSHA256=sha,
                             triangles=model['triangles'], originalGeometryOnly=True,
                             native=dict(cacheKey=cache, resultSha=found[0][0], model=model),
                             candidate=dict(path=str(asset.relative_to(ROOT)), entry=entry)))
    pointer = read(ROOT / 'docs/astra-city/model-integration-20260909/current-source-review.json')
    delta = inventory_delta(read(PREVIOUS), [r['candidate']['entry'] for r in rows],
                            manifest_sha=manifestsha, snapshot=pointer['snapshotId'])
    assert digest(manifestpath.read_bytes()) == manifestsha
    assert reservations.owns(lease)
    save(out / 'selection.json.gz', dict(rows=rows, manifestSHA256=manifestsha))
    summary = dict(uids=sorted(wanted), cohorts=cohorts, currentNativeActors=7007,
                   currentManifestSHA256=manifestsha, sourceSHA256ByUid={r['uid']: r['sourceSHA256'] for r in rows},
                   projectedXLDelta=delta, projectionOnly=True, sourceGeometryChanges=0, sourcePoseChanges=0,
                   assetDownloads=0, identityAccepted=False, physicalAccepted=False, installationApproved=False,
                   qualification='Seven exact cached originals bound to unchanged current forms, typed georefs and pinned native records. Two independent sites remain separate. Positive original surface contacts nominate companions only; no dependency/identity/terrain/current-scene approval or installation credit transfers.', publication=False)
    save(out / 'summary.json', summary)
    module('civic_current_original_selection_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'seven-current-exact-originals-two-civic-site-selections', list(dict.fromkeys(refs)), read(out / 'summary.json'))
    print(dict(prepared=len(rows), sites=len(cohorts), projectedFixedXL=delta['expectedFixedXLDelta'], downloads=0), flush=True)


if __name__ == '__main__':
    main()
