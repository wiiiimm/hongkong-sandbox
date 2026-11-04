"""Checkpoint completed immutable Museum source context; no acceptance credit."""
import importlib.util
from pathlib import Path

from run import ROOT, HERE, read, save, digest, connect

BASE = ROOT / 'docs/astra-city/government-import'
PACKET = BASE / 'government-xl-heritage165054-source-context-draft-v1-20261014'
OUTPUT = PACKET / 'source-context-output-v1'
DOC = BASE / 'government-xl-heritage165054-complete-source-context-receipt-v1-20261014'
RESULT_HASH = 'bda7fa03edd0ac926d563496f37c193bebc7ba57002be4e44e63691dde293372'


def check(ref):
    path = (ROOT / ref['path']).resolve()
    assert path.is_relative_to(ROOT.resolve())
    assert digest(path.read_bytes()) == ref['sha256'], ref['path']
    return path


def main():
    assert not DOC.exists()
    result_path = OUTPUT / 'result.json'
    assert digest(result_path.read_bytes()) == RESULT_HASH
    source = read(result_path)
    terminal = read(OUTPUT / 'terminal.json')
    supervisor = read(PACKET / 'ROOT-supervisor-terminal.json')
    assert supervisor['actualWorkerExitCode'] == 0 and supervisor['leaseReleased']
    assert terminal['complete'] and terminal['allInputHashesUnchanged']
    assert terminal['resultSHA256'] == RESULT_HASH
    assert source['complete'] and source['uid'] == 'landsd/165054:0'
    assert source['completeOriginalFaces'] == 15140
    assert source['farFaces'] == 462 and source['independentOverlapCounts'] == [1106, 2]
    assert source['geometryChanges'] == source['sourcePoseChanges'] == source['newlyInstalled'] == 0
    for field in ('identityAccepted', 'physicalAccepted', 'sourceRoleAccepted', 'currentAcceptance', 'installationApproved'):
        assert source[field] is False
    paths = [check({'path': p, 'sha256': h}) for p, h in source['allInputHashes'].items()]
    for ref in [source['completeArrayRef'], source['contextRef']] + source['actualExports']:
        paths.append(check(ref))
    assert len(source['actualExports']) == 3
    assert all(ref['dimensions'] == [3000, 1800] for ref in source['actualExports'])
    DOC.mkdir()
    save(DOC / 'ROOT-REVIEW.json', {
        'completedSourceResultSHA256': RESULT_HASH,
        'actualExportsInspected': [ref['path'] for ref in source['actualExports']],
        'coordinateConvention': 'X=E-834500; Z=816500-N; greater Z is south',
        'diagramLimitations': 'Isolated low-feature Y-axis labels are crowded; use complete XYZ data for metric conclusions.',
        'scope': 'Complete source coordinates and descriptive diagrams only. No legal ownership, whole-component engineering role, identity, placement or physical approval.',
        'historicalOverlapRecipe': 'Projected area >1e-10 reproduces historical diagnostic counts only; all 15140 original faces remain retained.',
        'nextStep': 'Current-bound typed identity account and whole-source finite collision checks against both independent actors, followed by all remaining placement/runtime/browser/publication gates.',
        'newlyInstalled': 0,
    })
    paths += [p for p in PACKET.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    paths.append(Path(__file__))
    spec = importlib.util.spec_from_file_location('heritage_complete_source_freezer', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py')
    freezer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(freezer)
    receipt = freezer.freeze(DOC.name, 'heritage-complete-original-source-context-v1', paths, {
        'uids': ['landsd/165054:0'],
        'sourceSHA256': source['sourceSHA256'],
        'worldTrianglesSHA256': source['worldTrianglesSHA256'],
        'completeOriginalFaces': 15140,
        'completeArrayRef': source['completeArrayRef'],
        'contextRef': source['contextRef'],
        'retainedFarOriginalFaces': 462,
        'retainedIndependentOverlapCounts': [1106, 2],
        'independentActors': ['landsd/104467:0', 'landsd/57455:0'],
        'identityAccepted': False,
        'physicalAccepted': False,
        'currentAcceptance': False,
        'currentHeldReason': 'whole-source identity and independent-actor physical checks unfinished',
        'nextStep': 'Use saved complete coordinates for typed identity and full finite collision checks; preserve original geometry and poses.',
        'geometryChanges': 0,
        'sourcePoseChanges': 0,
    })
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (receipt['jobId'],)).fetchone() == ('complete', receipt)
    for ref in receipt['evidenceRefs']:
        check(ref)
    save(DOC / 'ROOT-VERIFIED.json', {
        'jobId': receipt['jobId'], 'exactNeonReadback': True,
        'allEvidenceHashesVerified': True, 'evidenceRefCount': len(receipt['evidenceRefs']),
        'newlyInstalled': 0, 'identityAccepted': False, 'physicalAccepted': False,
    })
    print({'jobId': receipt['jobId'], 'evidenceRefs': len(receipt['evidenceRefs']), 'newlyInstalled': 0})


if __name__ == '__main__':
    main()
