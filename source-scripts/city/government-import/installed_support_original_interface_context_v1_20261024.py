"""Inspect immutable original child/installed-parent interfaces and buried walls.
Diagnostic only: shared-edge paths, source topology and full original diagrams
provide evidence without granting architectural, physical or publication credit.
"""
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
from original_four_world_contact_paths_v1_20261023 import paths
from source_closed_components import components


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for k in ['batch', 'support-checks', 'buried-context', 'native-contacts']:
        p.add_argument('--' + k, required=True)
    a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base = ROOT / 'docs/astra-city/government-import'
    out = base / a.batch
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
    checks = take(a.support_checks, 'summary.json')
    uid, parent_uid = checks['supportedUid'], checks['installedSupportUid']
    buried = take(a.buried_context, 'summary.json')
    assert set(buried['uids']) == {uid, parent_uid}
    rows, original = [], None
    for check in checks['rows']:
        mode = check['mode']
        inp = take(a.support_checks, mode + '/input.json.gz')
        source = inp['rows'][0]
        assert source['uid'] == uid
        triangles = np.asarray(source['position'], dtype='<f8').reshape(-1, 3)[np.asarray(source['index']).reshape(-1, 3)]
        parent = np.asarray(inp['podium'], dtype='<f8')
        for key, tri in [(uid, triangles), (parent_uid, parent)]:
            assert digest(tri.tobytes()) == check['sourceWorldSHA256ByUid'][key]
        faces = next(r for r in buried['rows'] if r['mode'] == mode)['buriedFaces']
        contacts = take(a.native_contacts, uid.split('/')[1] + '--' + parent_uid.split('/')[1] + '--' + mode + '.json.gz')
        topology = components(triangles)
        targets = []
        for face in faces:
            i = face['faceIndex']
            assert triangles[i].tolist() == face['vertices']
            targets.append(dict(witness=dict(position=triangles[i].mean(0).tolist(), sourceFace=i), incidentFaces=[i]))
        verified = paths(triangles, dict(targets=targets, proof=contacts))
        ids = {f['faceIndex'] for f in faces}
        owned_components = [r for r in topology['components'] if ids.intersection(r['faceIndices'])]
        row = dict(mode=mode, buriedFaces=sorted(ids), finitePaths=sum(r['verifiedPath'] is not None for r in verified),
                   directBuriedFaceContacts=[c for c in contacts['contacts'] if c['sourceFaceA'] in ids],
                   paths=verified, completeSourceTopology=topology, affectedComponents=owned_components)
        save(out / (mode + '.json.gz'), row)
        rows.append(dict(mode=mode, buriedFaces=sorted(ids), finitePaths=row['finitePaths'],
                         directBuriedFaceContacts=len(row['directBuriedFaceContacts']),
                         componentFaces=[r['triangles'] for r in owned_components],
                         closedComponents=[r['closedConsistentlyWound'] for r in owned_components]))
        print(rows[-1], flush=True)
        if mode == 'original': original = triangles, parent, ids
    child, parent, ids = original
    center = (child.min((0, 1)) + child.max((0, 1))) / 2
    def transform(t): return (t - center)[:, :, [0, 2, 1]]
    shown = np.concatenate([transform(parent), transform(child)])
    colors = ['#c6b78c'] * len(parent) + ['#729ebc'] * len(child)
    for i in ids: colors[len(parent) + i] = '#ed4035'
    lo, hi = shown.min((0, 1)), shown.max((0, 1))
    fig = plt.figure(figsize=(16, 8), layout='constrained')
    for i, angle in enumerate([35, 215]):
        ax = fig.add_subplot(1, 2, i + 1, projection='3d')
        ax.add_collection3d(Poly3DCollection(shown, facecolors=colors, edgecolor='none'))
        ax.set(xlim=(lo[0], hi[0]), ylim=(lo[1], hi[1]), zlim=(lo[2], hi[2]), xlabel='Local east (m)', ylabel='Local viewer Z (m)', zlabel='Relative height (m)')
        ax.set_box_aspect(hi - lo)
        ax.view_init(elev=28, azim=angle)
    fig.suptitle('All unchanged original faces: installed podium tan, proposed hotel blue, sampled buried walls red')
    fig.savefig(out / 'complete-original-joint-perspectives.png', dpi=140)
    plt.close(fig)
    result = dict(uids=[uid, parent_uid], rows=rows, installationApproved=False,
                  architecturalRoleApproved=False, physicalSupportAccepted=False, sourceGeometryChanges=0,
                  qualification='Complete source topology and shared-edge continuous paths to already bound exact finite contacts. Full original joint diagram is diagnostic only; no geometry, pose, terrain, catalogue or approval changes.')
    save(out / 'summary.json', result)
    refs += [HERE / n for n in ['original_four_world_contact_paths_v1_20261023.py', 'source_closed_components.py']]
    module('native_original_interface_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'installed-native-original-complete-source-interface-context', refs, result)


if __name__ == '__main__': main()
