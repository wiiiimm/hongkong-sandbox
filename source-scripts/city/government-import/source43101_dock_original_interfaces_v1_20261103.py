"""Exact whole-source contacts with the recovered immutable Dock1A original."""
import sys
import uuid
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v2_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_v2_20261103 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-source43101-dock-original-interfaces-v1-20261103'
DOCK = 'government-xl-source43101-dock-source-original-v1-20261103'
SELECT = 'government-xl-source43101-current-selection-v1-20261029'
PROVIDER = 'government-xl-after-sha-tin-43101-provider-roots-v1-20261029'
UIDS = ['landsd/43101:0', 'landsd/316521:0', 'landsd/316522:0']


def owned():
    lease = read(HERE / 'local' / BATCH / 'reservation.json')
    assert reservations.owns(lease)
    refs = [Path(__file__), HERE / 'exact_packed_world_geometry_v2_20261103.py', HERE / 'exact_original_finite_triangle_contacts_20261010.py']
    def take(batch, name):
        _, pins = authenticate(BASE / batch)
        path = BASE / batch / name
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.extend([BASE / batch / 'result.json', path])
        return read(path)
    dock = take(DOCK, 'summary.json')['exactDockOriginals']
    assert len(dock) == 1 and dock[0]['uid'] == UIDS[1]
    selected = take(SELECT, 'selection.json.gz')['rows'][0]
    provider = take(PROVIDER, 'summary.json')
    arrays, shas = [], {}
    for uid, path, sha, count in [(UIDS[0], ROOT / selected['candidate']['path'], selected['sourceSHA256'], 24308),
                                   (UIDS[1], ROOT / dock[0]['path'], dock[0]['sha256'], 5804)]:
        assert digest(path.read_bytes()) == sha
        triangles = decode_original_world_triangles(path.read_bytes())
        assert len(triangles) == count
        arrays.append(triangles); refs.append(path); shas[uid] = sha
    assert shas[UIDS[0]] == provider['sourceSHA256']
    pieces = np.split(arrays[0], [12154])
    assert all(digest(part.astype('<f8').tobytes()) == root['providerWorldSHA256'] for part, root in zip(pieces, provider['roots']))
    contacts = exact_finite_contacts(arrays[0], range(len(arrays[0])), arrays[1], range(len(arrays[1])))
    assert contacts['allPairsExamined'] and contacts['sourceFacesOmitted'] == 0
    out = BASE / BATCH
    save(out / 'complete-original-finite-contacts.json.gz', contacts)
    roots = []
    for index, root in enumerate(provider['roots']):
        rows = [c for c in contacts['contacts'] if c['sourceFaceA'] // 12154 == index]
        roots.append(dict(name=root['name'], completeFaces=12154, finiteContacts=len(rows),
                          pointContacts=sum(c['dimension'] == 0 for c in rows),
                          lineContacts=sum(c['dimension'] == 1 for c in rows),
                          areaContacts=sum(c['dimension'] == 2 for c in rows)))
    summary = dict(uids=UIDS, sourceSHA256ByUid=shas, completeOriginalFaces=[24308, 5804], bothProviderRootsPreserved=True,
                   originalWorldArraySHA256s=[digest(a.astype('<f8').tobytes()) for a in arrays],
                   trianglePairsTested=contacts['trianglePairsTested'], allPairsExamined=True, sourceFacesOmitted=0,
                   rootContacts=roots, sourceGeometryChanges=0, sourcePoseChanges=0,
                   identityAccepted=False, physicalAcceptance=False, supportAcceptance=False, collisionExemption=False,
                   installationApproved=False, publication=False, permanentRejection=False,
                   qualification='Every original finite primitive in both complete source scenes participates in the existing exact inclusive-AABB contact scan. Root grouping is reporting only; no geometry is omitted. Original-coordinate contact evidence only, not four-world runtime acceptance, support approval, whole current scene clearance,316522coverage or an identity/terminal/publication decision.')
    save(out / 'summary.json', summary)
    assert reservations.owns(lease)
    module('source43101_dock_interfaces_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'whole-original-source-and-dock1a-finite-interface-context', refs, summary)
    print(dict(rootContacts=roots, trianglePairsTested=contacts['trianglePairsTested']), flush=True)


if __name__ == '__main__':
    if '--owned' in sys.argv:
        owned()
    else:
        assert not (BASE / BATCH).exists() and not (HERE / 'local' / BATCH).exists()
        claim = reservations.claim('source43101-dock-interfaces-' + str(uuid.uuid4()), ['building:' + u for u in UIDS] + ['immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
        assert claim['ok'], 'Exact source group reservation unavailable'
        execute_reserved(claim['reservation'], HERE / 'local' / BATCH / 'reservation.json', [sys.executable, __file__, '--owned'])
