"""Diagnostic runtime checks of twenty immutable originals on unchanged current terrain."""
import json
import subprocess
import sys
import uuid
from run import ROOT, HERE, read, save, digest, connect, reservations
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
SOURCE = BASE / 'government-xl-next-twenty-original-identity-v1-20261018'
BATCH = 'government-xl-next-three-current-terrain-v1-20261019'
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
    # Prior diagnostics contain historical mutable manifest/module references.
    # Authenticate only reused immutable selection/source inputs; the runtime
    # capture independently pins all current modules and terrain it consumes.
    recorded = {q['path']:q['sha256'] for q in receipt['evidenceRefs']}
    selection_path=SOURCE/'selection.json.gz'
    pins={str(selection_path.relative_to(ROOT)):recorded[str(selection_path.relative_to(ROOT))]}
    assert digest(selection_path.read_bytes())==pins[str(selection_path.relative_to(ROOT))]
    selection=read(selection_path)
    selection['historicalIdentityManifestSHA256']=selection['manifestSHA256']
    selection['manifestSHA256']=digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())
    uids={'landsd/64856:0','landsd/232240:0','landsd/233227:0'}
    selection['rows']=[r for r in selection['rows']if r['uid']in uids]
    assert len(selection['rows'])==3
    for row in selection['rows']:
        for path in [row['candidate']['path'],'3d-viewer/'+row['source']['tile']]:
            pins[path]=recorded[path]
            assert digest((ROOT/path).read_bytes())==pins[path],path
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        for row in selection['rows']:
            assert db.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s',(row['native']['cacheKey'],)).fetchone()==(row['native']['resultSha'],)
    refs = [__file__, SOURCE / 'result.json']
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
        BATCH, 'three-original-current-terrain-diagnostics', refs,
        dict(uids=[r['uid'] for r in selection['rows']], rows=report['rows'],
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
