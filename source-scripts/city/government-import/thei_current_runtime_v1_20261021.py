"""Refresh original THEi tower/podium runtime measurements under a renewable lease."""
import json
import subprocess
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations, connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

UIDS = ['landsd/259613:0', 'landsd/259803:0']
BATCH = 'government-xl-thei-current-runtime-v1-20261021'
BASE = ROOT / 'docs/astra-city/government-import'
DOC = BASE / BATCH
LOCAL = HERE / 'local' / BATCH
SOURCE = BASE / 'government-xl-three-untried-podium-original-closures-20261008'

def owned():
    lease = read(LOCAL / 'reservation.json')
    assert reservations.owns(lease)
    receipt = read(SOURCE / 'result.json')
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (receipt['jobId'],)).fetchone() == ('complete', receipt)
    pins = {e['path']: e['sha256'] for e in receipt['evidenceRefs']}
    selection_path = SOURCE / 'support-inputs.json'
    assert digest(selection_path.read_bytes()) == pins[str(selection_path.relative_to(ROOT))]
    rows = [r for r in read(selection_path)['sources'] if r['uid'] in UIDS]
    assert len(rows) == 2
    sources = []
    for row in rows:
        source = ROOT / row['candidate']['path']
        assert digest(source.read_bytes()) == row['sourceSHA256']
        sources.append(source)
        tile = ROOT / '3d-viewer' / row['source']['tile']
        assert next(b for b in read(tile)['buildings'] if b['uid'] == row['uid']) == row['source']['building']
        row['source']['tileSHA256'] = digest(tile.read_bytes())
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    manifest_hash = digest(manifest.read_bytes())
    save(DOC / 'selection.json.gz', dict(rows=rows, manifestSHA256=manifest_hash))
    capture = HERE / 'acceptance-metrics-multi-retained.mjs'
    command = ['node', str(capture), '--selection', str((DOC / 'selection.json.gz').relative_to(ROOT)),
               '--candidates', str(source.parent.parent.relative_to(ROOT)),
               '--out', str((DOC / 'metrics.json').relative_to(ROOT)),
               '--geometry-out', str((LOCAL / 'runtime-geometry.json.gz').relative_to(ROOT))]
    save(DOC / 'command.json', command)
    with (DOC / 'worker.log').open('w') as log:
        subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
    report = read(DOC / 'metrics.json')
    assert len(report['rows']) == 2 and all(not r.get('error') for r in report['rows']), report['rows']
    refs = [Path(__file__), SOURCE / 'result.json', selection_path, *sources, capture,
            LOCAL / 'runtime-geometry.json.gz']
    for path, expected in report['inputHashes'].items():
        assert digest((ROOT / path).read_bytes()) == expected, path
        refs.append(ROOT / path)
    assert digest(manifest.read_bytes()) == manifest_hash and reservations.owns(lease)
    module('murray_runtime_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'original-current-runtime-measurement', refs,
        dict(uids=UIDS, currentManifestSHA256=manifest_hash, runtime=report['rows'], installationApproved=False,
             nextStep='Assess current tower and podium ground contacts against the saved assembly interface; retain all installation checks.'))
    print(json.dumps(report['rows']), flush=True)

def main():
    if '--owned' in sys.argv:
        return owned()
    assert not DOC.exists() and not LOCAL.exists()
    claim = reservations.claim(BATCH + '-' + str(uuid.uuid4()), ['building:' + uid for uid in UIDS], batch=BATCH, ttl=3600)
    assert claim['ok'], claim
    lease = claim['reservation']
    save(LOCAL / 'reservation.json', json.loads(json.dumps(lease, default=str)))
    try:
        subprocess.run([sys.executable, str(HERE / 'harbourfront_reserved_runner_v1_20261021.py'),
                        str(LOCAL / 'reservation.json'), sys.executable, __file__, '--owned'], cwd=ROOT, check=True)
    finally:
        if reservations.owns(lease):
            assert reservations.release(lease)['ok']

if __name__ == '__main__':
    main()
