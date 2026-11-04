"""Images only: complete unchanged original P/T2 positioned source context.

Context colours distinguish actors/nonzero edge bodies, not material or function.
This is not an actual runtime/browser test, support proof or current capture.
"""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT, HERE, read, save, digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BASE = ROOT / 'docs/astra-city/government-import'
DOC = BASE / 'xl-terrain-recovery-20261011-twin-regency-two-original-source-context-v1'
GRAPH = BASE / 'xl-terrain-recovery-20261011-twin-regency-tower2-podium-original-contact-census-v2'


def ref(path):
    return dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()))


def main():
    assert not DOC.exists()
    graph = read(GRAPH / 'diagnostic.json.gz')
    worlds = []
    refs = [ref(Path(__file__)), ref(GRAPH / 'diagnostic.json.gz'),
            ref(GRAPH / 'result.json'), ref(HERE / 'exact_packed_world_geometry_20261009.py')]
    for source in graph['completeSourceInputs']:
        asset = ROOT / source['asset']['path']
        assert ref(asset) == source['asset']
        worlds.append(decode_original_world_triangles(asset.read_bytes()))
        refs.append(ref(asset))
    tri = np.concatenate(worlds)
    assert len(tri) == 13519 and digest(tri.tobytes()) == graph['completeOriginalWorldSHA256']
    # A common XY plot translation affects display labels only, never inputs.
    origin = np.asarray([-13372., 0., -18269.])
    plot = (tri - origin)[:, :, [0, 2, 1]]
    colour = np.repeat(np.array([[.37, .58, .77, 1.]]), len(tri), axis=0)
    colour[13063:] = [.68, .56, .42, 1.]
    main = graph['bodies'][18]
    assert main['actorUID'] == 'landsd/222465:0' and len(main['globalOriginalFaces']) == 1550
    colour[main['globalOriginalFaces']] = [.34, .38, .43, 1.]
    DOC.mkdir(parents=True)
    images = []
    for azimuth, label in [(-58, 'south-east'), (118, 'north-west')]:
        fig = plt.figure(figsize=(19, 11), dpi=100)
        ax = fig.add_subplot(111, projection='3d', computed_zorder=True)
        ax.add_collection3d(Poly3DCollection(plot, facecolors=colour,
            edgecolors=(.16, .18, .21, .28), linewidths=.12, rasterized=True))
        low, high = plot.min(axis=(0, 1)), plot.max(axis=(0, 1))
        pad = (high - low) * .04
        ax.set_xlim(low[0] - pad[0], high[0] + pad[0])
        ax.set_ylim(low[1] - pad[1], high[1] + pad[1])
        ax.set_zlim(low[2] - pad[2], high[2] + pad[2])
        ax.set_box_aspect(high - low)
        ax.view_init(elev=19, azim=azimuth)
        ax.set_xlabel('X relative to common plot origin (m)')
        ax.set_ylabel('Z relative to common plot origin (m)')
        ax.set_zlabel('Original world Y (m)')
        ax.set_title('Twin Regency original Tower 2 + podium: all 13,519 source facets\n'
                     'Grey: T2 main edge body; blue: other T2 originals; brown: full podium')
        fig.text(.02, .025, 'Source-only context. No source pose change, root/mount/function or current acceptance. '
                 'Seven T2 zero facets remain in the input; no support credit.', fontsize=11)
        fig.subplots_adjust(left=.02, right=.97, bottom=.065, top=.90)
        path = DOC / ('complete-original-tower2-podium-' + label + '-1900x1100.png')
        fig.savefig(path, dpi=100); plt.close(fig); images.append(ref(path))
    assert all(ref(ROOT / p['path']) == p for p in refs)
    save(DOC / 'context.json', dict(uids=graph['uids'], completeOriginalFaces=13519,
        sourceWorldSHA256=graph['completeOriginalWorldSHA256'], commonDisplayOrigin=origin.tolist(),
        unchangedOriginalArrays=True, contextColoursNotOriginalMaterials=True,
        images=images, sourceOnly=True, currentAcceptance=False, noFunctionOrStructuralCredit=True,
        sourceGeometryChanges=0, newlyInstalled=0, evidenceRefs=refs))
    print(json.dumps(dict(images=images, sourceOnly=True, currentAcceptance=False)), flush=True)


if __name__ == '__main__': main()
