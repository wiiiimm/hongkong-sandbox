"""Exact unnamed147996 source identity review; physical acceptance remains separate."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_georef_cell_identity_20261009 import verify_files

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-unnamed147996-identity-review-v1-20261020'
DOC = BASE / BATCH
LOCAL = HERE / 'local' / BATCH
PAIR = BASE / 'government-xl-next-twenty-current-terrain-v2-20261020'
VIEWS = BASE / 'government-xl-unnamed147996-whole-source-imagery-v1-20261020'
CONTEXT = BASE / 'government-xl-next-twenty-original-identity-v2-20261020/147996:0'

def main():
    assert not DOC.exists()
    pins, refs = {}, [Path(__file__)]
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        for folder in [VIEWS, BASE/'government-xl-unnamed147996-source-views-v1-20261020']:
            receipt = read(folder / 'result.json')
            assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (receipt['jobId'],)).fetchone() == ('complete', receipt)
            refs.append(folder / 'result.json')
            for e in receipt['evidenceRefs']:
                assert e['path'] not in pins or pins[e['path']] == e['sha256']
                pins[e['path']] = e['sha256']
    for p, h in pins.items():
        assert digest((ROOT / p).read_bytes()) == h, p
    row = next(r for r in read(PAIR / 'selection.json.gz')['rows'] if r['uid'] == 'landsd/147996:0')
    proof = verify_files(row, read(CONTEXT / 'context.json'), LOCAL / '147996:0')
    old = read(CONTEXT / 'identity.json')
    for k in ['sourceSHA256', 'sourceFormSHA256', 'worldTrianglesSHA256', 'freshCurrentIdentity', 'reasons']:
        assert proof[k] == old[k], k
    assert proof['originalOwnership']['sourceGraphVerified']
    assert proof['exactCurrentComponentRoute']['qualified']
    assert proof['exactWholeCellCoverage']['covered']
    assert proof['geographicCell']['targetCoversWholeCell']
    assert set(proof['reasons']) == {'fresh-current-spatial-bound:targetCoveredBySourceProjection','full-source-target-coverage'}
    projection=proof['originalOwnership']['fullProjection']
    assert projection['exactObjectAndCSUID'] and .8737 < projection['targetCoveredBySourceProjection'] < .8738
    assert 2.887 < projection['sourceExcessMaximumDistanceFromTargetM'] < 2.888
    assert projection['sourceExcessCoveredByUnrelatedFormsM2'] < .004
    assert {f['uid'] for f in projection['intersectingForms']} == {'landsd/147996:0'}
    images=[VIEWS/'region-147996:0.png',BASE/'government-xl-unnamed147996-source-views-v1-20261020/complete-source-four-views.png']
    save(DOC / '147996:0-review.json', dict(
        uid=row['uid'], reviewer='Codex ROOT', reviewType='exact-original-victoria-mall-identity',
        sourceSHA256=row['sourceSHA256'], sourceFormSHA256=proof['sourceFormSHA256'],
        worldTrianglesSHA256=proof['worldTrianglesSHA256'], modelId=row['modelId'], sourceFaces=row['triangles'],
        identityOnlyApproved=True, identityReviewApproved=True,
        identityProof=dict(exactObjectId=True, exactBuildingCSUID=True, uniqueViewerMatch=True, identityAccepted=True),
        rawProof=proof, rawReasonsRetained=proof['reasons'],
        imagesActuallyInspected=[dict(path=str(p.relative_to(ROOT)), sha256=digest(p.read_bytes())) for p in images],
        reviewBasis=[
            'Exact official ObjectID147996 and CSUID3503520469T20050430 uniquely route unchanged original B350352046901063C0 to this target; verified original graph and complete GeoRef cell agree. No alternative target is nominated by the current whole-map intersection evidence.',
            'The full original projected source covers 87.3778565% of the basic footprint and its maximum outward difference is 2.887443m. Both raw target-coverage flags remain recorded. A basic footprint is a proxy, and this difference does not contradict the exact original component route.',
            'ROOT inspected the four complete original views: a narrow tall slab with roof projections, vertical channels and a low end extension. This is consistent with the same narrow elongated target rather than a translated or rescaled unrelated source. No component was dropped or reconstructed.',
            'ROOT inspected the official aerial with unfitted source and target outlines. Both fall on the same narrow strip beside the larger roof. Shadows, resolution and unknown imagery date prevent precise facade/roof confirmation; the image is contextual corroboration, not the decisive identity evidence.',
            'The only positive-area intersecting form recorded by the current identity report is the target itself. The 0.003014 square metre residual unrelated overlap is retained. This identity-only judgement relies on exact official IDs, source graph, complete-cell routing and source/target correspondence; it grants no suppression, collision, placement, terrain or publication approval.',
            'No landmark name is assigned. Complete current terrain, retained actors, fallback, collision and browser acceptance remain required.'
        ], sourceIdentityReviewUsedAI=True, aiGeometryModelling=False,
        placementReviewed=False, publicationApproved=False, installationApproved=False))
    for p, h in pins.items():
        assert digest((ROOT / p).read_bytes()) == h, p
        refs.append(ROOT / p)
    refs.extend([CONTEXT / 'context.json', CONTEXT / 'identity.json', HERE / 'exact_original_georef_cell_identity_20261009.py'])
    refs.extend(p for p in LOCAL.rglob('*') if p.is_file())
    module('times_square_podium_identity_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'exact-original-unnamed147996-identity-review', list(dict.fromkeys(refs)),
        dict(uids=[row['uid']], identityAccepted=True, installationApproved=False))

if __name__ == '__main__':
    main()
