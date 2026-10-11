"""Check one verified closure source against unchanged currently rendered terrain.

Reuses the full current-ground checker without modifying its frozen 22-source
scope. The additional source is explicitly scoped by a complete, hash-verified
Neon closure-input job. No terrain/model edits, review changes or publication.
"""
import argparse
import importlib.util
import json
import subprocess
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations, connect


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verified_base(base, uid):
    result = read(base / 'result.json')
    sync = read(base / 'neon-sync.json')
    assert sync['resultVerified'] and sync['jobId'] == result['jobId']
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                           (result['jobId'],)).fetchone() == ('complete', result)
    for ref in result['evidenceRefs']:
        assert digest((ROOT / ref['path']).read_bytes()) == ref['sha256']
    assert uid in result['identityQualifiedUids'], 'Complete positive identity required'
    row = next(r for r in read(base / 'check-selection.json.gz')['rows'] if r['uid'] == uid)
    assert row['currentReview'] is None
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--uid', required=True)
    p.add_argument('--base', required=True)
    p.add_argument('--batch', required=True)
    p.add_argument('--owned', action='store_true')
    a = p.parse_args()
    base = (ROOT / a.base).resolve()
    assert base.is_relative_to(ROOT / 'docs/astra-city/government-import')
    assert Path(a.batch).name == a.batch and a.batch.startswith('government-xl-')
    proof = verified_base(base, a.uid)
    doc = ROOT / 'docs/astra-city/government-import' / a.batch
    local = HERE / 'local' / a.batch
    if not a.owned:
        assert not doc.exists(), 'Fresh evidence only'
        claim = reservations.claim('codex-xl-closure-current-ground-' + str(uuid.uuid4()),
                                   ['building:' + a.uid], batch=a.batch)
        assert claim['ok'], claim
        save(local / 'reservation.json', json.loads(json.dumps(claim['reservation'], default=str)))
        subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'),
                        'run', '--lease-file', str(local / 'reservation.json'), '--',
                        sys.executable, __file__, *sys.argv[1:], '--owned'], cwd=ROOT, check=True)
        return
    from publication_lock import locked_publication
    with locked_publication(ROOT):
        save(doc / 'closure-ground-routing.json', {
            'uid': a.uid, 'verifiedBaseJobId': proof['jobId'],
            'baseEvidenceRefs': proof['evidenceRefs'],
            'runner': {'path': str(Path(__file__).relative_to(ROOT)),
                       'sha256': digest(Path(__file__).read_bytes())},
            'terrainGeometryChanges': 0, 'modelGeometryChanges': 0, 'publication': False})
        checker = load('closure_current_ground_checker', 'xl-positive-current-ground-preflight.py')
        checker.BASES = [base]
        checker.SCOPED_UIDS = frozenset([a.uid])
        original_loader = checker.module
        def scoped_loader(name, filename):
            module = original_loader(name, filename)
            if filename == 'xl-current-ground-result.py':
                module.SCOPED_UIDS = frozenset([a.uid])
            return module
        checker.module = scoped_loader
        checker.owned(a, doc, local)


if __name__ == '__main__':
    main()
