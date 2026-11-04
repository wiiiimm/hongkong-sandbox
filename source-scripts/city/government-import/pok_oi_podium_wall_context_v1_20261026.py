"""Export remaining original podium wall/ground diagnostics without acceptance."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from sung_fung_original_podium_low_surface_views_v1_20261024 import clipped


def main():
    base = ROOT / 'docs/astra-city/government-import'
    batch = 'government-xl-after-ying-hoi-pok-oi-podium-wall-context-v2-20261026'
    runtime = 'government-xl-after-ying-hoi-pok-oi-pair-bound-ground-v1-20261026'
    clearance = 'government-xl-after-ying-hoi-pok-oi-71329-complete-clearance-v1-20261026'
    out = base / batch
    assert not out.exists()
    refs, pins = [Path(__file__)], {}
    def take(n, p):
        if n not in pins:
            pins[n] = authenticate(base / n)[1]
            refs.append(base / n / 'result.json')
        assert digest(p.read_bytes()) == pins[n][str(p.relative_to(ROOT))]
        refs.append(p)
        return read(p)
    selection = take(runtime, base / runtime / 'selection.json.gz')
    row = next(r for r in selection['rows'] if r['uid'] == 'landsd/71329:0')
    g = next(r for r in take(runtime, HERE / 'local' / runtime / 'runtime-geometry.json.gz')['rows'] if r['uid'] == row['uid'])
    detail = take(clearance, base / clearance / 'original.json.gz')
    cap = take(clearance, base / clearance / 'original-cap-paths.json.gz')['proof']
    asset = ROOT / row['candidate']['path']
    assert digest(asset.read_bytes()) == row['sourceSHA256'] == g['sourceSHA256']
    refs.append(asset)
    tri = decode_original_world_triangles(asset.read_bytes())
    ground = np.asarray(g['drawnGroundGeometry'], dtype='<f8').reshape(-1, 3, 3)
    assert digest(tri.tobytes()) == detail['sourceWorldSHA256']
    assert digest(ground.tobytes()) == detail['groundSHA256']
    ids = [r['sourceFace'] for r in cap['paths'] if not r['hasExactSharedEdgeClearCapPath']]
    unexposed = [r['sourceFace'] for r in detail['rows'] if not r['highestVertexAboveEveryOverlappingGroundFace']]
    records = []
    out.mkdir()
    for label, faces in [('remaining-cap-walls', ids), ('unexposed-highest-vertex', unexposed)]:
        assert faces
        bad = tri[faces]
        lo, hi = bad.min((0, 1)) - [2, 1, 2], bad.max((0, 1)) + [2, 2, 2]
        size = np.maximum((hi - lo)[[0, 2, 1]], .1)
        fig = plt.figure(figsize=(15, 7), layout='constrained')
        for k, angle in enumerate([35, 215]):
            ax = fig.add_subplot(1, 2, k + 1, projection='3d')
            for mesh, color, alpha in [(tri, '#64748b', .15), (bad, '#b91c1c', 1)]:
                polys = clipped(mesh, lo, hi)
                if polys:
                    ax.add_collection3d(Poly3DCollection(polys, facecolors=color, edgecolors=color, alpha=alpha, linewidth=.35))
            polys = clipped(ground, lo, hi)
            if polys:
                ax.add_collection3d(Line3DCollection([np.vstack([poly, poly[:1]]) for poly in polys], colors='#16834a', linewidth=.8), autolim=False)
            ax.set_xlim(0, size[0]); ax.set_ylim(0, size[1]); ax.set_zlim(0, size[2])
            ax.set_box_aspect(size); ax.view_init(24, angle)
            ax.set_xlabel('X offset m'); ax.set_ylabel('Z offset m'); ax.set_zlabel('HKPD offset m')
        fig.suptitle(f'Original Pok Oi podium: {label}, {len(faces)} faces\nRed: flagged original walls; grey: unchanged source; green: current ground. Display crops only.')
        path = out / (label + '.png')
        fig.savefig(path, dpi=130); plt.close(fig)
        records.append(dict(sourceFaces=faces, image=str(path.relative_to(ROOT)), imageSHA256=digest(path.read_bytes())))
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256']
    refs.extend([manifest, HERE / 'sung_fung_original_podium_low_surface_views_v1_20261024.py', HERE / 'exact_packed_world_geometry_20261009.py'])
    result = dict(uids=[row['uid']], sourceSHA256=row['sourceSHA256'], images=records,
                  installationApproved=False, physicalAcceptance=False, publication=False,
                  sourceGeometryChanges=0, sourcePoseChanges=0)
    save(out / 'summary.json', result)
    module('pok_oi_wall_views_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        batch, 'original-podium-unresolved-wall-current-ground-visual-context', refs, result)


if __name__ == '__main__':
    main()
