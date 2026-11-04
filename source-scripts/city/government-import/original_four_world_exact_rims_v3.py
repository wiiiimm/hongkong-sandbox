"""Check ordinary complete-source clearance and regenerated strict rims in four worlds.

Changed XZ requires fresh exact whole-source coverage and clearance for that stream.
Unused vertices and missing continuous minima still stop this adapter.
"""
import argparse
from fractions import Fraction
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_wall_rim_accounting_20261009 import original_samples


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for k in ['batch', 'runtime', 'attributes', 'continuous', 'uid']:
        p.add_argument('--' + k, required=True)
    p.add_argument('--coverage', required=True)
    a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc = base / a.batch
    assert not doc.exists()
    refs, cached = [Path(__file__)], {}
    refs.extend(HERE / name for name in [
        'original_four_world_exact_rims_v1.py',
        'original_four_world_exact_rims_v2.py',
        'exact_original_face_conservative_clearance_v4_20261010.py',
        'exact_original_paired_finite_clearance_v2_20261010.py',
        'exact_original_paired_finite_clearance_20261010.py',
        'exact_original_triangle_pair_column_gap_20261010.py',
        'exact_original_closed_projection_intersection_20261010.py',
        'exact_original_projection_coverage_20261009.py',
        'exact_original_projection_coverage_v2_20261010.py'])

    def take(batch, path):
        if batch not in cached:
            cached[batch] = authenticate(base / batch)[1]
            refs.append(base / batch / 'result.json')
        assert digest(path.read_bytes()) == cached[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    r = next(r for r in take(a.runtime, base / a.runtime / 'selection.json.gz')['rows'] if r['uid'] == a.uid)
    g = next(r for r in take(a.runtime, HERE / 'local' / a.runtime / 'runtime-geometry.json.gz')['rows'] if r['uid'] == a.uid)
    attr = next(r for r in take(a.attributes, base / a.attributes / 'attributes.json.gz')['rows'] if r['uid'] == a.uid)
    ctx = take(a.continuous, base / a.continuous / (a.uid.split('/')[1] + '.json.gz'))
    assert not ctx['continuousAffectedFaces']
    exact = take(a.coverage, base / a.coverage / (a.uid.split('/')[1] + '.json.gz'))
    assert exact['uid'] == a.uid and exact['sourceBinding'] == ctx['sourceBinding']
    assert exact['sourceSHA256'] == ctx['sourceSHA256'] == r['sourceSHA256']
    unresolved = {c['sourceFace'] for c in ctx['faces'] if not c['groundProjectionCovered']}
    assert ctx['wholeSourceUncoveredFaces'] == exact['rawFloatingUncovered'] == exact['exactCovered'] == len(unresolved)
    assert not exact['stillUncoveredFaces'] and {q['sourceFace'] for q in exact['proofs']} == unresolved
    asset = ROOT / r['candidate']['path']
    assert digest(asset.read_bytes()) == r['sourceSHA256'] == g['sourceSHA256'] == attr['sourceSHA256']
    refs.append(asset)
    ix = np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)
    literal = np.asarray(attr['completeLiteralWorldPosition']).reshape(-1, 3)
    assert len(set(ix.ravel())) == len(literal), 'Unused source vertices require their own original transform capture'
    original_tri = decode_original_world_triangles(asset.read_bytes())
    original = literal.copy()
    original[ix.reshape(-1)] = original_tri.reshape(-1, 3)
    assert np.array_equal(original[ix], original_tri)
    lt = literal[ix]
    assert digest(lt.tobytes()) == ctx['sourceBinding']['decodedWorldTrianglesSHA256']
    ground = np.asarray(g['drawnGroundGeometry']).reshape(-1, 3, 3)
    polygons = shapely.polygons(ground[:, :, [0, 2]])
    valid = shapely.area(polygons) > 1e-10
    ground, polygons = ground[valid], polygons[valid]
    tree = shapely.STRtree(polygons)
    assert digest(ground.tobytes()) == ctx['sourceBinding']['drawnGroundSHA256']
    residual_minima = np.array([c['minimum']['minimumGapM'] for c in ctx['faces']])
    boxes_low, boxes_high = ground[:, :, [0, 2]].min(1), ground[:, :, [0, 2]].max(1)
    exact_bounds = []
    for proof in exact['proofs']:
        i = proof['sourceFace']
        assert proof['exactProjectionCovered'] and proof['noToleranceOrBufferCredit']
        assert proof['completeGroundSHA256'] == digest(ground.tobytes())
        assert proof['sourceFaceSHA256'] == digest(lt[i].tobytes())
        assert proof['completeOriginalGroundTrianglesAccounted'] == len(ground)
        low, high = lt[i, :, [0, 2]].min(1), lt[i, :, [0, 2]].max(1)
        mask = (boxes_low[:, 0] <= high[0]) & (boxes_high[:, 0] >= low[0]) & (boxes_low[:, 1] <= high[1]) & (boxes_high[:, 1] >= low[1])
        assert mask.any()
        # Every intersecting ground triangle is included by the closed AABB.
        # Affine heights on either complete triangle stay within its vertex
        # heights. Downward rounding gives a conservative clearance bound.
        source_min, ground_max = float(lt[i, :, 1].min()), float(ground[mask, :, 1].max())
        bound = float(np.nextafter(source_min - ground_max, -np.inf))
        assert np.isfinite(bound)
        raw_bound, refinement = bound, None
        if bound < -.5:
            # A complete-triangle AABB bound can be too coarse. Reuse the
            # existing exact closed-projection and finite-column certificates,
            # without changing the -.5m requirement or omitting any facet.
            from exact_original_face_conservative_clearance_v4_20261010 import verify as clipped_verify
            refinement = clipped_verify(lt[i], ground)
            if not refinement['existingOrdinaryClearanceBoundProved']:
                from exact_original_paired_finite_clearance_v2_20261010 import verify as finite_verify
                clipped = refinement
                refinement = finite_verify(lt[i], ground)
                refinement['priorClippedConservativeProofVerbatim'] = clipped
            assert refinement['existingOrdinaryClearanceBoundProved']
            assert refinement['sourceFaceSHA256'] == digest(lt[i].tobytes())
            assert refinement['completeCurrentGroundSHA256'] == digest(ground.tobytes())
            exact_bound = Fraction(refinement['exactCertifiedLowerClearanceM'])
            assert exact_bound >= Fraction(-1,2)
            bound = float(np.nextafter(float(exact_bound), -np.inf))
        assert bound >= -.5
        residual_minima[i] = bound
        exact_bounds.append(dict(sourceFace=i, sourceMinimumHeight=source_min, candidateGroundMaximumHeight=ground_max, rawAABBClearanceM=raw_bound, conservativeClearanceM=bound, groundCandidates=int(mask.sum()), exactRefinement=refinement))
    sampler = module('four_strict_rim_sampler', HERE / 'xl-final-script-pass.py')
    worlds = dict(original=original, literal=literal,
                  leftF32=np.asarray(attr['completeExplicitLeftAssociatedFloat32WorldPosition']).reshape(-1, 3),
                  balancedF32=np.asarray(attr['completeExplicitBalancedFloat32WorldPosition']).reshape(-1, 3))
    rows = []
    for mode, vertices in worlds.items():
        tri = vertices[ix]
        # Positive, close binary heights satisfy Sterbenz exact subtraction.
        assert np.all(tri[:, :, 1] > .5 * lt[:, :, 1]) and np.all(tri[:, :, 1] < 2 * lt[:, :, 1])
        delta = np.abs(tri[:, :, 1] - lt[:, :, 1]).max(1)
        mode_proof = None
        if np.array_equal(tri[:, :, [0, 2]], lt[:, :, [0, 2]]):
            lower = np.nextafter(residual_minima - delta, -np.inf)
        else:
            # No literal-XZ certificate transfers. Re-prove every actual
            # transformed facet against the identical complete drawn ground.
            from exact_original_projection_coverage_v2_20261010 import exact_coverage
            from exact_original_face_conservative_clearance_v4_20261010 import verify as clipped_verify
            from exact_original_paired_finite_clearance_v2_20261010 import verify as finite_verify
            proofs, bounds = [], []
            for i, face in enumerate(tri):
                coverage = exact_coverage(face, ground)
                assert coverage['exactProjectionCovered'] and coverage['noToleranceOrBufferCredit'], (mode, i, coverage)
                assert coverage['sourceFaceSHA256'] == digest(face.tobytes())
                assert coverage['completeGroundSHA256'] == digest(ground.tobytes())
                assert coverage['completeOriginalGroundTrianglesAccounted'] == len(ground)
                xz = face[:, [0,2]]; low, high = xz.min(0), xz.max(0)
                mask = np.all(boxes_low <= high,axis=1) & np.all(boxes_high >= low,axis=1)
                assert mask.any()
                bound = float(np.nextafter(float(face[:,1].min())-float(ground[mask,:,1].max()),-np.inf))
                raw_bound, refinement = bound, None
                if bound < -.5:
                    refinement = clipped_verify(face,ground)
                    if not refinement['existingOrdinaryClearanceBoundProved']:
                        clipped = refinement; refinement = finite_verify(face,ground)
                        refinement['priorClippedConservativeProofVerbatim'] = clipped
                    assert refinement['existingOrdinaryClearanceBoundProved']
                    assert refinement['sourceFaceSHA256'] == digest(face.tobytes())
                    assert refinement['completeCurrentGroundSHA256'] == digest(ground.tobytes())
                    exact_bound = Fraction(refinement['exactCertifiedLowerClearanceM'])
                    assert exact_bound >= Fraction(-1,2)
                    bound = float(np.nextafter(float(exact_bound),-np.inf))
                assert np.isfinite(bound) and bound >= -.5, (mode,i,bound)
                bounds.append(bound)
                proofs.append(dict(sourceFace=i,coverage=coverage,rawAABBClearanceM=raw_bound,conservativeClearanceM=bound,exactRefinement=refinement))
                if (i+1)%1000 == 0: print(dict(mode=mode,exactFacetsChecked=i+1,total=len(tri)),flush=True)
            lower = np.asarray(bounds)
            proofpath = doc / (mode+'-whole-source-exact.json.gz')
            save(proofpath,dict(mode=mode,sourceWorldSHA256=digest(tri.tobytes()),completeCurrentGroundSHA256=digest(ground.tobytes()),completeSourceFaces=len(tri),proofs=proofs))
            refs.append(proofpath)
            mode_proof = dict(path=str(proofpath.relative_to(ROOT)),sha256=digest(proofpath.read_bytes()))
        assert lower.min() >= -.5, 'New continuous source clearance failure'
        bottom = float(vertices[:, 1].min())
        samples = original_samples(vertices, ix, bottom)
        assert all(s['originalIncidentFaces'] for s in samples)
        points = np.asarray([s['point'] for s in samples])
        heights = sampler.s.context.shared.samples(points[:, [0, 2]], ground, tree)
        assert np.isfinite(heights).all()
        gaps = points[:, 1] - heights
        low = points[:, 1] <= bottom + .35
        assert low.any() and gaps.min() >= -.5 and gaps[low].min() <= .1 and gaps[low].max() <= 1
        assert np.any((gaps[low] >= -.1) & (gaps[low] <= .1)), 'Missing strict grade anchor'
        item = dict(mode=mode, sourceWorldSHA256=digest(tri.tobytes()), completeSourceFaces=len(tri),
                    completeRuntimeSamples=len(samples), lowRimSamples=int(low.sum()),
                    minimumSampleGapM=float(gaps.min()), minimumRimGapM=float(gaps[low].min()),
                    maximumRimGapM=float(gaps[low].max()), maximumYDisplacementM=float(delta.max()),
                    continuousClearanceLowerBoundM=float(lower.min()), changedXZWholeSourceExactProof=mode_proof, passed=True)
        rows.append(item)
        print(item, flush=True)
    result = dict(uids=[a.uid], exactResidualCoverageBatch=a.coverage, rawUncoveredFacesRetained=sorted(unresolved), conservativeResidualClearance=exact_bounds, sourceSHA256=r['sourceSHA256'], rows=rows, installationApproved=False,
                  sourceGeometryChanges=0, newlyInstalled=0,
                  qualification='Every ordinary source face keeps continuous clearance via identical XZ/convex Y bounds or a fresh exact whole-source coverage/clearance certificate for the actual changed-XZ stream. All indexed original vertices and original sampling rules regenerated in each source representation; strict -.5m clearance, .1m minimum-contact and1m rim maximum unchanged. No exceptions, current-neighbour, identity or publication approval.')
    save(doc / 'summary.json', result)
    refs.extend(HERE / n for n in ['original_wall_rim_accounting_20261009.py',
                                  'exact_packed_world_geometry_20261009.py', 'xl-final-script-pass.py'])
    module('four_strict_rim_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        a.batch, 'complete-four-world-ordinary-clearance-and-strict-rims', refs, result)


if __name__ == '__main__':
    main()
