"""Audit all mixed BASIC/original Ocean states without granting model acceptance."""
import itertools
import numpy as np
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

IDS = ('234188', '156599', '210743', '231469')
MODES = ('original', 'literal', 'leftF32', 'balancedF32')


def face_context(source_contacts, basic_contacts, side):
    """Face membership is diagnostic only, never proof of equal contact regions."""
    assert side in ('A', 'B')
    authored = {c['sourceFace' + side] for c in source_contacts if c['dimension'] > 0}
    mixed = [c for c in basic_contacts if c['dimension'] > 0]
    return dict(positiveMixedContacts=len(mixed),
                mixedSourceFaces=sorted({c['sourceFaceA'] for c in mixed}),
                mixedSourceFacesWithoutPositiveAuthoredPairContact=sorted(
                    {c['sourceFaceA'] for c in mixed} - authored))


def enumerate_states(ids, directed_conflicts):
    ids = tuple(ids)
    assert len(ids) == len(set(ids))
    assert all(a in ids and b in ids and a != b for a, b in directed_conflicts)
    result = []
    for bits in itertools.product((False, True), repeat=len(ids)):
        active = {uid for uid, bit in zip(ids, bits) if bit}
        conflicts = sorted((a, b) for a, b in directed_conflicts if a in active and b not in active)
        result.append(dict(originalUids=sorted(active), basicUids=sorted(set(ids)-active),
                           mixedContactEdges=[dict(original=a, basic=b) for a, b in conflicts],
                           freeOfMeasuredMixedPositiveContacts=not conflicts,
                           physicalAcceptance=False))
    return result


def main():
    base = ROOT/'docs/astra-city/government-import'
    batch = 'government-xl-after-waterfront-ocean-four-mixed-basic-state-audit-v1-20261027'
    out = base/batch
    assert not out.exists()
    refs = [Path(__file__)]
    pins_by_batch = {}

    def take(name, filename='summary.json'):
        if name not in pins_by_batch:
            pins_by_batch[name] = authenticate(base/name)[1]
            refs.append(base/name/'result.json')
        path = base/name/filename
        assert digest(path.read_bytes()) == pins_by_batch[name][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    foreign = 'government-xl-after-waterfront-ocean-four-corrected-foreign-contacts-v1-20261027'
    foreign_summary = take(foreign)
    uids = ['landsd/'+i+':0' for i in IDS]
    assert set(foreign_summary['uids']) == set(uids)
    identity = take('government-xl-after-waterfront-ocean-four-corrected-identity-review-v1-20261027')
    source_shas = identity['sourceSHA256ByUid']
    assert set(source_shas) == set(uids)
    basic = {r['uid']: r for r in take(foreign, 'basic.json')['rows']}
    attrs = {r['uid']: r for r in take('government-xl-after-waterfront-ocean-four-attributes-v1-20261027', 'attributes.json.gz')['rows']}
    runtime_name = 'government-xl-after-waterfront-ocean-four-corrected-runtime-v1-20261027'
    runtime = {r['uid']: r for r in take(runtime_name, 'selection.json.gz')['rows']}
    rows = []
    bounds_proofs = []
    conflicts = set()
    for a, b in itertools.combinations(IDS, 2):
        pair = f'government-xl-after-waterfront-ocean-four-junction-{a}-{b}-contacts-v1-20261027'
        summary = take(pair)
        expected = {'landsd/'+i+':0': source_shas['landsd/'+i+':0'] for i in (a, b)}
        assert summary['sourceSHA256ByUid'] == expected
        assert summary['uids'] == ['landsd/'+i+':0' for i in (a, b)]
        for mode in MODES:
            authored = take(pair, mode+'.json.gz')
            assert authored['allPairsExamined'] and authored['sourceFacesOmitted'] == 0
            for source, other, side in ((a, b, 'A'), (b, a, 'B')):
                source_uid, other_uid = ['landsd/'+i+':0' for i in (source, other)]
                filename = f'{source}:0--{other}:0--{mode}.json.gz'
                if (base/foreign/filename).exists():
                    mixed = take(foreign, filename)
                    assert mixed['allPairsExamined'] and mixed['sourceFacesOmitted'] == 0
                    context = face_context(authored['contacts'], mixed['contacts'], side)
                else:
                    # Scope omission is not separation evidence. Prove disjointness
                    # from every actual source/basic vertex before accepting zero.
                    attr = attrs[source_uid]
                    assert attr['sourceSHA256'] == source_shas[source_uid]
                    if mode == 'original':
                        asset = ROOT/runtime[source_uid]['candidate']['path']
                        assert digest(asset.read_bytes()) == source_shas[source_uid]
                        assert pins_by_batch[runtime_name][str(asset.relative_to(ROOT))] == source_shas[source_uid]
                        refs.append(asset)
                        vertices = decode_original_world_triangles(asset.read_bytes()).reshape(-1, 3)
                    else:
                        field = dict(literal='completeLiteralWorldPosition', leftF32='completeExplicitLeftAssociatedFloat32WorldPosition', balancedF32='completeExplicitBalancedFloat32WorldPosition')[mode]
                        vertices = np.asarray(attr[field]).reshape(-1, 3)
                    target = np.asarray(basic[other_uid]['position']).reshape(-1, 3)
                    lo, hi = vertices.min(0), vertices.max(0)
                    tlo, thi = target.min(0), target.max(0)
                    gaps = np.maximum(tlo-hi, lo-thi)
                    assert np.any(gaps > 0), 'Unmeasured overlapping pair needs finite-contact computation'
                    bounds_proofs.append(dict(sourceUid=source_uid, basicUid=other_uid, mode=mode,
                        sourceBounds=[lo.tolist(), hi.tolist()], basicBounds=[tlo.tolist(), thi.tolist()], strictSeparatingAxisGapsM=gaps.tolist()))
                    context = face_context(authored['contacts'], [], side)
                if context['positiveMixedContacts']:
                    conflicts.add((source_uid, other_uid))
                rows.append(dict(sourceUid=source_uid, basicUid=other_uid, mode=mode, **context))
    states = enumerate_states(uids, conflicts)
    result = dict(uids=uids, sourceSHA256ByUid=source_shas, rows=rows, states=states, strictBoundsSeparation=bounds_proofs,
                  mixedStatesChecked=len(states),
                  statesWithMeasuredMixedPositiveContacts=sum(not r['freeOfMeasuredMixedPositiveContacts'] for r in states),
                  sourceFaceMembershipProvesContactEquivalence=False,
                  requiresActivationStateHandling=bool(conflicts),
                  sourceGeometryChanges=0, physicalAcceptance=False,
                  installationApproved=False, publication=False,
                  qualification='Complete authenticated four-world directed original/BASIC contact audit. Every one of sixteen four-source activation states is enumerated. Positive mixed contacts require explicit handling; face membership alone does not establish contact-region equivalence. An edge-free state is NOT physical, support, terrain, identity, visual or publication approval. No runtime or catalogue changes.')
    # Recheck all frozen provenance before recording the derived evidence.
    for pins in pins_by_batch.values():
        for path, sha in pins.items():
            assert digest((ROOT/path).read_bytes()) == sha
    save(out/'summary.json', result)
    module('ocean_mixed_state_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        batch, 'all-four-source-mixed-basic-activation-state-audit', list(dict.fromkeys(refs)), result)
    print(dict(states=len(states), conflicting=result['statesWithMeasuredMixedPositiveContacts'], directedEdges=len(conflicts)), flush=True)


if __name__ == '__main__':
    main()
