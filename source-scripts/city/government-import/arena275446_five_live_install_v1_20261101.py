"""Publish exact qualified originals, verify real HTTP, review exports, then credit.

Full byte rollback on failure. Does not write the unrelated legacy audit snapshot.
"""
import argparse
import functools
import hashlib
import http.server
import json
import os
import signal
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path
import arena275446_five_guarded_publish_v1_20261101 as guard
from safe_status_output_v1_20261031 import status as print
from run import ROOT, HERE, read, save, digest, connect, reservations, jobs, Jsonb, dict_row
from publication_lock import locked_publication
from installation_snapshot_identity_v1_20261031 import identity as snapshot_identity
from upton_staged_image_review_binding_v1_20261014 import inventory_delta
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs

stage = guard.stage
BASE, BATCH = stage.BASE, guard.BATCH
DOC, LOCAL = BASE / BATCH, HERE / 'local' / BATCH
LEASE = LOCAL / 'reservation.json'
PUB = HERE / 'arena275446_five_guarded_publish_v1_20261101.py'
BROWSER = HERE / 'sha_tin_live_atomic_browser_v2_20261101.mjs'
POINTER = ROOT / 'docs/astra-city/model-integration-20260909/current-source-review.json'
PREVIOUS = BASE / 'government-xl-palazzo76610-after-prosperous-twenty-original-installed-v1-20261101/full-xl-current-count.json'
MUTABLE = {'docs/astra-city/model-integration-20260909/current-source-review.json',
           '3d-viewer/city/data/building-progress.json',
           '3d-viewer/scripts/building-progress/review-proof.json',
           '3d-viewer/scripts/building-progress/screening-proof.json'}
PROTECTED = ['docs/astra-city/landmark-completion-audit/neon-snapshot.json',
             'docs/astra-city/government-import/government-xl-safe-boundary-recovery-sequence-20261006/working-commands.json',
             'docs/astra-city/government-import/government-xl-disneyland-piers-after-passenger-primary-imagery-v1-20261030/pier-lighting-design-photograph.jpg']


def check(binding):
    assert stage.ref(ROOT / binding['path']) == binding, binding['path']


def load():
    resources, q = guard.evidence()
    assert not DOC.exists(), 'Never repeat an installed or partially processed transaction'
    pointer = read(POINTER)
    previous = read(PREVIOUS)
    assert previous['counts'] == dict(total=521, installedVerified=413, remaining=108)
    models = read(stage.STAGE / 'catalogue.json')['models']
    delta = inventory_delta(previous, models, manifest_sha=q['currentManifest']['sha256'], snapshot=pointer['snapshotId'])
    assert delta['expectedFixedXLDelta'] == 1 and delta['returnedModels'] == 5
    result = read(stage.DOC / 'result.json')
    paths = [stage.DOC / 'result.json', Path(__file__), PUB, BROWSER,
             HERE / 'source_bound_basic_lifecycle_checks_v1_20261029.mjs', HERE/'arena275446_five_installation_contract_v1_20261101.py', ROOT/q['finalStageLifecycle']['path'],
             HERE / 'bounded_reserved_runner_v2_20261022.py',
             HERE.parent / 'shared-modelling/reservation_runner.py', PREVIOUS, POINTER]
    refs = distinct_refs(result['evidenceRefs'] + [stage.ref(p) for p in paths])
    for binding in refs:
        check(binding)
    return resources, q, pointer, models, delta, refs


def restore(saved):
    errors = []
    for relative, raw in sorted(saved.items(), key=lambda item: item[0] == '3d-viewer/city/data/manifest.json'):
        path = ROOT / relative
        try:
            if raw is None:
                path.unlink(missing_ok=True)
            else:
                tmp = path.with_name(path.name + '.elegant-rollback-' + uuid.uuid4().hex)
                tmp.write_bytes(raw)
                os.replace(tmp, path)
        except BaseException as error:
            errors.append(dict(path=relative, error=repr(error)))
    return errors


def verify_live(report, models):
    uids = {m['uid'] for m in models}
    assert report['passed'] and report['liveInstalledHTTP'] and not report['catalogueAndTerrainSubstitution']
    assert not report['pageErrors'] and len(report['cases']) == 6
    assert {(r['width'], r['failedUid']) for r in report['cases']} == {(1280, None)} | {(390, u) for u in uids}
    sources = {m['uid']: (m['sha256'], m['triangles']) for m in models}
    for row in report['cases']:
        assert {r['uid']: (r['sha256'], r['triangles']) for r in row['sources']} == sources
        assert all(r['active'] for r in row['sources'])
        assert row['baseOnlyRestoredCompleteGroup'] and row['completeGroupEvicted']
        assert row['capture']['fullyFramed'] and row['capture']['withinUnchangedInitialLoadRanges']
        assert not row['audit']['violations'] and row['audit']['frames'] > 0
        assert row['audit']['transitions'][-1]['active'] == []
        assert row['uiFreeCanvasExport']
        if row['failedUid']:
            assert row['failureKeptAllBasics']
    return True


def owned():
    with locked_publication(ROOT):
        resources, q, pointer, models, delta, refs = load()
        lease = read(LEASE)
        assert reservations.owns(lease) and resources <= set(lease['resources'])
        manifest = ROOT / '3d-viewer/city/data/manifest.json'
        before = read(manifest)
        old_models = [m for url in before['officialModelCatalogues'] for m in read(ROOT / '3d-viewer' / url)['models']]
        assert len(old_models) == len({m['uid'] for m in old_models}) == 7061
        protected = {path: digest((ROOT / path).read_bytes()) for path in PROTECTED}
        DOC.mkdir()

        def call(command, name, timeout=14400):
            assert reservations.owns(lease)
            with (DOC / (name + '.log')).open('w') as log:
                process = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                                         env={**os.environ, 'CHROME_PATH': '/opt/google/chrome/chrome'}, timeout=timeout)
            assert process.returncode == 0, name + ' failed; see saved log'
            assert reservations.owns(lease)

        command = [sys.executable, str(PUB), '--receipt', str(LEASE)]
        call(command, 'publisher-dry-run')
        pubdoc = ROOT / 'docs/astra-city/model-integration-20260909' / BATCH
        dry = read(pubdoc / 'publication-plan.json')
        assert not dry['published']
        plan = read(stage.STAGE / 'plan.json')
        destination = plan['areas'][0]['destination']
        assets = [(ROOT / '3d-viewer' / destination).parent / m['asset'] for m in models]
        mutable = set(dry['after']) | MUTABLE | {str(p.relative_to(ROOT)) for p in assets}
        assert not mutable & set(PROTECTED)
        saved = {r: (ROOT / r).read_bytes() if (ROOT / r).exists() else None for r in mutable}
        history = []
        for relative, raw in saved.items():
            if raw is not None:
                path = LOCAL / 'historical-current' / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)
                history.append(dict(originalPath=relative, originalSHA256=digest(raw), savedHistoricalBytes=stage.ref(path)))
        save(DOC / 'historical-input-context.json', dict(preInstallSnapshot=pointer['snapshotId'],
             mutableCurrentByteSnapshots=history, allMutableDestinations=sorted(mutable), originalEvidenceRefs=refs))
        acceptance = dict(transactionBatch=BATCH, uids=sorted(m['uid'] for m in models), sourceSHA256ByUid=q['sourceSHA256ByUid'],
                          sourceStage=stage.ref(stage.DOC / 'result.json'), ROOTStagedImageReview=stage.ref(stage.QUALIFICATION),
                          fixedXLDelta=delta, sourceGeometryChanges=0, sourcePoseChanges=0,
                          rawHeightConflictPreserved=True, publication=False, newlyInstalled=0)
        save(DOC / 'acceptance.json', acceptance)
        inventory = read(ROOT / pointer['inventory'])
        parts = {r['uid']: r for r in inventory['parts']}
        for model in models:
            old = parts.get(model['uid'], {})
            parts[model['uid']] = dict(uid=model['uid'], name=model.get('label') or model['uid'],
                landmarkIds=old.get('landmarkIds', []), objectId=model['objectId'], csuid=model['buildingCSUID'],
                candidate=dict(sha256=model['sha256']), sourceProgress='prepared-for-review',
                classification='script-verified-exact-original-functional-source', knownHold=False)
        ordered = sorted(parts.values(), key=lambda r: r['uid'])
        snapshot = snapshot_identity(ordered, acceptance, BATCH)
        assert snapshot != pointer['snapshotId'], 'New installation must have a distinct attempt snapshot'
        invpath = POINTER.parent / ('source-review-inventory-' + snapshot + '.json')
        assert not invpath.exists(), 'Never reseed a prior attempt snapshot'
        save(invpath, {**inventory, 'snapshotId': snapshot, 'derivedFrom': pointer['snapshotId'], 'parts': ordered,
                       'qualification': 'Exact unchanged original assembly with source-specific applicability, four-world physical roles and current atomic/publication evidence.'})
        sys.path.insert(0, str(HERE.parent / 'model-review-ledger'))
        import ledger
        ledger.seed(invpath, inherit=pointer['snapshotId'])
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        effort = dict(method='unknown', ai_model=None, reasoning_effort='unknown', issue='HKS-203',
                      run_id=snapshot, output_ref=stage.ref(DOC / 'acceptance.json')['path'])
        ledger.record_many(snapshot, LEASE, [(m['uid'], 'approved-for-integration', DOC / 'acceptance.json',
                           'Exact original qualification passed; live verification pending.', commit) for m in models],
                           effort=effort, request_id=BATCH + '-approved-' + snapshot)
        installed_history = False
        server = None
        server_log = None

        def interrupted(signum, frame):
            raise RuntimeError('Installation interrupted by lease supervisor')

        signal.signal(signal.SIGTERM, interrupted)
        try:
            for binding in refs:
                check(binding)
            call(command + ['--apply'], 'publisher-apply')
            for relative, sha in dry['after'].items():
                assert digest((ROOT / relative).read_bytes()) == sha
            after = read(manifest)
            all_models = [m for url in after['officialModelCatalogues'] for m in read(ROOT / '3d-viewer' / url)['models']]
            assert all_models == old_models + models and len(all_models) == 7066
            for path, model in zip(assets, models):
                assert digest(path.read_bytes()) == model['sha256']
            assert len(plan['topLevelTerrainPatches'])==1 and all('replaces'not in e for e in plan['topLevelTerrainPatches'])
            replaced = set()
            new_urls = {e['destination'] for e in plan['topLevelTerrainPatches']}
            assert [r for r in after['terrainPatches'] if r['url'] not in new_urls] == [r for r in before['terrainPatches'] if r['url'] not in replaced]
            assert len(after['terrainPatches']) == len(before['terrainPatches'])+1 and after['counts'] == before['counts']
            server_log = (DOC / 'private-server.log').open('w')

            class Handler(http.server.SimpleHTTPRequestHandler):
                def log_message(self, fmt, *args):
                    server_log.write((fmt % args) + '\n')
                    server_log.flush()

            server = http.server.ThreadingHTTPServer(('127.0.0.1', 4177), functools.partial(Handler, directory=str(ROOT / '3d-viewer')))
            threading.Thread(target=server.serve_forever, daemon=True).start()
            cfg = read(HERE / 'local' / (stage.P+'five-qualified-stage-lifecycle-v1-20261101') / 'config.json')
            cfg.update(liveInstalled=True, expectedPublicFiles=dry['after'], privateSourceBoundTileOverlays=[])
            cfgpath = LOCAL / 'live-http-config.json'
            save(cfgpath, cfg)
            call(['node', str(BROWSER), str(cfgpath.relative_to(ROOT)), str((DOC / 'live-http').relative_to(ROOT))], 'live-http-browser')
            reportpath = DOC / 'live-http/report.json'
            verify_live(read(reportpath), models)
            images = [stage.ref(DOC / 'live-http' / (r['name'] + '.png')) for r in read(reportpath)['cases']]
            save(DOC / 'live-image-review-required.json', dict(browserReport=stage.ref(reportpath), images=images,
                 expectedReview='ROOT-LIVE-EXPORT-OBSERVATIONS.json', installationApproved=False))
            print('LIVE_HTTP_COMPLETE:6cases passed. Waiting for ROOT inspection of the6bound UI-free exports; no installed credit yet.', flush=True)
            deadline = time.monotonic() + 3600
            reviewpath = DOC / 'ROOT-LIVE-EXPORT-OBSERVATIONS.json'
            while not reviewpath.exists():
                assert reservations.owns(lease) and time.monotonic() < deadline
                time.sleep(10)
            review = read(reviewpath)
            assert review['reviewer'] == 'Codex ROOT' and review['liveExportsAccepted'] is True
            assert review['browserReport'] == stage.ref(reportpath) and review['imagesActuallyInspected'] == images
            assert review['sourceGeometryChanges'] == 0
            verify_live(read(reportpath), models)
            for binding in images:
                check(binding)
            installed = {**acceptance, 'publication': True, 'newlyInstalled': 1, 'snapshotId': snapshot,
                         'installedUids': acceptance['uids'], 'manifest': stage.ref(manifest),
                         'liveBrowser': stage.ref(reportpath), 'ROOTLiveReview': stage.ref(reviewpath), 'completeCurrentCatalogueModels': 7066}
            save(DOC / 'installed-acceptance.json', installed)
            ledger.record_many(snapshot, LEASE, [(m['uid'], 'installed-verified', DOC / 'installed-acceptance.json',
                'Exact original source/support/atomic/publication guards and real HTTP desktop/mobile recovery checks passed; ROOT exports reviewed.', commit) for m in models],
                effort=effort, request_id=BATCH + '-installed-' + snapshot)
            installed_history = True
            assert read(POINTER) == pointer
            save(POINTER, {**pointer, 'snapshotId': snapshot, 'inventory': stage.ref(invpath)['path'],
                           'previousSnapshots': [*pointer.get('previousSnapshots', []), pointer['snapshotId']]})
            call([sys.executable, str(HERE.parent / 'building-progress/export.py'), '--refresh', '--snapshot-path',
                  str((DOC / 'progress/neon-snapshot.json').relative_to(ROOT))], 'progress-export')
            call(['node', str(ROOT / '3d-viewer/scripts/build_progress.mjs')], 'progress-build')
            call([sys.executable, str(HERE / 'xl-current-installed-count-audit.py'), '--previous', str(PREVIOUS.relative_to(ROOT)), '--batch', BATCH], 'fixed-xl-count')
            counts = read(DOC / 'full-xl-current-count.json')['counts']
            assert counts == dict(total=521, installedVerified=414, remaining=107)
            assert all(digest((ROOT / path).read_bytes()) == sha for path, sha in protected.items())
            finalrefs = distinct_refs([r for r in refs if r['path'] not in mutable] +
                [stage.ref(p) for folder in [DOC, LOCAL, pubdoc] for p in folder.rglob('*') if p.is_file() and p.name != 'reservation.json'] +
                [stage.ref(ROOT / p) for p in sorted(mutable) if (ROOT / p).exists()] + [stage.ref(invpath)])
            payload = dict(acceptance=stage.ref(DOC / 'installed-acceptance.json'), snapshot=snapshot)
            kind = 'exact-twenty-original-one-new-terrain-installed-v1'
            jid = jobs.enqueue(BATCH, kind, payload)
            job = jobs.claim(BATCH, lease['owner'], [kind], lease_seconds=1800)
            assert job and job['id'] == jid
            final = dict(**installed, jobId=jid, evidenceRefs=finalrefs, fullXLCurrentCounts=counts,
                         scriptExternalAICalls=0, aiGeometryModelling=False, protectedDirtyFilesUnchanged=protected)
            for binding in finalrefs:
                check(binding)
            with connect() as db:
                db.row_factory = dict_row
                db.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
                assert reservations._current(db, lease)
                assert db.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",
                    (Jsonb(final), jid, job['owner'], job['token'])).rowcount == 1
            with connect() as db:
                db.execute('SET TRANSACTION READ ONLY')
                assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (jid,)).fetchone() == ('complete', final)
                for uid, sha in q['sourceSHA256ByUid'].items():
                    assert db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s', (snapshot, uid)).fetchone() == ('installed-verified', sha)
            save(DOC / 'result.json', final)
            save(DOC / 'neon-sync.json', dict(jobId=jid, resultVerified=True, snapshotId=snapshot))
            print(dict(installedOriginals=5, installedFixedXL=1, counts=counts, jobId=jid), flush=True)
        except BaseException as error:
            errors = restore(saved)
            save(DOC / 'failure-recovery.json', dict(error=repr(error), allPublicDestinationsRestored=not errors,
                rollbackErrors=errors, derivedInstalledReviewHistoryRetained=installed_history,
                currentPointerRestoredNotDerivedCredit=True))
            raise
        finally:
            if server:
                server.shutdown()
                server.server_close()
            if server_log:
                server_log.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--install', action='store_true')
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    assert sum([args.prepare_only, args.install, args.owned]) == 1
    if args.prepare_only:
        resources, q, pointer, models, delta, refs = load()
        save(BASE / (BATCH + '-proposal') / 'installer-preflight.json', dict(passed=True, resources=sorted(resources),
             delta=delta, evidenceRefs=refs, caller=stage.ref(Path(__file__)), publication=False))
        print(dict(preflightPassed=True, delta=delta), flush=True)
        return
    if args.owned:
        return owned()
    resources, *_ = load()
    assert not LOCAL.exists()
    claim = reservations.claim('palazzo-twenty-original-install-' + str(uuid.uuid4()), sorted(resources | {'immutable-source-proof:' + BATCH}), batch=BATCH, ttl=3600)
    assert claim['ok']
    lease = claim['reservation']
    try:
        save(LEASE, json.loads(json.dumps(lease, default=str)))
        subprocess.run([sys.executable, str(HERE / 'bounded_reserved_runner_v2_20261022.py'), str(LEASE),
                        sys.executable, __file__, '--owned'], cwd=ROOT, check=True)
    finally:
        if reservations.owns(lease):
            assert reservations.release(lease)['ok']


if __name__ == '__main__':
    main()
