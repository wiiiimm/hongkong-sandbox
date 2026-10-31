"""Reconcile saved exact compound warnings without repeating geometric solvers.

This is historical source-bound diagnostic context, not current scene acceptance.
"""
import argparse
import sys
import uuid
from pathlib import Path

import numpy as np

from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
P = 'government-xl-palazzo76610-'
BATCH = P + 'saved-partition-audit-v1-20261031'
PARTS = [252774, 71042, 71045, 71688, 71703, 71709, 71886, 72626, 88303, 88899, 89150]
OWNER = 'landsd/76610:0'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lease')
    args = parser.parse_args()
    actors = [OWNER, *['landsd/' + str(i) + ':0' for i in PARTS]]
    resources = {'building:' + u for u in actors}
    out = BASE / BATCH
    assert not out.exists()
    if not args.lease:
        local = HERE / 'local' / BATCH
        assert not local.exists()
        claim = reservations.claim('palazzo-saved-audit-' + str(uuid.uuid4()),
                                   sorted(resources), batch=BATCH, ttl=3600)
        assert claim['ok'], claim
        return execute_reserved(claim['reservation'], local / 'reservation.json',
            [sys.executable, __file__, '--lease', str(local / 'reservation.json')])
    lease = read(Path(args.lease))
    assert reservations.owns(lease) and resources <= set(lease['resources'])
    refs, pins, receipts = [Path(__file__)], {}, {}

    def take(batch, path):
        if batch not in pins:
            receipts[batch], pins[batch] = authenticate(BASE / batch)
            refs.append(BASE / batch / 'result.json')
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    runtime = P + 'twelve-original-patch-runtime-v1-20261031'
    attributes = P + 'twelve-original-attributes-v1-20261031'
    selection = take(runtime, BASE / runtime / 'selection.json.gz')
    selected = {r['uid']: r for r in selection['rows']}
    geometry = {r['uid']: r for r in take(runtime, HERE / 'local' / runtime / 'runtime-geometry.json.gz')['rows']}
    attrs = {r['uid']: r for r in take(attributes, BASE / attributes / 'attributes.json.gz')['rows']}
    fields = [('literal', 'completeLiteralWorldPosition'),
              ('left', 'completeExplicitLeftAssociatedFloat32WorldPosition'),
              ('balanced', 'completeExplicitBalancedFloat32WorldPosition')]
    worlds = {}
    for uid in actors:
        source, attr = selected[uid], attrs[uid]
        asset = ROOT / source['candidate']['path']
        assert digest(asset.read_bytes()) == source['sourceSHA256'] == attr['sourceSHA256'] == geometry[uid]['sourceSHA256']
        refs.append(asset)
        ix = np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)
        worlds[uid] = {'original': decode_original_world_triangles(asset.read_bytes()),
                      **{m: np.asarray(attr[f], dtype='<f8').reshape(-1, 3)[ix] for m, f in fields}}
    rows = []
    for number in PARTS:
        uid = 'landsd/' + str(number) + ':0'
        batch = P + str(number) + '-compound-lower-context-v1-20261031'
        terrain = np.asarray(geometry[uid]['drawnGroundGeometry'], dtype='<f8').reshape(-1, 3, 3)
        for mode, source in worlds[uid].items():
            assert reservations.owns(lease)
            doc = take(batch, BASE / batch / (mode + '.json.gz'))
            peer = worlds[OWNER][mode]
            ground = np.concatenate([terrain, peer])
            assert doc['sourceWorldSHA256'] == digest(source.tobytes())
            assert doc['terrainSHA256'] == digest(terrain.tobytes())
            assert doc['peerUid'] == OWNER and doc['peerWorldSHA256'] == digest(peer.tobytes())
            assert doc['groundSHA256'] == digest(ground.tobytes())
            assert doc['completeSourceFaces'] == len(source)
            terrain_faces, peer_faces = set(), set()
            pair_counts = dict(terrain=0, peer=0)
            for face in doc['rows']:
                for pair in face['negativeGroundPairProofs']:
                    index = pair['groundFace']
                    assert 0 <= index < len(ground)
                    kind = 'terrain' if index < len(terrain) else 'peer'
                    pair_counts[kind] += 1
                    (terrain_faces if kind == 'terrain' else peer_faces).add(face['sourceFace'])
            caps = doc['completeCompoundClearanceCapPaths']
            rows.append(dict(uid=uid, mode=mode, sourceWorldSHA256=doc['sourceWorldSHA256'],
                terrainSHA256=doc['terrainSHA256'], peerWorldSHA256=doc['peerWorldSHA256'],
                terrainFaceBoundary=len(terrain), negativeTerrainSourceFaces=sorted(terrain_faces),
                negativePeerSourceFaces=sorted(peer_faces), negativePairCounts=pair_counts,
                nonWallFaces=caps['negativeNonWallFaces'],
                unresolvedCapFaces=[r['sourceFace'] for r in caps['paths'] if not r['hasExactSharedEdgeClearCapPath']],
                rawCompoundFlagsPreserved=True))
    assert reservations.owns(lease)
    result = dict(uids=actors, rows=rows, allCompanionTerrainPartitionsClear=all(not r['negativeTerrainSourceFaces'] for r in rows),
        historicalRuntimeManifestSHA256=selection['manifestSHA256'],
        currentManifestSHA256=digest((ROOT / '3d-viewer/city/data/manifest.json').read_bytes()),
        currentSceneAcceptance=False, sourceRoleAccepted=False, physicalAcceptance=False,
        installationApproved=False, publication=False, newlyInstalled=0, sourceGeometryChanges=0,
        qualification='Reuses completed exact negative-pair lists, authenticated by Neon and source/peer/ground array hashes in all four streams. Splits actual terrain pairs from original peer surfaces by the verified concatenation boundary. No geometry solver rerun, erased warnings, support roots, source-role approval or current-scene acceptance. Current whole-scene scope still requires refresh after Prosperous installation.')
    save(out / 'summary.json', result)
    refs.extend([HERE / 'exact_packed_world_geometry_20261009.py'])
    module('palazzo_saved_partition_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'authenticated-saved-four-world-compound-partition-audit', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
