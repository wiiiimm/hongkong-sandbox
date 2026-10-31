"""Measure original upward surfaces above an estimated current BASIC roof.

This nominates an ancillary association; projection/height is not ownership,
structural support, suppression or publication permission.
"""
import argparse
import uuid
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_low_face_group_views_v2_20261026 import groups


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['batch','capture','contacts','uid','foreign']:
        p.add_argument('--'+name, required=True)
    a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch and a.uid != a.foreign
    base = ROOT/'docs/astra-city/government-import'
    doc = base/a.batch
    assert not doc.exists()
    refs, pins = [Path(__file__), HERE/'exact_packed_world_geometry_20261009.py',
                  HERE/'original_low_face_group_views_v2_20261026.py'], {}
    for name in [a.capture,a.contacts]:
        directory = base/name
        _, bound = authenticate(directory)
        refs.append(directory/'result.json')
        for path, sha in bound.items():
            assert path not in pins or pins[path] == sha
            pins[path] = sha

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selected = take(base/a.capture/'selection.json.gz')
    row = next(r for r in selected['rows'] if r['uid'] == a.uid)
    basic = next(r for r in take(base/a.contacts/'basic.json')['rows'] if r['uid'] == a.foreign)
    path = ROOT/row['candidate']['path']
    assert digest(path.read_bytes()) == row['sourceSHA256']
    refs.append(path)
    claim = reservations.claim('original-upper-roof-context-'+str(uuid.uuid4()),
        ['building:'+a.uid,'building:'+a.foreign], batch=a.batch, ttl=1800)
    assert claim['ok']
    lease = claim['reservation']
    try:
        tri = decode_original_world_triangles(path.read_bytes())
        assert len(tri) == row['triangles']
        points = np.asarray(basic['position']).reshape(-1,3)
        highest_basic = float(points[:,1].max())
        form = basic['currentBuilding']
        footprint = shapely.GeometryCollection()
        for ring in form['rings']:
            footprint = footprint.symmetric_difference(shapely.Polygon(ring))
        assert footprint.is_valid and footprint.area > 0
        cross = np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])
        candidate_ids = np.flatnonzero((cross[:,1] > 0) & (tri[:,:,1].min(1) > highest_basic))
        ids = [int(i) for i in candidate_ids if shapely.Polygon(tri[i][:,[0,2]]).intersects(footprint)]
        projection = shapely.union_all([shapely.Polygon(tri[i][:,[0,2]]) for i in ids])
        components = groups(tri, list(range(len(tri))))
        involved = [dict(component=index, completeOriginalFaceIds=faces,
            upperRoofFaceIds=sorted(set(faces)&set(ids)),
            completeComponentBounds=[tri[faces].min((0,1)).tolist(),tri[faces].max((0,1)).tolist()])
            for index,faces in enumerate(components) if set(faces)&set(ids)]
        detail = dict(sourceSHA256=row['sourceSHA256'], originalWorldSHA256=digest(tri.astype('<f8').tobytes()),
            completeSourceFaces=len(tri), completeVertexConnectedComponents=len(components),
            basicWholeMeshHighestY=highest_basic, targetAreaM2=footprint.area,
            upwardFacesWhollyAboveBasicRoof=ids,
            upwardFaceVertices=[dict(sourceFace=i,vertices=tri[i].tolist()) for i in ids],
            upperProjectionTargetIntersectionM2=projection.intersection(footprint).area,
            upperProjectionTargetCoverage=projection.intersection(footprint).area/footprint.area,
            upperProjectionMissingTargetM2=footprint.difference(projection).area,
            upperProjectionExcessM2=projection.difference(footprint).area,
            completeOriginalComponents=involved, sourceFaceSelectionIsDiagnosticOnly=True)
        save(doc/'roof-context.json.gz',detail)
        out = dict(uids=[a.uid,a.foreign],sourceSHA256=row['sourceSHA256'],
            completeSourceFaces=len(tri), originalUpperRoofFaces=len(ids),
            basicHighestY=highest_basic, upperRoofTargetCoverage=detail['upperProjectionTargetCoverage'],
            basicSourceMetadata={k:form.get(k) for k in ['base','height','baseSource','heightSource','baseHeightHKPD','topHeightHKPD','buildingCSUID']},
            sourceGeometryChanges=0, identityAccepted=False, physicalAccepted=False,
            visibilitySuppressionApproved=False, installationApproved=False,
            qualification='Complete original source retained. Strictly upward original facets wholly above the actual BASIC maximum Y are measured against its exact current footprint; all incident complete vertex-connected original components are recorded. Numeric Float64 projection context only, not a rational maximum/coverage certificate, authoritative ancillary ownership or a structural contact/root proof. No model, baseline height or visibility changes.')
        save(doc/'summary.json',out)
        assert reservations.owns(lease)
        module('original_basic_upper_roof_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
            a.batch,'complete-original-upper-roof-basic-footprint-context',list(dict.fromkeys(refs)),out)
        print(dict(upperRoofFaces=len(ids),coverage=detail['upperProjectionTargetCoverage'],
                   missingM2=detail['upperProjectionMissingTargetM2'],components=len(involved)),flush=True)
    finally:
        assert reservations.release(lease)['ok']


if __name__ == '__main__':
    main()
