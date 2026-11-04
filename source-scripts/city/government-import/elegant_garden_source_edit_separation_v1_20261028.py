"""Locate every unresolved neighbour relative to the complete original project.

Diagnostic only: no mask or terrain is constructed and no obligation is waived.
"""
import uuid
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon, MultiPoint, box
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BASE = ROOT/'docs/astra-city/government-import'
BATCH = 'government-xl-elegant-garden-source-edit-separation-v1-20261028'
DOC = BASE/BATCH
CAP = BASE/'government-xl-elegant-garden-existing-ground-runtime-v2-20261027'
SCOPE = BASE/'government-xl-elegant-garden-private-inset-scope-v1-20261027'
FORMS = BASE/'government-xl-elegant-garden-private-inset-forms-v1-20261027'
TARGETS = ['landsd/173532:0', 'landsd/173768:0', 'landsd/236170:0']


def main():
    assert not DOC.exists()
    refs, pins = [Path(__file__), HERE/'exact_packed_world_geometry_20261009.py'], {}
    for directory in [CAP, SCOPE, FORMS]:
        _, bound = authenticate(directory)
        refs.append(directory/'result.json')
        for path, sha in bound.items():
            assert path not in pins or pins[path] == sha
            pins[path] = sha

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selection = take(CAP/'selection.json.gz')['rows']
    forms = take(SCOPE/'form-obligations.json.gz')
    native = take(SCOPE/'native-obligations.json.gz')
    flags = read(FORMS/'result.json')['flagged']
    assert {r['uid'] for r in selection} == set(TARGETS)
    assert len(flags) == 4 and len(native) == 3
    manifest_path = ROOT/'3d-viewer/city/data/manifest.json'
    manifest = read(manifest_path)
    refs.append(manifest_path)
    current_entries = {}
    for url in manifest['officialModelCatalogues']:
        path = ROOT/'3d-viewer'/url
        refs.append(path)
        for entry in read(path)['models']:
            if entry['uid'] in {r['uid'] for r in native}:
                current_entries[entry['uid']] = entry
    for row in native:
        assert current_entries[row['uid']]['sha256'] == row['sourceSHA256']
    resources = sorted('building:'+uid for uid in TARGETS+[r['uid'] for r in flags]+[r['uid'] for r in native])
    claim = reservations.claim('elegant-source-edit-separation-'+str(uuid.uuid4()), resources, batch=BATCH, ttl=1800)
    assert claim['ok']
    lease = claim['reservation']
    try:
        projections, originals = [], []
        for row in selection:
            path = ROOT/row['candidate']['path']
            sha = digest(path.read_bytes())
            assert sha == row['sourceSHA256']
            refs.append(path)
            triangles = decode_original_world_triangles(path.read_bytes())
            primitives = [MultiPoint(face[:, [0, 2]]).convex_hull for face in triangles]
            projection = shapely.union_all(primitives)
            assert not projection.is_empty
            projections.append(projection)
            originals.append(dict(uid=row['uid'], sourceSHA256=sha, allFaces=len(triangles),
                                  projectedAreaM2=projection.area, bounds=projection.bounds))
        project = shapely.union_all(projections)
        rows = []
        for flag in flags:
            form = next(r for r in forms if r['uid'] == flag['uid'])
            tile = ROOT/'3d-viewer/city/data/tiles'/(form['tile']+'.json')
            current = read(tile)
            # Only current exact form bytes may carry forward this old obligation.
            matches = [r for r in current['buildings'] if r['uid'] == form['uid']]
            assert matches == [form]
            refs.append(tile)
            polygon = Polygon(form['rings'][0], form['rings'][1:])
            assert polygon.is_valid and not polygon.is_empty
            rows.append(dict(uid=form['uid'], name=form.get('name'), rawFlag=flag,
                footprintOverlapM2=polygon.intersection(project).area,
                originalProjectionDistanceM=polygon.distance(project),
                entirelyOutsideOneMetreCore=polygon.disjoint(project.buffer(1)),
                entirelyOutsideTenMetreApron=polygon.disjoint(project.buffer(11)),
                independentlyPassesTerrainRegression=False))
        retained = []
        for row in native:
            rectangles = [box(bounds[0][0], bounds[0][2], bounds[1][0], bounds[1][2]) for bounds in row['completeFourWorldBounds']]
            bounds = shapely.union_all(rectangles)
            retained.append(dict(uid=row['uid'], sourceSHA256=row['sourceSHA256'],
                conservativeFourWorldBoundsDistanceM=bounds.distance(project),
                conservativeBoundsOutsideOneMetreCore=bounds.disjoint(project.buffer(1)),
                conservativeBoundsOutsideTenMetreApron=bounds.disjoint(project.buffer(11)),
                fullOriginalNativeNonregressionStillRequired=True))
        summary = dict(uids=TARGETS, originalSources=originals, flaggedForms=rows, retainedNative=retained,
            currentManifestSHA256=digest(manifest_path.read_bytes()),
            originalProjectProjectionAreaM2=project.area, sourceGeometryChanges=0,
            installationApproved=False, permanentRejection=False,
            qualification='Complete original projected finite primitives, including lines and points. Current exact BASIC form bytes and retained native source hashes verified. Separation only informs the next private terrain recipe; no terrain built, root/native overlap resolved, flag cleared or current physical/identity/runtime/browser approval granted.')
        save(DOC/'summary.json', summary)
        assert reservations.owns(lease)
        module('elegant_source_edit_separation_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
            BATCH, 'complete-original-project-neighbour-edit-separation-diagnostic', list(dict.fromkeys(refs)), summary)
        print(dict(forms=rows, retained=retained), flush=True)
    finally:
        assert reservations.release(lease)['ok']


if __name__ == '__main__':
    main()
