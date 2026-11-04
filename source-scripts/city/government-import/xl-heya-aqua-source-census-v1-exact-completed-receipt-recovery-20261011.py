"""Recover only the exact already-complete Heya source receipt.

No math rerun, new job, database writes, helper edits or acceptance credit.
JSON representation is checked using the unchanged production serializer and
the exact original freezer envelope; every original source/code ref is strict.
"""
import json
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect, jobs

BATCH = 'government-xl-heya-aqua-184286-installed-podium-complete-source-census-v1-20261011'
STAGE = 'heya-complete-provider-source-components-interfaces-no-root-credit'
JOB = '912860aeed19e2cc6c7d3217ee08041db284428573c9b9e732fdf191b2a26aa0'
BASE = ROOT / 'docs/astra-city/government-import'
DOC = BASE / BATCH
INPUT = BASE / 'government-xl-georef-sparkle-heya-original-supports-20261008'
ARCHIVE = BASE / 'government-xl-heya-aqua-source-census-v1-freeze-serialization-failure-archive-20261011'
DIAGNOSTIC_SHA = 'c872981947387f4f12970c2b1f880d489134111df7b38fc04d7cb72b2d70c46f'

def main():
    assert not (DOC / 'result.json').exists() and not (DOC / 'neon-sync.json').exists()
    diagnostic_path = DOC / 'diagnostic.json.gz'
    assert digest(diagnostic_path.read_bytes()) == DIAGNOSTIC_SHA
    original_numerical_out = read(diagnostic_path)
    assert original_numerical_out['uids'] == ['landsd/184286:0', 'landsd/184285:0']
    assert not original_numerical_out['currentAcceptance'] and not original_numerical_out['installationApproved']
    archived = read(ARCHIVE / 'complete-neon-result-readback.json')
    assert archived['jobId'] == JOB and archived['status'] == 'complete'
    expected_paths = [HERE / 'xl-heya-aqua-184286-installed-podium-complete-source-census-v1-20261011.py',
        INPUT / 'support-inputs.json', INPUT / 'support-failure-surfaces.json.gz', INPUT / 'result.json',
        diagnostic_path, HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py']
    for name in ['exact_packed_world_geometry_20261009.py',
        'exact_original_shared_edge_component_census_v2_20261011.py',
        'test_exact_original_shared_edge_component_census_v2_20261011.py',
        'exact_original_body_boundary_group_census_v1_20261011.py',
        'test_exact_original_body_boundary_group_census_v1_20261011.py',
        'exact_original_finite_triangle_contacts_20261010.py',
        'test_exact_original_finite_triangle_contacts_20261010.py',
        'exact_original_component_contacts_20261009.py',
        'exact_original_shell_intersections_20261009.py', 'xl_source_stream_binding_20261009.py']:
        expected_paths.append(HERE / name)
    source_rows = read(INPUT / 'support-inputs.json')['sources']
    for uid in original_numerical_out['uids']:
        rows = [r for r in source_rows if r['uid'] == uid]
        assert len(rows) == 1
        expected_paths.append(ROOT / rows[0]['candidate']['path'])
    refs = [dict(path=str(p.relative_to(ROOT)), sha256=digest(p.read_bytes()))
        for p in sorted(set(expected_paths))]
    assert len(refs) == 18 and refs == archived['result']['evidenceRefs']
    payload = dict(uids=original_numerical_out['uids'], evidenceRefs=refs)
    original_freezer_result = {**payload, **original_numerical_out, 'jobId': JOB,
        'batch': BATCH, 'stage': STAGE, 'newlyInstalled': 0, 'publication': False,
        'modelGeometryChanges': 0, 'terrainGeometryChanges': 0, 'scriptExternalAICalls': 0,
        'aiGeometryModelling': False, 'installationApproved': False, 'permanentRejection': False}
    exact_saved_representation = json.loads(jobs.encode(original_freezer_result))
    assert exact_saved_representation == archived['result']
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
            (JOB,)).fetchone() == ('complete', exact_saved_representation)
    for ref in refs:
        assert digest((ROOT / ref['path']).read_bytes()) == ref['sha256']
    assert digest(diagnostic_path.read_bytes()) == DIAGNOSTIC_SHA
    save(DOC / 'result.json', exact_saved_representation)
    save(DOC / 'neon-sync.json', dict(jobId=JOB, resultVerified=True))
    save(ARCHIVE / 'exact-completed-receipt-recovery.json', dict(jobId=JOB,
        originalCompleteJobPreserved=True, exactProductionSerializerAndFreezerEnvelopeEqual=True,
        originalFileReferenceVersionsVerified=len(refs), numericalDiagnosticSHA256=DIAGNOSTIC_SHA,
        producer=dict(path=str(Path(__file__).relative_to(ROOT)), sha256=digest(Path(__file__).read_bytes())),
        resultSHA256=digest((DOC / 'result.json').read_bytes()), databaseWrites=0,
        newJobs=0, numericalReruns=0, helperChanges=0, currentAcceptance=False,
        installationApproved=False, newlyInstalled=0))
    print(json.dumps(dict(jobId=JOB, exactOriginalReceiptRecovered=True,
        originalReferenceVersions=len(refs), currentAcceptance=False)), flush=True)

if __name__ == '__main__':
    main()
