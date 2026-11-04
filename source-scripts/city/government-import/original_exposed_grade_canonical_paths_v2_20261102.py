"""Diagnose canonical rim warnings against exposed original-wall ground contacts.

No role, physical, publication or installation approval. Existing endpoint and
incidence limits remain unchanged; every root is replayed against all actual
drawn ground primitives, including verticals. Zero-area-only canonical warnings
remain recorded separately and receive no path or root credit; every rendering
warning retains the unchanged full path requirements.
"""
import argparse, sys, uuid
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from original_assembly_four_world_pair_context_v3_20261101 import represented
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_upper_ground_interfaces_20261009 import exact_upper_ground_interfaces
from exact_original_triangle_pair_column_gap_20261010 import verify as exact_column
from original_face_attachment_minimax_v2_20261024 import attachment_paths
from original_wall_rim_accounting_20261009 import original_samples


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['batch', 'uid', 'runtime', 'attributes', 'context', 'rims', 'resources-plan']:
        p.add_argument('--'+name, required=True)
    p.add_argument('--owned', action='store_true'); a = p.parse_args()
    base = ROOT/'docs/astra-city/government-import'; out = base/a.batch
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    pp = (ROOT/a.resources_plan).resolve(); assert pp.is_relative_to(base)
    resources = read(pp)['resources']; assert {'building:'+a.uid, 'terrain:city/data/terrain.json'} <= set(resources)
    lp = HERE/'local'/a.batch/'reservation.json'
    if not a.owned:
        assert not out.exists() and not lp.parent.exists()
        claim = reservations.claim('exposed-grade-paths-'+str(uuid.uuid4()), resources, batch=a.batch, ttl=3600)
        assert claim['ok'], claim
        return execute_reserved(claim['reservation'], lp, [sys.executable, __file__, *sys.argv[1:], '--owned'])
    lease = read(lp); assert reservations.owns(lease) and set(lease['resources']) == set(resources)
    refs, pins = [Path(__file__), pp], {}
    def take(batch, name, local=False):
        assert batch.startswith('government-xl-') and '/' not in batch
        if batch not in pins:
            pins[batch] = authenticate(base/batch)[1]; refs.append(base/batch/'result.json')
        path = (HERE/'local'/batch if local else base/batch)/name
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path); return read(path)
    selection = take(a.runtime, 'selection.json.gz')
    source = next(r for r in selection['rows'] if r['uid'] == a.uid)
    attr = next(r for r in take(a.attributes, 'attributes.json.gz')['rows'] if r['uid'] == a.uid)
    g = next(r for r in take(a.runtime, 'runtime-geometry.json.gz', True)['rows'] if r['uid'] == a.uid)
    asset = ROOT/source['candidate']['path']; assert digest(asset.read_bytes()) == source['sourceSHA256'] == attr['sourceSHA256'] == g['sourceSHA256']; refs.append(asset)
    ix = np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)
    worlds = represented(attr, decode_original_world_triangles(asset.read_bytes()))
    ground = np.asarray(g['drawnGroundGeometry'], dtype='<f8').reshape(-1, 3, 3)
    glo, ghi = ground.min(1), ground.max(1); rows = []
    for mode, tri in worlds.items():
        assert reservations.owns(lease)
        context, rim = take(a.context, mode+'.json.gz'), take(a.rims, mode+'.json.gz')
        sha, gsha = digest(tri.astype('<f8').tobytes()), digest(ground.tobytes())
        assert context['sourceWorldSHA256'] == rim['sourceWorldSHA256'] == sha
        assert context['completeGroundSHA256'] == rim['groundSHA256'] == gsha
        paths = {r['sourceFace']: r for r in context['allWallCapPaths']}
        walls = sorted(i for i, r in paths.items() if r['hasExactSharedEdgeClearCapPath'])
        normal = np.cross(tri[:, 1]-tri[:, 0], tri[:, 2]-tri[:, 0]); lengths = np.linalg.norm(normal, axis=1)
        assert all(lengths[i] > 0 and abs(normal[i, 1]) <= .25*lengths[i] for i in walls)
        interfaces = exact_upper_ground_interfaces(tri, walls, ground); anchors, replays = [], []
        for record in interfaces:
            face = record['sourceFace']
            for interval in record['exactActiveUpperGroundIntervals']:
                endpoints = interval['exactSegmentEndpoints']
                point = np.asarray([float((F(x)+F(y))/2) for x, y in zip(*endpoints)])
                candidates = np.flatnonzero(np.all(glo[:, [0, 2]] <= point[[0, 2]], axis=1) & np.all(ghi[:, [0, 2]] >= point[[0, 2]], axis=1))
                proofs = []
                for j in candidates:
                    proof = exact_column(np.repeat(point[None, :], 3, axis=0), ground[j])
                    if proof['exactClosedHorizontalProjectionsMeet']:
                        proofs.append(dict(groundFace=int(j), proof=proof))
                assert proofs
                gap = min(F(r['proof']['exactMinimumFiniteColumnGapM']) for r in proofs)
                accepted = F(-1, 10) <= gap <= 1
                replays.append(dict(sourceFace=face, position=point.tolist(), exactGapM=str(gap), accepted=accepted, completeGroundProofs=proofs))
                if accepted:
                    height = float(point[1])-float(gap)
                    anchors.append(dict(position=point.tolist(), supportHeight=height, gap=float(point[1])-height, strictAccepted=True, incidentFaces=[face], originalWallClearCapPath=paths[face], actualUpperGroundInterval=interval))
        # Reproduce the original ordered canonical witnesses without rounding.
        positions = np.asarray(attr[{'original':'completeLiteralWorldPosition','literal':'completeLiteralWorldPosition','leftF32':'completeExplicitLeftAssociatedFloat32WorldPosition','balancedF32':'completeExplicitBalancedFloat32WorldPosition'}[mode]], dtype='<f8').reshape(-1, 3).copy()
        if mode == 'original': positions[ix.ravel()] = tri.reshape(-1, 3)
        assert np.array_equal(positions[ix], tri)
        samples = rim['completeOriginalSamples']; expected = original_samples(positions, ix, float(positions[:, 1].min()))
        assert len(samples) == len(expected)
        targets = []; warning_indices = []; nonrendering = []
        for i, (sample, original) in enumerate(zip(samples, expected)):
            assert all(sample[k] == v for k, v in original.items())
            assert sample['gap'] == sample['point'][1]-sample['ground']
            if sample['low'] and (sample['gap'] < -.5 or sample['gap'] > 1):
                incident = [f for f in sample['originalIncidentFaces'] if lengths[f] > 0]
                warning_indices.append(i)
                if not incident:
                    assert sample['originalIncidentFaces'] and all(lengths[f] == 0 for f in sample['originalIncidentFaces'])
                    nonrendering.append(dict(sampleIndex=i, position=sample['point'], rawGap=sample['gap'], originalIncidentFaces=sample['originalIncidentFaces'], pathCredit=False, groundRootCredit=False))
                    continue
                targets.append(dict(witness=dict(sampleIndex=i, position=sample['point'], rawGap=sample['gap']), incidentFaces=incident))
        result = attachment_paths(tri, dict(targets=targets, proof=dict(contacts=[])), [], strict_anchors=anchors)
        passed = bool(anchors) and all(r['hasUnrestrictedFiniteAttachment'] and r['passesExistingEndpointHeight'] and r['maximumResidualM'] <= .001 for r in result)
        save(out/(mode+'.json.gz'), dict(mode=mode, sourceWorldSHA256=sha, completeGroundSHA256=gsha, rawCanonicalWarningIndices=warning_indices, nonrenderingOnlyWarnings=nonrendering, everyWarningAccounted=len(result)+len(nonrendering)==len(warning_indices), originalUpperGradeInterfaces=interfaces, completeRootReplays=replays, acceptedOriginalWallRoots=anchors, rows=result, allPathsPass=passed, physicalAcceptance=False))
        rows.append(dict(mode=mode, rawWarnings=len(warning_indices), renderingWarnings=len(targets), nonrenderingOnlyWarnings=len(nonrendering), actualExposedWallRoots=len(anchors), finitePaths=sum(r['hasUnrestrictedFiniteAttachment'] for r in result), endpointFailures=sum(r.get('riseAboveEndpointsM', 0) > 0 for r in result), allPathsPass=passed)); print(rows[-1], flush=True)
    manifest = ROOT/'3d-viewer/city/data/manifest.json'; assert digest(manifest.read_bytes()) == selection['manifestSHA256']; refs.append(manifest)
    assert reservations.owns(lease)
    refs.extend(HERE/n for n in ['original_assembly_four_world_pair_context_v3_20261101.py','exact_packed_world_geometry_20261009.py','exact_original_upper_ground_interfaces_20261009.py','exact_original_triangle_pair_column_gap_20261010.py','original_face_attachment_minimax_v2_20261024.py','original_wall_rim_accounting_20261009.py'])
    summary = dict(uids=[a.uid], sourceSHA256=source['sourceSHA256'], rows=rows, sourceGeometryChanges=0, sourcePoseChanges=0, groundRootCredit=False, sourceRoleAccepted=False, physicalAcceptance=False, installationApproved=False, publication=False, qualification=__doc__)
    save(out/'summary.json', summary)
    module('exposed_grade_canonical_paths_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'complete-canonical-rim-paths-to-exact-exposed-original-wall-grade-diagnostic', refs, summary)


if __name__ == '__main__': main()
