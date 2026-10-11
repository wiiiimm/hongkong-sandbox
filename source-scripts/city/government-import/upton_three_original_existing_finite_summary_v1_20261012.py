"""Summarise an existing completed diagnostic; no database or geometry work."""
import collections
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DOC = ROOT / 'docs/astra-city/government-import/government-xl-upton-three-original-complete-current-finite-ground-v5-20261012'
DIAGNOSTIC_SHA = '8d9ca62b3e9b59a404538573a3b09a30ea74a9be4e5c7b28bd015089a5209468'


def summary():
    path = DOC / 'diagnostic.json.gz'
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == DIAGNOSTIC_SHA
    diagnostic = json.loads(gzip.decompress(raw))
    assert diagnostic['completeFaces'] == 13704
    assert not diagnostic['physicalAccepted'] and not diagnostic['installationApproved']
    rows = []
    for actor in diagnostic['actors']:
        census = actor['originalBodyCensus']
        labels = {face: body for body, faces in enumerate(census['sharedEdgeConnectedComponents']) for face in faces}
        zeros = census['exactNonrenderingOriginalFaces']
        for mode, binding in actor['allFourStreamBindings'].items():
            # This producer indexes proofs by whole-world SHA, not tuple SHA.
            proof = actor['distinctCompleteFiniteProofs'][binding['wholeWorldSHA256']]
            assert binding['wholeGroundSHA256'] == actor['completeGroundSHA256']
            assert binding['proofTupleSHA256'] == hashlib.sha256((binding['wholeWorldSHA256'] + binding['wholeGroundSHA256']).encode()).hexdigest()
            records = proof['allWholeFacetProofs']
            assert [record['face'] for record in records] == list(range(binding['completeFaces']))
            failed = proof['ordinaryFailingFaces']
            assert failed == [record['face'] for record in records if not record['ordinaryFiniteProved']]
            uncovered = proof['coverageFailingFaces']
            assert uncovered == [record['face'] for record in records if not record['completeProjectionCovered']]
            rows.append(dict(uid=actor['uid'], mode=mode, completeFaces=len(records), genuineBodies=len(census['sharedEdgeConnectedComponents']), retainedZeroFaces=len(zeros), ordinaryFailures=len(failed), uncoveredFaces=len(uncovered), coveredOrdinaryFailures=len(set(failed) - set(uncovered)), failedPlaneClasses=dict(collections.Counter(actor['completeOriginalPlaneAttribution'][face]['exactPlaneClass'] for face in failed)), failedOriginalBodies={str(body): count for body, count in sorted(collections.Counter(labels.get(face) for face in failed).items(), key=lambda item: str(item[0]))}))
    assert len(rows) == 12
    return dict(existingDiagnostic=dict(path=str(path.relative_to(ROOT)), sha256=DIAGNOSTIC_SHA), existingCompletedJobId='7b2c30c7df3cca9f42d7d3e8cee90f98525d0939c49ad396d900a256d8f4f325', rows=rows, sourceCrossingsRetained=23, noNumericalRecheck=True, noDatabaseQueriesOrWrites=True, noSourceOrTerrainChanges=True, installationApproved=False, newlyInstalled=0)


if __name__ == '__main__':
    print(json.dumps(summary(), indent=2))
