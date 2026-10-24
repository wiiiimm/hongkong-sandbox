"""Diagnostic runtime checks of forty immutable originals on unchanged current terrain."""
import json
import subprocess
import sys
import uuid
from run import ROOT, HERE, read, save, digest, connect, reservations
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
SOURCE = BASE / 'government-xl-remaining-forty-podium-identity-v1-20261021'
BATCH = 'government-xl-remaining-forty-assembly-runtime-v1-20261021'
DOC = BASE / BATCH
LOCAL = HERE / 'local' / BATCH


def owned():
    lease = read(LOCAL / 'reservation.json')
    assert reservations.owns(lease)
    receipt = read(SOURCE / 'result.json')
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                          (receipt['jobId'],)).fetchone() == ('complete', receipt)
    pins = {}
    for ref in receipt['evidenceRefs']:
        assert ref['path'] not in pins or pins[ref['path']] == ref['sha256']
        pins[ref['path']] = ref['sha256']
    for path, sha in pins.items():
        assert digest((ROOT / path).read_bytes()) == sha, path
    selection = read(SOURCE / 'selection.json.gz')
    primary = BASE / 'government-xl-remaining-forty-original-identity-v2-20261021'
    from china_ferry_current_foundations_v1_20261020 import authenticate
    primary_receipt, primary_pins = authenticate(primary)
    for path in [primary/'selection.json.gz', primary/'summary.json']:
        assert digest(path.read_bytes()) == primary_pins[str(path.relative_to(ROOT))]
    primary_selection = read(primary/'selection.json.gz')
    assert primary_selection['manifestSHA256'] == selection['manifestSHA256']
    passed = {r['uid'] for r in read(primary/'summary.json')['rows'] if r['status']=='identity-passed'}
    selection['rows'] += [r for r in primary_selection['rows'] if r['uid'] in passed]
    assert len(selection['rows']) == 20 and len({r['uid'] for r in selection['rows']}) == 20
    unavailable = [r for r in selection['rows'] if not r.get('candidate')]
    assert [r['uid'] for r in unavailable] == ['landsd/203884:0']
    save(DOC/'unavailable-sources.json', dict(rows=unavailable, reason='source-cache-missing', installationApproved=False, permanentRejection=False))
    selection['rows'] = [r for r in selection['rows'] if r.get('candidate')]
    assert len(selection['rows']) == 19
    for path, sha in primary_pins.items():
        assert path not in pins or pins[path] == sha
        pins[path] = sha
    refs = [__file__, SOURCE / 'result.json', primary/'result.json']
    for row in selection['rows']:
        native = row['native']['model']
        building = row['source']['building']
        candidates = native['matching']['officialCandidates']
        matches = [c for c in candidates if c['objectId'] == building['objectId']
                   and c['buildingCSUID'] == building['buildingCSUID']]
        assert len(matches) == 1
        # A private diagnostic binding, never an identity/publication approval.
        entry = dict(matches[0], **native['asset'], uid=row['uid'],
                     modelId=row['modelId'], worldBounds=native['worldBounds'],
                     triangles=row['triangles'], rootTranslation=[-834500, 0, 816500],
                     recordedBaseHeight=building.get('baseHeightHKPD'),
                     recordedTopHeight=building.get('topHeightHKPD'),
                     placementReviewed=False, publicationApproved=False)
        raw = (ROOT / row['candidate']['path']).read_bytes()
        assert digest(raw) == row['sourceSHA256'] == entry['sha256']
        target = LOCAL / entry['asset']
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        row['candidate'] = dict(path=str(target.relative_to(ROOT)), entry=entry)
        refs.append(target)
    save(DOC / 'selection.json.gz', selection)
    command = ['node', str(HERE / 'acceptance-metrics-multi-retained.mjs'),
               '--selection', str((DOC / 'selection.json.gz').relative_to(ROOT)),
               '--candidates', str(LOCAL.relative_to(ROOT)),
               '--out', str((DOC / 'metrics.json').relative_to(ROOT)),
               '--geometry-out', str((LOCAL / 'runtime-geometry.json.gz').relative_to(ROOT))]
    with (DOC / 'worker.log').open('w') as log:
        subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
    report = read(DOC / 'metrics.json')
    assert len(report['rows']) == len(selection['rows'])
    for path, sha in {**pins, **report['inputHashes']}.items():
        assert digest((ROOT / path).read_bytes()) == sha, path
    assert reservations.owns(lease)
    from pathlib import Path
    refs = [Path(p) for p in refs] + [ROOT / p for p in pins]
    refs += [ROOT / p for p in report['inputHashes']]
    refs += [HERE / 'acceptance-metrics-multi-retained.mjs', LOCAL / 'runtime-geometry.json.gz']
    result = module('next_five_terrain_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'twenty-original-assembly-current-terrain-diagnostics', refs,
        dict(uids=[r['uid'] for r in selection['rows'] + unavailable], rows=report['rows'],
             unavailableUids=[r['uid'] for r in unavailable], requestedSources=20, checkedSources=19,
             fullAcceptance=False, installationApproved=False))
    print(result['jobId'], flush=True)


def main():
    if '--owned' in sys.argv:
        return owned()
    assert not DOC.exists()
    claim = reservations.claim(BATCH + '-' + str(uuid.uuid4()),
                               ['immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
    assert claim['ok'], claim
    lease = claim['reservation']
    save(LOCAL / 'reservation.json', json.loads(json.dumps(lease, default=str)))
    try:
        subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'),
                        'run', '--lease-file', str(LOCAL / 'reservation.json'), '--ttl', '3600',
                        '--', sys.executable, __file__, '--owned'], cwd=ROOT, check=True)
    finally:
        if reservations.owns(lease):
            assert reservations.release(lease)['ok']


if __name__ == '__main__':
    main()
