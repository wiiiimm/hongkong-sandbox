"""Recover a diagnostic receipt after JSON tuple/list readback mismatch.

Read-only database access. Requires one completed, non-publishing diagnostic,
an exact JSON-canonical match to its saved summary, and every evidence hash.
Does not rerun a worker, grant acceptance, or change database state.
"""
import argparse
import json
from run import ROOT, connect, digest, read, save


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch', required=True)
    args = parser.parse_args()
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    folder = ROOT / 'docs/astra-city/government-import' / args.batch
    assert not (folder / 'result.json').exists()
    summary = json.loads(json.dumps(read(folder / 'summary.json')))
    with connect() as connection:
        connection.execute('SET TRANSACTION READ ONLY')
        rows = connection.execute(
            'SELECT id,status,result FROM astra_modelling.jobs WHERE batch=%s',
            (args.batch,)).fetchall()
    assert len(rows) == 1
    job_id, status, result = rows[0]
    assert status == 'complete' and result['jobId'] == job_id
    assert result['batch'] == args.batch
    for key, value in summary.items():
        assert result[key] == value, key
    for key in ['publication', 'installationApproved', 'physicalAcceptance',
                'permanentRejection', 'aiGeometryModelling']:
        assert result[key] is False, key
    for key in ['newlyInstalled', 'modelGeometryChanges', 'terrainGeometryChanges',
                'sourceGeometryChanges', 'scriptExternalAICalls']:
        assert result[key] == 0, key
    assert result['evidenceRefs']
    for reference in result['evidenceRefs']:
        path = (ROOT / reference['path']).resolve()
        assert path.is_relative_to(ROOT.resolve())
        assert digest(path.read_bytes()) == reference['sha256'], reference['path']
    save(folder / 'result.json', result)
    save(folder / 'neon-sync.json', dict(jobId=job_id, resultVerified=True,
         recovery='Completed diagnostic read back verbatim; JSON summary and all evidence hashes verified; database unchanged.'))
    print(dict(batch=args.batch, jobId=job_id, evidenceFiles=len(result['evidenceRefs']), databaseWrites=0))


if __name__ == '__main__':
    main()
