"""Bounded ROOT review of the private BASIC footing collision/interface role.

Not original-model placement, visual, structural or installation acceptance.
"""
import argparse
import sys
import uuid
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from elegant_basic_footing_foreign_volume_v1_20261028 import BASE, PREFIX, PROPOSAL, RUNTIME, ATTRS


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch', required=True)
    p.add_argument('--owned', action='store_true')
    a = p.parse_args()
    assert a.batch.startswith(PREFIX) and '/' not in a.batch
    out, local = BASE/a.batch, HERE/'local'/a.batch
    assert not out.exists()
    rp = BASE/(PREFIX+'sixteen-original-updated-terrain-plan-v1-20261028.json')
    resources, lp = set(read(rp)['resources']), local/'reservation.json'
    if not a.owned:
        assert not local.exists()
        claim = reservations.claim('basic-footing-collision-review-'+str(uuid.uuid4()), sorted(resources), batch=a.batch, ttl=1800)
        assert claim['ok']
        return execute_reserved(claim['reservation'], lp, [sys.executable, __file__, *sys.argv[1:], '--owned'])
    lease = read(lp)
    assert reservations.owns(lease) and resources <= set(lease['resources'])
    refs, pins = [Path(__file__), rp], {}

    def take(batch, name):
        if batch not in pins:
            pins[batch] = authenticate(BASE/batch)[1]
            refs.append(BASE/batch/'result.json')
        path = BASE/batch/name
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    context = take(PREFIX+'basic-footing-foreign-volume-v1-20261028', 'summary.json')
    interface_batch = PREFIX+'basic-footing-west-grand-interface-v1-20261028'
    interface = take(interface_batch, 'summary.json')
    software = take(PREFIX+'basic-footing-runtime-collision-v1-20261028', 'runtime-collision.json')
    b = take(PROPOSAL, 'input.json')['building']
    proposal = take(PROPOSAL, 'proposal.json')
    ground = take(PROPOSAL, 'continuous-ground.json.gz')
    geometry = take(PROPOSAL, 'geometry.json.gz')
    assert b['uid'] == proposal['uid'] == context['uid'] == software['uid'] == 'landsd/213586:0'
    assert b['structureType'] == 'Podium' and b['kind'] == 'yes' and b['minimum'] == 0
    assert b['baseSource'] == b['heightSource'] == 'landsd' and not b.get('modelGeometry')
    assert ground['uncoveredAreaM2'] == 0 and not ground['verticalOrDegenerateContacts']
    assert ground['groundRange'][1] < b['base']-.02
    assert geometry['after']['position'][:len(geometry['before']['position'])] == geometry['before']['position']
    assert geometry['after']['index'][:len(geometry['before']['index'])] == geometry['before']['index']
    assert context['candidateOriginals'] == 16 and context['testedForeignBasicForms'] == 155
    assert context['nativeBoundsPending'] == 0 and len(context['nativeRows']) == 9
    hits = [r for r in context['rows'] if r['closedFootingVolumeContacts']]
    native_hits = [r for r in hits if r['role'] == 'candidate-original']
    assert len(native_hits) == 4 and {r['uid'] for r in native_hits} == {'landsd/215726:0'}
    assert {r['mode'] for r in native_hits} == {'original', 'literal', 'leftF32', 'balancedF32'}
    assert {r['uid'] for r in hits if r['role'] == 'current-basic'} == {'landsd/224121:0', 'landsd/236170:0'}
    selection = take(RUNTIME, 'selection.json.gz')
    assert {'landsd/224121:0', 'landsd/236170:0'} <= {r['uid'] for r in selection['rows']}
    row = next(r for r in selection['rows'] if r['uid'] == 'landsd/215726:0')
    attrs = next(r for r in take(ATTRS, 'attributes.json.gz')['rows'] if r['uid'] == row['uid'])
    path = ROOT/row['candidate']['path']
    assert digest(path.read_bytes()) == row['sourceSHA256'] == attrs['sourceSHA256']
    refs.append(path)
    worlds = dict(original=decode_original_world_triangles(path.read_bytes()))
    idx = np.asarray(attrs['completeOriginalIndex']).reshape(-1, 3)
    for mode, field in [('literal', 'completeLiteralWorldPosition'), ('leftF32', 'completeExplicitLeftAssociatedFloat32WorldPosition'), ('balancedF32', 'completeExplicitBalancedFloat32WorldPosition')]:
        worlds[mode] = np.asarray(attrs[field]).reshape(-1, 3)[idx]
    for r in interface['rows']:
        assert r['existingBodyContactFaces'] == r['addedFootingContactFaces'] == [65, 93, 94]
        assert not r['newContactFaceIdsAbsentFromExistingBody']
        tri = worlds[r['mode']]
        assert digest(tri.astype('<f8').tobytes()) == r['sourceWorldSHA256']
        faces = tri[[65, 93, 94]]
        normals = np.cross(faces[:, 1]-faces[:, 0], faces[:, 2]-faces[:, 0])
        assert np.all(normals[:, 1] == 0) and np.all(np.linalg.norm(normals, axis=1) > 0)
    assert software['probes'] == 80640 and software['roofSamples'] == 5760 and software['unchangedRegionalForms'] == 155
    assert software['oldCollisionVolumesExactlyRetained'] and software['onlyAddedCollisionVolumeIsSameFootprintBelowBase']
    for key, sha in software['inputHashes'].items():
        assert digest((ROOT/key).read_bytes()) == sha
        refs.append(ROOT/key)
    image = ROOT/interface['image']['path']
    assert digest(image.read_bytes()) == interface['image']['sha256']
    refs.append(image)
    result = dict(uids=[b['uid']], uid=b['uid'], reviewer='Codex ROOT',
                  reviewType='exact-basic-only-footing-collision-and-continued-vertical-wall-interface',
                  collisionReviewApproved=True, visualReviewApproved=False, physicalAccepted=False,
                  sourcePlacementApproved=False, originalModelPlacementApproved=False,
                  installationApproved=False, publication=False, sourceGeometryChanges=0,
                  governmentGeometryChanges=0, aiGeometryModelling=False, evidenceInterpretationUsedAI=True,
                  sourceFormSHA256=digest(__import__('json').dumps(b, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()),
                  foundationBase=proposal['foundationBase'], existingOriginalWallFaces=[65, 93, 94],
                  originalSourceSHA256=row['sourceSHA256'], sourceWorldSHA256ByMode={k: digest(v.astype('<f8').tobytes()) for k, v in worlds.items()},
                  rawSurfaceContactsRetained=True, rawReverseSolidContainmentNotProved=True,
                  imageActuallyInspected=interface['image'],
                  basis=[
                      'The target is the existing surveyed solid BASIC podium with minimum0, not an open canopy or an official mesh. Its whole original body, roof and footprint remain unchanged. The extra windowless same-footprint volume only seals the previously floating lower body down to authenticated complete drawn ground.',
                      'All16candidate originals/all4streams and155foreign BASIC surfaces were tested against the CLOSED added volume, with all9installed neighbours bounds-separated. The sole original contact continues the SAME three exact vertical walls already intersecting the unchanged opaque BASIC body. No new original facet, roof, passage/deck surface or neighbour outside that intended footprint is introduced into the interface. These contacts are accepted as continuation inside this BASIC solid; no shared cadastral identity/ownership or original-model placement approval is inferred.',
                      'The two other contact contexts are BASIC counterparts of originals in this same proposed collection; they remain recorded and must not be represented as simultaneously clear detailed actors. BASE-only runtime semantics are separately retained by the BASIC-only guard.',
                      'Production BuildingIndex/collisionVolumes preserves the entire old volume,155other BASIC volumes and all sampled roofs.80640target/regional probes show no removed collision and changes attributable only to the added volume below the old base. This grants the bounded footing collision/interface review, not universal movement, structural engineering, reverse closed-solid containment, full original assembly or visual approval.',
                      'ROOT inspected the complete before/after two-direction geometry image. Full actual viewer/terrain desktop/mobile day/night and availability views still must pass before visual review/publication. The earlier private publication draft remains false/unapproved; do not mutate it or treat this collision-only receipt as a publisher-ready review.'
                  ])
    save(out/'review.json', result)
    assert reservations.owns(lease)
    module('basic_footing_collision_review_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'root-bounded-basic-only-footing-collision-interface-review', list(dict.fromkeys(refs)), result)
    print(dict(collisionReviewApproved=True, visualReviewApproved=False, installationApproved=False), flush=True)


if __name__ == '__main__':
    main()
