"""Source-only overlap role diagnosis; distinguish estimated foreign height."""
import importlib.util
import json
import uuid
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest, reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_mesh_components import face_components
from yoho_eight_related_original_podium_identity_20261009 import ring_poly

BATCH = 'government-xl-villa-premiere-original-overlap-primary-context-20261010'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
UID = 'landsd/89917:0'
OTHER = 'landsd/325786:0'
CSUIDS = ['2162333401P20050627', '2162233384T20211022']
ACQUIRED = DOC.parent / 'government-xl-villa-premiere-two-original-recovery-20261010'


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def main():
    assert not DOC.exists()
    claim = reservations.claim('villa-original-overlap-' + str(uuid.uuid4()),
        ['building:' + UID, 'building:' + OTHER], batch=BATCH, ttl=3600)
    assert claim['ok'], claim
    lease = claim['reservation']
    try:
        DOC.mkdir(parents=True)
        acquisition = read(ACQUIRED / 'selection.json.gz')
        assert len(acquisition['rows']) == 1 and acquisition['rows'][0]['uid'] == UID
        assert len(acquisition['missing']) == 1 and acquisition['missing'][0]['uid'] == OTHER
        row = acquisition['rows'][0]
        path = ROOT / row['candidate']['path']
        raw = path.read_bytes()
        assert digest(raw) == row['sourceSHA256']
        triangles = decode_original_world_triangles(raw)
        assert len(triangles) == row['triangles'] == 16669
        parts = face_components(triangles)
        manifest = ROOT / '3d-viewer/city/data/manifest.json'
        start_manifest = digest(manifest.read_bytes())
        final = module('villa_complete_current_forms', 'xl-final-script-pass.py')
        low, high = triangles.min(axis=(0, 1)), triangles.max(axis=(0, 1))
        forms = final.load_forms([low[0]-2, low[2]-2, high[0]+2, high[2]+2])
        own = next(b for b, _, _ in forms if b['uid'] == UID)
        foreign = next(b for b, _, _ in forms if b['uid'] == OTHER)
        projection = shapely.union_all(shapely.polygons(triangles[:, :, [0, 2]]))
        overlap = projection.difference(ring_poly(own['rings'])).intersection(ring_poly(foreign['rings']))
        ids = [i for i, face in enumerate(triangles)
               if shapely.Polygon(face[:, [0, 2]]).intersection(overlap).area > 0]
        assert ids and overlap.area > 1
        part_for = {int(face): index for index, group in enumerate(parts) for face in group}
        role_parts = sorted({part_for[i] for i in ids})
        primary = module('villa_exact_provider_query', 'xl-man-fuk-man-oi-primary-relations-20261010.py')
        primary.DOC = DOC
        where = 'BuildingCSUID IN (' + ','.join("'" + csuid + "'" for csuid in CSUIDS) + ')'
        features = primary.query(0, where, 'exact-current-primary', True)
        assert len(features) == 2 and {f['attributes']['BuildingCSUID'] for f in features} == set(CSUIDS)
        relations = primary.query(1002, where, 'exact-current-structure-relations')
        structure_ids = sorted({f['attributes']['BuildingStructureID'] for f in relations})
        structures = primary.query(1003, 'BuildingStructureID IN (' + ','.join(map(str, structure_ids)) + ')', 'exact-current-structures') if structure_ids else []
        plan = primary.fetch_pdf('epd-independent-villa-site-plan.pdf',
            'https://www.epd.gov.hk/eia/files/applications/en/pp_246/eia_1898/progress/action_1821/html/EM%26A%20Manual/Figures/Figure%206.3b%20-%20Mitigation%20Measures%20for%20Road%20Traffic%20Noise.pdf')
        if plan.get('isPDF'):
            import fitz
            document = fitz.open(DOC / 'epd-independent-villa-site-plan.pdf')
            save(DOC / 'epd-independent-villa-site-plan.pdf.text.json', [dict(page=i+1, text=p.get_text()) for i, p in enumerate(document)])
            for i, page in enumerate(document):
                page.get_pixmap(matrix=fitz.Matrix(2, 2)).save(DOC / f'epd-independent-villa-site-plan.pdf.page-{i+1}.png')
        normal = np.cross(triangles[ids, 1] - triangles[ids, 0], triangles[ids, 2] - triangles[ids, 0])
        diagnostic = dict(uid=UID, foreignUID=OTHER, sourceSHA256=row['sourceSHA256'],
            worldTrianglesSHA256=digest(triangles.astype('<f8').tobytes()), completeOriginalFaces=len(triangles),
            completeOriginalParts=len(parts), allOriginalPartFaceCounts=[len(group) for group in parts],
            currentForms=[b for b, _, _ in forms], exactPrimary=features, exactRelations=relations, exactStructures=structures,
            actualExcessOverlapM2=float(overlap.area), overlapGeometry=shapely.to_geojson(overlap),
            allOverlapOriginalFaceIds=ids, allOverlapOriginalFaces=triangles[ids].tolist(),
            allOverlapOriginalNormalVectors=normal.tolist(), overlapOriginalPartIds=role_parts,
            completeOverlapParts=[dict(part=index, faceIds=parts[index].tolist(), faces=triangles[parts[index]].tolist()) for index in role_parts],
            sourceOverlapYRange=[float(triangles[ids, :, 1].min()), float(triangles[ids, :, 1].max())],
            foreignHeightQualification=dict(base=foreign['base'], height=foreign['height'], baseSource=foreign['baseSource'], heightSource=foreign['heightSource'],
                providerBaseHeight=foreign['baseHeightHKPD'], providerTopHeight=foreign['topHeightHKPD'],
                exactOriginalUnavailable=True, nativeMissing=acquisition['missing'][0],
                surveyedSeparationClaim=False, sourceSupportCredit=False),
            actualProceduralForeignPrismTop=float(foreign['base'] + foreign['height']),
            entireOverlapFaceMinimumAboveProceduralPrism=float(triangles[ids, :, 1].min() - (foreign['base'] + foreign['height'])),
            sourceInputPath=str(path.relative_to(ROOT)), sourceInputSHA256=digest(raw),
            currentTileHashes={t: digest((ROOT / '3d-viewer' / t).read_bytes()) for _, _, t in forms},
            capturedManifestSHA256=start_manifest, finalManifestSHA256=digest(manifest.read_bytes()), primaryPlan=plan,
            identityAccepted=False, physicalAccepted=False, installationApproved=False, modelGeometryChanges=0,
            qualification='Source-only finite overlap role and independent primary-plan investigation. The current canopy height is estimated and its government original is unavailable: no surveyed separation, original-canopy silhouette, legal/shared ownership or support claim. Complete foreign actors and all raw overlap remain; future identity requires independent role review and fresh current binding.')
        save(DOC / 'diagnostic.json.gz', diagnostic)
        refs = [Path(__file__), HERE / 'xl-man-fuk-man-oi-primary-relations-20261010.py', HERE / 'exact_mesh_components.py',
                HERE / 'exact_packed_world_geometry_20261009.py', ACQUIRED / 'result.json', ACQUIRED / 'selection.json.gz', path]
        refs += [ROOT / '3d-viewer' / t for _, _, t in forms]
        result = module('villa_source_only_context_fence', 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
            BATCH, 'complete-original-villa-overlap-primary-role-diagnosis-v1', refs,
            dict(uids=[UID, OTHER], completeOriginalFaces=len(triangles), completeOriginalParts=len(parts),
                 overlapFaces=len(ids), overlapM2=float(overlap.area), foreignOriginalMissing=True,
                 foreignHeightEstimated=True, identityAccepted=False, physicalAccepted=False,
                 nextStep='Review complete unchanged overlap component, primary-plan/current canopy role and exact finite separation to the actual current procedural actor. Never describe estimated current height as surveyed or invent a missing source.',
                 qualification=diagnostic['qualification']))
        print(json.dumps(dict(jobId=result['jobId'], overlapFaces=len(ids), sourceParts=len(parts), roleParts=role_parts,
                              minimumAboveEstimatedCurrentPrism=diagnostic['entireOverlapFaceMinimumAboveProceduralPrism'], identityAccepted=False)), flush=True)
    finally:
        assert reservations.release(lease)['ok']


if __name__ == '__main__':
    main()
