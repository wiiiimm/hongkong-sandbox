"""Exact finite-column refinement of two inconclusive conservative caps.
Keeps prior source-only proofs; no native grounding or model acceptance.
"""
from pathlib import Path
from fractions import Fraction as F
import importlib.util
import json
import numpy as np
from run import ROOT, HERE, read, save, digest, connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_triangle_pair_column_gap_20261010 import verify

BASE = ROOT / 'docs/astra-city/government-import'
OLD = BASE / 'government-xl-parkview-next-three-original-cap-contacts-v1-20261011'
PROBE = BASE / 'government-xl-terrain-recovery-parkview-block11-complete-original-proposed-current-probe-v4-20261011'
BATCH = 'government-xl-parkview-next-three-exact-cap-refinement-v1-20261011'
DOC = BASE / BATCH


def ref(p):
    return dict(path=str(p.relative_to(ROOT)), sha256=digest(p.read_bytes()))


def main():
    assert not DOC.exists()
    helper_names = ['exact_packed_world_geometry_20261009.py',
        'exact_original_triangle_pair_column_gap_20261010.py',
        'exact_original_closed_projection_intersection_20261010.py',
        'exact_original_projection_coverage_v2_20261010.py']
    refs = [ref(p) for p in [Path(__file__), OLD / 'diagnostic.json.gz', OLD / 'result.json']]
    refs.extend(ref(HERE / n) for n in helper_names)
    previous = read(OLD / 'diagnostic.json.gz')
    receipt = read(OLD / 'result.json')
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
            (receipt['jobId'],)).fetchone() == ('complete', receipt)
    row = next(r for r in read(PROBE / 'selection.json.gz')['rows'] if r['uid'] == 'landsd/254491:0')
    source = ROOT / row['candidate']['path']
    assert digest(source.read_bytes()) == row['sourceSHA256']
    native = decode_original_world_triangles(source.read_bytes())
    runtime_path = HERE / 'local' / PROBE.name / 'runtime-geometry.json.gz'
    rt = next(r for r in read(runtime_path)['rows'] if r['uid'] == row['uid'])
    ground = np.asarray(rt['drawnGroundGeometry'], dtype='<f8').reshape(-1, 3, 3)
    assert digest(native.tobytes()) == previous['completeOriginalNativeWorldSHA256']
    assert digest(ground.tobytes()) == previous['completeFrozenGroundSHA256']
    rows = []
    for old in previous['rows']:
        prior = old['wholeOriginalCapAgainstFrozenGround']
        if F(prior['exactCertifiedLowerClearanceM']) > 0 and prior['groundProjectionCovered']:
            rows.append(dict(uid=old['uid'], cap=old['nativeOriginalCapFace'],
                existingStrictCapProofReused=True, priorProof=prior,
                wholeFiniteCapStrictClear=True, newPairProofs=[], noRootCredit=True))
            continue
        face = native[old['nativeOriginalCapFace']]
        gxz = ground[:, :, [0, 2]]
        fxz = face[:, [0, 2]]
        ids = np.flatnonzero(np.all(gxz.max(1) >= fxz.min(0), axis=1) &
            np.all(gxz.min(1) <= fxz.max(0), axis=1)).tolist()
        assert ids == prior['allProjectedBoundingCandidateOriginalGroundFacets']
        pieces = [dict(originalGroundFace=j, proof=verify(face, ground[j])) for j in ids]
        gaps = [F(p['proof']['exactMinimumFiniteColumnGapM']) for p in pieces
            if p['proof']['exactClosedHorizontalProjectionsMeet']]
        assert gaps
        low = min(gaps)
        covered = prior['completeOriginalProjectionCoverage']['exactProjectionCovered']
        out = dict(uid=old['uid'], cap=old['nativeOriginalCapFace'],
            existingStrictCapProofReused=False, priorConservativeProofRetained=prior,
            completeClosedAABBCandidateGroundIDs=ids, newPairProofs=pieces,
            exactCertifiedLowerClearanceM=str(low), completeProjectionCovered=covered,
            wholeFiniteCapStrictClear=covered and low > 0,
            sourceFacetSHA256=digest(face.tobytes()), noRootCredit=True)
        rows.append(out)
        print(json.dumps(dict(uid=old['uid'], cap=out['cap'], pairs=len(pieces),
            lower=str(low), covered=covered, strictClear=out['wholeFiniteCapStrictClear'])), flush=True)
    refs.extend(ref(p) for p in [PROBE / 'selection.json.gz', source, runtime_path])
    for r in refs:
        assert ref(ROOT / r['path']) == r
    save(DOC / 'diagnostic.json.gz', dict(uids=[r['uid'] for r in rows], rows=rows,
        completeOriginalNativeWorldSHA256=digest(native.tobytes()),
        completeFrozenGroundSHA256=digest(ground.tobytes()), evidenceRefs=refs,
        historicalGroundContextOnly=True, sourceOnly=True, nativeReacceptance=False,
        currentAcceptance=False, installationApproved=False, newlyInstalled=0,
        sourceGeometryChanges=0, terrainChanges=0))
    spec = importlib.util.spec_from_file_location('parkview_three_cap_refinement_freeze',
        HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py')
    recorder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(recorder)
    result = recorder.freeze(BATCH, 'exact-finite-column-refinement-two-conservative-caps-source-only-v1',
        [ROOT / r['path'] for r in {r['path']: r for r in refs}.values()],
        dict(uids=[r['uid'] for r in rows], sourceOnly=True,
            sourceGeometryChanges=0, terrainChanges=0, currentAcceptance=False,
            nativeReacceptance=False, installationApproved=False, newlyInstalled=0))
    print(json.dumps(dict(jobId=result['jobId'], newlyInstalled=0)), flush=True)


if __name__ == '__main__':
    main()
