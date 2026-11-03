"""Show every measured negative original facet in complete source/ground context.

Display-only context: no source geometry changes, new gate or role approval.
"""
import sys
import uuid
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_assembly_context_plot_v3_20261023 import clipped_faces

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-silvercord-lippo-complete-lower-source-views-v1-20261103'
LOCAL = HERE / 'local' / BATCH
RUNTIME = 'government-xl-silvercord-lippo-complete-floor-runtime-v2-20261103'
UIDS = ['landsd/233997:0', 'landsd/231645:0']


def owned():
    lease = read(LOCAL / 'reservation.json')
    assert reservations.owns(lease) and not (BASE / BATCH).exists()
    refs, pins = [Path(__file__)], {}

    def take(batch, path):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]
            refs.append(BASE / batch / 'result.json')
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selected = take(RUNTIME, BASE / RUNTIME / 'selection.json.gz')['rows']
    geometry = take(RUNTIME, HERE / 'local' / RUNTIME / 'runtime-geometry.json.gz')['rows']
    out = BASE / BATCH
    out.mkdir()
    exports, records = [], []
    for uid in UIDS:
        assert reservations.owns(lease)
        row = next(r for r in selected if r['uid'] == uid)
        g = next(r for r in geometry if r['uid'] == uid)
        asset = ROOT / row['candidate']['path']
        assert digest(asset.read_bytes()) == row['sourceSHA256'] == g['sourceSHA256']
        refs.append(asset)
        tri = decode_original_world_triangles(asset.read_bytes())
        ground = np.asarray(g['drawnGroundGeometry'], dtype='<f8').reshape(-1, 3, 3)
        name = 'government-xl-silvercord-lippo-complete-floor-low-faces-v1-20261103-' + uid.split('/')[1].replace(':', '-')
        low = take(name, BASE / name / 'original.json.gz')
        assert digest(tri.tobytes()) == low['sourceWorldSHA256'] and digest(ground.tobytes()) == low['groundSHA256']
        negative_ids = [r['sourceFace'] for r in low['rows']]
        assert len(tri) == low['completeSourceFaces'] == row['triangles']
        lo, hi = tri.min((0, 1))-[2, 1, 2], tri.max((0, 1))+[2, 1, 2]
        lower_top = min(hi[1], float(ground[:, :, 1].max())+1)
        for label, upper in [('whole-original', hi[1]), ('grade-band', lower_top)]:
            bound_hi = hi.copy()
            bound_hi[1] = upper
            planes = [(axis, float(lo[axis]), True) for axis in range(3)] + [(axis, float(bound_hi[axis]), False) for axis in range(3)]
            size = np.maximum((bound_hi-lo)[[0, 2, 1]], .1)
            fig = plt.figure(figsize=(16, 8), layout='constrained')
            for k, angle in enumerate([35, 215]):
                ax = fig.add_subplot(1, 2, k+1, projection='3d')
                for faces, color, alpha in [(tri, '#64748b', .12), (tri[negative_ids], '#d04729', .9)]:
                    polys = clipped_faces(faces, planes)
                    if len(polys):
                        ax.add_collection3d(Poly3DCollection((polys-lo)[:, :, [0, 2, 1]], facecolors=color, edgecolors=color, alpha=alpha, linewidth=.2))
                polys = clipped_faces(ground, planes)
                if len(polys):
                    ax.add_collection3d(Line3DCollection([np.vstack([v, v[:1]]) for v in (polys-lo)[:, :, [0, 2, 1]]], colors='#16834a', linewidth=.35, alpha=.65))
                ax.set(xlim=(0, size[0]), ylim=(0, size[1]), zlim=(0, size[2]), xlabel='X offset m', ylabel='Z offset m', zlabel='HKPD offset m')
                ax.set_box_aspect(size.copy())
                ax.view_init(25, angle)
            fig.suptitle(f'{uid}: {label}; original {len(tri)} faces, all {len(negative_ids)} negative facets red\nGrey: unchanged source; green: complete drawn ground. Band clips display only; no source-role/physical approval.', fontsize=11)
            path = out / (uid.split('/')[1].replace(':', '-')+'-'+label+'.png')
            fig.savefig(path, dpi=140)
            plt.close(fig)
            refs.append(path)
            exports.append(dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()), uid=uid, display=label))
        records.append(dict(uid=uid, sourceSHA256=row['sourceSHA256'], sourceWorldSHA256=digest(tri.tobytes()), groundSHA256=digest(ground.tobytes()), completeSourceFaces=len(tri), completeNegativeSourceFaceIds=negative_ids))
    assert reservations.owns(lease)
    result = dict(uids=UIDS, rows=records, exports=exports, sourceGeometryChanges=0, sourcePoseChanges=0,
                  sourceRoleAccepted=False, physicalAcceptance=False, installationApproved=False, publication=False,
                  qualification='Every measured negative original source facet is highlighted against whole-source and actual-drawn-ground context in two views. A separate grade-band display clips plotting context only; all original bytes/faces and raw proof IDs remain preserved. No architecture, basement-to-face identification, engineering root or physical approval.')
    save(out / 'summary.json', result)
    refs.extend(HERE / n for n in ['exact_packed_world_geometry_20261009.py', 'original_assembly_context_plot_v3_20261023.py'])
    module('silvercord_lippo_lower_whole_views_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'complete-original-negative-facet-and-drawn-grade-context-exports', list(dict.fromkeys(refs)), result)
    print(dict(exports=len(exports), sourceGeometryChanges=0, physicalAcceptance=False), flush=True)


if __name__ == '__main__':
    if '--owned' in sys.argv:
        owned()
    else:
        assert not LOCAL.exists() and not (BASE / BATCH).exists()
        claim = reservations.claim('silvercord-lippo-lower-context-views-' + str(uuid.uuid4()), ['building:' + u for u in UIDS] + ['immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
        assert claim['ok'], claim
        execute_reserved(claim['reservation'], LOCAL / 'reservation.json', [sys.executable, __file__, '--owned'])
