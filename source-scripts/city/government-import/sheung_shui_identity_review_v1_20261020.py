"""Exact Central Library podium identity review; independent physical gates remain open."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_georef_cell_identity_20261009 import verify_files

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-sheung-shui-identity-review-v1-20261020'
DOC = BASE / BATCH
LOCAL = HERE / 'local' / BATCH
PAIR = BASE / 'government-xl-sheung-shui-candidate-runtime-v2-20261020'
VIEWS = BASE / 'government-xl-sheung-shui-whole-source-imagery-v1-20261020'
CONTEXT = BASE / 'government-xl-next-twenty-original-identity-v2-20261020/56054:0'

def main():
    assert not DOC.exists()
    pins, refs = {}, [Path(__file__)]
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        for folder in [VIEWS, BASE/'government-xl-sheung-shui-source-imagery-overlay-v1-20261020', BASE/'government-xl-sheung-shui-aerial-observations-v1-20261020']:
            receipt = read(folder / 'result.json')
            assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (receipt['jobId'],)).fetchone() == ('complete', receipt)
            refs.append(folder / 'result.json')
            for e in receipt['evidenceRefs']:
                assert e['path'] not in pins or pins[e['path']] == e['sha256']
                pins[e['path']] = e['sha256']
    for p, h in pins.items():
        assert digest((ROOT / p).read_bytes()) == h, p
    row = next(r for r in read(PAIR / 'selection.json.gz')['rows'] if r['uid'] == 'landsd/56054:0')
    proof = verify_files(row, read(CONTEXT / 'context.json'), LOCAL / '56054:0')
    old = read(CONTEXT / 'identity.json')
    for k in ['sourceSHA256', 'sourceFormSHA256', 'worldTrianglesSHA256', 'freshCurrentIdentity', 'reasons']:
        assert proof[k] == old[k], k
    assert proof['originalOwnership']['sourceGraphVerified']
    assert proof['exactCurrentComponentRoute']['qualified']
    assert proof['exactWholeCellCoverage']['covered']
    assert proof['geographicCell']['targetCoversWholeCell']
    assert set(proof['reasons']) == {'fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent','fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'}
    projection=proof['originalOwnership']['fullProjection']
    assert projection['exactObjectAndCSUID'] and .9872 < projection['targetCoveredBySourceProjection'] < .9873
    assert 12.668 < projection['sourceExcessMaximumDistanceFromTargetM'] < 12.670
    assert 914.80 < projection['sourceExcessCoveredByUnrelatedFormsM2'] < 914.81
    assert {f['uid'] for f in projection['intersectingForms'] if not f['sameParent']} == {'landsd/74535:0','landsd/88048:0','landsd/47284:0','landsd/47324:0','landsd/87203:0'}
    images=[VIEWS/'region-56054:0.png']+[BASE/'government-xl-sheung-shui-source-imagery-overlay-v1-20261020'/('region-'+i+':0.png') for i in ['74535','88048','47284','47324','87203']]
    save(DOC / '56054:0-review.json', dict(
        uid=row['uid'], reviewer='Codex ROOT', reviewType='exact-original-sheung-shui-identity',
        sourceSHA256=row['sourceSHA256'], sourceFormSHA256=proof['sourceFormSHA256'],
        worldTrianglesSHA256=proof['worldTrianglesSHA256'], modelId=row['modelId'], sourceFaces=row['triangles'],
        identityOnlyApproved=True, identityReviewApproved=True,
        identityProof=dict(exactObjectId=True, exactBuildingCSUID=True, uniqueViewerMatch=True, identityAccepted=True),
        rawProof=proof, rawReasonsRetained=proof['reasons'],
        imagesActuallyInspected=[dict(path=str(p.relative_to(ROOT)), sha256=digest(p.read_bytes())) for p in images],
        reviewBasis=[
            'Exact government ObjectID56054 and CSUID3015841543T20050430, verified unchanged original graph, qualified current component route and exact whole GeoRef cell bind this source to the target.',
            'ROOT inspected complete official aerial overlay and all five detailed-source neighbour overlays. Without fitted translation or scale, the complete source perimeter follows the visible slaughterhouse wings, courtyard recesses and southern end block. Repeated curved side projections correspond to the source stair assemblies already inspected separately.',
            'The largest excess overlaps the end-wing roof margins of basic74535; narrow88048 follows the same long side feature. The remaining three basic records describe adjacent triangular/linear structures beside the detailed perimeter. Parent-null records are therefore not evidence of a different building identity. Their independent coverage remains required; this review authorises no removal or suppression of these five basic models.',
            'All four raw extent/overlap flags remain recorded. Aerial imagery has unknown capture date and cannot establish metre-level legal ownership or 3D collision clearance. This is source identity interpretation supported jointly by exact IDs, source graph, footprint evidence and observed whole-building correspondence.',
            'Terrain, collision, runtime, fallback and staged/live browser acceptance remain separate. No geometry edits, placement approval, basic-model suppression or publication approval is granted.'
        ], sourceIdentityReviewUsedAI=True, aiGeometryModelling=False,
        placementReviewed=False, publicationApproved=False, installationApproved=False))
    for p, h in pins.items():
        assert digest((ROOT / p).read_bytes()) == h, p
        refs.append(ROOT / p)
    refs.extend([CONTEXT / 'context.json', CONTEXT / 'identity.json', HERE / 'exact_original_georef_cell_identity_20261009.py'])
    refs.extend(p for p in LOCAL.rglob('*') if p.is_file())
    module('times_square_podium_identity_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'exact-original-sheung-shui-identity-review', list(dict.fromkeys(refs)),
        dict(uids=[row['uid']], identityAccepted=True, installationApproved=False))

if __name__ == '__main__':
    main()
