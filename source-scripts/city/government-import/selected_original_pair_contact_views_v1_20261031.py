"""Show complete saved original-pair junctions; crops are diagrams only."""
import argparse
import sys
import uuid
from fractions import Fraction
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_assembly_context_plot_v3_20261023 import clipped_faces
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch', required=True)
    parser.add_argument('--selection', required=True)
    parser.add_argument('--contacts', action='append', required=True)
    parser.add_argument('--lease')
    args = parser.parse_args()
    names = [args.batch, args.selection, *args.contacts]
    assert all(n.startswith('government-xl-') and '/' not in n for n in names)
    base = ROOT / 'docs/astra-city/government-import'
    out, local = base / args.batch, HERE / 'local' / args.batch
    assert not out.exists()
    receipts, pins, refs = {}, {}, [Path(__file__)]

    def take(batch, name):
        if batch not in pins:
            receipts[batch], pins[batch] = authenticate(base / batch)
            refs.append(base / batch / 'result.json')
        path = base / batch / name
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    pairs = {batch: take(batch, 'summary.json') for batch in args.contacts}
    uids = sorted({u for pair in pairs.values() for u in pair['uids']})
    if not args.lease:
        assert not local.exists()
        claim = reservations.claim('original-pair-views-' + str(uuid.uuid4()),
                                   ['building:' + u for u in uids], batch=args.batch, ttl=3600)
        assert claim['ok'], claim
        return execute_reserved(claim['reservation'], local / 'reservation.json',
                                [sys.executable, __file__, *sys.argv[1:],
                                 '--lease', str(local / 'reservation.json')])
    lease = read(Path(args.lease))
    assert reservations.owns(lease) and {'building:' + u for u in uids} <= set(lease['resources'])
    selection = take(args.selection, 'selection.json.gz')
    sources = {r['uid']: r for r in selection['rows']}
    triangles = {}
    for uid in uids:
        source = sources[uid]
        asset = ROOT / source['candidate']['path']
        assert digest(asset.read_bytes()) == source['sourceSHA256']
        refs.append(asset)
        triangles[uid] = decode_original_world_triangles(asset.read_bytes())
        assert len(triangles[uid]) == source['triangles']
    exports = []
    for batch, pair in pairs.items():
        left, right = pair['uids']
        assert pair['sourceSHA256ByUid'] == {u: sources[u]['sourceSHA256'] for u in pair['uids']}
        original = next(r for r in pair['rows'] if r['mode'] == 'original')
        assert original['sourceWorldSHA256ByUid'] == {u: digest(triangles[u].tobytes()) for u in pair['uids']}
        raw = take(batch, 'original.json.gz')
        assert raw['allPairsExamined'] and raw['sourceFacesOmitted'] == 0
        assert len(raw['contacts']) == original['finiteContactPairs']
        points = np.asarray([[float(Fraction(v)) for v in p]
                             for c in raw['contacts'] for p in c['exactPoints']])
        assert len(points)
        lo, hi = points.min(0) - [2, 1, 2], points.max(0) + [2, 2, 2]
        planes = [(axis, float(lo[axis]), True) for axis in range(3)]
        planes += [(axis, float(hi[axis]), False) for axis in range(3)]
        surfaces = [clipped_faces(triangles[u], planes) for u in [left, right]]
        size = np.maximum((hi - lo)[[0, 2, 1]], .1)
        fig = plt.figure(figsize=(15, 7), layout='constrained')
        for index, azimuth in enumerate([35, 215]):
            ax = fig.add_subplot(1, 2, index + 1, projection='3d')
            for faces, colour in zip(surfaces, ['#c54e36', '#286cb5']):
                if len(faces):
                    ax.add_collection3d(Poly3DCollection((faces - lo)[:, :, [0, 2, 1]],
                        facecolors=colour, edgecolors=colour, alpha=.4, linewidth=.35))
            for contact in raw['contacts']:
                vertices = np.asarray([[float(Fraction(v)) for v in p] for p in contact['exactPoints']])
                vertices = (vertices - lo)[:, [0, 2, 1]]
                ax.plot(*vertices.T, color='#8c00a5', linewidth=1.8, marker='.' if contact['dimension'] == 0 else None)
            ax.set(xlim=(0, size[0]), ylim=(0, size[1]), zlim=(0, size[2]),
                   xlabel='East offset (m)', ylabel='Z offset (m)', zlabel='HKPD offset (m)')
            ax.set_box_aspect(size)
            ax.view_init(25, azimuth)
        fig.suptitle(left + ' (red) / ' + right + ' (blue)\n'
                     'All exact original contacts in purple; diagram-only crop. No acceptance.')
        path = out / (right.split('/')[1].replace(':', '-') + '-junction.png')
        out.mkdir(exist_ok=True)
        fig.savefig(path, dpi=150)
        plt.close(fig)
        refs.append(path)
        exports.append(dict(left=left, right=right, originalContactCount=len(raw['contacts']),
                            displayBounds=[lo.tolist(), hi.tolist()],
                            image=dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()))))
        assert reservations.owns(lease)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256']
    result = dict(uids=uids, exports=exports, allSavedOriginalContactsDisplayed=True,
                  sourceGeometryChanges=0, sourcePoseChanges=0, physicalAcceptance=False,
                  identityAccepted=False, visualAcceptance=False, installationApproved=False,
                  qualification='Complete immutable original sources clipped only for display around every saved exact contact. All raw point/line/area contact witnesses displayed. No assets, normals, poses, terrain, contact thresholds or acceptance rules changed.')
    save(out / 'summary.json', result)
    refs.extend([manifest, HERE / 'exact_packed_world_geometry_20261009.py',
                 HERE / 'original_assembly_context_plot_v3_20261023.py'])
    module('selected_pair_contact_views_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        args.batch, 'complete-saved-original-pair-junction-views', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
