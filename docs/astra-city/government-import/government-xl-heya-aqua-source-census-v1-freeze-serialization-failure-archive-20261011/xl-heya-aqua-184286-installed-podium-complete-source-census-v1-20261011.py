"""Complete unchanged Heya source components/interfaces; no current approval.

The two old low-rim negatives stay verbatim. Both lie in the same authored
tower body, so complete positive finite interfaces are investigated without
inventing support at either point. Installed podium status is historical
context only: genuine current roots, visual placement, terrain and runtime
remain separate obligations. This draft is not executed during publication.
"""
import importlib.util
import json
from collections import deque
from pathlib import Path

import numpy as np
from run import ROOT, HERE, read, save, digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_body_boundary_group_census_v1_20261011 import census as boundary_census
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from xl_source_stream_binding_20261009 import source_stream_binding

BATCH = 'government-xl-heya-aqua-184286-installed-podium-complete-source-census-v1-20261011'
BASE = ROOT / 'docs/astra-city/government-import'
DOC = BASE / BATCH
INPUT = BASE / 'government-xl-georef-sparkle-heya-original-supports-20261008'
TOWER, PODIUM = 'landsd/184286:0', 'landsd/184285:0'
EXPECTED = {
    TOWER: dict(modelId='B339682218601063C0', csuid='3396822186T20151008', faces=17910,
        sourceSHA256='f9c73a61b679ebc18df1741c01c7e98463a4269928a38b882e3a41d268646155',
        worldSHA256='64083b7a54fc708319aa92abb8948beacf689c0b8928dd431ef470d50540c18d'),
    PODIUM: dict(modelId='B339442219102063C0', csuid='3394422191P20151008', faces=3844,
        sourceSHA256='46add0484e7cedd20b7de12c9843a2cba8bb419f5824dde27fb9b41fb8efa1b2',
        worldSHA256='65937caa244bc03136c29d5dd2162efba58a6ccadc54039c26ec303cec3484f3'),
}

def complete_contacts(a, ids_a, b, ids_b):
    result = exact_finite_contacts(a, ids_a, b, ids_b,
        maximum_pairs=len(ids_a) * len(ids_b))
    assert result['allPairsExamined'] and result['sourceFacesOmitted'] == 0
    return result

def positive_real_contacts(result):
    return [c for c in result['contacts'] if c['dimension'] > 0
        and c['sourcePrimitiveDimensionA'] == c['sourcePrimitiveDimensionB'] == 2]

def main():
    assert not DOC.exists()
    input_path = INPUT / 'support-inputs.json'
    failure_path = INPUT / 'support-failure-surfaces.json.gz'
    raw_inputs = read(input_path)
    selected = {uid: [r for r in raw_inputs['sources'] if r['uid'] == uid] for uid in EXPECTED}
    assert all(len(rows) == 1 for rows in selected.values())
    raw_failures = [r for r in read(failure_path)['rows'] if r['uid'] == TOWER]
    assert len(raw_failures) == 1 and raw_failures[0]['supportUid'] == PODIUM
    assert raw_failures[0]['unresolved'] == 2 and not raw_failures[0]['unchangedInterfacePassed']
    refs = [Path(__file__), input_path, failure_path, INPUT / 'result.json']
    helpers = ['exact_packed_world_geometry_20261009.py',
        'exact_original_shared_edge_component_census_v2_20261011.py',
        'test_exact_original_shared_edge_component_census_v2_20261011.py',
        'exact_original_body_boundary_group_census_v1_20261011.py',
        'test_exact_original_body_boundary_group_census_v1_20261011.py',
        'exact_original_finite_triangle_contacts_20261010.py',
        'test_exact_original_finite_triangle_contacts_20261010.py',
        'exact_original_component_contacts_20261009.py',
        'exact_original_shell_intersections_20261009.py', 'xl_source_stream_binding_20261009.py']
    refs.extend(HERE / name for name in helpers)
    pinned = {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in refs}
    actors, worlds, parts, component_of = {}, {}, {}, {}
    for uid, expected in EXPECTED.items():
        row = selected[uid][0]
        assert row['modelId'] == expected['modelId']
        assert row['source']['building']['buildingCSUID'] == expected['csuid']
        asset = ROOT / row['candidate']['path']
        raw = asset.read_bytes()
        assert digest(raw) == expected['sourceSHA256'] == row['candidate']['entry']['sha256']
        world = decode_original_world_triangles(raw)
        assert world.shape == (expected['faces'], 3, 3) and np.isfinite(world).all()
        assert digest(world.astype('<f8').tobytes()) == expected['worldSHA256']
        topology = census(world, list(range(len(world))))
        groups = topology['sharedEdgeConnectedComponents']
        mapping = {face: component for component, ids in enumerate(groups) for face in ids}
        assert len(mapping) + len(topology['exactNonrenderingOriginalFaces']) == len(world)
        worlds[uid], parts[uid], component_of[uid] = world, groups, mapping
        bounds = [(world[ids].min((0, 1)), world[ids].max((0, 1))) for ids in groups]
        actors[uid] = dict(sourceTuple=expected, completeProviderStreams=source_stream_binding(raw),
            completeOriginalTopology=topology, completeFaceToComponent=mapping,
            completeComponentBounds=[dict(component=i, completeFaceIds=ids,
                worldBounds=[bounds[i][0].tolist(), bounds[i][1].tolist()]) for i, ids in enumerate(groups)],
            completeBodyBoundaryCensus=[boundary_census(world, ids) for ids in groups],
            currentPoseApproved=False, groundRootsAccepted=False, visualRolesAccepted=False)
        refs.append(asset)
        pinned[str(asset.relative_to(ROOT))] = digest(raw)
    pairs, graph = [], {}
    for uid in EXPECTED:
        for i in range(len(parts[uid])):
            graph[(uid, i)] = set()
        for i, ids_a in enumerate(parts[uid]):
            low_a, high_a = worlds[uid][ids_a].min((0, 1)), worlds[uid][ids_a].max((0, 1))
            for j in range(i + 1, len(parts[uid])):
                ids_b = parts[uid][j]
                low_b, high_b = worlds[uid][ids_b].min((0, 1)), worlds[uid][ids_b].max((0, 1))
                if not (np.all(high_a >= low_b) and np.all(high_b >= low_a)):
                    continue
                contact = complete_contacts(worlds[uid], ids_a, worlds[uid], ids_b)
                positive = positive_real_contacts(contact)
                pairs.append(dict(uid=uid, componentA=i, componentB=j,
                    completePrimitiveContactInventory=contact, positiveRealFacetInterfaces=len(positive)))
                if positive:
                    graph[(uid, i)].add((uid, j)); graph[(uid, j)].add((uid, i))
            print(json.dumps(dict(uid=uid, completedComponent=i, totalComponents=len(parts[uid]))), flush=True)
    cross = complete_contacts(worlds[TOWER], list(range(len(worlds[TOWER]))),
        worlds[PODIUM], list(range(len(worlds[PODIUM]))))
    for c in positive_real_contacts(cross):
        a = (TOWER, component_of[TOWER][c['sourceFaceA']])
        b = (PODIUM, component_of[PODIUM][c['sourceFaceB']])
        graph[a].add(b); graph[b].add(a)
    families, remaining = [], set(graph)
    while remaining:
        start = min(remaining); seen = {start}; todo = deque([start])
        while todo:
            for node in sorted(graph[todo.popleft()]):
                if node not in seen:
                    seen.add(node); todo.append(node)
        remaining -= seen; families.append(sorted(seen))
    residuals = []
    for witness in raw_failures[0]['samples']:
        point = np.asarray(witness['position'])
        faces = np.flatnonzero(np.any(np.all(worlds[TOWER] == point, axis=2), axis=1)).tolist()
        assert faces
        ids = sorted({component_of[TOWER][i] for i in faces})
        assert ids == [4] and len(parts[TOWER][4]) == 2534
        residuals.append(dict(unalteredRawWitness=witness, completeIncidentOriginalFaceIds=faces,
            completeSourceComponentIds=ids, pointSupportCredit=False))
    out = dict(uids=[TOWER, PODIUM], actors=actors,
        everyBoundsNominatedWithinActorComponentPair=pairs,
        excludedWithinActorPairsProvenStrictlyDisjointByCompleteExactBounds=True,
        completeTowerToPodiumPrimitiveInterfaces=cross,
        completePositiveRealFacetInterfaceFamilies=families,
        rawTwoResidualRimFailuresRetained=raw_failures[0], residualSourceIncidences=residuals,
        sourceGeometryChanges=0, terrainGeometryChanges=0, sourceFacesOmitted=0,
        historicalPodiumInstalledContextOnly=True, currentAcceptance=False,
        structuralSupportAccepted=False, groundRootsAccepted=False, visualRolesAccepted=False,
        installationApproved=False, newlyInstalled=0,
        qualification='Complete unchanged provider originals only. Positive-dimensional real-facet interfaces are geometric evidence, not current roots, engineering support or foreign-collision exemptions. Both historical rim negatives remain. Every component boundary is inventoried without assigning a visual role or demanding that authored free boundaries be mounted. Fresh actual installed podium/current four-world ground and all foreign/native/runtime guards remain required.')
    save(DOC / 'diagnostic.json.gz', out)
    refs.append(DOC / 'diagnostic.json.gz')
    for path, sha in pinned.items():
        assert digest((ROOT / path).read_bytes()) == sha
    spec = importlib.util.spec_from_file_location('heya_complete_source_freeze',
        HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py')
    freezer = importlib.util.module_from_spec(spec); spec.loader.exec_module(freezer)
    receipt = freezer.freeze(BATCH, 'heya-complete-provider-source-components-interfaces-no-root-credit', refs, out)
    print(json.dumps(dict(jobId=receipt['jobId'], currentAcceptance=False, installationApproved=False)), flush=True)

if __name__ == '__main__':
    main()
