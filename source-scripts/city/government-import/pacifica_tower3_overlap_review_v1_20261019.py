"""Review two exact authored trim faces; retain strict foundation failures verbatim."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-pacifica-tower3-overlap-review-v1-20261019'
DOC = BASE / BATCH
UID = 'landsd/75351:0'
MODES = ['original', 'literal', 'explicitLeftF32', 'explicitBalancedF32']
def folder(name):
    return BASE / ('government-xl-pacifica-' + name + '-20261019')

def main():
    assert not DOC.exists()
    foundation = folder('four-mode-foundations-v1')
    attribution = folder('tower3-burial-attribution-v1')
    binding = folder('wall-binding-v1')
    views = folder('buried-face-views-v1')
    pins, refs = {}, [Path(__file__)]
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        for d in [foundation, attribution, binding, views]:
            receipt = read(d / 'result.json')
            assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (receipt['jobId'],)).fetchone() == ('complete', receipt)
            refs.append(d / 'result.json')
            for e in receipt['evidenceRefs']:
                assert e['path'] not in pins or pins[e['path']] == e['sha256']
                pins[e['path']] = e['sha256']
    for p, h in pins.items():
        assert digest((ROOT / p).read_bytes()) == h, p
    bound = read(binding / 'exact-source-face-bindings.json.gz')
    evidence = []
    for mode in MODES:
        f = read(foundation / ('75351:0-' + mode + '.json'))
        a = read(attribution / (mode + '.json'))
        b = next(r for r in bound['bindings'] if r['uid'] == UID and r['mode'] == mode)
        assert f['sourceSHA256'] == b['sourceSHA256']
        assert f['wholeWorldSHA256'] == b['wholeWorldSHA256']
        assert f['strictFoundationAccepted'] is False
        assert f['foundation']['triangles'] == f['foundation']['completeTerrainTriangles'] == b['completeFaces'] == 8563
        assert [r['faceId'] for r in f['buriedFaces']] == [3028, 3029]
        assert a['rawCompoundFoundation'] == f['foundation']
        assert a['terrainOnlyFoundation']['fullyBuriedTriangles'] == 0
        assert a['terrainOnlyFoundation']['completeTerrainTriangles'] == 8563
        assert [r['faceId'] for r in a['exactFaces']] == [3028, 3029]
        assert .55 < f['foundation']['fullyBuriedAreaM2'] < .56
        for face in a['exactFaces']:
            assert len(face['pointAttribution']) == 4
            assert all(p['candidatePodiumFaceIds'] and p['highestPodiumY'] > p['position'][1] for p in face['pointAttribution'])
        evidence.append(dict(binding=b, rawFoundation=f, exactAttribution=a))
    images = [views / n for n in ['buried-front.png', 'buried-reverse.png']]
    review = dict(uid=UID, reviewer='Codex ROOT', reviewType='exact-original-authored-trim-overlap',
        sourceFaceIds=[3028, 3029], sourceFunctionalInterpretationAccepted=True,
        interpretation=[
            'These two faces form a narrow sloping strip on the original tower at its junction with the original podium feature. Both inspected oblique views locate the strip at this authored junction.',
            'All 8563 tower faces are covered by terrain evidence in all four coordinate representations, with zero terrain-only buried faces. The two compound negatives arise because the maximum projected podium surface is higher at the strip coordinates.',
            'This is retained original tower/podium overlap, not a terrain placement correction. The exact original source faces and placement remain unchanged. No structural adequacy or independent support for the separate failed rim samples is asserted.',
            'The interpretation applies only to the two face IDs bound to these full source and coordinate hashes. Raw strict compound-foundation results remain false. Existing contact, loader, collision, neighbour, visual and publication gates are not approved by this review.'
        ], exactFourModeEvidence=evidence,
        imagesActuallyInspected=[dict(path=str(p.relative_to(ROOT)), sha256=digest(p.read_bytes())) for p in images],
        strictFoundationAccepted=False, rawNumericalFailuresRemainFailed=True,
        sourceEvidenceInterpretationUsedAI=True, aiGeometryModelling=False,
        sourceGeometryChanges=0, sourcePoseChanges=0, physicalAccepted=False,
        publicationApproved=False, installationApproved=False)
    save(DOC / 'ROOT-SOURCE-INTERPRETATION.json', review)
    for p, h in pins.items():
        assert digest((ROOT / p).read_bytes()) == h, p
        refs.append(ROOT / p)
    module('pacifica_tower3_review_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'two-exact-original-trim-face-interpretation', list(dict.fromkeys(refs)),
        dict(uids=[UID, 'landsd/283036:0'], sourceFunctionalInterpretationAccepted=True,
             strictFoundationAccepted=False, installationApproved=False))

if __name__ == '__main__':
    main()
