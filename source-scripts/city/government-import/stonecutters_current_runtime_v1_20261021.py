"""Refresh original Stonecutters runtime measurements under a renewable lease."""
import json
import subprocess
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

UID = 'landsd/127037:0'
BATCH = 'government-xl-stonecutters-current-runtime-v1-20261021'
BASE = ROOT / 'docs/astra-city/government-import'
DOC = BASE / BATCH
LOCAL = HERE / 'local' / BATCH
SOURCE = BASE / 'government-xl-next-twenty-current-terrain-v6-20261021'

def owned():
    lease = read(LOCAL / 'reservation.json')
    assert reservations.owns(lease)
    receipt, pins = authenticate(SOURCE)
    selection_path = SOURCE / 'selection.json.gz'
    assert digest(selection_path.read_bytes()) == pins[str(selection_path.relative_to(ROOT))]
    row = next(r for r in read(selection_path)['rows'] if r['uid'] == UID)
    source = ROOT / row['candidate']['path']
    assert digest(source.read_bytes()) == row['sourceSHA256']
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    manifest_hash = digest(manifest.read_bytes())
    save(DOC / 'selection.json.gz', dict(rows=[row], manifestSHA256=manifest_hash))
    capture = HERE / 'acceptance-metrics-multi-retained.mjs'
    command = ['node', str(capture), '--selection', str((DOC / 'selection.json.gz').relative_to(ROOT)),
               '--candidates', str(source.parent.parent.relative_to(ROOT)),
               '--out', str((DOC / 'metrics.json').relative_to(ROOT)),
               '--geometry-out', str((LOCAL / 'runtime-geometry.json.gz').relative_to(ROOT))]
    save(DOC / 'command.json', command)
    with (DOC / 'worker.log').open('w') as log:
        subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
    report = read(DOC / 'metrics.json')
    assert len(report['rows']) == 1 and not report['rows'][0].get('error'), report['rows']
    refs = [Path(__file__), SOURCE / 'result.json', selection_path, source, capture,
            LOCAL / 'runtime-geometry.json.gz']
    for path, expected in report['inputHashes'].items():
        assert digest((ROOT / path).read_bytes()) == expected, path
        refs.append(ROOT / path)
    assert digest(manifest.read_bytes()) == manifest_hash and reservations.owns(lease)
    module('stone_runtime_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'original-current-runtime-measurement', refs,
        dict(uids=[UID], currentManifestSHA256=manifest_hash, runtime=report['rows'][0],
             nextStep='Prepare bounded terrain repair from current ground evidence; retain identity and all installation checks.'))
    print(json.dumps(report['rows'][0]), flush=True)

def main():
    if '--owned' in sys.argv:
        return owned()
    assert not DOC.exists() and not LOCAL.exists()
    claim = reservations.claim(BATCH + '-' + str(uuid.uuid4()), ['building:' + UID], batch=BATCH, ttl=3600)
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
