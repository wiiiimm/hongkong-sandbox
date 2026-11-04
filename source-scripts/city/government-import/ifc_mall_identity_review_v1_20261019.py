"""Exact Central Library podium identity review; independent physical gates remain open."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_georef_cell_identity_20261009 import verify_files

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-ifc-mall-identity-review-v1-20261019'
DOC = BASE / BATCH
LOCAL = HERE / 'local' / BATCH
PAIR = BASE / 'government-xl-ifc-mall-unchanged-ground-v1-20261019'
VIEWS = BASE / 'government-xl-ifc-original-identity-views-v1-20261019'
CONTEXT = BASE / 'government-xl-next-twenty-original-identity-v1-20261018/64856:0'

def main():
    assert not DOC.exists()
    pins, refs = {}, [Path(__file__)]
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        for folder in [VIEWS]:
            receipt = read(folder / 'result.json')
            assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (receipt['jobId'],)).fetchone() == ('complete', receipt)
            refs.append(folder / 'result.json')
            for e in receipt['evidenceRefs']:
                assert e['path'] not in pins or pins[e['path']] == e['sha256']
                pins[e['path']] = e['sha256']
    for p, h in pins.items():
        assert digest((ROOT / p).read_bytes()) == h, p
    row = next(r for r in read(PAIR / 'selection.json.gz')['rows'] if r['uid'] == 'landsd/64856:0')
    proof = verify_files(row, read(CONTEXT / 'context.json'), LOCAL / '64856:0')
    old = read(CONTEXT / 'identity.json')
    for k in ['sourceSHA256', 'sourceFormSHA256', 'worldTrianglesSHA256', 'freshCurrentIdentity', 'reasons']:
        assert proof[k] == old[k], k
    assert proof['originalOwnership']['sourceGraphVerified']
    assert proof['exactCurrentComponentRoute']['qualified']
    assert proof['exactWholeCellCoverage']['covered']
    assert proof['geographicCell']['targetCoversWholeCell']
    assert set(proof['reasons']) == {'fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent'}
    projection=proof['originalOwnership']['fullProjection']
    assert projection['exactObjectAndCSUID'] and .9998 < projection['targetCoveredBySourceProjection'] < 1
    assert 55.909 < projection['sourceExcessMaximumDistanceFromTargetM'] < 55.910
    assert projection['sourceExcessCoveredByUnrelatedFormsM2']==0
    assert {f['uid'] for f in projection['intersectingForms']}=={'landsd/64856:0','way/664250327:0','way/664250326:0','landsd/232441:0','landsd/161250:0','landsd/257115:0'}
    images = [VIEWS / (n + '.png') for n in ['whole', 'mall-front', 'mall-reverse']]
    save(DOC / '64856:0-review.json', dict(
        uid=row['uid'], reviewer='Codex ROOT', reviewType='exact-original-ifc-mall-identity',
        sourceSHA256=row['sourceSHA256'], sourceFormSHA256=proof['sourceFormSHA256'],
        worldTrianglesSHA256=proof['worldTrianglesSHA256'], modelId=row['modelId'], sourceFaces=row['triangles'],
        identityOnlyApproved=True, identityReviewApproved=True,
        identityProof=dict(exactObjectId=True, exactBuildingCSUID=True, uniqueViewerMatch=True, identityAccepted=True),
        rawProof=proof, rawReasonsRetained=proof['reasons'],
        imagesActuallyInspected=[dict(path=str(p.relative_to(ROOT)), sha256=digest(p.read_bytes())) for p in images],
        reviewBasis=[
            'Exact government ObjectID64856 and CSUID3432516207T20050430, unchanged original source graph, current component route, and exact whole one-metre GeoRef cell establish the source-to-form binding.',
            'ROOT inspected all three complete original-source exports. The green original source comprises the long mall with an arched central roof, end blocks and authored side extensions; it meets the installed orange One IFC podium and purple tower in unchanged native placement. Whole view shows the entire assembly; closer mall views intentionally crop the tower top.',
            'The narrow target footprint is 99.98356 percent covered. Complete source extensions reach 55.909822 m beyond it and intersect the recorded IFC mall assembly forms. Exact original projection evidence finds zero unrelated overlap; original side blocks and extensions remain intact.',
            'This source-specific identity decision retains both raw maximum-extent flags. It does not establish tower structural support: the strict combined-original interface has 462 unresolved samples and remains failed. Identity approval does not relabel that historical tower support.',
            'The preferred installation route uses unchanged existing terrain. Owned source grade, full runtime, collision, fallback and staged/live browser acceptance remain separate. No geometry editing or placement/publication approval is granted.'
        ], sourceIdentityReviewUsedAI=True, aiGeometryModelling=False,
        placementReviewed=False, publicationApproved=False, installationApproved=False))
    for p, h in pins.items():
        assert digest((ROOT / p).read_bytes()) == h, p
        refs.append(ROOT / p)
    refs.extend([CONTEXT / 'context.json', CONTEXT / 'identity.json', HERE / 'exact_original_georef_cell_identity_20261009.py'])
    refs.extend(p for p in LOCAL.rglob('*') if p.is_file())
    module('times_square_podium_identity_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'exact-original-ifc-mall-identity-review', list(dict.fromkeys(refs)),
        dict(uids=[row['uid']], identityAccepted=True, installationApproved=False))

if __name__ == '__main__':
    main()
