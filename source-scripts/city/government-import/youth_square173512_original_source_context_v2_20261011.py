"""DRAFT unwarped original-world context only; no feature identity/current proof."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT, read, save, digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
B = ROOT / 'docs/astra-city/government-import'
INPUT = B / 'government-xl-youth-square173512-original-body-extent-podium-contacts-v2-20261011'
DOC = B / 'government-xl-youth-square173512-original-source-context-v2-20261011'
def ref(p):
    return dict(path=str(p.relative_to(ROOT)), sha256=digest(p.read_bytes()))
def main():
    assert not DOC.exists()
    d = read(INPUT / 'diagnostic.json.gz')
    assert d['sourceOnly'] and not d['currentAcceptance']
    triangles = {}
    for uid, source in d['sources'].items():
        p = ROOT / source['path']
        assert ref(p) == source
        t = decode_original_world_triangles(p.read_bytes())
        assert t.shape == (d['completeFaces'][uid], 3, 3)
        assert digest(t.astype('<f8').tobytes()) == d['worldSHA256'][uid]
        triangles[uid] = t
    uid = d['uid']
    far = {r['originalFace'] for r in d['all286HistoricalGroupFarFaces']}
    allpoints = np.concatenate(list(triangles.values())).reshape(-1, 3)
    lo, hi = allpoints.min(0), allpoints.max(0)
    DOC.mkdir(parents=True)
    fig, ax = plt.subplots(figsize=(12, 10))
    for actor, t in triangles.items():
        colors = [('darkorange' if i in far else '#5f84a4') if actor == uid else 'magenta' for i in range(len(t))]
        ax.add_collection(PolyCollection(t[:, :, [0, 2]], facecolors=colors, edgecolors='none', alpha=.65))
    for actor, form in d['historicalTowerAndPodiumForms'].items():
        for ring in form['rings']:
            r = np.asarray(ring)
            ax.plot(r[:, 0], r[:, 1], 'k--', linewidth=.8)
    ax.set_xlim(lo[0] - 3, hi[0] + 3)
    ax.set_ylim(lo[2] - 3, hi[2] + 3)
    ax.set_aspect('equal')
    ax.set_xlabel('Unchanged source world X (m)')
    ax.set_ylabel('Unchanged source world Z (m)')
    ax.set_title('All13100 tower +22 podium originals; orange286 historical far faces\nDashed historical forms; magenta recorded podium; no architecture/support qualification')
    fig.savefig(DOC / 'complete-original-plan-1800x1500.png', dpi=150)
    plt.close(fig)
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    for actor, t in triangles.items():
        colors = [('darkorange' if i in far else '#5f84a4') if actor == uid else 'magenta' for i in range(len(t))]
        ax.add_collection3d(Poly3DCollection(t[:, :, [0, 2, 1]], facecolors=colors, edgecolors='none', alpha=.65))
    ax.set_xlim(lo[0], hi[0]); ax.set_ylim(lo[2], hi[2]); ax.set_zlim(lo[1], hi[1])
    ax.set_box_aspect((hi - lo)[[0, 2, 1]])
    ax.view_init(elev=25, azim=-60)
    ax.set_xlabel('World X'); ax.set_ylabel('World Z'); ax.set_zlabel('World Y')
    ax.set_title('Complete unchanged original source context; occlusion is not absence')
    fig.savefig(DOC / 'complete-original-3d-minus60-1800x1500.png', dpi=150)
    plt.close(fig)
    save(DOC / 'context.json', dict(sourceOnly=True, fullOriginalFaces=d['completeFaces'], unwarpedOriginalWorld=True, identityAccepted=False, currentAcceptance=False, qualification='Visual context only: no primary-plan correspondence, measured registration, attachment, root or physical clearance is established. All source faces drawn, occluded faces remain obligations.', evidenceRefs=[ref(Path(__file__)), ref(INPUT / 'diagnostic.json.gz')] + [ref(ROOT / s['path']) for s in d['sources'].values()], exportedImages=[ref(p) for p in sorted(DOC.glob('*.png'))]))
    print(json.dumps(dict(outputs=[str(p.relative_to(ROOT)) for p in sorted(DOC.glob('*.png'))], currentAcceptance=False)))
if __name__ == '__main__':
    main()
