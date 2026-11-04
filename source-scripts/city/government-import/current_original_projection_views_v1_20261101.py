"""Plot complete original geometry beside exact current identity nominations."""
import argparse, sys, uuid
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

def main():
    p = argparse.ArgumentParser(description=__doc__)
    for f in ['batch', 'capture', 'identity', 'uid']: p.add_argument('--' + f, required=True)
    p.add_argument('--owned', action='store_true')
    a = p.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n for n in [a.batch, a.capture, a.identity])
    base = ROOT / 'docs/astra-city/government-import'
    out, local = base / a.batch, HERE / 'local' / a.batch
    assert not out.exists()
    if not a.owned:
        assert not local.exists()
        c = reservations.claim('original-identity-views-' + str(uuid.uuid4()), ['building:' + a.uid], batch=a.batch, ttl=1800)
        assert c['ok'], c
        return execute_reserved(c['reservation'], local / 'reservation.json', [sys.executable, __file__, *sys.argv[1:], '--owned'])
    lease = read(local / 'reservation.json')
    assert reservations.owns(lease)
    refs, pins = [Path(__file__)], {}
    def take(batch, name):
        if batch not in pins:
            pins[batch] = authenticate(base / batch)[1]
            refs.append(base / batch / 'result.json')
        f = base / batch / name
        assert digest(f.read_bytes()) == pins[batch][str(f.relative_to(ROOT))]
        refs.append(f)
        return read(f)
    selection = take(a.capture, 'selection.json.gz')
    row = next(r for r in selection['rows'] if r['uid'] == a.uid)
    subdir = a.uid.split('/')[1]
    raw = take(a.identity, subdir + '/identity.json')
    context = take(a.identity, subdir + '/context.json')['identity']
    asset = ROOT / row['candidate']['path']
    assert digest(asset.read_bytes()) == row['sourceSHA256'] == raw['sourceSHA256']
    tri = decode_original_world_triangles(asset.read_bytes())
    assert digest(tri.astype('<f8').tobytes()) == raw['worldTrianglesSHA256']
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    start = digest(manifest.read_bytes())
    assert start == selection['manifestSHA256'] == raw['exactRouteManifestSHA256']
    refs.extend([asset, manifest])
    current = []
    for nomination in context['intersectingForms']:
        path = ROOT / '3d-viewer' / nomination['tile']
        form = next(f for f in read(path)['buildings'] if f['uid'] == nomination['uid'])
        assert digest(path.read_bytes()) == raw['exactRouteTileHashes'][nomination['tile']]
        refs.append(path)
        current.append((nomination, form))
    fig = plt.figure(figsize=(18, 6), layout='constrained')
    ax = fig.add_subplot(1, 3, 1)
    ax.add_collection(PolyCollection(tri[:, :, [0, 2]], facecolors='#b7d2e5', edgecolors='none', alpha=.7))
    for nomination, form in current:
        color = '#171b22' if form['uid'] == a.uid else '#267947' if nomination['sameParent'] else '#af2438'
        for ring in form['rings']:
            xy = np.asarray(ring)
            ax.plot(xy[:, 0], xy[:, 1], color=color, linewidth=1.2)
        xy = np.asarray(form['rings'][0])
        ax.text(*xy.mean(0), form['uid'].split('/')[1], fontsize=7, color=color)
    ax.autoscale()
    ax.set_aspect('equal')
    ax.set_title('Complete source projection / current forms\nTarget black; same-parent green; unrelated red')
    ax.set(xlabel='World X m', ylabel='World Z m')
    ax.grid(alpha=.2)
    lo, hi = tri.min((0, 1)), tri.max((0, 1))
    size = np.maximum((hi - lo)[[0, 2, 1]], .1)
    for i, angle in enumerate([35, 215]):
        ax = fig.add_subplot(1, 3, i + 2, projection='3d')
        ax.add_collection3d(Poly3DCollection((tri - lo)[:, :, [0, 2, 1]], facecolors='#a5bdcd', edgecolors='#476578', linewidth=.12))
        ax.set(xlim=(0, size[0]), ylim=(0, size[1]), zlim=(0, size[2]), xlabel='X offset m', ylabel='Z offset m', zlabel='Y offset m')
        ax.set_box_aspect(size.copy())
        ax.view_init(elev=25, azim=angle)
        ax.set_title('Every original source face')
    fig.suptitle(a.uid + ' / ' + row['modelId'] + '\nUnchanged source/pose; extent and context only, no identity or physical acceptance')
    image = out / 'complete-original-current-projection.png'
    image.parent.mkdir(parents=True)
    fig.savefig(image, dpi=140)
    plt.close(fig)
    result = dict(uids=[a.uid], sourceSHA256=row['sourceSHA256'], completeSourceFaces=len(tri), currentManifestSHA256=start,
        originalWorldSHA256=raw['worldTrianglesSHA256'], currentFormUIDs=[r['uid'] for r, _ in current],
        sourceGeometryChanges=0, sourcePoseChanges=0, identityAccepted=False, physicalAcceptance=False,
        installationApproved=False, publication=False, image=dict(path=str(image.relative_to(ROOT)), sha256=digest(image.read_bytes()), dimensions=[2520, 840]))
    save(out / 'summary.json', result)
    assert reservations.owns(lease) and digest(manifest.read_bytes()) == start
    refs.extend([image, HERE / 'exact_packed_world_geometry_20261009.py'])
    module('original_projection_view_freezer', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'complete-original-current-projection-context-views', list(dict.fromkeys(refs)), result)

if __name__ == '__main__': main()
