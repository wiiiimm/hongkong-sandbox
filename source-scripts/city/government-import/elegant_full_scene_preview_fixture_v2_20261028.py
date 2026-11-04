"""Prepare an unapproved full-scene fixture; never publish or edit viewer files."""
import argparse
import copy
import subprocess
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations, connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from elegant_basic_footing_foreign_volume_v1_20261028 import BASE, PREFIX, SCOPE, RUNTIME, PROPOSAL

from original_catalogue_source_sheets_v1_20261028 import source_sheet_bindings

PATCH = PREFIX+'sixteen-original-two-member-partition-v1-20261028'
REGRESSION = PREFIX+'sixteen-original-updated-neighbours-v1-20261028'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch', required=True)
    p.add_argument('--owned', action='store_true')
    a = p.parse_args()
    assert a.batch.startswith(PREFIX) and '/' not in a.batch
    out, local = BASE/a.batch, HERE/'local'/a.batch
    assert not out.exists()
    rp = BASE/(PREFIX+'sixteen-original-updated-terrain-plan-v1-20261028.json')
    resources, lp = set(read(rp)['resources']), local/'reservation.json'
    if not a.owned:
        assert not local.exists()
        claim = reservations.claim('elegant-private-full-scene-fixture-'+str(uuid.uuid4()), sorted(resources), batch=a.batch, ttl=1800)
        assert claim['ok']
        return execute_reserved(claim['reservation'], lp, [sys.executable, __file__, *sys.argv[1:], '--owned'])
    lease = read(lp)
    assert reservations.owns(lease) and resources <= set(lease['resources'])
    refs, pins = [Path(__file__), rp], {}

    def take(batch, name):
        if batch not in pins:
            pins[batch] = authenticate(BASE/batch)[1]
            refs.append(BASE/batch/'result.json')
        path = BASE/batch/name
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    scope = take(SCOPE, 'scope.json')
    forms = take(SCOPE, 'form-obligations.json.gz')
    selection = take(RUNTIME, 'selection.json.gz')
    regression = take(REGRESSION, 'summary.json')
    terrain_receipt, terrain_pins = authenticate(BASE/PATCH)
    refs.append(BASE/PATCH/'result.json')
    assert len(selection['rows']) == 16 and len(forms) == scope['intersectingForms'] == regression['forms'] == 156
    assert set(scope['uids']) == {r['uid'] for r in selection['rows']}
    assert set(regression['requiredNativeUids']) == set(regression['nativeResolved']) == set(scope['touchingNativeUids'])
    assert len(scope['touchingNativeUids']) == 9 and all(r['passed'] for r in regression['nativeRows'])
    assert {r['uid'] for r in regression['basicFlags']} == {'landsd/99061:0', 'landsd/213586:0', 'landsd/336456:0'}
    manifest_path = ROOT/'3d-viewer/city/data/manifest.json'
    manifest_sha = digest(manifest_path.read_bytes())
    assert manifest_sha == selection['manifestSHA256'] == pins[SCOPE][str(manifest_path.relative_to(ROOT))]
    refs.append(manifest_path)
    manifest = read(manifest_path)
    all_native, retained = {}, []
    for url in manifest['officialModelCatalogues']:
        cat_path = ROOT/'3d-viewer'/url
        for e in read(cat_path)['models']:
            assert e['uid'] not in all_native
            all_native[e['uid']] = e
            if e['uid'] in scope['touchingNativeUids']:
                asset = cat_path.parent/e['asset']
                assert digest(asset.read_bytes()) == e['sha256']
                retained.append(dict(uid=e['uid'], entry=e, catalogue=url, catalogueSHA256=digest(cat_path.read_bytes()), assetPath=str(asset.relative_to(ROOT))))
                refs.extend([cat_path, asset])
    assert len(all_native) == scope['currentNativeActors'] == 6991 and len(retained) == 9
    assert not set(scope['uids']) & set(all_native)
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        sheets = source_sheet_bindings(db, selection['rows'])
    save(out/'source-sheet-bindings.json', list(sheets.values()))
    refs.append(HERE/'original_catalogue_source_sheets_v1_20261028.py')
    entries = []
    for row in selection['rows']:
        b = row['source']['building']
        tile = ROOT/'3d-viewer'/row['source']['tile']
        assert next(f for f in read(tile)['buildings'] if f['uid'] == b['uid']) == b
        assert digest(tile.read_bytes()) == row['source']['tileSHA256']
        asset = ROOT/row['candidate']['path']
        assert digest(asset.read_bytes()) == row['sourceSHA256']
        e = copy.deepcopy(row['candidate']['entry'])
        assert e['sha256'] == row['sourceSHA256'] and e['triangles'] == row['triangles']
        e['sourceTile'] = sheets[row['uid']]['sourceTile']
        e.update(priority='landmark', proceduralWindows=False, publicationApproved=False,
                 placementReviewed=False, identityReviewApproved=False, sourceIdentityReviewed=False)
        assert 'supportDependencies' not in e and 'activationGroup' not in e
        e['asset'] = 'assets/'+e['sha256']+'.glb.gz'
        dest = local/e['asset']
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(asset.read_bytes())
        assert digest(dest.read_bytes()) == e['sha256']
        refs.extend([tile, asset, dest])
        entries.append(e)
    save(local/'catalogue.json', dict(schemaVersion=1, kind='staged-official-model-catalogue',
        diagnosticOnly=True, physicalAcceptance=False, publicationApproved=False,
        datasetId='landsd_rcd_1742809441342_98380', crs='EPSG:2326',
        verticalDatum='Hong Kong Principal Datum', rootTranslation=[-834500, 0, 816500],
        models=entries, counts=dict(packedModels=len(entries))))
    preflight = HERE/'private_original_catalogue_preflight_v1_20261028.mjs'
    refs.extend([preflight, ROOT/'3d-viewer/city/official-model-assets.js'])
    with (out/'production-catalogue-preflight.log').open('w') as log:
        subprocess.run(['node', str(preflight), str((local/'catalogue.json').relative_to(ROOT)),
                        'http://127.0.0.1:4177/city/data/official-models/'+a.batch+'/catalogue.json'],
                       cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
    save(local/'source-forms.json', [r['source']['building'] for r in selection['rows']])
    terrains = []
    assert len(terrain_receipt['members']) == 2
    for member in terrain_receipt['members']:
        path = ROOT/member['candidate']['path']
        assert member['validatorPassed'] and digest(path.read_bytes()) == member['candidate']['sha256'] == terrain_pins[str(path.relative_to(ROOT))]
        old = member['replaces']
        old_path = ROOT/old['path']
        assert digest(old_path.read_bytes()) == old['sha256']
        terrains.append(dict(source=str(path.relative_to(ROOT)), sourceSHA256=digest(path.read_bytes()),
                             destination='city/data/government-xl-elegant-garden-'+member['member']+'-original-v1-20261028.json',
                             resolution=read(path)['cell'], area='Private unapproved full-scene diagnostic', replaces=old))
        refs.extend([path, old_path])
    assert {t['replaces']['url'] for t in terrains} == {t['url'] for t in scope['terrainContacts'] if t['coarseOverlapAreaM2'] > 0}
    by_tile = {}
    proposals = [(PROPOSAL, 'surveyed-solid-podium'),
                 (PREFIX+'main-canopy-final-sixteen-posts-v1-20261028', 'existing-estimated-open-canopy'),
                 (PREFIX+'grand-scholar-final-sixteen-posts-v1-20261028', 'existing-estimated-open-canopy')]
    for batch, role in proposals:
        inp = take(batch, 'input.json')
        proposal = take(batch, 'proposal.json')
        # Canopy producer and podium producer both bind the exact building.
        b = inp['building']
        assert b in forms and proposal['uid'] == b['uid'] and proposal['originalBase'] == b['base']
        url = 'city/data/tiles/'+b['tile']+'.json'
        path = ROOT/'3d-viewer'/url
        assert digest(path.read_bytes()) == pins[SCOPE][str(path.relative_to(ROOT))]
        assert next(f for f in read(path)['buildings'] if f['uid'] == b['uid']) == b
        if url not in by_tile:
            by_tile[url] = dict(path=path, before=read(path), changes=[])
        by_tile[url]['changes'].append(dict(uid=b['uid'], before=b, foundationBase=proposal['foundationBase'], role=role, proposalApproved=False,
            proposal=dict(path=str((BASE/batch/'proposal.json').relative_to(ROOT)), sha256=digest((BASE/batch/'proposal.json').read_bytes()))))
        refs.append(path)
    overlays = []
    for url, record in by_tile.items():
        after = copy.deepcopy(record['before'])
        for change in record['changes']:
            b = next(f for f in after['buildings'] if f['uid'] == change['uid'])
            assert b.get('foundationBase') is None and b.get('foundationPolicy') is None
            b['foundationBase'] = change['foundationBase']
        dest = local/('private-foundation-'+Path(url).name)
        save(dest, after)
        overlays.append(dict(url=url, beforeSHA256=digest(record['path'].read_bytes()),
                             source=str(dest.relative_to(ROOT)), afterSHA256=digest(dest.read_bytes()), changes=record['changes']))
        refs.append(dest)
    assert sum(len(o['changes']) for o in overlays) == 3
    config = dict(diagnosticOnly=True, publication=False, stage=str(local.relative_to(ROOT))+'/',
        catalogueURL='city/data/official-models/'+a.batch+'/catalogue.json', terrain=terrains,
        privateFoundationTileOverlays=overlays, viewerURL='http://127.0.0.1:4177/city.html',
        browserUids=scope['uids'], additionalRetainedUids=scope['touchingNativeUids'],
        retainedNativeOwnViews=True, jointUids=scope['uids'], fitJointCamera=True,
        fitJointCameraMobile=True, fitBox=True, failureTestUids=[],
        captureDirectionByModel={uid: [-.7, .8, 1] for uid in scope['uids']})
    save(local/'config.json', config)
    save(out/'retained-originals.json', retained)
    save(out/'fixture-inputs.json', dict(configPath=str((local/'config.json').relative_to(ROOT)), resources=sorted(resources),
        sourceSHA256ByUid={r['uid']: r['sourceSHA256'] for r in selection['rows']},
        currentManifestSHA256=manifest_sha, availabilityAcceptance=False, failureTestsDeliberatelyDeferred=True))
    refs.extend([local/'catalogue.json', local/'source-forms.json', local/'config.json', HERE/'ronsdale_three_live_browser_v17_20261028.mjs'])
    result = dict(uids=scope['uids'], models=16, retained=9, terrainMembers=2, privateBasicFoundations=3,
        fixture=str((local/'config.json').relative_to(ROOT)), currentManifestSHA256=manifest_sha,
        sourceGeometryChanges=0, governmentGeometryChanges=0, publication=False,
        diagnosticOnly=True, physicalAccepted=False, visualReviewApproved=False,
        installationApproved=False, availabilityAcceptance=False,
        qualification='Exact unapproved private scene fixture with sourceTile bound to unchanged Neon cache results and the production catalogue validator replayed before browser startup:16unchanged original assets,9unchanged installed entries/assets,two validated source-bound terrain members,and exactly3source-bound foundationBase-only BASIC tile overlays. Every approval staysfalse. Initial visual run deliberately has no candidate dependency/atomic-availability acceptance; failure testing is deferred and must not be inferred from this fixture. No viewer file, original geometry or installed catalogue changed.')
    save(out/'summary.json', result)
    assert reservations.owns(lease)
    module('elegant_full_scene_fixture_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'private-unapproved-full-sixteen-source-two-terrain-three-basic-fixture', list(dict.fromkeys(refs)), result)
    print(dict(models=16, retained=9, terrainMembers=2, privateBasicFoundations=3, publication=False), flush=True)


if __name__ == '__main__':
    main()
