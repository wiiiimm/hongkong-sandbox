"""Evaluate unchanged ordinary rim limits under explicitly provisional wall roles.

This diagnostic grants no role review, physical acceptance or publication approval.
"""
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_reviewed_lower_facet_rim_accounting_v1_20261029 import verify

BASE = ROOT / 'docs/astra-city/government-import'
PREFIX = 'government-xl-academy69025-'
BATCH = PREFIX + 'candidate-wall-rim-account-v1-20261029'
UID = 'landsd/69025:0'
SHA = '75d1193ec409e8522705df1f262f647e12beda5c4e309f9905ca8ba7e5e88414'


def main():
    out = BASE / BATCH
    assert not out.exists()
    refs, pins = [Path(__file__)], {}

    def take(batch, name):
        path = BASE / batch / name
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]
            refs.append(BASE / batch / 'result.json')
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    runtime = PREFIX + 'nested-original-runtime-v1-20261029'
    attrs = PREFIX + 'nested-original-attributes-v1-20261029'
    caps = PREFIX + 'nested-cap-paths-v1-20261029'
    rims = PREFIX + 'complete-nested-rims-v1-20261029'
    selected = next(r for r in take(runtime, 'selection.json.gz')['rows'] if r['uid'] == UID)
    attr = next(r for r in take(attrs, 'attributes.json.gz')['rows'] if r['uid'] == UID)
    assert selected['sourceSHA256'] == attr['sourceSHA256'] == SHA
    asset = ROOT / selected['candidate']['path']
    assert digest(asset.read_bytes()) == SHA
    refs.append(asset)
    ix = np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)
    literal = np.asarray(attr['completeLiteralWorldPosition']).reshape(-1, 3)
    assert len(set(ix.ravel())) == len(literal)
    original = literal.copy()
    original[ix.ravel()] = decode_original_world_triangles(asset.read_bytes()).reshape(-1, 3)
    worlds = dict(original=original, literal=literal,
                  leftF32=np.asarray(attr['completeExplicitLeftAssociatedFloat32WorldPosition']).reshape(-1, 3),
                  balancedF32=np.asarray(attr['completeExplicitBalancedFloat32WorldPosition']).reshape(-1, 3))
    out.mkdir()
    rows = []
    for mode, positions in worlds.items():
        cm = {'leftF32': 'left', 'balancedF32': 'balanced'}.get(mode, mode)
        cap, rim = take(caps, cm + '.json.gz'), take(rims, mode + '.json.gz')
        worldsha = digest(positions[ix].astype('<f8').tobytes())
        assert worldsha == cap['sourceWorldSHA256'] == rim['sourceWorldSHA256']
        partition = cap['completeGroundClearancePartition']
        assert partition['negativeNonWallFaces'] == []
        assert len(partition['paths']) == 153
        assert all(p['hasExactSharedEdgeClearCapPath'] for p in partition['paths'])
        roles = {p['sourceFace']: 'wall' for p in partition['paths']}
        metric = dict(checks=rim['samples'], lowRimChecks=rim['lowRimSamples'],
                      minSurfaceGap=rim['minimumSampleGapM'], minLowGap=rim['minimumRimGapM'],
                      maxLowGap=rim['maximumRimGapM'])
        # Conditional evaluation only. The helper requires this parameter; no
        # provisional role is promoted into an approval record or catalogue.
        account = verify(positions, ix, float(positions[:, 1].min()),
                         rim['completeOriginalSamples'], approved_roles=roles,
                         source_role_review_approved=True, expected_metric=metric)
        account['roleApprovalGranted'] = False
        account['conditionalOnFutureSourceRoleReview'] = True
        save(out / (mode + '-conditional-account.json'), account)
        rows.append(dict(mode=mode, sourceWorldSHA256=worldsha,
                         conditionalLimitsPassed=account['verified'],
                         ordinaryRimSamples=account['ordinaryRimSamples'],
                         strictOrdinaryAnchorSamples=account['strictOrdinaryAnchorSamples'],
                         rawReviewedClearanceFailuresRetained=account['rawReviewedClearanceFailuresRetained']))
    result = dict(uids=[UID], sourceSHA256=SHA, rows=rows,
                  allFourConditionalLimitsPassed=all(r['conditionalLimitsPassed'] for r in rows),
                  sourceRoleReviewApproved=False, physicalAcceptance=False,
                  installationApproved=False, publication=False, sourceGeometryChanges=0,
                  aiGeometryModelling=False,
                  nextStep='Review the exact source wall roles and authored campus interfaces; preserve raw warnings and all publisher gates.')
    save(out / 'summary.json', result)
    refs.extend([HERE / 'original_reviewed_lower_facet_rim_accounting_v1_20261029.py',
                 HERE / 'original_wall_rim_accounting_20261009.py',
                 HERE / 'exact_packed_world_geometry_20261009.py'])
    module('academy_candidate_wall_account_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'conditional-four-world-wall-rim-account-no-approval', refs, result)


if __name__ == '__main__':
    main()
