"""Revalidate the exact 35 reviewed landscape bases against current drawn ground.

Every other original face retains the unchanged foundation policy. No faces are
removed from assets/runtime, and this diagnostic never grants physical acceptance.
"""
import argparse
from fractions import Fraction
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from complete_original_tin_face_columns_v1_20261027 import finite_face_context

P = 'government-xl-west-kowloon-north-pair-after-ocean-'
BATCH = P + 'current-masked-foundation-v1-20261027'
UID = 'landsd/182397:0'
SHA = 'f16aa7f57a9b89962a6e1f3183e4dea922c7dbcb173515e608deae1ddc4b48b1'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lease', required=True)
    a = p.parse_args()
    lease = read(Path(a.lease))
    assert reservations.owns(lease) and 'building:' + UID in lease['resources']
    base = ROOT / 'docs/astra-city/government-import'
    out = base / BATCH
    assert not out.exists()
    pins, refs = {}, [Path(__file__)]

    def take(batch, path):
        if batch not in pins:
            _, pins[batch] = authenticate(base / batch)
            refs.append(base / batch / 'result.json')
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    role_batch = 'government-xl-west-kowloon-north-masked-landscape-role-review-v1-20261027'
    role = take(role_batch, base / role_batch / 'ROOT-SOURCE-ROLE-REVIEW.json')
    assert role['sourceRoleAccepted'] and role['sourceSpecificRoleOnly']
    assert role['sourceSHA256'] == SHA and role['uids'] == [UID]
    ids = role['reviewedSourceFaces']
    assert ids == sorted(set(ids)) and len(ids) == 35
    runtime, attributes = P + 'three-member-runtime-v2-20261027', P + 'three-member-attributes-v2-20261027'
    row = next(r for r in take(runtime, base / runtime / 'selection.json.gz')['rows'] if r['uid'] == UID)
    g = next(r for r in take(runtime, HERE / 'local' / runtime / 'runtime-geometry.json.gz')['rows'] if r['uid'] == UID)
    attrs = take(attributes, base / attributes / 'attributes.json.gz')
    assert attrs['startEndAllInputsVerified']
    attr = next(r for r in attrs['rows'] if r['uid'] == UID)
    asset = ROOT / row['candidate']['path']
    assert digest(asset.read_bytes()) == row['sourceSHA256'] == g['sourceSHA256'] == attr['sourceSHA256'] == SHA
    refs.append(asset)
    ix = np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)
    worlds = dict(original=decode_original_world_triangles(asset.read_bytes()), **{
        name: np.asarray(attr[field], dtype='<f8').reshape(-1, 3)[ix] for name, field in
        [('literal', 'completeLiteralWorldPosition'), ('leftF32', 'completeExplicitLeftAssociatedFloat32WorldPosition'),
         ('balancedF32', 'completeExplicitBalancedFloat32WorldPosition')]})
    assert np.array_equal(worlds['literal'], np.asarray(g['position']).reshape(-1, 3)[np.asarray(g['index']).reshape(-1, 3)])
    ground = np.asarray(g['drawnGroundGeometry'], dtype='<f8').reshape(-1, 3, 3)
    ground_sha = digest(ground.tobytes())
    building = row['source']['building']
    tile = ROOT / '3d-viewer' / row['source']['tile']
    assert digest(tile.read_bytes()) == row['source']['tileSHA256']
    assert next(b for b in read(tile)['buildings'] if b['uid'] == UID) == building
    refs.append(tile)
    polygon = Polygon(building['rings'][0], building['rings'][1:])
    core_lo, core_hi = np.asarray(building['rings'][0]).min(0), np.asarray(building['rings'][0]).max(0)
    final = module('current_masked_foundation_policy', HERE / 'xl-final-script-pass.py')
    cache, results = {}, []
    for mode, tri in worlds.items():
        assert len(tri) == row['triangles'] == 10322
        masks = []
        for i in ids:
            face = tri[i]
            gaps = np.maximum(core_lo - face[:, [0, 2]].max(0), face[:, [0, 2]].min(0) - core_hi)
            assert np.any(gaps > 0), 'Reviewed auxiliary face reaches the core footprint'
            key = face.astype('<f8').tobytes()
            if key not in cache:
                cache[key] = finite_face_context(face, ground)
            proof = cache[key]
            assert proof['completeProjectionCoverage']['sourceFaceSHA256'] == digest(key)
            assert proof['completeProjectionCoverage']['completeGroundSHA256'] == ground_sha
            masked = bool(proof['completeProjectionCoverage']['exactProjectionCovered']
                          and proof['exactMaximumAllFinitePairGapM'] is not None
                          and Fraction(proof['exactMaximumAllFinitePairGapM']) < 0)
            path = out / mode / (str(i) + '.json.gz')
            save(path, proof)
            masks.append(dict(sourceFace=i, completeProjectionCovered=proof['completeProjectionCoverage']['exactProjectionCovered'],
                              maximumAllFinitePairGapM=proof['exactMaximumAllFinitePairGapM'], strictlyMasked=masked,
                              strictCoreSeparatingAxisGapsM=gaps.tolist(), proof=dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()))))
        keep = [i for i in range(len(tri)) if i not in set(ids)]
        whole = final.foundation_context(tri, ground, polygon)
        ordinary = final.foundation_context(tri[keep], ground, polygon)
        ordinary_pass = (ordinary['completeTerrainTriangles'] == ordinary['triangles'] == 10287
                         and ordinary['fullyBuriedUpwardTriangles'] == 0 and ordinary['fullyBuriedAreaFraction'] <= .001)
        record = dict(mode=mode, sourceWorldSHA256=digest(tri.astype('<f8').tobytes()), groundSHA256=ground_sha,
                      reviewedSourceFaces=ids, currentMaskedFacets=masks, wholeRawFoundation=whole,
                      allOtherSourceFaces=keep, ordinaryFoundation=ordinary, ordinaryFoundationPolicyPassed=ordinary_pass,
                      allReviewedFacesStrictlyMasked=all(r['strictlyMasked'] for r in masks), sourceGeometryChanges=0,
                      physicalAcceptance=False, installationApproved=False)
        save(out / (mode + '.json.gz'), record)
        results.append({k: v for k, v in record.items() if k not in ['currentMaskedFacets', 'allOtherSourceFaces', 'wholeRawFoundation', 'ordinaryFoundation']})
        print(dict(mode=mode, ordinaryPolicyPassed=ordinary_pass, ordinaryBuried=ordinary['fullyBuriedTriangles'],
                   masked=sum(r['strictlyMasked'] for r in masks), wholeRawBuried=whole['fullyBuriedTriangles']), flush=True)
        assert reservations.owns(lease)
    result = dict(uids=[UID], sourceSHA256=SHA, groundSHA256=ground_sha, rows=results,
                  reviewedSourceFaces=ids, allFourCurrentMaskedRoleChecksPassed=all(r['allReviewedFacesStrictlyMasked'] for r in results),
                  allOtherFacesPassEstablishedFoundationPolicy=all(r['ordinaryFoundationPolicyPassed'] for r in results),
                  sourceGeometryChanges=0, sourcePoseChanges=0, physicalAcceptance=False, installationApproved=False, publication=False,
                  qualification='Only the exact previously reviewed35auxiliary source faces receive masking context; '
                  'complete exact finite projection and maximum gaps are checked against every actual current ground facet, '
                  'including collapsed/vertical primitives. All other10287faces retain the unchanged complete/zero-upward-burial/0.001-area '
                  'foundation policy. Analytical partition only: no asset/runtime face deletion, generic policy change, '
                  'closed-solid claim or source/interface/visual/publication approval.')
    save(out / 'summary.json', result)
    refs.extend(HERE / n for n in ['xl-final-script-pass.py', 'exact_packed_world_geometry_20261009.py',
        'complete_original_tin_face_columns_v1_20261027.py', 'exact_original_projection_coverage_v2_20261010.py',
        'exact_original_triangle_pair_column_gap_20261010.py'])
    module('current_masked_foundation_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'exact-current-four-world-masked-auxiliary-and-ordinary-foundation-partition', refs, result)


if __name__ == '__main__': main()
