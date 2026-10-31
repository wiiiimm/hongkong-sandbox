"""Inspect unchanged original support layers for three provisional XL sources.

Historical manifest/snapshot changes are explicit; all other old evidence must
still match. Current source and installed support bytes/poses are verified.
This diagnostic never changes reviews or grants installation credit.
"""
import importlib.util
import sys
from pathlib import Path
from run import ROOT, HERE, read, digest, connect
from provisional_original_review import verify

PREVIOUS = ROOT / 'docs/astra-city/government-import/government-xl-five-provisional-installed-supports-20261007'
UIDS = frozenset({'landsd/204143:0', 'landsd/204145:0', 'landsd/79318:0'})
ALLOWED_HISTORY = frozenset({'3d-viewer/city/data/manifest.json',
                           'docs/astra-city/model-integration-20260909/current-source-review.json'})

def inputs(paths):
    assert paths == [PREVIOUS]
    prior = read(PREVIOUS / 'result.json')
    assert read(PREVIOUS / 'neon-sync.json') == {'jobId': prior['jobId'], 'resultVerified': True}
    historical = []
    for evidence in prior['evidenceRefs']:
        current = digest((ROOT / evidence['path']).read_bytes())
        if current != evidence['sha256']:
            assert evidence['path'] in ALLOWED_HISTORY, evidence['path']
            historical.append({**evidence, 'currentSHA256': current})
    original = read(PREVIOUS / 'support-inputs.json')
    pairs = [p for p in original['pairs'] if p['uid'] in UIDS]
    assert {p['uid'] for p in pairs} == UIDS
    wanted = set(UIDS) | {p['supportUid'] for p in pairs}
    sources = {r['uid']: r for r in original['sources'] if r['uid'] in wanted}
    assert set(sources) == wanted
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    pointer_path = ROOT / 'docs/astra-city/model-integration-20260909/current-source-review.json'
    manifest = read(manifest_path)
    pointer = read(pointer_path)
    entries = {r['uid']: (r, ROOT / '3d-viewer' / u, c['rootTranslation'])
               for u in manifest['officialModelCatalogues']
               for c in [read(ROOT / '3d-viewer' / u)] for r in c['models'] if r['uid'] in wanted}
    assert not UIDS.intersection(entries)
    refs = []
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (prior['jobId'],)).fetchone() == ('complete', prior)
        for uid, row in sources.items():
            assert digest((ROOT / row['candidate']['path']).read_bytes()) == row['sourceSHA256']
            assert digest((ROOT / '3d-viewer' / row['source']['tile']).read_bytes()) == row['source']['tileSHA256']
            if uid in UIDS:
                verify(con, uid, row['sourceSHA256'], row['currentReview'])
            else:
                entry, catalogue, translation = entries[uid]
                expected = row['candidate']['entry']
                assert translation == expected['rootTranslation'] == [-834500, 0, 816500]
                for key in ['uid', 'objectId', 'buildingCSUID', 'sha256', 'worldBounds']:
                    assert entry[key] == expected[key], key
                assert entry.get('verticalPlacementOffsetHKPD', 0) == expected.get('verticalPlacementOffsetHKPD', 0) == 0
                assert con.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s', (pointer['snapshotId'], uid)).fetchone() == ('installed-verified', row['sourceSHA256'])
                asset = catalogue.parent / entry['asset']
                assert digest(asset.read_bytes()) == row['sourceSHA256']
                refs.extend(ref(p) for p in [catalogue, asset])
    refs.extend(ref(p) for p in [manifest_path, pointer_path, PREVIOUS / 'result.json',
                               PREVIOUS / 'support-inputs.json', PREVIOUS / 'support-checks.json.gz',
                               Path(__file__), HERE / 'xl-original-support-layer-json-diagnostic.py',
                               HERE / 'provisional_original_review.py'])
    return {'sources': list(sources.values()),
            'pairs': [{**p, 'previousChecks': str((PREVIOUS / 'support-checks.json.gz').relative_to(ROOT))} for p in pairs],
            'previousEvidenceRefs': refs, 'historicalContextChanges': historical,
            'publication': False, 'modelGeometryChanges': 0}

def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}

if __name__ == '__main__':
    spec = importlib.util.spec_from_file_location('original_layer_runner', HERE / 'xl-original-support-layer-json-diagnostic.py')
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    runner.inputs = inputs
    runner.__file__ = __file__
    runner.main()
