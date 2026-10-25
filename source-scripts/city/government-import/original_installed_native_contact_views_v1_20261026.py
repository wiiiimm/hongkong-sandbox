"""Plot every saved source/native contact; cropping affects diagrams only."""
import argparse
from collections import Counter
from fractions import Fraction
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
from original_assembly_context_plot_v3_20261023 import clipped_faces
from exact_contact_role_context_v1_20261023 import contact_role
from exact_original_shell_intersections_20261009 import rational_face as qtriangle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'runtime', 'contacts', 'uid']:
        parser.add_argument('--' + key, required=True)
    parser.add_argument('--native', action='append', required=True)
    args = parser.parse_args()
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    assert len(args.native) == len(set(args.native)) and args.uid not in args.native
    base = ROOT / 'docs/astra-city/government-import'
    out = base / args.batch
    assert not out.exists()
    refs, pins = [Path(__file__)], {}
    def take(batch, name):
        if batch not in pins:
            pins[batch] = authenticate(base / batch)[1]
            refs.append(base / batch / 'result.json')
        path = base / batch / name
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    selection = take(args.runtime, 'selection.json.gz')
    row = next(r for r in selection['rows'] if r['uid'] == args.uid)
    asset = ROOT / row['candidate']['path']
    assert digest(asset.read_bytes()) == row['sourceSHA256']
    refs.append(asset)
    source = decode_original_world_triangles(asset.read_bytes())
    assert len(source) == row['triangles']
    summary = take(args.contacts, 'summary.json')
    archived = take(args.contacts, 'native-input.json.gz')
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256']
    refs.append(manifest)
    out.mkdir()
    results = []
    for uid in args.native:
        pair = next(r for r in summary['rows'] if r['uid'] == args.uid and r['nativeUid'] == uid)
        entry = next(r for r in archived['rows'] if r['uid'] == uid)
        catalogue = ROOT / entry['cataloguePath']
        current = next(r for r in read(catalogue)['models'] if r['uid'] == uid)
        assert current == entry['entry'] == pair['rawCurrentNativeEntry']
        native_asset = ROOT / entry['path']
        assert native_asset == catalogue.parent / current['asset']
        assert digest(native_asset.read_bytes()) == current['sha256'] == pair['nativeSHA256']
        refs.extend([catalogue, native_asset])
        native = decode_original_world_triangles(native_asset.read_bytes())
        raw = take(args.contacts, args.uid.split('/')[1] + '--' + uid.split('/')[1] + '--original.json.gz')
        assert raw['allPairsExamined'] and raw['sourceFacesOmitted'] == 0
        mode = next(m for m in pair['modes'] if m['mode'] == 'original')
        assert len(raw['contacts']) == mode['finiteContactPairs']
        roles, points = Counter(), []
        for contact in raw['contacts']:
            coordinates = [tuple(Fraction(v) for v in p) for p in contact['exactPoints']]
            role = contact_role(qtriangle(source[contact['sourceFaceA']]), qtriangle(native[contact['sourceFaceB']]), coordinates,
                                contact['dimension'], [contact['sourcePrimitiveDimensionA'], contact['sourcePrimitiveDimensionB']])
            roles[role] += 1
            points.append(np.asarray([[float(v) for v in p] for p in coordinates]))
        assert points
        joined = np.concatenate(points)
        lo, hi = source.min((0, 1)) - [3, 2, 3], source.max((0, 1)) + [3, 2, 3]
        planes = [(axis, value, lower) for axis in range(3) for value, lower in [(lo[axis], True), (hi[axis], False)]]
        shown = clipped_faces(native, planes)
        centre = (lo + hi) / 2
        def transform(v):
            return (v - centre)[..., [0, 2, 1]]
        fig = plt.figure(figsize=(16, 8), layout='constrained')
        for number, azimuth in enumerate([35, 215]):
            ax = fig.add_subplot(1, 2, number + 1, projection='3d')
            for mesh, colour in [(shown, '#9cb4c3'), (source, '#d7a04d')]:
                ax.add_collection3d(Poly3DCollection(transform(mesh), facecolors=colour, edgecolor='none', alpha=.7))
            lines = [transform(p) for p in points if len(p) > 1]
            ax.add_collection3d(Line3DCollection(lines, colors='red', linewidths=2))
            bounds = transform(np.asarray([lo, hi]))
            ax.set(xlim=bounds[:, 0], ylim=bounds[:, 1], zlim=bounds[:, 2], xlabel='East offset', ylabel='Viewer Z offset', zlabel='Height offset')
            ax.set_box_aspect(bounds[1] - bounds[0]); ax.view_init(elev=25, azim=azimuth)
        fig.suptitle(f'{args.uid} gold / unchanged native {uid} blue / all exact original contacts red\nDiagram crop only; no source changes or acceptance')
        image_path = out / (uid.split('/')[1] + '-native-contact-context.png')
        fig.savefig(image_path, dpi=130); plt.close(fig)
        results.append(dict(uid=args.uid, nativeUid=uid, sourceSHA256=row['sourceSHA256'], nativeSHA256=current['sha256'],
                            completeSourceFaces=len(source), completeNativeFaces=len(native), contactCount=len(points),
                            roles=dict(roles), contactBounds=[joined.min(0).tolist(), joined.max(0).tolist()],
                            rawFourModeCounts=pair['modes'], rawCurrentNativeEntry=current, diagramBounds=[lo.tolist(), hi.tolist()],
                            image=str(image_path.relative_to(ROOT))))
    result = dict(uids=[args.uid], rows=results, sourceGeometryChanges=0, nativeMetadataChanges=0,
                  installationApproved=False, physicalAcceptance=False, visualAcceptance=False,
                  qualification='All original contact points are shown against the complete unchanged source and explicitly cropped current native context. All four-mode counts and original metadata retained. This is not ownership, source-role, physical or installation approval.')
    save(out / 'summary.json', result)
    refs.extend(HERE / n for n in ['exact_packed_world_geometry_20261009.py', 'exact_contact_role_context_v1_20261023.py',
                                  'original_assembly_context_plot_v3_20261023.py', 'exact_original_shell_intersections_20261009.py'])
    module('native_views_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        args.batch, 'complete-original-installed-native-contact-context-views', refs, result)


if __name__ == '__main__':
    main()
