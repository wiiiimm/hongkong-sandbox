"""ROOT's source-bound identity review; no placement, collision or publication waiver."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
SOURCE = BASE / 'government-xl-china-ferry-five-original-identity-v2-20261020'
EXTENT = BASE / 'government-xl-china-ferry-companion-extent-v1-20261020'
PRIMARY = BASE / 'government-xl-china-ferry-six-primary-records-v1-20261020'
BATCH = 'government-xl-china-ferry-companion-identity-review-v1-20261020'
DOC = BASE / BATCH
assert not DOC.exists()
pins = {}
refs = [Path(__file__)]
with connect() as db:
    db.execute('SET TRANSACTION READ ONLY')
    for folder in (SOURCE, EXTENT, PRIMARY):
        receipt = read(folder / 'result.json')
        assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                          (receipt['jobId'],)).fetchone() == ('complete', receipt)
        refs.append(folder / 'result.json')
        for e in receipt['evidenceRefs']:
            assert e['path'] not in pins or pins[e['path']] == e['sha256']
            pins[e['path']] = e['sha256']
for p, h in pins.items():
    assert digest((ROOT / p).read_bytes()) == h, p
footprints = {f['attributes']['BuildingCSUID']: f['attributes']
              for f in read(PRIMARY / 'footprints.json')['features']}
relations = {f['attributes']['BuildingCSUID']: f['attributes']['BuildingStructureID']
             for f in read(PRIMARY / 'relations.json')['features']}
structures = {f['attributes']['BuildingStructureID']: f['attributes']
              for f in read(PRIMARY / 'structures.json')['features']}
reviews = []
explanations = {
    'landsd/238208:0': (
        'The viewed complete original is the elongated Tower 2 body with a low '
        'projecting canopy carried in the same verified source graph. The tower '
        'body follows the official tower footprint. Its full excess projection '
        'lies within the official podium and intersects no unrelated form. The '
        '13m automated extent flag describes that authored canopy, not a misplaced '
        'tower. Geometry over the open-sided footprint is retained, but projection '
        'coverage alone does not establish that ancillary identity or permit suppressing it.'),
    'landsd/252498:0': (
        'The viewed complete original has the same elongated two-lobed body and '
        'paired middle recesses as Tower 5. The 94.30% automated footprint coverage '
        'results from narrow perimeter differences; the model is not a missing '
        'tower section. Its exact named graph, encoded georef cell, current CSUID '
        'and 14-storey tower record identify this source. Preserve the original '
        'placement and outline; do not reshape it to match the 2D polygon.')
}
for row in read(SOURCE / 'selection.json.gz')['rows']:
    uid = row['uid']
    if uid not in explanations:
        continue
    key = uid.split('/')[1]
    proof = read(SOURCE / key / 'identity.json')
    measured = read(EXTENT / (key + '.json'))
    building = row['source']['building']
    csuid = building['buildingCSUID']
    assert row['sourceSHA256'] == measured['sourceSHA256'] == proof['sourceSHA256']
    assert proof['exactCurrentComponentRoute']['qualified']
    assert proof['exactWholeCellCoverage']['covered']
    assert proof['originalOwnership']['sourceGraphVerified']
    assert proof['originalOwnership']['originalRootName'] == row['modelId']
    assert proof['freshCurrentIdentity']['exactObjectAndCSUID']
    assert proof['freshCurrentIdentity']['unrelatedIntersectingForms'] == 0
    official = footprints[csuid]
    structure = structures[relations[csuid]]
    assert official['Status'] == 'Active' and official['BuildingBlockType'] == 'Tower'
    assert official['BaseHeight'] == building['baseHeightHKPD']
    assert official['TopHeight'] == building['topHeightHKPD']
    assert structure['OPNo'] == 'K23/88' and structure['Storeys'] == 14
    assert structures[relations['3526717841P20050930']]['OPNo'] == structure['OPNo']
    expected = (
        {'fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM',
         'full-source-maximum-extent'} if uid == 'landsd/238208:0'
        else {'fresh-current-spatial-bound:targetCoveredBySourceProjection',
              'full-source-target-coverage'})
    assert set(proof['reasons']) == expected
    image = EXTENT / (key + '.png')
    reviews.append(dict(
        uid=uid, sourceSHA256=row['sourceSHA256'], modelId=row['modelId'],
        reviewer='Codex ROOT', imageActuallyViewed=dict(
            path=str(image.relative_to(ROOT)), sha256=digest(image.read_bytes())),
        rawIdentityReasons=proof['reasons'], sourceIdentityApproved=True,
        observation=explanations[uid], primaryCSUID=csuid,
        companionPodiumRequired='landsd/285642:0',
        ancillaryIdentityApproved=False, suppressesBuildingUids=[],
        geometryChanges=0, placementApproved=False, publicationApproved=False))
assert len(reviews) == 2
save(DOC / 'review.json', dict(rows=reviews, aiUsedForEvidenceInterpretation=True,
                             aiGeometryModelling=False, installationApproved=False))
refs.extend(ROOT / p for p in pins)
module('china_companion_review_freeze',
       HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
           BATCH, 'two-exact-original-companion-source-identity-reviews', refs,
           dict(uids=[r['uid'] for r in reviews], rows=reviews,
                installationApproved=False, physicalAndRuntimeChecksRequired=True))
