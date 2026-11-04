"""Exact finite source contacts for the nine remaining low downward facets.

No architectural labels, structural-root requirements, source edits or approval.
"""
import sys
import uuid
from collections import Counter
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-silvercord-lippo-lower-patch-source-contacts-v1-20261103'
LOCAL = HERE / 'local' / BATCH
RUNTIME = 'government-xl-silvercord-lippo-complete-floor-runtime-v2-20261103'
ATTRIBUTES = 'government-xl-silvercord-lippo-original-attributes-v1-20261101'
FACE_IDS = {'landsd/233997:0': [1347, 1348, 1349, 6240, 6241, 6242], 'landsd/231645:0': [8231, 8232, 8233]}


def owned():
    lease = read(LOCAL / 'reservation.json')
    assert reservations.owns(lease)
    out = BASE / BATCH
    assert not out.exists()
    refs, pins = [Path(__file__)], {}

    def take(batch, path):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]
            refs.append(BASE / batch / 'result.json')
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selection = take(RUNTIME, BASE / RUNTIME / 'selection.json.gz')
    attributes = take(ATTRIBUTES, BASE / ATTRIBUTES / 'attributes.json.gz')
    assert attributes['startEndAllInputsVerified']
    rows = []
    sources = {}
    for uid, faces in FACE_IDS.items():
        source = next(r for r in selection['rows'] if r['uid'] == uid)
        attr = next(r for r in attributes['rows'] if r['uid'] == uid)
        path = ROOT / source['candidate']['path']
        assert digest(path.read_bytes()) == source['sourceSHA256'] == attr['sourceSHA256']
        refs.append(path)
        sources[uid] = source['sourceSHA256']
        index = np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)
        worlds = dict(original=decode_original_world_triangles(path.read_bytes()), **{
            mode: np.asarray(attr[field], dtype='<f8').reshape(-1, 3)[index] for mode, field in [
                ('literal', 'completeLiteralWorldPosition'), ('leftF32', 'completeExplicitLeftAssociatedFloat32WorldPosition'), ('balancedF32', 'completeExplicitBalancedFloat32WorldPosition')]})
        low_batch = 'government-xl-silvercord-lippo-complete-floor-low-faces-v1-20261103-' + uid.split('/')[1].replace(':', '-')
        for mode, tri in worlds.items():
            assert reservations.owns(lease)
            old_mode = {'leftF32': 'left', 'balancedF32': 'balanced'}.get(mode, mode)
            low = take(low_batch, BASE / low_batch / (old_mode + '.json.gz'))
            assert digest(tri.tobytes()) == low['sourceWorldSHA256']
            assert len(tri) == low['completeSourceFaces'] == source['triangles']
            assert set(faces) <= {r['sourceFace'] for r in low['rows']}
            proof = exact_finite_contacts(tri, faces, tri, range(len(tri)))
            assert proof['allPairsExamined'] and proof['sourceFacesOmitted'] == 0
            normals = np.cross(tri[:, 1]-tri[:, 0], tri[:, 2]-tri[:, 0])
            lengths = np.linalg.norm(normals, axis=1)
            external = [r for r in proof['contacts'] if r['sourceFaceB'] not in faces]
            positive = [r for r in external if r['dimension'] > 0 and r['sourcePrimitiveDimensionA'] == r['sourcePrimitiveDimensionB'] == 2]
            wall_ids = sorted({r['sourceFaceB'] for r in positive if lengths[r['sourceFaceB']] > 0 and abs(normals[r['sourceFaceB'], 1]) <= .25*lengths[r['sourceFaceB']]})
            item = dict(uid=uid, mode=mode, sourceWorldSHA256=digest(tri.tobytes()), selectedDownwardSourceFaces=faces,
                        completeSourceFaces=len(tri), completeFiniteProof=proof, positiveExternalSourceContacts=positive,
                        positiveExternalWallFaces=wall_ids, qualification='Exact finite contact dimensions and measured normals only. No architectural purpose, structural support, root or physical acceptance.')
            save(out / (uid.split('/')[1].replace(':', '-') + '-' + mode + '.json.gz'), item)
            row = dict(uid=uid, mode=mode, completeSourceFaces=len(tri), selectedFaces=faces,
                       externalContactDimensions=dict(Counter(r['dimension'] for r in external)),
                       positiveExternalContactCount=len(positive), positiveExternalWallFaces=wall_ids,
                       selectedFacesWithPositiveExternalContact=sorted({r['sourceFaceA'] for r in positive}))
            rows.append(row)
            print(row, flush=True)
    assert reservations.owns(lease)
    result = dict(uids=list(FACE_IDS), sourceSHA256ByUid=sources, rows=rows, sourceGeometryChanges=0, sourcePoseChanges=0,
                  sourceRoleAccepted=False, supportApproved=False, physicalAcceptance=False, installationApproved=False, publication=False,
                  qualification='Every remaining declared low downward facet is tested against every face of its exact unchanged source in all four coordinate streams. Self/within-packet contacts and all zero-dimensional contacts remain in the complete raw proof. Disconnectedness or source crossings alone add no new gate; this evidence addresses the already recorded low-face/foundation investigation only.')
    save(out / 'summary.json', result)
    refs.extend(HERE / n for n in ['exact_packed_world_geometry_20261009.py', 'exact_original_finite_triangle_contacts_20261010.py'])
    module('silvercord_lippo_lower_contacts_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'complete-four-world-low-downward-source-facet-finite-contacts', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    if '--owned' in sys.argv:
        owned()
    else:
        assert not LOCAL.exists() and not (BASE / BATCH).exists()
        claim = reservations.claim('silvercord-lippo-lower-source-contacts-' + str(uuid.uuid4()), ['building:' + u for u in FACE_IDS] + ['immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
        assert claim['ok'], claim
        execute_reserved(claim['reservation'], LOCAL / 'reservation.json', [sys.executable, __file__, '--owned'])
