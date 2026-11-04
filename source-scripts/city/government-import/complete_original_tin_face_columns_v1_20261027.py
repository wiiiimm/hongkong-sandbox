"""Complete finite column bounds for explicitly scoped original-TIN warning facets."""
import argparse
from fractions import Fraction
from pathlib import Path
import uuid
import numpy as np
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_triangle_pair_column_gap_20261010 import verify as pair_verify
from exact_original_projection_coverage_v2_20261010 import exact_coverage


def finite_face_context(face, ground):
    face, ground = np.asarray(face, float), np.asarray(ground, float)
    assert face.shape == (3,3) and ground.ndim == 3 and ground.shape[1:] == (3,3) and len(ground)
    assert np.isfinite(face).all() and np.isfinite(ground).all()
    xz = face[:,[0,2]]
    gxz = ground[:,:,[0,2]]
    ids = np.flatnonzero(np.all(gxz.max(1)>=xz.min(0), axis=1)&np.all(gxz.min(1)<=xz.max(0), axis=1))
    proofs, values = [], []
    for i in ids:
        proof = pair_verify(face, ground[i])
        if not proof['exactClosedHorizontalProjectionsMeet']:
            continue
        proofs.append(dict(groundFace=int(i), proof=proof))
        values.extend(Fraction(v['exactGapM']) for v in proof['allExactBasicFeasibleColumnVertices'])
    coverage = exact_coverage(face, ground)
    minimum, maximum = (min(values), max(values)) if values else (None, None)
    return dict(completeProjectionCoverage=coverage, exactMinimumAllFinitePairGapM=str(minimum) if minimum is not None else None,
                exactMaximumAllFinitePairGapM=str(maximum) if maximum is not None else None,
                completeCandidateGroundFacets=list(map(int, ids)), finitePairs=proofs,
                belowEveryOverlappingGroundFaceByMoreThanHalfMetre=bool(coverage['exactProjectionCovered'] and maximum is not None and maximum < Fraction(-1,2)),
                exposedSurfaceProved=False, physicalAcceptance=False,
                qualification='Every finite pair column extremum retained. A positive maximum may be under a different overlapping terrain layer; it is not exposure proof. Whole-below credit requires complete exact projection coverage and ALL pair extrema below the unchanged -0.5m threshold.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for k in ('batch','facets','runtime','terrain','uid'):
        p.add_argument('--'+k, required=True)
    a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base = ROOT/'docs/astra-city/government-import'
    out = base/a.batch
    assert not out.exists()
    refs = [Path(__file__), HERE/'exact_original_triangle_pair_column_gap_20261010.py', HERE/'exact_original_projection_coverage_v2_20261010.py', HERE/'exact_packed_world_geometry_20261009.py']
    pins, checked_inputs = {}, {}
    def take(name, path):
        if name not in pins:
            pins[name] = authenticate(base/name)[1]
            refs.append(base/name/'result.json')
        assert digest(path.read_bytes()) == pins[name][str(path.relative_to(ROOT))]
        refs.append(path)
        checked_inputs[path] = digest(path.read_bytes())
        return read(path)
    warning = take(a.facets, base/a.facets/'summary.json')
    assert warning['uids'] == [a.uid] and warning['exactPriorFoundationReproduced']
    source = next(r for r in take(a.runtime, base/a.runtime/'selection.json.gz')['rows'] if r['uid'] == a.uid)
    asset = ROOT/source['candidate']['path']
    assert digest(asset.read_bytes()) == source['sourceSHA256'] == warning['sourceSHA256']
    refs.append(asset)
    tri = decode_original_world_triangles(asset.read_bytes())
    ground = np.asarray(take(a.terrain, HERE/'local'/a.terrain/'original-terrain.json.gz')['triangles'], float)
    assert digest(tri.astype('<f8').tobytes()) == warning['sourceWorldSHA256']
    assert digest(ground.astype('<f8').tobytes()) == warning['originalTerrainSHA256']
    ids = [r['sourceFace'] for r in warning['rows']]
    assert len(ids) == len(set(ids)) > 0
    claim = reservations.claim(a.batch+'-'+str(uuid.uuid4()), ['building:'+a.uid, 'original-compute:'+a.batch], batch=a.batch, ttl=3600)
    assert claim['ok']
    lease, rows = claim['reservation'], []
    try:
        for i in ids:
            assert reservations.heartbeat(lease)['ok']
            proof = finite_face_context(tri[i], ground)
            path = out/(str(i)+'.json.gz')
            save(path, proof)
            rows.append(dict(sourceFace=i, exactMinimumGapM=proof['exactMinimumAllFinitePairGapM'], exactMaximumGapM=proof['exactMaximumAllFinitePairGapM'], completeProjectionCovered=proof['completeProjectionCoverage']['exactProjectionCovered'], belowEveryOverlappingGroundFaceByMoreThanHalfMetre=proof['belowEveryOverlappingGroundFaceByMoreThanHalfMetre'], proof=dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()))))
            refs.append(path)
            print(dict(face=i, wholeBelow=rows[-1]['belowEveryOverlappingGroundFaceByMoreThanHalfMetre'], maximum=rows[-1]['exactMaximumGapM']), flush=True)
    finally:
        if reservations.owns(lease):
            assert reservations.release(lease)['ok']
    for path, sha in checked_inputs.items():
        assert digest(path.read_bytes()) == sha
    assert digest(asset.read_bytes()) == source['sourceSHA256']
    result = dict(uids=[a.uid], sourceSHA256=source['sourceSHA256'], sourceWorldSHA256=warning['sourceWorldSHA256'], originalTerrainSHA256=warning['originalTerrainSHA256'], explicitScopedSourceFaces=ids, rows=rows, completeFiniteFaceChecks=len(rows), allScopedFacesWholeBelow=all(r['belowEveryOverlappingGroundFaceByMoreThanHalfMetre'] for r in rows), fourPointWarningRecordChanged=False, sourceGeometryChanges=0, terrainGeometryChanges=0, exposedSurfaceProved=False, physicalAcceptance=False, installationApproved=False, publication=False, qualification='Complete finite-column checks for the explicit original-TIN warning list only. All source/ground bytes and original warnings preserved. Does not cover unscoped facets or prove current renderer acceptance, exposure, architectural role or installation.')
    save(out/'summary.json', result)
    module('complete_original_tin_columns_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'complete-explicit-original-tin-warning-facet-column-bounds', refs, result)
    print(dict(faces=len(rows), wholeBelow=sum(r['belowEveryOverlappingGroundFaceByMoreThanHalfMetre'] for r in rows)), flush=True)


if __name__ == '__main__':
    main()
