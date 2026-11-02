"""Classify saved exact contacts and display both complete original source scenes."""
import sys
import uuid
from collections import Counter
from fractions import Fraction
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v2_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_v2_20261103 import decode_original_world_triangles
from original_pair_area_plane_context_v1_20261103 import plane_context
from original_pair_contact_representation_context_v1_20261103 import exact_triangle

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-source43101-dock-contact-context-v1-20261103'
CONTACT = 'government-xl-source43101-dock-original-interfaces-v1-20261103'
DOCK = 'government-xl-source43101-dock-source-original-v1-20261103'
SELECT = 'government-xl-source43101-current-selection-v1-20261029'
UIDS = ['landsd/43101:0', 'landsd/316521:0', 'landsd/316522:0']


def owned():
    lease = read(HERE / 'local' / BATCH / 'reservation.json')
    assert reservations.owns(lease)
    refs = [Path(__file__), HERE / 'original_pair_area_plane_context_v1_20261103.py', HERE / 'original_pair_contact_representation_context_v1_20261103.py', HERE / 'exact_packed_world_geometry_v2_20261103.py']
    pins = {}
    def take(batch, name):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]; refs.append(BASE / batch / 'result.json')
        p = BASE / batch / name
        assert digest(p.read_bytes()) == pins[batch][str(p.relative_to(ROOT))]
        refs.append(p)
        return read(p)
    contact = take(CONTACT, 'summary.json')
    raw = take(CONTACT, 'complete-original-finite-contacts.json.gz')
    source = take(SELECT, 'selection.json.gz')['rows'][0]
    dock = take(DOCK, 'summary.json')['exactDockOriginals'][0]
    arrays = []
    for uid, path, count in [(UIDS[0], ROOT / source['candidate']['path'], 24308), (UIDS[1], ROOT / dock['path'], 5804)]:
        assert digest(path.read_bytes()) == contact['sourceSHA256ByUid'][uid]
        refs.append(path); a = decode_original_world_triangles(path.read_bytes())
        assert len(a) == count
        arrays.append(a)
    assert raw['allPairsExamined'] and raw['sourceFacesOmitted'] == 0 and len(raw['contacts']) == 72
    rows = []
    for c in raw['contacts']:
        assert c['dimension'] == 1 and c['sourcePrimitiveDimensionA'] == c['sourcePrimitiveDimensionB'] == 2
        a, b = arrays[0][c['sourceFaceA']], arrays[1][c['sourceFaceB']]
        rows.append(dict(sourceFaceA=c['sourceFaceA'], sourceFaceB=c['sourceFaceB'], providerRoot=c['sourceFaceA'] // 12154,
                         **plane_context(exact_triangle(a), exact_triangle(b))))
    out = BASE / BATCH
    save(out / 'all-saved-contact-plane-context.json.gz', dict(rows=rows, allSavedContactsExamined=True))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    full = np.concatenate(arrays); low, high = full.min((0, 1)), full.max((0, 1))
    images = []
    pieces = [arrays[0][:12154], arrays[0][12154:], arrays[1]]
    colors = ['#e94f37', '#009cbe', '#c5c9cc']
    for angle in [35, 215]:
        fig = plt.figure(figsize=(12, 9), dpi=140); ax = fig.add_subplot(111, projection='3d')
        for piece, color in zip(pieces, colors):
            ax.add_collection3d(Poly3DCollection(piece[:, :, [0, 2, 1]], facecolors=color, edgecolors='none', alpha=.75))
        for c in raw['contacts']:
            points = np.asarray([[float(Fraction(v)) for v in p] for p in c['exactPoints']])
            ax.plot(points[:, 0], points[:, 2], points[:, 1], color='black', linewidth=1.2)
        ax.set_xlim(low[0], high[0]); ax.set_ylim(low[2], high[2]); ax.set_zlim(low[1], high[1])
        ax.set_box_aspect((high - low)[[0, 2, 1]]); ax.view_init(elev=28, azim=angle)
        ax.ticklabel_format(useOffset=False, style='plain'); ax.set_xlabel('Native east X (m)'); ax.set_ylabel('Native south Z (m)'); ax.set_zlabel('HKPD (m)')
        ax.set_title('Complete originals: red B4561111; cyan named root; grey Dock1A; black exact contacts')
        fig.text(.02, .02, '24,308 + 5,804 original faces; unchanged poses. No terrain/current-scene or physical acceptance.', fontsize=10)
        fig.tight_layout(); path = out / ('complete-original-context-' + str(angle) + '.png'); fig.savefig(path); plt.close(fig)
        refs.append(path); images.append(dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())))
    result = dict(uids=UIDS, sourceSHA256ByUid=contact['sourceSHA256ByUid'], allSavedContactsExamined=True,
                  contactPairs=len(rows), bothTrianglesStraddleOtherPlane=sum(r['bothOriginalTrianglesStraddleOtherPlane'] for r in rows),
                  normalRolePairs=dict(Counter('/'.join(r['originalNormalRoles']) for r in rows)),
                  rootStraddleCounts=[sum(r['providerRoot'] == n and r['bothOriginalTrianglesStraddleOtherPlane'] for r in rows) for n in [0, 1]],
                  images=images, imagesActuallyInspected=False, allOriginalFacesShown=[24308, 5804],
                  sourceGeometryChanges=0, sourcePoseChanges=0, identityAccepted=False, physicalAcceptance=False,
                  collisionExemption=False, installationApproved=False, publication=False, permanentRejection=False,
                  qualification='Exact rational face-plane context for every saved line contact; full original source diagrams with every face. Strict straddling is evidence for interpretation, not automatic source rejection, role approval or collision exemption. No pair scan repeated and no current316522/four-world/terrain acceptance transferred.')
    save(out / 'summary.json', result)
    assert reservations.owns(lease)
    module('source43101_contact_context_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'saved-exact-source-dock1a-contact-plane-and-whole-scene-context', refs, result)
    print(dict(contacts=len(rows), bothStraddle=result['bothTrianglesStraddleOtherPlane'], byRoot=result['rootStraddleCounts']), flush=True)


if __name__ == '__main__':
    if '--owned' in sys.argv:
        owned()
    else:
        assert not (BASE / BATCH).exists() and not (HERE / 'local' / BATCH).exists()
        claim = reservations.claim('source43101-contact-context-' + str(uuid.uuid4()), ['building:' + u for u in UIDS] + ['immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
        assert claim['ok'], 'Exact source group reservation unavailable'
        execute_reserved(claim['reservation'], HERE / 'local' / BATCH / 'reservation.json', [sys.executable, __file__, '--owned'])
