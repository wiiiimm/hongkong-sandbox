"""Plot the exact original component containing all six current rim warnings.

Display clipping only; no geometry edits, threshold changes or role approval.
"""
import sys, uuid
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_assembly_context_plot_v3_20261023 import clipped_faces

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-hkdi88343-low-component-views-v2-20261101'
SUPPORT = 'government-xl-hkdi88343-after-one-peking-support-v1-20261101'
RUNTIME = 'government-xl-hkdi88343-after-one-peking-current-v1-20261101-runtime'
GRAPH = 'xl-terrain-recovery-20261010-hkdi-complete-original-support-v1'
NATIVE = 'government-xl-cohort19-installed-native-contacts-v1-20261101'
UID, PARENT = 'landsd/88343:0', 'landsd/22089:0'

def main():
    out, local = BASE / BATCH, HERE / 'local' / BATCH
    assert not out.exists()
    resources = ['building:' + u for u in [PARENT, UID]]
    if '--owned' not in sys.argv:
        assert not local.exists()
        c = reservations.claim('hkdi-low-component-' + str(uuid.uuid4()), resources, batch=BATCH, ttl=1800)
        assert c['ok'], c
        return execute_reserved(c['reservation'], local / 'reservation.json', [sys.executable, __file__, '--owned'])
    lease = read(local / 'reservation.json')
    assert reservations.owns(lease)
    refs, pins = [Path(__file__)], {}
    def take(batch, name):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]
            refs.append(BASE / batch / 'result.json')
        f = BASE / batch / name
        assert digest(f.read_bytes()) == pins[batch][str(f.relative_to(ROOT))]
        refs.append(f)
        return read(f)
    diagnostic = take(SUPPORT, 'original/diagnostic.json.gz')
    summary = take(SUPPORT, 'summary.json')
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == summary['currentManifestSHA256']
    refs.append(manifest)
    source = next(r for r in take(RUNTIME, 'selection.json.gz')['rows'] if r['uid'] == UID)
    native = next(r for r in take(NATIVE, 'native-input.json.gz')['rows'] if r['uid'] == PARENT)
    assets = [ROOT / source['candidate']['path'], ROOT / native['path']]
    assert digest(assets[0].read_bytes()) == source['sourceSHA256']
    assert digest(assets[1].read_bytes()) == native['entry']['sha256']
    source_world, parent_world = [decode_original_world_triangles(f.read_bytes()) for f in assets]
    refs.extend(assets)
    assert diagnostic['sourceWorldSHA256ByUid'] == {UID: digest(source_world.astype('<f8').tobytes()), PARENT: digest(parent_world.astype('<f8').tobytes())}
    # The historical freezer embeds its complete graph in the authenticated
    # result itself; its sibling diagnostic was not an evidence pin.
    graph, _ = authenticate(BASE / GRAPH)
    refs.append(BASE / GRAPH / 'result.json')
    actor = next(r for r in graph['actors'] if r['uid'] == UID)
    assert actor['sourceSHA256'] == source['sourceSHA256'] and actor['originalWorldTrianglesSHA256'] == digest(source_world.tobytes())
    offset = actor['globalFaceRange'][0]
    incident = {f + offset for r in diagnostic['paths'] for f in r['incidentFaces']}
    components = [r for r in graph['components'] if incident.intersection(r['globalOriginalFaces'])]
    assert len(components) == 1 and components[0]['actorUID'] == UID
    ids = [f - offset for f in components[0]['globalOriginalFaces']]
    assert len(ids) == 28
    low = source_world[ids]
    lo, hi = low.min((0, 1)), low.max((0, 1))
    origin = lo - [1, .8, 1]
    top = hi + [1, .8, 1]
    planes = [(i, float(origin[i]), True) for i in range(3)] + [(i, float(top[i]), False) for i in range(3)]
    parent_crop = clipped_faces(parent_world, planes)
    def xyz(t): return (t - origin)[:, :, [0, 2, 1]]
    fig = plt.figure(figsize=(15, 6), layout='constrained')
    size = (top - origin)[[0, 2, 1]]
    for i, angle in enumerate([35, 215]):
        ax = fig.add_subplot(1, 2, i + 1, projection='3d')
        ax.add_collection3d(Poly3DCollection(xyz(parent_crop), facecolors='#76a9cc', edgecolors='#376b90', linewidth=.2, alpha=.3))
        ax.add_collection3d(Poly3DCollection(xyz(low), facecolors='#e79a51', edgecolors='#70421e', linewidth=.5, alpha=1))
        points = np.asarray([r['witness']['position'] for r in diagnostic['paths']]) - origin
        ax.scatter(points[:, 0], points[:, 2], points[:, 1], c='#b51b2c', s=20, depthshade=False)
        ax.set(xlim=(0, size[0]), ylim=(0, size[1]), zlim=(0, size[2]), xlabel='Local X m', ylabel='Local Z m', zlabel='Local Y m')
        ax.set_box_aspect(size.copy())
        ax.view_init(elev=18, azim=angle)
    fig.suptitle('Exact 28-face source component (orange), original native platform (blue), six raw rim witnesses (red)\nDisplay crop only; no role/physical acceptance or geometry changes')
    image = out / 'exact-low-component-platform.png'
    image.parent.mkdir(parents=True)
    fig.savefig(image, dpi=140)
    plt.close(fig)
    result = dict(uids=[UID, PARENT], sourceSHA256=source['sourceSHA256'], nativeSHA256=native['entry']['sha256'],
        originalComponentGlobalIndex=graph['components'].index(components[0]), sourceFaces=ids, originalComponentBounds=[lo.tolist(), hi.tolist()],
        completeSourceFaces=len(source_world), nativeFaces=len(parent_world), rawRimWarningCount=len(diagnostic['paths']),
        sourceGeometryChanges=0, sourcePoseChanges=0, physicalAccepted=False, installationApproved=False, publication=False,
        originalGraphIsComponentIndexOnly=True, historicalGraphSupportApprovalTransferred=False,
        image=dict(path=str(image.relative_to(ROOT)), sha256=digest(image.read_bytes()), dimensions=[2100, 840]))
    save(out / 'summary.json', result)
    assert reservations.owns(lease) and digest(manifest.read_bytes()) == summary['currentManifestSHA256']
    refs.extend([image, HERE / 'original_assembly_context_plot_v3_20261023.py', HERE / 'exact_packed_world_geometry_20261009.py'])
    module('hkdi_low_component_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'exact-original-low-component-platform-context', refs, result)

if __name__ == '__main__': main()
