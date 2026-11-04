"""Render complete original assembly and a labelled base-only diagnostic view."""
import argparse
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles



def clipped_faces(triangles, planes):
    result = []
    for face in triangles:
        poly = [v.copy() for v in face]
        for axis, limit, lower in planes:
            out = []
            for start, end in zip(poly, poly[1:] + poly[:1]):
                inside_a = start[axis] >= limit if lower else start[axis] <= limit
                inside_b = end[axis] >= limit if lower else end[axis] <= limit
                if inside_a:
                    out.append(start)
                if inside_a != inside_b:
                    t = (limit - start[axis]) / (end[axis] - start[axis])
                    point = start + t * (end - start)
                    point[axis] = limit
                    out.append(point)
            poly = out
            if not poly:
                break
        result.extend([poly[0], poly[i], poly[i + 1]] for i in range(1, len(poly) - 1))
    return np.asarray(result).reshape(-1, 3, 3)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for k in ['batch', 'runtime']:
        p.add_argument('--' + k, required=True)
    p.add_argument('--base-height', type=float, required=True)
    a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc = base / a.batch
    assert not doc.exists()
    _, pins = authenticate(base / a.runtime)
    refs = [Path(__file__), base / a.runtime / 'result.json']

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    sources = take(base / a.runtime / 'selection.json.gz')['rows']
    runtime = take(HERE / 'local' / a.runtime / 'runtime-geometry.json.gz')['rows']
    models = []
    for row in sources:
        path = ROOT / row['candidate']['path']
        assert digest(path.read_bytes()) == row['sourceSHA256']
        refs.append(path)
        tri = decode_original_world_triangles(path.read_bytes())
        assert len(tri) == row['triangles']
        models.append((row, tri))
    all_tri = np.concatenate([t for _, t in models])
    low, high = all_tri.min((0, 1)), all_tri.max((0, 1))
    center = (low + high) / 2
    ground = np.asarray(runtime[0]['drawnGroundGeometry']).reshape(-1, 3, 3)
    mask = np.all(ground[:, :, [0, 2]].max(1) >= low[[0, 2]] - 5, axis=1) & np.all(ground[:, :, [0, 2]].min(1) <= high[[0, 2]] + 5, axis=1)
    ground = clipped_faces(ground[mask], [(0, low[0]-5, True), (0, high[0]+5, False), (2, low[2]-5, True), (2, high[2]+5, False)])
    doc.mkdir()
    colors = ['#abbcc8', '#d6815a', '#d6ae50', '#629c8e', '#9c81b8']
    def transform(tri):
        out = tri[:, :, [0, 2, 1]].copy()
        out[:, :, 0] -= center[0]
        out[:, :, 1] -= center[2]
        return out
    for clipped in [False, True]:
        fig = plt.figure(figsize=(16, 8), layout='constrained')
        for i, angle in enumerate([35, 215]):
            ax = fig.add_subplot(1, 2, i + 1, projection='3d')
            display_faces = [transform(ground)]
            display_colors = ['#d4cfba'] * len(ground)
            for model_index, (row, tri) in enumerate(models):
                color = colors[model_index % len(colors)]
                # Analysis view only: clip display facets at the view plane.
                # Complete original faces are shown in the separate full view.
                shown = clipped_faces(tri, [(1, a.base_height, False)]) if clipped else tri
                display_faces.append(transform(shown))
                display_colors.extend([color] * len(shown))
            # One collection sorts all terrain/building facets together.
            ax.add_collection3d(Poly3DCollection(np.concatenate(display_faces), facecolors=display_colors, edgecolor='none', alpha=1.))
            ax.set(xlim=(low[0]-center[0]-5, high[0]-center[0]+5), ylim=(low[2]-center[2]-5, high[2]-center[2]+5),
                   zlim=(min(low[1], float(ground[:, :, 1].min())), a.base_height if clipped else high[1]+2),
                   xlabel='Local east (m)', ylabel='Local viewer Z (m)', zlabel='HKPD height (m)')
            ax.set_box_aspect(tuple(hi-lo for lo,hi in [ax.get_xlim(), ax.get_ylim(), ax.get_zlim()]))
            ax.view_init(elev=24, azim=angle)
        fig.suptitle('Base diagnostic: view-only source clipping at '+str(a.base_height)+'m; original assets unchanged' if clipped else 'Complete unchanged government source assembly: all original faces')
        fig.savefig(doc / ('base-only-diagnostic.png' if clipped else 'complete-original-assembly.png'), dpi=160)
        plt.close(fig)
    result = dict(uids=[r['uid'] for r in sources], completeOriginalFaces=len(all_tri),
                  sourceSHA256ByUid={r['uid']: r['sourceSHA256'] for r in sources}, baseDiagnosticMaximumHeightM=a.base_height,
                  sourceGeometryChanges=0, installationApproved=False,
                  qualification='Complete original mesh diagram with exactly local terrain context and an explicitly clipped base-only view. Original assets, pose and scale unchanged. Images are source diagnostics, not browser/device, architectural-role, collision or support approval.')
    save(doc / 'summary.json', result)
    refs.append(HERE / 'exact_packed_world_geometry_20261009.py')
    module('assembly_context_plot_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        a.batch, 'original-assembly-and-labelled-partial-base-diagnostic-images', refs, result)


if __name__ == '__main__':
    main()
