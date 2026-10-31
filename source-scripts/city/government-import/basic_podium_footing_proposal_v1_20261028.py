"""Private continuous-ground footing proposal for an unchanged surveyed BASIC podium.

Exercises an existing renderer mechanism only. The canopy-only publisher does
not accept this proposal; a separate qualified contract and scene checks remain.
"""
import argparse
import subprocess
import uuid
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['batch', 'runtime', 'contacts', 'uid']:
        p.add_argument('--'+name, required=True)
    a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base = ROOT/'docs/astra-city/government-import'
    doc = base/a.batch
    assert not doc.exists()
    refs, pins = [Path(__file__)], {}
    for name in [a.runtime, a.contacts]:
        _, bound = authenticate(base/name)
        refs.append(base/name/'result.json')
        for path, sha in bound.items():
            assert path not in pins or pins[path] == sha
            pins[path] = sha
    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    basic = take(base/a.contacts/'basic.json')
    assert basic['startAndEndInputHashesVerified']
    row = next(r for r in basic['rows'] if r['uid'] == a.uid)
    b = row['currentBuilding']
    assert b['structureType'] == 'Podium' and b['kind'] == 'yes' and b['minimum'] == 0
    assert b['baseSource'] == b['heightSource'] == 'landsd'
    assert b['base'] == b['baseHeightHKPD'] and b['base']+b['height'] == b['topHeightHKPD']
    assert not b.get('modelGeometry') and b.get('foundationBase') is None
    selection = take(base/a.runtime/'selection.json.gz')['rows']
    assert a.uid not in {r['uid'] for r in selection}
    manifestpath = ROOT/'3d-viewer/city/data/manifest.json'
    manifest = take(manifestpath)
    assert not any(m['uid'] == a.uid for url in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models'])
    tile = ROOT/'3d-viewer/city/data/tiles'/(b['tile']+'.json')
    assert [f for f in read(tile)['buildings'] if f['uid'] == a.uid] == [b]
    refs.append(tile)
    claim = reservations.claim('basic-podium-footing-'+str(uuid.uuid4()),
        sorted({'building:'+a.uid, 'terrain:city/data/terrain.json'}|{'building:'+r['uid'] for r in selection}), batch=a.batch, ttl=1800)
    assert claim['ok']
    lease = claim['reservation']
    try:
        captured = take(HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']
        assert {r['uid']: r['sourceSHA256'] for r in captured} == {r['uid']: r['sourceSHA256'] for r in selection}
        # Deduplicate identical actual drawn facets, without generating or moving
        # terrain. Every contributing capture stays bound in the receipt.
        ground = np.unique(np.concatenate([np.asarray(r['drawnGroundGeometry'], dtype='<f8').reshape(-1, 3, 3) for r in captured]), axis=0)
        polygon = shapely.Polygon(b['rings'][0], b['rings'][1:])
        assert polygon.is_valid and polygon.area > 0
        shapes = shapely.polygons(ground[:, :, [0, 2]])
        valid = shapely.area(shapes) > 1e-10
        coverage = shapely.union_all(shapes[valid])
        uncovered = polygon.difference(coverage).area
        assert uncovered < 1e-8, 'Incomplete actual terrain under the whole footprint'
        heights, ids = [], []
        for i in np.flatnonzero(valid & shapely.intersects(shapes, polygon)):
            clipped = shapes[i].intersection(polygon)
            if clipped.area <= 1e-10:
                continue
            xy = shapely.get_coordinates(clipped)
            one, two, three = ground[i]
            normal = np.cross(two-one, three-one)
            y = one[1]-(normal[0]*(xy[:, 0]-one[0])+normal[2]*(xy[:, 1]-one[2]))/normal[1]
            heights.extend(y.tolist())
            ids.append(int(i))
        assert heights
        low, high = min(heights), max(heights)
        assert high < b['base']-.02, 'Existing body is not wholly above the drawn ground'
        foundation = low-.02
        save(doc/'input.json', dict(building=b, expectedUid=a.uid))
        save(doc/'proposal.json', dict(uid=a.uid, originalBase=b['base'], foundationBase=foundation,
            surveyedElevationsUnchanged=True, scope='BASIC-only private proposed footing', publication=False))
        tool = HERE/'basic_podium_footing_geometry_v1_20261028.mjs'
        refs.append(tool)
        with (doc/'worker.log').open('w') as log:
            subprocess.run(['node', str(tool), str(doc.relative_to(ROOT))+'/'], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
        proof = read(doc/'render-proof.json')
        assert proof['completeBasicBodyAndIndicesExactlyUnchanged'] and proof['governmentGeometryChanges'] == 0
        verticals = []
        for i in np.flatnonzero(~valid):
            face = ground[i]
            line = shapely.MultiPoint(face[:, [0, 2]]).convex_hull
            if line.intersects(polygon):
                verticals.append(dict(faceIndex=int(i), vertices=face.tolist()))
        save(doc/'continuous-ground.json.gz', dict(completeDrawnGroundSHA256=digest(ground.tobytes()),
            clippedPositiveAreaFaceIds=ids, uncoveredAreaM2=uncovered, groundRange=[low, high],
            verticalOrDegenerateContacts=verticals, foundationBottom=foundation, foundationTop=b['base']))
        result = dict(uids=[a.uid], uid=a.uid, foundationBase=foundation, originalBase=b['base'],
            fullPositiveAreaGroundWithinFooting=True, fullFootprintCovered=True,
            completeBasicBodyAndIndicesExactlyUnchanged=True, renderProof=proof,
            addedIllustrativeFootingOnly=True, sourceGeometryChanges=0,
            governmentGeometryChanges=0, privateIllustrativeGeometryChanges=1,
            verticalGroundContactsRequireReview=len(verticals),
            physicalAcceptance=False, collisionAndVisualAcceptancePending=True,
            publicationAdapterAvailable=False, installationApproved=False,
            qualification='Private exercise of the already implemented procedural BASIC foundation volume. All surveyed fields, roof, original complete BASIC vertices/indices and all government meshes remain fixed. Full continuous nonvertical terrain/footprint bounds lie inside the added volume; vertical contacts are explicit and unapproved. No canopy-only publisher exemption, native support credit, source identity, future native activation compatibility or live update is approved.')
        save(doc/'summary.json', result)
        for path, sha in proof['inputHashes'].items():
            assert digest((ROOT/path).read_bytes()) == sha
            refs.append(ROOT/path)
        assert reservations.owns(lease)
        module('basic_podium_footing_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'private-existing-basic-podium-footing-continuous-ground-proposal', list(dict.fromkeys(refs)), result)
        print(dict(uid=a.uid, groundRange=[low, high], foundationBase=foundation, bodyUnchanged=True, verticalContacts=len(verticals)), flush=True)
    finally:
        assert reservations.release(lease)['ok']


if __name__ == '__main__':
    main()
