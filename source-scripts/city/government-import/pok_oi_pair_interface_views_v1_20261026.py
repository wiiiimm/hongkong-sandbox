"""Show all exact hospital/podium contact loci with unchanged lower source context."""
from pathlib import Path
from fractions import Fraction
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_assembly_context_plot_v3_20261023 import clipped_faces


def main():
    base = ROOT / 'docs/astra-city/government-import'
    prefix = 'government-xl-after-ying-hoi-pok-oi-'
    batch = prefix + 'pair-interface-views-v1-20261026'
    runtime, contacts = prefix + 'pair-bound-ground-v1-20261026', prefix + 'pair-contacts-v1-20261026'
    out = base / batch
    assert not out.exists()
    refs, pins = [Path(__file__)], {}
    def take(n, filename):
        if n not in pins:
            pins[n] = authenticate(base / n)[1]; refs.append(base / n / 'result.json')
        p = base / n / filename
        assert digest(p.read_bytes()) == pins[n][str(p.relative_to(ROOT))]
        refs.append(p); return read(p)
    selection = take(runtime, 'selection.json.gz')
    summary = take(contacts, 'summary.json')
    raw = take(contacts, 'original.json.gz')
    assert raw['allPairsExamined'] and not raw['sourceFacesOmitted']
    meshes = []
    for uid in summary['uids']:
        row = next(r for r in selection['rows'] if r['uid'] == uid)
        asset = ROOT / row['candidate']['path']
        assert digest(asset.read_bytes()) == row['sourceSHA256'] == summary['sourceSHA256ByUid'][uid]
        refs.append(asset); meshes.append(decode_original_world_triangles(asset.read_bytes()))
    points = [np.asarray([[float(Fraction(x)) for x in q] for q in c['exactPoints']]) for c in raw['contacts'] if c['dimension'] > 0]
    joined = np.concatenate(points)
    lo, hi = joined.min(0) - [3, 2, 3], joined.max(0) + [3, 3, 3]
    center = (lo + hi) / 2
    planes = [(axis, value, lower) for axis in range(3) for value, lower in [(lo[axis], True), (hi[axis], False)]]
    transform = lambda t: (np.asarray(t) - center)[..., [0, 2, 1]]
    shown = [clipped_faces(t, planes) for t in meshes]
    fig = plt.figure(figsize=(17, 8), layout='constrained')
    for k, angle in enumerate([35, 215]):
        ax = fig.add_subplot(1, 2, k + 1, projection='3d')
        for t, color in zip(shown, ['#d5a149', '#78a6bf']):
            ax.add_collection3d(Poly3DCollection(transform(t), facecolors=color, edgecolors='#52616b', alpha=.45, linewidth=.2))
        ax.add_collection3d(Line3DCollection([transform(p) for p in points], colors='#bf1730', linewidths=1.5), autolim=False)
        bound = transform(np.array([lo, hi]))
        ax.set(xlim=bound[:, 0], ylim=bound[:, 1], zlim=bound[:, 2], xlabel='east offset m', ylabel='viewer Z offset m', zlabel='height offset m')
        ax.set_box_aspect((bound[1] - bound[0]).copy()); ax.view_init(24, angle)
    fig.suptitle('Pok Oi original hospital gold / original podium blue / all 238 exact contacts red\nLower-source display crop only. No geometry changes or physical approval.')
    out.mkdir(); image = out / 'all-original-pair-contacts.png'
    fig.savefig(image, dpi=140); plt.close(fig)
    result = dict(uids=summary['uids'], sourceSHA256ByUid=summary['sourceSHA256ByUid'],
                  completeContactLociShown=len(points), contactBounds=[joined.min(0).tolist(), joined.max(0).tolist()],
                  displayBounds=[lo.tolist(), hi.tolist()], image=str(image.relative_to(ROOT)), imageSHA256=digest(image.read_bytes()),
                  sourceGeometryChanges=0, physicalAcceptance=False, installationApproved=False, publication=False)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256']
    refs.extend([manifest, HERE / 'original_assembly_context_plot_v3_20261023.py', HERE / 'exact_packed_world_geometry_20261009.py'])
    save(out / 'summary.json', result)
    module('pok_oi_pair_views_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        batch, 'complete-original-pair-contact-loci-lower-source-context-views', refs, result)


if __name__ == '__main__':
    main()
