"""Render exact source-wall/terrain evidence; never alter source geometry."""
import argparse
from pathlib import Path
import numpy as np
import shapely
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'attribution', 'runtime', 'uid']:
        parser.add_argument('--' + key, required=True)
    args = parser.parse_args()
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc = base / args.batch
    assert not doc.exists()
    refs = [Path(__file__)]
    def take(name, path):
        _, pins = authenticate(base / name)
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.extend([base / name / 'result.json', path])
        return read(path)
    context = take(args.attribution, base / args.attribution / 'context.json')
    g = next(r for r in take(args.runtime, HERE / 'local' / args.runtime / 'runtime-geometry.json.gz')['rows'] if r['uid'] == args.uid)
    assert context['sourceSHA256'] == g['sourceSHA256']
    tri = np.asarray(g['position']).reshape(-1, 3)[np.asarray(g['index']).reshape(-1, 3)]
    ground = np.asarray(g['drawnGroundGeometry']).reshape(-1, 3, 3)
    ids = [r['faceIndex'] for r in context['faces']]
    assert 0 < len(ids) <= 12
    for record in context['faces']:
        assert np.array_equal(tri[record['faceIndex']], np.asarray(record['vertices']))
    doc.mkdir(parents=True)
    centre = tri.mean((0, 1))
    low, high = tri.min((0, 1)), tri.max((0, 1))
    near = ground[(ground[:, :, 0].max(1) >= low[0]-5) & (ground[:, :, 0].min(1) <= high[0]+5) & (ground[:, :, 2].max(1) >= low[2]-5) & (ground[:, :, 2].min(1) <= high[2]+5)]
    def plotcoords(values):
        return (values-centre)[..., [0, 2, 1]]
    fig = plt.figure(figsize=(14, 9))
    ax = fig.add_subplot(111, projection='3d')
    ax.add_collection3d(Poly3DCollection(plotcoords(near), facecolor='#819377', edgecolor='none', alpha=.55))
    ax.add_collection3d(Poly3DCollection(plotcoords(tri), facecolor='#bec8cf', edgecolor='#5c6970', linewidth=.15, alpha=.8))
    ax.add_collection3d(Poly3DCollection(plotcoords(tri[ids]), facecolor='#e23a32', edgecolor='#771919', linewidth=1.1))
    points = np.asarray([r['position'] for r in context['samples']])
    pc = plotcoords(points)
    ax.scatter(pc[:, 0], pc[:, 1], pc[:, 2], color='#ffdd00', s=70, depthshade=False)
    allvalues = plotcoords(np.concatenate([tri, near]))
    ax.auto_scale_xyz(allvalues[:, :, 0].ravel(), allvalues[:, :, 1].ravel(), allvalues[:, :, 2].ravel())
    ranges = np.ptp(allvalues.reshape(-1, 3), axis=0)
    ax.set_box_aspect(ranges)
    ax.view_init(elev=27, azim=-125)
    ax.set(xlabel='Local east (m)', ylabel='Local viewer Z (m)', zlabel='Height relative to local origin (m)', title=f'{args.uid}: complete unchanged podium, red flagged faces, yellow sampled corner')
    fig.tight_layout()
    fig.savefig(doc / 'source-context.png', dpi=130)
    plt.close(fig)
    polys = shapely.polygons(ground[:, :, [0, 2]])
    valid = shapely.area(polys) > 1e-10
    ground, polys = ground[valid], polys[valid]
    helper = module('source_profile_sampler', HERE / 'xl-final-script-pass.py')
    fig, axes = plt.subplots(len(ids), 1, figsize=(12, 3.5*len(ids)), squeeze=False)
    measurements = []
    for index, faceid in enumerate(ids):
        face = tri[faceid]
        xz = face[:, [0, 2]]
        i, j = max(((i, j) for i in range(3) for j in range(i+1, 3)), key=lambda ij: np.linalg.norm(xz[ij[1]]-xz[ij[0]]))
        direction = xz[j]-xz[i]
        length = np.linalg.norm(direction)
        assert length > 0
        direction /= length
        projected = (xz-xz[i]) @ direction
        distance = np.linspace(projected.min(), projected.max(), 101)
        points = xz[i] + distance[:, None]*direction
        heights = helper.s.context.shared.samples(points, ground, shapely.STRtree(polys))
        assert np.isfinite(heights).all()
        ax = axes[index, 0]
        ax.fill(projected, face[:, 1], color='#e23a32', alpha=.35, label='Complete original source face')
        ax.plot(distance, heights, color='#3b683b', label='Actual rendered terrain')
        for sample in [r for r in context['samples'] if r['faceIndex'] == faceid]:
            d = (np.asarray(sample['position'])[[0, 2]]-xz[i]) @ direction
            ax.scatter([d], [sample['position'][1]], color='#9a140e', marker='x', s=70)
        ax.set(xlabel='Distance along original face (m)', ylabel='Height HKPD (m)', title=f'Face {faceid} — unchanged vertices and terrain profile; red cross is the failed sample')
        ax.legend(loc='best')
        ax.grid(alpha=.2)
        measurements.append(dict(faceIndex=faceid, vertices=face.tolist(), profileDistance=distance.tolist(), renderedTerrainHeight=heights.tolist()))
    fig.tight_layout()
    fig.savefig(doc / 'face-profiles.png', dpi=130)
    plt.close(fig)
    result = dict(uids=[args.uid], sourceSHA256=g['sourceSHA256'], faces=ids, installationApproved=False, physicalInterpretationAccepted=False, sourceGeometryChanges=0, scriptExternalAICalls=0)
    save(doc / 'profiles.json', dict(**result, measurements=measurements))
    refs.append(HERE / 'xl-final-script-pass.py')
    module('selected_context_plot_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'exact-selected-source-wall-context-plots', refs, result)


if __name__ == '__main__':
    main()
