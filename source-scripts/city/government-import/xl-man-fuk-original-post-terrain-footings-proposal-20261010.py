"""Freeze a changed terrain proposal and complete four-post column diagnostic."""
import importlib.util
import json
import numpy as np
from run import ROOT, HERE, read, save, digest
from man_fuk_original_post_terrain_footings_20261010 import propose, POST_FACES
from original_bound_facet_wall_context_v2_20261010 import exposure_at_vertex

BATCH = 'government-xl-man-fuk-original-post-terrain-footings-proposal-20261010'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
LOCAL = HERE / 'local' / BATCH
BASE = ROOT / 'docs/astra-city/government-import'
OLD = 'government-xl-man-fuk-complete-retained-original-physical-v5-20261010'


def main():
    assert not DOC.exists() and not LOCAL.exists()
    row = read(BASE / OLD / 'selection.json.gz')['rows'][0]
    asset = ROOT / row['candidate']['path']
    patch_path = HERE / 'local' / OLD / 'government-native-266062-0.json'
    assert digest(patch_path.read_bytes()) == 'fc841cf888781fb57396fc03e1be2569d35c0113b01d893f8d6701722624f492'
    old = read(patch_path)
    patch, proof = propose(old, asset.read_bytes())
    runtime_path = HERE / 'local' / OLD / 'runtime-geometry.json.gz'
    runtime = read(runtime_path)['rows'][0]
    ground = np.asarray(runtime['drawnGroundGeometry'], np.float64).reshape(-1, 3, 3)
    assert digest(ground.tobytes()) == '90022d93ec31c681e0c8246663f284b44056263b068c1e7230cc24c11be9bb2d'
    index = np.asarray(old['nativeMesh']['index'], np.uint32).reshape(-1, 3)
    old_faces = np.asarray(old['nativeMesh']['position'], np.float32).reshape(-1, 3)[index].astype(np.float64)
    new_faces = np.asarray(patch['nativeMesh']['position'], np.float32).reshape(-1, 3)[index].astype(np.float64)
    lookup = {}
    for i in proof['changedIncidentTerrainFaces']:
        key = tuple(old_faces[i].reshape(-1))
        if key in lookup:
            assert np.array_equal(lookup[key][1], new_faces[i])
        lookup[key] = (i, new_faces[i])
    candidate_ground = ground.copy()
    replaced = []
    for i, face in enumerate(ground):
        hit = lookup.get(tuple(face.reshape(-1)))
        if hit is not None:
            candidate_ground[i] = hit[1]
            replaced.append(dict(drawnGroundFace=i, candidateTerrainFace=hit[0]))
    assert set(r['candidateTerrainFace'] for r in replaced) == set(proof['changedIncidentTerrainFaces'])
    prior = read(BASE / 'government-xl-man-fuk-four-original-footings-diagnostic-20261010' / 'diagnostic.json.gz')
    rows = []
    for part in prior['rows']:
        assert part['completeOriginalFaces'] == POST_FACES[part['component'] - 2]
        samples = []
        for sample in part['completeOriginalSamples']:
            result = exposure_at_vertex(sample['point'], candidate_ground)
            samples.append(dict(point=sample['point'], completeExactFiniteGroundColumn=result))
        rows.append(dict(component=part['component'], completeOriginalSamples=samples))
    save(LOCAL / 'government-native-266062-0.json', patch)
    save(DOC / 'terrain-only-proposal.json', proof)
    save(DOC / 'diagnostic.json.gz', dict(rows=rows, exactRenderedFacetSubstitutions=replaced,
        completeCandidateDrawnGroundSHA256=digest(candidate_ground.tobytes()),
        sourceGeometryChanges=0, physicalAccepted=False, rootCredit=False,
        installationApproved=False, qualification='Candidate-only exact literal finite columns; actual browser-exported ground and every physical gate must independently be rerun.'))
    paths = [__file__, asset, patch_path, runtime_path,
        BASE / 'government-xl-man-fuk-four-original-footings-diagnostic-20261010' / 'diagnostic.json.gz',
        HERE / 'man_fuk_original_post_terrain_footings_20261010.py',
        HERE / 'original_bound_facet_wall_context_v2_20261010.py',
        HERE / 'exact_original_triangle_pair_column_gap_20261010.py',
        HERE / 'exact_packed_world_geometry_20261009.py',
        LOCAL / 'government-native-266062-0.json', DOC / 'terrain-only-proposal.json', DOC / 'diagnostic.json.gz']
    spec = importlib.util.spec_from_file_location('freeze_post_terrain', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py')
    freeze = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(freeze)
    freeze.freeze(BATCH, 'changed-terrain-four-original-post-footing-candidate-v1', paths,
        dict(uids=[row['uid']], terrainProposalChanged=True, sourceGeometryChanges=0,
             rootCredit=False, physicalAccepted=False, installationApproved=False))
    print(json.dumps(dict(changedTerrainRecords=len(proof['changedTerrainVertexRecords']),
                         changedTerrainFaces=len(proof['changedIncidentTerrainFaces']),
                         parts=len(rows), samples=[len(r['completeOriginalSamples']) for r in rows])), flush=True)


if __name__ == '__main__':
    main()
