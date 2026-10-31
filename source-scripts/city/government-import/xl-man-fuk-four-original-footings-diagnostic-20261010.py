"""Record complete original samples for four still-unrooted Man Fuk parts.

Independent exact finite ground columns; no threshold change or root credit.
"""
import importlib.util
import json
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_wall_rim_accounting_20261009 import original_samples
from original_bound_facet_wall_context_v2_20261010 import exposure_at_vertex

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-man-fuk-four-original-footings-diagnostic-20261010'
DOC = BASE / BATCH
PHYSICAL = BASE / 'government-xl-man-fuk-complete-retained-original-physical-v5-20261010'
GRAPH = BASE / 'government-xl-man-fuk-v5-complete-original-support-20261010'
GRADE = BASE / 'government-xl-man-fuk-v5-complete-finite-wall-grade-source-20261010'


def main():
    assert not DOC.exists()
    row = read(PHYSICAL / 'selection.json.gz')['rows'][0]
    asset = ROOT / row['candidate']['path']
    raw = asset.read_bytes()
    assert digest(raw) == row['sourceSHA256'] == '22b458321ca483c53324ee152cb27c382e5ac4dfd745974f169b1c551ac8a6c1'
    original = decode_original_world_triangles(raw)
    graph = read(GRAPH / 'diagnostic.json.gz')
    grade = read(GRADE / 'diagnostic.json.gz')
    assert grade['unresolvedOriginalComponents'] == [2, 3, 4, 5]
    runtime_path = HERE / 'local' / PHYSICAL.name / 'runtime-geometry.json.gz'
    runtime = read(runtime_path)['rows'][0]
    positions = np.asarray(runtime['position']).reshape(-1, 3)
    index = np.asarray(runtime['index'], np.uint32).reshape(-1, 3)
    actual = positions[index]
    assert original.shape == actual.shape == (10661, 3, 3)
    ground = np.asarray(runtime['drawnGroundGeometry']).reshape(-1, 3, 3)
    original_positions = np.empty_like(positions)
    assigned = {}
    for ids, face in zip(index, original):
        for i, v in zip(ids, face):
            i = int(i)
            if i in assigned:
                assert np.array_equal(v, assigned[i])
            else:
                assigned[i] = v
                original_positions[i] = v
    assert len(assigned) == len(positions) and np.array_equal(original_positions[index], original)
    rows = []
    for component in [2, 3, 4, 5]:
        part = graph['components'][component]
        faces = part['globalOriginalFaces']
        ids = sorted(set(index[faces].reshape(-1).tolist()))
        mapping = {v: i for i, v in enumerate(ids)}
        cp = original_positions[ids]
        ci = np.asarray([[mapping[int(v)] for v in f] for f in index[faces]], np.uint32)
        bottom = float(cp[:, 1].min())
        samples = original_samples(cp, ci, bottom)
        for sample in samples:
            proof = exposure_at_vertex(sample['point'], ground)
            sample['completeExactFiniteGroundColumn'] = proof
        rows.append(dict(component=component, completeOriginalFaces=faces,
                         completeOriginalTriangles=original[faces].tolist(),
                         rawOrdinaryRootFailure=graph['ordinaryRootProofs'][component],
                         completeOriginalSamples=samples,
                         qualification='Literal original samples and all finite current ground columns only. Any existing strict support rule must still be independently replayed.'))
    paths = [Path(__file__), asset, runtime_path, PHYSICAL / 'selection.json.gz',
             GRAPH / 'diagnostic.json.gz', GRAPH / 'result.json', GRADE / 'diagnostic.json.gz', GRADE / 'result.json',
             HERE / 'exact_packed_world_geometry_20261009.py', HERE / 'original_wall_rim_accounting_20261009.py',
             HERE / 'original_bound_facet_wall_context_v2_20261010.py', HERE / 'exact_original_triangle_pair_column_gap_20261010.py']
    result = dict(uid=row['uid'], sourceSHA256=row['sourceSHA256'], rows=rows,
                  completeOriginalWorldSHA256=digest(original.tobytes()),
                  completeActualRenderedWorldSHA256=digest(actual.tobytes()),
                  completeActualDrawnGroundSHA256=digest(ground.tobytes()),
                  sourceGeometryChanges=0, rootCredit=False, physicalAccepted=False, installationApproved=False,
                  evidenceRefs=[dict(path=str(p.relative_to(ROOT)), sha256=digest(p.read_bytes())) for p in paths])
    save(DOC / 'diagnostic.json.gz', result)
    spec = importlib.util.spec_from_file_location('freeze_four_footings', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py')
    freeze = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(freeze)
    freeze.freeze(BATCH, 'complete-four-unrooted-original-footing-samples-v1', paths,
                  dict(uids=[row['uid']], unresolvedComponents=[2, 3, 4, 5], rootCredit=False, physicalAccepted=False,
                       installationApproved=False, sourceGeometryChanges=0))
    print(json.dumps(dict(parts=len(rows), samples=[len(r['completeOriginalSamples']) for r in rows])), flush=True)


if __name__ == '__main__':
    main()
