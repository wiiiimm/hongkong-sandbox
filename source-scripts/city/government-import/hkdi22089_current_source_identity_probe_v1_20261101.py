"""Recheck installed HKDI source identity without changing its legacy flags.

This is a current source-component diagnostic, not whole-campus acceptance or
permission for a new dependency. The normal identity verifier remains unchanged.
"""
import sys, uuid, subprocess
from pathlib import Path
from copy import deepcopy
from run import ROOT, HERE, read, save, digest, connect, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-hkdi22089-current-source-identity-probe-v1-20261101'
HISTORICAL = 'government-xl-terrain-recovery-hkdi-complete-original-current-probe-v1-20261010'
UID = 'landsd/22089:0'
SHA = '5cd70cb3bdb879ca96528fd1ff6ce29cc3b61c054b70456ec169fc9cf4831c40'

def main():
    out, local = BASE / BATCH, HERE / 'local' / BATCH
    assert not out.exists()
    if '--owned' not in sys.argv:
        assert not local.exists()
        c = reservations.claim('hkdi-parent-source-only-' + str(uuid.uuid4()), ['building:' + UID], batch=BATCH, ttl=3600)
        assert c['ok'], c
        return execute_reserved(c['reservation'], local / 'reservation.json', [sys.executable, __file__, '--owned'])
    lease = read(local / 'reservation.json')
    assert reservations.owns(lease)
    _, pins = authenticate(BASE / HISTORICAL)
    selectionpath = BASE / HISTORICAL / 'selection.json.gz'
    assert digest(selectionpath.read_bytes()) == pins[str(selectionpath.relative_to(ROOT))]
    row = deepcopy(next(r for r in read(selectionpath)['rows'] if r['uid'] == UID))
    assert row['sourceSHA256'] == SHA
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    start = digest(manifest.read_bytes())
    refs = [Path(__file__), BASE / HISTORICAL / 'result.json', selectionpath, manifest]
    matches = []
    for url in read(manifest)['officialModelCatalogues']:
        cat = ROOT / '3d-viewer' / url
        for e in read(cat)['models']:
            if e['uid'] == UID: matches.append((cat, e, read(cat)['rootTranslation']))
    assert len(matches) == 1
    cat, entry, root = matches[0]
    asset = cat.parent / entry['asset']
    assert root == [-834500, 0, 816500] and digest(asset.read_bytes()) == entry['sha256'] == SHA
    assert entry['identityReviewApproved'] is False and entry['wholeLandmarkAccepted'] is False
    assert entry['placementReviewed'] is True and entry['publicationApproved'] is True
    refs.extend([cat, asset])
    forms = []
    for tile in read(manifest)['tiles']:
        path = ROOT / '3d-viewer' / tile['url']
        for b in read(path)['buildings']:
            if b['uid'] == UID: forms.append((path, tile['url'], b))
    assert len(forms) == 1
    tile, url, form = forms[0]
    assert form['objectId'] == entry['objectId'] == 22089
    assert form['buildingCSUID'] == entry['buildingCSUID'] == row['source']['building']['buildingCSUID']
    assert entry['modelId'] == row['modelId'] == row['native']['model']['modelId']
    refs.append(tile)
    pointer = ROOT / 'docs/astra-city/model-integration-20260909/current-source-review.json'
    snapshot = read(pointer)['snapshotId']
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        assert db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s', (snapshot, UID)).fetchone() == ('installed-verified', SHA)
        native = db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s', (row['native']['cacheKey'],)).fetchone()
        assert native[0] == row['native']['resultSha']
        model = next(m for m in native[1]['models'] if m['modelId'] == entry['modelId'])
        assert model == row['native']['model'] and model['asset']['sha256'] == SHA
        candidates = [c for c in model['matching']['officialCandidates'] if c['objectId'] == form['objectId'] and c['buildingCSUID'] == form['buildingCSUID']]
        assert len(candidates) == 1
    refs.append(pointer)
    row['source'] = dict(building=form, tile=url, tileSHA256=digest(tile.read_bytes()))
    row['candidate'] = dict(path=str(asset.relative_to(ROOT)), entry={**deepcopy(entry), 'rootTranslation': root})
    source_acceptance = ROOT / 'docs/astra-city/assembly-support-review/visual-acceptance-hkdi.json'
    acceptance = read(source_acceptance)
    assert acceptance['approvedSourceUids'] == [UID] and not acceptance['wholeLandmarkAccepted'] and acceptance['sourceGeometryUnchanged']
    refs.append(source_acceptance)
    assert reservations.owns(lease) and digest(manifest.read_bytes()) == start
    save(out / 'selection.json.gz', dict(rows=[row], manifestSHA256=start))
    result = dict(uids=[UID], sourceSHA256=SHA, currentManifestSHA256=start, currentInstalledSnapshot=snapshot,
        rawInstalledEntry=entry, rawLegacyIdentityReviewApproved=False, rawWholeLandmarkAccepted=False,
        sourceComponentApprovalIsSeparateFromWholeLandmark=True, exactNativeStageRecordRechecked=True,
        oldSourceFormEqualsCurrent=row['source']['building'] == next(r for r in read(selectionpath)['rows'] if r['uid'] == UID)['source']['building'],
        nativeMetadataChanges=0, sourceGeometryChanges=0, sourcePoseChanges=0, identityAccepted=False,
        physicalAcceptance=False, installationApproved=False, publication=False,
        qualification='Existing installed native retained byte-for-byte, including negative identity/whole-landmark flags. Separate diagnostic selection permits the unchanged current source identity verifier to assess the exact original component; no approval or new support dependency is installed.')
    save(out / 'summary.json', result)
    module('hkdi_installed_source_probe_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'current-installed-original-source-component-identity-input-only', refs, result)
    subprocess.run([sys.executable, str(HERE / 'selected_original_identity_v3.py'), '--batch', BATCH + '-identity', '--capture', BATCH], cwd=ROOT, check=True)
    assert reservations.owns(lease) and digest(manifest.read_bytes()) == start

if __name__ == '__main__': main()
