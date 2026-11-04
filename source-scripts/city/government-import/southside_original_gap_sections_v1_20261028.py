"""Source-bound explanatory sections of the four unchanged Southland originals.

Plots are diagnostics, not structural acceptance or a geometry repair. The exact
finite-primitive proximity receipt remains the negative-distance evidence.
"""
import argparse
import sys
import uuid
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BASE = ROOT/'docs/astra-city/government-import'
BATCH = 'government-xl-southside-original-gap-sections-v1-20261028'
DOC, LOCAL = BASE/BATCH, HERE/'local'/BATCH
LEASE = LOCAL/'reservation.json'
CAP = BASE/'government-xl-southside-project-original-recovery-v1-20261028'
RIM = BASE/'government-xl-southside-project-original-rim-contacts-v1-20261028'
GRAPH = BASE/'government-xl-southside-original-support-proximity-graph-v2-20261028'
SURFACE = BASE/'government-xl-southside-source-bound-surface-contract-v1-20261028'
TARGETS = ['landsd/311759:0', 'landsd/311763:0', 'landsd/330243:0', 'landsd/330244:0']


def section(triangles, axis, coordinate):
    """Intersect complete triangles with an axis-aligned diagnostic plane.

    No vertices are altered. Coplanar faces retain all edges. These float64
    display intersections intentionally make no exact-distance claim.
    """
    segments = []
    for face in triangles:
        delta = face[:, axis] - coordinate
        if delta.min() > 0 or delta.max() < 0:
            continue
        points = []
        for i, j in [(0, 1), (1, 2), (2, 0)]:
            if delta[i] == 0:
                points.append(face[i])
            if delta[i] * delta[j] < 0:
                points.append(face[i] + (face[j]-face[i]) * (-delta[i]/(delta[j]-delta[i])))
        points = np.unique(np.asarray(points).reshape(-1, 3), axis=0)
        if len(points) == 2:
            segments.append(points)
        elif len(points) == 3:
            segments.extend([points[[0, 1]], points[[1, 2]], points[[2, 0]]])
    return np.asarray(segments).reshape(-1, 2, 3)


def owned():
    lease = read(LEASE)
    assert reservations.owns(lease) and not DOC.exists()
    refs, pins, receipts = [Path(__file__)], {}, {}
    for directory in [CAP, RIM, GRAPH, SURFACE]:
        receipt, bound = authenticate(directory)
        receipts[directory.name] = receipt
        refs.append(directory/'result.json')
        for path, sha in bound.items():
            assert path not in pins or pins[path] == sha
            pins[path] = sha

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selection = take(CAP/'selection.json.gz')['rows']
    rims = {r['uid']: r for r in take(RIM/'contacts.json.gz')['rows']}
    graph = take(GRAPH/'summary.json')
    assert all(not r['optimisticPathToAssumedRoot'] and not r['reachableUnknownSourceUnits'] for r in graph['targets'])
    needed = set(TARGETS + ['landsd/315025:0'])
    assert {'building:'+uid for uid in needed} <= set(lease['resources'])
    geometry, source_hashes = {}, {}
    for row in selection:
        if row['uid'] in needed:
            path = ROOT/row['candidate']['path']
            assert digest(path.read_bytes()) == row['sourceSHA256']
            refs.append(path)
            geometry[row['uid']] = decode_original_world_triangles(path.read_bytes())
            source_hashes[row['uid']] = row['sourceSHA256']
    surface = take(SURFACE/'summary.json')
    terrain = take(ROOT/surface['candidate']['path'])['nativeMesh']
    positions = np.asarray(terrain['position'], dtype='<f4').astype('<f8').reshape(-1, 3)
    geometry['private-ground'] = positions[np.asarray(terrain['index']).reshape(-1, 3)]
    rows = []
    fig, axes = plt.subplots(4, 2, figsize=(14, 15), constrained_layout=True)
    colors = {'landsd/315025:0': '#bd5b25', 'private-ground': '#64834a'}
    for index, uid in enumerate(TARGETS):
        assert reservations.owns(lease)
        unresolved = rims[uid]['rawInterface']['unresolved']
        # Largest recorded source/podium gap, deterministic XYZ tie breaker.
        point = sorted(unresolved, key=lambda r: (-r['gap'], r['position']))[0]
        anchor = np.asarray(point['position'])
        own = geometry[uid]
        lo, hi = own.min((0, 1)), own.max((0, 1))
        counts = {}
        for column, (axis, horizontal) in enumerate([(0, 2), (2, 0)]):
            ax = axes[index, column]
            for key in ['private-ground', 'landsd/315025:0', uid]:
                cut = section(geometry[key], axis, anchor[axis])
                counts[str(axis)+':'+key] = len(cut)
                ax.add_collection(LineCollection(cut[:, :, [horizontal, 1]],
                    colors=colors.get(key, '#1863b4'), linewidths=.7, label=key))
            ax.scatter([anchor[horizontal]], [anchor[1]], c='#b71937', s=25, zorder=5)
            support_y = anchor[1]-point['gap']
            ax.plot([anchor[horizontal]]*2, [support_y, anchor[1]], '--', color='#b71937', linewidth=1.5)
            ax.annotate(f"recorded rim gap {point['gap']:.3f} m", (anchor[horizontal], (anchor[1]+support_y)/2),
                        xytext=(8, 0), textcoords='offset points', fontsize=8)
            ax.set_xlim(lo[horizontal]-8, hi[horizontal]+8)
            ax.set_ylim(0, 65)
            ax.set_aspect('equal', adjustable='box')
            ax.grid(alpha=.2)
            ax.set_xlabel(('world Z' if horizontal == 2 else 'world X')+' (m)')
            ax.set_ylabel('HKPD elevation (m)')
            ax.set_title(uid+f" — {'X' if axis == 0 else 'Z'} = {anchor[axis]:.6f} m", fontsize=10)
        rows.append(dict(uid=uid, sourceSHA256=source_hashes[uid], originalBounds=[lo.tolist(), hi.tolist()],
                         diagnosticAnchor=point, sections=counts))
    axes[0, 0].legend(loc='upper left', fontsize=7)
    fig.suptitle('Unchanged government source sections: Southland lower junctions\nBlue: tower original · brown: podium original · green: private source-bound terrain\nDisplay crop only; no geometry edits. Float64 sections illustrate the separate exact proximity receipt.', fontsize=12)
    output = DOC/'original-gap-sections.png'
    output.parent.mkdir(parents=True)
    fig.savefig(output, dpi=150)
    plt.close(fig)
    result = dict(uids=TARGETS, rows=rows, originalSourceHashes=source_hashes,
                  image=dict(path=str(output.relative_to(ROOT)), sha256=digest(output.read_bytes()), width=2100, height=2250),
                  sourceGeometryChanges=0, geometryChanges=0, installationApproved=False,
                  permanentRejection=False, qualification='Explanatory float64 plane intersections of every complete original face. Exact no-root-path evidence is separately bound; visual sections alone cannot prove support absence or source identity. No source coordinates, terrain or catalogue edits.')
    save(DOC/'summary.json', result)
    assert reservations.owns(lease)
    module('southside_gap_sections_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'original-source-gap-section-diagnostic', list(dict.fromkeys(refs)), result)
    print(dict(image=str(output), models=len(rows)), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    if args.owned:
        return owned()
    assert not DOC.exists() and not LOCAL.exists()
    claim = reservations.claim('southside-gap-sections-'+str(uuid.uuid4()),
        sorted('building:'+uid for uid in TARGETS+['landsd/315025:0']), batch=BATCH, ttl=1800)
    assert claim['ok']
    execute_reserved(claim['reservation'], LEASE, [sys.executable, __file__, '--owned'])


if __name__ == '__main__':
    main()
