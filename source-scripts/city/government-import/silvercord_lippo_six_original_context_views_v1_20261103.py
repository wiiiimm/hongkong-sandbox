"""Plot five originals plus the unchanged installed tower against actual private ground."""
import sys
import uuid
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from observed_reserved_runner_v4_20261103 import execute_reserved
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_assembly_context_plot_v3_20261023 import clipped_faces

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-silvercord-lippo-six-original-context-views-v1-20261103'
LOCAL = HERE / 'local' / BATCH
RUNTIME = 'government-xl-silvercord-lippo-five-original-floor-runtime-v1-20261103'
NATIVE = 'government-xl-silvercord-lippo-current-native-contacts-v1-20261103'
OWNER = 'landsd/239465:0'
STYLE = {'landsd/233997:0': ('Silvercord podium', '#4169a1'),
         'landsd/231645:0': ('Lippo podium', '#429267'),
         'landsd/237843:0': ('Langham', '#b66a46'),
         'landsd/238659:0': ('Silvercord Tower 2', '#ae9851'),
         'landsd/239032:0': ('Silvercord Tower 1', '#986bb1'),
         OWNER: ('Installed Lippo tower', '#70777f')}


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

    selection = take(RUNTIME, BASE / RUNTIME / 'selection.json.gz')
    geometry = take(RUNTIME, HERE / 'local' / RUNTIME / 'runtime-geometry.json.gz')
    shapes, bindings, ground_by_key = {}, {}, {}
    for row in selection['rows']:
        uid = row['uid']
        asset = ROOT / row['candidate']['path']
        assert digest(asset.read_bytes()) == row['sourceSHA256']
        refs.append(asset)
        shapes[uid] = decode_original_world_triangles(asset.read_bytes())
        bindings[uid] = row['sourceSHA256']
        g = next(r for r in geometry['rows'] if r['uid'] == uid)
        assert g['sourceSHA256'] == row['sourceSHA256']
        for face in np.asarray(g['drawnGroundGeometry']).reshape(-1, 3, 3):
            # Display-only deduplication across the five overlapping capture windows.
            key = tuple(sorted(tuple(float(v) for v in p) for p in face))
            ground_by_key.setdefault(key, face)
    native_input = take(NATIVE, BASE / NATIVE / 'native-input.json.gz')
    owner = next(r for r in native_input['rows'] if r['uid'] == OWNER)
    asset = ROOT / owner['path']
    assert digest(asset.read_bytes()) == owner['entry']['sha256'] == '2ca41f96bdce41f47c95891182450878c1fc694b12c3ae22bbeb29ff07cc276c'
    refs.append(asset)
    shapes[OWNER] = decode_original_world_triangles(asset.read_bytes())
    bindings[OWNER] = owner['entry']['sha256']
    assert set(shapes) == set(STYLE)
    ground = np.asarray(list(ground_by_key.values()))
    source_points = np.concatenate([t.reshape(-1, 3) for t in shapes.values()])
    lo, hi = source_points.min(0) - [2, 1, 2], source_points.max(0) + [2, 1, 2]
    ground_top = min(float(hi[1]), float(ground[:, :, 1].max()) + 2)
    offset = np.asarray([lo[0], 0, lo[2]])
    out, exports = BASE / BATCH, []
    for label, top in [('whole-assembly', float(hi[1])), ('grade-band', ground_top)]:
        assert reservations.owns(lease)
        upper = hi.copy()
        upper[1] = top
        planes = [(a, float(lo[a]), True) for a in range(3)] + [(a, float(upper[a]), False) for a in range(3)]
        size = np.maximum((upper - lo)[[0, 2, 1]], .1)
        fig = plt.figure(figsize=(17, 10), layout='constrained')
        for i, angle in enumerate([35, 215]):
            ax = fig.add_subplot(1, 2, i + 1, projection='3d')
            for uid, tri in shapes.items():
                polygons = clipped_faces(tri, planes)
                if len(polygons):
                    color = STYLE[uid][1]
                    ax.add_collection3d(Poly3DCollection((polygons - offset)[:, :, [0, 2, 1]],
                        facecolors=color, edgecolors=color, alpha=.48, linewidth=.1))
            polygons = clipped_faces(ground, planes)
            if len(polygons):
                ax.add_collection3d(Line3DCollection([np.vstack([p, p[:1]]) for p in
                    (polygons - offset)[:, :, [0, 2, 1]]], colors='#248748', alpha=.5, linewidth=.3))
            ax.set(xlim=(0, size[0]), ylim=(0, size[1]), zlim=(lo[1], upper[1]),
                   xlabel='X offset m', ylabel='Z offset m', zlabel='HKPD m')
            ax.set_box_aspect(size)
            ax.view_init(25, angle)
        fig.legend(handles=[Patch(color=color, label=name) for name, color in STYLE.values()],
                   loc='outside lower center', ncol=3)
        fig.suptitle('Six unchanged originals at fixed1x source pose: ' + label +
            '\nGreen: actual private candidate ground. Display clipping only; no physical or publication approval.', fontsize=12)
        path = out / (label + '.png')
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=140)
        plt.close(fig)
        refs.append(path)
        exports.append(dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()), display=label))
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert reservations.owns(lease) and digest(manifest.read_bytes()) == selection['manifestSHA256']
    refs.append(manifest)
    result = dict(uids=list(STYLE), sourceSHA256ByUid=bindings, exports=exports,
        displayedSourceFaces={u: len(t) for u, t in shapes.items()}, uniqueDisplayedGroundFacets=len(ground),
        sourceGeometryChanges=0, sourcePoseChanges=0, physicalAcceptance=False, visualAcceptance=False,
        installationApproved=False, publication=False, qualification=__doc__ +
        ' All original indexed triangles are preserved; clipping and exact duplicate ground removal affect plot display only. Inspect exported files before recording ROOT observations. This is not live viewer or physical-phone evidence.')
    save(out / 'summary.json', result)
    refs.extend(HERE / n for n in ['exact_packed_world_geometry_20261009.py', 'original_assembly_context_plot_v3_20261023.py'])
    module('six_original_source_context_views', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'six-unchanged-original-complete-assembly-and-grade-context-exports', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    if '--owned' in sys.argv:
        owned()
    else:
        assert not LOCAL.exists() and not (BASE / BATCH).exists()
        claim = reservations.claim('six-original-context-views-' + str(uuid.uuid4()),
            ['building:' + u for u in STYLE] + ['immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
        assert claim['ok'], claim
        execute_reserved(claim['reservation'], LOCAL / 'reservation.json', [sys.executable, __file__, '--owned'])
