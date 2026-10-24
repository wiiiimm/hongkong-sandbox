"""Exact Pacifica podium identity review; independent physical gates remain open."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_georef_cell_identity_20261009 import verify_files

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-pacifica-podium-identity-review-v1-20261019'
DOC = BASE / BATCH
LOCAL = HERE / 'local' / BATCH
PAIR = BASE / 'government-xl-pacifica-original-assembly-v1-20261019'
VIEWS = BASE / 'government-xl-pacifica-podium-identity-views-v1-20261019'
CONTEXT = BASE / 'government-xl-next-twenty-original-identity-v1-20261018/283036:0'

def main():
    assert not DOC.exists()
    pins, refs = {}, [Path(__file__)]
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        for folder in [PAIR, VIEWS]:
            receipt = read(folder / 'result.json')
            assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (receipt['jobId'],)).fetchone() == ('complete', receipt)
            refs.append(folder / 'result.json')
            for e in receipt['evidenceRefs']:
                assert e['path'] not in pins or pins[e['path']] == e['sha256']
                pins[e['path']] = e['sha256']
    for p, h in pins.items():
        assert digest((ROOT / p).read_bytes()) == h, p
    row = next(r for r in read(PAIR / 'selection.json.gz')['rows'] if r['uid'] == 'landsd/283036:0')
    proof = verify_files(row, read(CONTEXT / 'context.json'), LOCAL / '283036:0')
    old = read(CONTEXT / 'identity.json')
    for k in ['sourceSHA256', 'sourceFormSHA256', 'worldTrianglesSHA256', 'freshCurrentIdentity', 'reasons']:
        assert proof[k] == old[k], k
    assert proof['originalOwnership']['sourceGraphVerified']
    assert proof['exactCurrentComponentRoute']['qualified']
    assert proof['exactWholeCellCoverage']['covered']
    assert proof['geographicCell']['targetCoversWholeCell']
    assert set(proof['reasons']) == {'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2', 'full-source-unrelated-overlap'}
    projection = proof['originalOwnership']['fullProjection']
    assert projection['exactObjectAndCSUID']
    assert projection['targetCoveredBySourceProjection'] > .996
    assert projection['sourceExcessMaximumDistanceFromTargetM'] < 8.887
    others = [f for f in projection['intersectingForms'] if f['uid'] != row['uid'] and not f['sameParent'] and not f['sharedOsmReference']]
    assert {f['uid'] for f in others} == {'landsd/265478:0', 'landsd/283034:0', 'landsd/77278:0'}
    images = [VIEWS / (n + '.png') for n in ['whole', 'liberte-edge', 'mall-join']]
    save(DOC / '283036:0-review.json', dict(
        uid=row['uid'], reviewer='Codex ROOT', reviewType='exact-original-podium-identity',
        sourceSHA256=row['sourceSHA256'], sourceFormSHA256=proof['sourceFormSHA256'],
        worldTrianglesSHA256=proof['worldTrianglesSHA256'], modelId=row['modelId'], sourceFaces=row['triangles'],
        identityOnlyApproved=True, identityReviewApproved=True,
        identityProof=dict(exactObjectId=True, exactBuildingCSUID=True, uniqueViewerMatch=True, identityAccepted=True),
        rawProof=proof, rawReasonsRetained=proof['reasons'],
        imagesActuallyInspected=[dict(path=str(p.relative_to(ROOT)), sha256=digest(p.read_bytes())) for p in images],
        reviewBasis=[
            'Exact government root, ObjectID and CSUID route bind the unchanged source to this podium; full cell and source graph checks pass.',
            'The inspected complete green source follows the recorded Pacifica podium and joins the purple installed Pacifica component. Its footprint covers over 99.6 percent of the target.',
            'The unrelated-form warning includes the other Pacifica podium and Tower 5 in the same assembly. The Liberte overlap lies along the narrow shared edge visible in the inspected source views; it does not identify the green source as Liberte.',
            'This resolves source identity only. Authored overlap, shared edge collision, all tower support and complete foundation acceptance remain independent. No placement or publication approval is implied.'
        ], sourceIdentityReviewUsedAI=True, aiGeometryModelling=False,
        placementReviewed=False, publicationApproved=False, installationApproved=False))
    for p, h in pins.items():
        assert digest((ROOT / p).read_bytes()) == h, p
        refs.append(ROOT / p)
    refs.extend([CONTEXT / 'context.json', CONTEXT / 'identity.json', HERE / 'exact_original_georef_cell_identity_20261009.py'])
    refs.extend(p for p in LOCAL.rglob('*') if p.is_file())
    module('pacifica_podium_identity_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'exact-original-podium-identity-review', list(dict.fromkeys(refs)),
        dict(uids=[row['uid']], identityAccepted=True, installationApproved=False))

if __name__ == '__main__':
    main()
