"""Plot authenticated negative original walls and their actual native floor roots."""
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for k in ['batch', 'runtime', 'wall-paths', 'uid']:
        parser.add_argument('--' + k, required=True)
    args = parser.parse_args()
    base = ROOT / 'docs/astra-city/government-import'
    out = base / args.batch
    assert args.batch.startswith('government-xl-') and '/' not in args.batch and not out.exists()
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
    summary = take(args.wall_paths, 'summary.json')
    detail = take(args.wall_paths, 'original.json.gz')
    asset = ROOT / row['candidate']['path']
    assert digest(asset.read_bytes()) == row['sourceSHA256'] == summary['sourceSHA256ByUid'][args.uid]
    refs.append(asset)
    tri = decode_original_world_triangles(asset.read_bytes())
    assert digest(tri.tobytes()) == detail['sourceWorldSHA256']
    ids = detail['rawCapProof']['negativeSourceFaces']
    assert len(ids) == len(set(ids)) == len(detail['rows']) and not detail['excludedNonWallFaces']
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256'] == summary['currentManifestSHA256']
    refs.append(manifest)
    n = len(ids)
    fig = plt.figure(figsize=(16, 3.8 * ((n + 4) // 5)), layout='constrained')
    records = []
    for k, (face_id, path) in enumerate(zip(ids, detail['rows'])):
        face = tri[face_id]
        assert face_id in path['incidentFaces']
        assert path['hasUnrestrictedFiniteAttachment'] and path['passesExistingEndpointHeight']
        assert path['terminal']['kind'] == 'canonical-strict-vertical-support-anchor'
        root = path['terminal']['strictRoot']
        assert root['strictAccepted'] and -.1 <= root['gap'] <= 1
        floor = np.asarray(root['provider']['vertices'])
        points = np.asarray(path['continuousPath'])
        center = face.mean(0)
        # Matplotlib Z is vertical; source Y remains the unchanged HKPD height.
        xyz = lambda t: (np.asarray(t) - center)[..., [0, 2, 1]]
        ax = fig.add_subplot((n + 4) // 5, 5, k + 1, projection='3d')
        ax.add_collection3d(Poly3DCollection([xyz(floor)], facecolors='#70b5a4', edgecolors='#245e52', alpha=.55))
        ax.add_collection3d(Poly3DCollection([xyz(face)], facecolors='#d6667a', edgecolors='#752232', alpha=.8))
        v = xyz(points)
        ax.plot(v[:, 0], v[:, 1], v[:, 2], color='#224eb8', marker='o', markersize=2)
        bounds = xyz(np.concatenate([face, floor, points]))
        low, high = bounds.min(0), bounds.max(0)
        span = np.maximum(high - low, .5)
        for setter, lo, hi, d in zip([ax.set_xlim, ax.set_ylim, ax.set_zlim], low, high, span):
            setter(lo - .12 * d, hi + .12 * d)
        ax.set_box_aspect(span)
        ax.view_init(elev=24, azim=-55)
        ax.set_title(f'Face {face_id}; floor {root["provider"]["faceIndex"]}\nwall {face[:,1].min():.3f}–{face[:,1].max():.3f} HKPD', fontsize=9)
        ax.tick_params(labelsize=6)
        normal = np.cross(face[1] - face[0], face[2] - face[0])
        records.append(dict(faceIndex=face_id, originalFaceVertices=face.tolist(),
                            verticalNormalFraction=abs(float(normal[1])) / float(np.linalg.norm(normal)),
                            originalWallAreaM2=float(np.linalg.norm(normal) / 2),
                            minimumHKPD=float(face[:, 1].min()), maximumHKPD=float(face[:, 1].max()),
                            actualNativeRoot=root, maximumPathResidualM=path['maximumResidualM'],
                            riseAboveEndpointsM=path['riseAboveEndpointsM']))
    out.mkdir()
    fig.suptitle('Original walls (red), authentic native floor-root facets (green), saved finite paths (blue)', fontsize=12)
    fig.savefig(out / 'negative-wall-native-floor-roots.png', dpi=150)
    plt.close(fig)
    result = dict(uids=summary['uids'], targetUid=args.uid, sourceSHA256ByUid=summary['sourceSHA256ByUid'],
                  rows=records, sourceGeometryChanges=0, sourcePoseChanges=0, installationApproved=False,
                  physicalAcceptance=False, publication=False,
                  qualification='Every original negative wall and authenticated native floor-root facet shown unchanged in local diagnostic coordinates. Display axis permutation/centering is for plotting only. The complete source, compound negatives and failed roof-cap verdicts remain untouched. This image is evidence for a separate bounded role review, not approval.')
    save(out / 'summary.json', result)
    refs.append(HERE / 'exact_packed_world_geometry_20261009.py')
    module('native_wall_views_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'original-negative-wall-and-authentic-native-floor-root-views', refs, result)


if __name__ == '__main__':
    main()
