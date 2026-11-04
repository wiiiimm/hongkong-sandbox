"""Three complete unchanged original sources against their recorded native caps.

Source-only nomination: no current identity, grounding, roof-role, retained native
reacceptance, terrain changes, or installation credit. Prior failures stay intact.
"""
from pathlib import Path
import importlib.util
import json
import numpy as np
from run import ROOT, HERE, read, save, digest, connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from exact_original_face_conservative_clearance_v5_20261010 import verify

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-parkview-next-three-original-cap-contacts-v1-20261011'
DOC = BASE / BATCH
RANK = BASE / 'xl-terrain-recovery-20261010-next-current-native-cap-source-only-ranking-v1'
PROBE = BASE / 'government-xl-terrain-recovery-parkview-block11-complete-original-proposed-current-probe-v4-20261011'
TARGETS = {
    'landsd/256319:0': (11351, 45867),
    'landsd/256116:0': (15614, 54418),
    'landsd/255646:0': (20200, 58397),
}


def ref(path):
    return dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()))


def main():
    assert not DOC.exists(), 'Preserve immutable completed diagnostics'
    helpers = ['exact_packed_world_geometry_20261009.py',
        'exact_original_shared_edge_component_census_v2_20261011.py',
        'exact_original_finite_triangle_contacts_20261010.py',
        'exact_original_shell_intersections_20261009.py',
        'exact_original_component_contacts_20261009.py',
        'exact_original_face_conservative_clearance_v5_20261010.py',
        'exact_original_projection_coverage_v2_20261010.py']
    helper_bindings = [ref(HERE / name) for name in helpers]
    rank = read(RANK / 'diagnostic.json.gz')
    selection = read(PROBE / 'selection.json.gz')
    native_row = next(r for r in selection['rows'] if r['uid'] == 'landsd/254491:0')
    native_path = ROOT / native_row['candidate']['path']
    assert digest(native_path.read_bytes()) == native_row['sourceSHA256']
    native = decode_original_world_triangles(native_path.read_bytes())
    assert native.shape == (63133, 3, 3)
    runtime_path = HERE / 'local' / PROBE.name / 'runtime-geometry.json.gz'
    runtime = next(r for r in read(runtime_path)['rows'] if r['uid'] == native_row['uid'])
    ground = np.asarray(runtime['drawnGroundGeometry'], dtype='<f8').reshape(-1, 3, 3)
    references = [ref(p) for p in [Path(__file__), RANK / 'diagnostic.json.gz',
        RANK / 'result.json', PROBE / 'selection.json.gz', PROBE / 'result.json',
        native_path, runtime_path]]
    with connect() as connection:
        connection.execute('SET TRANSACTION READ ONLY')
        for folder in [RANK, PROBE]:
            receipt = read(folder / 'result.json')
            assert connection.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                (receipt['jobId'],)).fetchone() == ('complete', receipt)
    rows = []
    for uid, (face_count, cap) in TARGETS.items():
        ranked = next(r for r in rank['rows'] if r['uid'] == uid)
        source_path = ROOT / ranked['cachedSource']['path']
        assert ref(source_path) == ranked['cachedSource']
        assert ranked['sourceSHA256'] == ranked['cachedSource']['sha256']
        assert ranked['completeOriginalFaces'] == face_count
        assert np.cross(native[cap, 1] - native[cap, 0], native[cap, 2] - native[cap, 0])[1] > 0
        assert any(p['nativeOriginalUpwardCapFace'] == cap and
            p['nativeUID'] == native_row['uid'] for p in ranked['exactOriginalNativeCapContacts'])
        source = decode_original_world_triangles(source_path.read_bytes())
        assert source.shape == (face_count, 3, 3) and np.isfinite(source).all()
        parts = census(source, list(range(face_count)))
        contacts = exact_finite_contacts(native, [cap], source, list(range(face_count)))
        body_by_face = {face: body for body, faces in enumerate(parts['sharedEdgeConnectedComponents'])
            for face in faces}
        positive = [p for p in contacts['contacts'] if p['dimension'] > 0]
        participating_faces = sorted({p['sourceFaceB'] for p in positive})
        assert all(face in body_by_face for face in participating_faces)
        cap_proof = verify(native[cap], ground)
        rows.append(dict(uid=uid, name=ranked['name'], source=ref(source_path),
            completeOriginalFaces=face_count, completeOriginalWorldSHA256=digest(source.tobytes()),
            completeOriginalNonzeroEdgeCensus=parts, nativeOriginalCapFace=cap,
            completeOwnedToOneOriginalCapContacts=contacts,
            positiveDimensionalContactSourceFaces=participating_faces,
            directlyContactingOwnedNonzeroEdgeBodies=sorted({body_by_face[f] for f in participating_faces}),
            wholeOriginalCapAgainstFrozenGround=cap_proof,
            historicalReasonsUnchanged=ranked['historicalReasons'],
            capGroundRootAccepted=False, currentSourceFiniteAcceptance=False,
            internalBodyContactsNotYetExamined=True, fullAcceptance=False))
        references.extend([ref(source_path), ranked['cachedSelection']])
        print(json.dumps(dict(uid=uid, faces=face_count,
            bodies=len(parts['sharedEdgeConnectedComponents']),
            positiveInterfaces=len(positive), directBodies=rows[-1]['directlyContactingOwnedNonzeroEdgeBodies'],
            conservativeCapCovered=cap_proof['groundProjectionCovered'],
            conservativeCapLower=cap_proof['exactCertifiedLowerClearanceM'])), flush=True)
    references.extend(helper_bindings)
    for reference in references:
        assert ref(ROOT / reference['path']) == reference
    save(DOC / 'diagnostic.json.gz', dict(uids=list(TARGETS), rows=rows,
        completeOriginalNativeFaces=63133, completeOriginalNativeWorldSHA256=digest(native.tobytes()),
        completeFrozenGroundFaces=len(ground), completeFrozenGroundSHA256=digest(ground.tobytes()),
        evidenceRefs=references, sourceOnly=True, historicalGroundContextOnly=True,
        sourceGeometryChanges=0, terrainChanges=0, currentAcceptance=False,
        nativeReacceptance=False, installationApproved=False, newlyInstalled=0))
    spec = importlib.util.spec_from_file_location('parkview_three_original_freeze',
        HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py')
    recorder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(recorder)
    receipt = recorder.freeze(BATCH, 'complete-original-three-parkview-cap-contact-census-source-only-v1',
        [ROOT / r['path'] for r in {r['path']: r for r in references}.values()],
        dict(uids=list(TARGETS), sourceGeometryChanges=0, terrainChanges=0,
            currentAcceptance=False, nativeReacceptance=False, installationApproved=False,
            newlyInstalled=0, noArchitecturalRoleClaim=True))
    print(json.dumps(dict(jobId=receipt['jobId'], newlyInstalled=0)), flush=True)


if __name__ == '__main__':
    main()
