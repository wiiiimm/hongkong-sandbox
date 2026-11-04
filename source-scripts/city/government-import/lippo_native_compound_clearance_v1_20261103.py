"""Exact tower clearance against actual ground plus the proposed Lippo podium.

Every represented original face is retained. Diagnostic only; no acceptance.
"""
import sys
import uuid
from fractions import Fraction
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from exact_original_triangle_pair_column_gap_20261010 import verify
from complete_clearance_cap_paths_v2_20261024 import verify as cap_verify

BASE = ROOT / 'docs/astra-city/government-import'
INPUT = 'government-xl-lippo-current-native-podium-migration-probe-v1-20261103'
RUNTIME = 'government-xl-silvercord-lippo-complete-floor-runtime-v2-20261103'
BATCH = 'government-xl-lippo-native-compound-clearance-v1-20261103'
LOCAL = HERE / 'local' / BATCH
TOWER, PODIUM = 'landsd/239465:0', 'landsd/231645:0'


def owned():
    lease = read(LOCAL / 'reservation.json')
    assert reservations.owns(lease)
    out = BASE / BATCH
    assert not out.exists()
    refs, pins = [Path(__file__)], {}

    def take(batch, path):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]
            refs.append(BASE / batch / 'result.json')
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    summary = take(INPUT, BASE / INPUT / 'summary.json')
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == summary['currentManifestSHA256']
    refs.append(manifest)
    geometry = next(r for r in take(RUNTIME, HERE / 'local' / RUNTIME / 'runtime-geometry.json.gz')['rows'] if r['uid'] == PODIUM)
    actual = np.asarray(geometry['drawnGroundGeometry'], dtype='<f8').reshape(-1, 3, 3)
    assert digest(actual.tobytes()) == summary['completeActualDrawnGroundSHA256']
    summaries = []
    for mode in ['original', 'literal', 'leftF32', 'balancedF32']:
        assert reservations.owns(lease)
        inp = take(INPUT, BASE / INPUT / mode / 'input.json.gz')
        prior = take(INPUT, BASE / INPUT / mode / 'diagnostic.json.gz')
        assert len(inp['rows']) == 1 and inp['rows'][0]['uid'] == TOWER
        row = inp['rows'][0]
        tri = np.asarray(row['position'], dtype='<f8').reshape(-1, 3)[np.asarray(row['index']).reshape(-1, 3)]
        support = np.asarray(inp['podium'], dtype='<f8')
        assert len(tri) == 3597 and len(support) == 13725
        assert digest(tri.tobytes()) == prior['sourceWorldSHA256ByUid'][TOWER]
        assert digest(support.tobytes()) == prior['sourceWorldSHA256ByUid'][PODIUM]
        assert prior['compoundFoundation']['completeTerrainTriangles'] == len(tri)
        ground = np.concatenate([actual, support])
        low, high = ground[:, :, [0, 2]].min(1), ground[:, :, [0, 2]].max(1)
        maximum = Fraction(float(ground[:, :, 1].max()))
        threshold = Fraction(-1, 2)
        negative, pruned, tested = [], 0, 0
        for face, t in enumerate(tri):
            if Fraction(float(t[:, 1].min())) - maximum >= threshold:
                pruned += 1
                continue
            xz = t[:, [0, 2]]
            ids = np.flatnonzero(np.all(high >= xz.min(0), axis=1) & np.all(low <= xz.max(0), axis=1))
            failures = []
            for j in ids:
                proof = verify(t, ground[j])
                tested += 1
                if proof['exactClosedHorizontalProjectionsMeet'] and Fraction(proof['exactMinimumFiniteColumnGapM']) < threshold:
                    failures.append(dict(groundFace=int(j), proof=proof))
            if failures:
                normal = np.cross(t[1]-t[0], t[2]-t[0])
                length = float(np.linalg.norm(normal))
                negative.append(dict(sourceFace=face, vertices=t.tolist(), absoluteNormalYRatio=abs(float(normal[1])) / length if length else None,
                                     signedNormalYRatio=float(normal[1]) / length if length else None, negativeGroundPairProofs=failures))
        affected = [r['sourceFace'] for r in negative]
        caps = cap_verify(tri, affected)
        save(out / (mode + '.json.gz'), dict(mode=mode, sourceWorldSHA256=prior['sourceWorldSHA256ByUid'][TOWER],
              actualGroundSHA256=digest(actual.tobytes()), supportWorldSHA256=prior['sourceWorldSHA256ByUid'][PODIUM],
              compoundGroundSHA256=digest(ground.tobytes()), completeSourceFaces=len(tri), completeGroundFaces=len(ground),
              globalHeightBoundPrunedFaces=pruned, finitePairsTested=tested, rows=negative, capPaths=caps,
              sourceGeometryChanges=0, physicalAcceptance=False))
        result = dict(mode=mode, completeSourceFaces=len(tri), globalHeightBoundPrunedFaces=pruned, finitePairsTested=tested,
                      exactAffectedFaces=affected, negativeNonWallFaces=caps['negativeNonWallFaces'],
                      unresolvedSharedEdgeWallFaces=[r['sourceFace'] for r in caps['paths'] if not r['hasExactSharedEdgeClearCapPath']],
                      allAffectedHaveClearCapPaths=caps['allAffectedHavePaths'])
        summaries.append(result)
        print({k: v for k, v in result.items() if k != 'exactAffectedFaces'}, flush=True)
    assert reservations.owns(lease) and digest(manifest.read_bytes()) == summary['currentManifestSHA256']
    result = dict(uids=[TOWER, PODIUM], sourceSHA256ByUid=summary['sourceSHA256ByUid'], currentManifestSHA256=summary['currentManifestSHA256'], rows=summaries,
                  allDrawnTerrainAndPodiumFacesAccountedFor=True, sourceGeometryChanges=0, sourcePoseChanges=0,
                  supportApproved=False, physicalAcceptance=False, sourceRoleAccepted=False, installationApproved=False, publication=False,
                  qualification='Exact -0.5m finite-column test over every source face and all inclusive-XZ compound providers, including vertical and collapsed projections. Only a conservative global height bound prunes source faces. Full actual-ground coverage is separately bound to the complete prior foundation result. Negative faces and existing shared-edge clear-cap paths remain diagnostic; no new intercomponent/root or publication credit.')
    save(out / 'summary.json', result)
    refs.extend(HERE / n for n in ['exact_original_triangle_pair_column_gap_20261010.py', 'complete_clearance_cap_paths_v2_20261024.py'])
    module('lippo_compound_clearance_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'complete-four-world-current-lippo-tower-ground-and-proposed-podium-clearance', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    if '--owned' in sys.argv:
        owned()
    else:
        assert not LOCAL.exists() and not (BASE / BATCH).exists()
        claim = reservations.claim('lippo-compound-clearance-' + str(uuid.uuid4()), ['building:' + u for u in [TOWER, PODIUM]] + ['immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
        assert claim['ok'], claim
        execute_reserved(claim['reservation'], LOCAL / 'reservation.json', [sys.executable, __file__, '--owned'])
