"""Display every nonempty original/current BASIC contact locus, without approval."""
import argparse
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_assembly_context_plot_v3_20261023 import clipped_faces
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['batch', 'runtime', 'contacts', 'lease-file']:
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n for n in [args.batch, args.runtime, args.contacts])
    base = ROOT / 'docs/astra-city/government-import'
    out = base / args.batch
    assert not out.exists()
    lease = read(Path(args.lease_file))
    assert reservations.owns(lease)
    refs, pins = [Path(__file__), HERE / 'exact_packed_world_geometry_20261009.py', HERE / 'original_assembly_context_plot_v3_20261023.py'], {}

    def take(batch, name):
        if batch not in pins:
            pins[batch] = authenticate(base / batch)[1]
            refs.append(base / batch / 'result.json')
        path = base / batch / name
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selected = take(args.runtime, 'selection.json.gz')
    sources = {r['uid']: r for r in selected['rows']}
    geometry_path = HERE / 'local' / args.runtime / 'runtime-geometry.json.gz'
    assert digest(geometry_path.read_bytes()) == pins[args.runtime][str(geometry_path.relative_to(ROOT))]
    refs.append(geometry_path)
    ground = {r['uid']: np.asarray(r['drawnGroundGeometry']).reshape(-1, 3, 3) for r in read(geometry_path)['rows']}
    contacts = take(args.contacts, 'summary.json')
    basic = take(args.contacts, 'basic.json')
    meshes = {r['uid']: np.asarray(r['position']).reshape(-1, 3)[np.asarray(r['index']).reshape(-1, 3)] for r in basic['rows']}
    required = {'building:' + u for u in sources}
    required.update(('building:' if u.startswith('landsd/') else 'source-form:') + u for u in meshes)
    assert required <= set(lease['resources'])
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selected['manifestSHA256'] == pins[args.contacts][str(manifest.relative_to(ROOT))]
    refs.append(manifest)
    producer = HERE / 'selected_original_model_only_foreign_contacts_v3_20261024.py'
    assert digest(producer.read_bytes()) == pins[args.contacts][str(producer.relative_to(ROOT))]
    refs.append(producer)
    worlds = {}
    exports = []
    out.mkdir()
    for pair in contacts['rows']:
        row = next(r for r in pair['modes'] if r['mode'] == 'original')
        if not row['allFiniteContactPairs']:
            continue
        assert reservations.owns(lease)
        uid, other = pair['uid'], pair['foreignUid']
        if uid not in worlds:
            asset = ROOT / sources[uid]['candidate']['path']
            assert digest(asset.read_bytes()) == sources[uid]['sourceSHA256']
            refs.append(asset)
            worlds[uid] = decode_original_world_triangles(asset.read_bytes())
        source, foreign = worlds[uid], meshes[other]
        assert len(source) == row['completeSourceFaces'] and len(foreign) == row['completeForeignFaces']
        name = uid.split('/')[1] + '--' + other.split('/')[1] + '--original.json.gz'
        raw = take(args.contacts, name)
        assert raw['allPairsExamined'] and raw['sourceFacesOmitted'] == 0
        assert len(raw['contacts']) == row['allFiniteContactPairs']
        points = np.asarray([[float(v) for v in q] for c in raw['contacts'] for q in c['exactPoints']])
        assert points.ndim == 2 and points.shape[1] == 3 and np.isfinite(points).all()
        lo, hi = points.min(0) - [2, 1, 2], points.max(0) + [2, 3, 2]
        planes = [(axis, float(lo[axis]), True) for axis in range(3)] + [(axis, float(hi[axis]), False) for axis in range(3)]
        size = np.maximum((hi - lo)[[0, 2, 1]], .1)
        fig = plt.figure(figsize=(15, 7), layout='constrained')
        for k, angle in enumerate([35, 215]):
            ax = fig.add_subplot(1, 2, k + 1, projection='3d')
            for tri, color in [(source, '#d04729'), (foreign, '#2368b6')]:
                keep = np.all(tri.max(1) >= lo, axis=1) & np.all(tri.min(1) <= hi, axis=1)
                polys = clipped_faces(tri[keep], planes)
                if len(polys):
                    ax.add_collection3d(Poly3DCollection((polys - lo)[:, :, [0, 2, 1]], facecolors=color, edgecolors=color, alpha=.3, linewidth=.3))
            tri = ground[uid]
            keep = np.all(tri.max(1) >= lo, axis=1) & np.all(tri.min(1) <= hi, axis=1)
            polys = clipped_faces(tri[keep], planes)
            if len(polys):
                ax.add_collection3d(Line3DCollection([np.vstack([v, v[:1]]) for v in (polys - lo)[:, :, [0, 2, 1]]], colors='#16834a', linewidth=.5))
            dots = (points - lo)[:, [0, 2, 1]]
            ax.scatter(dots[:, 0], dots[:, 1], dots[:, 2], color='#171717', s=3)
            ax.set(xlim=(0, size[0]), ylim=(0, size[1]), zlim=(0, size[2]), xlabel='X offset m', ylabel='Z offset m', zlabel='HKPD offset m')
            ax.set_box_aspect(size.copy())
            ax.view_init(24, angle)
        coimport = other in sources
        fig.suptitle(f'{uid} / {other}: complete original contact locus\nRed original; blue current BASIC; green drawn terrain; black saved contacts. Co-import BASIC peer: {coimport}. Diagnostic crop only.', fontsize=11)
        path = out / (uid.split('/')[1].replace(':', '-') + '--' + other.split('/')[1].replace(':', '-') + '.png')
        fig.savefig(path, dpi=140)
        plt.close(fig)
        refs.append(path)
        exports.append(dict(uid=uid, foreignUid=other, image=dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())), contactCount=len(raw['contacts']), coimportBasicPeer=coimport, sourceWorldSHA256=digest(source.astype('<f8').tobytes()), foreignWorldSHA256=digest(foreign.astype('<f8').tobytes()), contactBounds=[points.min(0).tolist(), points.max(0).tolist()]))
        print(dict(uid=uid, foreignUid=other, contacts=len(raw['contacts'])), flush=True)
    assert len(exports) == sum(next(r for r in p['modes'] if r['mode'] == 'original')['allFiniteContactPairs'] > 0 for p in contacts['rows'])
    for bound in pins.values():
        for name, sha in bound.items():
            assert digest((ROOT / name).read_bytes()) == sha
    assert reservations.owns(lease)
    result = dict(uids=list(sources), exports=exports, allNonemptyOriginalBasicPairsDisplayed=True, sourceGeometryChanges=0, physicalAcceptance=False, visualAcceptance=False, installationApproved=False, publication=False, qualification='Every saved nonempty original/BASIC finite-contact pair is displayed with both complete meshes cropped around its entire contact bounds. Co-import BASIC peers stay explicitly labelled. No production geometry hidden/changed, no architectural-role, suppression, contact, native support, browser or publication acceptance.')
    save(out / 'summary.json', result)
    module('original_basic_junction_view_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'complete-original-current-basic-junction-visual-context-no-approval', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
