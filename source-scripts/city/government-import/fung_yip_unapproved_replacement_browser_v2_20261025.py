"""Private unapproved Fung Yip preview; grants no physical, identity or publication acceptance."""
import argparse
import copy
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations, connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'runtime', 'patch', 'regression', 'scope']:
        parser.add_argument('--' + key, required=True)
    parser.add_argument('--support', action='append', default=[], help='sourceUid,supportUid')
    parser.add_argument('--retain-basic', action='append', default=[])
    parser.add_argument('--retain-native', action='append', default=[])
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc, local = base / args.batch, HERE / 'local' / args.batch
    leasepath = local / 'reservation.json'
    refs, receipts, pins = [Path(__file__)], {}, {}
    for name in [args.runtime, args.patch, args.regression, args.scope]:
        receipt, bound = authenticate(base / name)
        receipts[name] = receipt
        refs.append(base / name / 'result.json')
        for key, sha in bound.items():
            assert key not in pins or pins[key] == sha
            pins[key] = sha
    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    selection = take(base / args.runtime / 'selection.json.gz')
    rows = selection['rows']
    uids = [r['uid'] for r in rows]
    assert len(uids) == len(set(uids)) and len(uids) <= 40
    supports = dict(pair.split(',') for pair in args.support)
    assert set(supports) <= set(uids) and set(supports.values()) <= set(uids)
    # This is a deliberately unapproved private preview, never a qualified stage.
    prefix = 'government-xl-fung-yip-after-inone-'
    assert args.batch == prefix + 'unapproved-browser-v2-20261025'
    assert args.runtime == prefix + 'seam-runtime-v2-20261025'
    assert args.patch == prefix + 'replacement-binding-v2-20261025'
    assert args.regression == prefix + 'native-regression-v2-20261025'
    assert args.scope == prefix + 'seam-scope-v2-20261025'
    expected = {'landsd/254815:0': '501cc0df37031950a05a7725d0b918c2b28e8daa5fc0e02f1b78c0b2e9723c42',
                'landsd/79883:0': 'f6034a6d28e0f7d82bc2094e9817ea253fe700695d3d228825ea794c5375b6d5'}
    assert {r['uid']: r['sourceSHA256'] for r in rows} == expected
    assert supports == {'landsd/254815:0': 'landsd/79883:0'}
    regression = take(base / args.regression / 'summary.json')
    assert regression['forms'] == 56 and not regression['basicFlags']
    assert set(regression['requiredNativeUids']) == set(args.retain_native) == {'landsd/79882:0', 'landsd/12728:0', 'landsd/338946:0'}
    assert set(regression['nativeResolved']) == set(args.retain_native)
    assert len(regression['nativeRows']) == 3 and all(r['passed'] for r in regression['nativeRows'])
    assert not args.retain_basic
    forms = take(base / args.scope / 'form-obligations.json.gz')
    assert len(forms) == 56 and set(uids + args.retain_native) <= {f['uid'] for f in forms}
    old_url = receipts[args.patch]['candidate']['replaces']['url']
    resources = sorted({('building:' if f['uid'].startswith('landsd/') else 'source-form:') + f['uid'] for f in forms} | ({'terrain:city/data/terrain.json', 'terrain:' + old_url} | {'terrain:' + r['url'] for r in take(base / args.scope / 'scope.json')['terrainContacts']}))
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256']
    refs.append(manifest)
    if not args.owned:
        assert not doc.exists() and not local.exists()
        claim = reservations.claim(args.batch + '-' + str(uuid.uuid4()), resources, batch=args.batch, ttl=3600)
        assert claim['ok'], claim
        lease = claim['reservation']
        save(leasepath, json.loads(json.dumps(lease, default=str)))
        try:
            subprocess.run([sys.executable, str(HERE / 'bounded_reserved_runner_v2_20261022.py'), str(leasepath), sys.executable, __file__, *sys.argv[1:], '--owned'], cwd=ROOT, check=True)
        finally:
            if reservations.owns(lease):
                assert reservations.release(lease)['ok']
        return
    lease = read(leasepath)
    assert reservations.owns(lease) and not doc.exists()
    assert set(resources) <= set(lease['resources'])
    entries = []
    for row in rows:
        uid = row['uid']
        source = row['source']
        tile = ROOT / '3d-viewer' / source['tile']
        assert next(b for b in read(tile)['buildings'] if b['uid'] == uid) == source['building']
        refs.append(tile)
        with connect() as db:
            db.execute('SET TRANSACTION READ ONLY')
            native = db.execute('SELECT i.sheet,r.result_sha FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE i.cache_key=%s', (row['native']['cacheKey'],)).fetchone()
        assert native and native[1] == row['native']['resultSha']
        entry = copy.deepcopy(row['candidate']['entry'])
        if uid in supports:
            support = next(r for r in rows if r['uid'] == supports[uid])
            entry['supportDependencies'] = [dict(uid=support['uid'], state='installed', buildingCSUID=support['source']['building']['buildingCSUID'], sha256=support['sourceSHA256'])]
        entry.update(sourceTile=native[0], priority='landmark', proceduralWindows=False, publicationApproved=False, placementReviewed=False)
        asset = ROOT / row['candidate']['path']
        assert digest(asset.read_bytes()) == row['sourceSHA256']
        refs.append(asset)
        entry['asset'] = 'assets/' + row['sourceSHA256'] + '.glb.gz'
        destination = local / entry['asset']
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(asset.read_bytes())
        entries.append(entry)
    save(local / 'catalogue.json', dict(schemaVersion=1, kind='staged-official-model-catalogue', datasetId='landsd_rcd_1742809441342_98380', crs='EPSG:2326', verticalDatum='Hong Kong Principal Datum', rootTranslation=[-834500, 0, 816500], models=entries, counts=dict(packedModels=len(entries))))
    save(local / 'catalogue-index.json', dict(models=len(entries), catalogues=['catalogue.json']))
    save(local / 'source-forms.json', [r['source']['building'] for r in rows])
    save(local / 'validation-forms.json', {r['uid']: r['source'] for r in rows})
    candidate = receipts[args.patch]['candidate']
    terrainpath = ROOT / candidate['path']
    assert digest(terrainpath.read_bytes()) == candidate['sha256']
    refs.append(terrainpath)
    terrain = [dict(source=candidate['path'], destination='city/data/' + args.batch + '-terrain.json', sha256=candidate['sha256'], resolution=read(terrainpath)['cell'], area='Private original-source diagnostic')]
    replacement = candidate['replaces']
    old_path = ROOT / '3d-viewer' / replacement['url']
    assert digest(old_path.read_bytes()) == replacement['sha256']
    old, new = read(old_path), read(terrainpath)
    assert old['coarseCells'] == new['coarseCells']
    assert set(old['meta']['targetUids']) == set(replacement['retainedUids'])
    assert set(replacement['retainedUids']) <= set(new['meta']['targetUids']) & set(args.retain_native)
    assert any(t['url'] == replacement['url'] for t in read(manifest)['terrainPatches'])
    refs.append(old_path)
    terrain[0]['replaces'] = replacement
    tool = HERE / 'ronsdale_three_live_browser_v12_20261025.mjs'
    refs.append(tool)
    assert len(set(args.retain_native)) == len(args.retain_native) and not set(args.retain_native).intersection(uids + args.retain_basic)
    config = dict(retainedNativeOwnViews=True, retainedCaptureDirectionByModel={'landsd/79882:0': [-1, .9, .1]}, additionalRetainedUids=args.retain_native, stage=str(local.relative_to(ROOT)) + '/', catalogueURL='city/data/official-models/' + args.batch + '/catalogue.json', terrain=terrain, browserUids=uids, fitBox=True, captureDirectionByModel={uid: ([.1, 1.1, 1] if uid in supports.values() else [-.7, .7, 1]) for uid in uids}, retainedBuildingUids=args.retain_basic, jointUids=uids, nativeSupportUidsByModel={uid: [support] for uid, support in supports.items()})
    preflightpath = local / 'preflight-config.json'
    save(preflightpath, dict(**config, doc=str(doc.relative_to(ROOT)) + '/'))
    subprocess.run(['node', str(tool), 'preflight', str(preflightpath.relative_to(ROOT))], cwd=ROOT, check=True)
    for width in [1280, 390]:
        assert reservations.owns(lease)
        path = local / f'browser-config-{width}.json'
        save(path, dict(**config, viewportWidths=[width], failureTestUids=uids if width == 390 else [], doc=str((doc / str(width)).relative_to(ROOT)) + '/'))
        doc.mkdir(parents=True, exist_ok=True)
        with (doc / f'browser-{width}.log').open('w') as log:
            proc = subprocess.run(['node', str(tool), 'staged', str(path.relative_to(ROOT))], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, env={**os.environ, 'CHROME_PATH': '/opt/google/chrome/chrome'}, timeout=1200)
        save(doc / f'command-{width}.json', dict(exitCode=proc.returncode))
        assert proc.returncode == 0 and read(doc / str(width) / 'staged-browser.json')['passed']
    for path in set(refs):
        key = str(path.relative_to(ROOT))
        if key in pins:
            assert digest(path.read_bytes()) == pins[key]
    assert reservations.owns(lease)
    refs.extend(path for path in local.rglob('*') if path.is_file() and path.name != 'reservation.json')
    result = dict(uids=uids, installationApproved=False, visualAcceptance=False, identityAccepted=False, sourceSpecificPhysicalInterpretationAccepted=False, publication=False, privateDiagnosticOnly=True, sourceGeometryChanges=0, scriptExternalAICalls=0)
    module('selected_browser_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'unapproved-exact-fung-yip-retained-terrain-desktop-mobile-diagnostic', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
