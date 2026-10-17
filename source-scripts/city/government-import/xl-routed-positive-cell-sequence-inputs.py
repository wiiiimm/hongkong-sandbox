"""Bind a verified fresh identity cohort to the existing serial full-check runner.

Identity positives are only processing inputs. All physical, runtime, browser,
publication and current installed-review checks are still required.
"""
import argparse
from pathlib import Path
from run import ROOT, read, save, digest, connect, NATIVE_RUN
from routed_original_cell_identity import POLICY


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--proof', required=True)
    p.add_argument('--base', required=True)
    p.add_argument('--batch', required=True)
    a = p.parse_args()
    assert Path(a.batch).name == a.batch and a.batch.startswith('government-xl-')
    base, proof = (ROOT / a.base).resolve(), (ROOT / a.proof).resolve()
    parent = ROOT / 'docs/astra-city/government-import'
    assert base.parent == proof.parent == parent
    doc = parent / a.batch
    assert not doc.exists()
    result = read(proof / 'result.json')
    assert read(proof / 'neon-sync.json') == {'jobId': result['jobId'], 'resultVerified': True}
    assert result['identityPolicy'] == POLICY
    assert not result['publication'] and result['newlyInstalled'] == 0
    assert result['modelGeometryChanges'] == result['scriptExternalAICalls'] == 0
    for evidence in result['evidenceRefs']:
        assert ref(ROOT / evidence['path']) == evidence
    selected = read(base / 'check-selection.json.gz')
    originals = {r['uid']: r for r in selected['rows']}
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selected['manifestSHA256']
    rows = []
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                           (result['jobId'],)).fetchone() == ('complete', result)
        for identity in result['rows']:
            if not identity['passed']:
                continue
            row = originals[identity['uid']]
            assert identity['sourceSHA256'] == row['sourceSHA256']
            assert not identity['installationApproved'] and row['currentReview'] is None
            assert not con.execute('SELECT 1 FROM astra_modelling.model_reviews WHERE uid=%s LIMIT 1',
                                   (row['uid'],)).fetchone()
            native = row['native']
            assert con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r '
                'JOIN astra_modelling.native_stage_members m USING(cache_key) '
                'WHERE m.run_id=%s AND r.cache_key=%s',
                (NATIVE_RUN, native['cacheKey'])).fetchone() == (native['resultSha'],)
            rows.append({'uid': row['uid'], 'name': row.get('name'),
                         'sourceSHA256': row['sourceSHA256'], 'base': a.base})
    assert rows
    refs = result['evidenceRefs'] + [ref(proof / 'result.json'), ref(proof / 'neon-sync.json'),
                                   ref(manifest), ref(Path(__file__))]
    save(doc / 'sequence-inputs.json', {'rows': rows, 'evidenceRefs': refs,
        'identityJobId': result['jobId'], 'newlyInstalled': 0, 'publication': False,
        'scriptExternalAICalls': 0, 'modelGeometryChanges': 0,
        'qualification': 'Explicit verified identity positives for the serial existing full-check sequence; inputs alone grant no installation credit.'})
    print({'positiveIdentitySources': len(rows), 'identityNeonVerified': True, 'newlyInstalled': 0}, flush=True)


if __name__ == '__main__':
    main()
