"""Plot authenticated compound-clearance negatives without granting acceptance."""
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'compound', 'support-binding']:
        parser.add_argument('--' + key, required=True)
    args = parser.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n
               for n in [args.batch, args.compound, args.support_binding])
    base = ROOT / 'docs/astra-city/government-import'
    out = base / args.batch
    assert not out.exists()
    refs = [Path(__file__)]
    pins = {}
    for name in [args.compound, args.support_binding]:
        receipt, bound = authenticate(base / name)
        pins[name] = bound
        refs.append(base / name / 'result.json')
    def take(name, filename):
        path = base / name / filename
        assert digest(path.read_bytes()) == pins[name][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    compound = read(base / args.compound / 'result.json')
    binding = take(args.support_binding, 'summary.json')
    assert compound['supportedUid'] == binding['supportedUid']
    assert compound['supportUid'] == binding['installedSupportUid']
    negatives = take(args.compound, 'original.json.gz')
    caps = take(args.compound, 'original-cap-paths.json.gz')
    inp = take(args.support_binding, 'original/input.json.gz')
    child = inp['rows'][0]
    assert child['uid'] == compound['supportedUid']
    tri = np.asarray(child['position'], dtype='<f8').reshape(-1, 3)[np.asarray(child['index']).reshape(-1, 3)]
    support = np.asarray(inp['podium'], dtype='<f8')
    assert digest(tri.tobytes()) == negatives['sourceWorldSHA256']
    assert digest(support.tobytes()) == caps['supportWorldSHA256']
    assert len(tri) == negatives['completeSourceFaces']
    # Recover the exact compound prefix length from the bound compound hash.
    # The runtime ground is explicitly pinned by the producing receipt.
    ground_paths = [ROOT / p for p in pins[args.compound]
                    if p.endswith('/runtime-geometry.json.gz')]
    assert len(ground_paths) == 1
    runtime = read(ground_paths[0]); refs.append(ground_paths[0])
    g = next(r for r in runtime['rows'] if r['uid'] == child['uid'])
    ground = np.asarray(g['drawnGroundGeometry'], dtype='<f8').reshape(-1, 3, 3)
    assert digest(np.concatenate([ground, support]).tobytes()) == negatives['groundSHA256']
    ground_count = len(ground)
    wanted = caps['proof']['negativeNonWallFaces']
    assert wanted
    out.mkdir(parents=True)
    rows = []
    for face_id in wanted:
        row = next(r for r in negatives['rows'] if r['sourceFace'] == face_id)
        face = tri[face_id]
        assert np.array_equal(face, row['vertices'])
        contacts = row['negativeGroundPairProofs']
        native_ids = sorted({r['groundFace'] - ground_count for r in contacts
                             if r['groundFace'] >= ground_count})
        native = support[native_ids]
        extent = [face[:, 1].min(), face[:, 1].max()]
        rows.append(dict(sourceFace=face_id, sourceVertices=face.tolist(),
                         areaM2=float(np.linalg.norm(np.cross(face[1]-face[0], face[2]-face[0])) / 2),
                         heightHKPD=extent, minimumFiniteGapM=row['minimumFiniteGapM'],
                         nativeNegativeProviderFaces=native_ids,
                         terrainNegativeProviderFaces=[r['groundFace'] for r in contacts if r['groundFace'] < ground_count],
                         nondegenerate=bool(np.linalg.norm(np.cross(face[1]-face[0], face[2]-face[0]))),
                         physicalAcceptance=False))
        centre = face.mean(0)
        fig = plt.figure(figsize=(12, 6))
        for j, azimuth in enumerate([-120, 55]):
            ax = fig.add_subplot(1, 2, j+1, projection='3d')
            for values, colour in [(native, (0.2, 0.5, 0.8, 0.3)), (face[None], (0.95, 0.25, 0.1, 1))]:
                if not len(values):
                    continue
                local = (values-centre)[:, :, [0, 2, 1]]
                ax.add_collection3d(Poly3DCollection(local, facecolors=colour, edgecolor='grey', linewidth=.2))
            vertices = np.concatenate([face[None], native]).reshape(-1, 3) - centre
            ax.auto_scale_xyz(vertices[:, 0], vertices[:, 2], vertices[:, 1])
            ax.set(xlabel='East offset (m)', ylabel='Viewer Z offset (m)', zlabel='Height offset (m)')
            ax.view_init(elev=25, azim=azimuth)
        fig.suptitle(f'{child["uid"]} original face {face_id}: red source / blue exact native negative providers')
        fig.tight_layout(); fig.savefig(out / f'face-{face_id}.png', dpi=130); plt.close(fig)
    result = dict(uids=[child['uid'], compound['supportUid']], rows=rows,
                  allNegativeNonWallFacesAccountedFor=True, sourceGeometryChanges=0,
                  sourcePoseChanges=0, physicalAcceptance=False, installationApproved=False,
                  publication=False, newlyInstalled=0, scriptExternalAICalls=0,
                  qualification='Every raw original non-wall negative is retained with its exact source facet and compound-provider indices. Diagrams are evidence only; no component role, support, source repair or publication acceptance.')
    save(out / 'summary.json', result)
    module('negative_context_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        args.batch, 'exact-installed-compound-negative-source-context', refs, result)
    print(dict(faces=len(rows), nondegenerate=sum(r['nondegenerate'] for r in rows), installationApproved=False))


if __name__ == '__main__':
    main()
