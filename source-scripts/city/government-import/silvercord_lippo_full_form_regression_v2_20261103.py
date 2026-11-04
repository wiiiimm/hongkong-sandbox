"""Run the unchanged full-scope before/after form guard on the private parent."""
import sys
import math
import uuid
import subprocess
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v3_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
PREFIX = 'government-xl-silvercord-lippo-full-form-regression-v2-20261103'
CHUNK = int(sys.argv[sys.argv.index('--chunk')+1]) if '--chunk' in sys.argv else None
BATCH = PREFIX + ('-chunk-' + str(CHUNK).zfill(3) if CHUNK is not None else '')
CHUNK_SIZE = 900
SCOPE = 'government-xl-silvercord-lippo-full-current-parent-scope-v2-20261103'
CANDIDATE = 'government-xl-silvercord-lippo-coordinated-floor-candidate-v1-20261103'
LOCAL = HERE / 'local' / BATCH
UIDS = ['landsd/233997:0', 'landsd/231645:0']


def inputs():
    scope, pins = authenticate(BASE / SCOPE)
    path = BASE / SCOPE / 'full-parent-form-obligations.json.gz'
    assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
    forms = {f['uid']: f for f in read(path)}
    assert len(forms) == scope['basicFormsInFullParentScope']
    proposal, pp = authenticate(BASE / CANDIDATE); manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    mh = digest(manifest_path.read_bytes()); assert mh == scope['currentManifestSHA256'] == proposal['currentManifestSHA256']
    manifest = read(manifest_path); models = {}
    for url in manifest['officialModelCatalogues']:
        for model in read(ROOT / '3d-viewer' / url)['models']:
            assert model['uid'] not in models; models[model['uid']] = model
    required = set(scope['affectedNativeUids']); missing = required - forms.keys()
    for tile in manifest['tiles']:
        path = ROOT / '3d-viewer' / tile['url']; assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        for form in read(path)['buildings']:
            if form['uid'] in missing: forms[form['uid']] = form; missing.remove(form['uid'])
    assert not missing
    return scope, pins, proposal, pp, manifest, models, forms


def owned():
    lease = read(LOCAL / 'reservation.json'); assert reservations.owns(lease)
    scope, pins, proposal, pp, manifest, models, all_forms = inputs()
    assert CHUNK is not None and 0 <= CHUNK < math.ceil(len(all_forms)/CHUNK_SIZE)
    selected_ids = sorted(all_forms)[CHUNK*CHUNK_SIZE:(CHUNK+1)*CHUNK_SIZE]
    forms = {uid: all_forms[uid] for uid in selected_ids}
    refs = [Path(__file__), BASE / SCOPE / 'result.json', BASE / CANDIDATE / 'result.json']
    candidate = proposal['candidate']; path = ROOT / candidate['path']; assert digest(path.read_bytes()) == candidate['sha256']; refs.append(path)
    prior = proposal['replacedParent']; parent_path = ROOT / '3d-viewer' / prior['url']
    assert digest(parent_path.read_bytes()) == prior['sha256']; parent = read(parent_path); refs.append(parent_path)
    patch = dict(**candidate, replaces=dict(url=prior['url'], sha256=prior['sha256'], retainedUids=parent['meta']['targetUids']), uids=UIDS)
    hashes = {'3d-viewer/city/data/manifest.json': scope['currentManifestSHA256']}
    by_tile = {t['id']: t['url'] for t in manifest['tiles']}
    for form in forms.values():
        path = ROOT / '3d-viewer' / by_tile[form['tile']]; key = str(path.relative_to(ROOT))
        if key not in hashes:
            hashes[key] = digest(path.read_bytes()); assert hashes[key] == pins[key]; refs.append(path)
    out = BASE / BATCH
    save(out / 'neighbour-inputs.json.gz', dict(inputHashes=hashes, candidateIds=UIDS, patches=[patch],
                                             requiredNativeUids=sorted(set(scope['affectedNativeUids']) & set(forms)),
                                             rows=[dict(building=f, existingNative=f['uid'] in models, patchIndexes=[0]) for f in forms.values()]))
    tool = HERE / 'check-neighbours.mjs'
    with (out / 'worker.log').open('w') as log:
        subprocess.run(['node', str(tool), str(out.relative_to(ROOT))+'/'], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, timeout=7200, check=True)
    checks = read(out / 'neighbour-checks.json'); assert {r['uid'] for r in checks['rows']} == set(forms)
    for path, sha in checks['inputHashes'].items():
        assert digest((ROOT / path).read_bytes()) == sha; refs.append(ROOT / path)
    flagged = [r for r in checks['rows'] if r['reasons']]
    result = dict(uids=UIDS, chunk=CHUNK, checkedSourceUids=sorted(forms), fullScopeJobId=scope['jobId'], completeScopedForms=scope['basicFormsInFullParentScope'], checkedFormsIncludingRequiredNativeRecords=len(forms),
                  requiredFullNativeRegressions=len(scope['affectedNativeUids']), flagged=flagged,
                  ordinaryFlagged=sum(not r['existingNative'] for r in flagged), unapprovedCandidateDiagnosticOnly=True,
                  physicalAcceptance=False, terrainValidatorPassed=False, installationApproved=False, publication=False,
                  qualification='The unchanged check-neighbours.mjs before/after source-form guard covers every full-parent obligation and every required native source record. All raw failures remain. Changed native actors require full original mesh/support checks; this cannot approve the unvalidated coordinated terrain or install models.')
    save(out / 'summary.json', result)
    assert reservations.owns(lease)
    module('pair_full_form_regression_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'full-parent-current-basic-form-before-after-regression-diagnostic', list(dict.fromkeys(refs)), result)
    print(dict(forms=len(forms), ordinaryFlagged=result['ordinaryFlagged'], flagged=len(flagged)), flush=True)


if __name__ == '__main__':
    if '--owned' in sys.argv: owned()
    elif CHUNK is not None:
        assert not LOCAL.exists() and not (BASE / BATCH).exists()
        scope, _, proposal, _, _, _, all_forms = inputs()
        assert 0 <= CHUNK < math.ceil(len(all_forms)/CHUNK_SIZE)
        ids = sorted(all_forms)[CHUNK*CHUNK_SIZE:(CHUNK+1)*CHUNK_SIZE]
        keys = {('building:' if uid.startswith('landsd/') else 'source-form:')+uid for uid in ids}
        keys |= {'building:'+u for u in UIDS} | {'terrain:'+proposal['replacedParent']['url'], 'immutable-source-proof:'+BATCH}
        assert len(keys) <= 1000
        claim = reservations.claim('pair-full-parent-form-chunk-' + str(uuid.uuid4()), sorted(keys), batch=BATCH, ttl=3600)
        assert claim['ok'], 'Exact finite chunk source scope unavailable'
        execute_reserved(claim['reservation'], LOCAL / 'reservation.json', [sys.executable, __file__, '--owned', '--chunk', str(CHUNK)])
    else:
        assert not LOCAL.exists() and not (BASE / BATCH).exists()
        scope, _, proposal, _, _, _, forms = inputs()
        completed = []; flagged = []; checked = []
        for chunk in range(math.ceil(len(forms)/CHUNK_SIZE)):
            child = PREFIX + '-chunk-' + str(chunk).zfill(3)
            subprocess.run([sys.executable, __file__, '--chunk', str(chunk)], cwd=ROOT, check=True)
            result, _ = authenticate(BASE / child)
            assert result['fullScopeJobId'] == scope['jobId'] and result['chunk'] == chunk
            completed.append(dict(batch=child, jobId=result['jobId']))
            flagged.extend(result['flagged']); checked.extend(result['checkedSourceUids'])
            save(LOCAL / 'progress.json', dict(completed=completed, checked=len(checked), total=len(forms), installationApproved=False))
            print(dict(chunk=chunk, checked=len(checked), total=len(forms)), flush=True)
        assert len(checked) == len(set(checked)) == len(forms) and set(checked) == set(forms)
        result = dict(uids=UIDS, finiteChunks=completed, exactFullSourceCoverage=True, forms=len(forms), flagged=flagged,
                      ordinaryFlagged=sum(not r['existingNative'] for r in flagged), requiredFullNativeRegressions=len(scope['affectedNativeUids']),
                      canonicalResourceLimitUnchanged=1000, canonicalNonLandsDSourceKeysUsed=True,
                      installationApproved=False, physicalAcceptance=False, publication=False,
                      qualification='All full-parent obligations checked exactly once through the unchanged before/after form guard, in finite900-form chunks under canonical leases. Chunking does not reduce the full5403-form/1228-native scope or grant terrain/native/installation acceptance.')
        save(BASE / BATCH / 'summary.json', result)
        refs = [Path(__file__), BASE / SCOPE / 'result.json', BASE / CANDIDATE / 'result.json'] + [BASE / row['batch'] / 'result.json' for row in completed]
        module('pair_all_form_chunks_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
            BATCH, 'complete-finite-canonical-chunked-parent-form-regression', refs, result)
        print(dict(complete=True, forms=len(forms), ordinaryFlagged=result['ordinaryFlagged']), flush=True)
