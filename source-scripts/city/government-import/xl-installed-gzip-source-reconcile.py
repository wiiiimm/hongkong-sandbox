"""Reconcile an indexed hold with an installed identical GLB, gzip OS byte only.

The source and runtime compression hashes remain separate. No asset, review,
geometry, acceptance or inventory source binding is replaced.
"""
import gzip
import json
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect, jobs, reservations, Jsonb, dict_row, NATIVE_RUN
from publication_lock import locked_publication

sys.path.insert(0, str(HERE.parent / 'enhancement-screening'))
from shape_prepare import canonical_bytes

BATCH = 'government-xl-harrow-installed-gzip-source-reconciled-20261008'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
PRIOR = ROOT / 'docs/astra-city/government-import/government-xl-held-second-pass-dispositions-20261008'
UID = 'landsd/193532:0'

def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}

def main():
    assert not DOC.exists(), 'Fresh immutable source disposition required'
    audit = read(PRIOR / 'dispositions.json.gz')
    prior = read(PRIOR / 'result.json')
    row = next(r for r in audit['rows'] if r['uid'] == UID)
    assert not row['installed'] and row['reasons'] == ['different-original-source-already-published']
    claim = reservations.claim('codex-xl-gzip-reconcile-' + str(uuid.uuid4()),
        ['building:' + UID, 'native-model:' + row['sourceKey'], 'xl-disposition-inventory:' + NATIVE_RUN],
        ttl=3600, batch=BATCH)
    assert claim['ok'], claim
    lease = claim['reservation']
    try:
        with locked_publication(ROOT):
            pointerpath = ROOT / 'docs/astra-city/model-integration-20260909/current-source-review.json'
            manifestpath = ROOT / '3d-viewer/city/data/manifest.json'
            pointer = read(pointerpath)
            matches = [(model, ROOT / '3d-viewer' / url)
                for url in read(manifestpath)['officialModelCatalogues']
                for model in read(ROOT / '3d-viewer' / url)['models'] if model['uid'] == UID]
            assert len(matches) == 1
            model, catalogue = matches[0]
            asset = catalogue.parent / model['asset']
            raw = asset.read_bytes()
            assert digest(raw) == model['sha256'] != row['sourceSHA256']
            expected = canonical_bytes(raw, row['sourceSHA256'])
            changed = [i for i, (a, b) in enumerate(zip(raw, expected)) if a != b]
            assert len(raw) == len(expected) and changed == [9]
            assert {raw[9], expected[9]} == {3, 255}
            assert gzip.decompress(raw) == gzip.decompress(expected)
            native = row['evidence']['nativeModel']
            assert len(expected) == native['asset']['bytes']
            assert digest(expected) == native['asset']['sha256'] == row['sourceSHA256']
            for key in ('modelId', 'triangles', 'worldBounds'):
                assert model[key] == native[key]
            official = [v for v in native['matching']['officialCandidates']
                if v['objectId'] == model['objectId'] and v['buildingCSUID'] == model['buildingCSUID']]
            assert len(official) == 1
            assert read(catalogue)['rootTranslation'] == [-834500, 0, 816500]
            assert model.get('verticalPlacementOffsetHKPD', 0) == 0
            assert model['sourceIdentityReviewed'] and model['identityReviewApproved'] and model['placementReviewed']
            with connect() as con:
                con.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
                assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (prior['jobId'],)).fetchone() == ('complete', prior)
                actual = con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',
                    (NATIVE_RUN, row['sourceKey'].split('/')[0])).fetchone()
                assert actual == (row['evidence']['nativeResultSHA256'],)
                review = con.execute('SELECT review_state,source_sha256,result FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',
                    (pointer['snapshotId'], UID)).fetchone()
                assert review and review[:2] == ('installed-verified', model['sha256'])
            reviewproof = ref(ROOT / review[2]['evidence'])
            assert reviewproof['sha256'] == review[2]['sha256']
            evidence = [ref(PRIOR / 'dispositions.json.gz'), ref(PRIOR / 'result.json'), ref(pointerpath), ref(manifestpath),
                ref(catalogue), ref(asset), reviewproof, ref(Path(__file__).resolve()),
                ref(HERE.parent / 'enhancement-screening/shape_prepare.py')]
            payload = {'sourceKey': row['sourceKey'], 'sourceSHA256': row['sourceSHA256'], 'uid': UID,
                'evidenceRefs': evidence, 'priorDispositionJobId': row['jobId'], 'nativeRun': NATIVE_RUN}
            stage = 'indexed-original-installed-gzip-os-byte-equivalence-v1'
            jid = digest(jobs.encode([BATCH, stage, payload]).encode())
            result = {**payload, 'jobId': jid, 'batch': BATCH, 'stage': stage,
                'disposition': 'installed', 'humanStatus': 'installed', 'installed': True, 'reasons': [],
                'runtimeSourceSHA256': model['sha256'], 'uncompressedGLBSHA256': digest(gzip.decompress(raw)),
                'gzipDifferenceByteOffsets': changed, 'runtimeGzipOSByte': raw[9], 'indexedGzipOSByte': expected[9],
                'currentReview': {'state': review[0], 'sourceSHA256': review[1], 'result': review[2]},
                'snapshotId': pointer['snapshotId'], 'newlyInstalled': 0, 'existingInstallRecordsReconciled': 1,
                'newRuntimeAssetsInstalled': 0, 'modelGeometryChanges': 0, 'scriptExternalAICalls': 0,
                'publication': False, 'fullIndexedXLScope': 521,
                'fullXLCounts': {'installedVerified': 195, 'held': 326, 'open': 0, 'inProcess': 0},
                'qualification': 'The entire uncompressed original GLB is byte-identical to the current installed-verified source. Only gzip platform metadata differs. Retain both original compressed hashes and the existing accepted review; no new geometry, publication, physical waiver or installation credit.'}
            assert read(pointerpath) == pointer
            for item in evidence:
                assert ref(ROOT / item['path']) == item
            with connect() as con:
                con.row_factory = dict_row
                con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
                assert reservations._current(con, lease)
                con.execute("INSERT INTO astra_modelling.jobs(id,batch,stage,payload,status,result) VALUES(%s,%s,%s,%s,'complete',%s) ON CONFLICT(id) DO NOTHING",
                    (jid, BATCH, stage, Jsonb(payload), Jsonb(result)))
                assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (jid,)).fetchone() == {'status': 'complete', 'result': result}
            with connect() as con:
                assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (jid,)).fetchone() == ('complete', result)
            save(DOC / 'result.json', result)
            save(DOC / 'neon-sync.json', {'jobId': jid, 'freshReadbackVerified': True})
            print(json.dumps({'jobId': jid, 'uid': UID, 'fullXLCounts': result['fullXLCounts'], 'newlyInstalled': 0}), flush=True)
    finally:
        assert reservations.release(lease)

if __name__ == '__main__':
    main()
