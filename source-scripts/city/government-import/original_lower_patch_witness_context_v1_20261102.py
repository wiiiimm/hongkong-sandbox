"""Attribute failed original samples to exact lower patches, walls and ground paths.

Mechanical context only. Connected lower patches keep each original tilted face;
no coplanarity, geometry, tolerance, source role or publication is invented.
"""
import argparse
import sys
import uuid
from collections import Counter, deque
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from original_below_grade_source_context_v3_20261102 import face_adjacency
from original_assembly_four_world_pair_context_v3_20261101 import represented
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from complete_clearance_cap_paths_v2_20261024 import verify


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for k in ['batch', 'uid', 'runtime', 'attributes', 'belowgrade', 'canonical', 'roots', 'resources-plan']:
        p.add_argument('--' + k, required=True)
    p.add_argument('--owned', action='store_true')
    a = p.parse_args()
    base = ROOT / 'docs/astra-city/government-import'
    planpath = (ROOT / a.resources_plan).resolve()
    assert planpath.is_relative_to(base)
    plan = read(planpath)
    resources = set(plan['resources'])
    assert 'building:' + a.uid in resources and 'terrain:city/data/terrain.json' in resources
    out, local = base / a.batch, HERE / 'local' / a.batch
    assert not out.exists() and all(n.startswith('government-xl-') and '/' not in n for n in [a.batch, a.runtime, a.attributes, a.belowgrade, a.canonical, a.roots])
    lp = local / 'reservation.json'
    if not a.owned:
        assert not local.exists()
        c = reservations.claim('original-lower-witness-context-' + str(uuid.uuid4()), sorted(resources), batch=a.batch, ttl=3600)
        assert c['ok'], c
        return execute_reserved(c['reservation'], lp, [sys.executable, __file__, *sys.argv[1:], '--owned'])
    lease = read(lp)
    assert reservations.owns(lease) and set(lease['resources']) == resources
    refs, pins = [Path(__file__), planpath], {}

    def take(batch, filename):
        if batch not in pins:
            pins[batch] = authenticate(base / batch)[1]
            refs.append(base / batch / 'result.json')
        path = base / batch / filename
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selection = take(a.runtime, 'selection.json.gz')
    source = next(r for r in selection['rows'] if r['uid'] == a.uid)
    attrs = next(r for r in take(a.attributes, 'attributes.json.gz')['rows'] if r['uid'] == a.uid)
    asset = ROOT / source['candidate']['path']
    assert digest(asset.read_bytes()) == source['sourceSHA256'] == attrs['sourceSHA256']
    refs.append(asset)
    worlds = represented(attrs, decode_original_world_triangles(asset.read_bytes()))
    rows = []
    for mode, tri in worlds.items():
        assert reservations.owns(lease)
        below = take(a.belowgrade, mode + '.json.gz')
        canonical = take(a.canonical, mode + '.json.gz')
        roots = take(a.roots, a.uid.split('/')[1] + '/' + mode + '/paths.json.gz')
        sha = digest(tri.astype('<f8').tobytes())
        assert sha == below['sourceWorldSHA256'] == canonical['sourceWorldSHA256'] == roots['sourceWorldSHA256']
        assert below['completeGroundSHA256'] == canonical['completeDrawnGroundSHA256'] == roots['completeDrawnGroundSHA256']
        normal = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        lengths = np.linalg.norm(normal, axis=1)
        renderable = set(map(int, np.flatnonzero(lengths > 0)))
        down = set(map(int, np.flatnonzero(normal[:, 1] < -.25 * lengths)))
        walls = set(map(int, np.flatnonzero((lengths > 0) & (np.abs(normal[:, 1]) <= .25 * lengths))))
        adjacency = face_adjacency(tri)
        bad = set(below['completeNegativeFaces'])
        groups, seen = [], set()
        for seed in sorted(bad & down):
            if seed in seen:
                continue
            group, queue = {seed}, deque([seed])
            while queue:
                for j in adjacency[queue.popleft()] & down - group:
                    group.add(j)
                    queue.append(j)
            seen |= group
            boundary = {j for i in group for j in adjacency[i] if j not in group}
            groups.append(dict(sourceFaces=sorted(group), negativeSourceFaces=sorted(group & bad), boundaryWallFaces=sorted(boundary & walls)))
        boundary = {i for g in groups for i in g['boundaryWallFaces']}
        pairs = [r['sourceFaces'] for r in below['recomputedPositiveFiniteSourceContacts']]
        caps = verify(tri, sorted(bad | boundary), pairs)
        cap_paths = {r['sourceFace']: r for r in caps['paths']}
        grade = {c['sourceFaceA'] for c in below['completePositiveGradeContacts']}
        for group in groups:
            group['boundaryGradeAndClearCapFaces'] = [i for i in group['boundaryWallFaces'] if i in grade and cap_paths[i]['hasExactSharedEdgeClearCapPath']]
            group['hasBoundaryGradeAndClearCap'] = bool(group['boundaryGradeAndClearCapFaces'])
            group['originalYRangeM'] = [float(tri[group['sourceFaces'], :, 1].min()), float(tri[group['sourceFaces'], :, 1].max())]
        classified = {i for g in groups if g['hasBoundaryGradeAndClearCap'] for i in g['sourceFaces']}
        assert set(i for g in groups for i in g['negativeSourceFaces']) == bad & down
        qualified_faces = classified | {i for i in below['negativeWallFaces'] if cap_paths[i]['hasExactSharedEdgeClearCapPath']}
        path_by_point = {tuple(r['witness']['position']): r for r in roots['rows'] if r['hasUnrestrictedFiniteAttachment'] and r['passesExistingEndpointHeight']}
        anchors = {tuple(r['position']) for r in roots['canonicalStrictRoots']}
        witnesses, counts = [], Counter()
        for witness in canonical['failedSamplesVerbatim']:
            kinds = []
            incident = set(witness['originalIncidentFaces'])
            real = incident & renderable
            if witness['gap'] < -.5:
                kinds.append('classified-wall-or-lower-patch' if real and real <= qualified_faces else 'unattributed-clearance')
            if witness['low'] and witness['gap'] > 1:
                point = tuple(witness['point'])
                kinds.append('exact-canonical-root-path' if point in anchors or point in path_by_point else 'unattributed-raised-rim')
            assert kinds
            counts.update(kinds)
            witnesses.append(dict(witness=witness, renderableIncidentFaces=sorted(real), nonrenderingIncidentFaces=sorted(incident - renderable), attribution=kinds))
        unresolved = [w for w in witnesses if any(k.startswith('unattributed-') for k in w['attribution'])]
        assert len(witnesses) == len(canonical['failedSamplesVerbatim'])
        report = dict(mode=mode, sourceWorldSHA256=sha, groundSHA256=below['completeGroundSHA256'], downwardPatchComponents=groups, completeFailedWitnesses=witnesses, unattributedWitnesses=unresolved, counts=dict(counts), everyFailedWitnessMechanicallyAttributed=not unresolved, supportApproved=False, sourceRoleAccepted=False, physicalAcceptance=False)
        save(out / (mode + '.json.gz'), report)
        row = dict(mode=mode, failedWitnesses=len(witnesses), counts=dict(counts), unattributedWitnesses=len(unresolved), downwardPatches=len(groups), downwardPatchesWithGradeAndClearCap=sum(g['hasBoundaryGradeAndClearCap'] for g in groups), negativeDownwardFaces=len(bad & down), allNegativeWallsHaveClearCaps=not below['wallsWithoutSharedEdgeClearCapPath'])
        rows.append(row)
        print(row, flush=True)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256']
    refs.extend([manifest, HERE / 'original_below_grade_source_context_v3_20261102.py', HERE / 'complete_clearance_cap_paths_v2_20261024.py', HERE / 'original_assembly_four_world_pair_context_v3_20261101.py', HERE / 'exact_packed_world_geometry_20261009.py'])
    assert reservations.owns(lease)
    result = dict(uids=[a.uid], sourceSHA256=source['sourceSHA256'], rows=rows, sourceGeometryChanges=0, sourcePoseChanges=0, genericThresholdChanges=0, groundRootCredit=False, sourceRoleAccepted=False, physicalAcceptance=False, installationApproved=False, publication=False, qualification=__doc__ + ' Every failed canonical sample remains verbatim. Lower surfaces connect only by exact nonzero original edges; original tilted planes remain separate faces. Grade/cap and exact canonical point/path matches are diagnostics, not an acceptance policy or role approval. Unmatched witnesses stay explicit; no proximity matching is substituted.')
    save(out / 'summary.json', result)
    module('lower_patch_witness_context_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'complete-original-lower-patch-and-failed-sample-attribution-no-approval', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
